import abc

import micropython

DEFAULT_FREQ_SERVO = micropython.const(50)


class Servos(abc.ABC):
    @abc.abstractmethod
    def init(self, *args, **kwargs): ...

    @abc.abstractmethod
    def deinit(self): ...

    @abc.abstractmethod
    def write(self, index, degrees: int): ...

    @abc.abstractmethod
    def read(self, index: int): ...

    @abc.abstractmethod
    def position(self, index: int, degrees=None): ...

    @abc.abstractmethod
    def release(self, index: int): ...

    @property
    @abc.abstractmethod
    def degrees(self) -> int: ...

    @abc.abstractmethod
    def __getitem__(self, index: int): ...

    @abc.abstractmethod
    def __setitem__(self, index: int, degrees: int): ...

    @abc.abstractmethod
    def __len__(self): ...

    @abc.abstractmethod
    def __iter__(self):
        pass

