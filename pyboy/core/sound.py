#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
# Based on specs from:
# http://gbdev.gg8.se/wiki/articles/Sound_Controller
# http://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware
# http://www.devrs.com/gb/files/hosted/GBSOUND.txt

import struct
from array import array

import pyboy
from pyboy.utils import PyBoyAssertException, cython_compiled
from pyboy.utils import FRAME_CYCLES, MAX_CYCLES

if not cython_compiled:
    # Hide it from Cython in 'exec' statement
    exec("from pyboy.utils import double_to_uint64_ceil")

logger = pyboy.logging.get_logger(__name__)

CYCLES_512HZ = 8192


class Sound:
    def __init__(self, volume, emulate, sample_rate, cgb):
        self.volume = volume
        self.disable_sampling = False
        self.emulate = emulate  # Just emulate registers etc.
        logger.debug(
            "Sound emulated: %d, sound volume: %d, sound disable sampling: %d",
            self.emulate,
            self.volume,
            self.disable_sampling,
        )
        self.cgb = cgb

        if sample_rate is None:
            # self.sample_rate = 44100 # Hz
            self.sample_rate = 48000  # Hz
            # self.sample_rate = 24000  # Hz
        else:
            self.sample_rate = sample_rate
        assert self.sample_rate % 60 == 0, "We do not want a sample rate that doesn't divide the frame rate"
        self.audiobuffer_head = 0
        self.samples_per_frame = self.sample_rate // 60
        self.cycles_per_sample = float(FRAME_CYCLES) / self.samples_per_frame  # Notice use of float
        self.buffer_format = "b"
        # Buffer for 1 frame of stereo 8-bit sound. +1 for rounding error
        self.audiobuffer_length = (self.samples_per_frame + 1) * 2
        self.audiobuffer = array(self.buffer_format, [0] * self.audiobuffer_length)

        self.speed_shift = 0
        if not self.emulate:
            # No need to sample, when not enabled
            self.cycles_target = MAX_CYCLES
            self.cycles_target_512Hz = MAX_CYCLES
            self._cycles_to_interrupt = MAX_CYCLES
        else:
            if self.disable_sampling:
                self.cycles_target = MAX_CYCLES
            else:
                self.cycles_target = self.cycles_per_sample
            self.cycles_target_512Hz = CYCLES_512HZ
            # We have to use ceil on the double to round any decimals up to the next cycle. We have to pass the target
            # entirely, and as the cycles are integer, we cannot just round down, as that would be 1 cycle too early.
            # NOTE: speed_shift because they are using in externally in mb
            self._cycles_to_interrupt = (
                double_to_uint64_ceil(min(self.cycles_target, self.cycles_target_512Hz)) << self.speed_shift
            )

        self.cycles = 0
        self.last_cycles = 0

        self.div_apu_counter = 0
        self.div_apu = 0
        self.poweron = 0

        self.sweepchannel = SweepChannel()
        self.tonechannel = ToneChannel()
        self.wavechannel = WaveChannel(self.cgb)
        self.noisechannel = NoiseChannel()

        self.noise_left = 0
        self.wave_left = 0
        self.tone_left = 0
        self.sweep_left = 0
        self.noise_right = 0
        self.wave_right = 0
        self.tone_right = 0
        self.sweep_right = 0

    def reset_apu_div(self):
        # self.div_apu_counter = 0
        # self.div_apu = 0
        if self.emulate:
            self.cycles_target_512Hz = self.cycles + CYCLES_512HZ
        else:
            self.cycles_target_512Hz = MAX_CYCLES

    def get(self, offset):
        if not self.emulate:
            return 0
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
        elif offset == 20:  # Control register NR50: Vin enable and volume -- not implemented
            return 0
        elif offset == 21:  # Control register NR51: Channel stereo enable/panning
            return (
                self.noise_left
                | self.wave_left
                | self.tone_left
                | self.sweep_left
                | self.noise_right
                | self.wave_right
                | self.tone_right
                | self.sweep_right
            )
        elif offset == 22:  # Control register NR52: Sound/channel enable
            return (
                0b0111_0000
                | self.poweron
                | self.noisechannel.enable
                | self.wavechannel.enable
                | self.tonechannel.enable
                | self.sweepchannel.enable
            )
        elif offset < 32:  # Unused registers, read as 0xFF
            return 0xFF
        elif offset < 48:  # Wave Table
            return self.wavechannel.getwavebyte(offset - 32)
        else:
            logger.error("Attempted to read register %d in sound memory", offset)

    def set(self, offset, value):
        if not self.emulate:
            return

        # Pan-docs:
        # Read-only until turned back on, except NR52 and the length timers (in NRx1) on monochrome models.
        if offset < 20 and (self.poweron or (not self.cgb and offset % 5 == 1)):
            i = offset // 5
            if i == 0:
                self.sweepchannel.setreg(offset % 5, value)
            elif i == 1:
                self.tonechannel.setreg(offset % 5, value)
            elif i == 2:
                self.wavechannel.setreg(offset % 5, value)
            elif i == 3:
                self.noisechannel.setreg(offset % 5, value)
        elif offset == 20 and self.poweron:  # Control register NR50: Vin enable and volume
            # Not implemented
            pass
        elif offset == 21 and self.poweron:  # Control register NR51: Channel stereo enable/panning
            self.noise_left = value & 0b1000_0000
            self.wave_left = value & 0b0100_0000
            self.tone_left = value & 0b0010_0000
            self.sweep_left = value & 0b0001_0000
            self.noise_right = value & 0b0000_1000
            self.wave_right = value & 0b0000_0100
            self.tone_right = value & 0b0000_0010
            self.sweep_right = value & 0b0000_0001
            return
        elif offset == 22:  # Control register NR52: Sound on/off
            if value & 0x80 == 0:  # Sound power off
                for n in range(22):
                    self.set(n, 0)
                self.poweron = 0
            else:
                self.poweron = 0x80
                # self.reset_apu_div()
        elif offset < 32:  # Unused registers, unwritable?
            pass
        elif offset < 48:  # Wave pattern RAM
            self.wavechannel.setwavebyte(offset - 32, value)
        else:
            logger.error("Attempted to write register %d in sound memory", offset)

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        self.last_cycles = _cycles

        if not self.emulate:
            return

        cycles >>= self.speed_shift

        # Tick channels until point of sample (repeating) or however many cycles we have.
        while cycles > 0:
            if not self.disable_sampling:
                _cycles = max(0, min(double_to_uint64_ceil(self.cycles_target) - self.cycles, cycles))
            else:
                _cycles = cycles

            # Pan Docs:
            # Turning the APU off, however, does not affect ... the DIV-APU counter
            old_div_apu = self.div_apu
            while self.cycles >= self.cycles_target_512Hz:
                self.div_apu += 1
                self.cycles_target_512Hz += CYCLES_512HZ
            div_tick_count = self.div_apu - old_div_apu

            if self.poweron:
                self.sweepchannel.tick(_cycles)
                self.tonechannel.tick(_cycles)
                self.wavechannel.tick(_cycles)
                self.noisechannel.tick(_cycles)

                # Progress the channels by ticks of 512Hz
                for _ in range(div_tick_count):
                    # Pan docs:
                    # A “DIV-APU” counter is increased every time DIV’s bit 4 (5 in double-speed mode) goes from 1 to 0, therefore
                    # at a frequency of 512 Hz (regardless of whether double-speed is active). Thus, the counter can be made to
                    # increase faster by writing to DIV while its relevant bit is set (which clears DIV, and triggers the falling edge).

                    # The following events occur every N DIV-APU ticks:
                    # Event           Rate Frequency3
                    # Envelope sweep  8    64 Hz
                    # Sound length    2    256 Hz
                    # CH1 freq sweep  4    128 Hz
                    # 3 Indicated values are under normal operation; the frequencies will obviously differ if writing to DIV to
                    # increase the counter faster.

                    # Progress the channels by 1 tick at 256Hz
                    if self.div_apu % 2 == 0:
                        self.sweepchannel.tick_length()
                        self.tonechannel.tick_length()
                        self.wavechannel.tick_length()
                        self.noisechannel.tick_length()

                    # Progress the channels by 1 tick at 128Hz
                    if self.div_apu % 4 == 0:
                        self.sweepchannel.tick_sweep()

                    # Progress the channels by 1 tick at 64Hz
                    if self.div_apu % 8 == 0:
                        self.sweepchannel.tick_envelope()
                        self.tonechannel.tick_envelope()
                        self.noisechannel.tick_envelope()

            self.cycles += _cycles
            while self.cycles >= self.cycles_target:
                if not self.disable_sampling:
                    self.sample()
                self.cycles_target += self.cycles_per_sample

            # NOTE: speed_shift because they are using in externally in mb
            self._cycles_to_interrupt = (
                double_to_uint64_ceil(min(self.cycles_target, self.cycles_target_512Hz)) << self.speed_shift
            )
            cycles -= _cycles

    def pcm12(self):
        # NOTE: Volume can apparantly not exceed 15?
        return self.sweepchannel.sample() & 0xF | ((self.tonechannel.sample() & 0xF) << 4)

    def pcm34(self):
        # NOTE: Volume can apparantly not exceed 15?
        return self.wavechannel.sample() & 0xF | ((self.noisechannel.sample() & 0xF) << 4)

    def sample(self):
        if self.poweron:
            # Left channel
            left_sample = 0
            if self.sweep_left:
                left_sample += self.sweepchannel.sample()
            if self.tone_left:
                left_sample += self.tonechannel.sample()
            if self.wave_left:
                left_sample += self.wavechannel.sample()
            if self.noise_left:
                left_sample += self.noisechannel.sample()

            # Right channel
            right_sample = 0
            if self.sweep_right:
                right_sample += self.sweepchannel.sample()
            if self.tone_right:
                right_sample += self.tonechannel.sample()
            if self.wave_right:
                right_sample += self.wavechannel.sample()
            if self.noise_right:
                right_sample += self.noisechannel.sample()

            # Why cap it at 0<=sample<=127 when it's 8 bit and not 7 bit?
            left_sample = min(max(left_sample, 0), 127)
            right_sample = min(max(right_sample, 0), 127)
        else:
            left_sample = 0
            right_sample = 0

        if self.audiobuffer_head >= self.audiobuffer_length:
            logger.critical("Buffer overrun! %d of %d", self.audiobuffer_head, self.audiobuffer_length)
            return
        self.audiobuffer[self.audiobuffer_head] = left_sample
        self.audiobuffer[self.audiobuffer_head + 1] = right_sample

        self.audiobuffer_head += 2

    def clear_buffer(self):
        self.audiobuffer_head = 0

    def save_state(self, file):
        file.write_64bit(self.audiobuffer_head)
        file.write_64bit(self.samples_per_frame)
        for b in struct.pack("d", self.cycles_per_sample):
            file.write(b)

        for n in range(self.audiobuffer_length):
            file.write(self.audiobuffer[n])

        file.write(self.speed_shift)
        for b in struct.pack("d", self.cycles_target):
            file.write(b)
        for b in struct.pack("d", self.cycles_target_512Hz):
            file.write(b)
        file.write_64bit(self._cycles_to_interrupt)

        file.write_64bit(self.cycles)
        file.write_64bit(self.last_cycles)

        file.write_64bit(self.div_apu_counter)
        file.write_64bit(self.div_apu)
        file.write(self.poweron)
        file.write(self.disable_sampling)

        file.write(self.noise_left)
        file.write(self.wave_left)
        file.write(self.tone_left)
        file.write(self.sweep_left)
        file.write(self.noise_right)
        file.write(self.wave_right)
        file.write(self.tone_right)
        file.write(self.sweep_right)

        self.sweepchannel.save_state(file)
        self.tonechannel.save_state(file)
        self.wavechannel.save_state(file)
        self.noisechannel.save_state(file)

    def load_state(self, file, state_version):
        if state_version == 13:
            self.last_cycles = file.read_64bit()
            self.cycles = file.read_64bit()

            self.sweepchannel.load_state(file, state_version)
            self.tonechannel.load_state(file, state_version)
            self.wavechannel.load_state(file, state_version)
            self.noisechannel.load_state(file, state_version)
        elif state_version >= 14:
            self.audiobuffer_head = file.read_64bit()
            _samples_per_frame = file.read_64bit()
            if not _samples_per_frame == self.samples_per_frame:
                raise PyBoyAssertException(
                    "'Samples per frame' of saved state (%d) does not match current configuration (%d)",
                    _samples_per_frame,
                    self.samples_per_frame,
                )
            # self.samples_per_frame = _samples_per_frame
            self.cycles_per_sample = float(struct.unpack("d", bytes([file.read() for _ in range(8)]))[0])

            for n in range(self.audiobuffer_length):
                self.audiobuffer[n] = file.read()

            self.speed_shift = file.read()
            self.cycles_target = float(struct.unpack("d", bytes([file.read() for _ in range(8)]))[0])
            self.cycles_target_512Hz = float(struct.unpack("d", bytes([file.read() for _ in range(8)]))[0])
            self._cycles_to_interrupt = (
                file.read_64bit()
            )  # double_to_uint64_ceil(min(self.cycles_target, self.cycles_target_512Hz))

            self.cycles = file.read_64bit()
            self.last_cycles = file.read_64bit()

            self.div_apu_counter = file.read_64bit()
            self.div_apu = file.read_64bit()
            self.poweron = file.read()
            self.disable_sampling = file.read()

            self.noise_left = file.read()
            self.wave_left = file.read()
            self.tone_left = file.read()
            self.sweep_left = file.read()
            self.noise_right = file.read()
            self.wave_right = file.read()
            self.tone_right = file.read()
            self.sweep_right = file.read()

            self.sweepchannel.load_state(file, state_version)
            self.tonechannel.load_state(file, state_version)
            self.wavechannel.load_state(file, state_version)
            self.noisechannel.load_state(file, state_version)

    def stop(self):
        pass


