"""
LLM Configuration Module — LLM parameter and context management
Handles LLM model parameters, context window optimization, token management, and provider configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import json


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    LOCAL = "local"


class ModelTier(str, Enum):
    """Model tiers for cost vs quality tradeoffs."""
    PREMIUM = "premium"  # Highest quality, highest cost
    STANDARD = "standard"  # Balanced quality and cost
    ECONOMY = "economy"  # Lower cost, faster
    FAST = "fast"  # Fastest responses, for simple tasks


@dataclass
class ModelConfig:
    """
    Configuration for a specific LLM model.
    """
    name: str
    provider: ModelProvider
    tier: ModelTier
    max_tokens: int
    context_window: int
    supports_caching: bool = False
    supports_tools: bool = True
    supports_streaming: bool = True
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0

    @property
    def effective_context_window(self) -> int:
        """Get the effective context window accounting for system prompts and tools."""
        # Reserve 20% for system overhead
        return int(self.context_window * 0.8)


@dataclass
class LLMConfig:
    """
    LLM configuration management with context window optimization and token tracking.
    """
    # Model configurations
    default_model: str = field(
        default_factory=lambda: os.getenv(
            "FIGHTING_GAME_DEFAULT_MODEL", "claude-sonnet-4-6"
        )
    )
    fallback_model: str = field(
        default_factory=lambda: os.getenv(
            "FIGHTING_GAME_FALLBACK_MODEL", "claude-haiku-4-5-20251001"
        )
    )

    # Available models registry
    models: Dict[str, ModelConfig] = field(default_factory=dict)

    # Token optimization settings
    enable_token_optimization: bool = True
    target_token_count: int = 50000
    warning_threshold: float = 0.8  # Warn at 80% of context window
    critical_threshold: float = 0.95  # Critical at 95% of context window

    # Caching settings
    enable_response_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes default

    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    retry_backoff_multiplier: float = 2.0

    # Streaming settings
    enable_streaming: bool = True
    stream_chunk_size: int = 100

    def __post_init__(self):
        """Initialize model registry after creation."""
        if not self.models:
            self._initialize_default_models()

    def _initialize_default_models(self):
        """Initialize the default model registry."""
        self.models = {
            # Anthropic Models
            "claude-opus-4-7": ModelConfig(
                name="claude-opus-4-7",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.PREMIUM,
                max_tokens=8192,
                context_window=200000,
                supports_caching=True,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=15.0 / 1_000_000,
                cost_per_output_token=75.0 / 1_000_000
            ),
            "claude-sonnet-4-6": ModelConfig(
                name="claude-sonnet-4-6",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.STANDARD,
                max_tokens=8192,
                context_window=200000,
                supports_caching=True,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=3.0 / 1_000_000,
                cost_per_output_token=15.0 / 1_000_000
            ),
            "claude-haiku-4-5-20251001": ModelConfig(
                name="claude-haiku-4-5-20251001",
                provider=ModelProvider.ANTHROPIC,
                tier=ModelTier.ECONOMY,
                max_tokens=8192,
                context_window=200000,
                supports_caching=False,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=0.80 / 1_000_000,
                cost_per_output_token=4.0 / 1_000_000
            ),

            # OpenAI Models
            "gpt-4-turbo": ModelConfig(
                name="gpt-4-turbo",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.STANDARD,
                max_tokens=4096,
                context_window=128000,
                supports_caching=True,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=10.0 / 1_000_000,
                cost_per_output_token=30.0 / 1_000_000
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.STANDARD,
                max_tokens=4096,
                context_window=128000,
                supports_caching=True,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=5.0 / 1_000_000,
                cost_per_output_token=15.0 / 1_000_000
            ),
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                tier=ModelTier.ECONOMY,
                max_tokens=16384,
                context_window=128000,
                supports_caching=False,
                supports_tools=True,
                supports_streaming=True,
                cost_per_input_token=0.15 / 1_000_000,
                cost_per_output_token=0.60 / 1_000_000
            ),
        }

    def get_model_config(self, model_name: Optional[str] = None) -> ModelConfig:
        """
        Get the configuration for a specific model.

        Args:
            model_name: Name of the model. If None, returns default model.

        Returns:
            ModelConfig: The model configuration.

        Raises:
            ValueError: If the model is not registered.
        """
        name = model_name or self.default_model
        if name not in self.models:
            raise ValueError(
                f"Model '{name}' not registered. "
                f"Available models: {list(self.models.keys())}"
            )
        return self.models[name]

    def select_model_for_task(
        self,
        task_type: str,
        token_estimate: Optional[int] = None,
        quality_preference: Optional[ModelTier] = None
    ) -> str:
        """
        Select the appropriate model for a specific task based on requirements.

        Args:
            task_type: Type of task (e.g., "analysis", "validation", "quick_check")
            token_estimate: Estimated token count for the task
            quality_preference: Preferred quality tier

        Returns:
            str: Selected model name
        """
        # Task-based selection logic
        task_model_map = {
            "core_analysis": self.default_model,
            "final_synthesis": self.default_model,
            "quick_validation": self.fallback_model,
            "simple_extraction": self.fallback_model,
            "complex_reasoning": "claude-opus-4-7" if "claude-opus-4-7" in self.models else self.default_model,
        }

        base_selection = task_model_map.get(task_type, self.default_model)

        # Override by quality preference if specified
        if quality_preference:
            matching_models = [
                name for name, config in self.models.items()
                if config.tier == quality_preference
            ]
            if matching_models:
                # Select the first matching model (could be optimized)
                return matching_models[0]

        # Check token constraints
        if token_estimate:
            for model_name, config in self.models.items():
                if config.effective_context_window >= token_estimate:
                    # Found a model that can handle the token count
                    # Prefer the configured selection if it works
                    if self.models[base_selection].effective_context_window >= token_estimate:
                        return base_selection
                    return model_name

        # Return base selection or default
        return base_selection

    def estimate_token_count(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for a given text.

        Args:
            text: Text to estimate tokens for
            model: Model name (affects tokenization)

        Returns:
            int: Estimated token count
        """
        # Simple heuristic: ~4 characters per token
        # This is a rough estimate; actual tokenization depends on the model
        return len(text) // 4

    def check_context_window(
        self,
        current_tokens: int,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if current token usage is within safe limits.

        Args:
            current_tokens: Current token count
            model: Model name to check against

        Returns:
            dict: Status information including usage percentage, warnings
        """
        model_config = self.get_model_config(model)
        effective_window = model_config.effective_context_window
        usage_percentage = (current_tokens / effective_window) * 100

        status = {
            "current_tokens": current_tokens,
            "effective_window": effective_window,
            "usage_percentage": usage_percentage,
            "warning": False,
            "critical": False,
            "recommendation": None
        }

        if usage_percentage >= self.critical_threshold * 100:
            status["critical"] = True
            status["recommendation"] = "REDUCE_CONTEXT: Token usage is critical. Consider summarization or context reduction."
        elif usage_percentage >= self.warning_threshold * 100:
            status["warning"] = True
            status["recommendation"] = "MONITOR: Token usage is approaching limit. Monitor carefully."

        return status

    def optimize_context(
        self,
        context_items: List[Any],
        model: Optional[str] = None,
        priority_callback: Optional[callable] = None
    ) -> List[Any]:
        """
        Optimize context items to fit within token limits.

        Args:
            context_items: List of context items (strings, messages, etc.)
            model: Model name for context window
            priority_callback: Optional function to assign priority scores to items

        Returns:
            list: Optimized list of context items
        """
        if not self.enable_token_optimization:
            return context_items

        model_config = self.get_model_config(model)
        target_tokens = min(self.target_token_count, model_config.effective_context_window)

        # Estimate current token count
        current_tokens = sum(
            self.estimate_token_count(str(item)) for item in context_items
        )

        if current_tokens <= target_tokens:
            return context_items

        # Need to reduce context
        # Assign priorities if callback provided, otherwise use insertion order
        if priority_callback:
            prioritized_items = sorted(
                enumerate(context_items),
                key=lambda x: priority_callback(x[1]),
                reverse=True
            )
        else:
            prioritized_items = list(enumerate(context_items))

        # Select items until we hit the target
        optimized_items = []
        accumulated_tokens = 0

        for idx, item in prioritized_items:
            item_tokens = self.estimate_token_count(str(item))
            if accumulated_tokens + item_tokens <= target_tokens:
                optimized_items.append((idx, item))
                accumulated_tokens += item_tokens
            else:
                break

        # Sort back to original order
        optimized_items.sort(key=lambda x: x[0])
        return [item for idx, item in optimized_items]

    def get_api_key(self, provider: ModelProvider) -> Optional[str]:
        """
        Get API key for a provider from environment variables.

        Args:
            provider: The model provider

        Returns:
            Optional[str]: API key if found, None otherwise
        """
        key_map = {
            ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            ModelProvider.OPENAI: "OPENAI_API_KEY",
            ModelProvider.AZURE_OPENAI: "AZURE_OPENAI_API_KEY",
            ModelProvider.GOOGLE: "GOOGLE_API_KEY",
        }
        return os.getenv(key_map.get(provider, ""))

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "default_model": self.default_model,
            "fallback_model": self.fallback_model,
            "enable_token_optimization": self.enable_token_optimization,
            "target_token_count": self.target_token_count,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "enable_response_caching": self.enable_response_caching,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_retries": self.max_retries,
            "enable_streaming": self.enable_streaming,
            "models": {
                name: {
                    "name": config.name,
                    "provider": config.provider.value,
                    "tier": config.tier.value,
                    "max_tokens": config.max_tokens,
                    "context_window": config.context_window,
                    "supports_caching": config.supports_caching,
                    "supports_tools": config.supports_tools,
                }
                for name, config in self.models.items()
            }
        }


# Global LLM config instance
_llm_config: Optional[LLMConfig] = None


def get_llm_config() -> LLMConfig:
    """Get the global LLM configuration instance (singleton)."""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config


def reset_llm_config():
    """Reset the global LLM configuration instance (mainly for testing)."""
    global _llm_config
    _llm_config = None
