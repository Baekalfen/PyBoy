INCLUDE "bootrom_common.asm"

SECTION "epilog", ROM0[$00F0]
exit:
    ld A, [0x0143] ; Cartridge compatibilty flag
    bit 7, A ; Check if CGB cartridge (0x80 or 0xC0)
    jr nz, _exit ; skip if CGB
    ld A, 4 ;  DMG-mode compatibility flag
_exit:
    ld [0xFF4C], A ; Write compatibility flag to key0
    ; A is the register that matters
    ; Games check a for $01 and $11, for DMG and CGB respectively
    ld A, $11
    ldh [$FF00+$50], A