class ToneChannel:
    """Second sound channel--simple square wave, no sweep"""

    def __init__(self):
        # Shape of square waves at different duty cycles
        # These could ostensibly be replaced with other waves for fun experiments
        self.wavetables = [
            [0, 0, 0, 0, 0, 0, 0, 1],  # 12.5% Duty cycle square
            [1, 0, 0, 0, 0, 0, 0, 1],  # 25%
            [1, 0, 0, 0, 0, 1, 1, 1],  # 50%
            [0, 1, 1, 1, 1, 1, 1, 0],  # 75% (25% inverted)
        ]

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the non-sweep tone channel
        self.wave_duty = 0  # Register 1 bits 7-6: wave table selection (duty cycle)
        self.init_length_timer = 0  # Register 1 bits 5-0: time to play sound before stop (64-x)

        self.envelope_volume = 0  # Register 2 bits 7-4: volume envelope initial volume
        self.envelope_direction = 0  # Register 2 bit 3: volume envelope change direction (0: decrease)
        self.envelope_pace = 0  # Register 2 bits 2-0: volume envelope period (0: disabled)

        self.sound_period = 0  # Register 4 bits 2-0 LSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        self.length_enable = 0  # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.

        # Internal values
        self.enable = 0  # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 64  # Length timer, counts down to disable channel automatically
        self.envelopetimer = 0  # Volume envelope timer, counts down to signal change in volume
        self.periodtimer = 0  # Period timer, counts down to signal change in wave frame
        self.period = 4  # Calculated copy of period, 4 * (2048 - sound_period)
        self.waveframe = 0  # Wave frame index into wave table entries
        self.volume = 0  # Current volume level, modulated by envelope

    def getreg(self, reg):
        if reg == 0:
            return 0
        elif reg == 1:
            return self.wave_duty << 6  # Other bits are write-only
        elif reg == 2:
            return self.envelope_volume << 4 | self.envelope_direction << 3 | self.envelope_pace
        elif reg == 3:
            return 0  # Write-only register?
        elif reg == 4:
            return self.length_enable << 6
        else:
            logger.error("Attempt to read register %d in ToneChannel", reg)

    def setreg(self, reg, val):
        if reg == 0:
            # NR20
            pass
        elif reg == 1:
            # NR11 NR21
            self.wave_duty = (val >> 6) & 0x03
            self.init_length_timer = val & 0x1F
            self.lengthtimer = 64 - self.init_length_timer
        elif reg == 2:
            # NR12 NR22
            self.envelope_volume = (val >> 4) & 0x0F
            self.envelope_direction = (val >> 3) & 0x01
            self.envelope_pace = val & 0x07
            if self.envelope_volume == 0 and self.envelope_direction == 0:
                self.enable = 0
        elif reg == 3:
            # NR13 NR23
            self.sound_period = (self.sound_period & 0x700) | val
            # The pulse channels’ period dividers are clocked at 1048576 Hz (not the same as wave channel!)
            self.period = 4 * (0x800 - self.sound_period)
        elif reg == 4:
            # NR14 NR24
            self.length_enable = (val >> 6) & 0x01
            self.sound_period = ((val << 8) & 0x0700) | (self.sound_period & 0xFF)
            # The pulse channels’ period dividers are clocked at 1048576 Hz (not the same as wave channel!)
            self.period = 4 * (0x800 - self.sound_period)
            if val & 0x80:
                self.trigger()  # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            logger.error("Attempt to write register%d} in ToneChannel", reg)

    def tick(self, cycles):
        self.periodtimer -= cycles
        while self.periodtimer <= 0:
            self.periodtimer += self.period
            self.waveframe = (self.waveframe + 1) % 8

    def tick_length(self):
        if self.length_enable and self.lengthtimer > 0:
            self.lengthtimer -= 1
            if self.lengthtimer == 0:
                self.enable = 0

    def tick_envelope(self):
        if self.envelopetimer != 0:
            self.envelopetimer -= 1
            if self.envelopetimer == 0:
                newvolume = self.volume + (self.envelope_direction or -1)
                if newvolume < 0 or newvolume > 15:
                    self.envelopetimer = 0
                else:
                    self.envelopetimer = self.envelope_pace
                    self.volume = newvolume
                # Note that setting envelopetimer to 0 disables it

    def sample(self):
        if self.enable:
            return self.volume * self.wavetables[self.wave_duty][self.waveframe]
        else:
            return 0

    def trigger(self):
        self.enable = 0x02
        self.lengthtimer = self.lengthtimer or 64
        self.periodtimer = self.period
        self.envelopetimer = self.envelope_pace
        self.volume = self.envelope_volume
        # TODO: If channel DAC is off (NRx2 & 0xF8 == 0) then this
        #   will be undone and the channel immediately disabled.
        #   Probably need a new DAC power state/variable.
        # For now:
        if self.envelope_pace == 0 and self.envelope_volume == 0:
            self.enable = 0

    def save_state(self, file):
        file.write(self.wave_duty)
        file.write(self.init_length_timer)

        file.write(self.envelope_volume)
        file.write(self.envelope_direction)
        file.write(self.envelope_pace)

        file.write_16bit(self.sound_period)
        file.write(self.length_enable)

        file.write(self.enable)
        file.write_64bit(self.lengthtimer)
        file.write_64bit(self.envelopetimer)
        file.write_64bit(self.periodtimer)
        file.write_64bit(self.period)
        file.write_64bit(self.waveframe)
        file.write_64bit(self.volume)

    def load_state(self, file, state_version):
        self.wave_duty = file.read()
        self.init_length_timer = file.read()

        self.envelope_volume = file.read()
        self.envelope_direction = file.read()
        self.envelope_pace = file.read()

        self.sound_period = file.read_16bit()
        self.length_enable = file.read()

        self.enable = file.read()
        self.lengthtimer = file.read_64bit()
        self.envelopetimer = file.read_64bit()
        self.periodtimer = file.read_64bit()
        self.period = file.read_64bit()
        self.waveframe = file.read_64bit()
        self.volume = file.read_64bit()


