import pytest
from types import SimpleNamespace

import numpy as np

from pyboy import PyBoy
from pyboy.api.torch_renderer import MPS_INPUT_SLOT_COUNT, TorchFrameRenderer
from pyboy.plugins.window_metal import WindowMetal
from pyboy.plugins.window_sdl2 import WindowSDL2
import pyboy.api.torch_renderer as torch_renderer_module
import pyboy.plugins.window_sdl2 as window_sdl2

torch = pytest.importorskip("torch")


ACCELERATOR_DEVICES = [
    pytest.param("mps", marks=pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")),
    pytest.param("cuda", marks=pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")),
]


def _new_state(cgb=False):
    return {
        "vram0": bytes(8192),
        "vram1": bytes(8192),
        "oam": bytes(160),
        "scanlines": [[0, 0, 7, 0, 0] for _ in range(144)],
        "cgb": cgb,
        "lcdc": 0x91,
        "background_map_offset": 0x1800,
        "window_map_offset": 0x1800,
        "background_palette_register": 0xE4,
        "object_palette_registers": (0xE4, 0xE4),
        "dmg_palettes": (
            (0x112233, 0xAABBCC, 0x445566, 0x778899),
            (0x010101, 0x020202, 0x030303, 0x040404),
            (0x111111, 0x222222, 0x333333, 0x010203),
        ),
        "background_color_palette": tuple([0] * 32),
        "object_color_palette": tuple([0] * 32),
    }


def _solid_tile(vram, tile, color, bank=0):
    offset = tile * 16
    low = 0xFF if color & 1 else 0
    high = 0xFF if color & 2 else 0
    for row in range(8):
        vram[bank][offset + row * 2] = low
        vram[bank][offset + row * 2 + 1] = high


def _frame_state(state, vram0, vram1, oam):
    state["vram0"] = bytes(vram0)
    state["vram1"] = bytes(vram1)
    state["oam"] = bytes(oam)
    return state


def _sprite_priority_state(cgb=False, background_color=1, map_priority=False, sprite_attributes=0x80):
    state = _new_state(cgb=cgb)
    state["lcdc"] = 0x93
    if cgb:
        background_palette = [0] * 32
        background_palette[1] = 0x03E0
        object_palette = [0] * 32
        object_palette[2] = 0x7C00
        state["background_color_palette"] = tuple(background_palette)
        state["object_color_palette"] = tuple(object_palette)

    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, background_color)
    _solid_tile((vram0, vram1), 1, 2)
    if cgb and map_priority:
        vram1[0x1800] = 0x80
    oam[:4] = bytes((16, 8, 1, sprite_attributes))
    return _frame_state(state, vram0, vram1, oam)


def _host_sync_renderer():
    # Exercises the incremental host-to-device memory synchronization without
    # requiring a physical accelerator.
    renderer = object.__new__(TorchFrameRenderer)
    renderer._torch = torch
    renderer.device = torch.device("cpu")
    renderer._vram0 = torch.empty(8192, dtype=torch.uint8)
    renderer._vram1 = torch.empty(8192, dtype=torch.uint8)
    renderer._oam = torch.empty(160, dtype=torch.uint8)
    renderer._vram0_snapshot = np.empty(8192, dtype=np.uint8)
    renderer._vram1_snapshot = np.empty(8192, dtype=np.uint8)
    renderer._oam_snapshot = np.empty(160, dtype=np.uint8)
    renderer._buffer_versions = [None, None, None]
    renderer._memory_initialized = False
    return renderer


def test_torch_renderer_rejects_unsupported_devices():
    with pytest.raises(RuntimeError, match='requires an "mps" or "cuda" device'):
        TorchFrameRenderer("cpu")


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_decodes_tiles_and_converts_dmg_palette_on_device(device):
    state = _new_state()
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 1)
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame.dtype == torch.uint8
    assert tuple(frame.shape) == (144, 160, 4)
    assert frame[0, 0].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_accepts_packed_scanline_state(device):
    state = _new_state()
    state["scanlines"] = bytes(value for line in state["scanlines"] for value in line)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0x11, 0x22, 0x33, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_blanks_lcd_off_and_empty_dmg_layers_without_rendering(device, monkeypatch):
    state = _new_state()
    state["background_palette_register"] = 0xE5
    renderer = TorchFrameRenderer(device)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("disabled layers must not synchronize or render")

    monkeypatch.setattr(renderer, "_sync_memory", fail_if_called)
    monkeypatch.setattr(renderer, "_sync_palettes", fail_if_called)

    expected = [0xAA, 0xBB, 0xCC, 0xFF]
    for lcdc in (0x80, 0x7F):
        state["lcdc"] = lcdc
        frame = renderer.render(state).cpu()
        assert frame[0, 0].tolist() == expected
        assert torch.all(frame == torch.tensor(expected, dtype=torch.uint8))


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_blanks_lcd_off_without_scanline_or_memory_state(device):
    palette_state = _new_state()
    state = {
        "lcdc": 0,
        "background_palette_register": 0xE5,
        "dmg_palettes": palette_state["dmg_palettes"],
    }

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]
    assert torch.all(frame == torch.tensor([0xAA, 0xBB, 0xCC, 0xFF], dtype=torch.uint8))


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_skips_disabled_dmg_background_but_draws_window(device):
    state = _new_state()
    state["lcdc"] = 0xB0
    state["scanlines"] = [[0, 0, 17, 0, 1] for _ in range(144)]
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 1)
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 9].tolist() == [0x11, 0x22, 0x33, 0xFF]
    assert frame[0, 10].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_skips_disabled_window_and_sprite_paths(device):
    state = _new_state()

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0x11, 0x22, 0x33, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_keeps_cgb_background_when_priority_bit_is_clear(device):
    state = _new_state(cgb=True)
    state["lcdc"] = 0x90
    background_palette = [0] * 32
    background_palette[2] = 0x001F
    state["background_color_palette"] = tuple(background_palette)
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 2)
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0xF8, 0, 0, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_uses_captured_scroll_values_with_wraparound(device):
    state = _new_state()
    state["scanlines"][0] = [0, 255, 7, 0, 0]
    state["scanlines"][1] = [255, 0, 7, 0, 0]
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 1, 1)
    _solid_tile((vram0, vram1), 2, 2)
    _solid_tile((vram0, vram1), 3, 3)
    vram0[0x1800] = 1
    vram0[0x1800 + 31] = 2
    vram0[0x1800 + 31 * 32] = 3
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0x77, 0x88, 0x99, 0xFF]
    assert frame[1, 0].tolist() == [0x44, 0x55, 0x66, 0xFF]
    assert frame[1, 1].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (_sprite_priority_state(), [0xAA, 0xBB, 0xCC, 0xFF]),
        (_sprite_priority_state(background_color=0), [3, 3, 3, 0xFF]),
        (_sprite_priority_state(sprite_attributes=0), [3, 3, 3, 0xFF]),
        (_sprite_priority_state(cgb=True, map_priority=True, sprite_attributes=0), [0, 0xF8, 0, 0xFF]),
        (_sprite_priority_state(cgb=True, background_color=0, map_priority=True), [0, 0, 0xF8, 0xFF]),
        (_sprite_priority_state(cgb=True), [0, 0xF8, 0, 0xFF]),
        (_sprite_priority_state(cgb=True, map_priority=True, sprite_attributes=0), [0, 0xF8, 0, 0xFF]),
    ],
)
def test_torch_renderer_obeys_dmg_and_cgb_background_sprite_priority(state, expected, device):
    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == expected


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_obeys_cgb_master_priority_disable(device):
    state = _sprite_priority_state(cgb=True, map_priority=True)
    state["lcdc"] &= ~0x01

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0, 0, 0xF8, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_clears_populated_sprites_when_obj_layer_is_disabled(device):
    state = _sprite_priority_state(sprite_attributes=0)
    renderer = TorchFrameRenderer(device)

    enabled_pixel = renderer.render(state)[0, 0].cpu().tolist()
    state["lcdc"] &= ~0x02
    disabled_pixel = renderer.render(state)[0, 0].cpu().tolist()

    assert enabled_pixel == [3, 3, 3, 0xFF]
    assert disabled_pixel == [0xAA, 0xBB, 0xCC, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_sprite_priority_applies_over_window_pixels(device):
    state = _sprite_priority_state(background_color=0)
    state["lcdc"] = 0xB3
    state["window_map_offset"] = 0x1C00
    state["scanlines"] = [[0, 0, 7, 0, 1] for _ in range(144)]
    vram0 = bytearray(state["vram0"])
    vram1 = bytearray(state["vram1"])
    oam = bytearray(state["oam"])
    _solid_tile((vram0, vram1), 0, 1)
    vram0[0x1C00] = 0
    state = _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_uses_next_visible_sprite_when_highest_is_behind_background(device):
    state = _sprite_priority_state()
    vram0 = bytearray(state["vram0"])
    vram1 = bytearray(state["vram1"])
    oam = bytearray(state["oam"])
    _solid_tile((vram0, vram1), 2, 3)
    oam[4:8] = bytes((16, 8, 2, 0))
    state = _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [4, 4, 4, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_flips_8x16_sprites_across_both_tiles(device):
    state = _new_state()
    state["lcdc"] = 0x97
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 4, 1)
    _solid_tile((vram0, vram1), 5, 2)
    oam[:4] = bytes((17, 9, 5, 0x70))
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[1, 1].tolist() == [0x33, 0x33, 0x33, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_uses_cgb_tile_bank_and_raw_color_palette(device):
    state = _new_state(cgb=True)
    state["lcdc"] = 0x93
    background_palette = [0] * 32
    background_palette[6] = 0x7C00
    object_palette = [0] * 32
    object_palette[13] = 0x001F
    state["background_color_palette"] = tuple(background_palette)
    state["object_color_palette"] = tuple(object_palette)
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 2, bank=1)
    _solid_tile((vram0, vram1), 1, 1, bank=1)
    vram1[0x1800] = 0x09
    oam[:4] = bytes((17, 9, 1, 0x0B))
    _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0, 0, 0xF8, 0xFF]
    assert frame[1, 1].tolist() == [0xF8, 0, 0, 0xFF]


