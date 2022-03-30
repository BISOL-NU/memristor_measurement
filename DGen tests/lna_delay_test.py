import pyvisa as visa
from time import sleep
import serial

def init_DGen(rm):
    dgen_name = GP_type+'::15::INSTR' #delay generator
    try:
        if not dgen_name in rm.list_resources(dgen_name):
            raise visa.VisaIOError(1) #randomly chosen error code
        DGen=rm.open_resource(dgen_name)
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
        
        return DGen
    except visa.VisaIOError:
        print("Not attached to delay generator!\n")
        return None

def init_DMM(rm): 
    dmm_name = GP_type+'::22::INSTR'
    try:
        if not dmm_name in rm.list_resources(dmm_name):
            raise visa.VisaIOError(1) #randomly chosen error code
        DMM=rm.open_resource(dmm_name)  ## Digital Multi Meter Agilent 34410A
        DMM.write('*RST') 
        DMM.write('CONF:VOLT:DC 10') 
        DMM.write('VOLT:DC:NPLC 10') 
        return DMM
    except visa.VisaIOError:
        print("Not attached to Digital Multimeter\n")
        return None 

def init_LNA():
    set_point=200#.2
    meas_LNA=0
    if(ser.isOpen() == False):
        ser.open()   
        sleep(1)
    ser.write(("BSON "+ "1"+ '\r\n').encode('utf-8'))
    sleep(.2)
    ser.write(("BSLV "+ set_point+ '\r\n').encode('utf-8'))
    sleep(1)
    ser.write(("SENS "+ meas_LNA+ '\r\n').encode('utf-8'))
    ser.close()

def meas_LNA(Current_Sensitivity, delay):
    Sens_Loop=True
    while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
        #loop through sensitivity until no longer saturated, sense_loop => False
        print ('sens' ,Current_Sensitivity)
        if(ser.isOpen() == False):
            ser.open() 
            sleep(1)
        ser.write(("SENS "+ str(Current_Sensitivity)+ '\r\n').encode('utf-8'))
        sleep(delay+.1) #this delay is very important
        DMM.write('READ?')    
        Test1=float(DMM.read())
                    
        if -4<Test1<4: # this limit can change. 
            Sens_Loop=False
            Dark_Current1=Sens_Table[Current_Sensitivity]*Test1
            print ("DMM voltage", Test1,"\ndark", Dark_Current1)
        elif Current_Sensitivity<27:                    
            Current_Sensitivity = Current_Sensitivity + 1                   
            sleep(delay+.1)
        else:
            Sens_Loop=False
            Dark_Current1=Sens_Table[Current_Sensitivity]*Test1
            print ("dark", Dark_Current1,"\nMaximum Sens _ Take Care!!!!")
    ser.close()
    return Dark_Current1, Current_Sensitivity

def switch_relay(msg):
    while True:
        ser_mcu.write(msg)
        # Wait for ACK from Arduino
        try:
            ser_mcu.read_until(msg)
            break
        except:
            pass

# Initialization for GPIB
rm = visa.ResourceManager()
GP_type="GPIB0"
dgen_name = GP_type+'::15::INSTR' #delay generator
DGen=rm.open_resource(dgen_name)
DGEN_BUFFER_PERIOD = 25e-9
### TEST FOR TRIGGER
pulse_on_period = 100e-6
pulse_off_period = pulse_on_period
pulse_number = 1
burst_period = (pulse_on_period+pulse_off_period)
trig_period = pulse_number*(burst_period)*2
trig_freq = 1/burst_period
DGen = init_DGen(rm)
sens = 6
delay = .05

DMM = init_DMM(rm)
# Initialization for Serial
ser_mcu = serial.Serial('COM6', timeout=1)
CLOSED = bytearray([0])
DGEN_OPEN = bytearray([1])
LNA_OPEN = bytearray([2])
# Serial port for the LNA
ser = serial.Serial('COM7')
ser.baudrate = 9600
Sens_Table=[1e-12, 2e-12, 5e-12, 1e-11, 2e-11, 5e-11, 1e-10, 2e-10, 5e-10, 1e-9, 2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]


while True:
    # Programming pulses
    switch_relay(DGEN_OPEN)

    DGen.write('*TRG')
    sleep(trig_period)
    # Reading pulse from LNA
    switch_relay(LNA_OPEN)

    meas_LNA(27, delay)
    switch_relay(DGEN_OPEN)