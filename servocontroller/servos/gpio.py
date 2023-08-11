import math

import servocontroller.driver
import servocontroller.driver.gpio
import servocontroller.servos


class ServosGPIO(servocontroller.servos.Servos):
    @staticmethod
    def __old_degrees_duty(degrees):
        duty = (12.346 * degrees ** 2 + 7777.8 * degrees + 700000)
        if servocontroller.driver.gpio.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_ESP8266:
            return int((duty / 1000000) * 1023 / 20)
        elif servocontroller.driver.gpio.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_ESP32:
            return int(duty)
        elif servocontroller.driver.gpio.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_RP240:
            return int(duty)

    @staticmethod
    def __degrees_duty(degrees):
        default = servocontroller.driver.gpio.DriverGPIO.DEFAULT_GPIO_PLATFORM
        duty = 0
        if default == servocontroller.driver.gpio.DriverGPIO.GPIO_ESP8266:
            duty = servocontroller.driver.mapping(degrees, 0, 180, 35, 127)
        else:
            duty = servocontroller.driver.mapping(degrees, 0, 180, 700000, 2500014)
        return math.floor(duty)

    @staticmethod
    def __duty_degrees(duty):
        default = servocontroller.driver.gpio.DriverGPIO.DEFAULT_GPIO_PLATFORM
        degrees = 0
        if default == servocontroller.driver.gpio.DriverGPIO.GPIO_ESP8266:
            degrees = servocontroller.driver.mapping(duty, 35, 127, 0, 180)
        else:
            degrees = servocontroller.driver.mapping(duty, 700000, 2500014, 0, 180)
        return math.floor(degrees)

    def __init__(self, *args, **kwargs):
        self.__limit_degrees = 0
        self.driver = None
        self.init(*args, **kwargs)

    def init(self, driver: servocontroller.driver.gpio.DriverGPIO, degrees=180, freq=50):
        self.driver = driver
        self.__limit_degrees = degrees
        self.driver.freq(freq)

    def deinit(self):
        pass

    def write(self, index, degrees: int):
        self.driver.duty(index, ServosGPIO.__degrees_duty(degrees))

    def read(self, index: int) -> int:
        return ServosGPIO.__duty_degrees(self.driver.duty(index))

    def position(self, index, degrees=None):
        if degrees is None:
            return ServosGPIO.__duty_degrees(self.driver.duty(index))
        else:
            self.driver.duty(index, ServosGPIO.__degrees_duty(degrees))

    def release(self, index: int):
        self.driver.duty(index, 0)

    @property
    def degrees(self) -> int:
        return self.__limit_degrees

    def __getitem__(self, index: int):
        return self.position(index)

    def __setitem__(self, index: int, degrees: int):
        return self.position(index, degrees)

    def __len__(self):
        return len(self.driver)

    @staticmethod
    def bind():
        pass

    def __iter__(self):
        for i in range(len(self)):
            yield i

