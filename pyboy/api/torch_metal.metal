#include <metal_stdlib>
using namespace metal;

struct TilePixel {
    uint color;
    uint palette;
    bool priority;
};

inline TilePixel sample_tile(
    uint x,
    uint y,
    uint map_offset,
    bool unsigned_tiledata,
    bool cgb,
    device const uchar *vram0,
    device const uchar *vram1
) {
    uint map_address = map_offset + (y >> 3) * 32 + (x >> 3);
    uint tile = vram0[map_address];
    uint attributes = cgb ? vram1[map_address] : 0;
    uint palette = cgb ? attributes & 7 : 0;
    uint bank = cgb ? (attributes >> 3) & 1 : 0;
    uint pixel_x = x & 7;
    uint pixel_y = y & 7;

    if (cgb && (attributes & 0x20)) {
        pixel_x = 7 - pixel_x;
    }
    if (cgb && (attributes & 0x40)) {
        pixel_y = 7 - pixel_y;
    }

    uint tile_index = tile;
    if (!unsigned_tiledata && tile < 128) {
        tile_index += 256;
    }
    uint row_address = tile_index * 16 + pixel_y * 2;
    device const uchar *tiledata = bank ? vram1 : vram0;
    uint bit = 7 - pixel_x;
    uint low = tiledata[row_address];
    uint high = tiledata[row_address + 1];

    TilePixel result;
    result.color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1);
    result.palette = palette;
    result.priority = (attributes & 0x80) != 0;
    return result;
}

inline void write_pixel(
    device uchar *frame,
    uint offset,
    uint color,
    uint palette,
    bool cgb,
    bool object,
    uint dmg_group,
    uint dmg_register,
    constant int *config
) {
    uint red;
    uint green;
    uint blue;

    if (cgb) {
        uint palette_offset = object ? 51 : 19;
        uint packed = config[palette_offset + palette * 4 + color];
        red = (packed & 0x1F) << 3;
        green = ((packed >> 5) & 0x1F) << 3;
        blue = ((packed >> 10) & 0x1F) << 3;
    } else {
        uint shade = (dmg_register >> (color * 2)) & 3;
        uint packed = config[7 + dmg_group * 4 + shade];
        red = (packed >> 16) & 0xFF;
        green = (packed >> 8) & 0xFF;
        blue = packed & 0xFF;
    }

    frame[offset] = (uchar)red;
    frame[offset + 1] = (uchar)green;
    frame[offset + 2] = (uchar)blue;
    frame[offset + 3] = 0xFF;
}