def test_torch_renderer_sparsely_syncs_vram_and_oam():
    state = _new_state()
    state["lcdc"] = 0x93
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 1)
    renderer = _host_sync_renderer()

    renderer._sync_memory(_frame_state(state, vram0, vram1, oam))
    assert renderer._vram0[0].item() == 0xFF
    assert renderer._vram0[1].item() == 0x00

    _solid_tile((vram0, vram1), 0, 2)
    _solid_tile((vram0, vram1), 1, 3)
    oam[:4] = bytes((17, 9, 1, 0x10))
    renderer._sync_memory(_frame_state(state, vram0, vram1, oam))

    assert renderer._vram0[0].item() == 0x00
    assert renderer._vram0[1].item() == 0xFF
    assert renderer._oam[:4].tolist() == [17, 9, 1, 0x10]


def test_torch_renderer_skips_unchanged_memory_scans_with_versions(monkeypatch):
    state = _new_state()
    state.update(vram0_generation=0, vram1_generation=0, oam_generation=0)
    renderer = _host_sync_renderer()
    renderer._sync_memory(state)

    flatnonzero = np.flatnonzero
    scanned_sizes = []

    def track_scan(values):
        scanned_sizes.append(values.size)
        return flatnonzero(values)

    monkeypatch.setattr(np, "flatnonzero", track_scan)
    renderer._sync_memory(state)
    assert scanned_sizes == []

    state["vram0"] = bytes([0x5A]) + state["vram0"][1:]
    state["vram0_generation"] += 1
    renderer._sync_memory(state)

    assert scanned_sizes == [8192]
    assert renderer._vram0[0].item() == 0x5A


