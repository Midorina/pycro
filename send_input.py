import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

def GetKeyCode(key, value):
    MOUSEEVENTF_MOVE = 0x0001  # mouse move
    MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
    MOUSEEVENTF_LEFTUP = 0x0004  # left button up
    MOUSEEVENTF_RIGHTDOWN = 0x0008  # right button down
    MOUSEEVENTF_RIGHTUP = 0x0010  # right button up
    MOUSEEVENTF_MIDDLEDOWN = 0x0020  # middle button down
    MOUSEEVENTF_MIDDLEUP = 0x0040  # middle button up
    MOUSEEVENTF_WHEEL = 0x0800  # wheel button rolled
    MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move

    if key == 1:
        if value == "down":
            return MOUSEEVENTF_LEFTDOWN
        if value == "up":
            return MOUSEEVENTF_LEFTUP
    if key == 2:
        if value == "up":
            return MOUSEEVENTF_RIGHTUP
        if value == "down":
            return MOUSEEVENTF_RIGHTDOWN
    if key == 4:
        if value == "up":
            return MOUSEEVENTF_MIDDLEUP
        if value == "down":
            return MOUSEEVENTF_MIDDLEDOWN

# Functions

def PressKey(hexKeyCode):
    if 1 <= hexKeyCode <= 6:
        # x = INPUT(type=INPUT_MOUSE,
        #           mi=MOUSEINPUT(mouseData=hexKeyCode))
        ctypes.windll.user32.mouse_event(GetKeyCode(hexKeyCode, "down"), 0, 0, 0, 0)
    else:
        x = INPUT(type=INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    if 1 <= hexKeyCode <= 6:
        # x = INPUT(type=INPUT_MOUSE,
        #           mi=MOUSEINPUT(mouseData=hexKeyCode,
        #                         dwFlags=KEYEVENTF_KEYUP))
        ctypes.windll.user32.mouse_event(GetKeyCode(hexKeyCode, "up"), 0, 0, 0, 0)
    else:
        x = INPUT(type=INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode,
                                dwFlags=KEYEVENTF_KEYUP))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


# def AltTab():
#     """Press Alt+Tab and hold Alt key for 2 seconds
#     in order to see the overlay.
#     """
#     PressKey(VK_MENU)   # Alt
#     PressKey(VK_TAB)    # Tab
#     ReleaseKey(VK_TAB)  # Tab~
#     time.sleep(2)
#     ReleaseKey(VK_MENU) # Alt~
#
# if __name__ == "__main__":
#     AltTab()
