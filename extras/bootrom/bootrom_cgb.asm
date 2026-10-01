DEF BOOTROM_CGB EQU 1
INCLUDE "bootrom_common.asm"

SECTION "registers", ROM0[$00EB]
exit:
    ld E, 8
    ld L, $7C

SECTION "epilog", ROM0[$00F0]
    ld A, [0x0143] ; Cartridge compatibilty flag
    bit 7, A ; Check if CGB cartridge (0x80 or 0xC0)
    jr nz, _exit ; CGB native mode is already active
    ld A, 4 ;  DMG-mode compatibility flag
    ldh [$FF00+$4C], A
_exit:
    xor A
    ; A is the register that matters
    ; Games check a for $01 and $11, for DMG and CGB respectively
    ld A, $11
    ldh [$FF00+$50], A
