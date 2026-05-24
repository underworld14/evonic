"""Minimal synchronous event bus for inter-component communication.

Provides `on()`, `off()`, `emit()`, and `clear()` for registering callbacks
and firing events. Used by UserMixin for auto-register hooks and ERP sync.

Usage:
    from backend.events import on, emit

    def handle_user_created(data):
        print(f"User created: {data['user_id']}")

    on('user.created', handle_user_created)
    emit('user.created', {'user_id': 'abc-123'})
"""
import logging

log = logging.getLogger(__name__)

_listeners: dict = {}


def on(event_name: str, callback: callable):
    """Register a callback for an event."""
    _listeners.setdefault(event_name, []).append(callback)


def off(event_name: str, callback: callable):
    """Remove a callback registration."""
    if event_name in _listeners:
        _listeners[event_name] = [cb for cb in _listeners[event_name] if cb != callback]


def emit(event_name: str, data: dict = None):
    """Emit an event, calling all registered callbacks with the given data."""
    for cb in _listeners.get(event_name, []):
        try:
            cb(data)
        except Exception as e:
            log.error(f"Event handler {cb.__name__} failed for {event_name}: {e}")


def clear():
    """Clear all listeners (for testing)."""
    _listeners.clear()
