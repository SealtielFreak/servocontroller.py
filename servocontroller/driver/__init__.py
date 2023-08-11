import abc


def mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def fmapping(in_min, in_max, out_min, out_max):
    return lambda x: (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class Driver(abc.ABC):
    @abc.abstractmethod
    def init(self, *args, **kwargs): ...

    @abc.abstractmethod
    def deinit(self): ...

    @abc.abstractmethod
    def freq(self, freq=None): ...

    @abc.abstractmethod
    def pwm(self, index, on=None, off=None): ...

    @abc.abstractmethod
    def duty(self, index, value=None, invert=False): ...

    @abc.abstractmethod
    def reset(self): ...

    @abc.abstractmethod
    def __len__(self) -> int: ...
