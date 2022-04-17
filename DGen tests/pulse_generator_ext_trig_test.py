# Attempts to use the Delay generator to trigger the pulse generator
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import AV1010B, DG645
import numpy as np
from time import sleep

PGen = AV1010B.AV1010B()
PGen.set_trigger('EXT')
PGen.config_pulse(pulse_width='in')

pulse_on_period = 300e-3
pulse_off_period = pulse_on_period
pulse_number = 3
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
trig_freq = 1/trig_period
DGen = DG645.DG645()

while True:
    for v in [2.5, 5, 7.5, 10]:
        PGen.config_pulse(pulse_voltage=v)
        for t in np.arange(100e-3, 301e-3, 100e-3):
            DGen.config_burst(t, burst_period, pulse_number, trig_freq, 2)
            DGen.trig_burst()
