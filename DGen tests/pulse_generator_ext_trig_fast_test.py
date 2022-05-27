# Attempts to use the Delay generator to trigger the pulse generator
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import AV1010B, DG645
import numpy as np
from time import sleep

PGen = AV1010B.AV1010B()
PGen.set_trigger('EXT')
PGen.config_pulse(pulse_voltage=2, pulse_width='in')

pulse_on_period = 50e-9
pulse_off_period = pulse_on_period
pulse_number = 1000
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
trig_freq = 1/trig_period
DGen = DG645.DG645()

DGen.config_burst(pulse_on_period, burst_period, pulse_number, trig_freq, 2, 
                    bnc=1, channel_start=2, channel_end=3)
DGen.config_burst(pulse_on_period, burst_period, pulse_number, trig_freq, 2, 
                    bnc=2, channel_start=4, channel_end=5)
while True:
    DGen.trig_burst()
