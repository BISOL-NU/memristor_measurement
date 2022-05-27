from asyncio.windows_events import ERROR_CONNECTION_REFUSED
import pyvisa as visa
import serial
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

v_bias = np.linspace(0,1000,101)

name='GPIB0::22::INSTR'
rm = visa.ResourceManager()
DMM = rm.open_resource(name)
port='COM9'
baud=9600
ser = serial.Serial(port,baud,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_TWO)
sens_table = [1e-12, 2e-12, 5e-12, 1e-11, 2e-11, 5e-11, 1e-10, 2e-10, 5e-10, 1e-9, 2e-9, 5e-9, 1e-8, 
                 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]
n=0
ser.write(f'SENS {n};\r\n'.encode('utf-8'))

i = np.zeros([v_bias.size])

for ii in range(0,v_bias.size):
    ser.write(f'BSLV {round(v_bias[ii])};\r\n'.encode('utf-8'))

    sleep(.2)
    DMM.write('READ?')
    v_result = float(DMM.read())

    while v_result >=3 or v_result <= -3:
        n= n+1
        ser.write(f'SENS {n};\r\n'.encode('utf-8'))
        sleep(.2)
        DMM.write('READ?')
        v_result = float(DMM.read())

    i[ii] = v_result* sens_table[n]

plt.figure()
plt.plot(v_bias, i)
plt.show()
