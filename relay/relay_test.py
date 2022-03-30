from time import sleep
import serial
from time import sleep

ser = serial.Serial('COM6') # Or whatever Arduino IDE identifies
while True:
    ser.write(bytearray([0])) 
    sleep(1)
    ser.write(bytearray([1]))
    sleep(1)
    ser.write(bytearray([2]))
    sleep(1)