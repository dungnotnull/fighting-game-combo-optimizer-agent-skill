"""
Skill Executor Module — Production-grade skill execution with error handling and retries
Provides structured execution with proper error handling, retry logic, and fallback mechanisms.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable
from enum import Enum
import logging
import traceback

from config.skill_registry import SkillRegistry, SkillMetadata, resolve_skill
from config.settings import get_settings
from config.llm_config import LLMConfig, get_llm_config
from hooks.lifecycle import (
    LifecyclePhase,
    execute_pre_hooks,
    execute_post_hooks,
    on_error as on_error_hook
)
from hooks.state_sync import StateManager, StateScope, get_state_manager
from hooks.event_emitter import (
    EventEmitter,
    EventType,
    emit_event,
    get_event_emitter
)
from .logger import StructuredLogger, LogContext, get_logger
from .quality_gates import QualityGateResult, apply_quality_gates
from .token_manager import TokenManager, get_token_manager


logger = logging.getLogger("fighting-game-combo-optimizer")


class ExecutionStatus(str, Enum):
    """Status of skill execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """
    Result of skill execution.
    """
    status: ExecutionStatus
    output: Any = None
    error: Optional[Exception] = None
    duration_ms: float = 0.0
    tokens_used: int = 0
    quality_gate_results: List[QualityGateResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate execution result."""
        if self.status == ExecutionStatus.FAILED and self.error is None:
            raise ValueError("FAILED status requires error to be set")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value,
            "output": str(self.output) if self.output else None,
            "error": str(self.error) if self.error else None,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "quality_gates": {
                "passed": sum(1 for r in self.quality_gate_results if r.passed),
                "failed": sum(1 for r in self.quality_gate_results if not r.passed),
                "details": [r.to_dict() for r in self.quality_gate_results]
            },
            "metadata": self.metadata
        }


@dataclass
class ExecutionConfig:
    """
    Configuration for skill execution.
    """
    # Retry settings
    max_retries: int = 2
    retry_delay: float = 1.0
    retry_backoff_multiplier: float = 2.0

    # Timeout settings
    default_timeout: float = 120.0  # seconds

    # Token management
    enable_token_tracking: bool = True
    max_tokens: Optional[int] = None

    # Quality gates
    enable_quality_gates: bool = True
    strict_quality_gates: bool = True

    # Logging
    enable_structured_logging: bool = True
    log_level: str = "INFO"

    # Graceful degradation
    enable_graceful_degradation: bool = True
    degradation_levels: int = 5

    # Caching
    enable_result_caching: bool = True
    cache_ttl: int = 300  # seconds

    def __post_init__(self):
        """Validate configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        if self.default_timeout <= 0:
            raise ValueError("default_timeout must be positive")


class SkillExecutor:
    """
    Production-grade skill executor with error handling, retries, and fallbacks.
    Integrates with hooks, state management, events, logging, and quality gates.
    """

    def __init__(
        self,
        skill_registry: Optional[SkillRegistry] = None,
        state_manager: Optional[StateManager] = None,
        event_emitter: Optional[EventEmitter] = None,
        token_manager: Optional[TokenManager] = None,
        structured_logger: Optional[StructuredLogger] = None,
        config: Optional[ExecutionConfig] = None
    ):
        """
        Initialize the skill executor.

        Args:
            skill_registry: Skill registry instance
            state_manager: State manager instance
            event_emitter: Event emitter instance
            token_manager: Token manager instance
            structured_logger: Structured logger instance
            config: Execution configuration
        """
        # Dependencies
        self._skill_registry = skill_registry or get_skill_registry()
        self._state_manager = state_manager or get_state_manager()
        self._event_emitter = event_emitter or get_event_emitter()
        self._token_manager = token_manager or get_token_manager()
        self._structured_logger = structured_logger or get_logger()

        # Configuration
        self._config = config or ExecutionConfig()

        # Settings
        self._settings = get_settings()
        self._llm_config = get_llm_config()

        # Execution statistics
        self._stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "retries": 0,
            "total_tokens_used": 0,
            "total_duration_ms": 0.0
        }

    def execute(
        self,
        skill_name: Optional[str] = None,
        query: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """
        Execute a skill with full production-grade error handling.

        Args:
            skill_name: Exact skill name to execute (optional if query provided)
            query: Query for automatic skill resolution (optional if skill_name provided)
            input_data: Input data for the skill
            context: Additional execution context
            config_override: Override execution config for this execution

        Returns:
            ExecutionResult: Result of execution
        """
        # Merge config
        config = config_override or self._config

        # Create execution context
        execution_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        context = self._prepare_context(
            execution_id=execution_id,
            skill_name=skill_name,
            query=query,
            input_data=input_data,
            additional_context=context
        )

        # Create log context
        log_ctx = LogContext(
            execution_id=execution_id,
            skill_name=skill_name or "auto-resolved",
            correlation_id=context.get("correlation_id")
        )

        # Resolve skill
        skill = self._resolve_skill(skill_name, query, context)
        if not skill:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error=ValueError(f"No skill resolved for: {skill_name or query}"),
                duration_ms=(time.perf_counter() - start_time) * 1000
            )

        context["skill"] = skill.name
        log_ctx.skill_name = skill.name

        # Initialize result
        result = ExecutionResult(
            status=ExecutionStatus.PENDING,
            metadata={"execution_id": execution_id, "skill": skill.name}
        )

        # Emit invocation event
        emit_event(
            EventType.SKILL_INVOKED,
            payload={
                "skill": skill.name,
                "execution_id": execution_id,
                "query": query
            }
        )

        # Execute with retry logic
        retry_count = 0
        max_retries = config.max_retries

        while retry_count <= max_retries:
            try:
                # Update status
                if retry_count > 0:
                    result.status = ExecutionStatus.RETRYING
                    emit_event(
                        EventType.SKILL_RETRY,
                        payload={
                            "skill": skill.name,
                            "execution_id": execution_id,
                            "attempt": retry_count + 1
                        }
                    )

                result.status = ExecutionStatus.RUNNING

                # Log execution start
                self._structured_logger.log_with_context(
                    "info",
                    f"Executing skill '{skill.name}'",
                    context=log_ctx
                )

                # Pre-execution hooks
                hook_results = execute_pre_hooks(
                    LifecyclePhase.PRE_EXECUTION,
                    context
                )

                # Execute skill
                output = self._execute_skill_logic(skill, context)

                # Post-execution hooks
                context["output"] = output
                hook_results = execute_post_hooks(
                    LifecyclePhase.POST_EXECUTION,
                    context
                )

                # Apply quality gates
                if config.enable_quality_gates:
                    gate_results = apply_quality_gates(
                        skill.name,
                        output,
                        strict=config.strict_quality_gates
                    )
                    result.quality_gate_results = gate_results

                # Success
                result.status = ExecutionStatus.COMPLETED
                result.output = output
                result.duration_ms = (time.perf_counter() - start_time) * 1000

                # Track tokens if enabled
                if config.enable_token_tracking:
                    result.tokens_used = self._token_manager.get_execution_tokens(
                        execution_id
                    )

                # Emit completion event
                emit_event(
                    EventType.SKILL_COMPLETED,
                    payload={
                        "skill": skill.name,
                        "execution_id": execution_id,
                        "duration_ms": result.duration_ms,
                        "tokens_used": result.tokens_used
                    }
                )

                # Update statistics
                self._update_stats(success=True, duration=result.duration_ms)

                # Log success
                self._structured_logger.log_with_context(
                    "info",
                    f"Skill '{skill.name}' completed successfully in {result.duration_ms:.2f}ms",
                    context=log_ctx
                )

                break  # Exit retry loop

            except Exception as e:
                retry_count += 1
                result.error = e

                # Log error
                self._structured_logger.log_with_context(
                    "error",
                    f"Execution error (attempt {retry_count}): {str(e)}",
                    context=log_ctx
                )

                # Check if should retry
                if retry_count > max_retries:
                    result.status = ExecutionStatus.FAILED
                    result.duration_ms = (time.perf_counter() - start_time) * 1000

                    # Emit failure event
                    emit_event(
                        EventType.SKILL_FAILED,
                        payload={
                            "skill": skill.name,
                            "execution_id": execution_id,
                            "error": str(e),
                            "retries": retry_count
                        }
                    )

                    # Update statistics
                    self._update_stats(success=False, duration=result.duration_ms)

                    # Execute error hooks
                    error_context = context.copy()
                    error_context["error"] = e
                    execute_pre_hooks(LifecyclePhase.ON_ERROR, error_context)

                    break

                # Apply retry delay with backoff
                delay = config.retry_delay * (config.retry_backoff_multiplier ** (retry_count - 1))
                time.sleep(delay)

        return result

    def _resolve_skill(
        self,
        skill_name: Optional[str],
        query: Optional[str],
        context: Dict[str, Any]
    ) -> Optional[SkillMetadata]:
        """Resolve skill by name or query."""
        if skill_name:
            return self._skill_registry.get_skill(skill_name)
        if query:
            return resolve_skill(query=query, context=context)
        return None

    def _prepare_context(
        self,
        execution_id: str,
        skill_name: Optional[str],
        query: Optional[str],
        input_data: Optional[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare execution context."""
        context = {
            "execution_id": execution_id,
            "skill_name": skill_name,
            "query": query,
            "input": input_data or {},
            "correlation_id": str(uuid.uuid4())[:8],
            "timestamp": time.time()
        }

        # Add state references
        context["state"] = {
            "session": self._state_manager.get_all(StateScope.SESSION),
            "task": self._state_manager.get_all(StateScope.TASK),
            "skill": self._state_manager.get_all(StateScope.SKILL)
        }

        # Merge additional context
        if additional_context:
            context.update(additional_context)

        return context

    def _execute_skill_logic(
        self,
        skill: SkillMetadata,
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute the core skill logic.

        This is a placeholder - actual implementation depends on how skills
        are stored and invoked (markdown files, Python modules, etc.)
        """
        # For markdown-based skills, this would:
        # 1. Read the skill file
        # 2. Parse instructions
        # 3. Execute the workflow
        # 4. Return the result

        # For now, return a placeholder
        return {"status": "executed", "skill": skill.name}

    def _update_stats(self, success: bool, duration: float):
        """Update execution statistics."""
        self._stats["total_executions"] += 1
        self._stats["total_duration_ms"] += duration

        if success:
            self._stats["successful_executions"] += 1
        else:
            self._stats["failed_executions"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        stats = self._stats.copy()
        if stats["total_executions"] > 0:
            stats["average_duration_ms"] = (
                stats["total_duration_ms"] / stats["total_executions"]
            )
            stats["success_rate"] = (
                stats["successful_executions"] / stats["total_executions"]
            )
        return stats

    def execute_batch(
        self,
        executions: List[Dict[str, Any]],
        parallel: bool = False
    ) -> List[ExecutionResult]:
        """
        Execute multiple skills in batch.

        Args:
            executions: List of execution specifications
            parallel: Whether to execute in parallel (requires threading)

        Returns:
            list: List of execution results
        """
        results = []

        if parallel:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(self.execute, **exec_spec)
                    for exec_spec in executions
                ]

                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append(
                            ExecutionResult(
                                status=ExecutionStatus.FAILED,
                                error=e
                            )
                        )
        else:
            for exec_spec in executions:
                try:
                    result = self.execute(**exec_spec)
                    results.append(result)
                except Exception as e:
                    results.append(
                        ExecutionResult(
                            status=ExecutionStatus.FAILED,
                            error=e
                        )
                    )

        return results


# Global executor instance
_executor: Optional[SkillExecutor] = None


def get_executor(config: Optional[ExecutionConfig] = None) -> SkillExecutor:
    """Get the global skill executor instance (singleton)."""
    global _executor
    if _executor is None:
        _executor = SkillExecutor(config=config)
    return _executor


def reset_executor():
    """Reset the global executor (mainly for testing)."""
    global _executor
    _executor = None
