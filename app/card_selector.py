"""Interactive card selection phase."""

import curses
import time

try:
    from .assets import C_BRIGHT, C_DIM, C_NORMAL, C_ULTRA, FONT_3H, LOCATIONS
except ImportError:
    from assets import C_BRIGHT, C_DIM, C_NORMAL, C_ULTRA, FONT_3H, LOCATIONS


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    try:
        curses.init_pair(C_DIM, 8, -1)
        curses.init_pair(C_NORMAL, 37, -1)
        curses.init_pair(C_BRIGHT, 51, -1)
        curses.init_pair(C_ULTRA, 51, -1)
    except curses.error:
        pass


def render_big_text(text):
    lines = ["", "", ""]
    for char in text:
        glyph = FONT_3H.get(char, FONT_3H[" "])
        for index in range(3):
            lines[index] += glyph[index] + " "
    return [line.rstrip() for line in lines]


def safe_addstr(win, y, x, text, attr=0):
    try:
        max_y, max_x = win.getmaxyx()
        if 0 <= y < max_y and 0 <= x < max_x:
            win.addstr(y, x, text[:max_x - x], attr)
    except curses.error:
        pass


def draw_card(win, location, index, total, flip_progress):
    win.erase()
    max_y, max_x = win.getmaxyx()
    big_lines = render_big_text(location)
    text_width = len(big_lines[0]) if big_lines[0] else 1
    card_width = min(130, max_x - 4)
    if card_width % 2:
        card_width += 1
    center_x, center_y = max_x // 2, max_y // 2
    start_x = center_x - card_width // 2
    end_x = start_x + card_width
    safe_addstr(win, center_y, start_x - 6, "[=O=]", curses.color_pair(C_DIM))
    safe_addstr(win, center_y, end_x + 1, "[=O=]", curses.color_pair(C_DIM))
    half_height = int(12 * flip_progress)
    half_width = (card_width - 2) // 2
    tab_width = 5
    tab_space = " " * ((card_width - tab_width) // 2)
    tab_text = f"{tab_space}_____{tab_space}"
    tab_rim = f"{tab_space}| {location[0].upper()} |{tab_space}"
    top_border = ("." + "-" * ((card_width - tab_width) // 2 - 1) + "-+-"
                  + "-" * (tab_width - 2) + "-+-"
                  + "-" * ((card_width - tab_width) // 2 - 1) + ".")[:card_width]
    split = ("'" + "-" * (half_width - 2) + "-+-+-"
             + "-" * (half_width - 2) + "'")[:card_width]
    main_attr, text_attr = (
        (curses.color_pair(C_ULTRA) | curses.A_BOLD, curses.color_pair(C_BRIGHT) | curses.A_BOLD)
        if flip_progress > 0.7 else
        (curses.color_pair(C_BRIGHT) | curses.A_BOLD, curses.color_pair(C_NORMAL))
        if flip_progress > 0.3 else
        (curses.color_pair(C_NORMAL), curses.color_pair(C_DIM))
    )
    top_y, bottom_y = center_y - half_height, center_y + half_height
    if half_height >= 6:
        safe_addstr(win, top_y - 2, start_x, tab_text, main_attr)
        safe_addstr(win, top_y - 1, start_x, tab_rim, main_attr)
    safe_addstr(win, top_y, start_x, top_border, main_attr)
    for y in range(top_y + 1, center_y):
        safe_addstr(win, y, start_x, "|" + " " * (card_width - 2) + "|", main_attr)
    if half_height >= 6:
        text_x = center_x - text_width // 2
        for offset, line in enumerate(big_lines):
            target_y = center_y - 7 + offset
            if top_y < target_y < center_y:
                safe_addstr(win, target_y, text_x, line, text_attr)
    safe_addstr(win, center_y, start_x, split, main_attr)
    for y in range(center_y + 1, bottom_y):
        safe_addstr(win, y, start_x, "|" + " " * (card_width - 2) + "|", main_attr)
    if half_height > 0:
        safe_addstr(win, bottom_y, start_x, split, main_attr)
    status = (f"FILE {index + 1}/{total}  --  SPACE / -> : NEXT   "
              "<- : PREV   S / ENTER : SELECT   Q : QUIT")
    safe_addstr(win, max_y - 2, max(0, (max_x - len(status)) // 2), status,
                curses.color_pair(C_DIM))
    win.refresh()


def run(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(15)
    total, index = len(LOCATIONS), 0
    slide_duration, hold_duration, frame = 7, 90, 0
    while True:
        if frame < slide_duration:
            progress = 1.0 - (1.0 - frame / slide_duration) ** 2
        elif frame < slide_duration + hold_duration:
            progress = 1.0
        else:
            elapsed = frame - slide_duration - hold_duration
            remaining = 1.0 - elapsed / slide_duration
            progress = remaining ** 2 if remaining > 0 else -0.1
            if progress < 0:
                index = (index + 1) % total
                frame, progress = 0, 0.0
        draw_card(stdscr, LOCATIONS[index], index, total, progress)
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1
        if key in (ord("q"), ord("Q")):
            return None
        if key in (ord("s"), ord("S"), 10, 13):
            if progress >= 0.95:
                return LOCATIONS[index]
            frame = slide_duration
            continue
        if key in (ord(" "), curses.KEY_RIGHT):
            frame = slide_duration + hold_duration
        elif key == curses.KEY_LEFT:
            index = (index - 1) % total
            frame = 0
        frame += 1
        time.sleep(0.01)
