import io
import pytest
from io import BytesIO
from pyboy.utils import (
    IntIOWrapper,
    IntIOInterface,
    PyBoyAssertException,
    PyBoyNotImplementedException,
    PyBoyOutOfBoundsException,
    dec_to_bcd,
    bcd_to_dec,
    AccessError,
    PillowImportError,
    WindowEvent,
    color_code,
)

def test_utilities_integration():
    """
    Test various uncovered scenarios in pyboy/utils.py:
      - Validate IntIOWrapper write method rejects non-int and out-of-bound values.
      - Ensure dec_to_bcd and bcd_to_dec perform a correct roundtrip conversion for both one-byte and two-byte widths.
      - Confirm that AccessError (specifically PillowImportError) behaves as expected by raising an exception
        when accessing restricted attributes and its bool conversion returns False.
      - Verify that WindowEvent.__str__ returns the correct event name.
    """
    # Test IntIOWrapper write method with invalid type and out-of-bound value.
    buf = io.BytesIO()
    wrapper = IntIOWrapper(buf)
    with pytest.raises(PyBoyAssertException, match="Input has to be of type 'int'"):
        wrapper.write("not an int")  # Should raise because input is not int.
    with pytest.raises(PyBoyOutOfBoundsException):
        wrapper.write(300)  # Should raise because 300 is out of allowed 0-255 range.
    
    # Test valid write and read.
    wrapper.write(128)
    buf.seek(0)
    # Check that the written byte is exactly 128.
    assert buf.read() == b'\x80', "IntIOWrapper did not write the correct byte."
    
    # Test conversion functions dec_to_bcd and bcd_to_dec.
    # One-byte conversion:
    bcd_val = dec_to_bcd(32, byte_width=1, byteorder="little")
    # For 32: tens = (3 << 4) = 48 (0x30) and units = 2, so BCD result is 0x32.
    assert bcd_val == 0x32, "BCD conversion failed for one byte input."
    assert bcd_to_dec(bcd_val, byte_width=1, byteorder="little") == 32, "Decimal conversion failed for one byte input."
    
    # Two-byte conversion:
    bcd_val2 = dec_to_bcd(1234, byte_width=2, byteorder="little")
    # For 1234, expected BCD (little-endian) is 0x1234.
    assert bcd_val2 == 0x1234, "BCD conversion failed for two bytes input."
    assert bcd_to_dec(bcd_val2, byte_width=2, byteorder="little") == 1234, "Decimal conversion failed for two bytes input."
    
    # Test AccessError behavior using PillowImportError.
    p_error = PillowImportError()
    assert not p_error, "Bool conversion of AccessError subclass should return False."
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        _ = p_error.some_attribute  # Accessing any attribute aside from defined ones must raise an error.
    
    # Test WindowEvent __str__ method.
    event = WindowEvent(WindowEvent.PAUSE)
    assert str(event) == "PAUSE", "WindowEvent.__str__ does not return the expected event name."

def test_int_io_interface_and_color_code():
    """
    Test that IntIOInterface methods throw PyBoyNotImplementedException
    and that the color_code function returns expected results.
    
    The IntIOInterface methods (write, read, seek, flush, new, commit,
    seek_frame, and tell) should raise a "Not implemented!" exception.
    
    The color_code function is tested by verifying its output for specific
    byte inputs and offsets.
    """
    # Test that abstract methods of IntIOInterface raise NotImplemented exceptions.
    dummy = IntIOInterface(None)
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.write(0)
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.read()
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.seek(0)
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.flush()
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.new()
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.commit()
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.seek_frame(0)
    with pytest.raises(PyBoyNotImplementedException, match="Not implemented!"):
        dummy.tell()
    
    # Test the color_code function.
    # For offset 0:
    # byte1 = 0x91 (binary 1001 0001), byte2 = 0x7C (binary 0111 1100)
    # (0x7C >> 0) & 1 = 0, and (0x91 >> 0) & 1 = 1, so expected color code is (0 << 1) + 1 = 1.
    result0 = color_code(0x91, 0x7C, 0)
    assert result0 == 1, "color_code did not return expected value for offset 0."
    
    # For offset 4:
    # (0x7C >> 4) & 1 = ((124 >> 4) & 1) = (7 & 1) = 1,
    # (0x91 >> 4) & 1 = ((145 >> 4) & 1) = (9 & 1) = 1,
    # so expected color code is (1 << 1) + 1 = 3.
    result4 = color_code(0x91, 0x7C, 4)
    assert result4 == 3, "color_code did not return expected value for offset 4."

def test_int_io_wrapper_multi_byte_handling():
    """
    Test the multi-byte write and read functions of IntIOWrapper.
    
    The test writes a 16-bit, a 32-bit, and a 64-bit integer into a BytesIO buffer 
    using write_16bit, write_32bit, and write_64bit, then reads them back in order using 
    read_16bit, read_32bit, and read_64bit to verify that the multi-byte operations are
    correctly handled.
    """
    buf = BytesIO()
    wrapper = IntIOWrapper(buf)
    # Set test values.
    val16 = 0xABCD         # 16-bit value: 43981 in decimal.
    val32 = 0x12345678     # 32-bit value: 305419896 in decimal.
    val64 = 0x1122334455667788  # 64-bit value: 1234605616436508552 in decimal.
    # Write multi-byte values in sequence.
    wrapper.write_16bit(val16)
    wrapper.write_32bit(val32)
    wrapper.write_64bit(val64)
    # Reset the buffer pointer to the beginning.
    buf.seek(0)
    # Read back the values (in the same order they were written).
    read16 = wrapper.read_16bit()
    read32 = wrapper.read_32bit()
    read64 = wrapper.read_64bit()
    # Assert that the read values match the values written.
    assert read16 == val16, "16-bit read value does not match the written value."
    assert read32 == val32, "32-bit read value does not match the written value."
    assert read64 == val64, "64-bit read value does not match the written value."
