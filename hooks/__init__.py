"""
Hooks Module — fighting-game-combo-optimizer
Provides lifecycle hooks, state synchronization, and event emission for the skill execution system.
"""

from .lifecycle import (
    LifecycleHook,
    LifecyclePhase,
    register_lifecycle_hook,
    execute_pre_hooks,
    execute_post_hooks,
    get_hook_manager
)
from .state_sync import (
    StateManager,
    StateScope,
    get_state_manager,
    create_state_scope,
    sync_state
)
from .event_emitter import (
    EventEmitter,
    EventType,
    get_event_emitter,
    emit_event,
    subscribe_to_event,
    unsubscribe_from_event
)

__all__ = [
    # Lifecycle
    "LifecycleHook",
    "LifecyclePhase",
    "register_lifecycle_hook",
    "execute_pre_hooks",
    "execute_post_hooks",
    "get_hook_manager",

    # State Sync
    "StateManager",
    "StateScope",
    "get_state_manager",
    "create_state_scope",
    "sync_state",

    # Event Emitter
    "EventEmitter",
    "EventType",
    "get_event_emitter",
    "emit_event",
    "subscribe_to_event",
    "unsubscribe_from_event"
]
