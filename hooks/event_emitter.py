"""
Event Emitter Module — Event-driven architecture for skill execution
Provides event emission, subscription, and handling capabilities with error handling and filtering.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger("fighting-game-combo-optimizer")


class EventType(str, Enum):
    """Standard event types for the system."""
    SKILL_INVOKED = "skill_invoked"
    SKILL_COMPLETED = "skill_completed"
    SKILL_FAILED = "skill_failed"
    SKILL_RETRY = "skill_retry"
    GATE_ENTERED = "gate_entered"
    GATE_PASSED = "gate_passed"
    GATE_FAILED = "gate_failed"
    DATA_FETCHED = "data_fetched"
    DATA_VALIDATED = "data_validated"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    EVIDENCE_COLLECTED = "evidence_collected"
    OUTPUT_GENERATED = "output_generated"
    STATE_UPDATED = "state_updated"
    HOOK_EXECUTED = "hook_executed"
    ERROR_OCCURRED = "error_occurred"
    CUSTOM = "custom"


@dataclass
class Event:
    """
    An event with payload and metadata.
    """
    type: EventType
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher priority events handled first

    def __post_init__(self):
        """Generate correlation ID if not provided."""
        if self.correlation_id is None:
            import uuid
            self.correlation_id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
            "priority": self.priority
        }


@dataclass
class EventSubscription:
    """
    A subscription to events with filtering and handling.
    """
    event_type: EventType
    handler: Callable[[Event], Any]
    filter_func: Optional[Callable[[Event], bool]] = None
    enabled: bool = True
    once: bool = False  # If True, unsubscribe after first trigger
    max_retries: int = 0
    retry_delay: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Statistics
    executions: int = 0
    failures: int = 0
    last_execution: Optional[float] = None

    def should_handle(self, event: Event) -> bool:
        """Check if this subscription should handle the event."""
        if not self.enabled:
            return False

        if self.event_type != event.type and self.event_type != EventType.CUSTOM:
            return False

        if self.filter_func and not self.filter_func(event):
            return False

        return True

    def execute(self, event: Event) -> Any:
        """Execute the handler for an event."""
        self.executions += 1
        self.last_execution = time.time()

        try:
            result = self.handler(event)
            return result
        except Exception as e:
            self.failures += 1
            logger.error(f"Event handler error for {self.event_type.value}: {e}")
            raise


class EventEmitter:
    """
    Manages event emission, subscription, and handling.
    Thread-safe implementation with priority queues and error handling.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize the event emitter.

        Args:
            async_mode: If True, events are handled asynchronously
        """
        # Subscriptions organized by event type
        self._subscriptions: Dict[EventType, List[EventSubscription]] = {
            event_type: [] for event_type in EventType
        }

        # Event history (circular buffer)
        self._history: List[Event] = []
        self._history_size = 1000

        # Thread safety
        self._lock = threading.RLock()

        # Async handling
        self._async_mode = async_mode
        self._event_queue: List[Event] = []
        self._queue_lock = threading.Lock()

        # Statistics
        self._stats = {
            "events_emitted": 0,
            "events_handled": 0,
            "handling_errors": 0,
            "active_subscriptions": 0
        }

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], Any],
        filter_func: Optional[Callable[[Event], bool]] = None,
        enabled: bool = True,
        once: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventSubscription:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
            filter_func: Optional filter function for events
            enabled: Whether subscription is enabled
            once: If True, unsubscribe after first trigger
            metadata: Optional metadata for the subscription

        Returns:
            EventSubscription: The created subscription
        """
        subscription = EventSubscription(
            event_type=event_type,
            handler=handler,
            filter_func=filter_func,
            enabled=enabled,
            once=once,
            metadata=metadata or {}
        )

        with self._lock:
            self._subscriptions[event_type].append(subscription)
            self._stats["active_subscriptions"] = sum(
                len(subs) for subs in self._subscriptions.values()
            )

        logger.debug(f"Subscribed to event type '{event_type.value}'")
        return subscription

    def unsubscribe(self, subscription: EventSubscription) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription: The subscription to remove

        Returns:
            bool: True if subscription was found and removed
        """
        with self._lock:
            event_type = subscription.event_type
            if event_type in self._subscriptions:
                try:
                    self._subscriptions[event_type].remove(subscription)
                    self._stats["active_subscriptions"] = sum(
                        len(subs) for subs in self._subscriptions.values()
                    )
                    logger.debug(f"Unsubscribed from event type '{event_type.value}'")
                    return True
                except ValueError:
                    pass

        return False

    def emit(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> Event:
        """
        Emit an event to all subscribers.

        Args:
            event_type: Type of event to emit
            payload: Event payload data
            source: Optional source identifier
            correlation_id: Optional correlation ID
            metadata: Optional event metadata
            priority: Event priority (higher = handled first)

        Returns:
            Event: The emitted event
        """
        event = Event(
            type=event_type,
            payload=payload,
            source=source,
            correlation_id=correlation_id,
            metadata=metadata or {},
            priority=priority
        )

        with self._lock:
            self._stats["events_emitted"] += 1

            # Add to history
            self._history.append(event)
            if len(self._history) > self._history_size:
                self._history.pop(0)

            # Handle synchronously or queue for async
            if self._async_mode:
                with self._queue_lock:
                    self._event_queue.append(event)
                # Sort queue by priority
                self._event_queue.sort(key=lambda e: e.priority, reverse=True)
            else:
                self._handle_event(event)

        return event

    def _handle_event(self, event: Event):
        """Handle an event by executing subscriptions."""
        # Get subscriptions for this event type
        subscriptions = self._subscriptions.get(event.type, [])
        subscriptions = subscriptions + self._subscriptions.get(EventType.CUSTOM, [])

        # Sort by priority (if we had subscription priority)
        subscriptions = [s for s in subscriptions if s.should_handle(event)]

        for subscription in subscriptions:
            try:
                subscription.execute(event)
                self._stats["events_handled"] += 1

                # Unsubscribe if once=True
                if subscription.once:
                    self.unsubscribe(subscription)

            except Exception as e:
                self._stats["handling_errors"] += 1
                logger.error(f"Error handling event {event.type.value}: {e}")

                # Retry logic
                if subscription.max_retries > 0:
                    subscription.max_retries -= 1
                    if subscription.retry_delay > 0:
                        time.sleep(subscription.retry_delay)

    def process_queue(self) -> int:
        """
        Process queued events (for async mode).

        Returns:
            int: Number of events processed
        """
        if not self._async_mode:
            return 0

        processed = 0

        with self._queue_lock:
            while self._event_queue:
                event = self._event_queue.pop(0)
                self._handle_event(event)
                processed += 1

        return processed

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: Optional[int] = None,
        since: Optional[float] = None
    ) -> List[Event]:
        """
        Get event history.

        Args:
            event_type: Filter by event type
            limit: Maximum number of events to return
            since: Only return events after this timestamp

        Returns:
            list: Filtered event history
        """
        with self._lock:
            history = self._history[:]

        if event_type:
            history = [e for e in history if e.type == event_type]

        if since:
            history = [e for e in history if e.timestamp >= since]

        if limit:
            history = history[-limit:]

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """Get emitter statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats["queue_size"] = len(self._event_queue)
            stats["history_size"] = len(self._history)
            stats["subscriptions_by_type"] = {
                event_type.value: len(subs)
                for event_type, subs in self._subscriptions.items()
            }
            return stats

    def clear_history(self):
        """Clear event history."""
        with self._lock:
            self._history.clear()