class SweepChannel(ToneChannel):
    def __init__(self):
        ToneChannel.__init__(self)
        # Register Values
        self.sweep_pace = 0  # Register 0 bits 6-4: Sweep pace
        self.sweep_direction = 0  # Register 0 bit 3: Sweep direction (0: increase)
        # Pan docs:
        # Note that the value written to this field is not re-read by the hardware until a sweep iteration completes,
        # or the channel is (re)triggered.
        self.sweep_magnitude = 0  # Register 0 bits 2-0: Sweep size as a bit shift
        # self.sweep_magnitude_latch = 0

        # Internal Values
        self.sweeptimer = 0  # Sweep timer, counts down to shift pitch
        self.sweepenable = False  # Internal sweep enable flag
        self.shadow = 0  # Shadow copy of period register for ignoring writes to sndper

    def getreg(self, reg):
        if reg == 0:
            return self.sweep_pace << 4 | self.sweep_direction << 3 | self.sweep_magnitude | 0x80
        else:
            return ToneChannel.getreg(self, reg)

    def setreg(self, reg, val):
        if reg == 0:
            # NR10
            self.sweep_pace = val >> 4 & 0x07
            self.sweep_direction = val >> 3 & 0x01

            # self.sweep_magnitude_latch = val & 0x07
            self.sweep_magnitude = val & 0x07
            # However, if 0 is written to this field, then iterations are instantly disabled,
            # and it will be reloaded as soon as it’s set to something else.
            # if self.sweep_magnitude_latch == 0:
            #     self.sweep_magnitude = 0
        else:
            ToneChannel.setreg(self, reg, val)

    def tick_sweep(self):
        # Clock sweep timer on 2 and 6
        if self.sweepenable and self.sweep_pace:
            self.sweeptimer -= 1
            if self.sweeptimer == 0:
                if self.sweep(True):
                    self.sweeptimer = self.sweep_pace
                    self.sweep(False)

    def trigger(self):
        ToneChannel.trigger(self)
        if self.enable:  # Fixes NR52 enabled read
            self.enable = 0x01
        self.shadow = self.sound_period
        self.sweeptimer = self.sweep_pace
        # self.sweep_magnitude = self.sweep_magnitude_latch
        self.sweepenable = self.sweep_pace or self.sweep_magnitude
        if self.sweep_magnitude:
            self.sweep(False)

    def sweep(self, save):
        if self.sweep_direction == 0:
            newper = self.shadow + (self.shadow >> self.sweep_magnitude)
        else:
            newper = self.shadow - (self.shadow >> self.sweep_magnitude)

        # Pan Docs:
        # Note that if the period ever becomes 0, the period sweep will never be able to change it. For the same reason,
        # the period sweep cannot underflow the period (which would turn the channel off).

        # Pan Docs:
        # If the period value would overflow (i.e. ... more than $7FF), the channel is turned off instead
        if newper >= 0x800:  # NOTE: Pan docs: This occurs even if sweep iterations are disabled by the pace being 0.
            self.enable = False
            # Is this "sweep complete?"
            # self.sweep_magnitude = self.sweep_magnitude_latch
            return False
        elif save and self.sweep_magnitude:
            # Pan Docs:
            # On each sweep iteration, the period in NR13 and NR14 is modified and written back.
            self.sound_period = self.shadow = newper
            self.period = 4 * (0x800 - self.sound_period)  # 2048*4 = 8192 cycles = 512Hz
            return True

    def save_state(self, file):
        ToneChannel.save_state(self, file)
        file.write(self.sweep_pace)
        file.write(self.sweep_direction)
        file.write(self.sweep_magnitude)
        file.write_64bit(self.sweeptimer)
        file.write(self.sweepenable)
        file.write_64bit(self.shadow)

    def load_state(self, file, state_version):
        ToneChannel.load_state(self, file, state_version)
        self.sweep_pace = file.read()
        self.sweep_direction = file.read()
        self.sweep_magnitude = file.read()
        self.sweeptimer = file.read_64bit()
        self.sweepenable = file.read()
        self.shadow = file.read_64bit()


