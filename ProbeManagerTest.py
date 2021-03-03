'''
Created on 28 Apr 2017

@author: jackw
'''
import PI
import InstrumentManagerTest as IM
import BatchManagerTest

BM = BatchManagerTest.BatchManager()


class ProbeManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.PI = PI.PI()
        self.PD = PI.ProbeData()
        
        self.testResults = []
        self.debugResults = [[1,1,1,],[2,2,2],[3,3,3]]
        
        
    def ConnectToProbeInterface(self, comPort):
        '''
        Pass in a com port ID (COMX) and connect to that comport.
        '''
        self.PI.Connect(comPort)
    
    def ProgramProbe(self, probeType):
        '''
        pass in a string containing the probe type
        program the probe as that type
        returns the probes serial number if programming was succesful, False if not
        '''
        probeData = self.PD.GenerateDataString(probeType)
        # get first two lots of 8 bights for error checking

        #write the data to the probe
        self.PI.ProbeWrite(probeData[0])
        
        #check to see if programming was succesful
        pd = ''.join(probeData[1])
        check = self.PI.ProbeReadAllBytes()
        if check == pd:
            sn = self.PI.ProbeReadSerialNumber()
            return sn
        else:
            return False
        
    def ProbePresent(self):
        '''
        returns True of a probe is inserted into PI, false if not
        '''
        if self.PI.ProbePresent() == True:
            return True
        else:
            return False
    
    def ProbeIsProgrammed(self):
        '''
        Checks to see if the first byte of the eeprom is programmed with the probe type byte,
        returns true if it is, false if not
        '''
        x = self.PI.ReadFirstByte()

        if x in ['48','49','50','51','52','53','54','55','56','57']: #Probe type codes in decimal
            return True
        else:
            return False



class Probe(object):
    
    def __init__(self):
        pass