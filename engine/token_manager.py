"""
Token Manager Module — Token budget management and optimization
Tracks token usage, enforces budgets, and provides optimization recommendations.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from collections import defaultdict

from config.llm_config import LLMConfig, get_llm_config

logger = logging.getLogger("fighting-game-combo-optimizer")


class TokenAlertLevel(str, Enum):
    """Alert levels for token usage."""
    NORMAL = "normal"  # Below 80% of budget
    WARNING = "warning"  # 80-95% of budget
    CRITICAL = "critical"  # Above 95% of budget
    EXCEEDED = "exceeded"  # Over budget


@dataclass
class TokenBudget:
    """
    Token budget configuration.
    """
    max_tokens: int
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    per_execution_limit: Optional[int] = None
    enable_optimization: bool = True

    def get_warning_limit(self) -> int:
        """Get warning threshold in tokens."""
        return int(self.max_tokens * self.warning_threshold)

    def get_critical_limit(self) -> int:
        """Get critical threshold in tokens."""
        return int(self.max_tokens * self.critical_threshold)


@dataclass
class TokenUsage:
    """
    Token usage tracking for an execution.
    """
    execution_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    model: Optional[str] = None
    optimized: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate total tokens."""
        self.total_tokens = self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp,
            "model": self.model,
            "optimized": self.optimized,
            "metadata": self.metadata
        }


