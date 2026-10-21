#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
import triton
import triton.language as tl


@triton.jit
def _prepare_window_lines(scanlines, render_state, oam, window_lines, BLOCK: tl.constexpr):
    y = tl.arange(0, BLOCK)
    window_x = tl.load(scanlines + y * 5 + 2, mask=y < 144, other=0xFF).to(tl.int32)
    window_active = tl.load(scanlines + y * 5 + 4, mask=y < 144, other=0).to(tl.int32) != 0
    lcdc = tl.load(render_state).to(tl.int32)
    visible_window = window_active & (window_x < 167) & ((lcdc & 0x20) != 0) & (y < 144)
    window_line = tl.cumsum(visible_window.to(tl.int32), axis=0) - 1
    tl.store(window_lines + y, window_line, mask=y < 144)

    has_enabled_sprite_lines = (lcdc & 0x02) != 0
    sprite_y = tl.load(oam + y * 4, mask=y < 40, other=0).to(tl.int32) - 16
    sprite_x = tl.load(oam + y * 4 + 1, mask=y < 40, other=0).to(tl.int32) - 8
    sprite_height = tl.where((lcdc & 4) != 0, 16, 8)
    visible_sprite = (
        (y < 40)
        & has_enabled_sprite_lines
        & (sprite_y < 144)
        & (sprite_y + sprite_height > 0)
        & (sprite_x < 160)
        & (sprite_x + 8 > 0)
    )
    tl.store(window_lines + 144, tl.sum(visible_sprite.to(tl.int32), axis=0))


@triton.jit
def _sample_tile(vram0, vram1, x, y, map_offset, unsigned_tiledata, cgb: tl.constexpr, mask):
    map_address = map_offset + (y >> 3) * 32 + (x >> 3)
    tile = tl.load(vram0 + map_address, mask=mask, other=0).to(tl.int32)
    if cgb:
        attributes = tl.load(vram1 + map_address, mask=mask, other=0).to(tl.int32)
        palette = attributes & 7
        priority = (attributes & 0x80) != 0
        bank = (attributes >> 3) & 1
        pixel_x = tl.where((attributes & 0x20) != 0, 7 - (x & 7), x & 7)
        pixel_y = tl.where((attributes & 0x40) != 0, 7 - (y & 7), y & 7)
    else:
        palette = tl.zeros_like(tile)
        priority = tl.zeros_like(tile, dtype=tl.int1)
        bank = tl.zeros_like(tile)
        pixel_x = x & 7
        pixel_y = y & 7

    tile_index = tl.where(unsigned_tiledata, tile, tile + tl.where(tile < 128, 256, 0))
    row_address = tile_index * 16 + pixel_y * 2
    bit = 7 - pixel_x
    low0 = tl.load(vram0 + row_address, mask=mask & (bank == 0), other=0).to(tl.int32)
    high0 = tl.load(vram0 + row_address + 1, mask=mask & (bank == 0), other=0).to(tl.int32)
    low1 = tl.load(vram1 + row_address, mask=mask & (bank != 0), other=0).to(tl.int32)
    high1 = tl.load(vram1 + row_address + 1, mask=mask & (bank != 0), other=0).to(tl.int32)
    low = tl.where(bank == 0, low0, low1)
    high = tl.where(bank == 0, high0, high1)
    color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
    return color, palette, priority


