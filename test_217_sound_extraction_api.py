import sys
import os
import pyboy
from pyboy.utils import WindowEvent
import time
import numpy as np
import wave
import struct
import json

# Add the current directory to the path so we can import pyboy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sound_extraction_api():
    """
    Comprehensive test for the sound extraction API (Issue #217).
    Tests different sound scenarios and verifies the API works correctly.
    """
    print("\n=== Sound Extraction API Test (Issue #217) ===")
    print("This test verifies that PyBoy can capture audio from GameBoy games.")    
    
    # Check if ROM directory exists
    rom_dir = "roms"
    if not os.path.exists(rom_dir):
        print(f"Error: ROM directory '{rom_dir}' not found")
        return
        
    # Initialize PyBoy with a ROM that produces sound
    rom_path = os.path.join(rom_dir, "Tetris (USA) (Rev-A).gb")
    if not os.path.exists(rom_path):
        print(f"Error: ROM file '{rom_path}' not found")
        return
        
    print(f"1. Loading ROM: {rom_path}")
    print("   Enabling sound emulation...")
    
    try:
        keybinds = json.dumps({
            "UP": "Up",
            "DOWN": "Down",
            "LEFT": "Left",
            "RIGHT": "Right",
            "A": "a",
            "B": "s",
            "START": "Return",
            "SELECT": "BackSpace",
        })
        pyboy_instance = pyboy.PyBoy(rom_path, sound_emulated=True, keybinds=keybinds, window="SDL2")
        # Set emulation speed to 1x (real-time)
        pyboy_instance.set_emulation_speed(1)
    except Exception as e:
        print(f"Error initializing PyBoy: {str(e)}")
        return
    
    print("\n2. Starting game sequence:")
    print("   - Pressing START to begin")
    print("   - Pressing A to start game")
    print("   - Waiting for sound effects...")
    
    # Start the game
    pyboy_instance.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.RELEASE_BUTTON_START)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.PRESS_BUTTON_A)
    pyboy_instance.tick()
    pyboy_instance.send_input(WindowEvent.RELEASE_BUTTON_A)
    pyboy_instance.tick()
    
    print("\n3. Monitoring sound output:")
    print("   Format: [Frame #] Samples captured | Max amplitude | Sound detected?")
    print("   " + "-" * 60)
    
    # Now run the emulation and check for sound
    non_zero_samples = False
    max_amplitude = 0
    sound_frame = 0
    
    for frame in range(1, 1200):  # Run for 20 seconds (60fps * 20)
        pyboy_instance.tick()
        sound_data = pyboy_instance.sound.ndarray
        
        frame_max = np.abs(sound_data).max() if sound_data.size > 0 else 0
        max_amplitude = max(max_amplitude, frame_max)
        
        if frame % 60 == 0 or (frame_max > 0 and not non_zero_samples):
            has_sound = "✓" if frame_max > 0 else " "
            print(f"   [Frame {frame:4d}] {len(sound_data):4d} samples | Amp: {frame_max:3d} | [{has_sound}]")
        
        # Record sound
        if not non_zero_samples and frame_max > 0:
            non_zero_samples = True
            sound_frame = frame
    


    print("\n4. Test Results:")
    print("   " + "-" * 60)
    if non_zero_samples:
        print(f"   ✓ Sound detected at frame {sound_frame} (after {sound_frame/60:.2f} seconds)")
        print(f"   ✓ Maximum amplitude recorded: {max_amplitude}")
        print(f"   ✓ Sound buffer size: {len(pyboy_instance.sound.ndarray)} samples")
        print("   ✓ Sound extraction API is working correctly")
    else:
        print("   ✗ No sound detected during test")
        print("   ✗ Sound extraction API may not be working correctly")


    
    # Test sound disabled state
    print("\n5. Verifying sound-disabled state:")
    print("   " + "-" * 60)
    pyboy_instance.stop()
    
    print("   Creating new instance with sound disabled...")
    pyboy_instance = pyboy.PyBoy(rom_path, sound_emulated=False, keybinds=keybinds)
    


    try:
        sound_data = pyboy_instance.sound.ndarray
        print("   ✗ ERROR: Should not be able to access sound when disabled")
    except pyboy.utils.PyBoyFeatureDisabledError:
        print("   ✓ Correctly blocked access to sound when disabled")
    pyboy_instance.stop()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_sound_extraction_api() 
#some snippets of code implemented by ai
