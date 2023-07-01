import time
import math
import machine

from servocontroller import ServoTask, Animate, Step
from servocontroller.servos import ServosGPIO
from servocontroller.driver import DriverGPIO


def func(x):
    return math.cos(x / 30) * math.sin(x / 60) * 90 + 90


if __name__ == '__main__':
    driver = DriverGPIO()
    driver.freq(50)
    driver.attach(3, machine.Pin(19))
    driver.attach(2, machine.Pin(21))
    driver.attach(1, machine.Pin(22))
    driver.attach(0, machine.Pin(23))

    servos = ServosGPIO(driver)
    
    anim0 = Animate(0, servos)
    anim0.step.expr = func
    anim0.step.speed = 1.5
    print(anim0.period)
    # anim0.period = 15
    print(anim0.period, anim0.running)
    # anim0.servo.irq(lambda servo: print(f"Servo[{servo.index}] is running, and current degrees:", servo.read()))
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        ServoTask.stop_all()
    