@triton.jit
def _render_sprites(
    vram0,
    vram1,
    oam,
    x,
    y,
    lcdc,
    dmg_palettes,
    object_palette,
    object_palette_register0,
    object_palette_register1,
    valid_x,
    background_color,
    background_priority,
    sprite_line_enabled,
    priority_enabled,
    cgb: tl.constexpr,
    BLOCK: tl.constexpr,
):
    has_sprite = tl.full((BLOCK,), False, tl.int1)
    sprite_rgba = tl.zeros((BLOCK,), tl.int32)
    height = tl.where((lcdc & 4) != 0, 16, 8)
    for sprite_id in tl.range(0, 40):
        sprite_y = tl.load(oam + sprite_id * 4).to(tl.int32) - 16
        row = y - sprite_y
        if (row >= 0) & (row < height):
            sprite_x = tl.load(oam + sprite_id * 4 + 1).to(tl.int32) - 8
            if (sprite_x < 160) & (sprite_x + 8 > 0):
                sprite_tile = tl.load(oam + sprite_id * 4 + 2).to(tl.int32)
                sprite_attributes = tl.load(oam + sprite_id * 4 + 3).to(tl.int32)
                if (sprite_attributes & 0x40) != 0:
                    row = height - 1 - row
                if (lcdc & 4) != 0:
                    sprite_tile = (sprite_tile & 0xFE) + (row >> 3)
                row_address = sprite_tile * 16 + (row & 7) * 2
                if cgb and ((sprite_attributes >> 3) & 1) != 0:
                    low = tl.load(vram1 + row_address).to(tl.int32)
                    high = tl.load(vram1 + row_address + 1).to(tl.int32)
                else:
                    low = tl.load(vram0 + row_address).to(tl.int32)
                    high = tl.load(vram0 + row_address + 1).to(tl.int32)
                pixel_x = tl.minimum(tl.maximum(x - sprite_x, 0), 7)
                if (sprite_attributes & 0x20) != 0:
                    pixel_x = 7 - pixel_x
                bit = 7 - pixel_x
                color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
                if cgb:
                    sprite_visible = (
                        (~priority_enabled)
                        | (background_color == 0)
                        | (~background_priority & ((sprite_attributes & 0x80) == 0))
                    )
                else:
                    sprite_visible = (background_color == 0) | ((sprite_attributes & 0x80) == 0)
                opaque = (
                    valid_x
                    & (x >= sprite_x)
                    & (x < sprite_x + 8)
                    & (color != 0)
                    & sprite_line_enabled
                    & sprite_visible
                    & ~has_sprite
                )
                if cgb:
                    selected_palette = sprite_attributes & 7
                    color_rgba = tl.load(object_palette + selected_palette * 4 + color, mask=opaque, other=0).to(
                        tl.int32
                    )
                else:
                    palette_register = tl.where(
                        (sprite_attributes & 0x10) != 0,
                        object_palette_register1,
                        object_palette_register0,
                    )
                    palette_group = tl.where((sprite_attributes & 0x10) != 0, 2, 1)
                    shade = (palette_register >> (color * 2)) & 3
                    color_rgba = tl.load(dmg_palettes + palette_group * 4 + shade, mask=opaque, other=0).to(tl.int32)
                sprite_rgba = tl.where(opaque, color_rgba, sprite_rgba)
                has_sprite = has_sprite | opaque
    return has_sprite, sprite_rgba


