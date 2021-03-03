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
        self.monitor = True
        self.results= []
        
        
    def set_ODM_port_number(self, monitor_com):
        monitor_port = monitor_com
        
    def set_port_number(self, port):
        port_number = port
    
    def AccessPortRead(self, port_number):
        port_number = port_number
        
        serial_port_read = serial.Serial(port = port_number, 
                                   baudrate=9600,
                                   bytesize=8,
                                   timeout=4,
                                   parity = serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE)
        
        return serial_port_read
    
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
        
        

 
    
    def read_monitor(self, monitor):
        if monitor == True:
            results = InstrumentationManager.ReadSerialODM()
        
        if monitor == False:
            results = InstrumentationManager.GetExtendedParamerts()
            
        return results   
        
    
        
    # def ContinuePatient(self):
    #     # return current patient
        
    
    
    
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


class ChooseMonitor(object):
    
    def get_monitor_type(self):
        return monitor
    
    def set_monitor_type(self, monitor):
        self.monitor = monitor
    
    def read_monitor(self, monitor_type):
        if monitor == True:
            results = InstrumentationManager.ReadSerialODM()
        
        if monitor == False:
            results = InstrumentationManager.GetExtendedParamerts()
            
        return results