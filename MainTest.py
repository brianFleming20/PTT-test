'''
Created on 3 May 2017

@author: jackw
Ammended by BrianF

Naming convention
- Variables = no spaces, capitals for every word except the first : thisIsAVariable
- Local functions = prefixed with _, _ for spaces, no capitals : _a_local_function

Dependencies
-NI VISA Backend
-Non standard python modules
    pyvisa
    pyserial


to do:
-complete button on TPW doesn't work
-TPW freezes if a probe is inserted
-add SQ probe to list

#         s = ttk.Separator(self.root, orient=VERTICAL)
#         s.grid(row=0, column=1, sticky=(N,S))

'''

import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tm
import pyvisa as visa
import time


import InstrumentManagerTest
# from InstrumentManager import ZND
import ProbeManagerTest
from ProbeManagerTest import Probe
from ProbeManagerTest import ProbeManager
import BatchManagerTest
from BatchManagerTest import Batch

PM = ProbeManager()
IM = InstrumentManagerTest.InstrumentationManager()
BM = BatchManagerTest.BatchManager()


# define global variables
PTT_Version = 'Deltex Medical : XXXX-XXXX Probe Test Tool V0.1'
w = 800  # window width
h = 600  # window height
LARGE_FONT = ("Verdana", 14)
BTN_WIDTH = 30


class WindowController(tk.Tk):
    
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.title(PTT_Version)
        # get window width and height
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        # calculate x and y coordinates for the window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (
                  ConnectionWindow,
                  
                  TestProgramWindow):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ConnectionWindow)

    def show_frame(self, newFrame):

        frame = self.frames[newFrame]
        frame.tkraise()

        # Does the frame have a refresh method, if so call it.
        if hasattr(newFrame, 'refresh_window') and callable(getattr(newFrame, 'refresh_window')):
            self.frames[newFrame].refresh_window()


class TestProgramWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.sessionOnGoing = False
        self.sessionComplete = None
        self.action = StringVar()

        # define variables
        self.currentBatch = StringVar()
        self.currentUser = StringVar()
        self.probesPassed = IntVar()
        self.deviceDetails = ""
        self.probeType = StringVar()
        self.SD_data = IntVar()
        self.FTc_data = IntVar()
        self.PV_data = IntVar()
        

        #import images
        self.greenlight = (PhotoImage(file="green128.gif"))
        self.amberlight = (PhotoImage(file="amber128.gif"))
        self.redlight = (PhotoImage(file="red128.gif"))
        self.greylight = (PhotoImage(file="grey128.gif"))
        
        ttk.Label(self, text='Batch number: ').place(
            relx=0.1, rely=0.05, anchor='w')
        ttk.Label(self, textvariable=self.currentBatch, relief=SUNKEN, font="bold",
                 width=10).place(relx=0.3, rely=0.05, anchor='w')

        ttk.Label(self, text='Probe type: ').place(
            relx=0.45, rely=0.05, anchor='w')
        ttk.Label(self, textvariable=self.probeType, relief=SUNKEN, font="bold",
                  width=10).place(relx=0.6, rely=0.05, anchor='w')

        # ttk.Label(self, text='User: ').place(relx=0.1, rely=0.15, anchor='w')
        # ttk.Label(self, textvariable=self.currentUser, relief=SUNKEN, font="bold",
        #           width=20).place(relx=0.3, rely=0.15, anchor='w')
        
        ttk.Label(self, text='Connected to: ').place(
            relx=0.1, rely=0.25, anchor='w')
        ttk.Label(self, textvariable=self.deviceDetails, relief=SUNKEN,
                  width=50).place(relx=0.3, rely=0.25, anchor='w')
        
        ttk.Label(self, text="Probe parameter data").place(
            relx=0.7, rely=0.4, anchor="w")
        ttk.Label(self, text="SD").place(relx=0.70, rely=0.44, anchor="w")
        ttk.Label(self, text="FTc").place(relx=0.77, rely=0.44, anchor="w")
        ttk.Label(self, text="PV").place(relx=0.85, rely=0.44, anchor="w")
        ttk.Label(self, textvariable=self.SD_data, relief=SUNKEN, font="bold",
                  width=5).place(relx=0.69, rely=0.49, anchor='w')
        ttk.Label(self, textvariable=self.FTc_data, relief=SUNKEN, font="bold",
                  width=5).place(relx=0.76, rely=0.49, anchor='w')
        ttk.Label(self, textvariable=self.PV_data, relief=SUNKEN, font="bold",
                  width=5).place(relx=0.84, rely=0.49, anchor='w')

        ttk.Label(self, text='Program/Test Status: ').place(relx=0.1,
                                            rely=0.5, anchor='w')
        self.status_image = ttk.Label(self, image=self.greylight)
        self.status_image.place(relx=0.5, rely=0.5, anchor=CENTER)

        ttk.Label(self, text='Probes Passed: ').place(
            relx=0.1, rely=0.7, anchor='w')
        ttk.Label(self, textvariable=self.probesPassed, relief=SUNKEN, font="bold",
                  width=10).place(relx=0.3, rely=0.7, anchor='w')

        ttk.Label(self, text='Action: ').place(relx=0.1, rely=0.8, anchor='w')
        ttk.Label(self, textvariable=self.action, background='yellow',
                  width=40, relief=GROOVE).place(relx=0.3, rely=0.8, anchor='w')
        self.action.set('Connect New Probe')

        ttk.Button(self, text='Complete Session', command=lambda: self.cmplt_btn_clicked(
            controller)).place(relx=0.4, rely=0.9, anchor=CENTER)
        ttk.Button(self, text='Suspend Session', command=lambda: self.suspnd_btn_clicked(
            controller)).place(relx=0.6, rely=0.9, anchor=CENTER)

    def cmplt_btn_clicked(self, controller):
        Tk.update(self)
       

    def suspnd_btn_clicked(self, controller):
        print("sessionWindow")

    # def RefreshWindow(self):
    #    Tk.update(self)
    #    Tk.update_idletasks(self)


    def refresh_window(self):
        self.sessionOnGoing = True
        serial_results = []
        self.deviceDetails = IM.GetAnalyserPortNumber()
        print("analyser port {}".format(self.deviceDetails))
        # self.root.deiconify()
        # self.probeType.set(BM.currentBatch.probeType)
        # self.currentBatch.set(BM.currentBatch.batchNumber)
        self.probesPassed.set(0)
        self.currentUser = "Tester"
        # self.deviceDetails.set(PM.ZND.deviceDetails)
        self.RLLimit = -1  # pass criteria for return loss measurement

        # Collect serial data
        try:
            
            serial_results = IM.ReadSerialODM()
            # serial_results = IM.GetPatientParamerts()
            # self.SD_data.set(serial_results[0])
            # self.FTc_data.set(serial_results[1])
            # self.PV_data.set(serial_results[2])
           
            self.SD_data.set(serial_results[0][5])
            self.FTc_data.set(serial_results[0][6])
            self.PV_data.set(serial_results[0][9])
            Tk.update(self)
        except:
            tm.showerror(
                'Connection Error', 'Unable to collect the data from the ODM.')

        
        
        
        while(self.sessionOnGoing == True):
            Tk.update(self)
            if PM.ProbePresent() == True:
                self.action.set('Probe connected')
                self.status_image.configure(image=self.amberlight)
                ProbeIsProgrammed = PM.ProbeIsProgrammed()

                if ProbeIsProgrammed == False or tm.askyesno('Programmed Probe Detected', 'This probe is already programmed.\nDo you wish to re-program and test?'):
                    self.action.set('Programming probe')
                    # serialNumber = PM.ProgramProbe(BM.currentBatch.probeType)
                    serialNumber = "12345"
                    if serialNumber == False:
                        tm.showerror('Programming Error',
                                     'Unable to program\nPlease check U1')
                        self.action.set('Probe failed')
                        self.status_image.configure(image=self.redlight)
                    else:
                        Tk.update(self)
                        self.action.set('Testing probe...')
                            
                        results = PM.TestProbe(
                            serialNumber, BM.currentBatch.batchNumber, self.currentUser.get())
                        self.action.set('Testing complete. Disconnect probe')
                        # if PM.ZND.get_marker_values()[0] < self.RLLimit and PM.ZND.get_marker_values()[1] < self.RLLimit:
                        if self.RLLimit == -1: #check for crystal pass value, now pass every time
                            BM.UpdateResults(
                                results, BM.currentBatch.batchNumber)
                            self.probesPassed.set(self.probesPassed.get() + 1)
                            self.status_image.configure(image=self.greenlight)
                            Tk.update(self)
                        else:
                            self.status_image.configure(image=self.redlight)
                            tm.showerror('Return Loss Error',
                                         'Check crystal connections')
                            Tk.update(self)
                        
                         # Collect serial data
                        while PM.ProbePresent() == True:
                            # serial_results = IM.GetPatientParamerts()
                            try:
                                
                                serial_results = IM.ReadPortODM()
                            # print(serial_results)
                            # self.SD_data.set(serial_results[0])
                            # self.FTc_data.set(serial_results[1])
                            # self.PV_data.set(serial_results[2])
                            # Tk.update(self)
                            
                                self.SD_data.set(serial_results[0][5])
                                self.FTc_data.set(serial_results[0][6])
                                self.PV_data.set(serial_results[0][9])
                                Tk.update(self)
                            except:
                                tm.showerror(
                                        'Connection Error', 'Unable to collect the data from the ODM.')
                        
                while 1:
                    if PM.ProbePresent() == False:
                        # PM.ClearAnalyzer()
                        self.status_image.configure(image=self.greylight)
                        self.action.set('Connect New Probe')
                        break
        
       
                        
        # put something here to move csv?
        if self.sessionComplete == True:
            BM.CompleteBatch(BM.currentBatch)

