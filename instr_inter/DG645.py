import pyvisa as visa
from time import sleep

class DG645:
    def __init__(self,
                 name='GPIB0::15::INSTR',
                 pulse_on_period = 100e-6,
                 burst_period=200e-6,
                 pulse_number=1,
                 trig_freq=400e6,
                 bnc='1', channel_start='2', channel_end='3'):
        self.rm = visa.ResourceManager()
        self.pulse_on_period = pulse_on_period
        self.burst_period = burst_period
        self.pulse_number = pulse_number
        self.trig_freq = trig_freq

        self.bnc = bnc # AB
        self.channel_start = channel_start # A
        self.channel_end = channel_end # B

        try:
            if not name in self.rm.list_resources(name):
                raise visa.VisaIOError(1) #randomly chosen error code
            DGen=self.rm.open_resource(name)

        except visa.VisaIOError:
            raise Exception("Not attached to delay generator")
        
        ## Configurations for the burst and trigger
        _ = DGen.write("*RST") # Reset settings
        _ = DGen.write('*CLS')# Clear all errors

        DGen.write('BURT 1') # Only output t0 at first delay cycle
        DGen.write('TSRC 5') # Set single trigger
        DGen.write("BURM 1") # Enable burst
        DGen.write("BURD 0") # Delay from trigger to burst

        ## Configurations for the individual channel (A and B)
        DGen.write(f"LOFF {self.bnc},0")
        DGen.write(f"LPOL {self.bnc},1")
        DGen.write(f"DLAY {self.channel_start},0,0") # Sets time offset for the first channel
        DGen.write(f"DLAY {self.channel_end},{channel_start},{pulse_on_period}") # Set pulse duration

        DGen.write('*WAI') # Wait for all prior commands to be completed
        
        self.DGen = DGen
    
    def config_burst(self, pulse_on_period, burst_period, pulse_number, 
                           trig_freq, voltage, bnc=None, channel_start=None, channel_end=None):
        # Trigger relays to disconnect DGen before triggering the burst
        #   Otherwise there might be a small voltage spike due to offset
        assert(voltage >= -2 and voltage <= 5)

        if bnc is not None:
            self.bnc = bnc
        if channel_start is not None:
            self.channel_start = channel_start
        if channel_end is not None:
            self.channel_end = channel_end

        if voltage > 0:
            self.DGen.write(f"LPOL {self.bnc},1")
            self.DGen.write(f"LOFF {self.bnc},0")
        else:
            self.DGen.write(f"LPOL {self.bnc},0")
            self.DGen.write(f"LOFF {self.bnc},{voltage}")
        self.DGen.write(f"LAMP {self.bnc},{abs(voltage)}")

        self.pulse_on_period = pulse_on_period
        self.burst_period = burst_period
        self.pulse_number = pulse_number
        self.trig_freq = trig_freq
        self.DGen.write(f"DLAY {self.channel_end},{self.channel_start},{pulse_on_period}") # Set pulse duration
        self.DGen.write(f"BURP {self.burst_period}") # Burst Period (Time between delay cycles)
        self.DGen.write(f"BURC {self.pulse_number}") # Burst count
        self.DGen.write(f"TRAT {self.trig_freq}") # Trigger frequency
        self.DGen.write('*WAI') # Wait for all prior commands to be completed
    
    def trig_burst(self):
        self.DGen.write('*TRG')
        self.DGen.write('*WAI') # Wait for all prior commands to be completed
        sleep(1/self.trig_freq) # Wait for full duration of the burst

    def check_error(self):
        # Check for errors on the delay generator,
        #   Returns a list with all error messages, might be empty
        err = []
        while True:
            err.append(self.DGen.write('LERR?'))
            # 0 indicates that there are no errors
            if err[-1] == 0:
                err.pop(-1)
                break

        return err
        