@triton.jit
def _render_frame(
    vram0,
    vram1,
    oam,
    scanlines,
    window_lines,
    render_state,
    dmg_palettes,
    background_palette,
    object_palette,
    frame,
    cgb: tl.constexpr,
    BLOCK: tl.constexpr,
):
    y = tl.program_id(0)
    x = tl.arange(0, BLOCK)
    valid_x = x < 160

    lcdc = tl.load(render_state).to(tl.int32)
    background_map_offset = tl.load(render_state + 1).to(tl.int32)
    window_map_offset = tl.load(render_state + 2).to(tl.int32)
    background_palette_register = tl.load(render_state + 3).to(tl.int32)
    if (lcdc & 0x80) == 0:
        shade = background_palette_register & 3
        blank_rgba = tl.load(dmg_palettes + shade).to(tl.int32)
        output = frame.to(tl.pointer_type(tl.uint32))
        tl.store(output + y * 160 + x, blank_rgba, mask=valid_x)
        return

    object_palette_register0 = tl.load(render_state + 4).to(tl.int32)
    object_palette_register1 = tl.load(render_state + 5).to(tl.int32)

    line_offset = y * 5
    scroll_x = tl.load(scanlines + line_offset).to(tl.int32)
    scroll_y = tl.load(scanlines + line_offset + 1).to(tl.int32)
    window_x = tl.load(scanlines + line_offset + 2).to(tl.int32) - 7
    window_active = tl.load(scanlines + line_offset + 4).to(tl.int32) != 0
    sprite_line_enabled = (lcdc & 0x02) != 0
    priority_enabled = (lcdc & 0x01) != 0
    window_line = tl.load(window_lines + y).to(tl.int32)

    if cgb:
        background_color, background_tile_palette, background_priority = _sample_tile(
            vram0,
            vram1,
            (x + scroll_x) & 0xFF,
            (y + scroll_y) & 0xFF,
            background_map_offset,
            (lcdc & 0x10) != 0,
            cgb,
            valid_x,
        )
        background_rgba = tl.load(
            background_palette + background_tile_palette * 4 + background_color, mask=valid_x, other=0
        ).to(tl.int32)
    else:
        if (lcdc & 1) != 0:
            background_color, _, _ = _sample_tile(
                vram0,
                vram1,
                (x + scroll_x) & 0xFF,
                (y + scroll_y) & 0xFF,
                background_map_offset,
                (lcdc & 0x10) != 0,
                cgb,
                valid_x,
            )
        else:
            background_color = tl.full((BLOCK,), 0, tl.int32)
        background_priority = tl.full((BLOCK,), False, tl.int1)
        shade = (background_palette_register >> (background_color * 2)) & 3
        background_rgba = tl.load(dmg_palettes + shade, mask=valid_x, other=0).to(tl.int32)

    window_visible = ((lcdc & 0x20) != 0) & window_active & (window_x < 160)
    if window_visible:
        use_window = (x >= window_x) & valid_x
        window_color, window_tile_palette, window_priority = _sample_tile(
            vram0,
            vram1,
            (x - window_x) & 0xFF,
            window_line & 0xFF,
            window_map_offset,
            (lcdc & 0x10) != 0,
            cgb,
            use_window,
        )
        if cgb:
            window_rgba = tl.load(
                background_palette + window_tile_palette * 4 + window_color, mask=use_window, other=0
            ).to(tl.int32)
        else:
            shade = (background_palette_register >> (window_color * 2)) & 3
            window_rgba = tl.load(dmg_palettes + shade, mask=use_window, other=0).to(tl.int32)
        rgba = tl.where(use_window, window_rgba, background_rgba)
        background_color = tl.where(use_window, window_color, background_color)
        background_priority = tl.where(use_window, window_priority, background_priority)
    else:
        rgba = background_rgba

    if tl.load(window_lines + 144) != 0:
        has_sprite, sprite_rgba = _render_sprites(
            vram0,
            vram1,
            oam,
            x,
            y,
            lcdc,
            dmg_palettes,
            object_palette,
            object_palette_register0,
            object_palette_register1,
            valid_x,
            background_color,
            background_priority,
            sprite_line_enabled,
            priority_enabled,
            cgb,
            BLOCK,
        )
        rgba = tl.where(has_sprite, sprite_rgba, rgba)
    output = frame.to(tl.pointer_type(tl.uint32))
    tl.store(output + y * 160 + x, rgba, mask=valid_x)


