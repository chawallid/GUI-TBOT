import serial
import time

from serial.serialutil import Timeout

ser = serial.Serial(
    port='COM16',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout= 1)
print(ser.name)
while True:
    line = ser.readline(ser.in_waiting)
    print(line)
    time.sleep(0.5)

ser.close()
