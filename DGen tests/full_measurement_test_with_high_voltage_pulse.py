import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import *
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
from datetime import datetime
import os

relay = relay_inter.relay_inter()
relay.switch_relay(relay.NONE) # Close relay during setup
DGen = DG645.DG645()
DMM = A34410A.A34410A()
filter_type='6dB'
filter_freq=1
gain_mode='low_drift'
LNA = SR570.SR570(filter_type=filter_type, filter_freq=filter_freq, gain_mode=gain_mode)
PGen = AV1010B.AV1010B()
PGen.set_trigger('EXT')

now = datetime.now()
date = now.strftime('%Y-%m-%d')
dir_name = f"C:\\Users\\Lab User\\Documents\\Memristor\\Measurements\\Device Exploration\\{date}"
if not os.path.exists(dir_name):
    os.mkdir(dir_name)
array_name = 'FIB1'
device_name = 'A3'
lna_bias = 200
v_sweep = [-5, 5]
num_bursts = 10
#pulse_num = np.array(range(1,101))
currents = np.empty((len(v_sweep)*num_bursts, 10))
currents[:] = np.NaN

# Configuring programming pulses on the DGen
pulse_on_period = 500e-6
pulse_off_period = pulse_on_period
pulse_number = 100
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
trig_freq = 1/trig_period
# Set integration time for the DMM,
#   previous interaction time is around .75s so using 100/60s integ time
#   This could very well change the interaction time
integ_time = 1
DMM.set_integ_time(integ_time)
LNA.set_bias(lna_bias)

# Run the measurement loop to make sure that we are not overloaded
def meas_current(sens, delay=.05):
    Sens_Loop=True
    while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
        #loop through sensitivity until no longer saturated, sense_loop => False
        if sens != LNA.sens:
            print ('sens' ,sens)
            LNA.set_sens(sens)
        Test1 = DMM.read()
                    
        if -1<=np.log10(abs(Test1))<=.3: # this limit can change. 
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            print ("DMM voltage", Test1,"\ndark", Dark_Current1)    
        elif -1>np.log10(abs(Test1)) and sens > 0:
            sens -= 1
            sleep(delay+.1)
        elif np.log10(abs(Test1))>.3 and sens < 27:
            sens += 1                   
            sleep(delay+.1)
        elif sens==0:
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            print ("dark", Dark_Current1,"\nMinimum Sens")
        elif sens==27:
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            print ("dark", Dark_Current1,"\nMaximum Sens _ Take Care!!!!")
        
    return Dark_Current1, sens

sens = 0 # Initial Sensitivity of measurement
# Plot to show measured current over time
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()
plt.show()
device_str = f'{array_name}_{device_name}'
if filter_type is not None:
    filter_str = f'Filter Type: {filter_type}, Filter Freq: {filter_freq} Hz, Integ time: {integ_time}/60 s'
else:
    filter_str = f'Filter Type: None, Integ time: {integ_time}/60 s'
pulse_str = f'Pulse: {v_sweep[0]}V (RED) {pulse_on_period}s X {pulse_number}\n{v_sweep[1]}V (BLUE) {pulse_on_period}s X {pulse_number}'
lna_str = f'LNA Meas Bias: {lna_bias/100} V'

plt.title(f'{device_str}\n{filter_str}\n{pulse_str}\n{lna_str}')
plt.tight_layout()
# Postive Pulses 50 * Postive and 50 * negative
DGen.config_burst(pulse_on_period, burst_period, pulse_number, trig_freq, 2, 
                    bnc=1, channel_start=2, channel_end=3)
DGen.config_burst(pulse_on_period, burst_period, pulse_number, trig_freq, 2, 
                    bnc=2, channel_start=4, channel_end=5)

for v_idx, v in enumerate(v_sweep):
    relay.switch_relay(relay.NONE)
    PGen.config_pulse(pulse_voltage=v, pulse_width='in')
    sleep(2)

    idx_range = range(v_idx*num_bursts,(v_idx+1)*num_bursts)
    for ii in idx_range:
        # Start with pulse measurement
        relay.switch_relay(relay.DGEN)
        # for _ in range(10):
        #     _, sens = meas_current(sens)
        DGen.trig_burst()
        relay.switch_relay(relay.LNA)
        sleep(5)

        for jj in range(currents.shape[1]):
            currents[ii, jj], sens = meas_current(sens)
            if v_idx == 0:
                plt.plot(ii, currents[ii, jj], 'ro')
            else:
                plt.plot(ii, currents[ii, jj], 'bo')
        plt.draw()
        plt.pause(0.01)

device_str = f'{array_name}_{device_name}'
if filter_type is not None:
    filter_str = f'LP{filter_type}_{filter_freq}Hz'
else:
    filter_str = f'None'
integ_str = f'Integ_{integ_time}'
lna_str = f'Meas_Bias_{lna_bias}'
title_str = f'{device_str}-{filter_str}-{integ_str}-{lna_str}'
plt.tight_layout()
fig.savefig(os.path.join(dir_name, f'{title_str}.png'))

# Make the array to save the file
# The first 3 column of the array should contain the pulse information
pulse_info = np.ones((currents.shape[0], 3))
pulse_info[:, 0] = pulse_on_period
pulse_info[:, 1] = pulse_number
for ii, v in enumerate(v_sweep):
    pulse_info[ii*num_bursts:(ii+1)*num_bursts, 2] = v
save_arr = np.hstack((pulse_info, currents))
np.savetxt(os.path.join(dir_name, f'{title_str}.csv'), save_arr, delimiter=',')

a = 1