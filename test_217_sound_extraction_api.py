import sys
import os
import pyboy
import time
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt

# Add the current directory to the path so we can import pyboy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import only the Sound class directly
from pyboy.core.sound import Sound

def test_sound_extraction_api():
    """
    Comprehensive test for the sound extraction API (Issue #217).
    Tests different sound scenarios and verifies the API works correctly.
    """
    print("Testing Sound Extraction API (Issue #217)")
    print("========================================")
    
    # Initialize PyBoy with a ROM that produces sound
    rom_path = "roms/Tetris Attack (USA) (SGB Enhanced).gb"
    pyboy_instance = pyboy.PyBoy(rom_path, sound_emulated=True, sound_volume=100)
    
    # Skip boot logo and get to title screen where music should play
    print("\nSkipping to title screen...")
    for _ in range(180):  # Skip about 3 seconds
        pyboy_instance.tick()
    
    # Press start to get to the game
    print("Pressing START button...")
    pyboy_instance.button_press("START")
    pyboy_instance.tick()
    pyboy_instance.button_release("START")
    
    # Let the game run for a bit to get some music/sound
    print("\nCollecting sound data...")
    all_left_samples = []
    all_right_samples = []
    non_zero_samples = 0
    
    # Run for 10 seconds (600 frames at 60fps)
    for frame in range(600):
        pyboy_instance.tick()
        
        # Press some buttons occasionally to trigger sound effects
        if frame % 60 == 0:  # Every second
            pyboy_instance.button_press("A")
            pyboy_instance.tick()
            pyboy_instance.button_release("A")
        
        # Get the sound samples
        _, left_channel, right_channel = pyboy_instance.sound.get_current_frame_samples()
        
        # Count non-zero samples to verify we're getting sound
        non_zero_samples += np.count_nonzero(left_channel) + np.count_nonzero(right_channel)
        
        all_left_samples.extend(left_channel)
        all_right_samples.extend(right_channel)
        
        if frame % 60 == 0:  # Print progress every second
            print(f"Frame {frame}/600 - Non-zero samples so far: {non_zero_samples}")
    
    print(f"\nTotal non-zero samples: {non_zero_samples}")
    
    # Convert to numpy arrays and normalize to 16-bit range
    left_samples = np.array(all_left_samples, dtype=np.float32)
    right_samples = np.array(all_right_samples, dtype=np.float32)
    
    # Normalize if we have non-zero samples
    if np.max(np.abs(left_samples)) > 0:
        left_samples = (left_samples / np.max(np.abs(left_samples)) * 32767).astype(np.int16)
    if np.max(np.abs(right_samples)) > 0:
        right_samples = (right_samples / np.max(np.abs(right_samples)) * 32767).astype(np.int16)
    
    # Create stereo audio
    stereo_samples = np.empty(len(left_samples) + len(right_samples), dtype=np.int16)
    stereo_samples[0::2] = left_samples
    stereo_samples[1::2] = right_samples
    
    # Save to WAV file
    output_file = "test_sound_output.wav"
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(pyboy_instance.sound.sample_rate)
        wav_file.writeframes(stereo_samples.tobytes())
    
    print(f"\nSaved audio file: {os.path.abspath(output_file)}")
    print(f"Sample rate: {pyboy_instance.sound.sample_rate} Hz")
    print(f"Duration: {len(stereo_samples) / (2 * pyboy_instance.sound.sample_rate):.2f} seconds")
    print(f"Total samples: {len(stereo_samples)}")
    
    # Plot a small section of the waveform to verify we have actual audio data
    plt.figure(figsize=(15, 5))
    plt.plot(left_samples[:1000])  # Plot first 1000 samples
    plt.title("First 1000 samples of left channel")
    plt.savefig("waveform.png")
    plt.close()
    
    pyboy_instance.stop()
    print("\nSound extraction API test complete!")

if __name__ == "__main__":
    test_sound_extraction_api() 