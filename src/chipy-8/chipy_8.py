import random
from functools import wraps

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


class Chip8(graphics.Graphics, audio):
    memory: list[int] = [0] * MEM_SIZE
    v: list[int] = [0] * REG_NUM
    stack: list[int] = [0] * STACK_SIZE
    delay_counter: int = 0
    sound_counter: int = 0
    rom_path: str
    pc: int = 0x200
    opcode: int = 0
    i: int = 0
    sp: int = 0

    def __init__(self, rom):
        self.rom_path = rom
        graphics.setup()
        audio.setup()

    def delay_timer(self):
        for x in range(self.delay_counter):
            self.delay_counter = x
            yield x

    def sound_timer(self):
        for x in range(self.sound_counter):
            self.sound_counter = x
            if x == 1:
                audio.play_sound()
            yield x

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
        operation = None
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
                operation = self.LD_byte
            case 0x7:
                operation = self.ADD_byte
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
                        operation = self.ADD_Reg
                    case 0x0005:
                        operation = self.SUB
                    case 0x0006:
                        operation = self.SHR
                    case 0x0007:
                        operation = self.SUBN
                    case 0x000E:
                        operation = self.SHL
            case 0x9:
                operation = self.SNE_Reg
            case 0xA:
                operation = self.LD_I
            case 0xB:
                operation = self.JP_V
            case 0xC:
                operation = self.RND
            case 0xD:
                operation = self.DRW
            case 0xE:
                data = 0x00FF & self.opcode
                match data:
                    case 0x9E:
                        operation = self.SKP
                    case 0xA1:
                        operation = self.SKNP
            case 0xF:
                data = 0x00FF & self.opcode
                match data:
                    case 0x07:
                        operation = self.LD_DT
                    case 0x0A:
                        operation = self.LD_K
                    case 0x15:
                        operation = self.SET_DT
                    case 0x18:
                        operation = self.SET_ST
                    case 0x1E:
                        operation = self.ADD_I
                    case 0x29:
                        operation = self.LD_ADDR
                    case 0x33:
                        operation = self.LD_BCD
                    case 0x55:
                        operation = self.CP
                    case 0x65:
                        operation = self.RD
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

    @get_addr
    def SYS(self, addr):
        """jump to machine code (ignored in current)"""
        pass

    def CLS(self):
        """clear display"""
        graphics.clear()

    def RET(self):
        """return from subroutine"""
        self.pc = self.stack[self.sp]
        self.sp -= 1

    @get_addr
    def JP(self, addr):
        self.pc = addr

    @get_addr
    def CALL(self, addr):
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = addr

    @get_x
    @get_byte
    def SE(self, x, byte):
        if self.v[x] == byte:
            self.pc += 2

    @get_x
    @get_byte
    def SNE(self, x, byte):
        if self.v[x] != byte:
            self.pc += 2

    @get_x
    @get_y
    def SE_VV(self, x, y):
        if self.v[x] == self.v[y]:
            self.pc += 2

    @get_x
    @get_byte
    def LD_byte(self, x, byte):
        self.v[x] = byte

    @get_x
    @get_byte
    def ADD_byte(self, x, byte):
        self.v[x] += byte

    @get_x
    @get_y
    def LD_VV(self, x, y):
        self.v[x] = self.v[y]

    @get_x
    @get_y
    def OR(self, x, y):
        self.v[x] |= self.v[y]

    @get_x
    @get_y
    def AND(self, x, y):
        self.v[x] &= self.v[y]

    @get_x
    @get_y
    def XOR(self, x, y):
        self.v[x] ^= self.v[y]

    @get_x
    @get_y
    def ADD_Reg(self, x, y):
        res = self.v[x] + self.v[y]
        self.v[15] = (res & 0xF00) >> 8
        self.v[x] = res & 0xF00

    @get_y
    @get_x
    def SUB_Reg(self, x, y):
        if self.v[x] > self.v[y]:
            self.v[15] = 1
        else:
            self.v[15] = 0

        self.v[x] -= self.v[y]

    @get_x
    def SHR(self, x):
        self.v[15] = 1 if self.v[x] & 1 else 0
        self.v[x] >>= 1

    @get_x
    @get_y
    def SUBN_Reg(self, x, y):
        if self.v[x] > self.v[y]:
            self.v[15] = 1
        else:
            self.v[15] = 0

        self.v[x] = self.v[y] - self.v[x]

    @get_x
    def SHL(self, x):
        self.v[15] = 1 if self.v[x] & 1 else 0
        self.v[x] <<= 1

    @get_x
    @get_y
    def SNE_Reg(self, x, y):
        if self.v[x] != self.v[y]:
            self.pc += 2

    @get_addr
    def LD_I(self, addr):
        self.i = addr

    @get_addr
    def JP_V(self, addr):
        self.pc = addr + self.v[0]

    @get_x
    @get_byte
    def RND(self, x, byte):
        self.v[x] = random.randbytes & byte

    @get_x
    @get_y
    @get_nibble
    def DRW(self, x, y, nibble):
        pass

    @get_x
    def SKP(self, x):
        ok, input = self.get_input()
        if ok:
            if int(input[0]) == self.v[x]:
                self.pc += 2

    @get_x
    def SKNP(self, x):
        ok, input = self.get_input()
        if ok:
            if int(input[0]) != self.v[x]:
                self.pc += 2

    @get_x
    def LD_DT(self, x):
        self.v[x] = self.delay_counter

    @get_x
    def LD_K(self, x):
        ok, input = self.get_input()
        if ok:
            self.v[x] = int(input[0])

    @get_x
    def SET_DT(self, x):
        self.delay_counter = self.v[x]

    @get_x
    def SET_ST(self, x):
        self.sound_counter = self.v[x]

    @get_x
    def ADD_I(self, x):
        self.i += self.v[x]

    def LD_ADDR(self):
        pass

    @get_x
    def LD_BCD(self, x):
        val = self.v[x]
        self.memory[self.i] = val // 100
        val = val // 100
        self.memory[self.i + 1] = self.v[x] // 10
        val = val // 10
        self.memory[self.i + 2] = val

    def CP(self):
        self.memory[self.i : self.i + 16] = self.v[:]

    def RD(self):
        self.v[:] = self.memory[self.i : self.i + 16]
