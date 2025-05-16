#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport int8_t, int64_t, uint8_t, uint16_t, uint64_t

from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface, double_to_uint64_ceil

cdef int FRAME_CYCLES
cdef uint64_t MAX_CYCLES

cdef Logger logger

cdef uint64_t CYCLES_512HZ

cdef class Sound:
    cdef int64_t volume
    cdef bint emulate, cgb, disable_sampling

    cdef uint64_t sample_rate

    cdef uint64_t cycles
    cdef cython.double cycles_target
    cdef cython.double cycles_target_512Hz
    cdef uint64_t last_cycles
    cdef uint64_t _cycles_to_interrupt

    cdef uint8_t speed_shift

    cdef uint64_t div_apu_counter
    cdef uint64_t div_apu

    cdef uint8_t poweron

    cdef readonly uint64_t audiobuffer_head
    cdef uint64_t audiobuffer_length
    cdef uint64_t samples_per_frame
    cdef cython.double cycles_per_sample
    cdef int8_t[:] audiobuffer
    cdef str buffer_format

    cdef uint8_t noise_left
    cdef uint8_t wave_left
    cdef uint8_t tone_left
    cdef uint8_t sweep_left
    cdef uint8_t noise_right
    cdef uint8_t wave_right
    cdef uint8_t tone_right
    cdef uint8_t sweep_right

    cdef SweepChannel sweepchannel
    cdef ToneChannel tonechannel
    cdef WaveChannel wavechannel
    cdef NoiseChannel noisechannel

    cdef uint8_t get(self, uint8_t) noexcept nogil
    cdef void set(self, uint8_t, uint8_t) noexcept nogil

    @cython.locals(cycles=uint64_t, _cycles=uint64_t)
    cdef void tick(self, uint64_t) noexcept nogil
    cdef void sample(self) noexcept nogil
    cdef uint8_t pcm12(self) noexcept nogil
    cdef uint8_t pcm34(self) noexcept nogil
    cdef void clear_buffer(self) noexcept nogil
    cdef void reset_apu_div(self) noexcept nogil
    cdef void stop(self) noexcept

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

cdef class ToneChannel:
    cdef uint8_t[4][8] wavetables

    cdef uint8_t wave_duty # Register 1 bits 7-6: wave table selection (duty cycle)
    cdef uint8_t init_length_timer # Register 1 bits 5-0: time to play sound before stop (64-x)
    cdef uint8_t envelope_volume # Register 2 bits 7-4: volume envelope initial volume
    cdef uint8_t envelope_direction # Register 2 bit 3: volume envelope change direction (0: decrease)
    cdef uint8_t envelope_pace # Register 2 bits 2-0: volume envelope period (0: disabled)
    cdef uint16_t sound_period # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t length_enable # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef int64_t enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int64_t lengthtimer # Length timer, counts down to disable channel automatically
    cdef int64_t periodtimer # Period timer, counts down to signal change in wave frame
    cdef int64_t envelopetimer # Volume envelope timer, counts down to signal change in volume
    cdef int64_t period # Calculated copy of period, 4 * (2048 - sndper)
    cdef int64_t waveframe # Wave frame index into wave table entries
    cdef int64_t volume # Current volume level, modulated by envelope

    cdef uint8_t getreg(self, uint8_t) noexcept nogil
    cdef void setreg(self, uint8_t, uint8_t) noexcept nogil
    cdef void tick(self, uint64_t) noexcept nogil
    cdef void tick_length(self) noexcept nogil
    cdef void tick_envelope(self) noexcept nogil
    cdef uint8_t sample(self) noexcept nogil
    cdef void trigger(self) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

cdef class SweepChannel(ToneChannel):
    # Register Values
    cdef uint8_t sweep_pace # Register 0 bits 6-4: Sweep period
    cdef uint8_t sweep_direction # Register 0 bit 3: Sweep direction (0: increase)
    cdef uint8_t sweep_magnitude # Register 0 bits 2-0: Sweep size as a bit shift

    # Internal Values
    cdef int64_t sweeptimer # Sweep timer, counts down to shift pitch
    cdef bint sweepenable # Internal sweep enable flag
    cdef int64_t shadow # Shadow copy of period register for ignoring writes to sndper
    cdef void tick_sweep(self) noexcept nogil
    cdef bint sweep(self, bint) noexcept nogil


cdef class WaveChannel:
    # Memory for wave sample
    cdef uint8_t[16] wavetable
    cdef bint cgb

    # Register values (abbreviated to keep track of what's external)
    # Register 0 is unused in the wave channel
    cdef uint8_t dacpow # Register 0 bit 7: DAC Power, enable playback
    cdef uint8_t init_length_timer # Register 1 bits 7-0: time to play sound before stop (256-x)
    cdef uint8_t volreg # Register 2 bits 6-5: volume code
    cdef uint16_t sound_period # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t length_enable # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef bint enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int64_t lengthtimer # Length timer, counts down to disable channel automatically
    cdef int64_t periodtimer # Period timer, counts down to signal change in wave frame
    cdef int64_t period # Calculated copy of period, 4 * (2048 - sndper)
    cdef int64_t waveframe # Wave frame index into wave table entries
    cdef int64_t volumeshift # Bitshift for volume, set by volreg

    cdef uint8_t getreg(self, uint8_t) noexcept nogil
    cdef void setreg(self, uint8_t, uint8_t) noexcept nogil
    cdef void tick(self, uint64_t) noexcept nogil
    cdef void tick_length(self) noexcept nogil
    cdef uint8_t sample(self) noexcept nogil
    cdef void trigger(self) noexcept nogil
    cdef uint8_t getwavebyte(self, uint8_t) noexcept nogil
    cdef void setwavebyte(self, uint8_t, uint8_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1


cdef class NoiseChannel:
    cdef uint8_t[8] DIVTABLE

    # Register values (abbreviated to keep track of what's external)
    # Register 0 is unused in the noise channel
    cdef uint8_t init_length_timer # Register 1 bits 5-0: time to play sound before stop (64-x)
    cdef uint8_t envelope_volume # Register 2 bits 7-4: volume envelope initial volume
    cdef uint8_t envelope_direction # Register 2 bit 3: volume envelope change direction (0: decrease)
    cdef uint8_t envelope_pace # Register 2 bits 2-0: volume envelope period (0: disabled)
    cdef uint8_t clkpow # Register 3 bits 7-4: lfsr clock shift
    cdef uint8_t regwid # Register 3 bit 3: lfsr bit width (0: 15, 1: 7)
    cdef uint8_t clkdiv # Register 3 bits 2-0: base divider for lfsr clock
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t length_enable # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef bint enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int64_t lengthtimer # Length timer, counts down to disable channel automatically
    cdef int64_t periodtimer # Period timer, counts down to signal change in wave frame
    cdef int64_t envelopetimer # Volume envelope timer, counts down to signal change in volume
    cdef int64_t period # Calculated copy of period, 8 << 0
    cdef int64_t shiftregister # Internal shift register value
    cdef int64_t lfsrfeed # Bit mask for inserting feedback in shift register
    cdef int64_t volume # Current volume level, modulated by envelope

    cdef uint8_t getreg(self, uint8_t) noexcept nogil
    cdef void setreg(self, uint8_t, uint8_t) noexcept nogil
    cdef void tick(self, uint64_t) noexcept nogil
    cdef void tick_length(self) noexcept nogil
    cdef void tick_envelope(self) noexcept nogil
    cdef uint8_t sample(self) noexcept nogil
    cdef void trigger(self) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
