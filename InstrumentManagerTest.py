'''
Created on 24 Apr 2017

@author: jackw
'''

import pyvisa as visa
import serial
import time




class InstrumentationManager(object):
    """
    Not sure why I gave this it's own class, fix it. give ZND 'isConnected' bool
    """
    
    def __init__(self):

        self.patient = ["name", "age", "height", "weight"]
        self.port_read = ""
        self.port_control = ""
        self.monitor_port = ""
        self.analyser_port_number = ''
        self.results= []
        self.analyser_data = []
        
        self.monitor =""
        
  
    
    def read_analyser_data(self):
        port = self.GetAnalyserPortNumber()
        print("port number = {}".format(port))
        self.open(port)
        # self.analyser_data = serial.write("data\r".encode('ascii'))
        # print("{}".format(analyser_data))
    
    def AccessSerialControl(self, port_number):
        port_number = port_number
        
        serial_port_control = serial.Serial(port = port_number,
                                    baudrate=9600,
                                    bytesize=8,
                                    timeout=1,
                                    parity= serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE)
        
        return serial_port_control
      
        
    def ReadSerialODM(self):
        
        # initalise parameters
        found_item = "A"
        stop_item = "\n"
        ignor_bit = ","
        serial_result = []
        temp_add = []
        temp = ""
        port = "COM5"
        # ======================
        # Set up port connection
        #=======================
        
        serial_port = self.AccessSerialControl(port)
        
        # ===========================
        # Access the ODM via the port
        # ===========================
        
        parameter = serial_port.read().decode('Ascii')
        while parameter != found_item:                     # Test for start of parameters
            parameter = serial_port.read().decode('Ascii')
            
        while parameter != stop_item:                      # Test for end of parameters
            parameter = serial_port.read().decode('Ascii')
            temp = temp + parameter                        # Collect one parameters data
            if parameter == ignor_bit:                     # Test for seperation between parameters
                temp_add.append(temp[:-1])                 # Add to collection list
                temp= ""
                
        serial_result.append(temp_add)                     # Collect all parameters sent
            
        serial_port.close()                                # Close serial port
      
        return serial_result                               # return all paramters

     
    
    def TestPatientConfig(self):
        # Detect port and connect
        patient_dectected = ["name", "age", "height", "weight"]
        
        if patient == patient_dectected:
            return True
        else:
            return False
        
        
    def GetAnalyserPortNumber(self):
        port = self.analyser_port_number
        print("A port {}".format(self.analyser_port_number))
        return port
    
    def SetAnalyserPortNumber(self, port):
        self.analyser_port_number = port
           
     
    def set_ODM_port_number(self, monitor_com):
        self.monitor_port = monitor_com
        
    
    
    
    #======================================================
    
    # Detecting patient parameters from ODM extended
        
        
    
        
    def GetODMParameters(self):
        packet = bytearray()
        
        found_item = "r"
        stop_item = ""
        ignor_bit = ","
        serial_result = []
        port = "COM5"
        # Access port at 19200 Baud in ODM extebded mode
        serialPort = serial.Serial(port = port, 
                                   baudrate=19200,
                                   bytesize=8,
                                   timeout=4,
                                   parity = serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE)
        # Send command for patient info
        packet.append(0x1B)
        packet.append(0x52)
        packet.append(0x50)
        packet.append(0x0D)
        packet.append(0x0A)
        
        serialPort.write(packet)
        parameter = serialPort.read().decode('Ascii')
        # Collect the patient info into a list
        while parameter != found_item:
            parameter = serialPort.read().decode('Ascii')
            
        while parameter != stop_item:
            parameter = serialPort.read().decode('Ascii')
            serial_result.append(parameter)
            
        serialPort.close()
        print(serial_result)
        
    def GetExtendedParamerts(self):
        packet_select = bytearray()
        packet_read = bytearray()
        
        found_item = "-"
        stop_item = "\r"
        ignor_bit = ","
        error_bit = "\n"
        serial_result = []
        serial_temp = ""
        port = "COM5"
        # Access port at 19200 Baud in ODM extended mode
        serialPort = serial.Serial(port = port, 
                                   baudrate=19200,
                                   bytesize=8,
                                   timeout=4,
                                   parity = serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE)
        # Send command for selecting parameters 
        packet_select.append(0x1B)
        packet_select.append(0x53)
        packet_select.append(0x20)
        packet_select.append(0x53)
        packet_select.append(0x44)
        packet_select.append(0x2C)
        packet_select.append(0x46)
        packet_select.append(0x54)
        packet_select.append(0x2C)
        packet_select.append(0x50)
        packet_select.append(0x56)
        packet_select.append(0x0D)
        packet_select.append(0x0A)
        # command for reading the selected parameters returned
        packet_read.append(0x1B)
        packet_read.append(0x52)
        packet_read.append(0x4C)
        packet_read.append(0x44)
        packet_read.append(0x0D)
        packet_read.append(0x0A)
        # sending commands to ODM extended version
        serialPort.write(packet_select)
        parameter = serialPort.read(2).decode('Ascii')
        # print(parameter)
        # pause between commands sent
        
        serialPort.write(packet_read)
        temp = serialPort.read().decode('Ascii')
       
        # Collect the patient info into a list
        while temp != found_item:
            temp = serialPort.read().decode('Ascii')
            
        parameter = serialPort.read(40).decode('Ascii')
        parameter = parameter[1:]
        parameter = parameter + ignor_bit
        # print(parameter)

        for str in parameter:
            if str != ignor_bit:
                serial_temp = serial_temp + str
                if str == error_bit:
                    serial_temp = serial_temp[:-2]
            else:
                serial_result.append(serial_temp)
                serial_temp = ""       
        
        serial_result.pop(0)
        serialPort.close()
        print(serial_result)
        
        return serial_result
    
