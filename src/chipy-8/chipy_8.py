import random
from functools import wraps

from chipy_8 import audio, graphics

MEM_SIZE = 4096
REG_NUM = 16
STACK_SIZE = 48
valid_inputs = ['0', '1', '2', '3' '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']



class chip8(graphics, audio):
    memory: bytearray = bytearray(MEM_SIZE)
    v: bytearray = bytearray(REG_NUM)
    stack: bytearray = bytearray(STACK_SIZE)
    delay_counter: int
    sound_counter: int
    rom_path: str

    def __init__(self, rom):
        self.rom_path = rom
        graphics.setup()
        audio.setup()
        setupInput()


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
        

    def decode(self):
        op = 0xF000 & self.opcode >> 12
        operation = None
        match op:
            case 0x0:
                op = 0x0FFF & self.opcode
                match op:
                    case 0x00E0:
                        operation = self.disp_clear
                    case 0x00EE:
                        operation = self.ret
                    case _:
                        operation = self.call
            case 0x1:
                operation = self.goto
            case 0x2:
                operation = self.call_sub
            case 0x3:
                operation = self.eqV
            case 0x4:
                operation = self.neqV
            case 0x5:
                operation = self.eqVV
            case 0x6:
                operation = self.assigV
            case 0x7:
                operation = self.sum_constV
            case 0x8:
                op = self.opcode & 0x000F
                match op:
                    case 0x0:
                        operation = self.assigVV
                    case 0x1:
                        operation = self.orVV
                    case 0x2:
                        operation = self.andVV
                    case 0x3:
                        operation = self.xorVV
                    case 0x4:
                        operation = self.add_assigVV
                    case 0x5:
                        operation = self.sub_assigVV
                    case 0x6:
                        operation = self.l_shiftV
                    case 0x7:
                        operation = self.sub_flipVV
                    case 0xE:
                        operation = self.r_shiftV
            case 0x9:
                operation = self.neqVV
            case 0xA:
                operation = self.assignI
            case 0xB:
                operation = self.jump
            case 0xC:
                operation = self.rand
            case 0xD:
                operation = self.draw
            case 0xE:
                op = self.opcode & 0x00FF
                match op:
                    case 0x009E:
                        operation = self.eqKeyV
                    case 0x00A1:
                        operation = self.neqKeyV
            case 0xF:
                op = self.opcode & 0x00FF
                match op:
                    case 0x07:
                        operation = self.get_delay
                    case 0x0A:
                        operation = self.get_key
                    case 0x15:
                        operation = self.timer
                    case 0x18:
                        operation = self.soundTimer
                    case 0x1E:
                        operation = self.sum_assignI
                    case 0x29:
                        operation = self.assign_spriteI
                    case 0x33:
                        operation = self.set_BCD
                    case 0x55:
                        operation = self.dump
                    case 0x65:
                        operation = self.load

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
    def get_nnn(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nnn = bytes(self.opcode & 0x0FFF)
            return func(self, nnn, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_nn(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nn = bytes(self.opcode & 0x00FF)
            return func(self, nn, *args, **kwargs)

        return wrapper

    @staticmethod
    def get_n(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nnn = bytes(self.opcode & 0x000F)
            return func(self, nnn, *args, **kwargs)

        return wrapper

    def ret(self):
        self.pc = self.stack[self.sp]
        self.sp -= 1

    @get_nnn
    def goto(self, nnn):
        self.pc = nnn

    @get_nnn
    def call_sub(self,nnn):
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = nnn

    @get_x
    @get_nn
    def eqV(self, x, nn):
        return nn == self.v[x]

    @get_x
    @get_y
    def eqVV(self, x, y):
        return self.v[y] != self.v[x]

    @get_x
    @get_nn
    def assigV(self, x, nn):
        self.v[x] = nn

    @get_x
    @get_y
    def orVV(self, x, y):
        self.v[x] |= self.v[y]

    @get_x
    @get_y
    def andVV(self, x, y):
        self.v[x] &= self.v[y]

    @get_x
    @get_y
    def xorVV(self, x, y):
        self.v[x] ^= self.v[y]

    @get_x
    @get_y
    def add_assigVV(self, x, y):
        self.v[x] += self.v[y]

    @get_x
    @get_y
    def sub_assigVV(self, x, y):
        self.v[x] -= self.v[y]

    @get_x
    def l_shiftV(self, x):
        self.v[x] <<= 1

    @get_x
    @get_y
    def sub_flipVV(self, x, y):
        self.v[x] = self.v[y] - self.v[x]

    @get_x
    def r_shiftV(self, x):
        self.v[x] >>= 1

    @get_x
    @get_y
    def neqVV(self, x, y):
        return self.v[x] != self.v[y]

    @get_nnn
    def assignI(self, nnn):
        self.I = nnn

    @get_nnn
    def jump(self, nnn):
        self.pc = self.v[0] & nnn

    @get_nn
    def rand(self, x, nn):
        self.v[x] = random.randbytes(1) & nn

    @get_x
    @get_y
    @get_n
    def draw(self, x, y, n):
        pass

    def eqKeyV(self):
        key = self.get_input()
        pass

    def neqKeyV(self):
        pass

    def get_delay(self):
        return self.delay_counter

    def get_key(self):
        return self.key

    @get_x
    def setDelayTimer(self, x):
        self.delay_counter = self.v[x]
        return self.delay_timer

    @get_x
    def setSoundTimer(self, x):
        self.sound_timer = self.v[x]
        return self.sound_timer

    @get_x
    def sum_assignI(self, x):
        self.I += self.v[x]

    @get_x
    def assign_spriteI(self, x):
        self.I += self.sprite_addr[x]

    def set_BCD(self):
        pass

    def dump(self):
        pass

    def load(self):
        pass