def test_torch_renderer_validates_buffer_size_before_skipping_version():
    state = _new_state()
    state.update(vram0_generation=0, vram1_generation=0, oam_generation=0)
    renderer = _host_sync_renderer()
    renderer._sync_memory(state)

    invalid_state = dict(state, vram0=b"invalid")
    with pytest.raises(ValueError, match="Expected 8192 bytes to synchronize"):
        renderer._sync_memory(invalid_state)


def test_torch_renderer_skips_unchanged_mps_slot_copies(monkeypatch):
    renderer = object.__new__(TorchFrameRenderer)
    renderer.device = SimpleNamespace(type="mps")
    renderer._memory_slot_versions = [[None, None, None]]
    state = _new_state()
    state.update(vram0_generation=0, vram1_generation=0, oam_generation=0)
    slot = np.empty(8192 * 2 + 160, dtype=np.uint8)

    copyto = np.copyto
    copies = []

    def track_copy(target, source):
        copies.append(source.size)
        copyto(target, source)

    monkeypatch.setattr(np, "copyto", track_copy)
    renderer._sync_memory(state, slot, slot=0)
    renderer._sync_memory(state, slot, slot=0)
    assert copies == [8192, 8192, 160]

    state["oam"] = bytes([0xA5]) + state["oam"][1:]
    state["oam_generation"] += 1
    renderer._sync_memory(state, slot, slot=0)
    assert copies == [8192, 8192, 160, 160]
    assert slot[-160] == 0xA5


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_fast_renderer_reuses_memory_snapshots_until_a_write(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    original_render = TorchFrameRenderer.render
    states = []

    def record_render(renderer, state):
        states.append(state)
        return original_render(renderer, state)

    monkeypatch.setattr(TorchFrameRenderer, "render", record_render)
    try:
        pyboy.memory[0xFF40] = 0x91
        pyboy.screen.gpu_tensor("mps")
        first = states[-1]
        pyboy.screen.gpu_tensor("mps")
        unchanged = states[-1]
        assert unchanged["vram0"] is first["vram0"]
        assert unchanged["oam"] is first["oam"]

        pyboy.memory[0x8000] = first["vram0"][0]
        pyboy.memory[0xFE00] = first["oam"][0]
        pyboy.screen.gpu_tensor("mps")
        same_values = states[-1]
        assert same_values["vram0_generation"] == first["vram0_generation"]
        assert same_values["oam_generation"] == first["oam_generation"]

        pyboy.memory[0xFF40] = 0
        pyboy.memory[0x8000] = first["vram0"][0] ^ 0xFF
        pyboy.memory[0xFE00] = 0x31
        pyboy.memory[0xFF40] = 0x91
        pyboy.screen.gpu_tensor("mps")
        changed = states[-1]

        assert changed["vram0_generation"] == first["vram0_generation"] + 1
        assert changed["oam_generation"] == first["oam_generation"] + 1
        assert changed["vram0"] is not first["vram0"]
        assert changed["oam"] is not first["oam"]
        assert changed["vram0"][0] == first["vram0"][0] ^ 0xFF
        assert changed["oam"][0] == 0x31
    finally:
        pyboy.stop(save=False)


def test_torch_renderer_packs_dense_scanlines_without_unused_wy():
    state = _new_state()
    scanlines = np.asarray(state["scanlines"], dtype=np.uint8)
    scanlines[72:, 0] = 4
    scanlines[:, 3] = np.arange(144, dtype=np.uint8)
    renderer = object.__new__(TorchFrameRenderer)

    packed = renderer._pack_metal_scanlines(state, scanlines)

    assert packed.shape == (144, 5)
    assert packed[0].tolist() == [0, 0, 7, 0, 0xFF]
    assert packed[72].tolist() == [4, 0, 7, 0, 0xFF]


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_torch_renderer_runs_window_and_sprite_composition_on_mps():
    state = _new_state()
    state["lcdc"] = 0xF3
    state["window_map_offset"] = 0x1C00
    state["scanlines"] = [[0, 0, 9, 0, int(y > 0)] for y in range(144)]
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 1)
    _solid_tile((vram0, vram1), 1, 2)
    _solid_tile((vram0, vram1), 2, 3)
    vram0[0x1C00] = 1
    vram0[0x1C01] = 1
    oam[:4] = bytes((17, 9, 2, 0x10))
    state = _frame_state(state, vram0, vram1, oam)

    renderer = TorchFrameRenderer("mps")
    frame = renderer.render(state)

    assert frame.device.type == "mps"
    assert frame.cpu()[1, 1].tolist() == [0x01, 0x02, 0x03, 0xFF]
    assert frame.cpu()[1, 10].tolist() == [0x44, 0x55, 0x66, 0xFF]

    _solid_tile((vram0, vram1), 0, 2)
    oam[1] = 10
    updated = renderer.render(_frame_state(state, vram0, vram1, oam))

    assert updated is frame
    assert updated.cpu()[0, 0].tolist() == [0x44, 0x55, 0x66, 0xFF]
    assert updated.cpu()[1, 2].tolist() == [0x01, 0x02, 0x03, 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_renders_dense_two_scanline_state(device):
    state = _new_state()
    state["lcdc"] = 0x93
    state["scanlines"] = [[0, 0, 7, 0, 0] for _ in range(144)]
    for line in range(72, 144):
        state["scanlines"][line][0] = 4

    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    _solid_tile((vram0, vram1), 0, 1)
    _solid_tile((vram0, vram1), 1, 2)
    vram0[0x1800] = 0
    vram0[0x1801] = 1
    vram0[0x1800 + 9 * 32] = 0
    vram0[0x1800 + 9 * 32 + 1] = 1
    state = _frame_state(state, vram0, vram1, oam)

    frame = TorchFrameRenderer(device).render(state).cpu()

    assert frame[0, 0].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]
    assert frame[0, 8].tolist() == [0x44, 0x55, 0x66, 0xFF]
    assert frame[72, 0].tolist() == [0xAA, 0xBB, 0xCC, 0xFF]
    assert frame[72, 4].tolist() == [0x44, 0x55, 0x66, 0xFF]


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_torch_renderer_mps_reuses_pinned_input_slots_safely(monkeypatch):
    state = _new_state()
    vram0 = bytearray(8192)
    vram1 = bytearray(8192)
    oam = bytearray(160)
    renderer = TorchFrameRenderer("mps")
    synchronize = torch.mps.synchronize
    synchronizations = []

    assert len(renderer._memory_slot_tensors) == MPS_INPUT_SLOT_COUNT

    def track_synchronize():
        synchronizations.append(None)
        synchronize()

    monkeypatch.setattr(torch.mps, "synchronize", track_synchronize)

    for frame_index in range(MPS_INPUT_SLOT_COUNT + 1):
        color = frame_index % 3 + 1
        _solid_tile((vram0, vram1), 0, color)
        frame = renderer.render(_frame_state(state, vram0, vram1, oam))

    assert len(synchronizations) == 1
    expected_colors = ([0xAA, 0xBB, 0xCC], [0x44, 0x55, 0x66], [0x77, 0x88, 0x99])
    assert frame.cpu()[0, 0].tolist() == [*expected_colors[MPS_INPUT_SLOT_COUNT % 3], 0xFF]


