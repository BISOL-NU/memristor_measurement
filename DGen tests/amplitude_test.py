import pyvisa as visa
from time import sleep
from numpy import arange

## README
# Some limitations show by this test
# 1)    Some commands need additional processing time otherwise,
#       there will be an read error from the DGen, a simple fix is to
#       assign a dummy variable at the output of the write function.
#       For a practical case, it might be easier to make a wrapper function
# 2)    When going from negative to positive or vice versa
#       There is a brief blip in the amplitude by necessity
#       There doesn't seem to be a way to avoid this.
#       In fact, ANY offset switches will result in a brief voltage pulse.
#       For memristor measurement setup, disconnect relay before changing voltage
# 3)    Pulses seem largely restricted to +- 2v to +- 0.5V, You can go higher,
#       but the offset only goes to +- 2V 

rm = visa.ResourceManager()
lis=rm.list_resources()
print ("avaliable modules:",lis)
GP_type="GPIB0"

dgen_name = GP_type+'::4::INSTR' #delay generator

DGen=rm.open_resource(dgen_name)
DGEN_BUFFER_PERIOD = 25e-9

### TEST FOR TRIGGER
pulse_on_period = 100e-6
pulse_off_period = pulse_on_period
pulse_number = 20
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)#*2
trig_freq = 1/burst_period

## Configurations for the burst and trigger
_ = DGen.write("*RST") # Reset settings
_ = DGen.write('*CLS')# Clear all errors

DGen.write('BURT 1') # Only output t0 at first delay cycle
DGen.write('TSRC 5') # Set single trigger
DGen.write("BURM 1") # Enable burst
DGen.write("BURD 0") # Delay from trigger to burst
DGen.write(f"BURP {burst_period}") # Burst Period (Time between delay cycles)
DGen.write(f"BURC {pulse_number}") # Burst count
DGen.write(f"TRAT {trig_freq}") # Trigger frequency

## Configurations for the individual channel (A and B)
bnc = '1' # AB
channel_start = '2' # A
channel_end = '3' # B
DGen.write(f"DLAY {channel_start},0,0") # Sets time offset for the first channel
DGen.write(f"DLAY {channel_end},{channel_start},{pulse_on_period}") # Set pulse duration

while True:
    # Set postive amplitude steps
    DGen.write(f"LOFF {bnc},0")
    DGen.write(f"LPOL {bnc},1")
    #DGen.write(f"SPLA {bnc},1")
    for v in arange(.5,5,.25):
        DGen.write(f"LAMP {bnc},{v}")
        DGen.write('*TRG')
        sleep(trig_period)
    # Set postive amplitude steps
    #DGen.write(f"LOFF {bnc},0")
    DGen.write(f"LAMP {bnc},2")
    DGen.write(f"LPOL {bnc},0")
    #DGen.write(f"SPLA {bnc},0")
    for v in arange(2,.5,-.25):
        DGen.write(f"LOFF {bnc},{-v}")
        DGen.write(f"LAMP {bnc},{v}")
        #DGen.write(f"SSLA {bnc},{v}")
        DGen.write('*TRG')
        sleep(trig_period)
    