class MoveProbe():
    
    def __init__(self):
        self.step_acheived = False
        self.g_code_setup = "G90 G21 G17"
        self.setup = False
        self.Probe_grip = False
        self.probe_in_place = True
        
    def MoveProbeClockwise(self):
        # Check port access in 10 degrees
        step_acheved = False
        g_code_setup = "G90 G21 G17"
        g_code_move = "G68 X0 Y0 R5"
        port_control = "COM4"
        serial_port_control = self.AccessPortControl(port_control)
        
                
        if self.setup == False:
            serial_port_control.write(g_code_setup)
            self.setup = True
                
        if self.setup == True and self.probe_grip == True:
            serial_port_control.write(g_code_move)
            step_acheved = True
            
            
        # access serial port with own port number
        # try / catch move motor 10 degrees
        # step acheved as true
        
        return step_acheved
    
    
    def MoveProbeAnticlockwise(self):
        # Check port access in 10 degrees
        step_acheved = False
        g_code_move = "G68 X0 Y0 R-5"
        port_control = "COM4"
        serial_port_control = self.AccessPortControl(port_control)
        
                
        if self.setup == False:
            serial_port_control.write(g_code_setup)
            self.setup = True
                
        if self.setup == True and self.probe_grip == True:
            serial_port_control.write(g_code_move)
            step_acheved = True
        
        # access serial port with own port number
        # try / catch move motor 10 degrees
        # step acheved as true
        
        return step_acheved
    
   
        
        
    
    def ProbeGrip(self):
        # check port access
        port_command = "M10"
        port_control = "COM4"
        serial_port_control = self.AccessPortControl(port_control)
        
        if self.Probe_grip == False:
            serial_port_control.write(port_command)
            self.probe_in_place = True
            
        return probe_in_place
       
        
        
    def Release_tool(self):
        # check port access
        port_command = "M11"
        port_control = "COM4"
        serial_port_control = self.AccessPortControl(port_control)
        
        if self.Probe_grip == True:
            serial_port_control.write(port_command)
            self.probe_in_place = False
            
        return probe_in_place



    
