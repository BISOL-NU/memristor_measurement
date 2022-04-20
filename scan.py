from instr_inter import *
import numpy as np
from time import sleep

def meas_current(sens, LNA, DMM, delay=.05, LNA_gui_var=None, DMM_gui_var=None, Sens_gui_var=None):
    def update_gui_vars(curr=None, volt=None, sens=None):
        if LNA_gui_var is not None and curr is not None:
            LNA_gui_var.set(f'Current: {curr:.2g}')
        if DMM_gui_var is not None and volt is not None:
            DMM_gui_var.set(f'DMM Voltage: {volt:.2g}')
        if Sens_gui_var is not None and sens is not None:
            Sens_gui_var.set(f'Sens: {LNA.sens_table[sens]}')

    Sens_Loop=True
    while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
        #loop through sensitivity until no longer saturated, sense_loop => False
        if sens != LNA.sens:
            update_gui_vars(sens=sens)
            #print ('sens' ,sens)
            LNA.set_sens(sens)
        Test1 = DMM.read()
                    
        if -1<=np.log10(abs(Test1))<=.3: # this limit can change. 
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            update_gui_vars(volt=Test1, curr=Dark_Current1)
            #print ("DMM voltage", Test1,"\ndark", Dark_Current1)    
        elif -1>np.log10(abs(Test1)) and sens > 0:
            sens -= 1
            sleep(delay+.1)
        elif np.log10(abs(Test1))>.3 and sens < 27:
            sens += 1                   
            sleep(delay+.1)
        elif sens==0:
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            update_gui_vars(volt=Test1, curr=Dark_Current1)
        elif sens==27:
            Sens_Loop=False
            Dark_Current1=LNA.sens_table[sens]*Test1
            update_gui_vars(volt=Test1, curr=Dark_Current1)
        
    return Dark_Current1, sens