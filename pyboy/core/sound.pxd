#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
# cimport sdl2
from libc.stdint cimport uint8_t, uint16_t, uint64_t
from pyboy.utils cimport IntIOInterface

cdef int SOUND_DESYNC_THRESHOLD
cdef int CPU_FREQ

cdef class Sound:
    cdef uint8_t[8*1024] internal_ram0
    cdef uint8_t[0x60] non_io_internal_ram0
    cdef uint8_t[0x4C] io_ports
    cdef uint8_t[0x7F] internal_ram1
    cdef uint8_t[0x34] non_io_internal_ram1
    cdef uint8_t[0x01] interrupt_register

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)

    cdef int device

    cdef int sample_rate
    cdef int sampleclocks
    # cdef uint8_t[4096] audiobuffer
    cdef object audiobuffer
    cdef object audiobuffer_p

    cdef int clock

    cdef bint poweron

    cdef SweepChannel sweepchannel
    cdef ToneChannel tonechannel
    cdef WaveChannel wavechannel
    cdef NoiseChannel noisechannel

    cdef bint leftnoise, leftwave, lefttone, leftsweep, rightnoise, rightwave, righttone, rightsweep

    cdef uint8_t get(self, uint8_t)
    cdef void set(self, uint8_t, uint8_t)

    @cython.locals(nsamples=int, sample=int, i=int, queued_time=int, )
    cdef void sync(self)


cdef class ToneChannel:
    cdef uint8_t[4][8] wavetables

    cdef uint8_t wavsel # Register 1 bits 7-6: wave table selection (duty cycle)
    cdef uint8_t sndlen # Register 1 bits 5-0: time to play sound before stop (64-x)
    cdef uint8_t envini # Register 2 bits 7-4: volume envelope initial volume
    cdef uint8_t envdir # Register 2 bit 3: volume envelope change direction (0: decrease)
    cdef uint8_t envper # Register 2 bits 2-0: volume envelope period (0: disabled)
    cdef uint16_t sndper # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t uselen # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef bint enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int lengthtimer # Length timer, counts down to disable channel automatically
    cdef int periodtimer # Period timer, counts down to signal change in wave frame
    cdef int envelopetimer # Volume envelope timer, counts down to signal change in volume
    cdef int period # Calculated copy of period, 4 * (2048 - sndper)
    cdef int waveframe # Wave frame index into wave table entries
    cdef int frametimer # Frame sequencer timer, underflows to signal change in frame sequences
    cdef int frame # Frame sequencer value, generates clocks for length/envelope/(sweep)
    cdef int volume # Current volume level, modulated by envelope

    cdef uint8_t getreg(self, uint8_t)
    cdef void setreg(self, uint8_t, uint8_t)
    cdef void run(self, uint64_t)
    cdef uint8_t sample(self)
    cdef void trigger(self)
    cdef void tickframe(self)


cdef class SweepChannel(ToneChannel):
    # Register Values
    cdef uint8_t swpper # Register 0 bits 6-4: Sweep period
    cdef uint8_t swpdir # Register 0 bit 3: Sweep direction (0: increase)
    cdef uint8_t swpmag # Register 0 bits 2-0: Sweep size as a bit shift

    # Internal Values
    cdef int sweeptimer # Sweep timer, counts down to shift pitch
    cdef bint sweepenable # Internal sweep enable flag
    cdef int shadow # Shadow copy of period register for ignoring writes to sndper

    cdef uint8_t getreg(self, uint8_t)
    cdef void setreg(self, uint8_t, uint8_t)
    cdef bint sweep(self, bint)
    cdef void trigger(self)
    cdef void tickframe(self)


cdef class WaveChannel:
    # Memory for wave sample
    cdef uint8_t[16] wavetable

    # Register values (abbreviated to keep track of what's external)
    # Register 0 is unused in the wave channel
    cdef uint8_t dacpow # Register 0 bit 7: DAC Power, enable playback
    cdef uint8_t sndlen # Register 1 bits 7-0: time to play sound before stop (256-x)
    cdef uint8_t volreg # Register 2 bits 6-5: volume code
    cdef uint16_t sndper # Register 4 bits 2-0 MSB + register 3 all: period of tone ("frequency" on gg8 wiki)
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t uselen # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef bint enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int lengthtimer # Length timer, counts down to disable channel automatically
    cdef int periodtimer # Period timer, counts down to signal change in wave frame
    cdef int period # Calculated copy of period, 4 * (2048 - sndper)
    cdef int waveframe # Wave frame index into wave table entries
    cdef int frametimer # Frame sequencer timer, underflows to signal change in frame sequences
    cdef int frame # Frame sequencer value, generates clocks for length/envelope/(sweep)
    cdef int volumeshift # Bitshift for volume, set by volreg

    cdef uint8_t getreg(self, uint8_t)
    cdef void setreg(self, uint8_t, uint8_t)
    cdef void run(self, uint64_t)
    cdef uint8_t sample(self)
    cdef void trigger(self)
    cdef void tickframe(self)
    cdef uint8_t getwavebyte(self, uint8_t)
    cdef void setwavebyte(self, uint8_t, uint8_t)


cdef class NoiseChannel:
    cdef uint8_t[8] DIVTABLE

    # Register values (abbreviated to keep track of what's external)
    # Register 0 is unused in the noise channel
    cdef uint8_t sndlen # Register 1 bits 5-0: time to play sound before stop (64-x)
    cdef uint8_t envini # Register 2 bits 7-4: volume envelope initial volume
    cdef uint8_t envdir # Register 2 bit 3: volume envelope change direction (0: decrease)
    cdef uint8_t envper # Register 2 bits 2-0: volume envelope period (0: disabled)
    cdef uint8_t clkpow # Register 3 bits 7-4: lfsr clock shift
    cdef uint8_t regwid # Register 3 bit 3: lfsr bit width (0: 15, 1: 7)
    cdef uint8_t clkdiv # Register 3 bits 2-0: base divider for lfsr clock
    # Register 4 bit 7: Write-only trigger bit. Process immediately.
    cdef uint8_t uselen # Register 4 bit 6: enable/disable sound length timer in reg 1 (0: continuous)

    # Internal values
    cdef bint enable # Enable flag, turned on by trigger bit and off by length timer
    cdef int lengthtimer # Length timer, counts down to disable channel automatically
    cdef int periodtimer # Period timer, counts down to signal change in wave frame
    cdef int envelopetimer # Volume envelope timer, counts down to signal change in volume
    cdef int period # Calculated copy of period, 8 << 0
    cdef int shiftregister # Internal shift register value
    cdef int lfsrfeed # Bit mask for inserting feedback in shift register
    cdef int frametimer # Frame sequencer timer, underflows to signal change in frame sequences
    cdef int frame # Frame sequencer value, generates clocks for length/envelope/(sweep)
    cdef int volume # Current volume level, modulated by envelope

    cdef uint8_t getreg(self, uint8_t)
    cdef void setreg(self, uint8_t, uint8_t)
    cdef void run(self, uint64_t)
    cdef uint8_t sample(self)
    cdef void trigger(self)
    cdef void tickframe(self)
