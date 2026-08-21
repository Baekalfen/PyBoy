from pyboy.plugins import dap_disassembler as disassembler


def _mem(data, base=0):
    def read(addr):
        idx = addr - base
        if 0 <= idx < len(data):
            return data[idx]
        return 0

    return read


def test_simple_instructions():
    # NOP; INC B; LD A,d8 $42
    data = [0x00, 0x04, 0x3E, 0x42]
    read = _mem(data)
    length, text, target = disassembler.disassemble_one(read, 0)
    assert (length, text, target) == (1, "NOP", None)
    length, text, target = disassembler.disassemble_one(read, 1)
    assert (length, text, target) == (1, "INC B", None)
    length, text, target = disassembler.disassemble_one(read, 2)
    assert (length, text, target) == (2, "LD A,$42", None)


def test_jp_a16():
    data = [0xC3, 0x50, 0x01]  # JP $0150
    read = _mem(data)
    length, text, target = disassembler.disassemble_one(read, 0)
    # No parens: JP jumps directly to the address, it isn't a memory dereference (unlike LD's
    # memory operands, e.g. "LD (a16),A").
    assert (length, text, target) == (3, "JP $0150", 0x0150)


def test_jr_relative_forward():
    # JR $02 (jump 2 bytes forward, past the 2-byte instruction itself)
    data = [0x18, 0x02]
    read = _mem(data, base=0x100)
    length, text, target = disassembler.disassemble_one(read, 0x100)
    assert length == 2
    assert text == "JR $0104"
    assert target == 0x0104


def test_jr_relative_backward():
    # JR $FE (jump -2, i.e. back to itself - a classic infinite loop)
    data = [0x18, 0xFE]
    read = _mem(data, base=0x100)
    length, text, target = disassembler.disassemble_one(read, 0x100)
    assert length == 2
    assert text == "JR $0100"
    assert target == 0x0100


def test_cb_prefixed():
    # CB 7C -> BIT 7,H
    data = [0xCB, 0x7C]
    read = _mem(data)
    length, text, target = disassembler.disassemble_one(read, 0)
    assert (length, text, target) == (2, "BIT 7,H", None)


def test_ldh_a8():
    # LDH A,(a8) -- LDH A,($FF44) i.e. reading the LY register
    data = [0xF0, 0x44]
    read = _mem(data)
    length, text, target = disassembler.disassemble_one(read, 0)
    assert (length, text, target) == (2, "LDH A,($FF44)", 0xFF44)


def test_undefined_opcode():
    data = [0xD3]
    read = _mem(data)
    length, text, target = disassembler.disassemble_one(read, 0)
    assert length == 1
    assert "D3" in text
    assert target is None


def test_instruction_length_matches_disassemble():
    for opcode in range(0x100):
        data = [opcode, 0, 0]
        read = _mem(data)
        length, _text, _target = disassembler.disassemble_one(read, 0)
        assert length == disassembler.instruction_length(opcode)
