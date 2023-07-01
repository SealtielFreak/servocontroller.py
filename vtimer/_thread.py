import _thread
import time

import vtimer.timer


class ThreadTimer(vtimer.timer.NoTimer):
    __ALL_TIMERS = {}
    __GLOBAL_THREAD = None
    __GLOBAL_THREAD_LOCK = _thread.allocate_lock()

    def __init__(self, *args, **kwargs):
        self.__interval = 1
        self.__id = -1
        self.__callback = None
        self.__mode = 0
        self.__next_time = 0
        if ThreadTimer.__GLOBAL_THREAD is None:
            ThreadTimer.__GLOBAL_THREAD = _thread.start_new_thread(ThreadTimer.__main_loop, ())
        self.init(*args, **kwargs)

    def init(self, id=-1, mode=vtimer.timer.NoTimer.PERIODIC, freq=-1, period=-1, callback=None):
        with ThreadTimer.__GLOBAL_THREAD_LOCK:
            if freq != -1:
                self.__interval = 1 / freq
            elif period != -1:
                self.__interval = period / 1000
            if id == -1 or id < 0:
                ThreadTimer.__ALL_TIMERS[len(ThreadTimer.__ALL_TIMERS) + 1] = self
            else:
                ThreadTimer.__ALL_TIMERS[id] = self
            self.__id = id
            self.__callback = callback
            self.__mode = mode
            self.__next_time = time.ticks_us() + int(self.__interval * 1000000)

    def deinit(self):
        with ThreadTimer.__GLOBAL_THREAD_LOCK:
            if self.__id in ThreadTimer.__ALL_TIMERS:
                ThreadTimer.__ALL_TIMERS.pop(self.__id)

    def __start(self):
        pass

    def __stop(self):
        with ThreadTimer.__GLOBAL_THREAD_LOCK:
            ThreadTimer.__ALL_TIMERS.clear()

    def __valid_interval(self):
        return self.__interval > 0

    @staticmethod
    def __main_loop():
        while True:
            with ThreadTimer.__GLOBAL_THREAD_LOCK:
                for k, timer in ThreadTimer.__ALL_TIMERS.items():
                    if not timer.__valid_interval():
                        continue
                    if time.ticks_diff(timer.__next_time, time.ticks_us()) <= 0:
                        if timer.__callback is not None:
                            timer.__callback(timer)
                        if timer.__mode == ThreadTimer.PERIODIC:
                            timer.__next_time += int(timer.__interval * 1000000)
                        else:
                            ThreadTimer.__ALL_TIMERS.pop(k)
            time.sleep_us(5)
