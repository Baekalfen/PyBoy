import pyboy
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import cython_compiled
from ctypes import c_uint, cast, c_void_p, POINTER, c_ubyte, c_int

logger = pyboy.logging.get_logger(__name__)


try:
    from openal import al, alc

    openal_enabled = True
except (ImportError, AttributeError):
    openal_enabled = False


MAX_SOUND_BUFFERS = 8


################################################
#
#  THIS IS NOT A WINDOW TYPE! THIS IS CODE FOR
#  SOUND USING OPENAL.
#
################################################
class WindowOpenAL(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        # Helps Cython access mb.sound
        self.init_audio(mb)

    def init_audio(self, mb):
        if mb.sound.emulate:
            try:
                self.sound_device = alc.alcOpenDevice(None)
                if not self.sound_device:
                    self.sound_support = False
                    logger.warning("Failed to open OpenAL device")
                    return

                self.sound_context = alc.alcCreateContext(self.sound_device, None)
                if not self.sound_context:
                    self.sound_support = False
                    logger.warning("Failed to create OpenAL context")
                    alc.alcCloseDevice(self.sound_device)
                    return

                alc.alcMakeContextCurrent(self.sound_context)

                self.source = c_uint()
                al.alGenSources(1, self.source)

                al.alSourcef(self.source, al.AL_GAIN, float(self.mb.sound.volume) / 100)

                self.buffers = (c_uint * MAX_SOUND_BUFFERS)()
                al.alGenBuffers(MAX_SOUND_BUFFERS, self.buffers)

                # buffer_size = c_int()
                # al.alGetBufferi(self.buffers[0], al.AL_SIZE, buffer_size)
                # logger.debug("Buffer size: %d", buffer_size.value)

                self.buffers_free = [self.buffers[x] for x in range(MAX_SOUND_BUFFERS)]

                if cython_compiled:
                    audiobuffer, _ = self.sound.audiobuffer.base.buffer_info()
                else:
                    audiobuffer, _ = self.sound.audiobuffer.buffer_info()
                self.audiobuffer_p = cast(c_void_p(audiobuffer), POINTER(c_ubyte))

                self.sound_support = True
                self.sound_paused = False
            except Exception as e:
                self.sound_support = False
                logger.warning("OpenAL initialization failed: %s", str(e))
        else:
            self.sound_support = False

    def _get_sound_frames_buffered(self):
        frames_buffered = c_int()
        al.alGetSourcei(self.source, al.AL_BUFFERS_QUEUED, frames_buffered)
        return frames_buffered.value

    def post_tick(self):
        if self.sound_support and not self.sound_paused:
            processed = c_int()
            al.alGetSourcei(self.source, al.AL_BUFFERS_PROCESSED, processed)
            logger.debug("Buffers processed: %s", processed.value)

            if processed:
                free_buffers = (c_uint * MAX_SOUND_BUFFERS)()
                al.alSourceUnqueueBuffers(self.source, processed, free_buffers)
                for i, f in enumerate(free_buffers):
                    if f == 0:
                        break  # FIXME: No buffers with id 0 right now
                    # if i == processed:
                    #     break
                    # logger.debug("Buffer unqueued: %s", f)
                    self.buffers_free.append(f)

            if self.buffers_free:
                length = min(self.sound.audiobuffer_head, self.sound.audiobuffer_length)
                logger.debug("Buffer length: %d", length)
                # al.alBufferData(self.buffer, al.AL_FORMAT_STEREO8, self.mixingbuffer_p,
                #                 len(self.mixingbuffer), self.sound.sample_rate)
                queue_buf = self.buffers_free.pop()
                al.alBufferData(queue_buf, al.AL_FORMAT_STEREO8, self.audiobuffer_p, length, self.sound.sample_rate)
                al.alSourceQueueBuffers(self.source, 1, c_uint(queue_buf))
                # logger.debug("Buffer enqueued: %s", queue_buf)

            queued = c_int()
            al.alGetSourcei(self.source, al.AL_BUFFERS_QUEUED, queued)
            logger.debug("Buffers queued: %s", queued.value)

            # Get current source state
            state = c_int()
            al.alGetSourcei(self.source, al.AL_SOURCE_STATE, state)
            logger.debug("source state %s", state.value)
            if (
                (state.value == al.AL_STOPPED) or (state.value == al.AL_INITIAL) or (state.value == al.AL_PAUSED)
            ):  # and queued.value > SOUND_PREBUFFER_THRESHOLD:
                logger.debug("Starting source")
                al.alSourcePlay(self.source)
                self.sound_paused = False

    def paused(self, pause):
        self.sound_paused = pause
        if self.sound_support:
            if self.sound_paused:
                al.alSourcePause(self.source)
            else:
                al.alSourcePlay(self.source)

    def stop(self):
        if self.sound_support:
            alc.alcCloseDevice(self.sound_device)
