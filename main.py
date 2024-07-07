import machine, uos 
import sx1262
import utime 
import _thread
from collections import deque

# CONSTANTS
FLUSH_DELAY = const(1000) # 10 seconds
GPS_SAMPLE_TIME = const(400) # 400 milli
            
# FRAME TYPES
FRAME_LOG = const(0)
FRAME_GPS = const(1)


class Data:
    def __init__(self):
        self.log_buffer = deque((), 100)
        open('data.txt', 'w').close() # Clear data file
        open('log.txt', 'w').close() # Clear log file
        
    def write_data(self, data):
            with open('data.txt', 'a') as f:
                f.write(data + '\n')
            print("Data written to file")
            
    def flush_log(self):
            with open('log.txt', 'a') as f:
                while True:
                    try:
                        line = self.log_buffer.popleft() # Try to fetch one line
                        f.write(line + '\n')
                    except IndexError:
                        break
                    
    def new_log(self, frame_type, data):
        timestamp = utime.ticks_ms()
        log = f"{timestamp}|{frame_type}|{data}"
        self.log_buffer.append(log)
        print(f"LOG:{log}")

""" 
class SD: #Deprecated until SPI bug is fixed
    def __init__(self):
        self.spi = machine.SPI(0, baudrate=100000, polarity=0, phase=0,    
                                mosi=machine.Pin(7),
                                sck=machine.Pin(6),
                                miso=machine.Pin(4)) #SPI 0 mosi=7, SCK=6, CS=5, miso=4
        self.sd = sdcard.SDCard(self.spi, machine.Pin(5))
        self.log_buffer = deque((), 100)
        uos.mount(self.sd, '/sd', readonly=False)
        print("INFO:SD Card mounted")

    def sd_write_data(self, data):
        with open('/sd/data.txt', 'a') as f:
            f.write(data + '\n')
        print("Data written to SD Card")
        
    def sd_flush_log(self):
        with open('/sd/log.txt', 'a') as f:
            while True:
                try:
                    line = self.log_buffer.popleft() # Try to fetch one line
                    f.write(line + '\n')
                except IndexError:
                    break

    def new_log(self, frame_type, data):
        timestamp = utime.ticks_ms()
        log = f"{timestamp}|{frame_type}|{data}"
        self.log_buffer.append(log)
        print(f"LOG:{log}")
"""

class Lora:
    def __init__(self):
        self.lora = sx1262.SX1262(spi_bus=1, mosi=11, clk=10, cs=13, miso=12, irq=21, gpio=20, rst=18) 
    
    def lora_init(self):
        self.lora.begin(freq=923, bw=500.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)
        print("LoRa Initialized")
        
    def lora_send(self, data):
        self.lora.send(data)
        print("Data sent")
        
    def lora_reset(self):
        self.lora.reset()
        print("LoRa Reset")
        
class GPS:
    def __init__(self):
        self.uart = machine.UART(1, baudrate=9600, tx=machine.Pin(8,machine.Pin.OUT), rx=machine.Pin(9,machine.Pin.IN), timeout = 100) #UART 1 tx=8, rx=9
        self.TIMEOUT = False
        self.FIX_STATUS = False
        self.latitude = ""
        self.longitude = ""
        self.satellites = ""
        self.GPStime = ""
        self.buffer = bytearray(255)
        
    def convertToDegree(self, RawDegrees):
        RawAsFloat = float(RawDegrees)
        firstdigits = int(RawAsFloat/100) 
        nexttwodigits = RawAsFloat - float(firstdigits*100) 
        
        Converted = float(firstdigits + nexttwodigits/60.0)
        Converted = '{0:.6f}'.format(Converted) 
        return str(Converted)    
    
    def getGPS(self) -> str | None:
        timeout = utime.time() +8
        self.TIMEOUT = False
        while True:
            self.uart.readline()
            self.buffer = str(self.uart.readline())
            parts = self.buffer.split(',')
        
            if (parts[0] == "b'$GPGGA" and len(parts) == 15):
                
                if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                    print(self.buffer)
                    
                    self.latitude = self.convertToDegree(parts[2]) + parts[3]
                    self.longitude = self.convertToDegree(parts[4]) + parts[5]
                    self.satellites = parts[7]
                    self.GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                    self.FIX_STATUS = True
                    break
                    
            if (utime.time() > timeout):
                self.TIMEOUT = True
                break
            
        return self.lastGPSFrame()
    
    def lastGPSFrame(self) -> str | None:
        if self.TIMEOUT == True:
            return None
        else:
            return f"{self.latitude}|{self.longitude}|{self.GPStime}"
    
    def printGPS(self):
        if(self.FIX_STATUS == True):
            print("Printing GPS data...")
            print(" ")
            print(f"Latitude: {self.latitude}")
            print(f"Longitude: {self.longitude}")
            print(f"Satellites: {self.satellites}")
            print(f"Time: {self.GPStime}")
            print("----------------------")
            
        if(self.TIMEOUT == True):
            print("No GPS data is found.")


def flush_logs_loop():
    last_flush = 0
    while True:
        if utime.ticks_ms()-last_flush > FLUSH_DELAY: # Flush every seconds
            data.flush_log()
            last_flush = utime.ticks_ms()

def gps_fetch_loop():
    last_loop = 0
    while True:
        if utime.ticks_ms()-last_loop > GPS_SAMPLE_TIME: # Fetch every 400 milliseconds
            gps_frame = gps.getGPS()
            if gps_frame is not None:
                data.new_log(FRAME_GPS, gps_frame)
            else:
                data.new_log(FRAME_LOG, "No GPS data found!")
            last_loop = utime.ticks_ms()

def main():
    data.new_log(FRAME_LOG, "Start HUB module!")  
    gps_fetch_loop()
    """ 
    print(gps.uart)
    while True:
        print(gps.uart.readline())  
    """ 
    """
    while True:
        gps_frame = gps.getGPS()
        if gps_frame is not None:
            data.new_log(FRAME_GPS, gps_frame)
        else:
            data.new_log(FRAME_LOG, "No GPS data found!")
    
    """
 
        
        
# STATIC INITIALIZATION
data = Data()
lora = Lora()
gps = GPS()

if __name__ == "__main__":
    _thread.start_new_thread(flush_logs_loop, ())  
    
    main() 