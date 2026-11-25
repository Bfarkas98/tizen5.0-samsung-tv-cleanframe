import os
import shutil
import sys

SCREENS = {
    "Status": ("TV OS is running.", "This image is configured for x86-64 PCs and virtual machines."),
    "Controls": ("Up / Down: move", "Enter: open", "Escape / Backspace: return"),
}
MENU = tuple(SCREENS)


def main(read_key, render):
    selected = 0
    opened = None
    while True:
        lines = ["TV OS", ""]
        if opened:
            lines.extend((opened, "", *SCREENS[opened], "", "Esc  Back"))
        else:
            lines.extend(f"{'>' if i == selected else ' '}  {name}" for i, name in enumerate(MENU))
            lines.extend(("", "Up / Down  Move     Enter  Open"))
        render(lines)
        key = read_key()
        if opened:
            if key == "back":
                opened = None
        elif key in ("up", "down"):
            selected = (selected + (-1 if key == "up" else 1)) % len(MENU)
        elif key == "enter":
            opened = MENU[selected]


def render_windows(lines):
    width = shutil.get_terminal_size((80, 25)).columns
    sys.stdout.write("\x1b[2J\x1b[H" + "\n".join(line.center(width - 1) for line in lines) + "\n")
    sys.stdout.flush()


def windows_preview():
    import ctypes
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetStdHandle.restype = ctypes.c_void_p
    kernel.GetConsoleMode.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32))
    kernel.SetConsoleMode.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    handle = kernel.GetStdHandle(-11)
    mode = ctypes.c_uint32()
    if not kernel.GetConsoleMode(handle, ctypes.byref(mode)) or not kernel.SetConsoleMode(handle, mode.value | 4):
        raise OSError("Open this preview in a Windows terminal.")

    def read_key():
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            return {"H": "up", "P": "down"}.get(msvcrt.getwch())
        return {"\r": "enter", "\x1b": "back", "\x08": "back"}.get(key)

    try:
        main(read_key, render_windows)
    finally:
        kernel.SetConsoleMode(handle, mode.value)


def linux_console(screen):
    import curses

    def read_key():
        return {
            curses.KEY_UP: "up", curses.KEY_DOWN: "down", curses.KEY_ENTER: "enter",
            curses.KEY_BACKSPACE: "back", 10: "enter", 13: "enter", 27: "back", 127: "back",
        }.get(screen.getch())

    def render(lines):
        height, width = screen.getmaxyx()
        screen.erase()
        for row, line in enumerate(lines[:height]):
            text = line[:width - 1]
            screen.addstr(row, (width - len(text)) // 2, text)
        screen.refresh()

    main(read_key, render)


if __name__ == "__main__":
    try:
        if os.name == "nt":
            windows_preview()
        else:
            import curses

            curses.wrapper(linux_console)
    except KeyboardInterrupt:
        pass