# Global event emitter instance
_event_emitter: Optional[EventEmitter] = None


def get_event_emitter() -> EventEmitter:
    """Get the global event emitter instance (singleton)."""
    global _event_emitter
    if _event_emitter is None:
        _event_emitter = EventEmitter()
    return _event_emitter


def emit_event(
    event_type: EventType,
    payload: Dict[str, Any],
    source: Optional[str] = None,
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    priority: int = 0
) -> Event:
    """
    Emit an event (convenience function).

    Args:
        event_type: Type of event to emit
        payload: Event payload data
        source: Optional source identifier
        correlation_id: Optional correlation ID
        metadata: Optional event metadata
        priority: Event priority

    Returns:
        Event: The emitted event
    """
    return get_event_emitter().emit(
        event_type=event_type,
        payload=payload,
        source=source,
        correlation_id=correlation_id,
        metadata=metadata,
        priority=priority
    )


def subscribe_to_event(
    event_type: EventType,
    handler: Callable[[Event], Any],
    filter_func: Optional[Callable[[Event], bool]] = None,
    once: bool = False
) -> EventSubscription:
    """
    Subscribe to events (convenience function).

    Args:
        event_type: Type of event to subscribe to
        handler: Function to call when event occurs
        filter_func: Optional filter function
        once: If True, unsubscribe after first trigger

    Returns:
        EventSubscription: The created subscription
    """
    return get_event_emitter().subscribe(
        event_type=event_type,
        handler=handler,
        filter_func=filter_func,
        once=once
    )


def unsubscribe_from_event(subscription: EventSubscription) -> bool:
    """
    Unsubscribe from events (convenience function).

    Args:
        subscription: The subscription to remove

    Returns:
        bool: True if subscription was removed
    """
    return get_event_emitter().unsubscribe(subscription)


def reset_event_emitter():
    """Reset the global event emitter (mainly for testing)."""
    global _event_emitter
    _event_emitter = None


# Event decorators for common patterns
def on_event(event_type: EventType):
    """Decorator to register a function as an event handler."""
    def decorator(func: Callable[[Event], Any]):
        subscribe_to_event(event_type, func)
        return func
    return decorator


def once_on_event(event_type: EventType):
    """Decorator to register a function as a one-time event handler."""
    def decorator(func: Callable[[Event], Any]):
        subscribe_to_event(event_type, func, once=True)
        return func
    return decorator
