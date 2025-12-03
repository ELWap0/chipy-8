#!/usr/bin/env python
import curses
import functools

import click
from chipy_8 import Chip8


def main(rom, stdscr):
    c = Chip8(rom)
    c.run_loop()


@click.command()
@click.argument("rom", nargs=1)
def start(rom):
    mainFunc = functools.partial(main, rom)
    curses.wrapper(mainFunc)


if __name__ == "__main__":
    start()
