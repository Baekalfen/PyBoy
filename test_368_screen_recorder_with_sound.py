import pyboy
import time
import os
import numpy as np
import wave
import struct
from PIL import Image
import io

def test_screen_recorder_with_sound():
    """
    Test for the screen recorder with sound support (Issue #368).
    Demonstrates how to integrate the sound extraction API with the screen recorder.
    """
    print("Testing Screen Recorder with Sound Support (Issue #368)")
    print("=====================================================")
    
    # Initialize PyBoy with a ROM that produces sound
    rom_path = "roms/Tetris Attack (USA) (SGB Enhanced).gb"  # Using available Tetris variant
    pyboy_instance = pyboy.PyBoy(rom_path, sound_emulated=True, sound_volume=100)
    
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize arrays to store frames and audio samples
    frames = []
    all_left_samples = []
    all_right_samples = []
    
    # Get sample rate for audio
    sample_rate = pyboy_instance.sound.sample_rate
    
    # Record for 3 seconds (180 frames at 60fps)
    print("Recording for 3 seconds...")
    for frame in range(180):
        # Tick the emulator
        pyboy_instance.tick()
        
        # Capture the screen
        screen = np.array(pyboy_instance.screen.image)  # Using the image property instead of screen_ndarray
        frames.append(screen.copy())
        
        # Get audio samples
        _, left_channel, right_channel = pyboy_instance.sound.get_current_frame_samples()
        all_left_samples.extend(left_channel)
        all_right_samples.extend(right_channel)
        
        # Print progress every 30 frames
        if frame % 30 == 0:
            print(f"Recorded {frame+1}/180 frames")
    
    # Stop the emulator
    pyboy_instance.stop()
    
    # Save frames as images
    print("\nSaving frames as images...")
    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        img.save(os.path.join(output_dir, f"frame_{i:04d}.png"))
    
    print(f"Saved {len(frames)} frames to {output_dir}")
    
    # Process audio samples
    print("\nProcessing audio samples...")
    
    # Convert to numpy arrays for easier manipulation
    left_samples = np.array(all_left_samples, dtype=np.int16)
    right_samples = np.array(all_right_samples, dtype=np.int16)
    
    # Create stereo audio by interleaving left and right channels
    stereo_samples = np.empty(len(left_samples) + len(right_samples), dtype=np.int16)
    stereo_samples[0::2] = left_samples
    stereo_samples[1::2] = right_samples
    
    # Save to WAV file
    audio_file = os.path.join(output_dir, "audio.wav")
    with wave.open(audio_file, 'wb') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_samples.tobytes())
    
    print(f"Saved audio to {audio_file}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Duration: {len(stereo_samples) / sample_rate:.2f} seconds")
    
    # Demonstrate how to combine video and audio
    print("\nTo combine video and audio into a video file, you would use a library like FFmpeg:")
    print("ffmpeg -framerate 60 -i test_output/frame_%04d.png -i test_output/audio.wav -c:v libx264 -pix_fmt yuv420p -c:a aac test_output/output.mp4")
    
    print("\nScreen recorder with sound test complete!")
    print(f"Output files saved to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    test_screen_recorder_with_sound() 