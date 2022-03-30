import serial
from time import sleep

class relay_inter:
    NONE = bytearray([0])
    DGEN = bytearray([1])
    LNA = bytearray([2])

    def __init__(self, port='COM6', timeout=1):
        self.ser_mcu = serial.Serial(port, timeout=timeout)

    def switch_relay(self, msg):
        if not self.ser_mcu.isOpen():
            self.ser_mcu.open()   
            sleep(.25)
        while True:
            self.ser_mcu.write(msg)
            # Wait for ACK from Arduino
            try:
                self.ser_mcu.read_until(msg)
                sleep(1)
                break
            except:
                pass