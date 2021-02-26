'''
Created on 28 Apr 2017

@author: jackw
'''
import serial
from serial import Serial
import codecs
import binascii
from time import gmtime, strftime
import time
from bitstring import BitArray


class PI(object):
    """
    SC18IM700 commands
    
    S 53 I2C start
    P 50 I2C stop
    R 52 read SC18IM internal register
    W 57 write to SC18IM internal register
    I 49 read IO port
    O 4F write to GPIO port
    Z 5A power down
    
    A0 write address
    A1 read address

    """
    
    def __init__(self):
        self.loggedInUser = False
        self.SM = SerialManager()
        self.PD = ProbeData()

    
    def Connect(self, comPort):
        self.ser = self.SM.ConfigurePort(comPort)
            
    def ProbeWrite(self, data):
        '''
        pass in a list of bytes, writes a byte at a time to the probe
        '''
        
        self.SM.OpenPort()
        print(data)
        for item in data:
            self.SM.Send(item)
            time.sleep(0.01)
        self.SM.ClosePort()
            
    def ProbeReadSerialNumber(self):
        '''
        Returns a 32 character string of the first 16 bytes of the probe's memory
        
        
        sends: I2c start, write address, number of bytes, data... , I2C start, read address, number of bytes, I2C stop
        sends:    53    ,        A0    ,       01       ,    00   ,    53    ,     A1      ,       10       ,    50
        '''   
        serialData = []
        self.SM.OpenPort()   
        
        for i in range(2): 
            self.SM.Send(b'53A0010053A11e50')
           #self.SM.Send(b'53A0010053A10150')   
            time.sleep(0.05) #allow time for the data to be received  
            
        serialData = self.SM.Read()
        self.SM.ClosePort()
        
        return serialData

    def ProbePresent(self):
        '''
        Returns True if a probe is present, False if not
        '''           
        #get the IO byte
        self.SM.OpenPort()
        self.SM.Send(b'4950')   
        time.sleep(0.05) #allow time for the data to be received  
        IOByte = self.SM.Read()
        self.SM.ClosePort()

        #get the relevant bit
        bits = BitArray(hex=IOByte)
        bit = bits.bin[2:3]

        #check to see if the pin is pulled low by the probe
        if bit == '0':
            return True
        else:
            return False
        
    def ReadFirstByte(self):
        '''
        returns a single byte as a 2 character string
        '''
        self.SM.OpenPort()         #open the port
        self.SM.Send(b'53A0010053A10150') #write data to request first byte from the probe EEPROM
        time.sleep(0.05) #allow time for the data to be received  
        firstByte = self.SM.Read() #read the first byte
        self.SM.ClosePort()

        return firstByte
    
    def ProbeReadAllBytes(self):
        '''
        Returns a 32 character string of the first 16 bytes of the probe's memory
        
        
        sends: I2c start, write address, number of bytes, data... , I2C start, read address, number of bytes, I2C stop
        sends:    53    ,        A0    ,       01       ,    00   ,    53    ,     A1      ,       10       ,    50
        '''   
        serialData = []
        self.SM.OpenPort()   
        

        self.SM.Send(b'53A0010053A11e50')  
        time.sleep(0.05) #allow time for the data to be received     
        serialData = self.SM.Read()
        
        self.SM.Send(b'53A0011e53A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()

        self.SM.Send(b'53A0013c53A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.Send(b'53A0015A53A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()

        self.SM.Send(b'53A0017853A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.Send(b'53A0019653A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.Send(b'53A001B453A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.Send(b'53A001D253A11e50')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.Send(b'53A001F053A11050')
        time.sleep(0.05)
        serialData = serialData + self.SM.Read()
        
        self.SM.ClosePort()
        
        return serialData
   

class SerialManager(object):
    '''
    A wrapper for TaTT specific PySerial usage.
    '''
    
    def __init__(self):
        self.ser = False
        
    def ConfigurePort(self, port):
        self.ser = serial.Serial(port = port, baudrate = 9600, \
            parity = serial.PARITY_NONE, \
            stopbits = serial.STOPBITS_ONE, \
            bytesize  = serial.EIGHTBITS, \
            timeout  = 0, \
             )

        self.ser.close()


    def Send(self, input):
        '''
        pass in hex bytes, send the whole lot down the serial port.
        '''
        
        #flush the buffers
        self.ser.flushInput()   
        self.ser.flushOutput() 
        
        #convert the input to ASCII characters and send it
        self.ser.write(codecs.decode(input, "hex_codec"))

        
    def Read(self):
        '''
        reads the contents of the serial buffer and returns it as a string 
        of hex bytes
        '''
        serialData = ''

        while self.ser.inWaiting() > 0:
            b = binascii.hexlify(self.ser.read(1))
            serialData += codecs.decode(b) 
        
        return serialData
    
    def OpenPort(self):
        '''
        Opens the port, readying it for communication
        '''
        self.ser.open()
    
    def ClosePort(self):
        '''
        Closes the port
        '''
        self.ser.close()
    
    
class ProbeData(object):
    '''
    Responsible for creating the full 256 bytes of EEPROM data.
    '''
    pass
    
    def __init__(self):
        '''
        '''
        self.timeStamp = ''
        self.typeBytes = ''
        
        self.DP240TypeBytes = ['50','46','30','4a']
        self.DP12TypeBytes = ['50','30','43','4a']
        self.DP6TypeBytes = ['50','30','36','4a']
        self.I2CTypeBytes = ['50','34','38','4a']
        self.I2PTypeBytes = ['50','31','38','4a']
        self.I2STypeBytes = ['50','30','36','4a']
        self.KDP72TypeBytes = ['50','34','38','4a']
        self.SDP30TypeBytes = ['53','33','30','4a']

    
    def GenerateDataString(self, probeType):
        '''
        Pass in a probe type, returns the full 255 byte probe data including time stamped serial number
        
        The first 8 and last 2 values of each list item are for SC18IM configuration, the bytes inbetween are that actual data that is written
        '''
        probezeros = ['53A00900000000000000000050', '53A00908000000000000000050', '53A00910000000000000000050', '53A00918000000000000000050', '53A00920000000000000000050', '53A00928000000000000000050', '53A00930000000000000000050', '53A00938000000000000000050', '53A00940000000000000000050', '53A00948000000000000000050', '53A00950000000000000000050', '53A00958000000000000000050', '53A00960000000000000000050', '53A00968000000000000000050', '53A00970000000000000000050', '53A00978000000000000000050', '53A00980000000000000000050', '53A00988000000000000000050', '53A00990000000000000000050', '53A00998000000000000000050', '53A009a0000000000000000050', '53A009a8000000000000000050', '53A009b0000000000000000050', '53A009b8000000000000000050', '53A009c0000000000000000050', '53A009c8000000000000000050', '53A009d0000000000000000050', '53A009d8000000000000000050', '53A009e0000000000000000050', '53A009e8000000000000000050', '53A009f0000000000000000050', '53A009f8000000000000000050']
        probeData = ['53A00910303030303030303050', '53A00918303030303030303050', '53A00920303030303030303050', '53A00928303030303030300050', '53A009303001f00a3030303050', '53A00938303030303030303050', '53A009402863292044656c7450', '53A009486578204d6564696350', '53A00950616c204c696d697450', '53A00958656420323030370050', '53A00960303030303030303050', '53A00968303030303030303050', '53A00970303030303030303050', '53A00978303030303030303050', '53A00980303030303030303050', '53A00988303030303030303050', '53A00990303030303030303050', '53A00998303030303030303050', '53A009a0303030303030303050', '53A009a8303030303030303050', '53A009b0303030303030303050', '53A009b8303030303030303050', '53A009c0303030303030303050', '53A009c8303030303030303050', '53A009d0303030303030303050', '53A009d8303030303030303050', '53A009e0303030303030303050', '53A009e8303030303030303050', '53A009f0303030303030303050', '53A009f8303030303030303050']
        SDprobeData = ['53A00910303030303030303050', '53A00918303030303030303050', '53A00920303030303030303050', '53A00928303030303030300050', '53A0093030fafa1e3030303050', '53A00938303030303030303050', '53A009402863292044656c7450', '53A009486578204d6564696350', '53A00950616c204c696d697450', '53A00958656420323030370050', '53A00960303030303030303050', '53A00968303030303030303050', '53A00970303030303030303050', '53A00978303030303030303050', '53A00980303030303030303050', '53A00988303030303030303050', '53A00990303030303030303050', '53A00998303030303030303050', '53A009a0303030303030303050', '53A009a8303030303030303050', '53A009b0303030303030303050', '53A009b8303030303030303050', '53A009c0303030303030303050', '53A009c8303030303030303050', '53A009d0303030303030303050', '53A009d8303030303030303050', '53A009e0303030303030303050', '53A009e8303030303030303050', '53A009f0303030303030303050', '53A009f8303030303030303050']

        firstStart = '53A00900'
        secondStart = '53A00908'
        end = '50'
        
        if probeType == 'Blank':
            return probezeros
        
        #set the correct probe type bytes
        if probeType == 'DP240':
            typeBytes = self.DP240TypeBytes
        elif probeType == 'DP12':
            typeBytes = self.DP12TypeBytes
        elif probeType == 'DP6':
            typeBytes = self.DP6TypeBytes
        elif probeType == 'I2C':
            typeBytes = self.I2CTypeBytes
        elif probeType == 'I2S':
            typeBytes = self.I2STypeBytes
        elif probeType == 'I2P':
            typeBytes = self.I2PTypeBytes
        elif probeType == 'KDP72':
            typeBytes = self.KDP72TypeBytes
        elif probeType == 'I2P':
            typeBytes = self.I2PTypeBytes
        elif probeType == 'SDP30':
            typeBytes = self.SDP30TypeBytes
            
        #create a 12 byte timestamp of the format
        timeStamp = strftime("%Y%m%d%H%M%S", gmtime())
        timeStampFormatted = timeStamp[2:]
        timeStampASCII = []
        for item in timeStampFormatted:
            x = (ord(item))
            timeStampASCII.append(format((x), "x"))
        
        #stick the type bytes and the timestamp together 
        serialNumber = typeBytes + timeStampASCII
        
        #put them in a format that can be sent via the SC18IM
        lower  = serialNumber[0:8]
        upper = serialNumber[8:]
        slower = ''.join(lower)
        supper = ''.join(upper)
        firstByte = firstStart + slower + end
        secondByte = secondStart + supper + end
        
        #add them to the probe data list
        SDprobeData.insert(0, secondByte)
        SDprobeData.insert(0, firstByte)
        
        #create a single string of the actual data for error checking
        stripped = ''
        for item in SDprobeData:
            stripped = stripped + item[8:-2]
        return SDprobeData, stripped