@pytest.mark.parametrize("device", ACCELERATOR_DEVICES)
def test_torch_renderer_rejects_invalid_scanline_shape(device):
    state = _new_state()
    state["scanlines"] = [[0, 0, 0, 0]]

    with pytest.raises(ValueError, match="Expected 144 scanline parameter rows of five values"):
        TorchFrameRenderer(device).render(state)


@pytest.mark.parametrize("device", ["mps", "cuda"])
def test_screen_gpu_tensor_blanks_disabled_lcd_instead_of_returning_stale_frame(default_rom, monkeypatch, device):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        renderers = []

        class CachedCudaRenderer:
            def __init__(self, requested_device):
                self.device_spec = str(requested_device)
                self.device = SimpleNamespace(type=requested_device)
                self.state = None
                renderers.append(self)

            def render(self, state):
                self.state = state
                return "blank-frame"

            def get_frame(self):
                return "stale-frame"

        monkeypatch.setattr(torch_renderer_module, "TorchFrameRenderer", CachedCudaRenderer)
        pyboy.memory[0xFF40] = 0x91

        expected_cached_frame = "stale-frame" if device == "cuda" else "blank-frame"
        assert pyboy.screen.gpu_tensor(device) == expected_cached_frame
        pyboy.memory[0xFF40] = 0

        assert pyboy.screen.gpu_tensor(device) == "blank-frame"
        assert renderers[0].state["lcdc"] & 0x80 == 0
        assert set(renderers[0].state) == {"lcdc", "background_palette_register", "dmg_palettes"}
    finally:
        pyboy.stop(save=False)


