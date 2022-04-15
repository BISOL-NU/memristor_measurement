import serial
from time import sleep
import numpy as np

class SR570:
    filters = {None: 5, '6dB':3, '12dB':4}
    filter_freqs = [.03, .1, .3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10e3, 30e3, 100e3, 300e3, 1e6]
    sens_table = [1e-12, 2e-12, 5e-12, 1e-11, 2e-11, 5e-11, 1e-10, 2e-10, 5e-10, 1e-9, 2e-9, 5e-9, 1e-8, 
                 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]
    off_curr = np.array([1e-12, 2e-12, 5e-12, 10e-12, 20e-12, 50e-12, 100e-12, 200e-12, 500e-12, \
                         1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, \
                         1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,\
                         1e-3, 2e-3, 5e-3])
    gain_mode = {'low_noise': 0, 'high_bw':1, 'low_drift':2}

    def __init__(self,
                 port='COM9', baud=9600,
                 set_point=200, sens=0,
                 filter_type='12dB',
                 filter_freq=1,
                 gain_mode='low_noise'):
        self.set_point = set_point
        self.sens = sens

        self.ser = serial.Serial(port,baud,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_TWO)
        
        self.write('*RST') # Resets the LNA
        self.write('IOON 0') # Turns off offset current
        self.write(f'GNMD {self.gain_mode[gain_mode]}') # Set to low noise mode
        self.write('BSON 1') # Turns on bias voltage
        self.set_bias(set_point) # Set the bias voltages
        self.set_sens(sens) # Sets the initial sensitivity

        self.set_filter(filter_type, filter_freq)
    
    def write(self, msg, pause=0.1):
        if not self.ser.isOpen():
            self.ser.open()   
            sleep(.25)
        self.ser.write(f'{msg};\r\n'.encode('utf-8'))
        sleep(pause)
    
    def set_filter(self, filter_type, filter_freq):
        assert(filter_type in self.filters)
        assert(filter_freq in self.filter_freqs)

        self.filter_type = filter_type
        self.filter_freq = filter_freq

        self.write(f'FLTT {self.filters[self.filter_type]}')
        self.write(f'LFRQ {self.filter_freqs.index(self.filter_freq)}')
        self.write('*WAI')
        sleep(.5)
    
    def set_sens(self, sens, delay=.1):
        assert(sens >=0 and sens < 28)
        self.sens = sens
        self.write(f'SENS {sens}', delay)
        sleep(.5)

    def set_bias(self, bias=200, delay=.5):
        self.write(f'BSLV {bias}', delay) # Set the bias voltages
    
    def set_input_offset(self, curr):
        self.write('IOON 1')
        if curr < 0:
            self.write('IOSN 0')
        else:
            self.write('IOSN 1')
        
        # Find the value closest the current
        idx = np.searchsorted(self.off_curr, abs(curr), side='right')
        self.write(f'IOLV {idx}')
        # Set offset to some percentage of the scale
        scale = round(abs(curr)/self.off_curr[idx]*1000)
        self.write(f'IOUV {scale}')
    
    def reset_filter_caps(self, delay=.5):
        self.write('ROLD')
        sleep(delay)