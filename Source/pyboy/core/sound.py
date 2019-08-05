#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array
from ctypes import c_void_p

import sdl2


class Sound:

    def __init__(self):
        self.registers = array.array('B', [0] * 0x30)

        # Initialization is handled in the windows, otherwise we'd need this
        # sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO)

        # Open audio device
        self.spec_want = sdl2.SDL_AudioSpec(32768, sdl2.AUDIO_S8, 2, 64)
        self.spec_have = sdl2.SDL_AudioSpec(0,0,0,0)
        self.device = sdl2.SDL_OpenAudioDevice(None, 0, self.spec_want, self.spec_have, 0)
        # ...sdl2.SDL_AUDIO_ALLOW_ANY_CHANGE)

        # print(self.spec_have.format)
        # print(self.spec_have.freq)
        # print(self.spec_have.samples)
        self.sampleclocks = 0x400000 // self.spec_have.freq  # Clocks per sample (TODO: what if it's not an integer?)
        self.audiobuffer = array.array('b', [0] * 4096)  # Over 2 frames of sample space--should probably calculate
        self.audiobuffer_p = c_void_p(self.audiobuffer.buffer_info()[0])

        self.clock = 0

        self.tonechannel = ToneChannel()

        # Start playback (move out of __init__ if needed, maybe for headless)
        sdl2.SDL_PauseAudioDevice(self.device, 0)

    def get(self, offset):
        self.sync()
        if 5 <= offset < 10:
            return self.tonechannel.getreg(offset - 5)
        else:
            return self.registers[offset]

    def set(self, offset, value):
        self.sync()
        if 5 <= offset < 10:
            self.tonechannel.setreg(offset - 5, value)
        else:
            self.registers[offset] = value

    def sync(self):
        """Run the audio for the number of clock cycles stored in self.clock"""
        nsamples = self.clock // self.sampleclocks
        # print(self.clock, self.sampleclocks, nsamples)
        if nsamples > 2048:
            self.clock = 0
            sdl2.SDL_ClearQueuedAudio(self.device)
            return
        for i in range(nsamples):
            self.tonechannel.run(self.sampleclocks)
            self.audiobuffer[2*i]   = 8 * self.tonechannel.sample()
            self.audiobuffer[2*i+1] = 8 * self.tonechannel.sample()
        sdl2.SDL_QueueAudio(self.device, self.audiobuffer_p, 2*nsamples)
        self.clock %= self.sampleclocks

    def stop(self):
        sdl2.SDL_CloseAudioDevice(self.device)

    def save_state(self, file):
        pass

    def load_state(self, file):
        pass


class ToneChannel:

    def __init__(self):
        # Shape of square waves at different duty cycles
        # These could ostensibly be replaced with other waves for fun experiments
        self.wavetables = [[0, 0, 0, 0, 0, 0, 0, 1],  # 12.5% Duty cycle square
                           [1, 0, 0, 0, 0, 0, 0, 1],  # 25%
                           [1, 0, 0, 0, 0, 1, 1, 1],  # 50%
                           [0, 1, 1, 1, 1, 1, 1, 0]]  # 75% (25% inverted)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the non-sweep tone channel
        self.wavsel = 0  # Register 1 bits 7-6: wave table selection (duty cycle)
        self.sndlen = 0  # Register 1 bits 5-0: time to play sound before stop
        self.envini = 0  # Register 2 bits 7-4: volume envelope initial volume
        self.envdir = 0  # Register 2 bit 3: volume envelope change direction (0: decrease)
        self.envper = 0  # Register 2 bits 2-0: volume envelope period (0: disabled)
        self.period = 0  # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.uselen = 0  # Register 4 bit 6: enable/disable sound length counter in reg 1 (0: continuous)

        # Internal values
        self.enabled = False        # Enable flag, turned on by trigger bit and off by length counter
        self.lengthcounter = 0      # Length counter, underflows to disable channel automatically
        self.periodcounter = 0      # Period counter, underflows to signal change in wave frame
        self.envelopecounter = 0    # Volume envelope counter, underflows to signal change in volume
        self.waveframe = 0          # Wave frame index into wave table entries
        self.framecounter = 0x2000  # Frame sequencer counter, underflows to signal change in frame sequences
        self.frame = 0              # Frame sequencer value, generates clocks for length/envelope/(sweep)
        self.volume = 0             # Current volume level, modulated by envelope

    def getreg(self, reg):
        if reg == 0:
            return 0
        elif reg == 1:
            return self.wavsel << 6  # Other bits are write-only
        elif reg == 2:
            return self.envini << 4 + self.envdir << 3 + self.envper
        elif reg == 3:
            # return self.period & 0xFF
            return 0  # Write-only register?
        elif reg == 4:
            return self.uselen << 6  # Other bits are write-only
        else:
            raise IndexError("Attempt to read register {} in ToneChannel".format(reg))

    def setreg(self, reg, val):
        print(reg, hex(val))
        if reg == 0:
            return
        elif reg == 1:
            self.wavsel = val >> 6 & 0x03
            self.sndlen = val & 0x1F
        elif reg == 2:
            self.envini = val >> 4 & 0x0F
            self.envdir = val >> 3 & 0x01
            self.envper = val & 0x07
        elif reg == 3:
            self.period = (self.period & 0x700) + val  # Is this ever written solo?
        elif reg == 4:
            if val >> 7 & 0x01:
                self.trigger()  # Sync is called first in Sound.set so it's okay to trigger immediately
            self.uselen = val >> 6 & 0x01
            self.period = (val << 8 & 0x0700) + (self.period & 0xFF)
        else:
            raise IndexError("Attempt to write register {} in ToneChannel".format(reg))

    def run(self, clocks):
        """Advances time to sync with system state.

        Doesn't generate samples, but we assume that it is called at
        the sample rate or faster, so this might not be not prepared
        to handle high values for 'clocks'.

        """
        self.periodcounter -= clocks
        while self.periodcounter <= 0:
            self.periodcounter += 4*(0x800 - self.period)
            self.waveframe = (self.waveframe + 1) % 8

        self.framecounter -= clocks
        while self.framecounter <= 0:
            self.framecounter += 0x2000
            self.frame = (self.frame + 1) % 8
            # Clock length counter on 0, 2, 4, 6
            if self.frame & 1 == 0:
                self.lengthcounter -= 1
                if self.lengthcounter == 0:
                    self.enabled = False
            # Clock envelope counter on 7
            if self.frame == 7 and self.envelopecounter != 0:
                self.envelopecounter -= 1
                if self.envelopecounter == 0:
                    self.volume += self.envdir or -1
                    self.envelopecounter = 0 if self.volume in (0, 15) else self.envper
                    # Note that setting envelopecounter to 0 disables it

    def sample(self):
        # TOOD: Is -1 wrong? (Temp lazy hack, but might mess up scaling)
        return self.volume * self.wavetables[self.wavsel][self.waveframe] if self.enabled else -1

    def trigger(self):
        self.enabled = True
        self.lengthcounter = self.lengthcounter or 64
        self.periodcounter = 4*(0x800 - self.period)
        self.envelopecounter = self.envper
        self.volume = self.envini
