#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pathlib import Path

import numpy as np


MPS_INPUT_SLOT_COUNT = 64


class TorchFrameRenderer:
    def __init__(self, device):
        try:
            import torch
        except ImportError as exc:
            raise ImportError(
                'Install the optional "ai-training" dependencies with `pip install pyboy[ai-training]`.'
            ) from exc

        self._torch = torch
        self.device = torch.device(device)
        self.device_spec = str(self.device)
        if self.device.type == "mps":
            self._memory_slot_tensors = [
                torch.empty(8192 * 2 + 160, dtype=torch.uint8, pin_memory=True) for _ in range(MPS_INPUT_SLOT_COUNT)
            ]
            self._memory_slot_arrays = [tensor.numpy() for tensor in self._memory_slot_tensors]
            self._memory_slot_versions = [[None, None, None] for _ in self._memory_slot_tensors]
            self._metal_frame_index = 0
            self._vram0 = self._vram1 = self._oam = None
        else:
            self._memory_slot_tensors = None
            self._memory_slot_arrays = None
            self._memory_slot_versions = None
            self._metal_frame_index = 0
            self._vram0 = torch.empty(8192, dtype=torch.uint8, device=self.device)
            self._vram1 = torch.empty(8192, dtype=torch.uint8, device=self.device)
            self._oam = torch.empty(160, dtype=torch.uint8, device=self.device)
        self._vram0_snapshot = np.empty(8192, dtype=np.uint8)
        self._vram1_snapshot = np.empty(8192, dtype=np.uint8)
        self._oam_snapshot = np.empty(160, dtype=np.uint8)
        self._buffer_versions = [None, None, None]
        self._memory_initialized = False
        self._frame = torch.empty((144, 160, 4), dtype=torch.uint8, device=self.device)
        self._palette_key = None
        self._dmg_palette_rgba = None
        self._background_color_palette_rgba = None
        self._object_color_palette_rgba = None
        self._metal_renderer = None
        self._cuda_renderer = None
        if self.device.type == "cuda":
            try:
                from pyboy.api.torch_cuda import TorchCudaFrameRenderer
            except ImportError:
                pass
            else:
                self._cuda_renderer = TorchCudaFrameRenderer(torch, self.device)
        if self.device.type != "mps":
            self._rows = torch.arange(144, dtype=torch.long, device=self.device)
            self._columns = torch.arange(160, dtype=torch.long, device=self.device)
            self._sprite_indices = torch.arange(40, dtype=torch.long, device=self.device).view(1, 1, 40)

    def _sync_buffer(
        self, tensor, snapshot, raw_data, non_blocking=False, index=None, generation=None, host_buffer=None
    ):
        source = np.frombuffer(raw_data, dtype=np.uint8)
        if source.size != snapshot.size:
            raise ValueError(f"Expected {snapshot.size} bytes to synchronize, got {source.size}")
        if index is not None and generation is not None and self._buffer_versions[index] == generation:
            return

        if host_buffer is not None:
            if index is not None and generation is not None:
                snapshot_name = ("_vram0_snapshot", "_vram1_snapshot", "_oam_snapshot")[index]
                snapshot = host_buffer.numpy()
                np.copyto(snapshot, source)
                setattr(self, snapshot_name, snapshot)
            else:
                np.copyto(snapshot, source)
                host_buffer.copy_(self._torch.from_numpy(snapshot))
            tensor.copy_(host_buffer, non_blocking=True)
            if index is not None:
                self._buffer_versions[index] = generation
            return

        if self.device.type == "mps":
            if not self._memory_initialized or not np.array_equal(source, snapshot):
                values = source.copy()
                np.copyto(snapshot, values)
                tensor.copy_(self._torch.from_numpy(values))
            if index is not None:
                self._buffer_versions[index] = generation
            return

        if not self._memory_initialized:
            np.copyto(snapshot, source)
            host = self._torch.from_numpy(snapshot.copy())
            if non_blocking:
                host = host.pin_memory()
                tensor.copy_(host, non_blocking=True)
            else:
                tensor.copy_(host.to(self.device))
            if index is not None:
                self._buffer_versions[index] = generation
            return

        changed = np.flatnonzero(source != snapshot)
        if changed.size == 0:
            if index is not None:
                self._buffer_versions[index] = generation
            return

        if changed.size > source.size // 2:
            np.copyto(snapshot, source)
            host = self._torch.from_numpy(snapshot.copy())
            if non_blocking:
                host = host.pin_memory()
                tensor.copy_(host, non_blocking=True)
            else:
                tensor.copy_(host.to(self.device))
            if index is not None:
                self._buffer_versions[index] = generation
            return

        values = source[changed].copy()
        snapshot[changed] = values
        indices = self._torch.from_numpy(changed)
        updates = self._torch.from_numpy(values)
        if non_blocking:
            indices = indices.pin_memory().to(self.device, non_blocking=True)
            updates = updates.pin_memory().to(self.device, non_blocking=True)
        else:
            indices = indices.to(self.device)
            updates = updates.to(self.device)
        tensor.index_copy_(0, indices, updates)
        if index is not None:
            self._buffer_versions[index] = generation

    def _sync_memory(self, state, memory=None, non_blocking=False, slot=None, memory_host=None):
        if self.device.type == "mps":
            if memory is None:
                raise ValueError("A reusable MPS input slot is required to synchronize renderer memory")
            if slot is None:
                raise ValueError("The MPS input slot index is required to track its memory version")
            sources = [
                np.frombuffer(state["vram0"], dtype=np.uint8),
                np.frombuffer(state["vram1"], dtype=np.uint8),
                np.frombuffer(state["oam"], dtype=np.uint8),
            ]
            expected_sizes = (8192, 8192, 160)
            version_keys = ("vram0_generation", "vram1_generation", "oam_generation")
            versions = tuple(state.get(key) for key in version_keys)
            slot_versions = self._memory_slot_versions[slot]
            offset = 0
            for index, (source, expected, version) in enumerate(zip(sources, expected_sizes, versions)):
                if source.size != expected:
                    raise ValueError(f"Expected {expected} bytes to synchronize, got {source.size}")
                target = memory[offset : offset + source.size]
                if version is None or version != slot_versions[index]:
                    np.copyto(target, source)
                    slot_versions[index] = version
                offset += source.size
            return

        self._sync_buffer(
            self._vram0,
            self._vram0_snapshot,
            state["vram0"],
            non_blocking,
            0,
            state.get("vram0_generation"),
            None if memory_host is None else memory_host[0],
        )
        self._sync_buffer(
            self._vram1,
            self._vram1_snapshot,
            state["vram1"],
            non_blocking,
            1,
            state.get("vram1_generation"),
            None if memory_host is None else memory_host[1],
        )
        self._sync_buffer(
            self._oam,
            self._oam_snapshot,
            state["oam"],
            non_blocking,
            2,
            state.get("oam_generation"),
            None if memory_host is None else memory_host[2],
        )
        self._memory_initialized = True

    def prefetch_memory(self, state):
        if self.device.type not in ("cpu", "mps"):
            cuda_renderer = getattr(self, "_cuda_renderer", None)
            if cuda_renderer is None:
                self._sync_memory(state, non_blocking=True)
            else:
                slot = cuda_renderer.reserve_memory_slot()
                self._sync_memory(
                    state,
                    non_blocking=True,
                    memory_host=cuda_renderer._memory_host[slot],
                )

    def needs_memory_prefetch(self, generations):
        return any(generation != version for generation, version in zip(generations, self._buffer_versions))

    def _load_metal_renderer(self):
        if self._metal_renderer is not None:
            return

        from torch.utils.cpp_extension import load

        source_dir = Path(__file__).parent
        module = load(
            name="pyboy_torch_metal_renderer_v2",
            sources=[str(source_dir / "torch_metal.mm")],
            extra_cflags=["-fobjc-arc", "-fblocks", "-x", "objective-c++"],
            extra_ldflags=["-framework", "Metal", "-framework", "Foundation", "-framework", "QuartzCore"],
            verbose=False,
        )
        shader_source = (source_dir / "torch_metal.metal").read_text(encoding="utf-8")
        self._metal_renderer = module.MetalFrameRenderer(shader_source)

    def _pack_metal_scanlines(self, state, scanlines):
        window_rows = (scanlines[:, 4] != 0) & (scanlines[:, 2] < 167) & bool(state["lcdc"] & 0x20)
        window_lines = np.cumsum(window_rows, dtype=np.int32) - 1
        packed = np.empty((144, 5), dtype=np.uint8)
        packed[:, :3] = scanlines[:, :3]
        packed[:, 3] = scanlines[:, 4]
        packed[:, 4] = window_lines
        return packed

    def _render_metal(self, state, scanlines, memory):
        metal_scanlines = self._pack_metal_scanlines(state, scanlines)

        config = np.zeros(83, dtype=np.int32)
        config[0] = int(state["cgb"])
        config[1] = state["lcdc"]
        config[2] = state["background_map_offset"]
        config[3] = state["window_map_offset"]
        config[4] = state["background_palette_register"]
        config[5:7] = state["object_palette_registers"]
        config[7:19] = np.asarray(state["dmg_palettes"], dtype=np.int32).reshape(-1)
        if state["cgb"]:
            config[19:51] = state["background_color_palette"]
            config[51:83] = state["object_color_palette"]

        self._metal_renderer.render(
            memory,
            metal_scanlines,
            config,
            self._frame,
        )
        return self._frame

    def _sync_palettes(self, state):
        key = (
            state["dmg_palettes"],
            state["background_color_palette"],
            state["object_color_palette"],
        )
        if key == self._palette_key:
            return

        self._set_palette_tensor("_dmg_palettes", state["dmg_palettes"], self._torch.int64)
        if state["cgb"]:
            self._set_palette_tensor("_background_color_palette", state["background_color_palette"], self._torch.int64)
            self._set_palette_tensor("_object_color_palette", state["object_color_palette"], self._torch.int64)
        if self.device.type == "cuda":
            dmg_rgb = np.asarray(state["dmg_palettes"], dtype=np.uint32).reshape(-1)
            dmg_rgba = (
                ((dmg_rgb >> 16) & 0xFF)
                | (((dmg_rgb >> 8) & 0xFF) << 8)
                | ((dmg_rgb & 0xFF) << 16)
                | np.uint32(0xFF000000)
            ).view(np.int32)
            self._set_palette_tensor("_dmg_palette_rgba", dmg_rgba, self._torch.int32)
            if state["cgb"]:
                background_rgb15 = np.asarray(state["background_color_palette"], dtype=np.uint32)
                object_rgb15 = np.asarray(state["object_color_palette"], dtype=np.uint32)
                background_rgba = (
                    ((background_rgb15 & 0x1F) << 3)
                    | (((background_rgb15 >> 5) & 0x1F) << 11)
                    | (((background_rgb15 >> 10) & 0x1F) << 19)
                    | np.uint32(0xFF000000)
                ).view(np.int32)
                object_rgba = (
                    ((object_rgb15 & 0x1F) << 3)
                    | (((object_rgb15 >> 5) & 0x1F) << 11)
                    | (((object_rgb15 >> 10) & 0x1F) << 19)
                    | np.uint32(0xFF000000)
                ).view(np.int32)
                self._set_palette_tensor("_background_color_palette_rgba", background_rgba, self._torch.int32)
                self._set_palette_tensor("_object_color_palette_rgba", object_rgba, self._torch.int32)
        self._palette_key = key

    def _set_palette_tensor(self, name, values, dtype):
        tensor = self._torch.tensor(values, dtype=dtype, device=self.device)
        current = getattr(self, name, None)
        if self.device.type == "cuda" and current is not None:
            current.copy_(tensor)
        else:
            setattr(self, name, tensor)

    def _tile_pixels(self, x, y, map_offset, unsigned_tiledata, cgb):
        torch = self._torch
        map_address = map_offset + (y >> 3) * 32 + (x >> 3)
        tile = self._vram0[map_address].to(torch.long)
        if cgb:
            attributes = self._vram1[map_address].to(torch.long)
            palette = attributes & 0x07
            bank = (attributes >> 3) & 1
            priority = (attributes & 0x80) != 0
            pixel_x = x & 7
            pixel_y = y & 7
            pixel_x = torch.where(attributes & 0x20 != 0, 7 - pixel_x, pixel_x)
            pixel_y = torch.where(attributes & 0x40 != 0, 7 - pixel_y, pixel_y)
        else:
            palette = torch.zeros_like(tile)
            bank = torch.zeros_like(tile)
            priority = torch.zeros_like(tile, dtype=torch.bool)
            pixel_x = x & 7
            pixel_y = y & 7

        if unsigned_tiledata:
            tile_address = tile * 16
        else:
            signed_tile = torch.where(tile < 128, tile + 256, tile)
            tile_address = signed_tile * 16

        row_address = tile_address + pixel_y * 2
        low = torch.where(bank != 0, self._vram1[row_address], self._vram0[row_address]).to(torch.long)
        high = torch.where(bank != 0, self._vram1[row_address + 1], self._vram0[row_address + 1]).to(torch.long)
        bit = 7 - pixel_x
        color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
        return color, palette, priority

    def _dmg_rgb(self, color, palette_register, palette_index=0):
        torch = self._torch
        register = torch.full_like(color, int(palette_register), dtype=torch.long)
        shade = (register >> (color * 2)) & 3
        base_color = self._dmg_palettes[palette_index][shade]
        return self._rgba(base_color)

    def _cgb_rgb(self, color, palette, object_palette=False):
        palette_data = self._object_color_palette if object_palette else self._background_color_palette
        packed = palette_data[palette * 4 + color]
        red = (packed & 0x1F) << 3
        green = ((packed >> 5) & 0x1F) << 3
        blue = ((packed >> 10) & 0x1F) << 3
        rgb = (red << 16) | (green << 8) | blue
        return self._rgba(rgb)

    def _rgba(self, rgb):
        torch = self._torch
        return torch.stack(
            (
                (rgb >> 16) & 0xFF,
                (rgb >> 8) & 0xFF,
                rgb & 0xFF,
                torch.full_like(rgb, 0xFF),
            ),
            dim=-1,
        ).to(torch.uint8)

    def _fill_blank_frame(self, state):
        color = state["dmg_palettes"][0][state["background_palette_register"] & 3]
        pixel = self._torch.tensor(
            ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, 0xFF),
            dtype=self._torch.uint8,
            device=self.device,
        )
        self._frame.copy_(pixel)
        return self._frame

    def _render_background(self, state, scanlines, window_rows=None):
        torch = self._torch
        cgb = state["cgb"]
        lcdc = state["lcdc"]
        background_enabled = cgb or bool(lcdc & 0x01)
        if background_enabled:
            scroll_x = torch.as_tensor(scanlines[:, 0].copy(), dtype=torch.long, device=self.device)[:, None]
            scroll_y = torch.as_tensor(scanlines[:, 1].copy(), dtype=torch.long, device=self.device)[:, None]
            x = (self._columns[None, :] + scroll_x) & 0xFF
            y = (self._rows[:, None] + scroll_y) & 0xFF
            color, palette, priority = self._tile_pixels(
                x,
                y,
                state["background_map_offset"],
                bool(lcdc & 0x10),
                cgb,
            )
            if cgb:
                frame = self._cgb_rgb(color, palette)
            else:
                frame = self._dmg_rgb(color, state["background_palette_register"])
        else:
            color = torch.zeros((144, 160), dtype=torch.long, device=self.device)
            priority = torch.zeros((144, 160), dtype=torch.bool, device=self.device)
            frame = self._dmg_rgb(color, state["background_palette_register"])

        if window_rows is None and lcdc & 0x20:
            window_rows = (scanlines[:, 4] != 0) & (scanlines[:, 2] < 167)
        if window_rows is None or not np.any(window_rows):
            return frame, color, priority

        window_x = torch.as_tensor(scanlines[:, 2].copy(), dtype=torch.long, device=self.device) - 7
        window_rows = torch.as_tensor(window_rows.copy(), dtype=torch.bool, device=self.device)
        window_line = torch.cumsum(window_rows.to(torch.long), dim=0) - 1
        window_x_grid = self._columns[None, :] - window_x[:, None]
        window_y_grid = window_line[:, None].expand(144, 160)
        window_color, window_palette, window_priority = self._tile_pixels(
            window_x_grid & 0xFF,
            window_y_grid & 0xFF,
            state["window_map_offset"],
            bool(lcdc & 0x10),
            cgb,
        )
        if cgb:
            window_frame = self._cgb_rgb(window_color, window_palette)
        else:
            window_frame = self._dmg_rgb(window_color, state["background_palette_register"])

        window_mask = (
            window_rows[:, None] & (self._columns[None, :] >= window_x[:, None]) & (self._columns[None, :] < 160)
        )
        return (
            torch.where(window_mask[:, :, None], window_frame, frame),
            torch.where(window_mask, window_color, color),
            torch.where(window_mask, window_priority, priority),
        )

    def _render_sprites(self, state, frame, background_color, background_priority):
        torch = self._torch
        lcdc = state["lcdc"]
        if not lcdc & 0x02:
            return frame

        cgb = state["cgb"]
        priority_enabled = bool(lcdc & 0x01)
        height = 16 if lcdc & 0x04 else 8
        oam = self._oam.reshape(40, 4).to(torch.long)
        sprite_y = oam[:, 0] - 16
        sprite_x = oam[:, 1] - 8
        sprite_tile = oam[:, 2]
        attributes = oam[:, 3]

        row = self._rows[:, None, None] - sprite_y[None, None, :]
        column = self._columns[None, :, None] - sprite_x[None, None, :]
        visible = (row >= 0) & (row < height) & (column >= 0) & (column < 8)
        row = row.clamp(0, height - 1)
        column = column.clamp(0, 7)
        y_flip = attributes[None, None, :] & 0x40 != 0
        x_flip = attributes[None, None, :] & 0x20 != 0
        row = torch.where(y_flip, height - 1 - row, row)
        column = torch.where(x_flip, 7 - column, column)

        tile = sprite_tile[None, None, :]
        if height == 16:
            tile = (tile & 0xFE) + (row >> 3)
        row_address = tile * 16 + (row & 7) * 2
        bank = ((attributes >> 3) & 1)[None, None, :] if cgb else torch.zeros_like(row_address)
        low = torch.where(bank != 0, self._vram1[row_address], self._vram0[row_address]).to(torch.long)
        high = torch.where(bank != 0, self._vram1[row_address + 1], self._vram0[row_address + 1]).to(torch.long)
        bit = 7 - column
        color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1)
        background_color_zero = background_color == 0
        sprite_behind_background = attributes[None, None, :] & 0x80 != 0
        if cgb:
            sprite_visible = (
                (not priority_enabled)
                | background_color_zero[:, :, None]
                | (~background_priority[:, :, None] & ~sprite_behind_background)
            )
        else:
            sprite_visible = background_color_zero[:, :, None] | ~sprite_behind_background
        opaque = visible & (color != 0) & sprite_visible

        winner = torch.where(opaque, self._sprite_indices, 40).amin(dim=2)
        has_sprite = winner < 40
        selected = winner.clamp(max=39)
        color = torch.gather(color, 2, selected[:, :, None]).squeeze(2)
        selected_attributes = attributes[selected]

        if cgb:
            palette = selected_attributes & 0x07
            sprite_frame = self._cgb_rgb(color, palette, object_palette=True)
        else:
            object_palette = (selected_attributes & 0x10) != 0
            register = torch.full_like(color, int(state["object_palette_registers"][0]), dtype=torch.long)
            register = torch.where(
                object_palette,
                torch.full_like(color, int(state["object_palette_registers"][1]), dtype=torch.long),
                register,
            )
            shade = (register >> (color * 2)) & 3
            base = self._dmg_palettes[1 + object_palette.to(torch.long), shade]
            sprite_frame = self._rgba(base)

        return torch.where(has_sprite[:, :, None], sprite_frame, frame)

    def render(self, state):
        lcdc = state["lcdc"]
        if not lcdc & 0x80:
            return self._fill_blank_frame(state)

        scanline_data = state["scanlines"]
        if isinstance(scanline_data, bytes):
            if len(scanline_data) != 144 * 5:
                raise ValueError(f"Expected 144 scanline parameter rows of five values, got {len(scanline_data)} bytes")
            scanlines = np.frombuffer(scanline_data, dtype=np.uint8).reshape((144, 5))
        else:
            scanlines = np.asarray(scanline_data, dtype=np.uint8)
        if scanlines.shape != (144, 5):
            raise ValueError(f"Expected 144 scanline parameter rows of five values, got {scanlines.shape}")

        window_rows = None
        if lcdc & 0x20:
            window_rows = (scanlines[:, 4] != 0) & (scanlines[:, 2] < 167)
        window_visible = window_rows is not None and bool(np.any(window_rows))
        if not state["cgb"] and not lcdc & 0x01 and not window_visible and not lcdc & 0x02:
            return self._fill_blank_frame(state)

        if self.device.type == "mps":
            self._load_metal_renderer()
            slot_count = len(self._memory_slot_tensors)
            if self._metal_frame_index and self._metal_frame_index % slot_count == 0:
                self._torch.mps.synchronize()
            slot = self._metal_frame_index % slot_count
            self._sync_memory(state, self._memory_slot_arrays[slot], slot=slot)
            frame = self._render_metal(state, scanlines, self._memory_slot_tensors[slot])
            self._metal_frame_index += 1
            return frame

        if (
            self.device.type != "cuda"
            or not self._memory_initialized
            or any(
                state.get(key) is None or state[key] != self._buffer_versions[index]
                for index, key in enumerate(("vram0_generation", "vram1_generation", "oam_generation"))
            )
        ):
            self._sync_memory(state, non_blocking=self.device.type == "cuda")
        self._sync_palettes(state)
        if self.device.type == "cuda" and self._cuda_renderer is not None:
            return self._cuda_renderer.render(
                state,
                scanlines,
                self._frame,
                self._vram0,
                self._vram1,
                self._oam,
                self._dmg_palette_rgba,
                self._background_color_palette_rgba if state["cgb"] else self._dmg_palette_rgba,
                self._object_color_palette_rgba if state["cgb"] else self._dmg_palette_rgba,
            )
        frame, background_color, background_priority = self._render_background(state, scanlines, window_rows)
        if lcdc & 0x02:
            frame = self._render_sprites(state, frame, background_color, background_priority)
        self._frame.copy_(frame)
        return self._frame

    def get_frame(self):
        return self._frame

    def present_metal(self, frame, layer_address):
        if self.device.type != "mps":
            raise RuntimeError("Direct Metal presentation requires the MPS renderer")
        self._load_metal_renderer()
        self._metal_renderer.present(frame, int(layer_address))