class WaveChannel:
    """Third sound channel--sample-based playback"""

    def __init__(self, cgb):
        # Memory for wave sample
        self.wavetable = array("B", [0xFF] * 16)
        self.cgb = cgb

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the wave channel
        self.dacpow = 0  # Register 0 bit 7: DAC Power, enable playback
        self.init_length_timer = 0  # Register 1 bits 7-0: time to play sound before stop (256-x)
        self.volreg = 0  # Register 2 bits 6-5: volume code
        self.sound_period = 0  # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.length_enable = 0  # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

        # Internal values
        self.enable = 0  # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 256  # Length timer, counts down to disable channel automatically
        self.periodtimer = 0  # Period timer, counts down to signal change in wave frame
        self.period = 4  # Calculated copy of period, 4 * (0x800 - sndper)
        self.waveframe = 0  # Wave frame index into wave table entries
        self.volumeshift = 0  # Bitshift for volume, set by volreg

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
            return self.length_enable << 6 | 0xBF
        else:
            logger.error("Attempt to read register %d in ToneChannel", reg)

    def setreg(self, reg, val):
        if reg == 0:
            self.dacpow = val >> 7 & 0x01
            if self.dacpow == 0:
                self.enable = 0
        elif reg == 1:
            self.init_length_timer = val
            self.lengthtimer = 256 - self.init_length_timer
        elif reg == 2:
            self.volreg = val >> 5 & 0x03
            if self.volreg > 0:
                self.volumeshift = self.volreg - 1
            else:
                self.volumeshift = 4  # Muted as it's a 4-bit wave table
        elif reg == 3:
            self.sound_period = (self.sound_period & 0x700) + val
            # The wave channel’s period divider is clocked at 2097152 Hz (not the same as tone channels!)
            self.period = 2 * (0x800 - self.sound_period)  # Cycles per period
        elif reg == 4:
            self.length_enable = val >> 6 & 0x01
            self.sound_period = (val << 8 & 0x0700) + (self.sound_period & 0xFF)
            # The wave channel’s period divider is clocked at 2097152 Hz (not the same as tone channels!)
            self.period = 2 * (0x800 - self.sound_period)  # Cycles per period
            if val & 0x80:
                self.trigger()  # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            logger.error("Attempt to write register %d in WaveChannel", reg)

    def getwavebyte(self, offset):
        # Pan docs:
        # Wave RAM can be accessed normally even if the DAC is on, as long as the channel is not active.
        if self.enable:
            if self.cgb:
                return self.wavetable[self.waveframe % 16]
            else:
                # Pan docs:
                # On monochrome consoles, wave RAM can only be accessed on the same cycle that CH3 does. Otherwise,
                # reads return $FF, and writes are ignored.
                return 0xFF
        else:
            return self.wavetable[offset]

    def setwavebyte(self, offset, value):
        # Pan docs:
        # Wave RAM can be accessed normally even if the DAC is on, as long as the channel is not active.
        if self.enable:
            if self.cgb:
                self.wavetable[self.waveframe % 16] = value
            else:
                pass
        else:
            self.wavetable[offset] = value

    def tick(self, cycles):
        self.periodtimer -= cycles
        while self.periodtimer <= 0:
            self.periodtimer += self.period
            self.waveframe += 1
            self.waveframe %= 32

    def tick_length(self):
        if self.length_enable and self.lengthtimer > 0:
            self.lengthtimer -= 1
            if self.lengthtimer == 0:
                self.enable = 0

    def sample(self):
        if self.enable and self.dacpow:
            sample = self.wavetable[self.waveframe // 2]
            if self.waveframe % 2 == 1:  # Read 4-bit value
                sample >>= 4
            sample &= 0x0F
            return sample >> self.volumeshift
        else:
            return 0

    def trigger(self):
        self.enable = 0x04 if self.dacpow else 0
        self.lengthtimer = self.lengthtimer or 256
        self.periodtimer = self.period
        # self.waveframe = 1 # Implement CH3 bug, that first sample is skipped

    def save_state(self, file):
        for n in range(16):
            file.write(self.wavetable[n])

        file.write(self.dacpow)
        file.write(self.init_length_timer)
        file.write(self.volreg)
        file.write_16bit(self.sound_period)
        file.write(self.length_enable)

        file.write(self.enable)
        file.write_64bit(self.lengthtimer)
        file.write_64bit(self.periodtimer)
        file.write_64bit(self.period)
        file.write_64bit(self.waveframe)
        file.write_64bit(self.volumeshift)

    def load_state(self, file, state_version):
        for n in range(16):
            self.wavetable[n] = file.read()

        self.dacpow = file.read()
        self.init_length_timer = file.read()
        self.volreg = file.read()
        self.sound_period = file.read_16bit()
        self.length_enable = file.read()

        self.enable = file.read()
        self.lengthtimer = file.read_64bit()
        self.periodtimer = file.read_64bit()
        self.period = file.read_64bit()
        self.waveframe = file.read_64bit()
        self.volumeshift = file.read_64bit()


class NoiseChannel:
    """Fourth sound channel--white noise generator"""

    def __init__(self):
        self.DIVTABLE = (8, 16, 32, 48, 64, 80, 96, 112)

        # Register values (abbreviated to keep track of what's external)
        # Register 0 is unused in the noise channel
        self.init_length_timer = 0  # Register 1 bits 5-0: time to play sound before stop (64-x)
        self.envelope_volume = 0  # Register 2 bits 7-4: volume envelope initial volume
        self.envelope_direction = 0  # Register 2 bit 3: volume envelope change direction (0: decrease)
        self.envelope_pace = 0  # Register 2 bits 2-0: volume envelope period (0: disabled)
        self.clkpow = 0  # Register 3 bits 7-4: lfsr clock shift
        self.regwid = 0  # Register 3 bit 3: lfsr bit width (0: 15, 1: 7)
        self.clkdiv = 0  # Register 3 bits 2-0: base divider for lfsr clock
        # Register 4 bit 7: Write-only trigger bit. Process immediately.
        self.length_enable = 0  # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

        # Internal values
        self.enable = 0  # Enable flag, turned on by trigger bit and off by length timer
        self.lengthtimer = 64  # Length timer, counts down to disable channel automatically
        self.periodtimer = 0  # Period timer, counts down to signal change in wave frame
        self.envelopetimer = 0  # Volume envelope timer, counts down to signal change in volume
        self.period = 8  # Calculated copy of period, 8 << 0
        self.shiftregister = 1  # Internal shift register value
        self.lfsrfeed = 0x4000  # Bit mask for inserting feedback in shift register
        self.volume = 0  # Current volume level, modulated by envelope

    def getreg(self, reg):
        if reg == 0:
            return 0xFF
        elif reg == 1:
            return 0xFF
        elif reg == 2:
            return self.envelope_volume << 4 | self.envelope_direction << 3 | self.envelope_pace
        elif reg == 3:
            return self.clkpow << 4 | self.regwid << 3 | self.clkdiv
        elif reg == 4:
            return self.length_enable << 6 | 0xBF
        else:
            logger.error("Attempt to read register %d in NoiseChannel", reg)

    def setreg(self, reg, val):
        if reg == 0:
            return
        elif reg == 1:
            self.init_length_timer = val & 0x1F
            self.lengthtimer = 64 - self.init_length_timer
        elif reg == 2:
            self.envelope_volume = val >> 4 & 0x0F
            self.envelope_direction = val >> 3 & 0x01
            self.envelope_pace = val & 0x07
            if self.envelope_volume == 0 and self.envelope_direction == 0:
                self.enable = 0
        elif reg == 3:
            self.clkpow = val >> 4 & 0x0F
            self.regwid = val >> 3 & 0x01
            self.clkdiv = val & 0x07
            self.period = self.DIVTABLE[self.clkdiv] << self.clkpow
            self.lfsrfeed = 0x4040 if self.regwid else 0x4000
        elif reg == 4:
            self.length_enable = val >> 6 & 0x01
            if val & 0x80:
                self.trigger()  # Sync is called first in Sound.set so it's okay to trigger immediately
        else:
            logger.error("Attempt to write register %d in ToneChannel", reg)

    def tick(self, cycles):
        self.periodtimer -= cycles
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

    def tick_length(self):
        if self.length_enable and self.lengthtimer > 0:
            self.lengthtimer -= 1
            if self.lengthtimer == 0:
                self.enable = 0

    def tick_envelope(self):
        if self.envelopetimer != 0:
            self.envelopetimer -= 1
            if self.envelopetimer == 0:
                newvolume = self.volume + (self.envelope_direction or -1)
                if newvolume < 0 or newvolume > 15:
                    self.envelopetimer = 0
                else:
                    self.envelopetimer = self.envelope_pace
                    self.volume = newvolume
                # Note that setting envelopetimer to 0 disables it

    def sample(self):
        if self.enable:
            return self.volume if self.shiftregister & 0x01 == 0 else 0
        else:
            return 0

    def trigger(self):
        self.enable = 0x08
        self.lengthtimer = self.lengthtimer or 64
        self.periodtimer = self.period
        self.envelopetimer = self.envelope_pace
        self.volume = self.envelope_volume
        self.shiftregister = 0x7FFF
        # TODO: tidy instead of double change variable
        if self.envelope_pace == 0 and self.envelope_volume == 0:
            self.enable = 0

    def save_state(self, file):
        file.write(self.init_length_timer)
        file.write(self.envelope_volume)
        file.write(self.envelope_direction)
        file.write(self.envelope_pace)
        file.write(self.clkpow)
        file.write(self.regwid)
        file.write(self.clkdiv)
        file.write(self.length_enable)

        file.write(self.enable)
        file.write_64bit(self.lengthtimer)
        file.write_64bit(self.periodtimer)
        file.write_64bit(self.envelopetimer)
        file.write_64bit(self.period)
        file.write_64bit(self.shiftregister)
        file.write_64bit(self.lfsrfeed)
        file.write_64bit(self.volume)

    def load_state(self, file, state_version):
        self.init_length_timer = file.read()
        self.envelope_volume = file.read()
        self.envelope_direction = file.read()
        self.envelope_pace = file.read()
        self.clkpow = file.read()
        self.regwid = file.read()
        self.clkdiv = file.read()
        self.length_enable = file.read()

        self.enable = file.read()
        self.lengthtimer = file.read_64bit()
        self.periodtimer = file.read_64bit()
        self.envelopetimer = file.read_64bit()
        self.period = file.read_64bit()
        self.shiftregister = file.read_64bit()
        self.lfsrfeed = file.read_64bit()
        self.volume = file.read_64bit()
