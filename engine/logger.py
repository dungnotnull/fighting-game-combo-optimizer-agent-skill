"""
Logger Module — Structured logging with context and correlation
Provides production-grade structured logging with context tracking and correlation IDs.
"""

import logging
import time
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from pathlib import Path
from datetime import datetime
import traceback as tb

from config.settings import get_settings


@dataclass
class LogContext:
    """
    Context information for log entries.
    """
    execution_id: Optional[str] = None
    skill_name: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "skill_name": self.skill_name,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            **self.additional_context
        }

    def merge(self, other: 'LogContext') -> 'LogContext':
        """Merge another context into this one."""
        return LogContext(
            execution_id=other.execution_id or self.execution_id,
            skill_name=other.skill_name or self.skill_name,
            correlation_id=other.correlation_id or self.correlation_id,
            user_id=other.user_id or self.user_id,
            session_id=other.session_id or self.session_id,
            additional_context={**self.additional_context, **other.additional_context}
        )


class StructuredLogger:
    """
    Structured logger with context tracking and correlation.
    Outputs JSON-formatted logs for production environments.
    """

    def __init__(self, name: str = "fighting-game-combo-optimizer"):
        """
        Initialize the structured logger.

        Args:
            name: Logger name
        """
        self._logger = logging.getLogger(name)
        self._current_context: Optional[LogContext] = None

        # Configure based on settings
        settings = get_settings()
        self._configure_logger(settings)

    def _configure_logger(self, settings):
        """Configure the Python logger."""
        # Get log configuration from settings
        log_config = settings.get_log_config()

        # Apply configuration
        logging.config.dictConfig(log_config)

        # Set logger level
        self._logger.setLevel(settings.log_level.value)

    def log_with_context(
        self,
        level: str,
        message: str,
        context: Optional[LogContext] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        """
        Log a message with context.

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Log context
            extra_data: Additional data to include
            exc_info: Exception information
        """
        # Merge contexts
        log_context = context or self._current_context

        # Build extra data
        extra = {}

        if log_context:
            extra.update(log_context.to_dict())

        if extra_data:
            extra.update(extra_data)

        if exc_info:
            extra["exception"] = {
                "type": type(exc_info).__name__,
                "message": str(exc_info),
                "traceback": ''.join(tb.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
            }

        # Add timestamp
        extra["timestamp"] = datetime.utcnow().isoformat()
        extra["level"] = level.upper()

        # Get the logging method
        log_method = getattr(self._logger, level.lower(), self._logger.info)

        # Log with extra data
        if extra:
            # For structured logging, add as extra
            log_method(message, extra={"structured": extra})
        else:
            log_method(message)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log_with_context("debug", message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log_with_context("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log_with_context("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log_with_context("error", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log_with_context("critical", message, **kwargs)

    def exception(self, message: str, exc_info: Exception, **kwargs):
        """Log exception with traceback."""
        self.log_with_context("error", message, exc_info=exc_info, **kwargs)

    def set_context(self, context: LogContext):
        """
        Set the current log context.

        Args:
            context: Context to set
        """
        self._current_context = context

    def clear_context(self):
        """Clear the current log context."""
        self._current_context = None

    def get_context(self) -> Optional[LogContext]:
        """Get the current log context."""
        return self._current_context

    def create_child_context(self, **kwargs) -> LogContext:
        """
        Create a child context from current context.

        Args:
            **kwargs: Fields to override or add

        Returns:
            LogContext: New child context
        """
        base = self._current_context or LogContext()
        return LogContext(
            execution_id=kwargs.get("execution_id", base.execution_id),
            skill_name=kwargs.get("skill_name", base.skill_name),
            correlation_id=kwargs.get("correlation_id", base.correlation_id),
            user_id=kwargs.get("user_id", base.user_id),
            session_id=kwargs.get("session_id", base.session_id),
            additional_context={**base.additional_context, **kwargs}
        )


class LogAggregator:
    """
    Aggregates logs for analysis and monitoring.
    """

    def __init__(self, max_entries: int = 10000):
        """
        Initialize the log aggregator.

        Args:
            max_entries: Maximum number of log entries to store
        """
        self._logs: List[Dict[str, Any]] = []
        self._max_entries = max_entries

    def add_log(self, log_entry: Dict[str, Any]):
        """
        Add a log entry.

        Args:
            log_entry: Log entry to add
        """
        self._logs.append(log_entry)

        # Trim if over limit
        if len(self._logs) > self._max_entries:
            self._logs = self._logs[-self._max_entries:]

    def get_logs(
        self,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: Optional[int] = None,
        since: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get filtered logs.

        Args:
            level: Filter by log level
            execution_id: Filter by execution ID
            limit: Maximum number of entries
            since: Only logs after this timestamp

        Returns:
            list: Filtered log entries
        """
        logs = self._logs[:]

        if level:
            logs = [l for l in logs if l.get("level") == level.upper()]

        if execution_id:
            logs = [l for l in logs if l.get("execution_id") == execution_id]

        if since:
            logs = [l for l in logs if l.get("timestamp_ts", 0) >= since]

        logs = logs[::-1]  # Most recent first

        if limit:
            logs = logs[:limit]

        return logs

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get log statistics.

        Returns:
            dict: Log statistics
        """
        if not self._logs:
            return {"total": 0}

        level_counts = {}
        for log in self._logs:
            level = log.get("level", "UNKNOWN")
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total": len(self._logs),
            "level_distribution": level_counts,
            "oldest_timestamp": min(l.get("timestamp_ts", 0) for l in self._logs),
            "newest_timestamp": max(l.get("timestamp_ts", 0) for l in self._logs)
        }

    def export_logs(self, output_file: str):
        """
        Export logs to a file.

        Args:
            output_file: Path to output file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self._logs, f, indent=2, default=str)

    def clear(self):
        """Clear all logs."""
        self._logs.clear()


# Global logger instance
_logger: Optional[StructuredLogger] = None
_aggregator: Optional[LogAggregator] = None


def get_logger(name: str = "fighting-game-combo-optimizer") -> StructuredLogger:
    """Get the global structured logger instance (singleton)."""
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name)
    return _logger


def get_log_aggregator(max_entries: int = 10000) -> LogAggregator:
    """Get the global log aggregator instance (singleton)."""
    global _aggregator
    if _aggregator is None:
        _aggregator = LogAggregator(max_entries)
    return _aggregator


def reset_logger():
    """Reset the global logger (mainly for testing)."""
    global _logger, _aggregator
    _logger = None
    _aggregator = None
