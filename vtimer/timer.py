import machine
import micropython


class NoTimer:
    PERIODIC = micropython.const(machine.Timer.PERIODIC)
    ONE_SHOT = micropython.const(machine.Timer.ONE_SHOT)

    def init(self, id=-1, mode=PERIODIC, freq=-1, period=-1, callback=None):
        raise NotImplementedError()

    def deinit(self):
        raise NotImplementedError()

    def __start(self):
        raise NotImplementedError()

    def __stop(self):
        raise NotImplementedError()