def test_screen_gpu_tensor_requires_fast_mode(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    try:
        with pytest.raises(RuntimeError, match="requires PyBoy fast mode"):
            pyboy.screen.gpu_tensor("cpu")
    finally:
        pyboy.stop(save=False)


def test_metal_window_is_an_sdl2_subclass():
    assert issubclass(WindowMetal, WindowSDL2)


def test_sdl2_setup_creates_window_only_in_video_initializer(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", sound_emulated=False)
    created = []
    try:
        sdl = window_sdl2.sdl2
        monkeypatch.setattr(sdl, "SDL_InitSubSystem", lambda flags: 0)
        monkeypatch.setattr(sdl, "SDL_SetHint", lambda *args: 0)
        monkeypatch.setattr(sdl, "SDL_CreateWindow", lambda *args: created.append(args))

        def initialize_video(width, height, render_width, render_height):
            sdl.SDL_CreateWindow(
                b"PyBoy",
                sdl.SDL_WINDOWPOS_CENTERED,
                sdl.SDL_WINDOWPOS_CENTERED,
                width,
                height,
                sdl.SDL_WINDOW_RESIZABLE,
            )

        pyboy._plugin_manager.window_sdl2._initialize_video_audio(initialize_video)

        assert len(created) == 1
    finally:
        pyboy.stop(save=False)


def test_metal_window_requires_fast_mode(default_rom):
    with pytest.raises(RuntimeError, match="requires fast_mode=True"):
        PyBoy(default_rom, window="Metal")


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_torch_renderer_passes_mps_frame_to_metal_presenter():
    calls = []
    renderer = TorchFrameRenderer("mps")
    renderer._metal_renderer = SimpleNamespace(present=lambda frame, layer: calls.append((frame, layer)))
    frame = renderer.get_frame()

    renderer.present_metal(frame, 1234)

    assert calls == [(frame, 1234)]


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_screen_gpu_tensor_returns_pytorch_frame(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(3, render=True, sound=False)

        first_frame = pyboy.screen.gpu_tensor("mps")
        second_frame = pyboy.screen.gpu_tensor("mps")

        assert first_frame is second_frame
        assert first_frame.dtype == torch.uint8
        assert tuple(first_frame.shape) == (144, 160, 4)
        assert np.any(first_frame.cpu().numpy())
    finally:
        pyboy.stop(save=False)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_screen_gpu_tensor_matches_regular_renderer(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        for _ in range(30):
            pyboy.tick(1, render=True, sound=False)

        expected = pyboy.screen.ndarray.copy()
        frame = pyboy.screen.gpu_tensor("mps").cpu().numpy()

        np.testing.assert_array_equal(frame, expected)
    finally:
        pyboy.stop(save=False)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_screen_gpu_tensor_dispatches_at_vblank(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.memory[0xFF40] = 0x91
        pyboy.tick(1, render=True, sound=False)
        pyboy.screen.gpu_tensor("mps")

        original_render = TorchFrameRenderer.render
        calls = []

        def record_render(renderer, state):
            calls.append(state)
            return original_render(renderer, state)

        monkeypatch.setattr(TorchFrameRenderer, "render", record_render)
        pyboy.tick(1, render=True, sound=False)
        pyboy.screen.gpu_tensor("mps")

        assert len(calls) == 1
        assert len(calls[0]["scanlines"]) == 144 * 5
    finally:
        pyboy.stop(save=False)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_screen_gpu_tensor_surfaces_vblank_dispatch_error(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(1, render=True, sound=False)
        pyboy.screen.gpu_tensor("mps")

        def fail_render(renderer, state):
            raise RuntimeError("GPU dispatch failed")

        monkeypatch.setattr(TorchFrameRenderer, "render", fail_render)
        pyboy.tick(1, render=True, sound=False)

        with pytest.raises(RuntimeError, match="GPU dispatch failed"):
            pyboy.screen.gpu_tensor("mps")
    finally:
        pyboy.stop(save=False)


def test_torch_renderer_prefetches_accelerator_memory_non_blocking():
    renderer = object.__new__(TorchFrameRenderer)
    renderer.device = SimpleNamespace(type="cuda")
    renderer._buffer_versions = [0, 0, 0]
    calls = []
    renderer._sync_memory = lambda state, memory=None, non_blocking=False, memory_host=None: calls.append(
        ("memory", non_blocking)
    )
    renderer._cuda_renderer = SimpleNamespace(
        reserve_memory_slot=lambda: 0,
        _memory_host=[[object(), object(), object()]],
    )
    state = _new_state()

    renderer.prefetch_memory(state)

    assert calls == [("memory", True)]
    assert not renderer.needs_memory_prefetch((0, 0, 0))
    assert renderer.needs_memory_prefetch((0, 1, 0))


def test_torch_cuda_renderer_skips_memory_sync_after_prefetch():
    renderer = object.__new__(TorchFrameRenderer)
    renderer.device = SimpleNamespace(type="cuda")
    renderer._memory_initialized = True
    renderer._buffer_versions = [0, 0, 0]
    renderer._frame = renderer._vram0 = renderer._vram1 = renderer._oam = object()
    renderer._dmg_palette_rgba = object()
    memory_syncs = []
    renderer._sync_memory = lambda state, non_blocking=False: memory_syncs.append(state)
    renderer._sync_palettes = lambda state: None
    renderer._cuda_renderer = SimpleNamespace(render=lambda *args: args[0])
    state = _new_state()
    state.update(vram0_generation=0, vram1_generation=0, oam_generation=0)

    renderer.render(state)
    assert memory_syncs == []

    state["oam_generation"] += 1
    renderer.render(state)
    assert memory_syncs == [state]


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_tick_prefetches_cuda_memory_before_rendered_frame(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    calls = []
    late_write_values = []
    frame_renderers = []
    try:
        pyboy.set_emulation_speed(0)
        for _ in range(10):
            if pyboy.memory[0xFF40] & 0x80:
                break
            pyboy.tick(1, render=True, sound=False)
        assert pyboy.memory[0xFF40] & 0x80
        pyboy.screen.gpu_tensor("cuda")
        pyboy.memory[0x8000] ^= 0xFF
        original_prefetch = TorchFrameRenderer.prefetch_memory
        original_render = TorchFrameRenderer.render

        def record_prefetch(renderer, state):
            calls.append(("prefetch", state))
            result = original_prefetch(renderer, state)
            if not late_write_values:
                value = pyboy.memory[0x8000] ^ 0xFF
                pyboy.memory[0x8000] = value
                late_write_values.append(value)
            return result

        def record_render(renderer, state):
            calls.append(("render", state))
            frame_renderers.append(renderer)
            return original_render(renderer, state)

        monkeypatch.setattr(TorchFrameRenderer, "prefetch_memory", record_prefetch)
        monkeypatch.setattr(TorchFrameRenderer, "render", record_render)

        for _ in range(3):
            pyboy.tick(1, render=True, sound=False)
            if any(name == "render" for name, _ in calls):
                break
            pyboy.screen.gpu_tensor("cuda")
        frame = pyboy.screen.gpu_tensor("cuda")
        torch.cuda.synchronize()

        render_index = next(index for index, (name, _) in enumerate(calls) if name == "render")
        assert render_index > 0
        assert all(name == "prefetch" for name, _ in calls[:render_index])
        assert "vram0_generation" in calls[0][1]
        assert calls[render_index][1]["vram0_generation"] > calls[0][1]["vram0_generation"]
        assert isinstance(calls[render_index][1]["scanlines"], bytes)
        assert len(calls[render_index][1]["scanlines"]) == 144 * 5
        assert frame_renderers[0]._vram0[0].item() == late_write_values[0]
        assert frame.device.type == "cuda"
    finally:
        pyboy.stop(save=False)


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="MPS is unavailable")
def test_screen_gpu_tensor_skips_cpu_rendering_on_later_frames(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(3, render=True, sound=False)
        pyboy.screen.gpu_tensor("mps")
        cpu_frame = pyboy.screen.ndarray.copy()

        pyboy.tick(1, render=True, sound=False)
        updated_frame = pyboy.screen.gpu_tensor("mps")

        np.testing.assert_array_equal(pyboy.screen.ndarray, cpu_frame)
        assert updated_frame.device.type == "mps"
    finally:
        pyboy.stop(save=False)
