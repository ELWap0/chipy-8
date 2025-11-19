import curses


class Graphics:
    stdscr: curses.window
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.nocbreak()
        curses.curs_set(False)

        self.stdscr.refresh()

    def __del__(self):
        curses.echo()
        curses.curs_set(True)
        curses.endwin()

    def draw(self):
        self.stdscr.refresh()

    def getInput(self):
        curses.halfdelay(2)
        try:
            value = self.stdscr.getch()
        except:
            value = -1
        return value
