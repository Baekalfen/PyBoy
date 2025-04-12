# Sound Extraction API and Screen Recorder with Sound

This document describes the implementation of two related features:
1. Sound Extraction API (Issue #217)
2. Screen Recorder with Sound Support (Issue #368)

## Sound Extraction API

The Sound Extraction API provides a way to extract audio samples from the PyBoy emulator. This is useful for applications that need to access the emulator's audio output, such as recording gameplay with sound.

### API Method

The API consists of a single method in the `Sound` class:

# PyBoy Sound API Documentation

## Audio Frame Processing

### `get_current_frame_samples()`

This function is the core of the audio processing system. It extracts stereo audio samples from the emulator's audio buffer for the current frame.

#### Function Signature
```python
def get_current_frame_samples(self) -> tuple[int, list[int], list[int]]
```

#### Parameters
None

#### Returns
A tuple containing:
- `samples_per_frame`: Number of stereo samples in this frame
- `left_channel`: Array of left channel samples (16-bit signed integers)
- `right_channel`: Array of right channel samples (16-bit signed integers)

#### Implementation Details
1. **Emulation Check**
   - First verifies if emulation is active
   - Returns empty data if emulation is disabled

2. **Sample Calculation**
   - Calculates number of stereo samples: `samples_in_frame = self.audiobuffer_head // 2`
   - Division by 2 because each stereo sample contains both left and right channels

3. **Channel Separation**
   - Iterates through audio buffer in pairs
   - Even indices → left channel
   - Odd indices → right channel
   - Maintains proper stereo separation

4. **Usage Example**
```python
samples, left, right = pyboy.get_current_frame_samples()
if samples > 0:
    # Process left and right channels
    process_audio(left, right)
```

#### Technical Notes
- Sample format: 16-bit signed integers
- Buffer organization: Interleaved stereo (LRLRLR...)
- Frame timing: Synchronized with emulator frame rate
- Memory efficient: Processes only current frame's samples

### Usage Example

```python
import pyboy

# Initialize PyBoy with sound enabled
pyboy_instance = pyboy.PyBoy("game.gb", sound_emulated=True, sound_volume=100)

# Run the emulator for a few frames
for _ in range(10):
    pyboy_instance.tick()
    
    # Get the audio samples for this frame
    samples_count, left_channel, right_channel = pyboy_instance.sound.get_current_frame_samples()
    
    # Process the audio samples as needed
    print(f"Frame: {samples_count} samples")
    print(f"Left channel: {len(left_channel)} samples")
    print(f"Right channel: {len(right_channel)} samples")

# Clean up
pyboy_instance.stop()
```

### Notes

- The method returns samples for the current frame only. You need to call it each frame to get continuous audio.
- If sound is disabled, the method returns empty arrays.
- The samples are floating-point values that need to be normalized to 16-bit integers for WAV output.
- The sample rate is fixed at 48000 Hz in the current version.
- Use `sound_emulated=True` and `sound_volume=100` for best results.

## Screen Recorder with Sound Support

The Screen Recorder with Sound Support feature allows recording gameplay with audio. This is implemented by combining the screen capture functionality with the sound extraction API.

### Implementation Example

```python
import pyboy
import numpy as np
import wave
from PIL import Image
import os

# Initialize PyBoy with sound enabled
pyboy_instance = pyboy.PyBoy("game.gb", sound_emulated=True, sound_volume=100)

# Create output directory
output_dir = "recording_output"
os.makedirs(output_dir, exist_ok=True)

# Initialize arrays to store frames and audio samples
frames = []
all_left_samples = []
all_right_samples = []
non_zero_samples = 0

# Record for a few seconds
for frame in range(180):  # 3 seconds at 60fps
    # Tick the emulator
    pyboy_instance.tick()
    
    # Capture the screen
    screen = np.array(pyboy_instance.screen.image)
    frames.append(screen.copy())
    
    # Get audio samples
    _, left_channel, right_channel = pyboy_instance.sound.get_current_frame_samples()
    all_left_samples.extend(left_channel)
    all_right_samples.extend(right_channel)
    
    # Track non-zero samples to verify audio capture
    non_zero_samples += np.count_nonzero(left_channel) + np.count_nonzero(right_channel)

# Stop the emulator
pyboy_instance.stop()

# Save frames as images
for i, frame in enumerate(frames):
    img = Image.fromarray(frame)
    img.save(os.path.join(output_dir, f"frame_{i:04d}.png"))

# Process audio samples
left_samples = np.array(all_left_samples, dtype=np.float32)
right_samples = np.array(all_right_samples, dtype=np.float32)

# Normalize samples to 16-bit range
if np.max(np.abs(left_samples)) > 0:
    left_samples = (left_samples / np.max(np.abs(left_samples)) * 32767).astype(np.int16)
if np.max(np.abs(right_samples)) > 0:
    right_samples = (right_samples / np.max(np.abs(right_samples)) * 32767).astype(np.int16)

# Create stereo audio
stereo_samples = np.empty(len(left_samples) + len(right_samples), dtype=np.int16)
stereo_samples[0::2] = left_samples
stereo_samples[1::2] = right_samples

# Save to WAV file
audio_file = os.path.join(output_dir, "audio.wav")
with wave.open(audio_file, 'wb') as wav_file:
    wav_file.setnchannels(2)  # Stereo
    wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
    wav_file.setframerate(48000)  # Fixed sample rate
    wav_file.writeframes(stereo_samples.tobytes())
```

### Combining Video and Audio

To combine the video frames and audio into a single video file, you can use a tool like FFmpeg:

```bash
ffmpeg -framerate 60 -i recording_output/frame_%04d.png -i recording_output/audio.wav -c:v libx264 -pix_fmt yuv420p -c:a aac recording_output/output.mp4
```

## Testing

Two test scripts are provided to demonstrate the functionality:

1. `test_217_sound_extraction_api.py` - Tests the sound extraction API (Issue #217)
   - Tests basic API functionality
   - Verifies sound sample collection
   - Saves normalized audio to WAV
   - Includes waveform visualization
   - Tracks non-zero samples for verification

2. `test_368_screen_recorder_with_sound.py` - Tests the screen recorder with sound support (Issue #368)
   - Captures both video frames and audio
   - Handles game interaction to trigger sounds
   - Saves synchronized video and audio data
   - Provides progress tracking and verification

Run these scripts to verify that the features are working correctly.

## Dependencies

The implementation requires the following Python packages:
- numpy (for array operations and audio processing)
- Pillow (PIL) (for image handling)
- matplotlib (for waveform visualization)
- wave (for WAV file output)
- pyboy[all] (includes all optional dependencies)

For combining video and audio, FFmpeg is recommended.

## Troubleshooting

1. No sound in output:
   - Verify `sound_emulated=True` and `sound_volume=100`
   - Check non-zero samples count in test output
   - Try different games known to have sound
   - Interact with the game to trigger sound effects

2. Sample rate issues:
   - The sample rate is fixed at 48000 Hz
   - Custom sample rates are not supported in the current version

3. Audio normalization:
   - Samples are normalized to 16-bit range (-32768 to 32767)
   - Check the waveform visualization for proper audio levels 