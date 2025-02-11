import pytest

from pyboy.utils import WindowEvent


def test_window_event_equality_with_window_event():
    event1 = WindowEvent(WindowEvent.PAUSE)
    event2 = WindowEvent(WindowEvent.PAUSE)
    event3 = WindowEvent(WindowEvent.QUIT)
    assert event1 == event2
    assert event1 != event3


def test_window_event_equality_with_int():
    event = WindowEvent(WindowEvent.QUIT)
    assert event == WindowEvent.QUIT
    assert event != WindowEvent.PAUSE


@pytest.mark.parametrize("invalid_value", ["string", None, 3.14, []])
def test_window_event_inequality_with_other_types(invalid_value):
    event = WindowEvent(WindowEvent.PAUSE)
    assert event != invalid_value


def test_window_event_integer_conversion():
    event = WindowEvent(WindowEvent.PAUSE)
    assert int(event) == WindowEvent.PAUSE


@pytest.mark.parametrize(
    "event_int, event_name",
    [
        (WindowEvent.PAUSE, "PAUSE"),
        (WindowEvent.QUIT, "QUIT"),
    ],
)
def test_window_event_string_conversion(event_int, event_name):
    event = WindowEvent(event_int)
    assert str(event) == event_name


def test_window_event_eq_against_other_class():
    event = WindowEvent(1)
    assert event.__eq__(1) is True
    assert event.__eq__(WindowEvent(1)) is True

    # Testing a==b and b==a. This is done by Python when returning 'NotImplemented'
    class Other:
        pass

    assert event.__eq__(Other()) is NotImplemented
    # Doesn't work, because neither class has an __eq__ implementation that fits
    assert not event == Other()

    class AnOther:
        def __init__(self, value):
            self.value = value

        def __eq__(self, value):
            return int(value) == self.value

    # Although WindowEvent doesn't recognize AnOther,
    assert event.__eq__(AnOther(1)) is NotImplemented
    # AnOther recognizes equality to WindowEvent.
    assert event == AnOther(1)
    assert event != AnOther(2)
