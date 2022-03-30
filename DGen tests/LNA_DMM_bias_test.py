from instr_inter import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from time import sleep
from tqdm import tqdm

DMM = A34410A.A34410A()
# Set low integration to read several voltages
LNA = SR570.SR570()

# Run the measurement loop to make sure that we are not overloaded0
def meas_voltage(sens, delay=.1, min_sens=0):
    LNA.write(f"SENS {sens}", delay+.1)
    Test1 = DMM.read()
    return Test1

DMM.set_integ_time(10)
delay = 0.1 
min_sens = 0
sens = min_sens

bias_v = np.concatenate((np.arange(0, 2500, 100),
                        np.arange(2500, 0, -100),
                        np.arange(0, -2500, -100),
                        np.arange(-2500, 1, 100)))
bias = np.zeros((bias_v.shape[0], 10))
changed_sens = np.full(bias.shape, False)
# Experimentally found sens table for the DMM
sens_table_mag = np.array([1, 11, 11, 11, 12, 12, 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14])
sens_table = np.concatenate((sens_table_mag, 
                               np.flip(sens_table_mag[1:-1]),
                               sens_table_mag, 
                               np.flip(sens_table_mag[1:])))
changed_sens = np.concatenate(([True], sens_table[1:] != sens_table[:-1]))
# Plot colors
color = cm.rainbow(np.linspace(0,1,bias_v.shape[0]))

for ii, v in tqdm(enumerate(bias_v)):
    LNA.set_bias(v)
    for jj in range(bias.shape[1]):
        bias[ii, jj] = meas_voltage(sens_table[ii], delay)

# Plotting for measurements
plt.figure()
for ii in tqdm(range(bias_v.shape[0])):
    for jj in range(bias.shape[1]):
        if jj == 0 and changed_sens[ii]:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], 'X', c=color[ii])
        else:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], '.', c=color[ii])

plt.xlabel(f'Meas # (Integ time = {10*1/60} s)')
plt.ylabel('Bias Voltage (V)')
plt.title(f'Filter Type: 12 dB LP, Filter Freq: 1 Hz')
plt.grid()
plt.xlim([0, bias.shape[1]*bias.shape[0]])
plt.ylim([-2.5, 2.5])
plt.tight_layout()
plt.show()
