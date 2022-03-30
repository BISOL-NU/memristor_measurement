from instr_inter import *
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
from tqdm import tqdm

DMM = A34410A.A34410A()
LNA = SR570.SR570()

def meas_current(sens, delay=.05):
    Sens_Loop=True
    while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
        #loop through sensitivity until no longer saturated, sense_loop => False
        print ('sens' ,sens)
        LNA.write(f"SENS {sens}", delay+.1)
        Test1 = DMM.read()
                    
        if -2<=np.log10(abs(Test1))<=.7: # this limit can change. 
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            print ("DMM voltage", Test1,"\ndark", Dark_Current1)
        elif sens<27:    
            if -2>np.log10(abs(Test1)):
                sens -= 1
            elif np.log10(abs(Test1))>.7:
                sens += 1                   
            sleep(delay+.1)
        else:
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            print ("dark", Dark_Current1,"\nMaximum Sens _ Take Care!!!!")
    return Dark_Current1, sens

LNA.set_bias(0)
bias_v = np.concatenate((np.arange(0, 2500, 100),
                        np.arange(2500, 0, -100),
                        np.arange(0, -2500, -100),
                        np.arange(-2500, 1, 100)))
delay = .1

sens = 0
curr_wo_offset = np.zeros(bias_v.shape[0])
DMM.set_integ_time(10)
for ii, v in tqdm(enumerate(bias_v)):
    LNA.set_bias(v)
    curr_wo_offset[ii], sens = meas_current(sens, delay)

# Take an measurement with zero bias to detect the current floor
DMM.set_integ_time(100)
curr_floor, sens = meas_current(0)
LNA.set_input_offset(-curr_floor)

curr = np.zeros(bias_v.shape[0])
DMM.set_integ_time(10)
for ii, v in tqdm(enumerate(bias_v)):
    LNA.set_bias(v)
    curr[ii], sens = meas_current(sens, delay)

plt.figure()
plt.plot(bias_v, abs(curr_wo_offset), 'bo', label='W/O Offset')
plt.plot(bias_v, abs(curr), 'ro', label='Offset')

plt.legend()
plt.yscale('log')
plt.xlabel('Bias Voltage (V)')
plt.ylabel('Current (V)')
plt.title(f'Filter Type: 12 dB LP, Filter Freq: 1 Hz, Integ time = 1/6 s')
plt.tight_layout()
plt.show()