kernel void render_frame(
    device const uchar *vram0 [[buffer(0)]],
    device const uchar *vram1 [[buffer(1)]],
    device const uchar *oam [[buffer(2)]],
    constant uchar *scanlines [[buffer(3)]],
    constant int *config [[buffer(4)]],
    device uchar *frame [[buffer(5)]],
    uint3 position [[thread_position_in_grid]],
    uint3 group_position [[threadgroup_position_in_grid]],
    uint thread_index [[thread_index_in_threadgroup]]
) {
    uint x = position.x;
    uint y = group_position.y;
    if (x >= 160 || y >= 144) {
        return;
    }

    bool cgb = config[0] != 0;
    uint lcdc = config[1];
    uint output_offset = (y * 160 + x) * 4;
    bool sprite_line_enabled = (lcdc & 0x02) != 0;
    bool priority_enabled = (lcdc & 0x01) != 0;
    if (!(lcdc & 0x80)) {
        write_pixel(frame, output_offset, 0, 0, false, false, 0, config[4], config);
        return;
    }

    threadgroup uint line_sprites[40];
    threadgroup uint line_sprite_count;
    threadgroup uint line_scroll_x;
    threadgroup uint line_scroll_y;
    threadgroup uint line_window_x;
    threadgroup uint line_window_active;
    threadgroup uint line_window_line;
    if (thread_index == 0) {
        uint count = 0;
        if (sprite_line_enabled) {
            int height = (lcdc & 4) ? 16 : 8;
            for (uint sprite = 0; sprite < 40; ++sprite) {
                int top = (int)oam[sprite * 4] - 16;
                if ((int)y >= top && (int)y < top + height) {
                    line_sprites[count++] = sprite;
                }
            }

        }
        line_sprite_count = count;

        uint line_offset = y * 5;
        line_scroll_x = scanlines[line_offset];
        line_scroll_y = scanlines[line_offset + 1];
        line_window_x = scanlines[line_offset + 2];
        line_window_active = scanlines[line_offset + 3] != 0;
        line_window_line = scanlines[line_offset + 4];
    }
    threadgroup_barrier(mem_flags::mem_threadgroup);

    uint scroll_x = line_scroll_x;
    uint scroll_y = line_scroll_y;
    int window_x = (int)line_window_x - 7;
    bool window_active = line_window_active != 0;
    uint window_line = line_window_line;

    TilePixel background;
    if (cgb || (lcdc & 1)) {
        background = sample_tile(
            (x + scroll_x) & 0xFF,
            (y + scroll_y) & 0xFF,
            (uint)config[2],
            (lcdc & 0x10) != 0,
            cgb,
            vram0,
            vram1
        );
    } else {
        background.color = 0;
        background.palette = 0;
        background.priority = false;
    }
    uint background_color = background.color;
    bool background_priority = background.priority;
    write_pixel(frame, output_offset, background.color, background.palette, cgb, false, 0, config[4], config);

    if ((lcdc & 0x20) && window_active && window_x < 160 && (int)x >= window_x) {
        TilePixel window = sample_tile(
            (uint)((int)x - window_x) & 0xFF,
            window_line,
            (uint)config[3],
            (lcdc & 0x10) != 0,
            cgb,
            vram0,
            vram1
        );
        background_color = window.color;
        background_priority = window.priority;
        write_pixel(frame, output_offset, window.color, window.palette, cgb, false, 0, config[4], config);
    }

    uint sprite_height = (lcdc & 4) ? 16 : 8;
    bool has_sprite = false;
    uint sprite_color = 0;
    uint sprite_attributes = 0;
    for (uint index = 0; index < line_sprite_count; ++index) {
        uint sprite = line_sprites[index];
        uint sprite_offset = (uint)sprite * 4;
        int top = (int)oam[sprite_offset] - 16;
        int left = (int)oam[sprite_offset + 1] - 8;
        int row = (int)y - top;
        int column = (int)x - left;
        if (row < 0 || row >= (int)sprite_height || column < 0 || column >= 8) {
            continue;
        }

        uint tile = oam[sprite_offset + 2];
        uint attributes = oam[sprite_offset + 3];
        if (sprite_height == 16) {
            tile &= 0xFE;
        }
        if (attributes & 0x40) {
            row = (int)sprite_height - 1 - row;
        }
        if (attributes & 0x20) {
            column = 7 - column;
        }
        if (sprite_height == 16) {
            tile += (uint)row >> 3;
        }

        uint bank = cgb ? (attributes >> 3) & 1 : 0;
        device const uchar *tiledata = bank ? vram1 : vram0;
        uint row_address = tile * 16 + ((uint)row & 7) * 2;
        uint bit = 7 - (uint)column;
        uint low = tiledata[row_address];
        uint high = tiledata[row_address + 1];
        uint color = ((low >> bit) & 1) | (((high >> bit) & 1) << 1);
        if (color == 0) {
            continue;
        }
        bool sprite_visible;
        if (cgb) {
            sprite_visible = !priority_enabled ||
                background_color == 0 ||
                (!background_priority && !(attributes & 0x80));
        } else {
            sprite_visible = background_color == 0 || !(attributes & 0x80);
        }
        if (!sprite_visible) {
            continue;
        }

        has_sprite = true;
        sprite_color = color;
        sprite_attributes = attributes;
        break;
    }

    if (has_sprite) {
        if (cgb) {
            write_pixel(frame, output_offset, sprite_color, sprite_attributes & 7, true, true, 0, 0, config);
        } else {
            bool use_obp1 = (sprite_attributes & 0x10) != 0;
            uint palette_register = use_obp1 ? (uint)config[6] : (uint)config[5];
            uint palette_group = use_obp1 ? 2 : 1;
            write_pixel(
                frame,
                output_offset,
                sprite_color,
                0,
                false,
                true,
                palette_group,
                palette_register,
                config
            );
        }
    }
}

kernel void present_frame(
    device const uchar *frame [[buffer(0)]],
    texture2d<float, access::write> drawable [[texture(0)]],
    uint2 position [[thread_position_in_grid]]
) {
    uint width = drawable.get_width();
    uint height = drawable.get_height();
    if (position.x >= width || position.y >= height) {
        return;
    }

    uint content_width;
    uint content_height;
    if (width * 144 <= height * 160) {
        content_width = width;
        content_height = max(1u, width * 144 / 160);
    } else {
        content_width = max(1u, height * 160 / 144);
        content_height = height;
    }

    uint origin_x = (width - content_width) / 2;
    uint origin_y = (height - content_height) / 2;
    if (position.x < origin_x || position.x >= origin_x + content_width ||
        position.y < origin_y || position.y >= origin_y + content_height) {
        drawable.write(float4(0.0, 0.0, 0.0, 1.0), position);
        return;
    }

    uint source_x = (position.x - origin_x) * 160 / content_width;
    uint source_y = (position.y - origin_y) * 144 / content_height;
    uint offset = (source_y * 160 + source_x) * 4;
    float4 color = float4(
        frame[offset],
        frame[offset + 1],
        frame[offset + 2],
        frame[offset + 3]
    ) / 255.0;
    drawable.write(color, position);
}
