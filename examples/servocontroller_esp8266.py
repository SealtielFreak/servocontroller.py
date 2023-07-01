import time
import math
import machine

from servocontroller import ServoTask
from servocontroller.servos import ServosGPIO
from servocontroller.driver import DriverGPIO

if __name__ == '__main__':
    driver = DriverGPIO()
    driver.freq(50)
    driver.attach(3, machine.Pin(12))
    driver.attach(2, machine.Pin(13))
    driver.attach(1, machine.Pin(14))
    driver.attach(0, machine.Pin(4))

    servos = ServosGPIO(driver)

    servo0 = ServoTask(0, servos)
    servo1 = ServoTask(1, servos)
    servo2 = ServoTask(2, servos)
    servo3 = ServoTask(3, servos)
    
    while True:
        for i in range(0, 180, 5):
            for j in range(4):
                servos.write(j, i)
                time.sleep_ms(1)
                
        for i in reversed(range(0, 180, 5)):
            for j in range(4):
                servos.write(j, i)
                time.sleep_ms(1)
        
