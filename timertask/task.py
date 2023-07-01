import micropython


class Queue:
    def __init__(self):
        self.__list = []

    def appendleft(self, item):
        self.__list = [item] + self.__list

    def append(self, item):
        self.__list.append(item)

    def popleft(self):
        self.__list.pop(0)

    def pop(self):
        self.__list.pop()

    def __iter__(self):
        return iter(self.__list)


class Task:
    PERIODIC = micropython.const(1)
    ONE_SHOT = micropython.const(2)

    DEFAULT_TIMER_PERIOD_MS = micropython.const(5)
    DEFAULT_TIMEOUT_MS = micropython.const(5)

    __all_timers = []

    def __init__(self):
        Task.__all_timers.append(self)

    def init(self, mode=PERIODIC, freq=-1, period=-1, timeout=DEFAULT_TIMEOUT_MS, callback=None):
        raise NotImplementedError()

    def deinit(self):
        raise NotImplementedError()

    @property
    def running(self):
        raise NotImplementedError()

    @property
    def mode(self):
        raise NotImplementedError()

    @property
    def freq(self):
        raise NotImplementedError()

    @property
    def period(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def waiting(self):
        raise NotImplementedError()

    @staticmethod
    def get_all_timer_task():
        return iter(Task.__all_timers)

    @staticmethod
    def pause_all():
        for tim in Task.get_all_timer_task():
            tim.running = True

    @staticmethod
    def stop_all():
        for tim in Task.get_all_timer_task():
            tim.stop()

    @staticmethod
    def pause_all():
        for tim in Task.get_all_timer_task():
            tim.pause()
