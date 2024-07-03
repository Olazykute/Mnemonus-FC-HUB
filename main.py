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
        
    

#main function
def main():
    print("Hello World!")
    #code here

#run main function
if __name__ == "__main__":
    main()  
