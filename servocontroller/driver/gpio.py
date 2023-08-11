import sys

import machine
import micropython

import servocontroller.driver


class DriverGPIO(servocontroller.driver.Driver):
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


def initialize_gpio(driver: DriverGPIO, *pins, **kwargs) -> DriverGPIO:
    freq = kwargs.get("freq", 50)

    for i, pin in pins:
        driver.attach(i, pin)

    driver.freq(freq)

    return driver
