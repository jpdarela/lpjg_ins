"""Generate light and dark icons for the lpjg_ins VS Code extension."""
import struct
import zlib
import os

def create_png(width, height, pixels):
    """Create a PNG file from raw RGBA pixel data."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))

    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter none
        for x in range(width):
            idx = (y * width + x) * 4
            raw_data += bytes(pixels[idx:idx+4])

    idat = chunk(b'IDAT', zlib.compress(raw_data))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend


def draw_gear_icon(size, fg_color, bg_color, text_color):
    """Draw a gear/cog icon with 'ins' text."""
    import math

    pixels = [0] * (size * size * 4)

    def set_pixel(x, y, r, g, b, a=255):
        if 0 <= x < size and 0 <= y < size:
            idx = (y * size + x) * 4
            # Alpha blending with existing pixel
            old_a = pixels[idx + 3]
            if old_a == 0 or a == 255:
                pixels[idx] = r
                pixels[idx+1] = g
                pixels[idx+2] = b
                pixels[idx+3] = a
            elif a > 0:
                fa = a / 255.0
                pixels[idx] = int(r * fa + pixels[idx] * (1 - fa))
                pixels[idx+1] = int(g * fa + pixels[idx+1] * (1 - fa))
                pixels[idx+2] = int(b * fa + pixels[idx+2] * (1 - fa))
                pixels[idx+3] = min(255, old_a + a)

    def fill_circle(cx, cy, radius, r, g, b, a=255):
        for y in range(max(0, int(cy - radius - 1)), min(size, int(cy + radius + 2))):
            for x in range(max(0, int(cx - radius - 1)), min(size, int(cx + radius + 2))):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if dist <= radius:
                    set_pixel(x, y, r, g, b, a)

    def fill_rect(x1, y1, x2, y2, r, g, b, a=255):
        for y in range(max(0, int(y1)), min(size, int(y2))):
            for x in range(max(0, int(x1)), min(size, int(x2))):
                set_pixel(x, y, r, g, b, a)

    cx, cy = size / 2, size / 2
    outer_r = size * 0.42
    inner_r = size * 0.30
    hole_r = size * 0.15
    n_teeth = 8
    tooth_w = size * 0.10
    tooth_h = size * 0.12

    # Draw gear teeth
    for i in range(n_teeth):
        angle = 2 * math.pi * i / n_teeth
        tx = cx + (outer_r) * math.cos(angle)
        ty = cy + (outer_r) * math.sin(angle)
        fill_circle(tx, ty, tooth_w, *fg_color)

    # Draw gear body
    fill_circle(cx, cy, inner_r, *fg_color)

    # Draw center hole
    fill_circle(cx, cy, hole_r, *bg_color)

    # Draw "ins" text (simple pixel font)
    # Position text in the lower portion
    text_y = int(size * 0.70)
    text_x_start = int(size * 0.22)
    char_w = int(size * 0.13)
    char_h = int(size * 0.18)

    # Background rectangle for text
    fill_rect(text_x_start - 2, text_y - 2,
              text_x_start + char_w * 3 + int(size*0.08) + 2, text_y + char_h + 2,
              *bg_color)

    # Simple block letters for "ins"
    def draw_letter_i(sx, sy, w, h, color):
        bar_w = max(2, w // 3)
        # Top bar
        fill_rect(sx, sy, sx + w, sy + bar_w, *color)
        # Vertical
        fill_rect(sx + w//2 - bar_w//2, sy, sx + w//2 + bar_w//2 + 1, sy + h, *color)
        # Bottom bar
        fill_rect(sx, sy + h - bar_w, sx + w, sy + h, *color)

    def draw_letter_n(sx, sy, w, h, color):
        bar_w = max(2, w // 4)
        # Left vertical
        fill_rect(sx, sy, sx + bar_w, sy + h, *color)
        # Right vertical
        fill_rect(sx + w - bar_w, sy, sx + w, sy + h, *color)
        # Top connector
        fill_rect(sx, sy, sx + w, sy + bar_w, *color)

    def draw_letter_s(sx, sy, w, h, color):
        bar_w = max(2, w // 4)
        mid = sy + h // 2
        # Top bar
        fill_rect(sx, sy, sx + w, sy + bar_w, *color)
        # Left upper
        fill_rect(sx, sy, sx + bar_w, mid, *color)
        # Middle bar
        fill_rect(sx, mid - bar_w//2, sx + w, mid + bar_w//2 + 1, *color)
        # Right lower
        fill_rect(sx + w - bar_w, mid, sx + w, sy + h, *color)
        # Bottom bar
        fill_rect(sx, sy + h - bar_w, sx + w, sy + h, *color)

    spacing = int(size * 0.03)
    x = text_x_start
    draw_letter_i(x, text_y, char_w, char_h, text_color)
    x += char_w + spacing
    draw_letter_n(x, text_y, char_w, char_h, text_color)
    x += char_w + spacing
    draw_letter_s(x, text_y, char_w, char_h, text_color)

    return pixels


def main():
    size = 128
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Light icon (dark foreground on transparent - for light themes)
    fg_light = (80, 80, 80)      # dark gray gear
    bg_light = (255, 255, 255)   # white background for cutouts
    text_light = (40, 100, 40)   # dark green text
    pixels_light = draw_gear_icon(size, fg_light, bg_light, text_light)
    png_light = create_png(size, size, pixels_light)
    with open(os.path.join(script_dir, 'ins-icon-light.png'), 'wb') as f:
        f.write(png_light)

    # Dark icon (light foreground on transparent - for dark themes)
    fg_dark = (200, 200, 200)    # light gray gear
    bg_dark = (30, 30, 30)       # dark background for cutouts
    text_dark = (100, 200, 100)  # green text
    pixels_dark = draw_gear_icon(size, fg_dark, bg_dark, text_dark)
    png_dark = create_png(size, size, pixels_dark)
    with open(os.path.join(script_dir, 'ins-icon-dark.png'), 'wb') as f:
        f.write(png_dark)

    print("Icons generated successfully!")


if __name__ == '__main__':
    main()
