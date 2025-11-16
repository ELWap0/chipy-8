from functools import wraps

import numpy
from chipy_8 import audio, graphics

MEM_SIZE = 4096
REG_NUM = 16
STACK_SIZE = 48
valid_inputs = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
]


class chip8(graphics, audio):
    memory: numpy.typing.NDArray = numpy.zeros(MEM_SIZE, dtype=numpy.uint8)
    v: numpy.typing.NDArray = numpy.zeros(REG_NUM, dtype=numpy.uint8)
    stack: numpy.typing.NDArray = numpy.zeros(STACK_SIZE, dtype=numpy.uint16)
    delay_counter: int
    sound_counter: int
    rom_path: str
    pc: numpy.uint16 = numpy.uint16(0x200)
    opcode: numpy.uint16 = numpy.uint16(0x0)
    i: numpy.uint16 = numpy.uint16(0x0)
    sp: numpy.uint8 = numpy.uint8(0x00)

    def __init__(self, rom):
        self.rom_path = rom
        graphics.setup()
        audio.setup()

    def delay_timer(self):
        for x in range(self.delay_counter):
            self.delay_counter = x
            yield

    def sound_timer(self):
        for i in range(self.sound_counter):
            if i == 1:
                audio.play_sound()
            yield

    def get_input(self):
        user_input = input()
        if user_input in valid_inputs:
            return (True, user_input)
        else:
            return (False, user_input)

    def emulation_cycle(self):
        self.opcode = self.memory[self.pc] << 8 + self.memory[self.pc + 1]
        self.decode()
        self.pc = self.pc + 2

    def decode(self):
        op = (self.opcode & 0xF000) >> 12
        match op:
            case 0x0:
                data = self.opcode & 0x0FFF
                match data:
                    case 0x00E0:
                        operation = self.CLS
                    case 0x00EE:
                        operation = self.RET
                    case _:
                        operation = self.SYS
            case 0x1:
                operation = self.JP
            case 0x2:
                operation = self.CALL
            case 0x3:
                operation = self.SE
            case 0x4:
                operation = self.SNE
            case 0x5:
                operation = self.SE_VV
            case 0x6:
                operation = self.LD
            case 0x7:
                operation = self.ADD
            case 0x8:
                data = self.opcode & 0x0FFF
                match data:
                    case 0x0000:
                        operation = self.LD_VV
                    case 0x0001:
                        operation = self.OR
                    case 0x0002:
                        operation = self.AND
                    case 0x0003:
                        operation = self.XOR
                    case 0x0004:
                        operation = self.ADD
                    case 0x0005:
                        operation = self.ADD
                    case 0x0006:
                        operation = self.ADD
                    case 0x0006:
                        operation = self.ADD
                    case 0x0007:
                        operation = self.ADD
                    case 0x000E:
                        operation = self.ADD
            case 0x9:
                operation = self.OR
            case 0xa:
            case 0xb:
            case 0xc:
            case 0xd:
            case 0xe:
            case 0xf:
        return operation

    @staticmethod
    def get_x(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            x = bytes(self.opcode & 0x0F00 >> 8)
            return func(self, x, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_y(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            y = bytes(self.opcode & 0x00F0 >> 4)
            return func(self, y, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_addr(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            addr = bytes(self.opcode & 0x0FFF)
            return func(self, addr, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_byte(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            byte = bytes(self.opcode & 0x00FF)
            return func(self, byte, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_nibble(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nibble = bytes(self.opcode & 0x000F)
            return func(self, nibble, *args, **kwargs)

        return wrapper