class TorchCudaFrameRenderer:
    _SCANLINE_BYTES = 144 * 5
    _RENDER_STATE_BYTES = 6 * 4

    def __init__(self, torch, device):
        self._torch = torch
        self._device = device
        self._device_index = device.index
        if self._device_index is None:
            self._device_index = torch.cuda.current_device()
        self._raw_current_stream = getattr(torch._C, "_cuda_getCurrentRawStream", None)
        self._current_stream = torch.cuda.current_stream(self._device_index)
        self._slot_count = 64
        self._scanline_host = [
            torch.empty(self._SCANLINE_BYTES + self._RENDER_STATE_BYTES, dtype=torch.uint8, pin_memory=True)
            for _ in range(self._slot_count)
        ]
        self._scanline_host_arrays = [
            buffer.numpy()[: self._SCANLINE_BYTES].reshape((144, 5)) for buffer in self._scanline_host
        ]
        self._render_state_host_arrays = [
            buffer.numpy()[self._SCANLINE_BYTES :].view(np.int32) for buffer in self._scanline_host
        ]
        self._input_device = torch.empty(
            self._SCANLINE_BYTES + self._RENDER_STATE_BYTES, dtype=torch.uint8, device=device
        )
        self._scanline_device = self._input_device[: self._SCANLINE_BYTES].view((144, 5))
        self._window_lines_device = torch.empty(145, dtype=torch.int32, device=device)
        self._render_state_device = self._input_device[self._SCANLINE_BYTES :].view(torch.int32)
        self._memory_host = [
            [torch.empty(size, dtype=torch.uint8, pin_memory=True) for size in (8192, 8192, 160)]
            for _ in range(self._slot_count)
        ]
        self._events = [torch.cuda.Event() for _ in range(self._slot_count)]
        self._slot_used = [False] * self._slot_count
        self._frame_index = 0
        self._reserved_slot = None
        self._graph = None
        self._graph_bindings = None
        self._graph_inputs = None
        self._graph_cgb = None

    def reserve_memory_slot(self):
        if self._reserved_slot is None:
            slot = self._frame_index % self._slot_count
            if self._slot_used[slot]:
                self._events[slot].synchronize()
                self._slot_used[slot] = False
            self._reserved_slot = slot
        return self._reserved_slot

    def _launch_frame(
        self,
        state,
        frame,
        vram0,
        vram1,
        oam,
        dmg_palettes,
        background_palette,
        object_palette,
    ):
        _prepare_window_lines[(1,)](
            self._scanline_device,
            self._render_state_device,
            oam,
            self._window_lines_device,
            256,
            num_warps=4,
        )
        _render_frame[(144,)](
            vram0,
            vram1,
            oam,
            self._scanline_device,
            self._window_lines_device,
            self._render_state_device,
            dmg_palettes,
            background_palette,
            object_palette,
            frame,
            bool(state["cgb"]),
            256,
            num_warps=4,
        )

    def render(
        self,
        state,
        scanlines,
        frame,
        vram0,
        vram1,
        oam,
        dmg_palettes,
        background_palette,
        object_palette,
    ):
        slot = self.reserve_memory_slot()

        host_scanlines = self._scanline_host_arrays[slot]
        host_scanlines[:] = scanlines
        render_state = self._render_state_host_arrays[slot]
        render_state[0] = state["lcdc"]
        render_state[1] = state["background_map_offset"]
        render_state[2] = state["window_map_offset"]
        render_state[3] = state["background_palette_register"]
        render_state[4] = state["object_palette_registers"][0]
        render_state[5] = state["object_palette_registers"][1]
        self._input_device.copy_(self._scanline_host[slot], non_blocking=True)

        graph_inputs = (
            vram0,
            vram1,
            oam,
            dmg_palettes,
            background_palette,
            object_palette,
            frame,
            self._scanline_device,
            self._window_lines_device,
            self._render_state_device,
        )
        graph_bindings = tuple(tensor.data_ptr() for tensor in graph_inputs)
        cgb = bool(state["cgb"])
        if self._graph is None or graph_bindings != self._graph_bindings or cgb != self._graph_cgb:
            self._launch_frame(state, frame, vram0, vram1, oam, dmg_palettes, background_palette, object_palette)
            self._torch.cuda.synchronize(self._device)
            graph = self._torch.cuda.CUDAGraph()
            with self._torch.cuda.graph(graph):
                self._launch_frame(state, frame, vram0, vram1, oam, dmg_palettes, background_palette, object_palette)
            self._graph = graph
            self._graph_bindings = graph_bindings
            self._graph_inputs = graph_inputs
            self._graph_cgb = cgb
        self._graph.replay()
        if self._raw_current_stream is not None:
            current_stream_handle = self._raw_current_stream(self._device_index)
            if current_stream_handle != self._current_stream.cuda_stream:
                self._current_stream = self._torch.cuda.current_stream(self._device_index)
        else:
            self._current_stream = self._torch.cuda.current_stream(self._device_index)
        self._events[slot].record(self._current_stream)
        self._slot_used[slot] = True
        self._frame_index += 1
        self._reserved_slot = None
        return frame
