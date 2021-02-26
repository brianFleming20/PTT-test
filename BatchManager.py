'''
Created on 1 May 2017

@author: jackw
fix path variables
'''

import csv
import os
from time import gmtime, strftime

class BatchManager(object):
    

    def __init__(self):
        '''
        Constructor
        '''
        self.currentBatch = None
        self.availableBatchs = []
        self.path = os.path.join("C:\\Users", os.getenv('username'), "Desktop\\PTT_Results", "")
        self.inProgressPath = os.path.join(self.path, "in_progress", "")
        self.completePath = os.path.join(self.path, "complete", "")
        
        self.CSVM = CSVManager()
    
    def CreateBatch(self, batch, user):
        '''
        tick
        creates a new batch object and adds it to the availableSessions list and
        creates a new csv file in  the in progress folder
        '''
        #check the new batch number does not already exist
        if batch.batchNumber not in self.CSVM.GetFileNamesInProgress() and batch.batchNumber not in self.CSVM.GetFileNamesComplete():
            #set the current batch to this batch
            self.currentBatch = batch
            
            #create the info list for the first row
            timeNow = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            StimeNow = str(timeNow)
            info = [batch.batchNumber, batch.probeType, user, StimeNow]
            list = [0,]
            list[0] = info

            self.CSVM.WriteListOfListsCSV(list, batch.batchNumber)    #create the CSV file
            self.availableBatchs = self.CSVM.GetFileNamesInProgress() #update the list of available batchs
        else:
            return False
            
    def SuspendBatch(self):
        '''
        tick
        check if batch object is the current batch
        makes the currentBatch False
        '''

        self.currentBatch = False
        
    
    def ResumeBatch(self, batch):
        '''
        tick
        pass in a batch object, check if this is in the availableBatchs list , if so: 
        make the batch the currentBatch
        '''
        if batch.batchNumber in self.CSVM.GetFileNames():
            self.currentBatch = batch
        
    def CompleteBatch(self, batch):
        '''
        tick
        pass in a batch object, check this is the current batch, if so: 
        set currentBatch = False, 
        move the batch file into the 'complete' folder 
        refresh the current batch list
        '''  
        
        if batch.batchNumber == self.currentBatch.batchNumber:
            self.CSVM.MoveToCompleted(batch.batchNumber)        #move the batch file to the complete folder
            self.availableBatchs = self.CSVM.GetFileNamesInProgress()     #update the availableBaths list
        else:
            return False
        
    def GetAvailableBatches(self):
        batchList = []
        for item in self.CSVM.GetFileNamesInProgress():
            if item != 'FOO':
                batchList.append(item)
        return batchList
    
    def GetBatchObject(self, batchNumber):
        #get the batch's info list
        info = self.CSVM.ReadFirstLine(batchNumber)
        #get the batch's probe type
        probeType = info[1]
        #get the batch's probes programmed value
        #probesProgrammed = int(info[2])
        
        batch = Batch(batchNumber)
        batch.probesProgrammed = None
        batch.probeType = probeType
        
        return batch

    def UpdateResults(self, results, batchNumber):
        '''
        Updates the batch's CSV file with a list of results
        '''
        self.CSVM.WriteListOfListsCSV(results, batchNumber)   #create the CSV file
    
        
class CSVManager(object):
    '''
    A TaTT specific wrapper for the CSV Module
    '''
    
    def __init__(self):
        self.path = os.path.join("C:\\Users", os.getenv('username'), "Desktop\\PTT_Results", "")
        self.inProgressPath = os.path.join(self.path, "in_progress", "")
        self.completePath = os.path.join(self.path, "complete", "")
        
        #os.rmdir(self.inProgressPath)
        #os.rmdir(self.completePath)
        
        '''
        Check that the directories exist, if not create them        
        '''
        if not os.path.isdir(self.path):
            try:
                os.makedirs(self.path, 0o777)
            except OSError:
                print ("Creation of the directory %s failed" % self.path)
            else:
                print ("Successfully created the directory %s" % self.path)

        if not os.path.isdir(self.inProgressPath):
            try:
                os.makedirs(self.inProgressPath, 0o777)
            except OSError:
                print ("Creation of the directory %s failed" % self.inProgressPath)
            else:
                print ("Successfully created the directory %s" % self.inProgressPath)

        if not os.path.isdir(self.completePath):
            try:
                os.makedirs(self.completePath, 0o777)
            except OSError:
                print ("Creation of the directory %s failed" % self.completePath)
            else:
                print ("Successfully created the directory %s" % self.completePath)

    def GetFileNamesInProgress(self):
        '''
        tick
        return a list of batchs in the in progress folder
        '''
        #get a list of all the files in the in_progress folder
        list = os.listdir(self.inProgressPath)
        
        #strip the '.csv' bit off the end
        newList = []
        for item in list:
            newItem = item[:-4]
            newList.append(newItem)
        return newList
    
    def GetFileNamesComplete(self):
        '''
        tick
        return a list of batchs in the complete folder
        '''
        #get a list of all the files in the in_progress folder
        list = os.listdir(self.completePath)
        
        #strip the '.csv' bit off the end
        newList = []
        for item in list:
            newItem = item[:-4]
            newList.append(newItem)
        
        return newList
    
    def WriteListOfListsCSV(self, inputList, fileName):
        '''
        tick
        pass in a list, save each item in the list as a new row in the csv file. Can also handle a list of lists
        '''
        #create the full path
        fullPath = os.path.abspath(self.inProgressPath + fileName + '.csv')

        #write the list to the CSV file
        with open(fullPath, 'a', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for item in inputList:
                datawriter.writerow(item)


    
    def MoveToCompleted(self, fileName):
        '''
        tick
        pass in a file name, move this file from the inprogress folder to the completed folder
        '''
        originalPath = os.path.abspath(self.inProgressPath + fileName + '.csv')
        destinationPath = os.path.abspath(self.completePath + fileName + '.csv')
        os.renames(originalPath, destinationPath)
        
    def ReadFirstLine(self, fileName):
        '''
        pass in a filename string and a number of lines.
        will return a list of lists with each list being a line
        '''
        #originalPath = r"C:\Users\jackw\Dropbox\BSc (Hons) Engineering Studies\TaTT_results\in_progress\\" 
        
        fullPath = os.path.abspath(self.inProgressPath + fileName + '.csv')
        
        with open(fullPath) as f:
            lis=[line.split() for line in f] 
        return lis[0]
#             print(lis)       # create a list of lists
#             for i,x in enumerate(lis):              #print the list items 
#                 print (i,x)
        
    def ReadAllLines(self, fileName):
        '''
        pass in a filename string and a number of lines.
        will return a list of lists with each list being a line
        '''
        #originalPath = r"C:\Users\jackw\Dropbox\BSc (Hons) Engineering Studies\TaTT_results\in_progress\\" 
        
        fullPath = os.path.abspath(self.inProgressPath + fileName + '.csv')
        
        with open(fullPath) as f:
            lis=[line.split() for line in f] # create a list of lists
            return[lis]
#             for i,x in enumerate(lis):              #print the list items 
#                 print (i,x)
            
class Batch(object):
    '''
    USed to create batch objects.
    '''
    def __init__(self, batchNumber):
        self.batchNumber = batchNumber
        self.probesProgrammed = 0
        self.probeType = ''
        
