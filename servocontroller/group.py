import abc


class ServoGroup:
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def init(self): ...

    @abc.abstractmethod
    def deinit(self): ...