from pyboy.utils import WindowEvent, WindowEventMouse, PillowImportError
import pytest


def test_window_event_and_accesserror_setters():
    """
    Test additional functionalities:
      - Verify WindowEvent __int__ conversion and equality (__eq__) work as expected.
      - Check that WindowEventMouse correctly stores additional mouse-related attributes.
      - Confirm that AccessError subclass (PillowImportError) correctly raises exceptions when
        using its __setattribute__, __getitem__, and __setitem__ methods.
    """
    # Test WindowEvent __int__ and __eq__
    event_a = WindowEvent(WindowEvent.PRESS_BUTTON_A)
    assert int(event_a) == WindowEvent.PRESS_BUTTON_A, "WindowEvent __int__ conversion failed."
    event_a_copy = WindowEvent(WindowEvent.PRESS_BUTTON_A)
    assert event_a == event_a_copy, "WindowEvent equality check failed when comparing two events with the same id."
    # Also check comparison between event and int
    assert event_a == WindowEvent.PRESS_BUTTON_A, "WindowEvent equality with int value failed."
    
    # Test WindowEventMouse attributes
    mouse_event = WindowEventMouse(
        WindowEvent.RELEASE_BUTTON_A,
        window_id=2, 
        mouse_x=50, 
        mouse_y=60, 
        mouse_scroll_x=1, 
        mouse_scroll_y=-1, 
        mouse_button=1
    )
    assert mouse_event.window_id == 2, "WindowEventMouse window_id mismatch."
    assert mouse_event.mouse_x == 50, "WindowEventMouse mouse_x mismatch."
    assert mouse_event.mouse_y == 60, "WindowEventMouse mouse_y mismatch."
    assert mouse_event.mouse_scroll_x == 1, "WindowEventMouse mouse_scroll_x mismatch."
    assert mouse_event.mouse_scroll_y == -1, "WindowEventMouse mouse_scroll_y mismatch."
    assert mouse_event.mouse_button == 1, "WindowEventMouse mouse_button mismatch."
    
    # Test AccessError (via PillowImportError) __setattribute__, __getitem__, and __setitem__
    p_error = PillowImportError()
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        # Explicitly call __setattribute__ to test the restricted attribute setting.
        p_error.__setattribute__("new_attr", 10)
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        _ = p_error["key"]
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        p_error["key"] = "value"
import pytest
from pyboy.utils import WindowEvent, WindowEventMouse, PillowImportError


def test_window_event_and_accesserror_setters():
    """
    Test additional functionalities:
      - Verify WindowEvent __int__ conversion and equality (__eq__) work as expected.
      - Check that WindowEventMouse correctly stores additional mouse-related attributes.
      - Confirm that PillowImportError (an AccessError subclass) raises exceptions when
        its __setattribute__, __getitem__, or __setitem__ methods are used.
    """
    # Test WindowEvent __int__ and __eq__
    event_a = WindowEvent(WindowEvent.PRESS_BUTTON_A)
    assert int(event_a) == WindowEvent.PRESS_BUTTON_A, "WindowEvent __int__ conversion failed."
    event_a_copy = WindowEvent(WindowEvent.PRESS_BUTTON_A)
    assert event_a == event_a_copy, "WindowEvent equality check failed when comparing two events with the same id."
    assert event_a == WindowEvent.PRESS_BUTTON_A, "WindowEvent equality with int value failed."

    # Test WindowEventMouse attributes
    mouse_event = WindowEventMouse(
        WindowEvent.RELEASE_BUTTON_A,
        window_id=2, 
        mouse_x=50, 
        mouse_y=60, 
        mouse_scroll_x=1, 
        mouse_scroll_y=-1, 
        mouse_button=1
    )
    assert mouse_event.window_id == 2, "WindowEventMouse window_id mismatch."
    assert mouse_event.mouse_x == 50, "WindowEventMouse mouse_x mismatch."
    assert mouse_event.mouse_y == 60, "WindowEventMouse mouse_y mismatch."
    assert mouse_event.mouse_scroll_x == 1, "WindowEventMouse mouse_scroll_x mismatch."
    assert mouse_event.mouse_scroll_y == -1, "WindowEventMouse mouse_scroll_y mismatch."
    assert mouse_event.mouse_button == 1, "WindowEventMouse mouse_button mismatch."
    
    # Test AccessError behavior via PillowImportError
    p_error = PillowImportError()
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        # Test __setattribute__
        p_error.__setattribute__("new_attr", 10)
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        # Test __getitem__
        _ = p_error["key"]
    with pytest.raises(p_error.exception_type, match=p_error.exception_message):
        # Test __setitem__
        p_error["key"] = "value"
