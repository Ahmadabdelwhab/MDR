"""Static data and configuration for the card selector and screensaver."""

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
    'I': [" _ ", " | ", " _ "], 'J': ["  _ ", "  | ", "  | "],
    'K': [" _ _ ", "|_/_ ", r"| \_ "], 'L': ["     ", "|    ", "|___ "],
    'M': ["_ _ _", "| | |", "|   |"], 'N': ["_   _", r"| \ |", r"|  \|"],
    'O': [" ___ ", "|   |", "|___|"], 'P': [" ___ ", "|___|", "|    "],
    'Q': [" ___ ", "|   |", r"|_\_ |"], 'R': [" ___ ", "|___|", r"|  \_"],
    'S': [" ___ ", "[__  ", " ___]"], 'T': ["_____", "  |  ", "  |  "],
    'U': ["_   _", "|   |", "|___|"], 'V': ["_   _", "|   |", r" \/ "],
    'W': ["_ _ _", "|   |", "|_|_|"], 'X': ["_   _", r" \/ ", r" / \ "],
    'Y': ["_   _", r" \/ ", "  |  "], 'Z': [" ___ ", "   / ", "  /__"],
    ' ': ["   ", "   ", "   "], '-': ["   ", "---", "   "],
    '.': ["   ", "   ", " . "],
}

C_BLACK = 1
C_DIM = 2
C_NORMAL = 3
C_BRIGHT = 4
C_ULTRA = 5

FPS = 24
IDLE_MIN = 1.2
IDLE_MAX = 2.5
FRAME_REVEAL = 1
FRAME_WIGGLE = 50
SELECT_FRAMES = FRAME_REVEAL + FRAME_WIGGLE
DROP_OPEN = 28
DROP_FALL = 36
DROP_CLOSE = 16
DROP_FRAMES = DROP_OPEN + DROP_FALL + DROP_CLOSE
CELL_W = 11
CELL_H = 7
BIN_COUNT = 4
BIN_H = 7
BIN_GAP = 2
LID_OPEN_ANGLE_DEG = 130
LID_FLAP_LEN_CLOSED = 0.50
LID_FLAP_LEN_OPEN = 0.14
FALL_GHOST_TRAIL = ((0.28, "pair_dim"), (0.20, "pair_dim"),
                    (0.12, "pair_member"), (0.05, "pair_ring"))
GRID_SKIP_BOTTOM = 2
BIN_NAMES = {1: "Woe", 2: "Frolic", 3: "Dread", 4: "Malice"}
WIGGLE_SPEED_MIN = 0.45
WIGGLE_SPEED_MAX = 0.75
WIGGLE_AMP_CENTER = 0.55
WIGGLE_AMP_RING = 0.95
WIGGLE_AMP_MEMBER = 0.80
WIGGLE_EMA = 0.20
WIGGLE_SHIFT = 3.8
RGB_BG = (0, 24, 36)
RGB_CYAN = (0, 195, 255)
RGB_DIM = (0, 90, 120)
RGB_GLOW = (120, 230, 255)
SHADE_EMPTY = " "
SHADE_LOW = "\u2591"
SHADE_MID = "\u2592"
SHADE_FULL = "\u2593"
FULLWIDTH_DIGITS = "\uFF10\uFF11\uFF12\uFF13\uFF14\uFF15\uFF16\uFF17\uFF18\uFF19"
PHASE_IDLE = "idle"
PHASE_SELECT = "select"
PHASE_DROP = "drop"
