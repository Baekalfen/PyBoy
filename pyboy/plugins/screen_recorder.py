#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import shutil
import subprocess
import tempfile
import time

import pyboy
from pyboy.api.constants import ROWS, COLS
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None

FPS = 60


class ScreenRecorder(PyBoyPlugin):
    def __init__(self, *args):
        super().__init__(*args)

        self.recording_gif = False
        self.recording_mp4 = False
        self.ffmpeg_bin = shutil.which("ffmpeg")
        self._session = None

    def handle_events(self, events):
        for event in events:
            if event == WindowEvent.SCREEN_RECORDING_TOGGLE:
                if self.recording_gif:
                    self._stop_recording()
                else:
                    self._start_recording("gif")
                break
            if event == WindowEvent.SCREEN_RECORDING_TOGGLE_MP4:
                if self.recording_mp4:
                    self._stop_recording()
                else:
                    self._start_recording("mp4")
                break
        return events

    def post_tick(self):
        # Plugin: Screen Recorder
        session = self._session
        if session is None:
            return
        if session["mode"] == "gif":
            self._capture_gif_frame()
        else:
            self._write_frame()
            self._write_audio()

    def stop(self):
        if self.recording_gif or self.recording_mp4:
            self._stop_recording()

    def _start_recording(self, mode):
        if self.recording_gif or self.recording_mp4:
            logger.warning("ScreenRecorder already active")
            return

        if mode == "gif" and Image is None:
            logger.error('ScreenRecorder gif requires dependency "Pillow"')
            return

        if mode == "mp4" and not self.mb.sound.emulate:
            logger.error("ScreenRecorder mp4 requires sound emulation enabled")
            return

        if mode == "mp4" and self.ffmpeg_bin is None:
            logger.error('ScreenRecorder mp4 requires dependency "ffmpeg"')
            return

        directory = os.path.join(os.path.curdir, "recordings")
        os.makedirs(directory, mode=0o755, exist_ok=True)
        stamp = time.strftime(f"{self.pyboy.cartridge_title}-%Y.%m.%d-%H.%M.%S")
        tmpdir = tempfile.mkdtemp(prefix="screenrec-", dir=directory)
        video_raw = os.path.join(tmpdir, "video.rgba")
        audio_raw = os.path.join(tmpdir, "audio.s8")
        output_path = os.path.join(directory, f"{stamp}.{mode}")

        self._session = {
            "mode": mode,
            "tmpdir": tmpdir,
            "video_raw": video_raw if mode == "mp4" else None,
            "audio_raw": audio_raw if mode == "mp4" else None,
            "output_path": output_path,
            "frames": 0,
            "audio_bytes": 0,
            "gif_frames": [] if mode == "gif" else None,
            "video_fh": open(video_raw, "wb") if mode == "mp4" else None,
            "audio_fh": open(audio_raw, "wb") if mode == "mp4" else None,
        }

        self.recording_gif = mode == "gif"
        self.recording_mp4 = mode == "mp4"
        logger.info("ScreenRecorder started: %s", mode.upper())

    def _stop_recording(self):
        session = self._session
        if session is None:
            return

        logger.info("ScreenRecorder saving...")
        if session["video_fh"] is not None:
            session["video_fh"].close()
        if session["audio_fh"] is not None:
            session["audio_fh"].close()

        success = False
        if session["frames"] > 0:
            if session["mode"] == "gif":
                success = self._encode_gif(session)
            else:
                success = self._encode_mp4(session)
        else:
            logger.error("Screen recording failed: no frames")

        if success:
            logger.info("Screen recording saved in %s", session["output_path"])
        self._cleanup_session(session)
        self._session = None
        self.recording_gif = False
        self.recording_mp4 = False

    def _write_frame(self):
        frame = self.pyboy.screen.ndarray
        self._session["video_fh"].write(frame.tobytes(order="C"))
        self._session["frames"] += 1

    def _capture_gif_frame(self):
        # Keep RGB data for Pillow to avoid palette artifacts.
        self._session["gif_frames"].append(self.pyboy.screen.image.copy())
        self._session["frames"] += 1

    def _write_audio(self):
        audio = self.pyboy.sound.ndarray
        data = audio.tobytes(order="C")
        self._session["audio_fh"].write(data)
        self._session["audio_bytes"] += len(data)

    def _encode_gif(self, session):
        frames = session["gif_frames"]
        if not frames:
            logger.error("Screen recording failed: no frames")
            return False
        try:
            frames[0].save(
                session["output_path"],
                save_all=True,
                interlace=False,
                loop=0,
                optimize=True,
                append_images=frames[1:],
                duration=int(round(1000 / FPS, -1)),
            )
            return True
        except Exception:
            logger.exception("ScreenRecorder failed to encode GIF")
            return False

    def _encode_mp4(self, session):
        if session["audio_bytes"] == 0:
            logger.error("Screen recording failed: no audio samples were captured")
            return False
        return self._run_ffmpeg(
            [
                self.ffmpeg_bin,
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgba",
                "-s:v",
                f"{COLS}x{ROWS}",
                "-r",
                str(FPS),
                "-i",
                session["video_raw"],
                "-f",
                "s8",
                "-ar",
                str(self.pyboy.sound.sample_rate),
                "-ac",
                "2",
                "-i",
                session["audio_raw"],
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-shortest",
                session["output_path"],
            ]
        )

    # Execution of ffmpeg commands :)
    def _run_ffmpeg(self, cmd):
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            logger.error("ffmpeg failed with code %d", proc.returncode)
            if proc.stderr:
                logger.error(proc.stderr.decode(errors="replace"))
            return False
        return True

    def _cleanup_session(self, session):
        if session.get("gif_frames") is not None:
            session["gif_frames"] = []
        if os.path.exists(session["tmpdir"]):
            shutil.rmtree(session["tmpdir"], ignore_errors=True)

    def enabled(self):
        if Image is None and self.ffmpeg_bin is None:
            logger.warning('%s: Missing dependencies "Pillow" and "ffmpeg". Recording disabled', __name__)
            return False
        return True
