import math

import machine
import micropython

import servocontroller.driver

DEFAULT_FREQ_SERVO = micropython.const(50)


class Servos:
    def init(self, *args, **kwargs):
        raise NotImplementedError()

    def deinit(self):
        raise NotImplementedError()

    def write(self, index, degrees: int):
        raise NotImplementedError()

    def read(self, index: int):
        raise NotImplementedError()

    def position(self, index: int, degrees=None):
        raise NotImplementedError()

    def release(self, index: int):
        raise NotImplementedError()

    @property
    def degrees(self) -> int:
        raise NotImplementedError()

    def __getitem__(self, index: int):
        raise NotImplementedError()

    def __setitem__(self, index: int, degrees: int):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()


class ServosGPIO(Servos):
    @staticmethod
    def __old_degrees_duty(degrees):
        duty = (12.346 * degrees ** 2 + 7777.8 * degrees + 700000)
        if servocontroller.driver.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_ESP8266:
            return int((duty / 1000000) * 1023 / 20)
        elif servocontroller.driver.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_ESP32:
            return int(duty)
        elif servocontroller.driver.DriverGPIO.DEFAULT_GPIO_PLATFORM == servocontroller.driver.DriverGPIO.GPIO_RP240:
            return int(duty)

    @staticmethod
    def __degrees_duty(degrees):
        default = servocontroller.driver.DriverGPIO.DEFAULT_GPIO_PLATFORM
        duty = 0
        if default == servocontroller.driver.DriverGPIO.GPIO_ESP8266:
            duty = servocontroller.driver.mapping(degrees, 0, 180, 35, 127)
        else:
            duty = servocontroller.driver.mapping(degrees, 0, 180, 700000, 2500014)
        return math.floor(duty)

    @staticmethod
    def __duty_degrees(duty):
        default = servocontroller.driver.DriverGPIO.DEFAULT_GPIO_PLATFORM
        degrees = 0
        if default == servocontroller.driver.DriverGPIO.GPIO_ESP8266:
            degrees = servocontroller.driver.mapping(duty, 35, 127, 0, 180)
        else:
            degrees = servocontroller.driver.mapping(duty, 700000, 2500014, 0, 180)
        return math.floor(degrees)

    def __init__(self, *args, **kwargs):
        self.__limit_degrees = 0
        self.driver = None
        self.init(*args, **kwargs)

    def init(self, driver: servocontroller.driver.DriverGPIO, degrees=180, freq=50):
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


class ServosPCA9685(Servos):
    def __init__(self, i2c: machine.I2C, *args, **kwargs):
        self.__current_degrees = {}
        self.__limit_degrees = 0
        self.__freq = None
        self.i2c = i2c
        self.divers_pca9685 = []
        self.period = None
        self.min_duty = None
        self.max_duty = None
        self.init(i2c, *args, **kwargs)

    def __us2duty(self, value: int) -> int:
        return int(4095 * value / self.period)

    def __select_driver(self, index: int, duty=None) -> servocontroller.driver.DriverPCA9685:
        if index > len(self):
            raise IndexError('driver out of range')
        driver_pca9685 = self.divers_pca9685[index // servocontroller.driver.DriverPCA9685.MAX_CHANNELS]
        if duty is not None:
            driver_pca9685[index % servocontroller.driver.DriverPCA9685.MAX_CHANNELS].set_duty(duty)
        return driver_pca9685

    def init(self, i2c: machine.I2C, address=0x40, freq=50, min_us=600, max_us=2400, degrees=180):
        self.__limit_degrees = degrees
        self.__freq = freq
        self.period = 1000000 / freq
        self.min_duty = self.__us2duty(min_us)
        self.max_duty = self.__us2duty(max_us)
        self.i2c = i2c
        all_address = []
        if any(map(lambda obj: isinstance(address, obj), (list, tuple))):
            all_address += address
        else:
            all_address = [address]
        for _address in all_address:
            self.divers_pca9685.append(servocontroller.driver.DriverPCA9685(self.i2c, _address))
        for driver in self.divers_pca9685:
            driver.freq(freq)

    def deinit(self):
        for k, _ in self.__current_degrees.items():
            self.release(k)
        for driver in self.divers_pca9685:
            driver.reset()
        self.__current_degrees.clear()

    def write(self, index, degrees: int):
        span = self.max_duty - self.min_duty
        duty = self.min_duty + span * degrees / self.degrees
        duty = min(self.max_duty, max(self.min_duty, int(duty)))
        self.__select_driver(index).duty(index, duty)

    def read(self, index: int):
        return self.__select_driver(index).duty(index)

    def position(self, index, degrees=None):
        if degrees is None:
            driver = self.__select_driver(index)
            return driver.duty(index)
        else:
            driver = self.__select_driver(index)
            span = self.max_duty - self.min_duty
            duty = self.min_duty + span * degrees / self.degrees
            duty = min(self.max_duty, max(self.min_duty, int(duty)))
            driver.duty(index, duty)

    def release(self, index: int):
        self.__select_driver(index, 0)

    @property
    def degrees(self):
        return self.__limit_degrees

    def __getitem__(self, index: int):
        return self.__current_degrees[index]

    def __setitem__(self, index: int, degrees: int):
        self.__current_degrees[index] = degrees
        self.position(index, degrees)

    def __len__(self):
        return servocontroller.driver.DriverPCA9685.MAX_CHANNELS * len(self.divers_pca9685)
