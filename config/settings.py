"""
Settings Module — Type-safe configuration management
Handles environment variables, feature flags, and system-wide settings with validation and type safety.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels for the system."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Environment types for deployment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class Settings:
    """
    Type-safe settings configuration.
    All settings are validated at initialization and cannot be modified at runtime (immutable).
    """
    # Environment
    environment: Environment = field(
        default_factory=lambda: Environment(
            os.getenv("FIGHTING_GAME_ENV", "development")
        )
    )

    # Logging
    log_level: LogLevel = field(
        default_factory=lambda: LogLevel(
            os.getenv("FIGHTING_GAME_LOG_LEVEL", "INFO")
        )
    )
    log_file: Optional[str] = field(
        default_factory=lambda: os.getenv("FIGHTING_GAME_LOG_FILE")
    )
    structured_logging: bool = field(
        default_factory=lambda: os.getenv(
            "FIGHTING_GAME_STRUCTURED_LOGGING", "true"
        ).lower() == "true"
    )

    # Knowledge Pipeline
    knowledge_update_enabled: bool = field(
        default_factory=lambda: os.getenv(
            "FIGHTING_GAME_KNOWLEDGE_UPDATE_ENABLED", "true"
        ).lower() == "true"
    )
    knowledge_cron_schedule_academic: str = field(
        default="0 8 * * 1"
    )
    knowledge_cron_schedule_news: str = field(
        default="0 7 * * *"
    )

    # Feature Flags
    enable_hooks: bool = True
    enable_state_sync: bool = True
    enable_event_emission: bool = True
    enable_skill_caching: bool = True

    # Performance
    max_context_window: int = field(
        default_factory=lambda: int(
            os.getenv("FIGHTING_GAME_MAX_CONTEXT_WINDOW", "200000")
        )
    )
    token_optimization_enabled: bool = True

    # Quality Gates
    strict_quality_gates: bool = field(
        default_factory=lambda: os.getenv(
            "FIGHTING_GAME_STRICT_QUALITY_GATES", "true"
        ).lower() == "true"
    )
    max_retry_attempts: int = field(
        default_factory=lambda: int(
            os.getenv("FIGHTING_GAME_MAX_RETRY_ATTEMPTS", "2")
        )
    )

    # Validation
    validate_all_inputs: bool = True
    validate_all_outputs: bool = True

    # Paths (computed from project root)
    project_root: str = field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    def __post_init__(self):
        """Validate settings after initialization."""
        # Validate context window is positive
        if self.max_context_window <= 0:
            raise ValueError(
                f"max_context_window must be positive, got {self.max_context_window}"
            )

        # Validate retry attempts
        if self.max_retry_attempts < 0:
            raise ValueError(
                f"max_retry_attempts must be non-negative, got {self.max_retry_attempts}"
            )

        # Validate log file path if provided
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    def get_log_config(self) -> dict:
        """Get logging configuration dict for Python logging module."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "structured": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                } if self.structured_logging else {}
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured" if self.structured_logging else "default",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "structured" if self.structured_logging else "default",
                    "filename": self.log_file,
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                } if self.log_file else None
            },
            "loggers": {
                "fighting-game-combo-optimizer": {
                    "level": self.log_level.value,
                    "handlers": ["console"] + (["file"] if self.log_file else []),
                    "propagate": False
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        }


# Global settings instance (singleton pattern)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings():
    """Reset the global settings instance (mainly for testing)."""
    global _settings
    _settings = None
