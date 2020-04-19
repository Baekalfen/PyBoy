#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
# Based on specs from:
# http://gbdev.gg8.se/wiki/articles/Sound_Controller
# http://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware

from array import array
from ctypes import c_void_p

import sdl2


class Sound:
    def __init__(self):
        # Initialization is handled in the windows, otherwise we'd need this
        sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)

        # Open audio device
        # spec_want = sdl2.SDL_AudioSpec(32768, sdl2.AUDIO_S8, 2, 64, sdl2.SDL_AudioCallback(self.callback))
        spec_want = sdl2.SDL_AudioSpec(32768, sdl2.AUDIO_S8, 2, 64)
        spec_have = sdl2.SDL_AudioSpec(0, 0, 0, 0)
        self.device = sdl2.SDL_OpenAudioDevice(None, 0, spec_want, spec_have, 0)
        # ...sdl2.SDL_AUDIO_ALLOW_ANY_CHANGE)

        print(spec_have.format)
        print(spec_have.freq)
        print(spec_have.samples)

        self.sampleclocks = 0x404ac0 / spec_have.freq
        self.audiobuffer = array("b", [0] * 4096)  # Over 2 frames
        self.audiobuffer_p = c_void_p(self.audiobuffer.buffer_info()[0])

        self.clock = 0

        self.sweepchannel = SweepChannel()
        self.tonechannel = ToneChannel()
        self.wavechannel = WaveChannel()
        self.noisechannel = NoiseChannel()

        self.channels = (self.sweepchannel,
                         self.tonechannel,
                         self.wavechannel,
                         self.noisechannel)

        # Start playback (move out of __init__ if needed, maybe for headless)
        sdl2.SDL_PauseAudioDevice(self.device, 0)

    def get(self, offset):
        self.sync()
        if offset < 20:
            return self.channels[offset // 5].getreg(offset % 5)
        elif offset == 20: # Control register NR50
            return 0
        elif offset == 21: # Control register NR51
            return 0
        elif offset == 22: # Control register NR52
            return 0
        elif offset < 32: # Unused registers, read as 0xFF
            return 0xFF
        elif offset < 48: # Wave Table
            return self.wavechannel.getwavebyte(offset - 32)
        else:
            raise IndexError(f"Attempted to read register {offset} in sound memory")

    def set(self, offset, value):
        self.sync()
        if offset < 20:
            self.channels[offset // 5].setreg(offset % 5, value)
        elif offset == 20: # Control register NR50
            return
        elif offset == 21: # Control register NR51
            return
        elif offset == 22: # Control register NR52
            return
        elif offset < 32: # Unused registers, unwritable?
            return
        elif offset < 48: # Wave Table
            self.wavechannel.setwavebyte(offset - 32, value)
        else:
            raise IndexError(f"Attempted to write register {offset} in sound memory")

    def sync(self):
        """Run the audio for the number of clock cycles stored in self.clock"""
        nsamples = int(self.clock / self.sampleclocks)

        # print(self.clock, self.sampleclocks, nsamples)
        # print(sdl2.SDL_GetQueuedAudioSize(self.device))
        # if nsamples > 2048:
        #     self.clock = 0
        #     sdl2.SDL_ClearQueuedAudio(self.device)
        #     return
        for i in range(min(2048, nsamples)):
            self.sweepchannel.run(self.sampleclocks)
            self.tonechannel.run(self.sampleclocks)
            self.wavechannel.run(self.sampleclocks)
            sample = min(self.sweepchannel.sample() + self.tonechannel.sample() + self.wavechannel.sample(), 45)
            self.audiobuffer[2 * i] = sample
            self.audiobuffer[2*i + 1] = sample
            self.clock -= self.sampleclocks
        sdl2.SDL_QueueAudio(self.device, self.audiobuffer_p, 2 * nsamples)
        self.clock %= self.sampleclocks

    # Audio filling callback
    def callback(self, data, stream, length):
        for i in range(length // 2):
            self.sq1counter -= self.sampleclocks
            self.sq2counter -= self.sampleclocks
            if self.sq1counter < 0:
                self.sq1state ^= 1
                self.sq1counter = 16 * (2048 - (((0x7 & self.registers[4]) << 8) + self.registers[3]))
                # print(self.sq1counter)
            if self.sq2counter < 0:
                self.sq2state ^= 1
                self.sq2counter = 16 * (2048 - (((0x7 & self.registers[9]) << 8) + self.registers[8]))
            stream[2 * i] = 0x40 if self.sq1state else 0xB0
            stream[2 * i] += 0x3F if self.sq2state else -0x40
            stream[2*i + 1] = 0x00 if self.sq1state else 0xB0
            stream[2*i + 1] += 0x3F if self.sq2state else -0x40

    def stop(self):
        sdl2.SDL_CloseAudioDevice(self.device)

    def save_state(self, file):
        pass

    def load_state(self, file):
        pass


class ToneChannel:
    """Second sound channel--simple square wave, no sweep"""
    def __init__(self):
        # Shape of square waves at different duty cycles
        # These could ostensibly be replaced with other waves for fun experiments
        self.wavetables = [
            [0, 0, 0, 0, 0, 0, 0, 1], # 12.5% Duty cycle square
            [1, 0, 0, 0, 0, 0, 0, 1], # 25%
            [1, 0, 0, 0, 0, 1, 1, 1], # 50%
            [0, 1, 1, 1, 1, 1, 1, 0]
        ] # 75% (25% inverted)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the non-sweep tone channel
        self.wavsel = 0 # Register 1 bits 7-6: wave table selection (duty cycle)
        self.sndlen = 0 # Register 1 bits 5-0: time to play sound before stop (64-x)
        self.envini = 0 # Register 2 bits 7-4: volume envelope initial volume
        self.envdir = 0 # Register 2 bit 3: volume envelope change direction (0: decrease)
        self.envper = 0 # Register 2 bits 2-0: volume envelope period (0: disabled)
        self.sndper = 0 # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.uselen = 0 # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

        # Internal values
        self.enable = False # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 64 # Length timer, counts down to disable channel automatically
        self.periodtimer = 0 # Period timer, counts down to signal change in wave frame
        self.envelopetimer = 0 # Volume envelope timer, counts down to signal change in volume
        self.period = 4 # Calculated copy of period, 4 * (2048 - sndper)
        self.waveframe = 0 # Wave frame index into wave table entries
        self.frametimer = 0x2000 # Frame sequencer timer, underflows to signal change in frame sequences
        self.frame = 0 # Frame sequencer value, generates clocks for length/envelope/(sweep)
        self.volume = 0 # Current volume level, modulated by envelope

    def getreg(self, reg):
        if reg == 0:
            return 0
        elif reg == 1:
            return self.wavsel << 6 # Other bits are write-only
        elif reg == 2:
            return self.envini << 4 + self.envdir << 3 + self.envper
        elif reg == 3:
            return 0 # Write-only register?
        elif reg == 4:
            return self.uselen << 6 # Other bits are write-only
        else:
            raise IndexError("Attempt to read register {} in ToneChannel".format(reg))

    def setreg(self, reg, val):
        # print(reg, hex(val))
        if reg == 0:
            return
        elif reg == 1:
            self.wavsel = val >> 6 & 0x03
            self.sndlen = val & 0x1F
            self.lengthtimer = 64 - self.sndlen
        elif reg == 2:
            self.envini = val >> 4 & 0x0F
            self.envdir = val >> 3 & 0x01
            self.envper = val & 0x07
        elif reg == 3:
            self.sndper = (self.sndper & 0x700) + val # Is this ever written solo?
            self.period = 4 * (0x800 - self.sndper)
        elif reg == 4:
            self.uselen = val >> 6 & 0x01
            self.sndper = (val << 8 & 0x0700) + (self.sndper & 0xFF)
            self.period = 4 * (0x800 - self.sndper)
            if val & 0x80:
                self.trigger() # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            raise IndexError("Attempt to write register {} in ToneChannel".format(reg))

    def run(self, clocks):
        """Advances time to sync with system state.

        Doesn't generate samples, but we assume that it is called at
        the sample rate or faster, so this might not be not prepared
        to handle high values for 'clocks'.

        """
        self.periodtimer -= clocks
        while self.periodtimer <= 0:
            self.periodtimer += self.period
            self.waveframe = (self.waveframe + 1) % 8

        self.frametimer -= clocks
        while self.frametimer <= 0:
            self.frametimer += 0x2000
            self.tickframe()

    def tickframe(self):
        self.frame = (self.frame + 1) % 8
        # Clock length timer on 0, 2, 4, 6
        if self.uselen and self.frame & 1 == 0 and self.lengthtimer > 0:
            self.lengthtimer -= 1
            if self.lengthtimer == 0:
                self.enable = False
        # Clock envelope timer on 7
        if self.frame == 7 and self.envelopetimer != 0:
            self.envelopetimer -= 1
            if self.envelopetimer == 0:
                self.volume += self.envdir or -1
                self.envelopetimer = 0 if self.volume in (0, 15) else self.envper
                # Note that setting envelopetimer to 0 disables it

    def sample(self):
        return self.volume * self.wavetables[self.wavsel][self.waveframe] if self.enable else 0

    def trigger(self):
        self.enable = True
        self.lengthtimer = self.lengthtimer or 64
        self.periodtimer = self.period
        self.envelopetimer = self.envper
        self.volume = self.envini


class SweepChannel(ToneChannel):
    def __init__(self):
        ToneChannel.__init__(self)

        # Register Values
        self.swpper = 0 # Register 0 bits 6-4: Sweep period
        self.swpdir = 0 # Register 0 bit 3: Sweep direction (0: increase)
        self.swpmag = 0 # Register 0 bits 2-0: Sweep size as a bit shift

        # Internal Values
        self.sweeptimer = 0 # Sweep timer, counts down to shift pitch
        self.sweepenable = False # Internal sweep enable flag
        self.shadow = 0 # Shadow copy of period register for ignoring writes to sndper

    def getreg(self, reg):
        if reg == 0:
            return self.swpper << 4 + self.swpdir << 3 + self.swpmag
        else:
            return ToneChannel.getreg(self, reg)

    def setreg(self, reg, val):
        if reg == 0:
            self.swpper = val >> 4 & 0x07
            self.swpdir = val >> 3 & 0x01
            self.swpmag = val & 0x07
        else:
            ToneChannel.setreg(self, reg, val)

    # run() is the same as in ToneChannel, so we only override tickframe
    def tickframe(self):
        ToneChannel.tickframe(self)
        # Clock sweep timer on 2 and 6
        if self.sweepenable and self.swpper and self.frame & 3 == 2:
            self.sweeptimer -= 1
            if self.sweeptimer == 0:
                if self.sweep(True):
                    self.sweeptimer = self.swpper
                    self.sweep(False)

    def trigger(self):
        ToneChannel.trigger(self)
        self.shadow = self.sndper
        self.sweeptimer = self.swpper
        self.sweepenable = True if self.swpper or self.swpmag else False
        if self.swpmag:
            self.sweep(False)

    def sweep(self, save):
        if self.swpdir == 0:
            newper = self.shadow + (self.shadow >> self.swpmag)
        else:
            newper = self.shadow - (self.shadow >> self.swpmag)
        if newper >= 0x800:
            self.enable = False
            return False
        elif save and self.swpmag:
            self.sndper = self.shadow = newper
            self.period = 4 * (0x800 - self.sndper)
            return True


class WaveChannel:
    """Third sound channel--sample-based playback"""
    def __init__(self):
        # Memory for wave sample
        self.wavetable = array('B', [0xFF]*16)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the wave channel
        self.dacpow = 0 # Register 0 bit 7: DAC Power, enable playback
        self.sndlen = 0 # Register 1 bits 7-0: time to play sound before stop (256-x)
        self.volreg = 0 # Register 2 bits 6-5: volume code
        self.sndper = 0 # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.uselen = 0  # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

        # Internal values
        self.enable = False # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 256 # Length timer, counts down to disable channel automatically
        self.periodtimer = 0 # Period timer, counts down to signal change in wave frame
        self.period = 4 # Calculated copy of period, 4 * (2048 - sndper)
        self.waveframe = 0 # Wave frame index into wave table entries
        self.frametimer = 0x2000 # Frame sequencer timer, underflows to signal change in frame sequences
        self.frame = 0 # Frame sequencer value, generates clocks for length/envelope/(sweep)
        self.volumeshift = 0 # Bitshift for volume, set by volreg

    def getreg(self, reg):
        # https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware#Register_Reading
        if reg == 0:
            return self.dacpow << 7 | 0x7F
        elif reg == 1:
            return 0xFF
        elif reg == 2:
            return self.volreg << 5 | 0x9F
        elif reg == 3:
            return 0xFF
        elif reg == 4:
            return self.uselen << 6 | 0xBF
        else:
            raise IndexError("Attempt to read register {} in ToneChannel".format(reg))

    def setreg(self, reg, val):
        if reg == 0:
            self.dacpow = val >> 7 & 0x01
        elif reg == 1:
            self.sndlen = val
            self.lengthtimer = 256 - self.sndlen
        elif reg == 2:
            self.volreg = val >> 5 & 0x03
            self.volumeshift = self.volreg - 1 if self.volreg > 0 else 4
        elif reg == 3:
            self.sndper = (self.sndper & 0x700) + val # Is this ever written solo?
            self.period = 2 * (0x800 - self.sndper)
        elif reg == 4:
            self.uselen = val >> 6 & 0x01
            self.sndper = (val << 8 & 0x0700) + (self.sndper & 0xFF)
            self.period = 2 * (0x800 - self.sndper)
            if val & 0x80:
                self.trigger() # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            raise IndexError("Attempt to write register {} in WaveChannel".format(reg))

    def getwavebyte(self, offset):
        if self.dacpow:
            return self.wavetable[self.waveframe]
        else:
            return self.wavetable[offset]

    def setwavebyte(self, offset, value):
        # In GBA, a write is ignored while the channel is running.
        # Otherwise, it usually goes at the current frame byte.
        if self.dacpow:
            self.wavetable[self.waveframe] = value
        else:
            self.wavetable[offset] = value

    def run(self, clocks):
        """Advances time to sync with system state."""
        self.periodtimer -= clocks
        while self.periodtimer <= 0:
            self.periodtimer += self.period
            self.waveframe += 1
            self.waveframe %= 32

        self.frametimer -= clocks
        while self.frametimer <= 0:
            self.frametimer += 0x2000
            self.tickframe()

    def tickframe(self):
        self.frame = (self.frame + 1) % 8
        # Clock length timer on 0, 2, 4, 6
        if self.uselen and self.frame & 1 == 0 and self.lengthtimer > 0:
            self.lengthtimer -= 1
            if self.lengthtimer == 0:
                self.enable = False

    def sample(self):
        if self.enable and self.dacpow:
            sample = self.wavetable[self.waveframe // 2] >> (0 if self.waveframe % 2 else 4) & 0x0F
            return sample >> self.volumeshift
        else:
            return 0

    def trigger(self):
        self.enable = True
        self.lengthtimer = self.lengthtimer or 256
        self.periodtimer = self.period


class NoiseChannel:
    def __init__(self):
        pass

    def getreg(self, offset):
        pass

    def setreg(self, offset, value):
        pass