class ConnectionWindow(tk.Frame):
    def __init__(self, parent, controller):
        # define variables
        self.Monitor = StringVar()
        self.comPort = StringVar()
        self.AnalyserUSB = StringVar()
        self.connectedToCom = False
        self.connectedToAnalyser = False
        self.odm_connection = False
        AnalyserUSB = 'COM4'
        comPort = 'COM3'
        Monitor = 'COM5'

        # create the window and frame
        tk.Frame.__init__(self, parent)

        # create the widgets
        self.label_1 = ttk.Label(self, text="ODM monitor port")
        self.label_2 = ttk.Label(self, text="Probe Interface Port")
        self.label_3 = ttk.Label(self, text="Analyser name")

        self.entry_1 = ttk.Entry(self, textvariable=self.Monitor,)
        self.entry_2 = ttk.Entry(self, textvariable=self.comPort, )
        self.entry_3 = ttk.Entry(self, textvariable=self.AnalyserUSB, )
        
        self.entry_1.insert(END, Monitor)
        self.entry_2.insert(END, comPort)
        self.entry_3.insert(END, AnalyserUSB)

        self.label_1.place(relx=0.275, rely=0.2, anchor=CENTER)
        self.label_2.place(relx=0.275, rely=0.4, anchor=CENTER)
        self.label_3.place(relx=0.31, rely=0.3,anchor=CENTER)
        self.entry_1.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.entry_2.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.entry_3.place(relx=0.5, rely=0.3, anchor=CENTER)
        # self.rb1 = ttk.Radiobutton(
        #     self, text='Serial', variable=self.isSerial, value='true')
        # self.rb1.place(relx=0.45, rely=0.5, anchor=CENTER)
        # self.rb2 = ttk.Radiobutton(
        #     self, text='Extended', variable=self.isSerial, value='false')
        # self.rb2.place(relx=0.46, rely=0.55, anchor=CENTER)

        self.connectBtn = ttk.Button(
            self, text="Connect", command=lambda: self._connect_btn_clicked(controller))
        self.connectBtn.grid(row=2, column=1)
        self.connectBtn.place(relx=0.4, rely=0.8, anchor=CENTER)
        self.bind('<Return>', self._connect_btn_clicked)

        self.cancelBtn = ttk.Button(
            self, text="Cancel",  command=lambda: controller.show_frame(ConnectionWindow))
        self.cancelBtn.place(relx=0.6, rely=0.8, anchor=CENTER)

        self.entry_1.focus_set()
        
      
        
            

    def _connect_btn_clicked(self, controller):
        cp = self.comPort.get()
        odm = self.Monitor.get()
        usb = self.AnalyserUSB.get()
        
        try:
            PM.ConnectToAnalyzer(usb)
            self.connectedToAnalyser = True
        except:
            self.connectedToAnalyser = False
            tm.showerror(
                'Connection Error', 'Unable to connect to Analyser Interface\nPlease check the nanoZND Port is correct.')
            
       
        try:
            PM.ConnectToProbeInterface(cp)
                   
            self.connectedToCom = True
        except:
            self.connectedToCom = False
            tm.showerror(
                'Connection Error', 'Unable to connect to Probe Interface\nPlease check the Probe Port is correct.')

        try:
            IM.set_ODM_port_number(odm)  
            self.odm_connection = True
            
        except:
            self.odm_connection = False
            tm.showerror(
                'Connection Error', 'Unable to connect to ODM Interface\nPlease check the ODM Port is correct.')


        if self.connectedToCom and self.connectedToAnalyser and self.odm_connection == True :
            controller.show_frame(TestProgramWindow)
    

        
        
    def exit(self):
        quit()


app = WindowController()
app.mainloop()