class TokenManager:
    """
    Manages token budgets, tracking, and optimization.
    """

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        budget: Optional[TokenBudget] = None
    ):
        """
        Initialize the token manager.

        Args:
            llm_config: LLM configuration
            budget: Token budget configuration
        """
        self._llm_config = llm_config or get_llm_config()
        self._budget = budget or TokenBudget(max_tokens=200000)

        # Execution tracking
        self._executions: Dict[str, TokenUsage] = {}
        self._execution_history: List[TokenUsage] = []

        # Statistics
        self._stats = {
            "total_executions": 0,
            "total_tokens_used": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "optimizations_applied": 0,
            "budget_exceeded_count": 0
        }

    def start_execution(
        self,
        execution_id: str,
        estimated_input_tokens: int = 0
    ) -> TokenUsage:
        """
        Start tracking a new execution.

        Args:
            execution_id: Unique execution identifier
            estimated_input_tokens: Estimated input tokens

        Returns:
            TokenUsage: The usage tracker for this execution
        """
        usage = TokenUsage(
            execution_id=execution_id,
            input_tokens=estimated_input_tokens
        )

        self._executions[execution_id] = usage
        return usage

    def complete_execution(
        self,
        execution_id: str,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
        optimized: bool = False
    ) -> TokenUsage:
        """
        Complete execution tracking.

        Args:
            execution_id: Execution identifier
            input_tokens: Actual input tokens used
            output_tokens: Actual output tokens generated
            model: Model used
            optimized: Whether optimization was applied

        Returns:
            TokenUsage: The completed usage tracker
        """
        usage = self._executions.get(execution_id)
        if not usage:
            usage = TokenUsage(execution_id=execution_id)

        usage.input_tokens = input_tokens
        usage.output_tokens = output_tokens
        usage.total_tokens = input_tokens + output_tokens
        usage.model = model
        usage.optimized = optimized
        usage.timestamp = time.time()

        # Update history
        self._execution_history.append(usage)

        # Update statistics
        self._stats["total_executions"] += 1
        self._stats["total_tokens_used"] += usage.total_tokens
        self._stats["total_input_tokens"] += usage.input_tokens
        self._stats["total_output_tokens"] += usage.output_tokens
        if optimized:
            self._stats["optimizations_applied"] += 1

        # Check budget
        if usage.total_tokens > self._budget.max_tokens:
            self._stats["budget_exceeded_count"] += 1
            logger.warning(
                f"Execution {execution_id} exceeded token budget: "
                f"{usage.total_tokens} > {self._budget.max_tokens}"
            )

        return usage

    def get_execution_tokens(self, execution_id: str) -> int:
        """
        Get token count for an execution.

        Args:
            execution_id: Execution identifier

        Returns:
            int: Total tokens used (0 if not found)
        """
        usage = self._executions.get(execution_id)
        return usage.total_tokens if usage else 0

    def check_alert_level(self, current_tokens: int) -> TokenAlertLevel:
        """
        Check alert level for current token usage.

        Args:
            current_tokens: Current token count

        Returns:
            TokenAlertLevel: Current alert level
        """
        if current_tokens > self._budget.max_tokens:
            return TokenAlertLevel.EXCEEDED
        elif current_tokens >= self._budget.get_critical_limit():
            return TokenAlertLevel.CRITICAL
        elif current_tokens >= self._budget.get_warning_limit():
            return TokenAlertLevel.WARNING
        else:
            return TokenAlertLevel.NORMAL

    def get_optimization_recommendation(
        self,
        current_tokens: int,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get optimization recommendations for current usage.

        Args:
            current_tokens: Current token count
            context: Optional context information

        Returns:
            dict: Optimization recommendations
        """
        alert_level = self.check_alert_level(current_tokens)

        recommendations = {
            "alert_level": alert_level.value,
            "current_tokens": current_tokens,
            "max_tokens": self._budget.max_tokens,
            "usage_percentage": (current_tokens / self._budget.max_tokens) * 100,
            "recommendations": []
        }

        if alert_level in [TokenAlertLevel.CRITICAL, TokenAlertLevel.EXCEEDED]:
            recommendations["recommendations"].extend([
                "Enable aggressive token optimization",
                "Summarize context to key points only",
                "Remove redundant information",
                "Use higher compression ratio"
            ])
        elif alert_level == TokenAlertLevel.WARNING:
            recommendations["recommendations"].extend([
                "Monitor token usage closely",
                "Consider removing less critical context",
                "Enable token optimization"
            ])

        # Get model-specific recommendations
        if self._budget.enable_optimization:
            model_config = self._llm_config.get_model_config()
            if current_tokens > model_config.effective_context_window:
                recommendations["recommendations"].append(
                    f"Current usage ({current_tokens}) exceeds model's effective context "
                    f"window ({model_config.effective_context_window})"
                )

        return recommendations

    def estimate_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate
            model: Model name (affects tokenization)

        Returns:
            int: Estimated token count
        """
        return self._llm_config.estimate_token_count(text, model)

    def optimize_context(
        self,
        context_items: List[Any],
        model: Optional[str] = None,
        target_tokens: Optional[int] = None
    ) -> List[Any]:
        """
        Optimize context items to fit within token limits.

        Args:
            context_items: List of context items
            model: Model to optimize for
            target_tokens: Target token count

        Returns:
            list: Optimized context items
        """
        if not self._budget.enable_optimization:
            return context_items

        target = target_tokens or self._budget.max_tokens

        return self._llm_config.optimize_context(
            context_items=context_items,
            model=model,
            priority_callback=None
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get token usage statistics.

        Returns:
            dict: Statistics summary
        """
        stats = self._stats.copy()

        if self._stats["total_executions"] > 0:
            stats["average_tokens_per_execution"] = (
                self._stats["total_tokens_used"] / self._stats["total_executions"]
            )
            stats["average_input_tokens"] = (
                self._stats["total_input_tokens"] / self._stats["total_executions"]
            )
            stats["average_output_tokens"] = (
                self._stats["total_output_tokens"] / self._stats["total_executions"]
            )

        # Alert level distribution
        alert_distribution = defaultdict(int)
        for usage in self._execution_history:
            alert_level = self.check_alert_level(usage.total_tokens)
            alert_distribution[alert_level.value] += 1

        stats["alert_distribution"] = dict(alert_distribution)

        return stats

    def get_execution_history(
        self,
        limit: Optional[int] = None
    ) -> List[TokenUsage]:
        """
        Get execution history.

        Args:
            limit: Maximum number of entries

        Returns:
            list: Execution usage history
        """
        history = self._execution_history[::-1]  # Most recent first

        if limit:
            history = history[:limit]

        return history

    def reset_statistics(self):
        """Reset all statistics."""
        self._stats = {
            "total_executions": 0,
            "total_tokens_used": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "optimizations_applied": 0,
            "budget_exceeded_count": 0
        }
        self._execution_history.clear()


# Global token manager instance
_token_manager: Optional[TokenManager] = None


def get_token_manager(budget: Optional[TokenBudget] = None) -> TokenManager:
    """Get the global token manager instance (singleton)."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager(budget=budget)
    return _token_manager


def reset_token_manager():
    """Reset the global token manager (mainly for testing)."""
    global _token_manager
    _token_manager = None
