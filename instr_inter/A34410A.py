import pyvisa as visa
from time import sleep

class A34410A:
    integ_times = [.006, .02, 0.06, .2, 1, 2, 10, 100]

    def __init__(self, name='GPIB0::22::INSTR'): 
        try:
            rm = visa.ResourceManager()
            if not name in rm.list_resources(name):
                raise visa.VisaIOError(1) #randomly chosen error code
            self.DMM = rm.open_resource(name)  ## Digital Multi Meter Agilent 34410A
            self.DMM.write('*RST') 
            sleep(.1)
            self.DMM.write('CONF:VOLT:DC 10') 
            sleep(.1)
            self.DMM.write('VOLT:DC:NPLC 10') 
            sleep(.1)
            self.DMM.write('VOLT:DC:IMP:AUTO 1')
            sleep(.1)
            #self.DMM.write('VOLT::DC:ZERO:AUTO ONCE')

        except visa.VisaIOError:
            raise Exception("Not attached to Digital Multimeter")
    
    def read(self):
        self.DMM.write('READ?')
        return float(self.DMM.read())
    
    def set_integ_time(self,t=1):
        assert(t in self.integ_times)
        self.DMM.write(f'VOLT:DC:NPLC {t}')