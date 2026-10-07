INCLUDE "bootrom_common.asm"

SECTION "epilog", ROM0[$00F8]
exit:
    ld B, C ; C is 0 here. Restore B clobbered by the line-sync wait
    ; Keep the HL hand-off value of the previous boot ROM, which the
    ; mooneye boot register tests record (wave table address + index 0).
    ld HL, $0087
    ; A is already $01 after the final frame-count iteration.
    ; Preserve the DMG boot ROM's C register value used by hardware probes.
    ld C, $13
    ldh [$FF00+$50], A
