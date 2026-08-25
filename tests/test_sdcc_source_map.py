import os

from pyboy.plugins.dap_source_map import parse_sdcc_map_file


def test_parse_sdcc_source_map(tmp_path):
    source_root = tmp_path / "src"
    source_root.mkdir()
    source = source_root / "utils.c"
    source.write_text("void rand_num(void) {}\n", encoding="utf-8")

    map_file = tmp_path / "2048.gb.map"
    map_file.write_text(
        """Area                                    Addr        Size
_CODE                               00000200    00000010 =        16. bytes (REL,CON)

      Value  Global
     00000201  A$utils$68                          utils
     00000200  C$utils.c$11$0_0$142               utils
     00000202  C$utils.c$12$2_0$143               utils
     00000202  C$utils.c$13$1_0$142               utils
""",
        encoding="utf-8",
    )

    mapping = parse_sdcc_map_file(str(map_file), str(source_root))

    assert mapping[(0, 0x200)] == (os.path.normpath(str(source)), 11)
    assert mapping[(0, 0x201)] == (os.path.normpath(str(source)), 11)
    assert mapping[(0, 0x202)] == (os.path.normpath(str(source)), 12)


def test_parse_sdcc_banked_source_map(tmp_path):
    source_root = tmp_path / "src"
    source_root.mkdir()
    source = source_root / "banked.c"
    source.write_text("void banked(void) {}\n", encoding="utf-8")

    map_file = tmp_path / "game.map"
    map_file.write_text(
        """_CODE_2                           00004000    00000004 = 4. bytes (REL,CON)
     00004000  C$banked.c$4$0_0$1                   banked
""",
        encoding="utf-8",
    )

    mapping = parse_sdcc_map_file(str(map_file), str(source_root))

    assert mapping[(2, 0x4000)] == (os.path.normpath(str(source)), 4)
