import timertask.task
import timertask.timer
import uasyncio


class AsyncTimerTask(timertask.task.Task):
    def __init__(self, *args, **kwargs):
        timertask.task.Task.__init__(self)
        self.__tim = None
        self.__inner_callback = None
        self.__running = False
        self.__period = -1
        self.__freq = -1
        self.__mode = timertask.task.Task.ONE_SHOT
        self.timeout = 0
        self.init(*args, **kwargs)

    def init(self, mode=timertask.task.Task.PERIODIC, freq=-1, period=-1,
             timeout=timertask.task.Task.DEFAULT_TIMEOUT_MS, callback=None):
        self.__tim = timertask.timer.Timer(-1) if self.__tim is None else self.__tim
        self.__inner_callback = callback
        self.__mode = mode
        self.__period = period
        self.__freq = freq
        self.timeout = timeout
        if period > 0:
            self.__tim.init(callback=self.__callback, period=period, mode=mode)
        elif freq > 0:
            self.__tim.init(callback=self.__callback, freq=freq, mode=mode)
        else:
            self.__tim.init(callback=self.__callback, period=timertask.timer_task.Task.DEFAULT_TIMER_PERIOD_MS,
                            mode=mode)

        self.__running = True

        return self.__tim

    def deinit(self):
        self.stop()
        self.__tim = None
        self.__inner_callback = None

    @property
    def running(self):
        return self.__running

    @property
    def mode(self):
        return self.__mode

    @property
    def freq(self):
        return self.__freq

    @property
    def period(self):
        return self.__period

    def reset(self):
        self.init(self.mode, self.period, self.freq)

    def stop(self):
        self.__running = False
        self.__tim.deinit()

    def pause(self):
        self.__running = False

    def waiting(self):
        while self.running:
            pass

    def __callback(self, t):
        if not self.running:
            return

        if self.__inner_callback is not None:
            loop = uasyncio.get_event_loop()
            loop.run_until_complete(self.__run_async_function())

    async def __run_async_function(self):
        if self.__inner_callback is not None:
            try:
                await uasyncio.wait_for_ms(self.__inner_callback(self), self.timeout)
            except uasyncio.TimeoutError:
                pass

    @staticmethod
    def bind(_task, *args, **kwargs):
        def inner(func):
            _task.__inner_callback = func

        _task.init(*args, **kwargs)

        return inner


def bind(_task: timertask.timer_task.Task, *args, **kwargs):
    return AsyncTimerTask.bind(_task, *args, **kwargs)


if __name__ == '__main__':
    task0 = AsyncTimerTask()


    @bind(task0, period=250)
    async def my_task0(t):
        print('Hello world from Task0', t)


    task1 = AsyncTimerTask()


    @bind(task1, period=75)
    async def my_task1(t):
        print('Hello world from Task1', t)


    task2 = AsyncTimerTask()


    @bind(task2, period=50)
    async def my_task2(t):
        print('Hello world from Task2', t)
        await uasyncio.sleep_ms(5)
        print('Task is complete...')


    while True:
        print('Main thread is running!')
