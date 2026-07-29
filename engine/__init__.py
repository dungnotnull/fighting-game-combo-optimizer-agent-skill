"""
Execution Engine — Production-grade skill execution with token optimization and error handling
Provides structured execution with logging, token management, quality gates, and graceful fallbacks.
"""

from .executor import (
    SkillExecutor,
    ExecutionResult,
    ExecutionConfig,
    get_executor
)
from .quality_gates import (
    QualityGate,
    QualityGateResult,
    apply_quality_gates,
    UNIVERSAL_GATES,
    DOMAIN_GATES
)
from .token_manager import (
    TokenManager,
    TokenBudget,
    get_token_manager
)
from .logger import (
    StructuredLogger,
    get_logger,
    LogContext
)

__all__ = [
    # Executor
    "SkillExecutor",
    "ExecutionResult",
    "ExecutionConfig",
    "get_executor",

    # Quality Gates
    "QualityGate",
    "QualityGateResult",
    "apply_quality_gates",
    "UNIVERSAL_GATES",
    "DOMAIN_GATES",

    # Token Management
    "TokenManager",
    "TokenBudget",
    "get_token_manager",

    # Logging
    "StructuredLogger",
    "get_logger",
    "LogContext"
]
