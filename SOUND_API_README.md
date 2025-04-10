# Sound Extraction API and Screen Recorder with Sound

This document describes the implementation of two related features:
1. Sound Extraction API (Issue #217)
2. Screen Recorder with Sound Support (Issue #368)

## Quick Start

To run everything in sequence:

1. First, build the project:
```bash
python3 setup.py build
```

2. Then install in development mode:
```bash
python3 setup.py develop
```

3. Run the game launcher:
```bash
python3 game_launcher.py
```

4. Run test 217:
```bash
python3 test_217_sound_extraction_api.py
```

5. Finally, run test 368:
```bash
python3 test_368_screen_recorder_with_sound.py
```

**Important Note**: Before running the tests, make sure to update the ROM path in both test files (`test_217_sound_extraction_api.py` and `test_368_screen_recorder_with_sound.py`) to point to your Game Boy ROM file. Look for the comment `#UPDATE HARDCODED ROM PATH BELOW` in each file.

## Sound Extraction API

The Sound Extraction API provides access to the emulator's audio output in real-time. The audio data is available through the `sound.ndarray` property, which returns a numpy array containing the current frame's audio samples.

### API Properties

```python
@property
def ndarray(self):
    """
    Returns the audio samples for the current frame as a numpy array.
    
    Returns
    -------
    numpy.ndarray:
        A 2D array of shape (samples, 2) containing stereo audio samples.
        The first column is the left channel, the second is the right channel.
    """
```

### Usage Example

```python
import pyboy

# Initialize PyBoy with sound enabled
pyboy_instance = pyboy.PyBoy("roms/tetris.gb", sound_emulated=True)

# Run the emulator for a few frames
for _ in range(10):
    pyboy_instance.tick()
    
    # Get the audio samples for this frame
    audio_samples = pyboy_instance.sound.ndarray
    left_channel = audio_samples[:, 0]
    right_channel = audio_samples[:, 1]
    
    # Process the audio samples as needed
    print(f"Left channel: {len(left_channel)} samples")
    print(f"Right channel: {len(right_channel)} samples")

# Clean up
pyboy_instance.stop()
```

## Screen Recorder with Sound

The screen recorder with sound support provides a complete solution for recording gameplay with synchronized audio. It captures both video frames and audio samples in real-time and combines them into a single MP4 file.

### Features

- Real-time capture of both video frames and audio samples
- Proper audio scaling from 8-bit to 16-bit
- Synchronized audio and video
- Automatic cleanup of temporary files
- Single output file in MP4 format

### Example Implementation

See `test_368_screen_recorder_with_sound.py` for a complete implementation. Here's a simplified version:

```python
import pyboy
import numpy as np
import wave
import cv2
import os

# Initialize PyBoy with sound
pyboy_instance = pyboy.PyBoy("roms/tetris.gb", sound_emulated=True)

# Initialize arrays for frames and audio
frames = []
all_left_samples = []
all_right_samples = []

# Record frames and audio
for _ in range(300):  # 5 seconds at 60fps
    pyboy_instance.tick()
    
    # Capture screen
    screen = pyboy_instance.screen.ndarray
    rgb_frame = cv2.cvtColor(screen, cv2.COLOR_RGBA2RGB)
    frames.append(rgb_frame)
    
    # Capture audio
    audio_samples = pyboy_instance.sound.ndarray
    all_left_samples.extend(audio_samples[:, 0])
    all_right_samples.extend(audio_samples[:, 1])

# Save video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('temp_video.mp4', fourcc, 60.0, (160, 144))
for frame in frames:
    out.write(frame)
out.release()

# Save audio
scale = 32768 // 128  # Scale 8-bit to 16-bit
left_samples = np.array(all_left_samples, dtype=np.int16) * scale
right_samples = np.array(all_right_samples, dtype=np.int16) * scale

stereo_samples = np.empty(len(left_samples) + len(right_samples), dtype=np.int16)
stereo_samples[0::2] = left_samples
stereo_samples[1::2] = right_samples

with wave.open('temp_audio.wav', 'wb') as wav_file:
    wav_file.setnchannels(2)
    wav_file.setsampwidth(2)
    wav_file.setframerate(pyboy_instance.sound.sample_rate)
    wav_file.writeframes(stereo_samples.tobytes())

# Combine video and audio using FFmpeg
os.system('ffmpeg -y -i temp_video.mp4 -i temp_audio.wav -c:v copy -c:a aac output.mp4')

# Cleanup
os.remove('temp_video.mp4')
os.remove('temp_audio.wav')
pyboy_instance.stop()
```

## Requirements

- Python 3.6+
- PyBoy
- NumPy
- OpenCV (opencv-python)
- Pillow
- FFmpeg (system installation)

## Troubleshooting

1. **No video output**: Make sure OpenCV is installed correctly with `pip install opencv-python`
2. **No audio**: Verify that PyBoy was initialized with `sound_emulated=True`
3. **FFmpeg errors**: Ensure FFmpeg is installed on your system and accessible from the command line
4. **Import errors**: Make sure all required packages are installed in your virtual environment

## Testing

Two test files are provided:
1. `test_217_sound_extraction_api.py`: Tests the sound extraction API
2. `test_368_screen_recorder_with_sound.py`: Tests the screen recorder with sound support

To run the tests:
```bash
# Activate virtual environment first
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Run the tests
python test_368_screen_recorder_with_sound.py
``` 