"""
Lifecycle Hooks Module — Pre/post execution hooks for skill lifecycle management
Provides hooks that execute before and after skill execution with error handling and retry logic.
"""

import time
import functools
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger("fighting-game-combo-optimizer")


class LifecyclePhase(str, Enum):
    """Lifecycle phases where hooks can be attached."""
    PRE_EXECUTION = "pre_execution"
    PRE_VALIDATION = "pre_validation"
    POST_VALIDATION = "post_validation"
    PRE_ANALYSIS = "pre_analysis"
    POST_ANALYSIS = "post_analysis"
    PRE_SYNTHESIS = "pre_synthesis"
    POST_SYNTHESIS = "post_synthesis"
    PRE_QUALITY_GATE = "pre_quality_gate"
    POST_QUALITY_GATE = "post_quality_gate"
    POST_EXECUTION = "post_execution"
    ON_ERROR = "on_error"
    ON_RETRY = "on_retry"


@dataclass
class LifecycleHook:
    """
    A lifecycle hook that executes at a specific phase.
    """
    phase: LifecyclePhase
    name: str
    handler: Callable
    priority: int = 0  # Higher priority hooks execute first
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __call__(self, context: Dict[str, Any]) -> Any:
        """Execute the hook handler with the given context."""
        return self.handler(context)


@dataclass
class HookResult:
    """
    Result of hook execution.
    """
    hook_name: str
    phase: LifecyclePhase
    success: bool
    duration_ms: float
    result: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "hook_name": self.hook_name,
            "phase": self.phase.value,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "result": str(self.result) if self.result is not None else None,
            "error": str(self.error) if self.error else None,
            "metadata": self.metadata
        }


