import math
import time

import micropython

import servocontroller.servos
import timertask


class ServoController:
    __all_servos_attach = []

    def __init__(self, *args, **kwargs):
        self.__index = 0
        self.__servos = None
        self.attach(*args, **kwargs)

    def attach(self, index: int, servos: servocontroller.servos.Servos):
        self.__index = index
        self.__servos = servos

        ServoController.__all_servos_attach.append(hash(self))

    def dettach(self):
        self.__index = 0
        self.__servos = None
        ServoController.__all_servos_attach.remove(hash(self))

    @property
    def index(self):
        return self.__index

    def write(self, degrees: float):
        if self.__servos is not None:
            self.__servos.write(self.__index, math.ceil(degrees))

    def read(self) -> int:
        if self.__servos is not None:
            return self.__servos.read(self.__index)
        else:
            return 0

    def __hash__(self):
        return hash((self.__servos, self.index))


class ServoTask(ServoController):
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

    DEFAULT_TIMER_PERIOD_MS = 5

    __all_current_servos = []
    __all_current_task = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__last_time = time.ticks_ms()
        self.__start_time = time.ticks_ms()
        self.__delta_time = 1
        self.__tim = None
        self.__handler = {}
        self.__index = 0
        self.__servos = None
        self.__running = False
        self.__step = 0
        self.__last_degrees = 0
        self.__start_delay_ms = time.ticks_ms()
        self.__delay_ms = 0
        self.min = 0
        self.max = 180
        self.step = 0
        self.init(*args, **kwargs)

    def init(self, index: int, servos: servocontroller.servos.Servos, **kwargs):
        self.attach(index, servos)
        self.__last_degrees = self.read()
        self.__init_tim(kwargs.get('period'), kwargs.get('freq'))
        ServoTask.__all_current_task.append(self)

    def deinit(self):
        self.stop()
        self.__call_handler(ServoTask.IRQ_DEINIT)
        self.__handler.clear()

    def __init_tim(self, period=None, freq=None):
        self.__tim = timertask.Timer()
        if period:
            self.__tim.init(callback=self.__getcallback(), period=period)
        elif freq:
            self.__tim.init(callback=self.__getcallback(), freq=freq)
        else:
            self.__tim.init(callback=self.__getcallback(), period=ServoTask.DEFAULT_TIMER_PERIOD_MS)

        self.__running = True

        return self.__tim

    def irq(self, handler, trigger=IRQ_RUNNING, priority=1, wake=None, hard=False):
        if trigger not in self.__handler:
            self.__handler[trigger] = []

        if priority < 1:
            self.__handler[trigger] = [handler] + self.__handler[trigger]
        elif priority > 1:
            self.__handler[trigger].append(handler)
        else:
            self.__handler[trigger].append(handler)

    @property
    def delta_time(self):
        return self.__delta_time

    @property
    def running(self):
        return self.__running

    def write(self, degrees: float):
        self.__last_degrees = degrees
        super().write(degrees)

    def pause(self):
        self.__running = False

    def stop(self):
        self.__running = False
        self.__tim.deinit()
        self.__call_handler(ServoTask.IRQ_STOP)

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

        def inner(t: timertask.Timer):
            if time.ticks_diff(time.ticks_ms(), self.__start_delay_ms) >= self.__delay_ms:
                self.__start_delay_ms = time.ticks_ms()

            if time.ticks_diff(time.ticks_ms(), self.__start_delay_ms) < self.__delay_ms:
                self.__call_handler(ServoTask.IRQ_DELAY)
            else:
                self.__delay_ms = 0
                self.__call_handler(ServoTask.IRQ_LOOP)

                __last_degrees = self.read()
                if self.__last_degrees != __last_degrees:
                    self.__last_degrees = __last_degrees
                    self.__call_handler(ServoTask.IRQ_CHANGED)

                if not self.running or self.__servos is None:
                    self.__call_handler(ServoTask.IRQ_PAUSED)
                else:
                    self.__call_handler(ServoTask.IRQ_RUNNING)

                    if self.read() > self.max or self.read() < self.min:
                        self.__call_handler(ServoTask.IRQ_LIMIT)
                    else:
                        # self.write(self.read() + (self.step * self.delta_time))
                        self.__call_handler(ServoTask.IRQ_MOVED)

            self.__last_time = time.ticks_ms()
            self.__delta_time = time.ticks_diff(self.__last_time, self.__start_time)
            self.__start_time = time.ticks_ms()

        self.__call_handler(ServoTask.IRQ_INIT)

        return inner

    @staticmethod
    def get_all_task():
        return iter(ServoTask.__all_current_task)

    @staticmethod
    def stop_all():
        for servo in ServoTask.get_all_task():
            servo.stop()

    @staticmethod
    def pause_all():
        for servo in ServoTask.get_all_task():
            servo.pause()

    @staticmethod
    def run_all():
        for servo in ServoTask.get_all_task():
            servo.running = True


_FuncType = type(lambda x: x)


class Step:
    def __init__(self, expr=lambda x: x):
        self.__current = 0.0
        self.expr = expr
        self.speed = 1
        self.step = 0
        self.limit = 0, 180

    @property
    def current(self):
        return self.__current

    def bind(self, expr):
        self.expr = expr

    def forward(self):
        self.step += self.speed

    def back(self):
        self.step -= self.speed

    def modify(self):
        self.__current = self.expr(self.step)

    def __next__(self):
        self.modify()
        self.forward()
        return self.current

    def __floor__(self):
        return math.floor(self.current)

    def __ceil__(self):
        return math.ceil(self.current)


class Animate(timertask.Timer):
    def __init__(self, index: int, servos: servocontroller.servos.Servos, *args, **kwargs):
        self.__servo = ServoTask(index, servos)
        self.step = Step()
        super().__init__(*args, callback=self.__inner_callback, **kwargs)

    @property
    def servo(self):
        return self.__servo

    def __inner_callback(self, t):
        self.servo.write(next(self.step))
