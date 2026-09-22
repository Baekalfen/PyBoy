INCLUDE "bootrom_common.asm"

SECTION "epilog", ROM0[$00FC]
exit:
    ; A is already $01 after the final frame-count iteration.
    ; Preserve the DMG boot ROM's C register value used by hardware probes.
    ld C, $13
    ldh [$FF00+$50], A
