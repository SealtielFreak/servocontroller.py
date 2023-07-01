import sys

try:
    if sys.platform in ('esp32',):
        from vtimer import Timer
    else:
        raise ImportError('platform no found')
except ImportError or MemoryError:
    from machine import Timer
