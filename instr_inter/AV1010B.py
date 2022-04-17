import pyvisa as visa
from time import sleep

class AV1010B:
    def __init__(self, name='GPIB0::11::INSTR', pulse_width=100e-9, voltage=0):
        self.rm = visa.ResourceManager()

        try:
            if not name in self.rm.list_resources(name):
                raise visa.VisaIOError(1) #randomly chosen error code
            PGen=self.rm.open_resource(name)

        except visa.VisaIOError:
            raise Exception("Not attached to pulse generator")    

        self.pulse_width = pulse_width
        self.pulse_voltage = voltage
        PGen.write('*rst')
        PGen.write(f'pulse:width {pulse_width}')
        PGen.write('pulse:delay 0')
        PGen.write(f'voltage {voltage}')
        PGen.write('output:impedance 50')
        PGen.write('output:load 10000')
        PGen.write('output on')
        self.PGen = PGen
    
    def set_trigger(self, source):
        assert(source in ['INT', 'EXT', 'MAN', 'HOLD', 'IMM'])
        self.PGen.write(f'trig:sour {source}')
    
    def trig(self):
        self.set_trigger('IMM')
    
    def config_pulse(self, pulse_width=None, pulse_voltage=None):
        if pulse_width != self.pulse_width and pulse_width is not None:
            self.pulse_width = pulse_width
            self.PGen.write(f'pulse:width {pulse_width}')
        if pulse_voltage != self.pulse_voltage and pulse_voltage is not None:
            self.pulse_voltage = pulse_voltage
            self.PGen.write(f'voltage {pulse_voltage}')
