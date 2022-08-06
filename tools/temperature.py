import binascii

from machine import Pin
import math
from lib import onewire

bus1wire = onewire.OneWire(Pin(25))


def refresh_temperature():
    bus1wire.reset(True)
    bus1wire.writebyte(bus1wire.SKIP_ROM)
    bus1wire.writebyte(0x44)


def scan_sensors():
    return [binascii.hexlify(rom).decode() for rom in bus1wire.scan() if rom[0] in (0x10, 0x22, 0x28)]


class TemperatureSensor:
    id: str or None

    def __init__(self, id: str or None = None):
        self.id = id
        self.temp = -127

    def read(self, decimal: int = 2) -> float:
        temp_buffer = bytearray(9)
        rom = binascii.unhexlify(self.id.encode())
        bus1wire.reset(True)
        bus1wire.select_rom(rom)
        bus1wire.writebyte(0xBE)
        bus1wire.readinto(temp_buffer)
        if bus1wire.crc8(temp_buffer):
            raise Exception("CRC error")
        if rom[0] == 0x10:
            if temp_buffer[1]:
                t = temp_buffer[0] >> 1 | 0x80
                t = -((~t + 1) & 0xFF)
            else:
                t = temp_buffer[0] >> 1
            temp = t - 0.25 + (temp_buffer[7] - temp_buffer[6]) / temp_buffer[7]
        else:
            t = temp_buffer[1] << 8 | temp_buffer[0]
            if t & 0x8000:
                t = -((t ^ 0xFFFF) + 1)
            temp = t / 16
        return math.ceil(temp * 10**decimal) / 10**decimal

