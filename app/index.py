#!/usr/bin/env python3
"""
Dranesville File Archive — Card Selector + Macro Data Refinement Screensaver.

Step 1: Browse and select a file card (SPACE/ENTER to advance, S to select).
Step 2: The MDR screensaver launches, themed with the chosen card's location name.

Quit: Q or Ctrl+C at any point.
Optional artwork:
  python3 mdr_combined.py --image path/to/picture.png
  pip3 install pillow
"""
from __future__ import annotations

import argparse
import curses
import math
import os
import random
import time

from assets import *
from card_selector import run as run_card_selector
from config import load_config
from helpers import (center_text, digit_canvas, display_char,
                     image_to_terminal_lines, shift_lines, smoothstep)

# ══════════════════════════════════════════════════════════════════════════════
#  Card Selector — constants & data
# ══════════════════════════════════════════════════════════════════════════════

LOCATIONS = [
    "ADELAIDE", "ALLENTOWN", "ASTORIA", "BELLINGHAM", "BILLINGS", "BODA",
    "CAIRNS", "CHICXULUB", "CIELO", "COLD HARBOR", "COLEMAN", "CORK",
    "CULPEPPER", "DRANESVILLE", "EAU CLAIRE", "EMINENCE", "ERIE",
    "FORT DODGE", "GOLD COAST", "GRIMALDI", "GRIMSBY", "HEFEI", "HOMESTEAD",
    "HORSESHOE BEND", "JASPUR", "JESUP", "KINGSPORT", "LABRADOR", "LE MARS",
    "LEXINGTON", "LONGBRANCH", "LOVELAND", "LUCKNOW", "MERIDA", "MINSK",
    "MOLDE", "MONTAUK", "MOONBEAM", "MORIOKA", "NANNING", "NARVA", "OCULA",
    "PACOIMA", "RHODES", "SANTA MIRA", "SIENA", "SOPCHOPPY", "ST. PIERRE",
    "SUNSET PARK", "TAN AN", "TIMINS", "TODOS SANTOS", "TRINITY", "TUMWATER",
    "VILNIUS", "WARRNAMBOOL", "WAYNESBORO", "WELLINGTON", "YAKIMA", "ZURICH",
]

FONT_3H = {
    'A': [" ___ ", "|   |", "|---|"], 'B': [" ___ ", "|__]", "|__]"],
    'C': [" ___ ", "|    ", "|___ "], 'D': [" ___ ", "|   |", "|___|"],
    'E': [" ___ ", "|___ ", "|___ "], 'F': [" ___ ", "|___ ", "|    "],
    'G': [" ___ ", "| __ ", "|___|"], 'H': [" _ _ ", "|_|_|", "|   |"],
    'I': [" _ ", " | ", " _ "],       'J': ["  _ ", "  | ", "  | "],
    'K': [" _ _ ", "|_/_ ", r"| \_ "], 'L': ["     ", "|    ", "|___ "],
    'M': ["_ _ _", "| | |", "|   |"], 'N': ["_   _", r"| \ |", r"|  \|"],
    'O': [" ___ ", "|   |", "|___|"], 'P': [" ___ ", "|___|", "|    "],
    'Q': [" ___ ", "|   |", r"|_\_ |"], 'R': [" ___ ", "|___|", r"|  \_"],
    'S': [" ___ ", "[__  ", " ___]"], 'T': ["_____", "  |  ", "  |  "],
    'U': ["_   _", "|   |", "|___|"], 'V': ["_   _", "|   |", r" \/ "],
    'W': ["_ _ _", "|   |", "|_|_|"], 'X': ["_   _", r" \/ ", r" /\ "],
    'Y': ["_   _", r" \/ ", "  |  "], 'Z': [" ___ ", "   / ", "  /__"],
    ' ': ["   ", "   ", "   "],       '-': ["   ", "---", "   "],
    '.': ["   ", "   ", " . "],
}

C_BLACK = 1
C_DIM   = 2
C_NORMAL= 3
C_BRIGHT= 4
C_ULTRA = 5


def card_init_colors():
    curses.start_color()
    curses.use_default_colors()
    try:
        curses.init_pair(C_BLACK,  -1,  -1)
        curses.init_pair(C_DIM,    8,   -1)
        curses.init_pair(C_NORMAL, 37,  -1)
        curses.init_pair(C_BRIGHT, 51,  -1)
        curses.init_pair(C_ULTRA,  51,  -1)
    except Exception:
        pass


def render_big_text(text):
    lines = ["", "", ""]
    for char in text:
        glyph = FONT_3H.get(char, FONT_3H[' '])
        for i in range(3):
            lines[i] += glyph[i] + " "
    return [line.rstrip() for line in lines]


def safe_addstr_card(win, y, x, text, attr=0):
    try:
        max_y, max_x = win.getmaxyx()
        if 0 <= y < max_y and 0 <= x < max_x:
            win.addstr(y, x, text[: max_x - x], attr)
    except curses.error:
        pass


