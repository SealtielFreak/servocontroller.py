import timertask.task
import timertask.timer


class TimerTask(timertask.task.Task):
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
        self.__inner_callback = callback
        self.__tim = timertask.timer.Timer(-1) if self.__tim is None else self.__tim
        self.__mode = mode
        self.__period = period
        self.__freq = freq
        self.timeout = timeout
        if period > 0:
            self.__tim.init(callback=self.__callback, period=period, mode=mode)
        elif freq > 0:
            self.__tim.init(callback=self.__callback, freq=freq, mode=mode)
        else:
            self.__period = TimerTask.DEFAULT_TIMER_PERIOD_MS
            self.__tim.init(callback=self.__callback, period=TimerTask.DEFAULT_TIMER_PERIOD_MS, mode=mode)

        self.__running = True

        return self.__tim

    def deinit(self):
        self.__tim.deinit()

    @property
    def running(self):
        return self.__running

    @property
    def mode(self):
        return self.__mode

    @property
    def freq(self):
        return self.__freq

    @freq.setter
    def freq(self, freq):
        if freq <= 0:
            raise ValueError('invalid value')

        self.__period = -1
        self.__freq = freq
        self.init(mode=self.mode, freq=self.__freq)

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, period):
        if period <= 0:
            raise ValueError('invalid value')

        self.__period = period
        self.__freq = -1
        self.init(mode=self.mode, period=self.__period)

    def reset(self):
        self.init(mode=self.mode, period=self.__period, freq=self.__freq)

    def stop(self):
        self.__running = False
        self.deinit()

    def pause(self):
        self.__running = False

    def waiting(self):
        while self.running:
            pass

    def __callback(self, t):
        if not self.running:
            return

        if self.__inner_callback is not None:
            self.__inner_callback(self)

    @staticmethod
    def bind(_task, *args, **kwargs):
        def inner(func):
            _task.__inner_callback = func

        _task.init(*args, **kwargs)

        return inner


Timer = TimerTask
__all__ = ['Timer', 'TimerTask']


def bind(_task: TimerTask, *args, **kwargs):
    return TimerTask.bind(_task, *args, **kwargs)


if __name__ == '__main__':
    task0 = TimerTask()


    @bind(task0, period=250)
    def my_task0(t):
        print('Hello world from Task0')


    task1 = TimerTask()


    @bind(task1, period=75)
    def my_task1(t):
        print('Hello world from Task1')


    task2 = TimerTask()


    @bind(task2, period=50)
    def my_task2(t):
        print('Hello world from Task2')


    try:
        while True:
            print('Main thread is running!')
    except KeyboardInterrupt:
        TimerTask.stop_all()
