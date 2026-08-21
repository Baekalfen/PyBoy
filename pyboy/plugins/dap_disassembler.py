#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""A small disassembler for the Game Boy CPU (Sharp SM83 / "LR35902").

This is only used to render human-readable instruction text for VSCode's
Disassembly View (via the DAP `disassemble` request) -- it has no bearing
on emulation or stepping, which is handled by PyBoy itself.

The opcode tables below encode, for each opcode, a mnemonic template and
the total instruction length in bytes (including the opcode byte itself).
Operand placeholders are filled in from the bytes following the opcode:

    d8   - an 8-bit immediate value, printed as hex (e.g. `$12`)
    d16  - a 16-bit immediate value, printed as hex (e.g. `$1234`)
    a8   - an 8-bit immediate value which is an "IO" address, i.e. the
           actual address is `$FF00 + d8`, printed as `($FF12)`
    a16  - a 16-bit immediate value which is a memory address, printed as `($1234)`
    r8   - a signed 8-bit relative jump offset, resolved to an absolute address
"""

# opcode -> (mnemonic template, length in bytes)
OPCODES = {
    0x00: ("NOP", 1), 0x01: ("LD BC,d16", 3), 0x02: ("LD (BC),A", 1), 0x03: ("INC BC", 1),
    0x04: ("INC B", 1), 0x05: ("DEC B", 1), 0x06: ("LD B,d8", 2), 0x07: ("RLCA", 1),
    0x08: ("LD a16,SP", 3), 0x09: ("ADD HL,BC", 1), 0x0A: ("LD A,(BC)", 1), 0x0B: ("DEC BC", 1),
    0x0C: ("INC C", 1), 0x0D: ("DEC C", 1), 0x0E: ("LD C,d8", 2), 0x0F: ("RRCA", 1),
    0x10: ("STOP", 2), 0x11: ("LD DE,d16", 3), 0x12: ("LD (DE),A", 1), 0x13: ("INC DE", 1),
    0x14: ("INC D", 1), 0x15: ("DEC D", 1), 0x16: ("LD D,d8", 2), 0x17: ("RLA", 1),
    0x18: ("JR r8", 2), 0x19: ("ADD HL,DE", 1), 0x1A: ("LD A,(DE)", 1), 0x1B: ("DEC DE", 1),
    0x1C: ("INC E", 1), 0x1D: ("DEC E", 1), 0x1E: ("LD E,d8", 2), 0x1F: ("RRA", 1),
    0x20: ("JR NZ,r8", 2), 0x21: ("LD HL,d16", 3), 0x22: ("LD (HL+),A", 1), 0x23: ("INC HL", 1),
    0x24: ("INC H", 1), 0x25: ("DEC H", 1), 0x26: ("LD H,d8", 2), 0x27: ("DAA", 1),
    0x28: ("JR Z,r8", 2), 0x29: ("ADD HL,HL", 1), 0x2A: ("LD A,(HL+)", 1), 0x2B: ("DEC HL", 1),
    0x2C: ("INC L", 1), 0x2D: ("DEC L", 1), 0x2E: ("LD L,d8", 2), 0x2F: ("CPL", 1),
    0x30: ("JR NC,r8", 2), 0x31: ("LD SP,d16", 3), 0x32: ("LD (HL-),A", 1), 0x33: ("INC SP", 1),
    0x34: ("INC (HL)", 1), 0x35: ("DEC (HL)", 1), 0x36: ("LD (HL),d8", 2), 0x37: ("SCF", 1),
    0x38: ("JR C,r8", 2), 0x39: ("ADD HL,SP", 1), 0x3A: ("LD A,(HL-)", 1), 0x3B: ("DEC SP", 1),
    0x3C: ("INC A", 1), 0x3D: ("DEC A", 1), 0x3E: ("LD A,d8", 2), 0x3F: ("CCF", 1),
    0x40: ("LD B,B", 1), 0x41: ("LD B,C", 1), 0x42: ("LD B,D", 1), 0x43: ("LD B,E", 1),
    0x44: ("LD B,H", 1), 0x45: ("LD B,L", 1), 0x46: ("LD B,(HL)", 1), 0x47: ("LD B,A", 1),
    0x48: ("LD C,B", 1), 0x49: ("LD C,C", 1), 0x4A: ("LD C,D", 1), 0x4B: ("LD C,E", 1),
    0x4C: ("LD C,H", 1), 0x4D: ("LD C,L", 1), 0x4E: ("LD C,(HL)", 1), 0x4F: ("LD C,A", 1),
    0x50: ("LD D,B", 1), 0x51: ("LD D,C", 1), 0x52: ("LD D,D", 1), 0x53: ("LD D,E", 1),
    0x54: ("LD D,H", 1), 0x55: ("LD D,L", 1), 0x56: ("LD D,(HL)", 1), 0x57: ("LD D,A", 1),
    0x58: ("LD E,B", 1), 0x59: ("LD E,C", 1), 0x5A: ("LD E,D", 1), 0x5B: ("LD E,E", 1),
    0x5C: ("LD E,H", 1), 0x5D: ("LD E,L", 1), 0x5E: ("LD E,(HL)", 1), 0x5F: ("LD E,A", 1),
    0x60: ("LD H,B", 1), 0x61: ("LD H,C", 1), 0x62: ("LD H,D", 1), 0x63: ("LD H,E", 1),
    0x64: ("LD H,H", 1), 0x65: ("LD H,L", 1), 0x66: ("LD H,(HL)", 1), 0x67: ("LD H,A", 1),
    0x68: ("LD L,B", 1), 0x69: ("LD L,C", 1), 0x6A: ("LD L,D", 1), 0x6B: ("LD L,E", 1),
    0x6C: ("LD L,H", 1), 0x6D: ("LD L,L", 1), 0x6E: ("LD L,(HL)", 1), 0x6F: ("LD L,A", 1),
    0x70: ("LD (HL),B", 1), 0x71: ("LD (HL),C", 1), 0x72: ("LD (HL),D", 1), 0x73: ("LD (HL),E", 1),
    0x74: ("LD (HL),H", 1), 0x75: ("LD (HL),L", 1), 0x76: ("HALT", 1), 0x77: ("LD (HL),A", 1),
    0x78: ("LD A,B", 1), 0x79: ("LD A,C", 1), 0x7A: ("LD A,D", 1), 0x7B: ("LD A,E", 1),
    0x7C: ("LD A,H", 1), 0x7D: ("LD A,L", 1), 0x7E: ("LD A,(HL)", 1), 0x7F: ("LD A,A", 1),
    0x80: ("ADD A,B", 1), 0x81: ("ADD A,C", 1), 0x82: ("ADD A,D", 1), 0x83: ("ADD A,E", 1),
    0x84: ("ADD A,H", 1), 0x85: ("ADD A,L", 1), 0x86: ("ADD A,(HL)", 1), 0x87: ("ADD A,A", 1),
    0x88: ("ADC A,B", 1), 0x89: ("ADC A,C", 1), 0x8A: ("ADC A,D", 1), 0x8B: ("ADC A,E", 1),
    0x8C: ("ADC A,H", 1), 0x8D: ("ADC A,L", 1), 0x8E: ("ADC A,(HL)", 1), 0x8F: ("ADC A,A", 1),
    0x90: ("SUB B", 1), 0x91: ("SUB C", 1), 0x92: ("SUB D", 1), 0x93: ("SUB E", 1),
    0x94: ("SUB H", 1), 0x95: ("SUB L", 1), 0x96: ("SUB (HL)", 1), 0x97: ("SUB A", 1),
    0x98: ("SBC A,B", 1), 0x99: ("SBC A,C", 1), 0x9A: ("SBC A,D", 1), 0x9B: ("SBC A,E", 1),
    0x9C: ("SBC A,H", 1), 0x9D: ("SBC A,L", 1), 0x9E: ("SBC A,(HL)", 1), 0x9F: ("SBC A,A", 1),
    0xA0: ("AND B", 1), 0xA1: ("AND C", 1), 0xA2: ("AND D", 1), 0xA3: ("AND E", 1),
    0xA4: ("AND H", 1), 0xA5: ("AND L", 1), 0xA6: ("AND (HL)", 1), 0xA7: ("AND A", 1),
    0xA8: ("XOR B", 1), 0xA9: ("XOR C", 1), 0xAA: ("XOR D", 1), 0xAB: ("XOR E", 1),
    0xAC: ("XOR H", 1), 0xAD: ("XOR L", 1), 0xAE: ("XOR (HL)", 1), 0xAF: ("XOR A", 1),
    0xB0: ("OR B", 1), 0xB1: ("OR C", 1), 0xB2: ("OR D", 1), 0xB3: ("OR E", 1),
    0xB4: ("OR H", 1), 0xB5: ("OR L", 1), 0xB6: ("OR (HL)", 1), 0xB7: ("OR A", 1),
    0xB8: ("CP B", 1), 0xB9: ("CP C", 1), 0xBA: ("CP D", 1), 0xBB: ("CP E", 1),
    0xBC: ("CP H", 1), 0xBD: ("CP L", 1), 0xBE: ("CP (HL)", 1), 0xBF: ("CP A", 1),
    0xC0: ("RET NZ", 1), 0xC1: ("POP BC", 1), 0xC2: ("JP NZ,a16", 3), 0xC3: ("JP a16", 3),
    0xC4: ("CALL NZ,a16", 3), 0xC5: ("PUSH BC", 1), 0xC6: ("ADD A,d8", 2), 0xC7: ("RST $00", 1),
    0xC8: ("RET Z", 1), 0xC9: ("RET", 1), 0xCA: ("JP Z,a16", 3), 0xCB: ("PREFIX CB", 1),
    0xCC: ("CALL Z,a16", 3), 0xCD: ("CALL a16", 3), 0xCE: ("ADC A,d8", 2), 0xCF: ("RST $08", 1),
    0xD0: ("RET NC", 1), 0xD1: ("POP DE", 1), 0xD2: ("JP NC,a16", 3), 0xD3: ("DB $D3", 1),
    0xD4: ("CALL NC,a16", 3), 0xD5: ("PUSH DE", 1), 0xD6: ("SUB d8", 2), 0xD7: ("RST $10", 1),
    0xD8: ("RET C", 1), 0xD9: ("RETI", 1), 0xDA: ("JP C,a16", 3), 0xDB: ("DB $DB", 1),
    0xDC: ("CALL C,a16", 3), 0xDD: ("DB $DD", 1), 0xDE: ("SBC A,d8", 2), 0xDF: ("RST $18", 1),
    0xE0: ("LDH a8,A", 2), 0xE1: ("POP HL", 1), 0xE2: ("LD (C),A", 1), 0xE3: ("DB $E3", 1),
    0xE4: ("DB $E4", 1), 0xE5: ("PUSH HL", 1), 0xE6: ("AND d8", 2), 0xE7: ("RST $20", 1),
    0xE8: ("ADD SP,r8", 2), 0xE9: ("JP (HL)", 1), 0xEA: ("LD a16,A", 3), 0xEB: ("DB $EB", 1),
    0xEC: ("DB $EC", 1), 0xED: ("DB $ED", 1), 0xEE: ("XOR d8", 2), 0xEF: ("RST $28", 1),
    0xF0: ("LDH A,a8", 2), 0xF1: ("POP AF", 1), 0xF2: ("LD A,(C)", 1), 0xF3: ("DI", 1),
    0xF4: ("DB $F4", 1), 0xF5: ("PUSH AF", 1), 0xF6: ("OR d8", 2), 0xF7: ("RST $30", 1),
    0xF8: ("LD HL,SP+r8", 2), 0xF9: ("LD SP,HL", 1), 0xFA: ("LD A,a16", 3), 0xFB: ("EI", 1),
    0xFC: ("DB $FC", 1), 0xFD: ("DB $FD", 1), 0xFE: ("CP d8", 2), 0xFF: ("RST $38", 1),
}  # yapf: disable

_CB_REGS = ["B", "C", "D", "E", "H", "L", "(HL)", "A"]
_CB_OPS = [
    "RLC", "RRC", "RL", "RR", "SLA", "SRA", "SWAP", "SRL", "BIT 0,", "BIT 1,", "BIT 2,", "BIT 3,", "BIT 4,",
    "BIT 5,", "BIT 6,", "BIT 7,", "RES 0,", "RES 1,", "RES 2,", "RES 3,", "RES 4,", "RES 5,", "RES 6,", "RES 7,",
    "SET 0,", "SET 1,", "SET 2,", "SET 3,", "SET 4,", "SET 5,", "SET 6,", "SET 7,"
]  # yapf: disable


def _cb_mnemonic(opcode):
    reg = _CB_REGS[opcode & 0x07]
    op = _CB_OPS[(opcode >> 3) & 0x1F]
    return f"{op}{reg}"


def instruction_length(opcode):
    """Returns the length in bytes of the instruction starting with `opcode` (1, 2, or 3).
    For the 0xCB prefix, this returns 2 (prefix byte + operand byte), matching the CB-prefixed
    instructions, which are always exactly 2 bytes total."""
    if opcode == 0xCB:
        return 2
    return OPCODES.get(opcode, ("DB", 1))[1]


def disassemble_one(read_byte, addr):
    """Disassembles a single instruction starting at `addr`.

    Args:
        read_byte (func): A function `read_byte(address) -> int` used to read program bytes.
        addr (int): The address (in the 16-bit Game Boy address space) to disassemble from.

    Returns:
        (length, text, target): `length` is the number of bytes making up the instruction
        (>= 1), `text` is a human readable representation, e.g. `"LD A,d8"` becomes
        `"LD A,$42"`, and `target` is the absolute 16-bit address referenced by the
        instruction's `a8`/`a16`/`r8` operand (e.g. a `CALL`/`JP` destination, a `JR` branch
        target, or an `LDH`/`LD` memory operand), or `None` if the instruction has no such
        address operand (e.g. it only uses an immediate `d8`/`d16` value). Callers can use
        `target` to look up and substitute in a symbol label for the referenced address.
    """
    opcode = read_byte(addr) & 0xFF

    if opcode == 0xCB:
        sub_opcode = read_byte((addr + 1) & 0xFFFF) & 0xFF
        return 2, _cb_mnemonic(sub_opcode), None

    template, length = OPCODES.get(opcode, ("DB ${:02X}".format(opcode), 1))
    target = None

    if "d8" in template or "a8" in template:
        d8 = read_byte((addr + 1) & 0xFFFF) & 0xFF
        if "a8" in template:
            target = 0xFF00 + d8
            text = template.replace("a8", "(${:04X})".format(target))
        else:
            text = template.replace("d8", "${:02X}".format(d8))
    elif "r8" in template:
        raw = read_byte((addr + 1) & 0xFFFF) & 0xFF
        signed = raw - 256 if raw >= 128 else raw
        target = (addr + length + signed) & 0xFFFF
        text = template.replace("r8", "${:04X}".format(target))
    elif "d16" in template or "a16" in template:
        lo = read_byte((addr + 1) & 0xFFFF) & 0xFF
        hi = read_byte((addr + 2) & 0xFFFF) & 0xFF
        value = (hi << 8) | lo
        if "a16" in template:
            target = value
            # JP/CALL jump directly to `a16` -- it isn't a memory dereference, so (unlike LD's
            # memory operands) it shouldn't be parenthesized.
            if template.startswith("JP") or template.startswith("CALL"):
                text = template.replace("a16", "${:04X}".format(value))
            else:
                text = template.replace("a16", "(${:04X})".format(value))
        else:
            text = template.replace("d16", "${:04X}".format(value))
    else:
        text = template

    return length, text, target
