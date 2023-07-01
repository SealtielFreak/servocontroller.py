import time

import machine

import vtimer.timer


class VirtualTimer(vtimer.timer.NoTimer):
    __ALL_TIMERS = {}
    __GLOBAL_TIMER = None
    GLOBAL_FREQ = 1

    def __init__(self, *args, **kwargs):
        self.__interval = 1
        self.__id = -1
        self.__callback = None
        self.__mode = 0
        self.__next_time = 0
        if VirtualTimer.__GLOBAL_TIMER is None:
            VirtualTimer.__GLOBAL_TIMER = machine.Timer(-1)
            VirtualTimer.__GLOBAL_TIMER.init(mode=machine.Timer.PERIODIC, period=VirtualTimer.GLOBAL_FREQ,
                                             callback=VirtualTimer.__main_loop)
        self.init(*args, **kwargs)

    def init(self, id=-1, mode=vtimer.timer.NoTimer.PERIODIC, freq=-1, period=-1, callback=None):
        if freq != -1:
            self.__interval = 1 / freq
        elif period != -1:
            self.__interval = period / 1000
        if id == -1:
            VirtualTimer.__ALL_TIMERS[len(VirtualTimer.__ALL_TIMERS) + 1] = self
        else:
            VirtualTimer.__ALL_TIMERS[id] = self
        self.__id = id
        self.__callback = callback
        self.__mode = mode
        self.__next_time = time.ticks_us() + int(self.__interval * 1000000)

    def deinit(self):
        self.__stop()

    def __start(self):
        pass

    def __stop(self):
        pass

    def __valid_interval(self):
        return self.__interval > 0

    @staticmethod
    def __main_loop():
        for k, timer in VirtualTimer.__ALL_TIMERS.items():
            if not timer.__valid_interval():
                continue
            if time.ticks_diff(timer.__next_time, time.ticks_us()) <= 0:
                if timer.__callback is not None:
                    timer.__callback(timer)
                if timer.__mode == VirtualTimer.PERIODIC:
                    timer.__next_time += int(timer.__interval * 1000000)
                else:
                    VirtualTimer.__ALL_TIMERS.pop(k)
