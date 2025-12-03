#!/usr/bin/env python

import curses

OFFSET_X = 1
OFFSET_Y = 1


class Graphics:
    window: curses.window
    x: int
    y: int
    row: list[int]

    def __init__(self):
        curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        self.row = [0 for _ in range(64)]
        self.window = curses.newwin(34, 67, 1, 1)

    def setup(self):
        self.window.scrollok(False)
        self.window.box("|", "-")
        self.window.refresh()

    def draw(self, x, y, h_code, w: curses.window | None = None):
        r = self.row[y]
        r ^= h_code << x
        if w is not None:
            w.addstr(y + OFFSET_Y, 70, f"{r}")
            w.refresh()
        for z in range(0, 64):
            if r & (0x1 << z):
                self.window.addch(y + OFFSET_Y, (64 - z) + OFFSET_X, "*")
        self.window.refresh()

    def draw_test(self, x, y):
        self.window.addch(y + OFFSET_Y, x + OFFSET_X, "*")
        self.window.refresh()

    def clear(self):
        self.window.clear()
        self.window.box("|", "-")
        self.window.refresh()

    def get_input(self) -> tuple[bool, int]:
        curses.halfdelay(2)
        try:
            value = chr(self.window.getch())
            return True, int(value, 16)
        except:
            return False, -1


def main(stdscr):
    g = Graphics()
    g.setup()
    g.draw(0, 0, 0x00000001, stdscr)
    curses.napms(1000)
    g.draw(0, 1, 0x00000002, stdscr)
    curses.napms(1000)
    g.draw(0, 2, 0x00000004, stdscr)
    curses.napms(1000)
    g.draw(0, 3, 0x00000008, stdscr)
    curses.napms(1000)


if __name__ == "__main__":
    curses.wrapper(main)
