from functools import wraps

from chipy_8 import audio, graphics

MEM_SIZE = 4096
REG_NUM = 16
STACK_SIZE = 48


class chip8(graphics, audio):
    memory: bytearray = bytearray(MEM_SIZE)
    v: bytearray = bytearray(REG_NUM)
    stack: bytearray = bytearray(STACK_SIZE)
    delay_counter: int

    def timer(self):
        for x in range(self.delay_counter):
            self.delay_counter = x
            yield

    def soundTimer(self, count):
        for _ in range(count):
            yield

    def get_input(self):
        pass

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
                        operation = self.get_dealy
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

    @classmethod
    def get_x(cls, func):
        x = cls.opcode & 0x0F00 >> 8

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, x, *args, **kwargs)

        return wrapper

    @classmethod
    def get_y(cls, func):
        y = cls.opcode & 0x00F0 >> 4

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, y, *args, **kwargs)

        return wrapper

    @classmethod
    def get_nnn(cls, func):
        nnn = cls.opcode & 0x0FFF

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, nnn, *args, **kwargs)

        return wrapper

    @classmethod
    def get_nn(cls, func):
        nn = cls.opcode & 0x00FF

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, nn, *args, **kwargs)

        return wrapper
