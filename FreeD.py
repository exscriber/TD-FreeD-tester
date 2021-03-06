# FreeD module by NNZ
#
from dataclasses import dataclass
from contextlib import suppress


@dataclass
class Param:
    name: str
    begin: int
    size: int
    mult: int = None
    signed: bool = False

    @property
    def loc(self):
        return slice(self.begin, self.begin + self.size)

    def parse(self, buf: bytes):
        return int.from_bytes(buf[self.loc],
                              byteorder='big',
                              signed=self.signed)


class Message:
    length = 0
    fmt = []

    @staticmethod
    def checksum(buf: bytes):
        return 0x40 - sum(buf) & 0xFF

    @classmethod
    def parse(cls, msg: bytes):
        result = dict()
        for param in cls.fmt:
            result[param.name] = param.parse(msg)
        return result

    @classmethod
    def from_bytes(cls, buf: bytes):
        obj = cls()
        for param in cls.fmt:
            value = param.parse(buf)
            if param.mult:
                value /= param.mult
            setattr(obj, param.name, value)
        return obj

    def to_bytes(self):
        result = bytearray(self.length)
        for param in self.fmt[:-1]:
            value = getattr(self, param.name)
            if param.mult:
                value *= param.mult
            with suppress(OverflowError):
                result[param.loc] = int(value).to_bytes(param.size,
                                                        byteorder='big',
                                                        signed=param.signed)
        result[-1] = self.checksum(result[:-1])
        return bytes(result)


@dataclass
class D1(Message):
    """ camera orientation data """
    length = 29
    _id = 0xD1
    cam: int = 255
    pan: float = 0
    tilt: float = 0
    roll: float = 0
    posx: float = 0
    posy: float = 0
    posz: float = 0
    zoom: int = 0
    focus: int = 0
    user: int = 0

    fmt = [
        Param('_id', 0, 1),
        Param('cam', 1, 1),
        Param('pan', 2, 3, mult=32768, signed=True),
        Param('tilt', 5, 3, mult=32768, signed=True),
        Param('roll', 8, 3, mult=32768, signed=True),
        Param('posx', 11, 3, mult=64000, signed=True),
        Param('posy', 14, 3, mult=64000, signed=True),
        Param('posz', 17, 3, mult=64000, signed=True),
        Param('zoom', 20, 3),
        Param('focus', 23, 3),
        Param('user', 26, 2),
        Param('_chk', 28, 1),
    ]


@dataclass
class DA(Message):
    """ camera calibration data """
    length = 30
    _id = 0xDA
    cam: int = 255
    shiftx: float = 0
    shifty: float = 0
    scalex: float = 1
    scaley: float = 1
    k1: float = 0
    k2: float = 0
    offsetx: float = 0
    offsety: float = 0
    offsetz: float = 0

    fmt = [
        Param('_id', 0, 1),
        Param('cam', 1, 1),
        Param('shiftx', 2, 3, mult=256, signed=True),
        Param('shifty', 5, 3, mult=256, signed=True),
        Param('scalex', 8, 3, mult=256, signed=True),
        Param('scaley', 11, 3, mult=256, signed=True),
        Param('k1', 14, 3, mult=256, signed=True),
        Param('k2', 17, 3, mult=256, signed=True),
        Param('offsetx', 20, 3, mult=64000, signed=True),
        Param('offsety', 23, 3, mult=64000, signed=True),
        Param('offsetz', 26, 3, mult=64000, signed=True),
        Param('_chk', 29, 1),
    ]


if __name__ == '__main__':
    msg1 = D1()
    print(msg1)
    msg2 = DA()
    print(msg2)
    pass
