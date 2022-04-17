import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import AV1010B
import numpy as np
from time import sleep

PGen = AV1010B.AV1010B()
PGen.set_trigger('HOLD')
while True:
    for v in np.arange(-10, 10, .25):
        for t in np.arange(10e-6, 30e-6, 10e-6):
            PGen.config_pulse(t, v)
            PGen.trig()