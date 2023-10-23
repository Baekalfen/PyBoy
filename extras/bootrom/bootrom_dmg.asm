INCLUDE "bootrom_common.asm"

SECTION "epilog", ROM0[$00FC]
exit:
    ; A is the register that matters
    ; Games check a for $01 and $11, for DMG and CGB respectively
    ld A, $01
    ldh [$FF00+$50], A