def draw_file_card_animation(win, location, index, total, flip_progress):
    win.erase()
    max_y, max_x = win.getmaxyx()

    big_lines = render_big_text(location)
    text_w = len(big_lines[0]) if big_lines[0] else 1

    card_w = 130
    if card_w > max_x - 4:
        card_w = max_x - 4
    if card_w % 2 != 0:
        card_w += 1

    target_half_h = 12

    center_x = max_x // 2
    center_y = max_y // 2
    start_x  = center_x - (card_w // 2)
    end_x    = start_x + card_w

    safe_addstr_card(win, center_y, start_x - 6, "[=O=]", curses.color_pair(C_DIM))
    safe_addstr_card(win, center_y, end_x + 1,   "[=O=]", curses.color_pair(C_DIM))

    current_half_h = int(target_half_h * flip_progress)

    half_w   = (card_w - 2) // 2
    tab_w    = 5
    top_tab_space = " " * ((card_w - tab_w) // 2)
    top_tab_text  = f"{top_tab_space}_____{top_tab_space}"
    top_tab_rim   = f"{top_tab_space}| {location[0].upper()} |{top_tab_space}"

    top_border   = ("." + "-" * ((card_w - tab_w) // 2 - 1) + "-+-" +
                    "-" * (tab_w - 2) + "-+-" + "-" * ((card_w - tab_w) // 2 - 1) + ".")
    folder_split = ("'" + "-" * (half_w - 2) + "-+-+-" + "-" * (half_w - 2) + "'")
    bottom_tab   = ("'" + "-" * (half_w - 2) + "-+-+-" + "-" * (half_w - 2) + "'")

    top_border   = top_border[:card_w]
    folder_split = folder_split[:card_w]
    bottom_tab   = bottom_tab[:card_w]

    if flip_progress > 0.7:
        main_attr = curses.color_pair(C_ULTRA)  | curses.A_BOLD
        text_attr = curses.color_pair(C_BRIGHT) | curses.A_BOLD
    elif flip_progress > 0.3:
        main_attr = curses.color_pair(C_BRIGHT) | curses.A_BOLD
        text_attr = curses.color_pair(C_NORMAL)
    else:
        main_attr = curses.color_pair(C_NORMAL)
        text_attr = curses.color_pair(C_DIM)

    y_top_border = center_y - current_half_h
    y_bottom_tab = center_y + current_half_h

    if current_half_h >= 6:
        safe_addstr_card(win, y_top_border - 2, start_x, top_tab_text, main_attr)
        safe_addstr_card(win, y_top_border - 1, start_x, top_tab_rim,  main_attr)

    safe_addstr_card(win, y_top_border, start_x, top_border, main_attr)
    for y in range(y_top_border + 1, center_y):
        safe_addstr_card(win, y, start_x, "|" + " " * (card_w - 2) + "|", main_attr)

    if current_half_h >= 6:
        start_y = center_y - 7
        txt_x   = center_x - (text_w // 2)
        for idx, line_str in enumerate(big_lines):
            target_y = start_y + idx
            if y_top_border < target_y < center_y:
                safe_addstr_card(win, target_y, txt_x, line_str, text_attr)

    safe_addstr_card(win, center_y, start_x, folder_split, main_attr)

    for y in range(center_y + 1, y_bottom_tab):
        safe_addstr_card(win, y, start_x, "|" + " " * (card_w - 2) + "|", main_attr)
    if current_half_h > 0:
        safe_addstr_card(win, y_bottom_tab, start_x, bottom_tab, main_attr)

    status_y    = max_y - 2
    status_text = (f"FILE {index + 1}/{total}  --  "
                   f"SPACE / \u2192 : NEXT   \u2190 : PREV   S / ENTER : SELECT   Q : QUIT")
    status_x = (max_x - len(status_text)) // 2
    safe_addstr_card(win, status_y, max(0, status_x), status_text,
                     curses.color_pair(C_DIM))

    win.refresh()


def run_card_selector(stdscr) -> str | None:
    """
    Display the file-card animation and return the selected location name,
    or None if the user quit without selecting.
    """
    card_init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(15)

    total         = len(LOCATIONS)
    index         = 0
    slide_dur     = 7
    hold_dur      = 90   # longer hold so user can read & decide
    frame_counter = 0

    while True:
        # ── animation progress ──────────────────────────────────────────────
        if frame_counter < slide_dur:
            t = frame_counter / slide_dur
            prog = 1.0 - (1.0 - t) ** 2
        elif frame_counter < slide_dur + hold_dur:
            prog = 1.0
        else:
            elapsed = frame_counter - slide_dur - hold_dur
            t = 1.0 - elapsed / slide_dur
            prog = t ** 2 if t > 0 else -0.1

            if prog < 0:
                index = (index + 1) % total
                frame_counter = 0
                prog = 0.0

        draw_file_card_animation(stdscr, LOCATIONS[index], index, total, prog)

        # ── input ───────────────────────────────────────────────────────────
        try:
            ch = stdscr.getch()
        except Exception:
            ch = -1

        if ch in (ord('q'), ord('Q')):
            return None

        # SELECT: Enter or S — wait for card to be fully open
        if ch in (ord('s'), ord('S'), 10, 13):
            if prog >= 0.95:          # card fully open — pick it now
                return LOCATIONS[index]
            else:                     # skip to fully open then select
                frame_counter = slide_dur  # jump to hold phase
                continue

        # NEXT
        if ch in (ord(' '), curses.KEY_RIGHT):
            frame_counter = slide_dur + hold_dur  # trigger close → advance

        # PREV
        if ch == curses.KEY_LEFT:
            index = (index - 1) % total
            frame_counter = 0

        frame_counter += 1
        time.sleep(0.01)


# ══════════════════════════════════════════════════════════════════════════════
#  MDR Screensaver — constants
# ══════════════════════════════════════════════════════════════════════════════

FPS          = 24
IDLE_MIN     = 1.2
IDLE_MAX     = 2.5

FRAME_REVEAL = 1
FRAME_WIGGLE = 50
SELECT_FRAMES = FRAME_REVEAL + FRAME_WIGGLE

DROP_OPEN  = 28
DROP_FALL  = 36
DROP_CLOSE = 16
DROP_FRAMES = DROP_OPEN + DROP_FALL + DROP_CLOSE

CELL_W = 11
CELL_H = 7
BIN_COUNT = 5
BIN_H  = 7
BIN_GAP = 2
LID_OPEN_ANGLE_DEG   = 130
LID_FLAP_LEN_CLOSED  = 0.50
LID_FLAP_LEN_OPEN    = 0.14

FALL_GHOST_TRAIL = (
    (0.28, "pair_dim"),
    (0.20, "pair_dim"),
    (0.12, "pair_member"),
    (0.05, "pair_ring"),
)
GRID_SKIP_BOTTOM = 2

BIN_NAMES = {1: "Woe", 2: "Frolic", 3: "Dread", 4: "Malice", 5: "Birr"}

WIGGLE_SPEED_MIN  = 0.45
WIGGLE_SPEED_MAX  = 0.75
WIGGLE_AMP_CENTER = 0.55
WIGGLE_AMP_RING   = 0.95
WIGGLE_AMP_MEMBER = 0.80
WIGGLE_EMA        = 0.20
WIGGLE_SHIFT      = 3.8

RGB_BG   = (0,  24,  36)
RGB_CYAN = (0, 195, 255)
RGB_DIM  = (0,  90, 120)
RGB_GLOW = (120, 230, 255)

SHADE_EMPTY = " "
SHADE_LOW   = "\u2591"
SHADE_MID   = "\u2592"
SHADE_FULL  = "\u2593"

_FULLWIDTH = "\uFF10\uFF11\uFF12\uFF13\uFF14\uFF15\uFF16\uFF17\uFF18\uFF19"

PHASE_IDLE   = "idle"
PHASE_SELECT = "select"
PHASE_DROP   = "drop"


# ══════════════════════════════════════════════════════════════════════════════
#  MDR helpers
# ══════════════════════════════════════════════════════════════════════════════

def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def center_text(text: str, width: int) -> str:
    t   = str(text)[:width]
    pad = (width - len(t)) // 2
    return (" " * pad + t + " " * width)[:width]


def display_char(digit: int, large: bool) -> str:
    key = int(digit) % 10
    return _FULLWIDTH[key] if large else str(key)


def digit_canvas(digit: int, large: bool, width: int, height: int) -> list[str]:
    height = max(1, height)
    blank  = " " * width
    ch     = display_char(digit, large)
    lines  = [center_text(ch, width)]
    out    = [blank] * height
    start  = (height - len(lines)) // 2
    for i, row in enumerate(lines):
        out[start + i] = row
    return out


def shift_lines(lines: list[str], row_delta: float, col_delta: float) -> list[str]:
    if not lines:
        return lines
    h = len(lines)
    w = len(lines[0])
    blank = " " * w
    rd = max(-(h - 1), min(h - 1, int(round(row_delta))))
    cd = max(-(w - 1), min(w - 1, int(round(col_delta))))
    out = [blank] * h
    for i, line in enumerate(lines):
        j = i + rd
        if 0 <= j < h:
            if cd > 0:
                out[j] = (" " * cd + line)[:w]
            elif cd < 0:
                out[j] = (line[-cd:] + " " * w)[:w]
            else:
                out[j] = line
    return out


def _block_char(top_on: bool, bottom_on: bool) -> str:
    if top_on and bottom_on: return "\u2588"
    if top_on:               return "\u2580"
    if bottom_on:            return "\u2584"
    return " "


# ══════════════════════════════════════════════════════════════════════════════
#  Image loading (optional Pillow)
# ══════════════════════════════════════════════════════════════════════════════

try:
    from PIL import Image as _PILImage
    _PILLOW = True
except ImportError:
    _PILLOW = False


def image_to_terminal_lines(path: str, max_width: int, max_height: int):
    if not _PILLOW:
        return [], "Pillow not installed — run: pip3 install pillow"
    if not path or not os.path.isfile(path):
        return [], "Image not found: %s" % path
    try:
        img = _PILImage.open(path).convert("RGBA")
    except Exception as exc:
        return [], "Could not open image: %s" % exc
    if max_width < 8 or max_height < 2:
        return [], None
    ratio = img.width / float(img.height)
    tw    = max_width
    th    = max(2, int(tw / ratio) // 2)
    if th > max_height:
        th = max_height
        tw = max(8, int(th * 2 * ratio))
    try:
        resample = _PILImage.Resampling.LANCZOS
    except AttributeError:
        resample = _PILImage.LANCZOS
    small  = img.resize((tw, th * 2), resample)
    pixels = small.load()
    lines  = []
    for y in range(0, th * 2, 2):
        chars  = []
        bright = False
        for x in range(tw):
            r,  g,  b,  a  = pixels[x, y]
            r2, g2, b2, a2 = pixels[x, y + 1] if y + 1 < th * 2 else (0, 0, 0, 0)
            top = a  > 40 and (r  + g  + b ) > 60
            bot = a2 > 40 and (r2 + g2 + b2) > 60
            chars.append(_block_char(top, bot))
            if top or bot:
                bright = bright or (r + g + b) > 200
        lines.append(("".join(chars).rstrip(), bright))
    while lines and lines[-1][0].strip() == "":
        lines.pop()
    return lines, None


# ══════════════════════════════════════════════════════════════════════════════
#  Cluster
# ══════════════════════════════════════════════════════════════════════════════

class Cluster:
    def __init__(self, center, ring, full, grid, target_bin):
        self.center     = center
        self.ring       = ring
        self.full       = full
        self.target_bin = target_bin
        cy, cx = center
        self.center_digit   = grid[cy][cx]
        self.ring_digits    = {pos: grid[pos[0]][pos[1]] for pos in ring}
        self.swallow_digits = [grid[y][x] for y, x in sorted(full)]

        self._phase  = {pos: random.random() * math.pi * 2 for pos in full}
        self._speed  = {pos: WIGGLE_SPEED_MIN + random.random() *
                             (WIGGLE_SPEED_MAX - WIGGLE_SPEED_MIN) for pos in full}
        self._smooth = {pos: {"dx": 0.0, "dy": 0.0} for pos in full}

        self.visible: set = {center}
        self.phase        = PHASE_SELECT
        self.frame_count  = 0
        self.anim_tick    = 0

    def update_visible(self):
        self.visible = set(self.full)

    def update_wiggle(self, should_float: bool):
        if not should_float:
            return
        cy, cx = self.center
        t = self.anim_tick / float(FPS)
        for pos in self.full:
            phase = self._phase[pos]
            speed = self._speed[pos]
            pulse = (math.sin(t * speed + phase) + 1.0) * 0.5
            if pos == self.center:
                angle = phase + t * speed * 0.65
                tdx   = math.cos(angle) * WIGGLE_AMP_CENTER * pulse
                tdy   = math.sin(angle) * WIGGLE_AMP_CENTER * pulse
            else:
                dy_d = float(pos[0] - cy)
                dx_d = float(pos[1] - cx)
                dist = math.sqrt(dy_d * dy_d + dx_d * dx_d) or 1.0
                amp  = WIGGLE_AMP_RING if pos in self.ring else WIGGLE_AMP_MEMBER
                push = pulse * amp
                tdx  = (dx_d / dist) * push
                tdy  = (dy_d / dist) * push
            s = self._smooth[pos]
            s["dx"] = s["dx"] * (1.0 - WIGGLE_EMA) + tdx * WIGGLE_EMA
            s["dy"] = s["dy"] * (1.0 - WIGGLE_EMA) + tdy * WIGGLE_EMA

    def wiggle_offset(self, pos):
        s = self._smooth.get(pos, {"dx": 0.0, "dy": 0.0})
        return s["dy"], s["dx"]

    def tier(self, pos):
        if pos not in self.visible:
            return None
        if pos == self.center:
            return "center"
        if pos in self.ring:
            return "ring"
        return "member"

    def drop_stage(self):
        f = self.frame_count
        if f < DROP_OPEN:
            return "open", smoothstep(f / DROP_OPEN)
        f2 = f - DROP_OPEN
        if f2 < DROP_FALL:
            return "fall", f2 / float(DROP_FALL)
        f3 = f2 - DROP_FALL
        return "close", smoothstep(f3 / DROP_CLOSE)

    @property
    def drop_done(self):
        return self.phase == PHASE_DROP and self.frame_count >= DROP_FRAMES

    def fall_progress(self):
        if self.phase != PHASE_DROP or self.frame_count < DROP_OPEN:
            return 0.0
        f2 = self.frame_count - DROP_OPEN
        if f2 >= DROP_FALL:
            return 1.0
        return smoothstep(f2 / float(DROP_FALL))

    def grid_hidden_positions(self):
        if self.phase != PHASE_DROP or self.frame_count < DROP_OPEN:
            return set()
        prog = self.fall_progress()
        if prog < 0.08:
            return set()
        if prog < 0.32:
            return {self.center}
        return set(self.full)

    def tick(self, select_done: bool):
        self.frame_count += 1
        self.anim_tick   += 1
        if self.phase == PHASE_SELECT:
            self.update_visible()
            if select_done:
                self.phase       = PHASE_DROP
                self.frame_count = 0


# ══════════════════════════════════════════════════════════════════════════════
#  Curses theme
# ══════════════════════════════════════════════════════════════════════════════

def rgb_to_curses(r, g, b):
    return (int(r / 255 * 1000), int(g / 255 * 1000), int(b / 255 * 1000))


def setup_theme() -> dict:
    theme: dict = {"ok": False}
    if not curses.has_colors():
        return theme
    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    if curses.can_change_color() and curses.COLORS >= 16:
        curses.init_color(20, *rgb_to_curses(*RGB_BG))
        curses.init_color(21, *rgb_to_curses(*RGB_CYAN))
        curses.init_color(22, *rgb_to_curses(*RGB_DIM))
        curses.init_color(23, *rgb_to_curses(*RGB_GLOW))
        bg, cyan, dim, glow = 20, 21, 22, 23
    else:
        bg   = curses.COLOR_BLACK
        cyan = curses.COLOR_CYAN
        dim  = curses.COLOR_BLUE
        glow = curses.COLOR_WHITE

    curses.init_pair(1, cyan, bg)
    curses.init_pair(2, dim,  bg)
    curses.init_pair(3, glow, bg)
    B = curses.A_BOLD
    theme.update({
        "ok":               True,
        "pair_dim":         curses.color_pair(2),
        "pair_normal":      curses.color_pair(1) | B,
        "pair_member":      curses.color_pair(1) | B,
        "pair_ring":        curses.color_pair(1) | B,
        "pair_center":      curses.color_pair(3) | B,
        "pair_header":      curses.color_pair(1) | B,
        "pair_bin":         curses.color_pair(2),
        "pair_bin_fill":    curses.color_pair(1),
        "pair_bin_shade":        curses.color_pair(1),
        "pair_bin_shade_dim":    curses.color_pair(2),
        "pair_bin_open":         curses.color_pair(3),
        "pair_bin_active":       curses.color_pair(3) | B,
        "pair_swallow":          curses.color_pair(1) | B,
    })
    return theme


# ══════════════════════════════════════════════════════════════════════════════
#  MDR helpers
# ══════════════════════════════════════════════════════════════════════════════

def init_bins() -> dict:
    starts = [1, 5, 0, 0, 3]
    return {i: {"progress": starts[i - 1], "drops": 0, "digits": []}
            for i in range(1, BIN_COUNT + 1)}


def init_grid(cols: int, rows: int) -> list:
    return [[random.randint(0, 9) for _ in range(cols)] for _ in range(rows)]


def build_cluster(cols, rows, exclude):
    candidates = [(r, c) for r in range(rows) for c in range(cols)
                  if (r, c) not in exclude]
    if not candidates:
        return None
    center = random.choice(candidates)
    cy, cx = center
    ring   = set()
    full   = {center}
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < rows and 0 <= nx < cols and (ny, nx) not in exclude:
            ring.add((ny, nx))
            full.add((ny, nx))
    target   = random.randint(4, min(8, cols * rows - len(exclude)))
    frontier = list(ring)
    while len(full) < target and frontier:
        cell = random.choice(frontier)
        y, x = cell
        grown = False
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if (0 <= ny < rows and 0 <= nx < cols
                    and (ny, nx) not in full and (ny, nx) not in exclude):
                full.add((ny, nx))
                frontier.append((ny, nx))
                grown = True
                break
        if not grown and cell in frontier:
            frontier.remove(cell)
    return center, ring, full


# ══════════════════════════════════════════════════════════════════════════════
#  RefinementScreensaver  — now carries a location_name for the header
# ══════════════════════════════════════════════════════════════════════════════

class RefinementScreensaver:

    def __init__(self, stdscr, theme: dict,
                 location_name: str = "DRANESVILLE",
                 image_path: str | None = None):
        self.stdscr        = stdscr
        self.theme         = theme
        self.image_path    = image_path
        self.location_name = location_name   # ← from card selector

        self.bins           = init_bins()
        self.total_progress = 3
        self.grid: list     = []
        self.cols           = 0
        self.rows           = 0
        self.grid_top       = 3            # +1 row to make room for location line
        self.grid_left      = 0

        self.cluster        = None
        self.phase          = PHASE_IDLE
        self.phase_until    = 0.0
        self.dirty_cells: set = set()

        self.bin_w  = 10
        self.bin_y  = 0
        self.height = 24
        self.width  = 80

        self.art_lines  = []
        self.art_error  = None
        self.art_h      = 0
        self._art_cache = None

    # ── util ─────────────────────────────────────────────────────────────────

    def attr(self, name: str) -> int:
        if self.theme.get("ok"):
            return self.theme.get(name, curses.A_NORMAL)
        fallback = {
            "pair_center":     curses.A_REVERSE | curses.A_BOLD,
            "pair_ring":       curses.A_BOLD,
            "pair_member":     curses.A_BOLD,
            "pair_bin_active": curses.A_REVERSE | curses.A_BOLD,
        }
        return fallback.get(name, curses.A_DIM)

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0):
        if y < 0 or y >= self.height or x >= self.width:
            return
        clip = text[: max(0, self.width - x - 1)]
        if not clip:
            return
        try:
            self.stdscr.addstr(y, x, clip, attr)
        except curses.error:
            pass

    def draw_glyph_lines(self, y0, x0, lines, digit_attr):
        pad_attr = self.attr("pair_dim")
        for i, line in enumerate(lines):
            for j, ch in enumerate(line):
                a = digit_attr if ch != " " else pad_attr
                self.safe_addstr(y0 + i, x0 + j, ch, a)

    # ── resize ───────────────────────────────────────────────────────────────

    def resize(self, height: int, width: int):
        self.height = height
        self.width  = width
        name_w  = max(len(n) for n in BIN_NAMES.values()) + 4
        self.bin_w = max(name_w,
                         (width - (BIN_COUNT - 1) * BIN_GAP - 2) // BIN_COUNT)
        self.bin_y = height - BIN_H - 2
        self._rebuild_art()
        usable_h = max(CELL_H, self.bin_y - self.grid_top - 2)
        usable_w = max(CELL_W, width - 1)
        self.cols = max(4, usable_w // CELL_W)
        self.rows = max(2, usable_h // CELL_H - GRID_SKIP_BOTTOM)
        self.grid = init_grid(self.cols, self.rows)
        self.cluster = None
        self._set_idle()

    # ── image art ────────────────────────────────────────────────────────────

    def _rebuild_art(self):
        if not self.image_path:
            self.art_lines = []
            self.art_error = None
            self.art_h     = 0
            self.grid_top  = 3
            return
        key = (self.image_path, self.width, self.bin_y)
        if key == self._art_cache:
            self.grid_top = 3 + (self.art_h + 1 if self.art_h else 0)
            return
        max_h          = max(4, self.bin_y - 10)
        lines, err     = image_to_terminal_lines(self.image_path, self.width - 2, max_h)
        self.art_lines = lines
        self.art_error = err
        self.art_h     = len(lines)
        self._art_cache = key
        self.grid_top  = 3 + (self.art_h + 1 if self.art_h else 0)

    # ── phase management ─────────────────────────────────────────────────────

    def _set_idle(self):
        self.phase       = PHASE_IDLE
        self.phase_until = time.time() + random.uniform(IDLE_MIN, IDLE_MAX)

    def _start_selection(self):
        result = build_cluster(self.cols, self.rows, set())
        if result is None:
            self._set_idle()
            return
        center, ring, full = result
        target_bin = self._pick_bin(set())
        self.cluster = Cluster(center, ring, full, self.grid, target_bin)
        self.phase   = PHASE_SELECT
        self.phase_until = time.time() + SELECT_FRAMES / FPS

    def _pick_bin(self, exclude_bins: set) -> int:
        scores = sorted(
            (self.bins[i]["progress"], self.bins[i]["drops"], i)
            for i in range(1, BIN_COUNT + 1)
            if i not in exclude_bins
        )
        return random.choice(scores[:2])[2]

    def _recompute_progress(self):
        self.total_progress = min(
            100,
            sum(self.bins[i]["progress"] for i in range(1, BIN_COUNT + 1)) // BIN_COUNT
        )

    def _tick_phase(self):
        now = time.time()
        if self.phase == PHASE_IDLE:
            if now >= self.phase_until:
                self._start_selection()
            return
        select_done = now >= self.phase_until
        cl = self.cluster
        if cl is None:
            self._set_idle()
            return
        cl.tick(select_done)
        if self.phase == PHASE_SELECT and select_done:
            self.phase = PHASE_DROP
        if cl.phase == PHASE_DROP and cl.drop_done:
            self._finish_drop(cl)
            self.cluster = None
            self._set_idle()

    def _finish_drop(self, cl: Cluster):
        b = self.bins[cl.target_bin]
        b["drops"] += 1
        gain = min(12, len(cl.full) + random.randint(1, 3))
        b["progress"] = min(99, b["progress"] + gain)
        for y, x in cl.full:
            self.grid[y][x] = random.randint(0, 9)
            self.dirty_cells.add((y, x))
        self._recompute_progress()

    # ── drawing ──────────────────────────────────────────────────────────────

    def _fill_background(self):
        try:
            self.stdscr.bkgd(" ", self.attr("pair_dim"))
        except curses.error:
            pass

    def _tier_attr(self, tier: str) -> int:
        return self.attr({
            "center": "pair_center",
            "ring":   "pair_ring",
            "member": "pair_member",
        }.get(tier, "pair_dim"))

    def _draw_header(self):
        """
        Two-line header:
          Row 0 — location name (left)  |  progress (right)
          Row 1 — separator bar with "Refinement Worker" centred
        """
        h_attr  = self.attr("pair_header")
        dim_attr = self.attr("pair_dim")

        # Row 0: location name + progress
        loc_label = f"FILE: {self.location_name}"
        prog_str  = "%d%% Complete" % self.total_progress
        self.safe_addstr(0, 0, loc_label, h_attr)
        self.safe_addstr(0, max(0, self.width - len(prog_str) - 1),
                         prog_str, h_attr)

        # Row 1: separator + worker label centred
        sep  = "\u2500" * (self.width - 1)
        lbl  = " Refinement Worker "
        mid  = (self.width - len(lbl)) // 2
        self.safe_addstr(1, 0, sep, dim_attr)
        self.safe_addstr(1, mid, lbl, h_attr)

    def _draw_art(self):
        if self.art_error:
            self.safe_addstr(2, 0, self.art_error[: self.width - 1],
                             self.attr("pair_dim"))
            return
        for i, (text, bright) in enumerate(self.art_lines):
            if not text:
                continue
            a = self.attr("pair_normal") if bright else self.attr("pair_dim")
            x = max(0, (self.width - len(text)) // 2)
            self.safe_addstr(3 + i, x, text, a)

    def _draw_grid(self):
        hidden = set()
        cl = self.cluster
        if cl:
            hidden.update(cl.grid_hidden_positions())
        pos_cluster = {}
        if cl:
            for pos in cl.full:
                pos_cluster[pos] = cl

        for gy in range(self.rows):
            for gx in range(self.cols):
                py0 = self.grid_top + gy * CELL_H
                px0 = self.grid_left + gx * CELL_W
                if py0 + CELL_H > self.bin_y - 2:
                    continue
                pos = (gy, gx)
                if pos in hidden:
                    continue
                cl   = pos_cluster.get(pos)
                tier = cl.tier(pos) if cl else None
                digit = self.grid[gy][gx]
                large = tier in ("center", "ring", "member")
                lines = digit_canvas(digit, large, CELL_W, CELL_H)
                if large and cl:
                    fy, fx = cl.wiggle_offset(pos)
                    if fy or fx:
                        lines = shift_lines(lines, fy * WIGGLE_SHIFT, fx * WIGGLE_SHIFT)
                    self.draw_glyph_lines(py0, px0, lines, self._tier_attr(tier))
                else:
                    for i, line in enumerate(lines):
                        self.safe_addstr(py0 + i, px0, line, self.attr("pair_dim"))

    # ── bin rendering ─────────────────────────────────────────────────────────

    def _bin_x(self, index: int) -> int:
        return 1 + (index - 1) * (self.bin_w + BIN_GAP)

    def _shade_for_row(self, progress, row_index, body_rows):
        pos      = body_rows.index(row_index)
        from_bot = len(body_rows) - 1 - pos
        fill_h   = (progress / 100.0) * len(body_rows)
        if from_bot + 1 <= fill_h:
            shade = (SHADE_FULL if progress >= 66 else
                     SHADE_MID  if progress >= 33 else SHADE_LOW)
            return shade, "pair_bin_shade"
        if from_bot < fill_h:
            return SHADE_LOW, "pair_bin_shade_dim"
        return SHADE_EMPTY, "pair_bin_shade_dim"

    def _lid_open_t(self, stage, amount):
        if stage == "open":  return smoothstep(amount)
        if stage == "fall":  return 1.0
        return 1.0 - smoothstep(amount)

    def _swing_flap_char(self, dx, dy, side):
        if dy == 0: return "-"
        if dx == 0: return "|"
        if side == "left":  return "\\" if dy < 0 else "/"
        return "/" if dy < 0 else "\\"

    def _draw_swing_flap(self, hx, hy, t, closed_len, open_len, wall_a, side):
        if closed_len < 1:
            return
        ot     = smoothstep(t)
        length = max(1, int(closed_len + (open_len - closed_len) * ot))
        open_rad = math.radians(LID_OPEN_ANGLE_DEG)
        if side == "left":
            angle = -ot * open_rad
        else:
            angle = math.pi + ot * open_rad

        if ot < 0.05:
            if side == "left":
                for i in range(1, length + 1):
                    self.safe_addstr(hy, hx + i, "-", wall_a)
            else:
                for i in range(1, length + 1):
                    self.safe_addstr(hy, hx - i, "-", wall_a)
            if 0 <= hy < self.height - 1 and 0 <= hx < self.width:
                self.safe_addstr(hy, hx, "+", wall_a)
            return

        h_rem = max(0, int(round(closed_len * (1.0 - ot) * 0.6)))
        if side == "left":
            for i in range(1, h_rem + 1):
                self.safe_addstr(hy, hx + i, "-", wall_a)
        else:
            for i in range(1, h_rem + 1):
                self.safe_addstr(hy, hx - i, "-", wall_a)

        tip_x = hx + int(round(length * math.cos(angle)))
        tip_y = hy + int(round(length * math.sin(angle)))
        x0, y0 = hx, hy
        x1, y1 = tip_x, tip_y
        dx_abs = abs(x1 - x0); dy_abs = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx_abs - dy_abs
        x, y = x0, y0
        prev_x, prev_y = None, None

        while True:
            if (x, y) != (hx, hy):
                if prev_x is not None:
                    ch = self._swing_flap_char(x - prev_x, y - prev_y, side)
                else:
                    ch = self._swing_flap_char(x1 - hx, y1 - hy, side)
                if 0 <= y < self.height - 1 and 0 <= x < self.width:
                    self.safe_addstr(y, x, ch, wall_a)
            if x == x1 and y == y1:
                break
            prev_x, prev_y = x, y
            e2 = 2 * err
            if e2 > -dy_abs:
                err -= dy_abs; x += sx
            if e2 < dx_abs:
                err += dx_abs; y += sy

        if 0 <= hy < self.height - 1 and 0 <= hx < self.width:
            self.safe_addstr(hy, hx, "+", wall_a)

    def _draw_dual_lid_flaps(self, x0, inner, t, wall_a):
        if self.bin_w < 3:
            return
        hy  = self.bin_y + 1
        hlx = x0
        hrx = x0 + self.bin_w - 1
        span = max(1, self.bin_w - 1)
        closed_len = max(2, int(span * LID_FLAP_LEN_CLOSED))
        open_len   = max(1, int(span * LID_FLAP_LEN_OPEN))
        self._draw_swing_flap(hlx, hy, t, closed_len, open_len, wall_a, "left")
        self._draw_swing_flap(hrx, hy, t, closed_len, open_len, wall_a, "right")

    def _draw_bin_top_open(self, bin_id, x0, stage, amount, active=True):
        inner    = max(1, self.bin_w - 2)
        lx, rx   = x0, x0 + self.bin_w - 1
        wall_a   = self.attr("pair_bin_active" if active else "pair_bin")
        open_a   = self.attr("pair_bin_open")
        body_rows = list(range(2, BIN_H - 1))
        mouth_rows = len(body_rows)
        t        = self._lid_open_t(stage, amount)
        mouth_t  = smoothstep(t)
        open_rows = int(round(mouth_t * mouth_rows))

        for row in range(1, BIN_H):
            py = self.bin_y + row
            if py >= self.height - 1:
                break
            if row not in body_rows:
                continue
            self.safe_addstr(py, lx, "|", wall_a)
            self.safe_addstr(py, rx, "|", wall_a)
            idx = body_rows.index(row)
            if idx < open_rows:
                self.safe_addstr(py, x0 + 1, " " * inner, open_a)
            else:
                ch, an = self._shade_for_row(
                    self.bins[bin_id]["progress"], row, body_rows)
                fill = (ch * inner)[:inner]
                self.safe_addstr(py, x0 + 1, fill, self.attr(an))
        self._draw_dual_lid_flaps(x0, inner, t, wall_a)

    def _fall_digit(self, cl):
        cy, cx = cl.center
        return int(self.grid[cy][cx]) % 10

    def _fall_glyph_layout(self, cl, x0, fall_t):
        glyph_w = min(CELL_W, max(3, self.bin_w - 2))
        glyph_h = min(5, CELL_H)
        cy, cx  = cl.center
        start_y = self.grid_top + cy * CELL_H + (CELL_H - glyph_h) // 2
        start_x = self.grid_left + cx * CELL_W + (CELL_W - glyph_w) // 2
        inner   = max(1, self.bin_w - 2)
        end_y   = self.bin_y + 2 + max(0, (BIN_H - 4 - glyph_h) // 2)
        end_x   = x0 + 1 + (inner - glyph_w) // 2
        t       = smoothstep(fall_t)
        cur_y   = start_y + (end_y - start_y) * t
        cur_x   = start_x + (end_x - start_x) * t
        return glyph_w, glyph_h, cur_y, cur_x, start_y, start_x, end_y, end_x

    def _draw_bin_fall(self, cl, x0, fall_progress):
        digit    = self._fall_digit(cl)
        ch_ascii = str(digit)
        gw, gh, cur_y, cur_x, _, _, _, _ = self._fall_glyph_layout(cl, x0, fall_progress)
        lines  = digit_canvas(digit, True, gw, gh)
        bright = self.attr("pair_swallow")
        ghost_y = lambda py: py + max(0, gh // 2)
        ghost_x = lambda px: px + max(0, (gw - 1) // 2)

        for lag, attr_name in FALL_GHOST_TRAIL:
            ghost_t = fall_progress - lag
            if ghost_t < 0.04:
                continue
            _, _, gy, gx, _, _, _, _ = self._fall_glyph_layout(
                cl, x0, min(1.0, ghost_t))
            giy, gix = int(round(gy)), int(round(gx))
            if giy == int(round(cur_y)) and gix == int(round(cur_x)):
                continue
            self.safe_addstr(ghost_y(giy), ghost_x(gix), ch_ascii, self.attr(attr_name))

        self.draw_glyph_lines(int(round(cur_y)), int(round(cur_x)), lines, bright)

    def _draw_bin(self, bin_id, x0, active, stage, amount):
        inner = max(1, self.bin_w - 2)
        if active:
            self._draw_bin_top_open(bin_id, x0, stage, amount, active=True)
        else:
            self._draw_bin_top_open(bin_id, x0, "close", 1.0, active=False)
        self.safe_addstr(
            self.bin_y, x0,
            center_text("%3d%%" % self.bins[bin_id]["progress"], self.bin_w),
            self.attr("pair_bin_fill"))
        label_a = self.attr("pair_bin_active") if active else self.attr("pair_bin")
        self.safe_addstr(
            self.bin_y + BIN_H - 1, x0 + 1,
            center_text(BIN_NAMES[bin_id], inner)[:inner], label_a)

    def _draw_bins(self):
        active_bins = {}
        cl = self.cluster
        if cl and cl.phase == PHASE_DROP:
            stage, amount = cl.drop_stage()
            active_bins[cl.target_bin] = (stage, amount, cl)
        for i in range(1, BIN_COUNT + 1):
            x0     = self._bin_x(i)
            active = i in active_bins
            if active:
                stage, amount, cl = active_bins[i]
                self._draw_bin(i, x0, True, stage, amount)
                if stage == "fall":
                    self._draw_bin_fall(cl, x0, amount)
            else:
                self._draw_bin(i, x0, False, "close", 1.0)

    def _draw_footer(self):
        cl = self.cluster
        if cl and cl.phase == PHASE_DROP:
            status = "refining -> %s" % BIN_NAMES[cl.target_bin]
        elif self.phase == PHASE_SELECT:
            status = "cluster refining"
        else:
            status = "listening to the field"
        self.safe_addstr(
            self.height - 1, 0,
            ("%s  |  q quit" % status)[: self.width - 1],
            self.attr("pair_dim"))

    # ── main frame ────────────────────────────────────────────────────────────

    def frame(self):
        if self.phase == PHASE_IDLE and random.random() < 0.04:
            y, x = random.randrange(self.rows), random.randrange(self.cols)
            self.grid[y][x] = random.randint(0, 9)
            self.dirty_cells.add((y, x))
        float_on = self.phase == PHASE_SELECT
        if self.cluster:
            self.cluster.update_wiggle(float_on)
        self._tick_phase()
        self.stdscr.erase()
        self._fill_background()
        self._draw_header()
        self._draw_art()
        self._draw_grid()
        self._draw_bins()
        self._draw_footer()
        self.stdscr.refresh()
        self.dirty_cells.clear()


# Use the extracted modules at runtime while the refinement renderer remains
# in this file during the migration.
from card_selector import run as run_card_selector
from helpers import (center_text, digit_canvas, image_to_terminal_lines,
                     shift_lines, smoothstep)


# ══════════════════════════════════════════════════════════════════════════════
#  Entry points
# ══════════════════════════════════════════════════════════════════════════════

def run_screensaver(stdscr, location_name: str, image_path: str | None = None):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    theme   = setup_theme()
    app     = RefinementScreensaver(stdscr, theme,
                                    location_name=location_name,
                                    image_path=image_path)
    last_sz = (0, 0)
    while True:
        h, w = stdscr.getmaxyx()
        if (h, w) != last_sz:
            last_sz = (h, w)
            app.resize(h, w)
        if stdscr.getch() in (ord("q"), ord("Q"), 27):
            break
        app.frame()
        time.sleep(1.0 / FPS)


def run_combined(stdscr, image_path: str | None = None):
    """Full flow: card selector → screensaver."""
    # Phase 1 – card selector
    location = run_card_selector(stdscr)
    if location is None:
        return   # user quit during selection

    # Brief flash before launching screensaver
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    msg  = f"  Loading file: {location}  "
    try:
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.A_REVERSE)
    except curses.error:
        pass
    stdscr.refresh()
    time.sleep(0.8)

    # Phase 2 – MDR screensaver themed to the chosen location
    run_screensaver(stdscr, location_name=location, image_path=image_path)


def main():
    parser = argparse.ArgumentParser(
        description="Dranesville File Archive — card selector + MDR screensaver")
    parser.add_argument("--config", metavar="PATH",
                        help="JSON configuration file (default: app/config.json)")
    parser.add_argument("--image", "-i", metavar="PATH",
                        help="PNG/JPG/WebP to render above the grid "
                             "(requires: pip3 install pillow)")
    args = parser.parse_args()
    settings = load_config(args.config)
    global FPS, IDLE_MIN, IDLE_MAX
    FPS = settings["fps"]
    IDLE_MIN = settings["idle_min"]
    IDLE_MAX = settings["idle_max"]
    image_path = args.image if args.image is not None else settings["image"]
    curses.wrapper(lambda s: run_combined(s, image_path=image_path))


if __name__ == "__main__":
    main()