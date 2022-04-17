import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import os
from time import sleep, time
from tqdm import tqdm
from math import ceil
from datetime import datetime

relay = relay_inter.relay_inter()
relay.switch_relay(relay.LNA) # Close relay during setup

DMM = A34410A.A34410A()
# Set low integration to read several voltages
#LNA = SR570.SR570(filter_type=None)
filter_type='6dB'
filter_freq=1
gain_mode='low_drift'
LNA = SR570.SR570(filter_type=filter_type, filter_freq=filter_freq, gain_mode=gain_mode)
#cutoff_freq = 1 # Twice of 1 Hz

integ_time=1
DMM.set_integ_time(integ_time)
delay = 0.1 
sens = 0 

now = datetime.now()
date = now.strftime('%Y-%m-%d')
dir_name = f"C:\\Users\\Lab User\\Documents\\Memristor\\Measurements\\Device Exploration\\{date}"
if not os.path.exists(dir_name):
    os.mkdir(dir_name)
array_name = 'FIB1'
device_name = 'C2'

v_max = 3000
v_step = 1000
step_0_max = np.arange(0, v_max, v_step)
step_max_0 = np.arange(v_max, 0, -v_step)
step_0_neg_max = np.arange(0, -v_max, -v_step)
step_neg_max_0 = np.arange(-v_max, 1, v_step)
num_steps = [step_0_max.size, step_max_0.size, step_0_neg_max.size, step_neg_max_0.size]
bias_v = np.concatenate((step_0_max,
                         step_max_0,
                         step_0_neg_max,
                         step_neg_max_0))
bias = np.zeros((bias_v.shape[0], 25))
changed_sens = np.full(bias.shape, False)

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

# Get the noise floor and subtract it
LNA.set_bias(0)
for _ in range(10):
    _, sens = meas_current(sens, delay)
curr_floor = np.zeros(10)
for ii in range(10):
     curr_floor[ii], sens = meas_current(sens, delay)
curr_floor_mean = np.mean(curr_floor)
#LNA.set_input_offset(curr_floor_mean)

for ii, v in tqdm(enumerate(bias_v)):
    print(f'Bias: {v} V')
    LNA.set_bias(v)
    LNA.reset_filter_caps()
    sleep(1.5)

    # Take a measurement with a long integration time
    # Value is discharged
    #DMM.set_integ_time(100)
    for _ in range(10):
         _, sens = meas_current(sens, delay)
    #DMM.set_integ_time(10)
    #sleep(1)

    # Take groups of measurements until stdev is lower than 1/e of the sensitivity
    while True:
        for jj in range(bias.shape[1]):
            # t = time()
            bias[ii, jj], sens_out = meas_current(sens, delay)
            #bias[ii, jj] -= curr_floor_mean
            if sens_out != sens:
                changed_sens[ii, jj]= True
                sens = sens_out
            
            # ecllipsed_time = time() - t
            # print(f'Loop time: {ecllipsed_time}')
        
        mean_curr = np.mean(bias[ii])
        diff = np.abs(bias[ii] - mean_curr) / LNA.sens_table[sens]
        if not any(np.abs(diff) > 3*np.e):
            break
        else:
            for _ in range(10):
                 _, sens = meas_current(sens, delay)
            # DMM.set_integ_time(100)
            # meas_current(sens, delay)
            # DMM.set_integ_time(10)
            # sleep(1)
    
    

# Plotting for measurements
# Plot colors
sweep_colors = np.zeros((0,4))
for colormap, steps in zip([cm.Purples, cm.Blues, cm.Greens, cm.Oranges], num_steps):
    unique_colors = colormap(np.linspace(.5,1,steps))
    #color = np.array([unique_colors] * ceil(steps/100))
    color = unique_colors.flatten().reshape(-1, 4)
    sweep_colors = np.vstack((sweep_colors, color))
f1 = plt.figure()
for ii in tqdm(range(bias_v.shape[0])):
    for jj in range(bias.shape[1]):
        if jj == 0 and changed_sens[ii, jj]:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], 'X', c=sweep_colors[ii])
        else:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], '.', c=sweep_colors[ii])

plt.xlabel(f'Meas #')
plt.ylabel('Open Current (A)')
if filter_type is not None:
    plt.title(f'{array_name}_{device_name} - Filter Type: {filter_type}, Filter Freq: {filter_freq} Hz, Integ time: {integ_time}/60 s')
else:
    plt.title(f'{array_name}_{device_name} - Filter Type: None, Integ time:  {integ_time}/60 s')
plt.grid()
plt.xlim([0, bias.shape[1]*bias.shape[0]])
#plt.yscale('symlog', linthresh=1e-12, linscale=1)
#plt.ylim([-2.5, 2.5])
#plt.yscale('log')

# Get current axis and add labels for the voltages
ax1 = plt.gca()
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
tick_pos = np.hstack(([0], np.cumsum(num_steps)*bias.shape[1]))
tick_labels = ["0V", f'{v_max/1000}V', "0V", f'-{v_max/1000}V', '0V']
ax2.set_xticks(tick_pos)
ax2.set_xticklabels(tick_labels)

plt.tight_layout()

f2 = plt.figure()
for ii in tqdm(range(bias_v.shape[0])):
    for jj in range(bias.shape[1]):
        if jj == 0 and changed_sens[ii, jj]:
            plt.plot(bias_v[ii], bias[ii,jj], 'X', c=sweep_colors[ii])
        else:
            plt.plot(bias_v[ii], bias[ii,jj], '.', c=sweep_colors[ii])

plt.xlabel(f'Bias Voltage (mV)')
plt.ylabel('Current (A)')
if filter_type is not None:
    plt.title(f'{array_name}_{device_name} - Filter Type: {filter_type}, Filter Freq: {filter_freq} Hz, Integ time: {integ_time}/60 s')
else:
    plt.title(f'{array_name}_{device_name} - Filter Type: None, Integ time:  {integ_time}/60 s')
#plt.title(f'Filter Type: None, Integ time: 0.0033 s')
plt.grid()
#plt.yscale('symlog', linthresh=1e-12, linscale=1)
#plt.ylim([-2.5, 2.5])
#plt.yscale('log')
plt.tight_layout()

# save plot in Device Exploration Directory
if filter_type is not None:
    filter_str = f'LP{filter_type}{filter_freq}Hz'
else:
    filter_str = 'None'
title = f'{array_name}_{device_name}_{filter_str}_Integ{integ_time}'
f1.savefig(os.path.join(dir_name, f'{title}.png'))
f2.savefig(os.path.join(dir_name, f'{title}_alt.png'))

save_arr = np.hstack((np.expand_dims(bias_v, 1), bias))
np.savetxt(os.path.join(dir_name, f'{title}.csv'), save_arr, delimiter=",")

plt.show()
a=1
