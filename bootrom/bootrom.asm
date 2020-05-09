SECTION "bootrom", ROM0[$0000]
    ; Init stackpointer
    ld SP, $FFFE

    ; Erase VRAM - it is filled with garbage on startup on hardware
    ld HL,$8000
.erase:
    xor A
    ld [HL+],A
    ld A, H
    cp $A0 ; Once HL hits $A000, break out of loop
    jr nz, .erase

    ; ####################
    ; Tile data copying
    ; ####################

    ; Copy 48 bytes of logo data to VRAM
    ; Write length
    ; Use double write
    ld BC, 48 << 8 | 1
    ld HL, Logo  ; Logo data start
    ld DE, $8010 ; Place it 1 tile in, so tile 0 stays white
.memcpy:
    ; Logo memcpy. HL is source, DE is target, B is length
    ld A, [HL+]

    ; Double up memory values for VRAM, as source image is 1-bit
    ld [DE], A
    inc DE
    ld [DE], A
    inc DE

    dec B
    jr NZ, .memcpy

    ; ####################
    ; Tile placement
    ; ####################
    ; Add two upper part of P for the P and B
    ld A, 1 ; A is 0 from before so just increment
    ld HL, $9808+($20*8)
    ld [HL+], A         ; The P position
    inc HL              ; Empty space above y
    ld [HL], A          ; The B position

    ; Add lower part of P, upper part of y, a wrong tile for the lower part of B, and the O. We'll correct the B later.
    ld B, 4             ; Loop counter
    ld A, 2             ; P2 tile index
    ld HL, $9808+($20*9)
.four_range:
    ld [HL+], A
    inc A
    dec B
    jr NZ, .four_range

    ; Add the upper part of the last Y at the current HL position
    ld A, 3             ; Y1 tile index
    ld [HL], A

    add A, A            ; Y2 tile index coincidentally 2xA
    ld HL, $9808+($20*10)+1
    ld [HL+], A
    inc HL
    inc HL
    ld [HL], A

    ; Enable LCD and background tilemap
    ld A, $91
    ldh [$FF00+$40], A

    ; Set color palette to 11111100
    ld A, $FC
    ldh [$FF00+$47], A

    ; Sound Setup
    ld A, $80
    ldh [$26], A ; Enable sound - NR52
    ldh [$11], A ; Use 50% duty cycle - NR11
    ld A, $F3
    ldh [$12], A
    ldh [$25], A
    ld A, $77
    ldh [$24], A

    ; #########################
    ; Graphics effect and wait
    ; #########################

    ; Wait an arbitrary 60 frames

    ld C, 60        ; Frame count

    xor A
    ld D, A         ; Reset D
    ld B, A         ; Reset B
.wait_vblank:
    ; Test vblank
    ldh A, [$FF00+$44]
    cp $90
    jr Z, .exit_vblank

    ld E, A         ; Save LY in E

    ; Invert frame counter to 1-60 instead of 60-1
    ld A, C
    cpl
    sub ($ff-16*7)  ; Start X lines down. Do it in multiple of 16 to fit wave

    ; Cut out one wave
    ; Is A larger than LY? Then we want the effect
    cp E
    jr C, NoEffect
    ; Is LY no more than 16 lines larger than A?
    sub A, 16
    cp E
    jr C, Effect
    ; Fall through to no effect
.no_effect:
    xor A
    ldh [$FF00+$43], A
    jr .wait_vblank

.play_sound:
    ; Adjust frequency sweep
    ld A, %0010011
    ldh [$10], A

    ld A, $48
    ldh [$13], A

    ; Trigger
    ld A, $81
    ldh [$14], A
    ret

.adj_sound:
    ; Adjust frequency sweep
    ld A, %0011001
    ldh [$10], A

    ; Trigger
    ld A, $81
    ldh [$14], A
    ret


.wave_table:
    DB 0, 0, 1, 2, 2, 3, 3, 3, 2, 1, 1, 0, 0, 0, 0, 0

.effect:
    ld A, C        ; Load frame counter for "time"
    add A, E         ; add LY from E
    and $0F         ; Clamp LY value to lookup table length
    ld E, A         ; Save LY in E
    ld HL, .wave_table
    add HL, DE      ; look up in wave table
    ld A, [HL]

    ldh [$FF00+$43], A
    jr .wait_vblank

.exit_vblank:
    ldh A, [$FF00+$44]
    cp $90
    jr Z, .exit_vblank
    ld A, c

    cp 27
    call z, .play_sound

    cp 31
    call z, .adj_sound

    ; One frame has passed, decrement counter
    dec C
    jr NZ, .wait_vblank

    ; TODO: Restore register values?
    jr .exit

; Logo generated by png_to_tiles.py. Remember to update copy range if dimensions change
INCLUDE "logo.asm"

SECTION "epilog", ROM0[$00FC]
.exit:
    ; A is the register that matters
    ; Games check a for $01 and $11, for DMG and CGB respectively
    ld A, $01
    ldh [$FF00+$50], A
