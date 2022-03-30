from instr_inter import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from time import sleep
from tqdm import tqdm
from math import ceil

relay = relay_inter.relay_inter()
relay.switch_relay(relay.LNA) # Close relay during setup

DMM = A34410A.A34410A()
# Set low integration to read several voltages
LNA = SR570.SR570(filter_type=None, gain_mode='low_drift')
#cutoff_freq = 1 # Twice of 1 Hz

# Run the measurement loop to make sure that we are not overloaded
def meas_current(sens, delay=.05):
    Sens_Loop=True
    while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
        #loop through sensitivity until no longer saturated, sense_loop => False
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


DMM.set_integ_time(100)
delay = 0.1 
sens = 0

bias_v = np.concatenate((np.arange(0, 2500, 100),
                        np.arange(2500, 0, -100),
                        np.arange(0, -2500, -100),
                        np.arange(-2500, 1, 100)))
bias = np.zeros((bias_v.shape[0], 5))
changed_sens = np.full(bias.shape, False)

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
    #sleep(2)

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
            bias[ii, jj], sens_out = meas_current(sens, delay)
            #bias[ii, jj] -= curr_floor_mean
            if sens_out != sens:
                changed_sens[ii, jj]= True
                sens = sens_out
        
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
unique_colors = cm.tab20(np.linspace(0,1,20))
color = np.array([unique_colors] * ceil(bias_v.shape[0]/20))
color = color.flatten().reshape(-1, 4)

plt.figure()
for ii in tqdm(range(bias_v.shape[0])):
    for jj in range(bias.shape[1]):
        if jj == 0 and changed_sens[ii, jj]:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], 'X', c=color[ii])
        else:
            plt.plot(ii*bias.shape[1]+jj, bias[ii,jj], '.', c=color[ii])

plt.xlabel(f'Meas #')
plt.ylabel('Open Current (A)')
#plt.title(f'Filter Type: 12 dB, Filter Freq: 1 Hz, Integ time: 1/6 s')
plt.title(f'Filter Type: None, Integ time: 10/6 s')
plt.grid()
plt.xlim([0, bias.shape[1]*bias.shape[0]])
#plt.yscale('symlog', linthresh=1e-12, linscale=1)
#plt.ylim([-2.5, 2.5])
plt.tight_layout()

plt.figure()
for ii in tqdm(range(bias_v.shape[0])):
    for jj in range(bias.shape[1]):
        if jj == 0 and changed_sens[ii, jj]:
            plt.plot(bias_v[ii], bias[ii,jj], 'X', c=color[ii])
        else:
            plt.plot(bias_v[ii], bias[ii,jj], '.', c=color[ii])

plt.xlabel(f'Bias Voltage (mV)')
plt.ylabel('Current (A)')
#plt.title(f'Filter Type: 12 dB, Filter Freq: 1 Hz, Integ time: 1/6 s')
plt.title(f'Filter Type: None, Integ time: 10/6 s')
plt.grid()
#plt.yscale('symlog', linthresh=1e-12, linscale=1)
#plt.ylim([-2.5, 2.5])
plt.tight_layout()

# plt.figure()
# for ii in tqdm(range(bias_v.shape[0])):
#     for jj in range(bias.shape[1]):
#         if jj == 0 and changed_sens[ii,jj]:
#             plt.plot(ii*bias.shape[1]+jj, abs(bias[ii,jj]), 'X', c=color[ii])
#         else:
#             plt.plot(ii*bias.shape[1]+jj, abs(bias[ii,jj]), '.', c=color[ii])

# plt.xlabel(f'Meas #')
# plt.ylabel('Open Current (A)')
# plt.title(f'Filter Type: 12 dB, Filter Freq: 1 Hz, Integ time: 1/6 s')
# plt.grid()
# plt.xlim([0, bias.shape[1]*bias.shape[0]])
# plt.yscale('log')
# #plt.ylim([-2.5, 2.5])
# plt.tight_layout()
plt.show()
