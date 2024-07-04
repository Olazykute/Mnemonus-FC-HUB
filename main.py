import machine, sdcard, uos 
import sx1262
import utime 

class SD:
    def __init__(self):
        self.spi = machine.SPI(0, baudrate=100000, polarity=0, phase=0,    
                                mosi=machine.Pin(7),
                                sck=machine.Pin(6),
                                miso=machine.Pin(4)) #SPI 0 mosi=7, SCK=6, CS=5, miso=4
        self.sd = sdcard.SDCard(self.spi, machine.Pin(5))
        uos.mount(self.sd, '/sd', readonly=False)
        print("SD Card mounted")

    def sd_write_data(self, data):
        with open('/sd/data.txt', 'a') as f:
            f.write(data + '\n')
        print("Data written to SD Card")
        
    def sd_write_log(self):
        with open('/sd/log.txt', 'a') as f:
            f.write("Log data" + '\n')
        print("Log written to SD Card")

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
        self.uart = machine.UART(1, baudrate=9600, tx=8, rx=9) #UART 2 tx=8, rx=9
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
    
    def getGPS(self):
        timeout = utime.time() + 8 
        while True:
            self.uart.readline()
            self.buffer = str(self.uart.readline())
            parts = self.buffer.split(',')
        
            if (parts[0] == "b'$GPGGA" and len(parts) == 15):
                if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                    print(self.buffer)
                    
                    self.latitude = self.convertToDegree(parts[2])
                    if (parts[3] == 'S'):
                        self.latitude = "-" + self.latitude
                    self.longitude = self.convertToDegree(parts[4])
                    if (parts[5] == 'W'):
                        self.longitude = "-" + self.longitude
                    self.satellites = parts[7]
                    self.GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                    self.FIX_STATUS = True
                    break
                    
            if (utime.time() > timeout):
                self.TIMEOUT = True
                break
            utime.sleep_ms(500)
    
    def printGPS(self):
        if(self.FIX_STATUS == True):
            print("Printing GPS data...")
            print(" ")
            print(f"Latitude: {self.latitude}")
            print(f"Longitude: {self.longitude}")
            print(f"Satellites: {self.satellites}")
            print(f"Time: {self.GPStime}")
            print("----------------------")
            
            #FIX_STATUS = False
            
        if(self.TIMEOUT == True):
            print("No GPS data is found.")
            self.TIMEOUT = False
            


def main():
    print("Hello World!")
    


if __name__ == "__main__":
    main()  
