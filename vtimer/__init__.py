import sys

try:
    if sys.platform not in ('esp32',):
        raise ImportError('maybe you do not need virtual timers')

    from vtimer._thread import ThreadTimer as Timer
    from vtimer._thread import ThreadTimer
    from vtimer._timer import VirtualTimer

    __all__ = ['Timer', 'ThreadTimer', 'VirtualTimer']
except ImportError or MemoryError:
    from machine import Timer
    from vtimer._timer import VirtualTimer

    __all__ = ['Timer', 'VirtualTimer']

if __name__ == '__main__':
    tim0 = Timer(-1)
    tim0.init(period=5, callback=lambda t: print('Hello world from Timer0'))

    tim1 = Timer(-1)
    tim1.init(period=25, callback=lambda t: print('Hello world from Timer1'))

    tim2 = Timer(-1)
    tim2.init(period=50, callback=lambda t: print('Hello world from Timer2'))

    tim3 = Timer(-1)
    tim3.init(period=150, callback=lambda t: print('Hello world from Timer3'))

    while True:
        ...
