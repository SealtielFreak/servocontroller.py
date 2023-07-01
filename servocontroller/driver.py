import sys
import time

import machine
import micropython
import ustruct


def mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def fmapping(in_min, in_max, out_min, out_max):
    return lambda x: (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Driver:
    def init(self, *args, **kwargs):
        raise NotImplementedError()

    def deinit(self):
        raise NotImplementedError()

    def freq(self, freq=None):
        raise NotImplementedError()

    def pwm(self, index, on=None, off=None):
        raise NotImplementedError()

    def duty(self, index, value=None, invert=False):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()


class DriverGPIO(Driver):
    GPIO_ESP8266 = micropython.const(1)
    GPIO_ESP32 = micropython.const(2)
    GPIO_RP240 = micropython.const(3)

    DEFAULT_GPIO_PLATFORM = micropython.const(
        {
            'esp8266': GPIO_ESP8266,
            'esp32': GPIO_ESP32,
            'RP2040': GPIO_RP240,
        }[sys.platform]
    )

    @staticmethod
    def set_duty(pwm, duty):
        if DriverGPIO.DEFAULT_GPIO_PLATFORM == DriverGPIO.GPIO_ESP8266:
            pwm.duty(duty)
        elif DriverGPIO.DEFAULT_GPIO_PLATFORM == DriverGPIO.GPIO_ESP32:
            pwm.duty_ns(duty)
        elif DriverGPIO.DEFAULT_GPIO_PLATFORM == DriverGPIO.GPIO_RP240:
            pwm.duty_u16(duty)

    def __init__(self, *args, **kwargs):
        self.__attach = {}
        self.__freq = 0
        self.init(*args, **kwargs)

    def attach(self, index: int, pin: machine.Pin) -> int:
        try:
            self.__attach[index] = (machine.PWM(pin, freq=self.freq()), 0)
        except ValueError as e:
            return False
        return True

    def init(self, *args, **kwargs):
        pass

    def deinit(self):
        pass

    def freq(self, freq=None):
        if freq is None:
            return self.__freq
        else:
            self.__freq = freq
            for k, (pwm, duty) in self.__attach.items():
                pwm.freq(freq)

    def pwm(self, index, on=None, off=None):
        if index in self.__attach:
            return self.__attach[index][1]
        return 0

    def duty(self, index, value=None, invert=False):
        if value is not None and index in self.__attach:
            pwm = self.__attach[index][0]
            DriverGPIO.set_duty(pwm, value)
            self.__attach[index] = pwm, value
        else:
            return self.__attach[index][1]

    def reset(self):
        self.freq(0)

    def __len__(self) -> int:
        return len(self.__attach)


class DriverPCA9685(Driver):
    DEFAULT_I2C_ADDRESS = micropython.const(0x40)
    MAX_CHANNELS = micropython.const(16)

    @staticmethod
    def pca9685_write(i2c: machine.I2C, address: int, address_device: int, value: int):
        i2c.writeto_mem(address, address_device, bytearray([value]))

    @staticmethod
    def pca9685_read(i2c: machine.I2C, address: int, address_device: int):
        return i2c.readfrom_mem(address, address_device, 1)[0]

    def __init__(self, i2c: machine.I2C, address=0x40):
        self.i2c = None
        self.address = None
        self.init(i2c, address)

    def init(self, i2c: machine.I2C, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()

    def __write(self, address, value):
        return DriverPCA9685.pca9685_write(self.i2c, self.address, address, value)

    def __read(self, address):
        return DriverPCA9685.pca9685_read(self.i2c, self.address, address)

    def deinit(self):
        self.reset()

    def freq(self, freq=None):
        if freq is None:
            return int(25000000.0 / 4096 / (self.__read(0xfe) - 0.5))
        else:
            pre_scale = int(25000000.0 / 4096.0 / freq + 0.5)
            old_mode = self.__read(0x00)  # Mode 1
            self.__write(0x00, (old_mode & 0x7F) | 0x10)  # Mode 1, sleep
            self.__write(0xfe, pre_scale)  # Prescale
            self.__write(0x00, old_mode)  # Mode 1
            time.sleep_us(5)
            self.__write(0x00, old_mode | 0xa1)  # Mode 1, autoincrement on

    def pwm(self, index, on=None, off=None):
        if on is None or off is None:
            data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
            return ustruct.unpack('<HH', data)
        else:
            data = ustruct.pack('<HH', on, off)
            self.i2c.writeto_mem(self.address, 0x06 + 4 * index, data)  # Mode 1, autoincrement on

    def duty(self, index, value=None, invert=False):
        if isinstance(value, int):
            if not 0 <= value <= 4095:
                raise ValueError("Out of range")
            if invert:
                value = 4095 - value
            if value == 0:
                self.pwm(index, 0, 4096)
            elif value == 4095:
                self.pwm(index, 4096, 0)
            else:
                self.pwm(index, 0, value)
        else:
            pwm = self.pwm(index)
            if pwm == (0, 4096):
                value = 0
            elif pwm == (4096, 0):
                value = 4095
            value = pwm[1]
            if invert:
                value = 4095 - value
            return value

    def reset(self):
        self.__write(0x00, 0x00)  # Mode1

    def __len__(self) -> int:
        return DriverPCA9685.MAX_CHANNELS
