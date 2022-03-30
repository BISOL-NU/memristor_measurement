import pyvisa as visa
from time import sleep

rm = visa.ResourceManager()
GP_type="GPIB0"

dgen_name = GP_type+'::15::INSTR' #delay generator

DGen=rm.open_resource(dgen_name)
DGEN_BUFFER_PERIOD = 25e-9

### TEST FOR TRIGGER
pulse_on_period = 100e-9
pulse_off_period = pulse_on_period
pulse_number = 1
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
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
DGen.write(f"LOFF {bnc},0")
DGen.write(f"LPOL {bnc},1")
DGen.write(f"DLAY {channel_start},0,0") # Sets time offset for the first channel
DGen.write(f"DLAY {channel_end},{channel_start},{pulse_on_period}") # Set pulse duration

while True:
    DGen.write('*TRG')
    sleep(trig_period)