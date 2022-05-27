import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from instr_inter import SR570, A34410A
from time import sleep
import numpy as np

lna = SR570.SR570()
dmm = A34410A.A34410A()
a = list(range(0, 5000, 100))
b = list(range(5000, 0, -100))
c = list(range(0, -5000, -100))
d = list(range(-5000, 0, 100))
i = np.zeros(len(a+b+c+d))
sens = 0
lna.set_sens(sens)

while True:
    for ii, v in enumerate(a+b+c+d):
        lna.set_bias(v, delay=0)

        Sens_Loop=True
        while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
            #loop through sensitivity until no longer saturated, sense_loop => False
            if sens != lna.sens:
                print ('sens' ,sens)
                lna.set_sens(sens, 0)
            Test1 = dmm.read()
                        
            if -1.5<=np.log10(abs(Test1))<=.3: # this limit can change. 
                Sens_Loop=False
                i[ii]=lna.sens_table[sens]*Test1 
            elif -1>np.log10(abs(Test1)) and sens > 0:
                sens -= 1
            elif np.log10(abs(Test1))>.3 and sens < 27:
                sens += 1                   
            elif sens==0:
                Sens_Loop=False
                i[ii]=lna.sens_table[sens]*Test1
            elif sens==27:
                Sens_Loop=False
                i[ii]=lna.sens_table[sens]*Test1

        sleep(1e-6)
    
    a = 1