class HookManager:
    """
    Manages lifecycle hooks for skill execution.
    Provides registration, execution, and error handling for hooks.
    """

    def __init__(self):
        """Initialize the hook manager."""
        # Hooks organized by phase
        self._hooks: Dict[LifecyclePhase, List[LifecycleHook]] = {
            phase: [] for phase in LifecyclePhase
        }

        # Execution history
        self._execution_history: List[HookResult] = []

        # Statistics
        self._hook_stats: Dict[str, Dict[str, Any]] = {}

    def register_hook(self, hook: LifecycleHook) -> bool:
        """
        Register a lifecycle hook.

        Args:
            hook: The hook to register

        Returns:
            bool: True if registration succeeded
        """
        if not hook.enabled:
            return False

        phase_hooks = self._hooks[hook.phase]
        phase_hooks.append(hook)

        # Sort by priority (higher priority first)
        phase_hooks.sort(key=lambda h: h.priority, reverse=True)

        # Initialize stats if needed
        if hook.name not in self._hook_stats:
            self._hook_stats[hook.name] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0.0,
                "average_duration_ms": 0.0
            }

        logger.debug(f"Registered hook '{hook.name}' for phase '{hook.phase.value}'")
        return True

    def unregister_hook(self, hook_name: str, phase: Optional[LifecyclePhase] = None) -> bool:
        """
        Unregister a hook by name.

        Args:
            hook_name: Name of the hook to unregister
            phase: Specific phase (if None, removes from all phases)

        Returns:
            bool: True if hook was found and removed
        """
        if phase:
            phase_hooks = self._hooks[phase]
            for i, hook in enumerate(phase_hooks):
                if hook.name == hook_name:
                    phase_hooks.pop(i)
                    return True
        else:
            for phase_hooks in self._hooks.values():
                for i, hook in enumerate(phase_hooks):
                    if hook.name == hook_name:
                        phase_hooks.pop(i)
                        return True
        return False

    def execute_hooks(
        self,
        phase: LifecyclePhase,
        context: Dict[str, Any],
        stop_on_error: bool = False
    ) -> List[HookResult]:
        """
        Execute all hooks for a specific phase.

        Args:
            phase: The lifecycle phase
            context: Execution context passed to hooks
            stop_on_error: Whether to stop execution if a hook fails

        Returns:
            list: Results of hook executions
        """
        results = []
        phase_hooks = self._hooks.get(phase, [])

        logger.debug(f"Executing {len(phase_hooks)} hooks for phase '{phase.value}'")

        for hook in phase_hooks:
            start_time = time.perf_counter()
            result = HookResult(
                hook_name=hook.name,
                phase=phase,
                success=False,
                duration_ms=0.0
            )

            try:
                # Execute the hook
                hook_result = hook(context)

                # Record success
                result.success = True
                result.result = hook_result
                result.duration_ms = (time.perf_counter() - start_time) * 1000

                # Update stats
                self._update_stats(hook.name, True, result.duration_ms)

                logger.debug(
                    f"Hook '{hook.name}' executed successfully "
                    f"in {result.duration_ms:.2f}ms"
                )

            except Exception as e:
                # Record failure
                result.success = False
                result.error = e
                result.duration_ms = (time.perf_counter() - start_time) * 1000

                # Update stats
                self._update_stats(hook.name, False, result.duration_ms)

                logger.error(
                    f"Hook '{hook.name}' failed: {e}",
                    exc_info=e
                )

                # Stop if configured
                if stop_on_error:
                    logger.error(f"Stopping hook execution due to error in '{hook.name}'")
                    break

            finally:
                results.append(result)
                self._execution_history.append(result)

        return results

    def _update_stats(self, hook_name: str, success: bool, duration_ms: float):
        """Update statistics for a hook."""
        if hook_name not in self._hook_stats:
            return

        stats = self._hook_stats[hook_name]
        stats["executions"] += 1
        stats["total_duration_ms"] += duration_ms
        stats["average_duration_ms"] = (
            stats["total_duration_ms"] / stats["executions"]
        )

        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1

    def get_hook_stats(self, hook_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for hooks.

        Args:
            hook_name: Specific hook name (if None, returns all stats)

        Returns:
            dict: Hook statistics
        """
        if hook_name:
            return self._hook_stats.get(hook_name, {})
        return self._hook_stats.copy()

    def get_execution_history(
        self,
        phase: Optional[LifecyclePhase] = None,
        limit: Optional[int] = None
    ) -> List[HookResult]:
        """
        Get hook execution history.

        Args:
            phase: Filter by specific phase
            limit: Maximum number of results to return

        Returns:
            list: Hook execution results
        """
        history = self._execution_history

        if phase:
            history = [r for r in history if r.phase == phase]

        if limit:
            history = history[-limit:]

        return history

    def clear_history(self):
        """Clear the execution history."""
        self._execution_history.clear()

    def get_hook_count(self, phase: Optional[LifecyclePhase] = None) -> int:
        """
        Get the number of registered hooks.

        Args:
            phase: Specific phase (if None, returns total count)

        Returns:
            int: Number of hooks
        """
        if phase:
            return len(self._hooks.get(phase, []))
        return sum(len(hooks) for hooks in self._hooks.values())


# Global hook manager instance
_hook_manager: Optional[HookManager] = None


def get_hook_manager() -> HookManager:
    """Get the global hook manager instance (singleton)."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
    return _hook_manager


def register_lifecycle_hook(
    phase: LifecyclePhase,
    name: str,
    handler: Callable,
    priority: int = 0,
    enabled: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Register a lifecycle hook.

    Args:
        phase: The lifecycle phase for this hook
        name: Unique name for the hook
        handler: Callable that takes context dict and returns result
        priority: Higher priority hooks execute first
        enabled: Whether the hook is enabled
        metadata: Optional metadata for the hook

    Returns:
        bool: True if registration succeeded
    """
    hook = LifecycleHook(
        phase=phase,
        name=name,
        handler=handler,
        priority=priority,
        enabled=enabled,
        metadata=metadata or {}
    )

    return get_hook_manager().register_hook(hook)


def execute_pre_hooks(phase: LifecyclePhase, context: Dict[str, Any]) -> List[HookResult]:
    """
    Execute pre-phase hooks.

    Args:
        phase: The phase to execute hooks for
        context: Execution context

    Returns:
        list: Hook execution results
    """
    return get_hook_manager().execute_hooks(phase, context)


def execute_post_hooks(phase: LifecyclePhase, context: Dict[str, Any]) -> List[HookResult]:
    """
    Execute post-phase hooks.

    Args:
        phase: The phase to execute hooks for
        context: Execution context

    Returns:
        list: Hook execution results
    """
    return get_hook_manager().execute_hooks(phase, context)


def create_hook_decorator(phase: LifecyclePhase):
    """
    Create a decorator for registering hooks at a specific phase.

    Args:
        phase: The lifecycle phase for the decorator

    Returns:
        callable: Decorator function
    """
    def decorator(name: str, priority: int = 0):
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapped(context: Dict[str, Any]) -> Any:
                return func(context)

            register_lifecycle_hook(
                phase=phase,
                name=name,
                handler=wrapped,
                priority=priority
            )

            return wrapped
        return wrapper
    return decorator


# Convenience decorators
pre_execution = create_hook_decorator(LifecyclePhase.PRE_EXECUTION)
pre_validation = create_hook_decorator(LifecyclePhase.PRE_VALIDATION)
post_validation = create_hook_decorator(LifecyclePhase.POST_VALIDATION)
pre_analysis = create_hook_decorator(LifecyclePhase.PRE_ANALYSIS)
post_analysis = create_hook_decorator(LifecyclePhase.POST_ANALYSIS)
pre_synthesis = create_hook_decorator(LifecyclePhase.PRE_SYNTHESIS)
post_synthesis = create_hook_decorator(LifecyclePhase.POST_SYNTHESIS)
pre_quality_gate = create_hook_decorator(LifecyclePhase.PRE_QUALITY_GATE)
post_quality_gate = create_hook_decorator(LifecyclePhase.POST_QUALITY_GATE)
post_execution = create_hook_decorator(LifecyclePhase.POST_EXECUTION)
on_error = create_hook_decorator(LifecyclePhase.ON_ERROR)
on_retry = create_hook_decorator(LifecyclePhase.ON_RETRY)
