import math
import time

import micropython
import machine

import servocontroller.servos


class Step:
    DEFAULT_STEP = micropython.const(lambda x: x)

    def __init__(self, limits=(0, 180), step_callback=DEFAULT_STEP):
        self.__step_callback = step_callback
        self.min, self.max = limits
        self.step = 1
        self.angle = 0

    def __next__(self):
        _min, _max = self.min, self.max

        current_angle = self.angle

        angle = (self.__step_callback(self.step) + self.angle)

        if angle > _max or angle < _min:
            self.step *= -1
        else:
            self.angle = angle

        return current_angle


class Animator:
    IRQ_INIT = micropython.const(1)
    IRQ_RUNNING = micropython.const(2)
    IRQ_MOVED = micropython.const(3)
    IRQ_STOP = micropython.const(4)
    IRQ_PAUSED = micropython.const(5)
    IRQ_CHANGED = micropython.const(6)
    IRQ_LOOP = micropython.const(7)
    IRQ_LIMIT = micropython.const(8)
    IRQ_DEINIT = micropython.const(9)
    IRQ_DELAY = micropython.const(9)

    def __init__(self, *args, **kwargs):
        self.__last_time = time.ticks_ms()
        self.__start_time = time.ticks_ms()
        self.__delta_time = 1
        self.__tim = None
        self.__handler = {}
        self.__steps = {}
        self.__index = 0
        self.__servos = None
        self.__running = False
        self.__step = 0
        self.__last_degrees = 0
        self.__start_delay_ms = time.ticks_ms()
        self.__delay_ms = 0
        self.__tim = None
        self.__servos = None

    def init(self, servos: servocontroller.servos.Servos):
        self.__servos = servos

    def deinit(self):
        pass

    def irq(self, handler, trigger=IRQ_RUNNING, priority=1, wake=None, hard=False):
        if trigger not in self.__handler:
            self.__handler[trigger] = []

        if priority < 1:
            self.__handler[trigger] = [handler] + self.__handler[trigger]
        elif priority > 1:
            self.__handler[trigger].append(handler)
        else:
            self.__handler[trigger].append(handler)

    def step(self, index: int, step: Step):
        self.__steps[index] = step

    @property
    def delta_time(self):
        return self.__delta_time

    @property
    def running(self):
        return self.__running

    def pause(self):
        self.__running = False

    def stop(self):
        self.__running = False
        self.__tim.deinit()
        self.__call_handler(Animator.IRQ_STOP)

    def waiting(self):
        while self.running:
            pass

    def delay(self, sec: int):
        self.__delay_ms = sec * 1000

    def delay_ms(self, ms: int):
        self.__delay_ms = ms

    def __call_handler(self, trigger: int):
        if trigger in self.__handler:
            for handler in self.__handler[trigger]:
                handler(self)

    def __getcallback(self):
        self.__start_time = time.ticks_ms()

        def inner(t: machine.Timer):
            if time.ticks_diff(time.ticks_ms(), self.__start_delay_ms) >= self.__delay_ms:
                self.__start_delay_ms = time.ticks_ms()

            if time.ticks_diff(time.ticks_ms(), self.__start_delay_ms) < self.__delay_ms:
                self.__call_handler(Animator.IRQ_DELAY)
            else:
                self.__delay_ms = 0
                self.__call_handler(Animator.IRQ_LOOP)

                for i in self.__servos:
                    self.__servos.read(i)

                    __last_degrees = self.__servos.read(i)
                    if self.__last_degrees != __last_degrees:
                        self.__last_degrees = __last_degrees
                        self.__call_handler(Animator.IRQ_CHANGED)

                    if not self.running or self.__servos is None:
                        self.__call_handler(Animator.IRQ_PAUSED)
                    else:
                        self.__call_handler(Animator.IRQ_RUNNING)

                        if self.Animator() > self.max or self.read() < self.min:
                            self.__call_handler(Animator.IRQ_LIMIT)
                        else:
                            # self.write(self.read() + (self.step * self.delta_time))
                            self.__call_handler(Animator.IRQ_MOVED)

            self.__last_time = time.ticks_ms()
            self.__delta_time = time.ticks_diff(self.__last_time, self.__start_time)
            self.__start_time = time.ticks_ms()

        self.__call_handler(Animator.IRQ_INIT)

        return inner

    @staticmethod
    def __init_tim(period=None, freq=None):
        pass
