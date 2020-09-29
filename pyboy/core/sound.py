#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
# Based on specs from:
# http://gbdev.gg8.se/wiki/articles/Sound_Controller
# http://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware
# http://www.devrs.com/gb/files/hosted/GBSOUND.txt

from array import array
from ctypes import c_void_p

import sdl2

SOUND_DESYNC_THRESHOLD = 5
CPU_FREQ = 4213440 # hz


class Sound:
    def __init__(self):
        # Initialization is handled in the windows, otherwise we'd need this
        sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)

        # Open audio device
        spec_want = sdl2.SDL_AudioSpec(32768, sdl2.AUDIO_S8, 2, 64)
        spec_have = sdl2.SDL_AudioSpec(0, 0, 0, 0)
        self.device = sdl2.SDL_OpenAudioDevice(None, 0, spec_want, spec_have, 0)

        self.sample_rate = spec_have.freq
        self.sampleclocks = CPU_FREQ / self.sample_rate
        self.audiobuffer = array("b", [0] * 4096) # Over 2 frames
        self.audiobuffer_p = c_void_p(self.audiobuffer.buffer_info()[0])

        self.clock = 0

        self.poweron = True

        self.sweepchannel = SweepChannel()
        self.tonechannel = ToneChannel()
        self.wavechannel = WaveChannel()
        self.noisechannel = NoiseChannel()

        self.leftnoise = False
        self.leftwave = False
        self.lefttone = False
        self.leftsweep = False
        self.rightnoise = False
        self.rightwave = False
        self.righttone = False
        self.rightsweep = False

        # Start playback (move out of __init__ if needed, maybe for headless)
        sdl2.SDL_PauseAudioDevice(self.device, 0)

    def get(self, offset):
        self.sync()
        if offset < 20:
            i = offset // 5
            if i == 0:
                return self.sweepchannel.getreg(offset % 5)
            elif i == 1:
                return self.tonechannel.getreg(offset % 5)
            elif i == 2:
                return self.wavechannel.getreg(offset % 5)
            elif i == 3:
                return self.noisechannel.getreg(offset % 5)
        elif offset == 20: # Control register NR50: Vin enable and volume -- not implemented
            return 0
        elif offset == 21: # Control register NR51: Channel stereo enable/panning
            return ((0x80 if self.leftnoise else 0) | (0x40 if self.leftwave else 0) | (0x20 if self.lefttone else 0) |
                    (0x10 if self.leftsweep else 0) | (0x08 if self.rightnoise else 0) |
                    (0x04 if self.rightwave else 0) | (0x02 if self.righttone else 0) |
                    (0x01 if self.rightsweep else 0))
        elif offset == 22: # Control register NR52: Sound/channel enable
            return 0x70 | ((0x80 if self.poweron else 0) | (0x08 if self.noisechannel.enable else 0) |
                           (0x04 if self.wavechannel.enable else 0) | (0x02 if self.tonechannel.enable else 0) |
                           (0x01 if self.sweepchannel.enable else 0))
        elif offset < 32: # Unused registers, read as 0xFF
            return 0xFF
        elif offset < 48: # Wave Table
            return self.wavechannel.getwavebyte(offset - 32)
        else:
            raise IndexError(f"Attempted to read register {offset} in sound memory")

    def set(self, offset, value):
        self.sync()
        if offset < 20 and self.poweron:
            i = offset // 5
            if i == 0:
                self.sweepchannel.setreg(offset % 5, value)
            elif i == 1:
                self.tonechannel.setreg(offset % 5, value)
            elif i == 2:
                self.wavechannel.setreg(offset % 5, value)
            elif i == 3:
                self.noisechannel.setreg(offset % 5, value)
        elif offset == 20 and self.poweron: # Control register NR50: Vin enable and volume -- not implemented
            return
        elif offset == 21 and self.poweron: # Control register NR51: Channel stereo enable/panning
            self.leftnoise = bool(value & 0x80)
            self.leftwave = bool(value & 0x40)
            self.lefttone = bool(value & 0x20)
            self.leftsweep = bool(value & 0x10)
            self.rightnoise = bool(value & 0x08)
            self.rightwave = bool(value & 0x04)
            self.righttone = bool(value & 0x02)
            self.rightsweep = bool(value & 0x01)
            return
        elif offset == 22: # Control register NR52: Sound on/off
            if value & 0x80 == 0: # Sound power off
                for n in range(22):
                    self.set(n, 0)
                self.poweron = False
            else:
                self.poweron = True
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

        for i in range(min(2048, nsamples)):
            if self.poweron:
                self.sweepchannel.run(self.sampleclocks)
                self.tonechannel.run(self.sampleclocks)
                self.wavechannel.run(self.sampleclocks)
                self.noisechannel.run(self.sampleclocks)
                # print(self.leftsweep, self.lefttone, self.leftwave, self.leftnoise)
                # print(self.rightsweep, self.righttone, self.rightwave, self.rightnoise)
                sample = ((self.sweepchannel.sample() if self.leftsweep else 0) +
                          (self.tonechannel.sample() if self.lefttone else 0) +
                          (self.wavechannel.sample() if self.leftwave else 0) +
                          (self.noisechannel.sample() if self.leftnoise else 0))
                self.audiobuffer[2 * i] = min(max(sample, 0), 127)
                sample = ((self.sweepchannel.sample() if self.rightsweep else 0) +
                          (self.tonechannel.sample() if self.righttone else 0) +
                          (self.wavechannel.sample() if self.rightwave else 0) +
                          (self.noisechannel.sample() if self.rightnoise else 0))
                self.audiobuffer[2*i + 1] = min(max(sample, 0), 127)
                self.clock -= self.sampleclocks
            else:
                self.audiobuffer[2 * i] = 0
                self.audiobuffer[2*i + 1] = 0
        # Clear queue, if we are behind
        queued_time = sdl2.SDL_GetQueuedAudioSize(self.device)
        samples_per_frame = (self.sample_rate / 60) * 2 # Data of 1 frame's worth (60) in stereo (2)
        if queued_time > samples_per_frame * SOUND_DESYNC_THRESHOLD:
            sdl2.SDL_ClearQueuedAudio(self.device)

        sdl2.SDL_QueueAudio(self.device, self.audiobuffer_p, 2 * nsamples)
        self.clock %= self.sampleclocks

    def stop(self):
        sdl2.SDL_CloseAudioDevice(self.device)

    def save_state(self, file):
        pass

    def load_state(self, file, state_version):
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
            return self.envini << 4 | self.envdir << 3 | self.envper
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
                newvolume = self.volume + (self.envdir or -1)
                if newvolume < 0 or newvolume > 15:
                    self.envelopetimer = 0
                else:
                    self.envelopetimer = self.envper
                    self.volume = newvolume
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
            return self.swpper << 4 | self.swpdir << 3 | self.swpmag
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
        self.sweepenable = True if (self.swpper or self.swpmag) else False
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
        self.wavetable = array("B", [0xFF] * 16)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the wave channel
        self.dacpow = 0 # Register 0 bit 7: DAC Power, enable playback
        self.sndlen = 0 # Register 1 bits 7-0: time to play sound before stop (256-x)
        self.volreg = 0 # Register 2 bits 6-5: volume code
        self.sndper = 0 # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.uselen = 0 # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

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
    """Fourth sound channel--white noise generator"""
    def __init__(self):
        self.DIVTABLE = (8, 16, 32, 48, 64, 80, 96, 112)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the noise channel
        self.sndlen = 0 # Register 1 bits 5-0: time to play sound before stop (64-x)
        self.envini = 0 # Register 2 bits 7-4: volume envelope initial volume
        self.envdir = 0 # Register 2 bit 3: volume envelope change direction (0: decrease)
        self.envper = 0 # Register 2 bits 2-0: volume envelope period (0: disabled)
        self.clkpow = 0 # Register 3 bits 7-4: lfsr clock shift
        self.regwid = 0 # Register 3 bit 3: lfsr bit width (0: 15, 1: 7)
        self.clkdiv = 0 # Register 3 bits 2-0: base divider for lfsr clock
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.uselen = 0 # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

        # Internal values
        self.enable = False # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 64 # Length timer, counts down to disable channel automatically
        self.periodtimer = 0 # Period timer, counts down to signal change in wave frame
        self.envelopetimer = 0 # Volume envelope timer, counts down to signal change in volume
        self.period = 8 # Calculated copy of period, 8 << 0
        self.shiftregister = 1 # Internal shift register value
        self.lfsrfeed = 0x4000 # Bit mask for inserting feedback in shift register
        self.frametimer = 0x2000 # Frame sequencer timer, underflows to signal change in frame sequences
        self.frame = 0 # Frame sequencer value, generates clocks for length/envelope/(sweep)
        self.volume = 0 # Current volume level, modulated by envelope

    def getreg(self, reg):
        if reg == 0:
            return 0xFF
        elif reg == 1:
            return 0xFF
        elif reg == 2:
            return self.envini << 4 | self.envdir << 3 | self.envper
        elif reg == 3:
            return self.clkpow << 4 | self.regwid << 3 | self.clkdiv
        elif reg == 4:
            return self.uselen << 6 | 0xBF
        else:
            raise IndexError("Attempt to read register {} in NoiseChannel".format(reg))

    def setreg(self, reg, val):
        if reg == 0:
            return
        elif reg == 1:
            self.sndlen = val & 0x1F
            self.lengthtimer = 64 - self.sndlen
        elif reg == 2:
            self.envini = val >> 4 & 0x0F
            self.envdir = val >> 3 & 0x01
            self.envper = val & 0x07
        elif reg == 3:
            self.clkpow = val >> 4 & 0x0F
            self.regwid = val >> 3 & 0x01
            self.clkdiv = val & 0x07
            self.period = self.DIVTABLE[self.clkdiv] << self.clkpow
            self.lfsrfeed = 0x4040 if self.regwid else 0x4000
        elif reg == 4:
            self.uselen = val >> 6 & 0x01
            if val & 0x80:
                self.trigger() # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            raise IndexError("Attempt to write register {} in ToneChannel".format(reg))

    def run(self, clocks):
        """Advances time to sync with system state."""
        self.periodtimer -= clocks
        while self.periodtimer <= 0:
            self.periodtimer += self.period
            # Advance shift register
            # This is good C, but terrible Python
            tap = self.shiftregister
            self.shiftregister >>= 1
            tap ^= self.shiftregister
            if tap & 0x01:
                self.shiftregister |= self.lfsrfeed
            else:
                self.shiftregister &= ~self.lfsrfeed

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
                newvolume = self.volume + (self.envdir or -1)
                if newvolume < 0 or newvolume > 15:
                    self.envelopetimer = 0
                else:
                    self.envelopetimer = self.envper
                    self.volume = newvolume
                # Note that setting envelopetimer to 0 disables it

    def sample(self):
        if self.enable:
            return self.volume if self.shiftregister & 0x01 == 0 else 0
        else:
            return 0

    def trigger(self):
        self.enable = True
        self.lengthtimer = self.lengthtimer or 64
        self.periodtimer = self.period
        self.envelopetimer = self.envper
        self.volume = self.envini
        self.shiftregister = 0x7FFF
