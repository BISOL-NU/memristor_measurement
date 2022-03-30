from instr_inter import *
import matplotlib.pyplot as plt
import numpy as np
from time import sleep

relay = relay_inter.relay_inter()
relay.switch_relay(relay.NONE) # Close relay during setup
DGen = DG645.DG645()
DMM = A34410A.A34410A()
LNA = SR570.SR570()

# Function to measure current
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

# Configuring programming pulses on the DGen
pulse_on_period = 500e-6
pulse_off_period = pulse_on_period
pulse_number = 100
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
trig_freq = 1/trig_period
#voltage = 4
# Set integration time for the DMM,
#   previous interaction time is around .75s so using 100/60s integ time
#   This could very well change the interaction time
DMM.set_integ_time(10)
LNA.set_bias(200)

sens = 0 # Initial Sensitivity of measurement
pulse_num = np.array(range(1,101))
currents = np.empty((100, 5))
# Plot to show measured current over time
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()
plt.show()


currents[:] = np.NaN
# Postive Pulses
for v in [-2, 4]:
    relay.switch_relay(relay.NONE)
    DGen.config_burst(pulse_on_period, burst_period, pulse_number, trig_freq, v)
    if v < 0:
        idx_range = range(50)
    else:
        idx_range = range(50, 100)
    for ii in idx_range:
        # Start with pulse measurement
        relay.switch_relay(relay.DGEN)
        for _ in range(10):
            _, sens = meas_current(sens)
        DGen.trig_burst()
        relay.switch_relay(relay.LNA)
        for jj in range(5):
            currents[ii, jj], sens = meas_current(sens)
            if v > 0:
                plt.plot(ii, currents[ii, jj], 'ro')
            else:
                plt.plot(ii, currents[ii, jj], 'bo')
        plt.draw()
        plt.pause(0.001)

a = 1