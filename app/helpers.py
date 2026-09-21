"""Reusable rendering, terminal, and optional image helpers."""

import os

try:
    from .assets import FULLWIDTH_DIGITS
except ImportError:
    from assets import FULLWIDTH_DIGITS

try:
    from PIL import Image as _PILImage
    _PILLOW = True
except ImportError:
    _PILLOW = False


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def center_text(text: str, width: int) -> str:
    text = str(text)[:width]
    pad = (width - len(text)) // 2
    return (" " * pad + text + " " * width)[:width]


def display_char(digit: int, large: bool) -> str:
    key = int(digit) % 10
    return FULLWIDTH_DIGITS[key] if large else str(key)


def digit_canvas(digit: int, large: bool, width: int, height: int) -> list[str]:
    height = max(1, height)
    blank = " " * width
    lines = [center_text(display_char(digit, large), width)]
    out = [blank] * height
    start = (height - len(lines)) // 2
    for i, row in enumerate(lines):
        out[start + i] = row
    return out


def shift_lines(lines: list[str], row_delta: float, col_delta: float) -> list[str]:
    if not lines:
        return lines
    height = len(lines)
    width = len(lines[0])
    blank = " " * width
    row_shift = max(-(height - 1), min(height - 1, round(row_delta)))
    col_shift = max(-(width - 1), min(width - 1, round(col_delta)))
    out = [blank] * height
    for index, line in enumerate(lines):
        target = index + row_shift
        if 0 <= target < height:
            if col_shift > 0:
                out[target] = (" " * col_shift + line)[:width]
            elif col_shift < 0:
                out[target] = (line[-col_shift:] + " " * width)[:width]
            else:
                out[target] = line
    return out


def block_char(top_on: bool, bottom_on: bool) -> str:
    if top_on and bottom_on:
        return "\u2588"
    if top_on:
        return "\u2580"
    if bottom_on:
        return "\u2584"
    return " "


def image_to_terminal_lines(path: str, max_width: int, max_height: int):
    if not _PILLOW:
        return [], "Pillow not installed - run: pip3 install pillow"
    if not path or not os.path.isfile(path):
        return [], f"Image not found: {path}"
    try:
        image = _PILImage.open(path).convert("RGBA")
    except (OSError, ValueError) as exc:
        return [], f"Could not open image: {exc}"
    if max_width < 8 or max_height < 2:
        return [], None
    ratio = image.width / float(image.height)
    target_width = max_width
    target_height = max(2, int(target_width / ratio) // 2)
    if target_height > max_height:
        target_height = max_height
        target_width = max(8, int(target_height * 2 * ratio))
    try:
        resample = _PILImage.Resampling.LANCZOS
    except AttributeError:
        resample = _PILImage.LANCZOS
    small = image.resize((target_width, target_height * 2), resample)
    pixels = small.load()
    result = []
    for y in range(0, target_height * 2, 2):
        chars = []
        bright = False
        for x in range(target_width):
            r, g, b, alpha = pixels[x, y]
            r2, g2, b2, alpha2 = pixels[x, y + 1]
            top = alpha > 40 and r + g + b > 60
            bottom = alpha2 > 40 and r2 + g2 + b2 > 60
            chars.append(block_char(top, bottom))
            bright = bright or (top and r + g + b > 200) or (bottom and r2 + g2 + b2 > 200)
        result.append(("".join(chars).rstrip(), bright))
    while result and not result[-1][0].strip():
        result.pop()
    return result, None
