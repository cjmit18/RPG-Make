import pytest
from game_sys.hooks.hooks import HookDispatcher, hook_dispatcher


def test_hookdispatcher_register_and_fire():
    hd = HookDispatcher()
    events = []

    def handler(**kwargs):
        events.append(kwargs)

    # Register the handler and fire the event
    hd.register('test.event', handler)
    hd.fire('test.event', foo=42, bar='baz')

    assert events == [{'foo': 42, 'bar': 'baz'}]


def test_hookdispatcher_unregister():
    hd = HookDispatcher()
    events = []

    def handler(**kwargs):
        events.append(kwargs)

    # Register and then unregister
    hd.register('test.event', handler)
    hd.unregister('test.event', handler)
    hd.fire('test.event', foo=1)

    # Handler should not be called after unregister
    assert events == []


def test_shared_hook_dispatcher():
    # Using the global hook_dispatcher
    events = []

    def shared_handler(**kwargs):
        events.append(kwargs)

    # Register on the shared dispatcher
    hook_dispatcher.register('shared.event', shared_handler)
    hook_dispatcher.fire('shared.event', baz=99)

    assert events == [{'baz': 99}]

    # Clean up
    hook_dispatcher.unregister('shared.event', shared_handler)