class ZND(object):
    '''
    Handles VNA operations. Primarily: configuring, refreshing traces and retrieving trace values
    '''
    
    def __init__(self):
        self.deviceDetails = ''
        self.rm = visa.ResourceManager('@py')
        # self.HISLIPAddress = ''
        self.analyser_data = []
        self.analyser_port_number = ''
        self.znd = False
        self.RxRL = None
        self.TxRL = None
        self.RxMinFreq = None
        self.RxMinMag = None
        self.TxMinFreq = None
        self.TxMinMag = None
        self.IM = InstrumentationManager()
        
        
    def GetAnalyserPortNumber(self):
            port_number = self.analyser_port_number
            return port_number
    

       
    
    def AccessPortRead(self, port_number):
        line = ''
        serial_port_read = serial.Serial(port = port_number, 
                                   baudrate=1152000,
                                   bytesize=8,
                                   timeout=0.05,
                                   parity = serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE)
        analyser_port_number = serial_port_read
        print("Nano data {}".format(analyser_port_number))
        self.IM.SetAnalyserPortNumber(analyser_port_number)
        serial_port_read.write("data\r".encode('ascii'))
        while True:
            c = serial_port_read.read().decode('utf-8')
            if c == chr(13):
                c=''
                next # ignore CR
            line += c
            if c == chr(10):
                c=''
                if line == 'data\n':
                    line='' # ignore data tag
                    next
                self.analyser_data.append(line[:-1])
                line = ''
                c = ''
                next
            if line.endswith('ch>'):
                # stop on prompt
                break
    
        print("{}".format(self.analyser_data))
        serial_port_read.close() # Close port 
        return serial_port_read
        
    def send_command(self, cmd):
        self.open()
        self.serial.write(cmd.encode())
        self.serial.readline()
        
    def capture(self):
        from PIL import Image
        self.send_command("capture\r")
        b = self.serial.read(320 * 240 * 2)
        print("b = {}".format(b))
        x = struct.unpack(">76800H", b)
        # # convert pixel format from 565(RGB) to 8888(RGBA)
        # arr = np.array(x, dtype=np.uint32)
        # arr = 0xFF000000 + ((arr & 0xF800) >> 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 19)
        # return Image.frombuffer('RGBA', (320, 240), arr, 'raw', 'RGBA', 0, 1)   
   
    def Configure(self):
        '''
        Configures the analyser with the following windows:
        Window 1: S12, S21 dBmag
        Window 2: S11, S22 Smith
        Window 3: S11, S22 dBmag
        '''
        
        #initial instrument configuration
        self.znd.write("*RST") #resets the instrument 
        self.znd.write("*CLS") # clears the error queue 
        self.znd.write("INITiate:CONTinuous:ALL OFF") #put it in single sweep mode
        self.znd.write("CALC1:PAR:DEL:ALL") #clear the default trace
        self.znd.write("FREQ:STAR 3MHz") #set start frequency value
        self.znd.write("FREQ:STOP 5MHz") # set stop frequency value
        
        #configure each window
        #config window1 as S12, S21 dBmag
        self.znd.write("DISP:WIND1:STAT ON") #create a window area no.1
        self.znd.write("CALC1:PAR:SDEF 'Ch1Tr1', 'S21'") #create an S21 trace on channel 1
        self.znd.write("DISP:WIND1:TRAC1:FEED 'CH1TR1'") #place the trace in the window
        self.znd.write("CALC1:PAR:SDEF 'Ch1Tr2', 'S12'") #create an S12 trace on channel 1
        self.znd.write("DISP:WIND1:TRAC2:FEED 'CH1TR2'") #place the trace in the window
    
        #config window2 as S22, S11 smith
        self.znd.write("DISP:WIND2:STAT ON") #create a window area no.2
        self.znd.write("CALC2:PAR:SDEF 'Ch2Tr1', 'S22'") #create an S22 trace on channel 2
        self.znd.write("CALCulate2:FORMat SMITh")
        self.znd.write("DISP:WIND2:TRAC3:FEED 'CH2Tr1'") #display the trace in window 2
        self.znd.write("CALC3:PAR:SDEF 'Ch2Tr2', 'S11'") #create an S11 trace on channel 2
        self.znd.write("CALCulate3:FORMat SMITh")
        self.znd.write("DISP:WIND2:TRAC4:FEED 'CH2Tr2'") #display the trace in window 2
     
        #config window3 as S11, S22 dBmag
        self.znd.write("CALC4:PAR:SDEF 'Ch3Tr1', 'S22'") #create an S22 trace on channel 3
        self.znd.write("CALC4:PAR:SDEF 'Ch3Tr2', 'S11'") #create an S11 trace on channel 3
        self.znd.write("DISP:WIND3:STAT ON") #create a window area no.3
        self.znd.write("DISP:WIND3:TRAC5:FEED 'CH3TR1'") #display the trace in the window
        self.znd.write("DISP:WIND3:TRAC6:FEED 'CH3TR2'") #display the trace in the window
        self.znd.write("DISP:WIND3:TRAC5:Y:PDIV 2") #change scale to 2db per div
        self.znd.write("DISP:WIND3:TRAC6:Y:PDIV 2") #change scale to 2db per div
        
        self.znd.close()