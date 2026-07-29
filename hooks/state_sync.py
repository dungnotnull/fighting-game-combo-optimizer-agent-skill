"""
State Synchronization Module — Manage and synchronize state across skill executions
Provides state management with scopes, validation, and synchronization capabilities.
"""

import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Callable, TypeVar
from enum import Enum
import threading
from pathlib import Path
import logging

logger = logging.getLogger("fighting-game-combo-optimizer")


class StateScope(str, Enum):
    """Scope levels for state management."""
    SESSION = "session"  # State for the current session
    TASK = "task"  # State for the current task
    SKILL = "skill"  # State for the current skill execution
    GLOBAL = "global"  # Global state across all sessions


class StateValidationStatus(str, Enum):
    """Status of state validation."""
    VALID = "valid"
    INVALID = "invalid"
    STALE = "stale"
    CONFLICT = "conflict"


@dataclass
class StateEntry:
    """
    A single state entry with metadata and validation.
    """
    key: str
    value: Any
    scope: StateScope
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[float] = None  # Time-to-live in seconds

    def __post_init__(self):
        """Compute checksum after initialization."""
        if self.checksum is None:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute SHA256 checksum of the value."""
        value_str = json.dumps(self.value, sort_keys=True, default=str)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]

    def is_expired(self) -> bool:
        """Check if this entry has expired (TTL)."""
        if self.ttl is None:
            return False
        return (time.time() - self.timestamp) > self.ttl

    def increment_version(self):
        """Increment the version and update checksum."""
        self.version += 1
        self.checksum = self._compute_checksum()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "scope": self.scope.value,
            "timestamp": self.timestamp,
            "version": self.version,
            "checksum": self.checksum,
            "metadata": self.metadata,
            "ttl": self.ttl
        }


@dataclass
class StateValidationResult:
    """
    Result of state validation.
    """
    status: StateValidationStatus
    key: str
    expected_version: Optional[int] = None
    actual_version: Optional[int] = None
    expected_checksum: Optional[str] = None
    actual_checksum: Optional[str] = None
    message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class StateManager:
    """
    Manages application state with scopes, validation, and synchronization.
    Thread-safe implementation for concurrent access.
    """

    def __init__(self, persist_to_disk: bool = False, persist_path: Optional[str] = None):
        """
        Initialize the state manager.

        Args:
            persist_to_disk: Whether to persist state to disk
            persist_path: Path for state persistence file
        """
        # State storage organized by scope
        self._state: Dict[StateScope, Dict[str, StateEntry]] = {
            scope: {} for scope in StateScope
        }

        # Validation callbacks
        self._validators: Dict[str, Callable[[Any], bool]] = {}

        # Change subscriptions
        self._subscriptions: Dict[str, List[Callable]] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Persistence
        self._persist_to_disk = persist_to_disk
        self._persist_path = Path(persist_path) if persist_path else None

        # Statistics
        self._stats = {
            "gets": 0,
            "sets": 0,
            "deletes": 0,
            "validations": 0,
            "conflicts": 0,
            "syncs": 0
        }

        # Load persisted state if configured
        if self._persist_to_disk and self._persist_path and self._persist_path.exists():
            self._load_from_disk()

    def get(self, key: str, scope: StateScope = StateScope.SESSION, default: Any = None) -> Any:
        """
        Get a value from state.

        Args:
            key: State key
            scope: State scope
            default: Default value if key not found

        Returns:
            The value or default if not found
        """
        with self._lock:
            self._stats["gets"] += 1
            scope_state = self._state[scope]

            if key not in scope_state:
                return default

            entry = scope_state[key]

            # Check expiration
            if entry.is_expired():
                del scope_state[key]
                return default

            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        scope: StateScope = StateScope.SESSION,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set a value in state.

        Args:
            key: State key
            value: Value to set
            scope: State scope
            ttl: Time-to-live in seconds
            metadata: Optional metadata

        Returns:
            bool: True if set succeeded
        """
        with self._lock:
            self._stats["sets"] += 1
            scope_state = self._state[scope]

            # Get existing entry if any
            existing = scope_state.get(key)

            if existing:
                # Update existing entry
                existing.value = value
                existing.increment_version()
                existing.timestamp = time.time()
                existing.ttl = ttl
                if metadata:
                    existing.metadata.update(metadata)
            else:
                # Create new entry
                entry = StateEntry(
                    key=key,
                    value=value,
                    scope=scope,
                    ttl=ttl,
                    metadata=metadata or {}
                )
                scope_state[key] = entry

            # Notify subscribers
            self._notify_subscribers(key, value, scope)

            # Persist if configured
            if self._persist_to_disk:
                self._save_to_disk()

            return True

    def delete(self, key: str, scope: StateScope = StateScope.SESSION) -> bool:
        """
        Delete a value from state.

        Args:
            key: State key
            scope: State scope

        Returns:
            bool: True if key was deleted
        """
        with self._lock:
            self._stats["deletes"] += 1
            scope_state = self._state[scope]

            if key in scope_state:
                del scope_state[key]

                # Persist if configured
                if self._persist_to_disk:
                    self._save_to_disk()

                return True

            return False

    def validate(self, key: str, scope: StateScope = StateScope.SESSION) -> StateValidationResult:
        """
        Validate a state entry.

        Args:
            key: State key
            scope: State scope

        Returns:
            StateValidationResult: Validation result
        """
        with self._lock:
            self._stats["validations"] += 1

            entry = self._state[scope].get(key)
            if not entry:
                return StateValidationResult(
                    status=StateValidationStatus.INVALID,
                    key=key,
                    message=f"Key '{key}' not found in scope '{scope.value}'"
                )

            # Check expiration
            if entry.is_expired():
                return StateValidationResult(
                    status=StateValidationStatus.STALE,
                    key=key,
                    actual_version=entry.version,
                    actual_checksum=entry.checksum,
                    message=f"Entry for '{key}' has expired"
                )

            # Run custom validator if registered
            if key in self._validators:
                try:
                    if not self._validators[key](entry.value):
                        return StateValidationResult(
                            status=StateValidationStatus.INVALID,
                            key=key,
                            actual_version=entry.version,
                            actual_checksum=entry.checksum,
                            message=f"Custom validation failed for '{key}'"
                        )
                except Exception as e:
                    logger.error(f"Validator error for '{key}': {e}")
                    return StateValidationResult(
                        status=StateValidationStatus.INVALID,
                        key=key,
                        message=f"Validator error: {e}"
                    )

            return StateValidationResult(
                status=StateValidationStatus.VALID,
                key=key,
                actual_version=entry.version,
                actual_checksum=entry.checksum
            )

    def register_validator(self, key: str, validator: Callable[[Any], bool]):
        """
        Register a validation function for a state key.

        Args:
            key: State key to validate
            validator: Function that takes value and returns bool
        """
        self._validators[key] = validator

    def subscribe(self, key: str, callback: Callable[[str, Any, StateScope], None]):
        """
        Subscribe to changes for a state key.

        Args:
            key: State key to watch
            callback: Function called when key changes
        """
        if key not in self._subscriptions:
            self._subscriptions[key] = []
        self._subscriptions[key].append(callback)

    def unsubscribe(self, key: str, callback: Optional[Callable] = None):
        """
        Unsubscribe from state key changes.

        Args:
            key: State key to unsubscribe from
            callback: Specific callback to remove (if None, removes all)
        """
        if callback:
            if key in self._subscriptions:
                self._subscriptions[key] = [
                    cb for cb in self._subscriptions[key]
                    if cb != callback
                ]
        else:
            self._subscriptions.pop(key, None)

    def _notify_subscribers(self, key: str, value: Any, scope: StateScope):
        """Notify subscribers of a state change."""
        if key in self._subscriptions:
            for callback in self._subscriptions[key]:
                try:
                    callback(key, value, scope)
                except Exception as e:
                    logger.error(f"Subscriber callback error for '{key}': {e}")

    def sync_state(
        self,
        source_scope: StateScope,
        target_scope: StateScope,
        keys: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> int:
        """
        Synchronize state between scopes.

        Args:
            source_scope: Source scope
            target_scope: Target scope
            keys: Specific keys to sync (if None, syncs all)
            overwrite: Whether to overwrite existing target values

        Returns:
            int: Number of keys synced
        """
        with self._lock:
            self._stats["syncs"] += 1
            source_state = self._state[source_scope]
            target_state = self._state[target_scope]

            keys_to_sync = keys if keys else list(source_state.keys())
            synced_count = 0

            for key in keys_to_sync:
                if key not in source_state:
                    continue

                if key in target_state and not overwrite:
                    # Check for conflict
                    self._stats["conflicts"] += 1
                    logger.warning(
                        f"State sync conflict for '{key}': "
                        f"exists in target scope and overwrite=False"
                    )
                    continue

                # Copy entry
                entry = source_state[key]
                target_state[key] = StateEntry(
                    key=entry.key,
                    value=entry.value,
                    scope=target_scope,
                    timestamp=entry.timestamp,
                    version=entry.version,
                    checksum=entry.checksum,
                    metadata=entry.metadata.copy(),
                    ttl=entry.ttl
                )
                synced_count += 1

            # Persist if configured
            if self._persist_to_disk and synced_count > 0:
                self._save_to_disk()

            return synced_count

    def clear_scope(self, scope: StateScope):
        """Clear all state in a scope."""
        with self._lock:
            self._state[scope].clear()

            if self._persist_to_disk:
                self._save_to_disk()

    def get_all(self, scope: StateScope) -> Dict[str, Any]:
        """Get all state in a scope as a dictionary."""
        with self._lock:
            return {
                key: entry.value
                for key, entry in self._state[scope].items()
                if not entry.is_expired()
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats["entries"] = {
                scope.value: len(state_dict)
                for scope, state_dict in self._state.items()
            }
            return stats

    def export_state(self, scope: StateScope) -> Dict[str, Any]:
        """Export state for a scope."""
        with self._lock:
            return {
                key: entry.to_dict()
                for key, entry in self._state[scope].items()
            }

    def _save_to_disk(self):
        """Persist state to disk."""
        if not self._persist_path:
            return

        try:
            export_data = {}
            for scope in StateScope:
                export_data[scope.value] = self.export_state(scope)

            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persist_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.debug(f"State persisted to {self._persist_path}")

        except Exception as e:
            logger.error(f"Failed to persist state to disk: {e}")

    def _load_from_disk(self):
        """Load state from disk."""
        if not self._persist_path or not self._persist_path.exists():
            return

        try:
            with open(self._persist_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            for scope_value, state_data in import_data.items():
                scope = StateScope(scope_value)
                for key, entry_data in state_data.items():
                    entry = StateEntry(
                        key=entry_data["key"],
                        value=entry_data["value"],
                        scope=scope,
                        timestamp=entry_data.get("timestamp", time.time()),
                        version=entry_data.get("version", 1),
                        checksum=entry_data.get("checksum"),
                        metadata=entry_data.get("metadata", {}),
                        ttl=entry_data.get("ttl")
                    )
                    self._state[scope][key] = entry

            logger.debug(f"State loaded from {self._persist_path}")

        except Exception as e:
            logger.error(f"Failed to load state from disk: {e}")


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the global state manager instance (singleton)."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def create_state_scope(scope: StateScope) -> StateScope:
    """
    Create and return a state scope (for convenience).

    Args:
        scope: The scope to create

    Returns:
        StateScope: The created scope
    """
    return scope


def sync_state(
    source_scope: StateScope,
    target_scope: StateScope,
    keys: Optional[List[str]] = None,
    overwrite: bool = False
) -> int:
    """
    Synchronize state between scopes (convenience function).

    Args:
        source_scope: Source scope
        target_scope: Target scope
        keys: Specific keys to sync
        overwrite: Whether to overwrite existing values

    Returns:
        int: Number of keys synced
    """
    return get_state_manager().sync_state(
        source_scope=source_scope,
        target_scope=target_scope,
        keys=keys,
        overwrite=overwrite
    )


def reset_state_manager():
    """Reset the global state manager (mainly for testing)."""
    global _state_manager
    _state_manager = None
