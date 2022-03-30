# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 14:18:28 2016

@author: mohsen
"""
import tkinter as tk
import os.path
import serial
import time
import pyvisa as visa
import matplotlib.pyplot as plt
import csv
import datetime
#import sys
import numpy as np


################################################################################
####---------------------------------- SETUP -------------------------------####
################################################################################ 
today = datetime.datetime.now()
DATE_E=str(today.month)+str(today.day)+str(today.year)

if os.path.isdir(r"C:\NU Camera Data"+DATE_E+"\\"):
    print("Destination directory already exists.  Good")
else:
    os.mkdir(r"C:\NU Camera Data"+DATE_E+"\\")

rm = visa.ResourceManager()
lis=rm.list_resources()
print ("avaliable modules:",lis)
GP_type="GPIB0"
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM7'
Sens_Table=[1e-12, 2e-12, 5e-12, 1e-11, 2e-11, 5e-11, 1e-10, 2e-10, 5e-10, 1e-9, 2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]

print ('Initializing ALL...')
def Init_DMM(rm): 
    dmm_name = GP_type+'::22::INSTR'
    try:
        if not dmm_name in rm.list_resources(dmm_name):
            raise visa.VisaIOError(1) #randomly chosen error code
        DMM=rm.open_resource(dmm_name)  ## Digital Multi Meter Agilent 34410A
        DMM.write('*RST') 
        DMM.write('CONF:VOLT:DC 10') 
        DMM.write('VOLT:DC:NPLC 10') 
        return DMM
    except visa.VisaIOError:
        print("Not attached to Digital Multimeter\n")
        return None
# def Init_HPP(rm):
#     hpp_name = GP_type+'::20::INSTR'
#     try:
#         if not hpp_name in rm.list_resources(hpp_name):
#             raise visa.VisaIOError(1) #randomly chosen error code   
#         HPP=rm.open_resource(hpp_name)  ## HP 8164A
#         HPP.write('INP2:WAV +1.5500000E-006')
#         HPP_stat=True
#         return HPP
#     except visa.VisaIOError:
#         print("Not attached to attenuator mainframe!\n")
#         return None
# def Init_MC(rm):
#     mc_name = GP_type+'::1::INSTR' #motor controller
#     try:
#         if not mc_name in rm.list_resources(mc_name):
#             raise visa.VisaIOError(1) #randomly chosen error code
#         MC=rm.open_resource(mc_name)
#         return MC
#     except visa.VisaIOError:
#         print("Not attached to motor controller!\n")
#         return None   
def Init_DGen(rm):
    dgen_name = GP_type+'::15::INSTR' #delay generator
    try:
        if not dgen_name in rm.list_resources(dgen_name):
            raise visa.VisaIOError(1) #randomly chosen error code
        DGen=rm.open_resource(dgen_name)
        return DGen
    except visa.VisaIOError:
        print("Not attached to delay generator!\n")
        return None     
# def Init_myScope(rm):
#     SCOPE_VISA_ADDRESS=GP_type+'::13::INSTR'
#     try:
#         if not SCOPE_VISA_ADDRESS in rm.list_resources(SCOPE_VISA_ADDRESS):
#             raise visa.VisaIOError(1) #randomly chosen error code
#         myScope = rm.open_resource(SCOPE_VISA_ADDRESS)
#         print ("Oscope is initialized")
#         return myScope
#     except visa.VisaIOError:
#         print("Not attached to Oscope!\n")
#         return None
#    except:
#        print ("Unable to connect to oscilloscope at " + str(SCOPE_VISA_ADDRESS) + ". Aborting script.\n")
#        sys.exit()
#        return None
# def Init_DC(rm):
#     dc_name = GP_type+'::25::INSTR' #DC
#     try:
#         if not dc_name in rm.list_resources(dc_name):
#             raise visa.VisaIOError(1) #randomly chosen error code
#         DC=rm.open_resource(dc_name)
#         return DC
#     except visa.VisaIOError:
#         print("Not attached to DC power supply!\n")
#         return None  

#global myScope
#global DMM
#global MC
#global HPP
#global DGen
# myScope = Init_myScope(rm)
DMM = Init_DMM(rm)
# MC = Init_MC(rm)
# HPP = Init_HPP(rm)
# DGen = Init_DGen(rm)
# DC = Init_DC(rm)
Current_Sensitivity=0
Dark_Current = []  #if this doesn't work, go yell at Cobi. it used to be defined as <global Dark_Current> in a function
    
def isInitialized(instr,initializer):
    if instr is None:
        instr = initializer(rm)
        if instr is None:
            return False
    return True


################################################################################
####--------------------------- HELPER FUNCTIONS ---------------------------####
################################################################################
def check_name(name):
    i=0
    while os.path.exists('{}{:d}.png'.format(name, i)):
        i += 1
    return '{}{:d}.png'.format(name, i)

def Set_Integ_Time():
    if not isInitialized(DMM,Init_DMM):
        return
    Int=DMM_E1.get()
    print ('VOLT:DC:NPLC '+ Int )
    DMM.write('VOLT:DC:NPLC '+ Int ) 
    
# def Set_DC():
#     if not isInitialized(DC,Init_DC):
#         return
#     Int=DC_E1.get()
#     print ('APPL P25V,'+Int+',0.002')
#     DC.write('APPL P25V,'+Int+',0.002')
#    power=DC.read()
#    print(power)
#    return power

def SET_Gain_Op_mode():
    if(ser.isOpen() == False):
        ser.open()
    ser.write(("GNMD "+ str(Gmode_E1.get())+ '\r\n').encode('utf-8'))
    print (Gmode_E1.get())
   
def savefile(Input,save_path,name_of_file): 
    completeName = os.path.join(save_path, name_of_file+".txt")  
    file = open(completeName, "w")
    for item in Input:
      file.write("%s\n" % item)
    file.close()

def saveCSV(Input,save_path,name_of_file):
    completeName = os.path.join(save_path, name_of_file+".csv")  
    with open(completeName, 'a') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(Input)

def Cal_gain(Ph_Current):
    gg=[0]*len(Ph_Current)
    gg[0]="Responsivity withot considering any insertion loss"
    gg[1]=Ph_Current[1]
    for ii in range(1, len(Ph_Current)-1):
         print (ii)
         gg[ii+1]=1e9*(Ph_Current[ii+1]-Dark_Current[ii+1])/Ph_Current[1]
    return gg

# def Read_Sensor():
#     if not isInitialized(HPP,Init_HPP):
#         return
#     HPP.write('fetc1:pow?')
#     power=float(HPP.read())
#     return power

# def attenuation(att):
#     if not isInitialized(HPP,Init_HPP):
#         return
#     atten="INP2:ATT %sdB" %att
#     print (atten)
#     HPP.write(atten) 
#     time.sleep(3)

# def On_Off_Att():
#     if not isInitialized(HPP,Init_HPP):
#         return
#     HPP.write('OUTP2:STAT?')
#     if float(HPP.read())==0:
#         HPP.write('OUTP2:STAT ON')
#         print ('Now is ON')
#     else:
#         HPP.write('OUTP2:STAT OFF')
#         print('Now is OFF')

# def Set_Att():
#     if not isInitialized(HPP,Init_HPP):
#         return
#     att=float(Att_E1.get())
#     attenuation(att)
#     if float(HPP.read())==0:
#         HPP.write('OUTP2:STAT ON')
#     print ('Now is ON and SET')

# def move_mc(Act_num,d):
#     if not isInitialized(MC,Init_MC):
#         return
#     d=d/1000
#     cfa=Act_num+"PR%s" % d
#     MC.write(cfa)

# def Relative_move(): #for a GUI button
#     if not isInitialized(MC,Init_MC):
#         return
#     print ("Actuator number %s is Moved %s um." % (MCE1.get(), MCE2.get()))
#     b=float(MCE2.get())
#     b=b/1000
#     cfa=MCE1.get()+"PR%s" % b
#     print (cfa)
#     MC.write(cfa)

def Init_LNA():
    set_point=Init_E0.get()
    Set_Sens=Init_E1.get()
    if(ser.isOpen() == False):
            ser.open()   
    ser.write(("BSON "+ "1"+ '\r\n').encode('utf-8'))
    time.sleep(.2)
    ser.write(("BSLV "+ set_point+ '\r\n').encode('utf-8'))
    time.sleep(1)
    ser.write(("SENS "+ Set_Sens+ '\r\n').encode('utf-8'))
    ser.close()
    
def split_number(a):
    l=a.find('.')
    if l>0:
        return a[:l]+'p'+a[l+1:]
    elif l==0:
        return '0'+'p'+a[1:]
    else:
        return a

# def Change_offset_delaygen():
#     DGen.write("LOFF 1,"+Speed_E1.get())
    
# def Change_level_delaygen():
#     DGen.write("LAMP 1,"+Speed_E2.get())

# def Change_delay_delaygen():
#     DGen.write("DLAY 3,2,"+Speed_E3_2.get())

################################################################################
####--------------------------- PLOTTING ROUTINES --------------------------####
################################################################################

# def plot_gainvspower(x,y):
#    plt.figure(3)
#    plt.xlabel('power, nW')
#    plt.ylabel('Resposivity, A/W')
#    plt.scatter(x,y,color=CE8.get())    
#    #plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
#    plt.xscale("log")      
#    plt.show() 
#    plt.pause(0.001)
   
# def plot_gainvspower2(x,y,sel):
#     if sel==0:
#         plt.figure(9)
#     else:
#         plt.figure()
#     name=E1.get()
#     save_path =E0.get()
#     ax_y1=.95*min(y)
#     ax_y2=1.05*max(y)
#     ax_x1=.9*min(x)
#     ax_x2=1.1*max(x)    
#     plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
#     plt.scatter(x,y,color=CE8.get(),marker=ME8.get(),label=name)
#     plt.xscale('log')
#     plt.title('Scan')
#     plt.xlabel('Power , nW')
#     plt.ylabel('Responsivity, A/W')
#     plt.legend(bbox_to_anchor=(.9, .9),
#            bbox_transform=plt.gcf().transFigure)
#     if sel==0:
#         name=check_name(save_path+name+'Gain_all_')
#         plt.savefig(name)
#     else:
#         name=check_name(save_path+name+'Gain_')
#         plt.savefig(name)
#         plt.close()

def plot_add(x,y,ax_x1,ax_x2,ax_y1,ax_y2,fig_num,subp):
    plt.figure(fig_num)
    plt.subplot(subp)
    if subp==122:
        plt.ylabel('Gain')
    else: 
        plt.ylabel('Current, A')
    plt.xlabel('Voltage, mV')
    plt.scatter(x,y,color=CE8.get(),marker=ME8.get())    
    plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
    plt.yscale("log")      
    #plt.show() 
    plt.pause(0.001)

def plott(x,y,title,sel):
    if sel==0:
        plt.figure(5)

#        ME8.set()
    else:
        plt.figure()

    plt.ion()
    plt.show()
    ax_y1=.2*min(y)
    ax_y2=15*max(y)
    ax_x1=min(x)
    ax_x2=max(x)    
    plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
    plt.scatter(x,y,color=CE8.get(),marker=ME8.get(),label=title)
    plt.yscale('log')
    plt.title('IV Sweep')
    plt.xlabel('Voltage, mV')
    plt.ylabel('Current, A')
    plt.legend(bbox_to_anchor=(.9, .9),
           bbox_transform=plt.gcf().transFigure)
    name=E1.get()
    save_path =E0.get()
    if sel==0:
        name=check_name(save_path+name+'Dark_all_')
        plt.savefig(name)
    else:
        name=check_name(save_path+name+'Dark_')
        plt.savefig(name)
        plt.close()
    
# def plot_scan(x,y):
#     plt.figure(2)
#     plt.ion()
#     plt.show()
       
#     plt.xlabel('Scan, um')
#     plt.ylabel('Photo current, A')
#     plt.scatter(x,y,color=CE8.get())    
#     #plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
#     plt.yscale("log")      
#     # plt.show() 
#     plt.pause(0.001)

# def plot_scan2(x,y,sel):
#     if sel==0:
#         plt.figure(7)
#     else:
#         plt.figure()
#     plt.ion()
#     plt.show()
#     name=E1.get()
#     save_path =E0.get()
#     ax_y1=.2*min(y)
#     ax_y2=15*max(y)
#     ax_x1=min(x)
#     ax_x2=max(x)    
#     plt.axis([ax_x1, ax_x2, ax_y1, ax_y2])
#     plt.scatter(x,y,color=CE8.get(),marker=ME8.get(),label=name)
#     plt.yscale('log')
#     plt.title('Scan')
#     plt.xlabel('X axis, um')
#     plt.ylabel('Current, Ampere')
#     plt.legend(bbox_to_anchor=(.9, .9),
#            bbox_transform=plt.gcf().transFigure)
   
#     if sel==0:
#         name=check_name(save_path+name+'Scan_all_')
#         plt.savefig(name)
#     else:
#         name=check_name(save_path+name+'Scan_')
#         plt.savefig(name)
#         plt.close()
    
################################################################################
####----------------------- FULL MEASUREMENT ROUTINES ----------------------####
################################################################################
    
"""This function Measures the IV curve"""
def IV_Meas(neg_bias,pos_bias,step,Initial_Sens,delay,sub_plot):
    def set_sens(Current_Sensitivity):
        Sens_Loop=True
        while(Sens_Loop):   # we shoukld make sure that new bias voltage didnt make the implifier to saturete
            #loop through sensitivity until no longer saturated, sense_loop => False
            print ('sens' ,Current_Sensitivity)
            ser.write(("SENS "+ str(Current_Sensitivity)+ '\r\n').encode('utf-8'))
            time.sleep(delay+.1) #this delay is very important
            DMM.write('READ?')    
            Test1=float(DMM.read())
                        
            if -4<Test1<4: # this limit can change. 
                Sens_Loop=False
                Dark_Current1=Sens_Table[Current_Sensitivity]*Test1
                print ("DMM voltage", Test1,"\ndark", Dark_Current1)
            elif Current_Sensitivity<27:                    
                Current_Sensitivity = Current_Sensitivity + 1                   
                time.sleep(delay+.1)
            else:
                Sens_Loop=False
                Dark_Current1=Sens_Table[Current_Sensitivity]*Test1
                print ("dark", Dark_Current1,"\nMaximum Sens _ Take Care!!!!")

        return Dark_Current1, Current_Sensitivity

    def loop_lin_step(starting_bias, step, ending_bias, Current_Sensitivity):
        run = True
        Dark_Current = []
        InV = []
        loop_count = 0

        
        while run:
            set_point = starting_bias + step*loop_count
            print ('InV', set_point)
            if step>0 and set_point >= ending_bias:
                    set_point = ending_bias
                    run = False
            elif step<=0 and set_point <= ending_bias:
                    set_point = ending_bias
                    run = False
            
            InV.append(set_point)  # here we are adding applied bias voltages to a list name InV
            ser.write(("BSLV "+ str(set_point)+ '\r\n').encode('utf-8'))  # this is the command to change the bias voltage
        
            time.sleep(delay)   # after changing the bias we will wait till everything become stable
            loop_count=loop_count+1

            Dark_Current1, Current_Sensitivity = set_sens(Current_Sensitivity)

            Dark_Current.append(abs(Dark_Current1))
            ax_x2=starting_bias
            ax_x1=ending_bias
            if ending_bias>starting_bias:
                ax_x1=starting_bias
                ax_x2=ending_bias
            
            ax_y1=.2*min(Dark_Current)
            ax_y2=15*max(Dark_Current)            
            plot_add(set_point,abs(Dark_Current1),ax_x1,ax_x2,ax_y1,ax_y2,1,sub_plot) # refer to the function
        
        return Dark_Current, InV, Current_Sensitivity


    if not isInitialized(DMM,Init_DMM):
        return
    if(ser.isOpen() == False):
            ser.open()
    ser.write("BSON 1".encode('utf-8'))
    
    SET_Gain_Op_mode()
    Set_Integ_Time()
    Dark_Current=[]
    InV=[]
#    Current_Sensitivity = 0
    Current_Sensitivity = Initial_Sens
    
    # 0 to +, + to 0, 0 to -, and - to 0
    # Hysteresis Loop
    Dark_Current_loop, InV_loop, Current_Sensitivity = loop_lin_step(0, step, pos_bias, Current_Sensitivity)
    Dark_Current += Dark_Current_loop
    InV += InV_loop

    Dark_Current_loop, InV_loop, Current_Sensitivity = loop_lin_step(pos_bias, -step, 0, Current_Sensitivity)
    Dark_Current += Dark_Current_loop
    InV += InV_loop

    Dark_Current_loop, InV_loop, Current_Sensitivity = loop_lin_step(0, -step, neg_bias, Current_Sensitivity)
    Dark_Current += Dark_Current_loop
    InV += InV_loop

    Dark_Current_loop, InV_loop, Current_Sensitivity = loop_lin_step(neg_bias, step, 0, Current_Sensitivity)
    Dark_Current += Dark_Current_loop
    InV += InV_loop
        
    ser.close()
    return (InV,Dark_Current)
    
    
def meas_n(): 
    # usingAttenuator = True
    # if not isInitialized(HPP,Init_HPP):
    #     usingAttenuator = False
    # if usingAttenuator:
    #     if bool(int(HPP.query("OUTP2:STAT?").strip()))==True:   #if this doesn't work, go yell at Cobi. He changed it from using HPP_stat as a global bool
    #         HPP.write('OUTP2:STAT OFF')
    name=E1.get()
    neg_bias=int(E3.get())
    pos_bias=int(E4.get())
    step=int(E5.get())
    Initial_Sens=int(E6.get())
    delay=float(E7.get())
    save_path =E0.get()
    InV1,Dark_Current1=IV_Meas(neg_bias,pos_bias,step,Initial_Sens,delay,111)
    
    # if usingAttenuator:
    #     actaul_att=float(HPP.ask('INP2:ATT?'))
    #     actual_power=1e9*Read_Sensor()
    # else:
    #     actaul_att = 0
    #     actual_power = 0
    # print ("Power is %s nW" % actual_power)
    # #name_of_file = name+"_Att =%s dB_Pw =%s" %  (actaul_att,actual_power)
    # csvThing="Att =%s dB_Pw =%s nW" %  (actaul_att,actual_power)
    
    # InV1.insert(0,"Power(nW)")
    # InV1.insert(0,"Voltage") 
    
    # Dark_Current1.insert(0,actual_power)
    # Dark_Current1.insert(0,csvThing)
    
    # plott(InV1[2:],Dark_Current1[2:],name,0)
    # plott(InV1[2:],Dark_Current1[2:],name,1)
    plott(InV1,Dark_Current1,name,0)
    plott(InV1,Dark_Current1,name,1)
    saveCSV(InV1,save_path,name)
    saveCSV(Dark_Current1,save_path,name)


# def meas_gain2():
#     if not isInitialized(HPP,Init_HPP):
#         return
#     name=E1.get()
#     n=int(E2.get())
#     starting_bias=int(E3.get())
#     ending_bias=int(E4.get())
#     step=int(E5.get())
#     Initial_Sens=int(E6.get())
#     delay=float(E7.get())
#     save_path =E0.get()
#     max_att =float(E8.get())
#     att_step =float(E9.get())
#     HPP.write('OUTP2:STAT OFF')
#     InV,Dark_Current=IV_Meas(starting_bias,ending_bias,step,Initial_Sens,delay,121)
#     #savefile(Dark_Current,save_path,name+"_DarK")
#     #savefile(InV,save_path,name+"_Voltage")
    
#     InV.insert(0,"Power(nW)")     
#     InV.insert(0,"Voltage") 
#     Dark_Current.insert(0,"0")
#     Dark_Current.insert(0,"Dark_Current")
#     saveCSV(InV,save_path,name)
#     saveCSV(Dark_Current,save_path,name)
#     HPP.write('OUTP2:STAT ON') 
#     time.sleep(1)
#     for ii in range(0, n):
#         print( ii)
#         Att=max_att-att_step*ii
#         attenuation(Att)
#         actaul_att=float(HPP.ask('INP2:ATT?'))
#         actual_power=1e9*Read_Sensor()
#         print ("Power is %s nW" % actual_power)
#         #name_of_file = name+"_Att =%s dB_Pw =%s" %  (actaul_att,actual_power)
#         csvThing="Att =%s dB_Pw =%s nW" %  (actaul_att,actual_power)
#         InV1,Current1=IV_Meas(starting_bias,ending_bias,step,Initial_Sens,delay,121)
#         Current1.insert(0,actual_power)
#         Current1.insert(0,csvThing)
#         gain=Cal_gain(Current1)
#         ax_x1=ending_bias;
#         ax_x2=starting_bias;
#         ax_y1=.2*min(gain[2:])
#         ax_y2=15*max(gain[2:])   
#         saveCSV(Current1,save_path,name)
#         saveCSV(gain,save_path,name)
#         plot_add(InV[2:],gain[2:],ax_x1,ax_x2,ax_y1,ax_y2,1,122)
#     HPP.write('OUTP2:STAT OFF') 
  

# def gain_vs_power():
#     if not isInitialized(HPP,Init_HPP):
#         return
# #    global Dark_Current
#     name=E1.get()
#     n=int(E2.get())
#     starting_bias=int(G_vs_Power_E1.get())
#     ending_bias=int(G_vs_Power_E1.get())
#     step=int(E5.get())
#     Initial_Sens=int(E6.get())
#     delay=float(E7.get())
#     save_path =E0.get()
#     max_att =float(E8.get())
#     att_step =float(E9.get())
#     HPP.write('OUTP2:STAT OFF')
#     InV,Dark_Current=IV_Meas(starting_bias,ending_bias,step,Initial_Sens,delay,121)
    
#     InV.insert(0,"Power(nW)")     
#     InV.insert(0,"Voltage") 
    
#     Dark_Current.insert(0,"0")
#     Dark_Current.insert(0,"Dark_Current")
#     saveCSV(InV,save_path,name)
#     saveCSV(Dark_Current,save_path,name)
    
#     HPP.write('OUTP2:STAT ON') 
#     GGain1=[]
#     PPow1=[]
#     for ii in range(0, n):
#         print (ii)
#         Att=max_att-att_step*ii
#         attenuation(Att)
#         actaul_att=float(HPP.ask('INP2:ATT?'))
#         actual_power=1e9*Read_Sensor()
        
#         print ("Power is %s nW" % actual_power)
#         #name_of_file = name+"_Att =%s dB_Pw =%s" %  (actaul_att,actual_power)
#         csvThing="Att =%s dB_Pw =%s nW" %  (actaul_att,actual_power)
        
#         InV1,Current1=IV_Meas(starting_bias,ending_bias,step,Current_Sensitivity,delay,121)
        
#         Current1.insert(0,actual_power)
#         Current1.insert(0,csvThing)
#         gain=Cal_gain(Current1)
#         GGain1.append(gain[2])
#         PPow1.append(actual_power)
#         plot_gainvspower(actual_power,gain[-1])

#         saveCSV(Current1,save_path,name)
#         saveCSV(gain,save_path,name)
        
#     plot_gainvspower2(PPow1,GGain1,0)
#     plot_gainvspower2(PPow1,GGain1,1)
#     HPP.write('OUTP2:STAT OFF')   
 


##def Scan():    ## This part is used to scan the illumination undet the sample and get the spatial response of the detector
#    if not (isInitialized(HPP,Init_HPP) and isInitialized(MC,Init_MC)):
#        return
# #   if bool(int(HPP.query("OUTP2:STAT?").strip()))==False:   #if this doesn't work, go yell at Cobi. He changed it from using HPP_stat as a global bool
# #      HPP.write('OUTP2:STAT ON')
#    
#    Act_num=Scan_E4.get()   ## which actuator we want to scan
#    n=int(Scan_E2.get())        ## number of scans
#    Res=float(Scan_E3.get())   ###resolution of scan in um
#    
#    
#    name=E1.get()
#    bias=int(Scan_E1.get())
#    starting_bias=bias
#    ending_bias=bias
#    step=int(E5.get())
#    Initial_Sens=int(Scan_E5.get())
#    delay=float(E7.get())
#    save_path =E0.get()
#    actual_pos=MC.ask(Act_num+'TP')
#    
#    move_d=round(-n/2)*Res  
#    print (move_d)
#    move_mc(Act_num,move_d)
#    time.sleep(1)
#    move_mc(Act_num,15)   ## this is for back-lash
#    time.sleep(1)
#    
#    
#    print (actual_pos)
#    if float(Act_num)==2:
#        axis='x'
#    else:
#        axis='y'
#        
# #   float(HPP.ask('INP2:ATT?'))
##    actual_power=1e9*Read_Sensor()
#    topp=[];
#    topp.append("Relative Position um")
#    topp.append("direction")
#    topp.append("ABSOLUTE Position mm")
#  #  topp.append("current at power level %s nW" %actual_power) 
#    saveCSV(topp,save_path,name) 
#    
#    InV1,Current=IV_Meas(starting_bias,ending_bias,step,Initial_Sens,delay,111)
#    Pos=[move_d]
#    act_pos2=float(MC.ask(Act_num+'TP'))
#    Pos.append(axis)
#    Pos.append(act_pos2)
#    Pos.append(Current[0])
#    saveCSV(Pos,save_path,name)
#    plot_scan(Pos[0],Current[0])
#    global CC
#    CC=[]
#    CC.append(Current[0])
#    Sensivity=Initial_Sens
#    CCur1=[]  ### A list to save all the currents
#    PPos1=[]  ### A list to save all the positions
#    for ii in range(1, n+1):
#        
#        print( ii)
#        move_mc(Act_num,Res)
#        InV1,Current=IV_Meas(starting_bias,ending_bias,step,Sensivity,delay,111)
#        
#        
#        CC.append(Current[0])
#        Pos=[move_d+Res*ii]
#        act_pos2=float(MC.ask(Act_num+'TP'))
#        Pos.append(axis)
#        Pos.append(act_pos2)
#        Pos.append(Current[0])
#        saveCSV(Pos,save_path,name)
#        plot_scan(Pos[0],Current[0])
#        
#        CCur1.append(Current[0])
#        PPos1.append(Pos[0])
#        ratio=abs(CC[-1])/abs(CC[-2])
#        
#        if 0.4<=ratio<.95:
#            Sensivity=Current_Sensitivity-1
#        elif .95<=ratio<2.5:
#            Sensivity=Current_Sensitivity
#        elif 2.5<=ratio: 
#            Sensivity=Current_Sensitivity+1
#            
#        else:
#            Sensivity=Initial_Sens
#     
#               
#    plot_scan2(PPos1,CCur1,0)
#    plot_scan2(PPos1,CCur1,1)        
#        
#    time.sleep(1)    
#    MC.write(Act_num+'PA'+actual_pos)   


def Sweep_Pulse():
    if not (isInitialized(myScope,Init_myScope) and isInitialized(DGen,Init_DGen)):
        return
#    myScope.write(":SAVE:WAVeform:FORMat csv") 
    DC_V=float(Speed_E1.get())
    Change_offset_delaygen()
    time.sleep(1)
    Change_level_delaygen()
    Pulse = float(Speed_E2.get())
    start= float(Speed_E1_2.get())
    stop=float(Speed_E3.get())
    step=float(Speed_E4.get())
#    step=round((stop-start)/number, 2)
    Atten=start
    nn=0
    while Atten<=stop:
#        att=str(float(HPP.ask('INP2:ATT?')))
#        att=split_number(att)
        
        DGen.write("DLAY 3,2,0")
        P=str(Pulse+DC_V)
        Pow=Pulse+DC_V
        DGen.write("LOFF 1,"+P)
        time.sleep(.6)
        actual_power=1e6*Read_Sensor()
        power_str="%0.5f" %actual_power
        power_ref=split_number(power_str)
        time.sleep(.05)
        print( "Power ref= ",power_ref,"uW at",str(round(Atten,2)),"Volt attenuation")
        Change_offset_delaygen()
        time.sleep(.05)    
        Change_delay_delaygen()
        time.sleep(.05)

        Volt_str="%0.1f" %Pow
        Volt_ref =split_number(Volt_str)
        name="speed_"+DATE_E+"_V"+Volt_ref+"_"+power_ref+"_"+Speed_E5.get()+"_"+Speed_E6.get()
        print(name)
              
        # DC.write("LAMP 1,"+str(Pulse)')
        DC.write('APPL P25V,'+str(Atten)+',0.002')
        time.sleep(1)
        
        myScope.write(":STOP"); time.sleep(.1)
        myScope.write(":SAVE:WAVeform:FORMat csv")
        time.sleep(1)
        myScope.write(":SAVE:WAV:STAR '"+name+"'")
        time.sleep(2)
        myScope.write(":RUN")
        time.sleep(1)

#        myScope.write(":STOP"); time.sleep(.1)
#        myScope.write(":SAVE:IMAGe:FORMat PNG")
#        time.sleep(1)
#        myScope.write(":SAVE:IMAG:STAR '"+name+"'")   
#        time.sleep(2)
#        myScope.write(":RUN")
#        time.sleep(1)
        
        Atten=Atten+step
        nn=nn+1
    print ("done")

def Sweep_DC():
    if not (isInitialized(myScope,Init_myScope) and isInitialized(DGen,Init_DGen)
                    and isInitialized(HPP,Init_HPP)):
        return
    myScope.write(":SAVE:WAVeform:FORMat csv") 
    Puls=float(Speed_E2.get())
    Change_offset_delaygen()
    time.sleep(1)
    Change_level_delaygen()
    
    start= float(Speed_E1.get())
    print( "start", start)
    
    stop=float(Speed_E1_2.get())
    
    step=float(Speed_E4.get())
#    step=round((stop-start)/number, 2)
    current_DC=start
    nn=0
    while current_DC<=stop:
        DGen.write("LOFF 1,"+str(current_DC))
        time.sleep(2)
        att=str(float(HPP.ask('INP2:ATT?')))
        att=split_number(att)
        name="speed_"+DATE_E+"_att_"+att+"dB_sample_"+Speed_E5.get()+"_device_"+Speed_E6.get()+"_DC"+str(round(current_DC*1000,0))[:-2]+"mV_Pulse"+str(round(Puls*1000,0))[:-2]+"mV"
        print (name)       
        myScope.write(":SAVE:WAV:STAR '"+name+"'")
        time.sleep(6)
        current_DC=current_DC+step
        nn=nn+1
    print("done")





################################################################################
####-------------- CALIBRATION? I'M NOT SURE WHAT TO CALL THESE ------------####
################################################################################

# def cal_attenuation():
#     if not (isInitialized(DGen,Init_DGen) and isInitialized(HPP,Init_HPP)):
#         return
#     DGen.write("DLAY 3,2,0")
#     time.sleep(.05)    
#     DGen.write("LOFF 1,1.5")
#     actual_power=1e6*Read_Sensor()
#     time.sleep(.05)
#     power_ref=float(Speed_E7.get())
#     atten=power_ref/actual_power
#     atten=10*np.log10(atten)
#     print( atten)
#     time.sleep(.1)
#     Change_offset_delaygen()
#     time.sleep(.1)    
#     Change_delay_delaygen()
#     return atten

# def cal_power_ref():
#     if not (isInitialized(DGen,Init_DGen) and isInitialized(HPP,Init_HPP)):
#         return
#     DGen.write("DLAY 3,2,0")
#     DC=float(Speed_E1.get())
#     AC=float(Speed_E2.get())
#     P=str(AC+DC)
    
#     DGen.write("LOFF 1,"+P)
#     time.sleep(.6)
#     actual_power=1e6*Read_Sensor()
#     time.sleep(.05)
#     print( "power ref= ",actual_power,"uW at",P,"Volt")
#     time.sleep(.05)
#     Change_offset_delaygen()
#     time.sleep(.05)    
#     Change_delay_delaygen()
#     return actual_power,P
    

################################################################################
####-------------------------------- SAVING --------------------------------####
################################################################################

def save_png_delaygen():
#    att=str(float(HPP.ask('INP2:ATT?')))
    if not (isInitialized(myScope,Init_myScope) and isInitialized(DGen,Init_DGen)):
        return
    myScope.write(":STOP"); time.sleep(.05)
    myScope.write(":SAVE:IMAGe:FORMat PNG"); time.sleep(.05)
    
    power_ref,Volt_ref=cal_power_ref()
    power_ref=split_number(str(power_ref))
    Volt_ref =split_number(Volt_ref)
    
#    att=cal_attenuation()
#    att=str(att)    
#    att=split_number(att)
    DC=float(DGen.ask("LOFF?1"))
    Puls=float(DGen.ask("LAMP?1"))
#    name="speed_"+DATE_E+"Power_ref_1p5V"+power_ref+"_att_"+att+"dB_sample_"+Speed_E5.get()+"_device_"+Speed_E6.get()+"_DC"+str(round(DC*1000,0))[:-2]+"mV_Pulse"+str(round(Puls*1000,0))[:-2]+"mV"
    name="speed_"+DATE_E+"_Power_ref_"+Volt_ref+"_"+power_ref+"_sample_"+Speed_E5.get()+"_device_"+Speed_E6.get()+"_DC"+str(round(DC*1000,0))[:-2]+"mV_Pulse"+str(round(Puls*1000,0))[:-2]+"mV"
        
    myScope.write(":SAVE:IMAG:STAR '"+name+"'")   
    print (name)
    myScope.write(":RUN")

def save_csv_delaygen():
    if not (isInitialized(myScope,Init_myScope) and isInitialized(DGen,Init_DGen)):
        return
    myScope.write(":STOP"); time.sleep(.05) 
    myScope.write(":SAVE:WAVeform:FORMat csv"); time.sleep(.05)
    DGen.write("DLAY 3,2,0")
    DC_V=float(Speed_E1.get())
    Pulse = float(Speed_E2.get())
    P=str(Pulse+DC_V)
    Pow=Pulse+DC_V
    DGen.write("LOFF 1,"+P)
    time.sleep(.6)
    Volt_str="%0.1f" %Pow
    Volt_ref =split_number(Volt_str)
    actual_power=1e6*Read_Sensor()
    power_str="%0.5f" %actual_power
    power_ref=split_number(power_str)
    time.sleep(.05)
    print( "Power ref= ",power_ref,"uW")
    Change_offset_delaygen()
    time.sleep(.05)    
    Change_delay_delaygen()
    time.sleep(.05)

    name="speed_"+DATE_E+"_V"+Volt_ref+"_"+power_ref+"_"+Speed_E5.get()+"_"+Speed_E6.get()
    print(name)
#    att=str(float(HPP.ask('INP2:ATT?')))
#    DC=float(DGen.ask("LOFF?1"))
#    Puls=float(DGen.ask("LAMP?1"))
#    name="speed_"+DATE_E+"Power_ref_1p5V"+power_ref+"_att_"+att+"dB_sample_"+Speed_E5.get()+"_device_"+Speed_E6.get()+"_DC"+str(round(DC*1000,0))[:-2]+"mV_Pulse"+str(round(Puls*1000,0))[:-2]+"mV"
    myScope.write(":SAVE:WAV:STAR '1'")   
    myScope.write(":RUN")



    
################################################################################
####------------------------------ BUILD THE GUI ---------------------------####
################################################################################

master = tk.Tk()

############################### BOILERPLATE SUBFRAME ###########################
subframe_boil = tk.Frame(master,bd=2,relief='groove')
subframe_boil.grid(row=0,column=0,padx=10,pady=10,rowspan = 3,columnspan=3)

tk.Label(subframe_boil, text="Directory to save").grid(row=1, column=1,pady=2)
E0 = tk.Entry(subframe_boil, bd =5,width = 50)
E0.grid(row=1,column=2,pady=2)
E0.insert(0, r"C:\NU Camera Data"+DATE_E+"\\")

tk.Label(subframe_boil, text="File name").grid(row=2, column=1,pady=2)
E1 = tk.Entry(subframe_boil, bd =5,width=50)
E1.grid(row=2,column=2)
E1.insert(0, DATE_E+"_")

tk.Label(subframe_boil, text="Number of Meas").grid(row=3,column=1,pady=2)
E2 = tk.Entry(subframe_boil, bd =5,width=5)
E2.grid(row=3,column=2,pady=2,sticky="W")
E2.insert(0, '1')


################################ SWEEP? SUBFRAME ###############################
subframe_sweep = tk.Frame(master,bd=2,relief='groove')
subframe_sweep.grid(row=3,column=0,padx=10,pady=10,rowspan = 11,columnspan=2)
tk.Label(subframe_sweep, text="I-V Measurements").grid(row=0, column=1,columnspan=2)

tk.Label(subframe_sweep, text="Max Negative Bias (mv)").grid(row=1,column=1,pady=2)
E3 = tk.Entry(subframe_sweep, bd =5)
E3.grid(row=1,column=2,pady=2)
E3.insert(0, "-2500")

tk.Label(subframe_sweep, text="Max Positive Bias (mv)").grid(row=2,column=1,pady=2)
E4 = tk.Entry(subframe_sweep, bd =5)
E4.grid(row=2,column=2,pady=2)
E4.insert(0, "2500")

tk.Label(subframe_sweep, text="step (mV)").grid(row=3,column=1,pady=2)
E5 = tk.Entry(subframe_sweep, bd =5)
E5.grid(row=3,column=2,pady=2)
E5.insert(0,"100")

tk.Label(subframe_sweep, text="Initial Sensitivity").grid(row=4,column=1,pady=2)
E6 = tk.Entry(subframe_sweep, bd =5)
E6.grid(row=4,column=2,pady=2)
E6.insert(0, str(Current_Sensitivity))

tk.Label(subframe_sweep, text="Delay bw steps").grid(row=5,column=1,pady=2)
E7 = tk.Entry(subframe_sweep, bd =5)
E7.grid(row=5,column=2,pady=2)
E7.insert(0, '0.1')

tk.Label(subframe_sweep, text="Max Att.").grid(row=6,column=1,pady=2)
E8 = tk.Entry(subframe_sweep, bd =5)
E8.grid(row=6,column=2,pady=2)
E8.insert(0, '60')

tk.Label(subframe_sweep, text="Att. Step").grid(row=7,column=1,pady=2)
E9 = tk.Entry(subframe_sweep, bd =5)
E9.grid(row=7,column=2,pady=2)
E9.insert(0, '3')

tk.Label(subframe_sweep, text="Color|brkgycm").grid(row=8,column=1,pady=2)
CE8 = tk.Entry(subframe_sweep, bd =5)
CE8.grid(row=8,column=2,pady=2)
CE8.insert(0, 'b')

tk.Label(subframe_sweep, text="Marker|.,osv<>phH").grid(row=9,column=1,pady=2)
ME8 = tk.Entry(subframe_sweep, bd =5)
ME8.grid(row=9,column=2,pady=2)
ME8.insert(0, 'o')

# tk.Label(subframe_sweep, text="BiasV for G_vs_P (mV)").grid(row=10,column=1,pady=2)
# G_vs_Power_E1 = tk.Entry(subframe_sweep, bd =5)
# G_vs_Power_E1.grid(row=10,column=2,pady=2)
# G_vs_Power_E1.insert(0, -1200)


############################ LNA INITIALIZER SUBFRAME ##########################
subframe_LNA = tk.Frame(master,bd=2,relief='groove')
subframe_LNA.grid(row=14,column=0,padx=10,pady=10,rowspan = 3,columnspan=2)

tk.Label(subframe_LNA, text="Set Voltage").grid(row=1,column=1,pady=2)
Init_E0 = tk.Entry(subframe_LNA, bd =5,width = 10)
Init_E0.grid(row=1,column=2,pady=2)
Init_E0.insert(0, '-1000')

tk.Label(subframe_LNA, text="Set Sens").grid(row=2,column=1,pady=2)
Init_E1 = tk.Entry(subframe_LNA, bd =5,width = 10)
Init_E1.grid(row=2,column=2,pady=2)
Init_E1.insert(0, '2')

tk.Button(subframe_LNA, text ="Init LNA", command = Init_LNA,height = 3, width = 8
          ).grid(row=1,column=3,columnspan=2,rowspan=2,padx=5,pady=2)


################################ SPEED SUBFRAME ################################
# subframe_speed = tk.Frame(master,bd=2,relief='groove')
# subframe_speed.grid(row=0,column=3,padx=10,pady=10,rowspan=10,columnspan=3)
# tk.Label(subframe_speed, text="SPEED Measurements").grid(row=0,column=0,columnspan=3)

# tk.Label(subframe_speed, text="Laser DC Voltage Start [V]").grid(row=1,column=0,pady=2)
# Speed_E1 = tk.Entry(subframe_speed, bd =5)
# Speed_E1.grid(row=1,column=1)
# Speed_E1.insert(0, '0.5')
# tk.Button(subframe_speed, text ="DC", command = Change_offset_delaygen).grid(row=1,column=2)

# tk.Label(subframe_speed, text="Laser Pulse Voltage Start [V])").grid(row=2,column=0,pady=2)
# Speed_E2 = tk.Entry(subframe_speed, bd =5)
# Speed_E2.grid(row=2,column=1,pady=2)
# Speed_E2.insert(0, '0.8')
# tk.Button(subframe_speed, text ="Pulse", command = Change_level_delaygen).grid(row=2,column=2,pady=2)

# tk.Label(subframe_speed, text="Atten. Voltage Start [V]").grid(row=3,column=0,pady=2)
# Speed_E1_2 = tk.Entry(subframe_speed, bd =5)
# Speed_E1_2.grid(row=3,column=1,pady=2)
# Speed_E1_2.insert(0, '0')

# tk.Label(subframe_speed, text="Atten. Voltage Stop [V]").grid(row=4,column=0,pady=2)
# Speed_E3 = tk.Entry(subframe_speed, bd =5)
# Speed_E3.grid(row=4,column=1,pady=2)
# Speed_E3.insert(0, '5')

# tk.Label(subframe_speed, text="Atten. Voltage Step [V]").grid(row=5,column=0,pady=2)
# Speed_E4 = tk.Entry(subframe_speed, bd =5)
# Speed_E4.grid(row=5,column=1,pady=2)
# Speed_E4.insert(0, '0.5')

# tk.Label(subframe_speed, text="Pulse Width [s]").grid(row=6,column=0,pady=2)
# Speed_E3_2 = tk.Entry(subframe_speed, bd =5)
# Speed_E3_2.grid(row=6,column=1,pady=2)
# Speed_E3_2.insert(0, '500e-9')
# tk.Button(subframe_speed, text ="GO", command = Change_delay_delaygen).grid(row=6,column=2,pady=2)

# tk.Label(subframe_speed, text="Sample name").grid(row=7,column=0,pady=2)
# Speed_E5 = tk.Entry(subframe_speed, bd =5)
# Speed_E5.grid(row=7,column=1,pady=2)
# Speed_E5.insert(0, 'sample')

# tk.Label(subframe_speed, text="Device Name").grid(row=8,column=0,pady=2)
# Speed_E6 = tk.Entry(subframe_speed, bd =5)
# Speed_E6.grid(row=8,column=1,pady=2)
# Speed_E6.insert(0, 'device')

# tk.Label(subframe_speed, text="Power at 1.5V bias,uW").grid(row=9,column=0,pady=2)
# Speed_E7 = tk.Entry(subframe_speed, bd =5)
# Speed_E7.grid(row=9,column=1,pady=2)
# Speed_E7.insert(0, '300')
# tk.Button(subframe_speed, text ="mmm", command = cal_attenuation).grid(row=9,column=2,pady=2)


# ############################# LIVE-CONTROLS SUBFRAME ###########################
subframe_live = tk.Frame(master,bd=2,relief='groove')
subframe_live.grid(row=10,column=3,padx=10,pady=10,rowspan = 7,columnspan=3)
tk.Label(subframe_live, text="LIVE CONTROLS").grid(row=0, column=1,columnspan=3)

# tk.Label(subframe_live, text="Actuator Number").grid(row=1,column=1,padx=2, pady=2)
# MCE1 = tk.Entry(subframe_live, bd =5, width=10)
# MCE1.grid(row=1,column=2,padx=2, pady=2)
# tk.Label(subframe_live, text="Move Relative, um").grid(row=2,column=1,pady=2)
# MCE2 = tk.Entry(subframe_live, bd =5, width=10)
# MCE2.grid(row=2,column=2,padx=2, pady=2)
# tk.Button(subframe_live, text ="Go", command = Relative_move, height=2,width=10
#           ).grid(row=1,column=3,columnspan=2,rowspan=2,padx=5,pady=2)

# tk.Button(subframe_live, text ="Set Attenuator", command = Set_Att,width=18
#           ).grid(row=3,column=1,padx=2, pady=2)
# Att_E1 = tk.Entry(subframe_live, bd =5, width=10)
# Att_E1.grid(row=3,column=2,padx=2, pady=2)
# Att_E1.insert(0, '20')
# tk.Button(subframe_live, text ="Off/On Att", command = On_Off_Att,width=10).grid(row=3,column=3)

tk.Button(subframe_live, text ="SET_Gain_Op_mode", command = SET_Gain_Op_mode,width = 18
          ).grid(row=4,column=1,padx=2, pady=2)
Gmode_E1 = tk.Entry(subframe_live, bd =5, width=10)
Gmode_E1.grid(row=4,column=2,padx=2, pady=2)
Gmode_E1.insert(0, "0")

tk.Button(subframe_live, text ="Set Integ Time", command = Set_Integ_Time,width = 18
          ).grid(row=5,column=1,padx=2,pady=2)
DMM_E1 = tk.Entry(subframe_live, bd =5, width=10)
DMM_E1.grid(row=5,column=2,padx=2, pady=2)
DMM_E1.insert(0, "6")

# tk.Button(subframe_live, text ="Set Atten. Volt.", command = Set_DC,width = 18
#           ).grid(row=6,column=1,padx=2,pady=2)
# DC_E1 = tk.Entry(subframe_live, bd =5, width=10)
# DC_E1.grid(row=6,column=2,padx=2, pady=2)
# DC_E1.insert(0, "0")


################################ BUTTONS SUBFRAME ##############################
subframe_buttons = tk.Frame(master,bd=2,relief='groove')
subframe_buttons.grid(row=3,column=2,padx=10,pady=10,rowspan = 15,columnspan=1)

tk.Button(subframe_buttons, text ="Save CSV", command = save_csv_delaygen,fg="red",bg = "blue",
          font=("Arial",10,"bold"),height = 3, width = 12).grid(row=0,column=0,padx=5,pady=5)

tk.Button(subframe_buttons, text ="Save PNG", command = save_png_delaygen,fg="red",bg = "blue",
          font=("Arial",10,"bold"),height = 3, width = 12).grid(row=1,column=0,padx=5,pady=5)

tk.Button(subframe_buttons, text="Sweep Pulse", command = Sweep_Pulse,fg="red",bg = "blue",
          font=("Arial",10,"bold"),height=3, width=12).grid(row=2,column=0,padx=5,pady=5)

# tk.Button(subframe_buttons, text ="Sweep DC bias", command = Sweep_DC,fg="red",bg = "blue",
#          font=("Arial",10,"bold"),height=3, width=12).grid(row=3,column=0,padx=5,pady=5)

tk.Button(subframe_buttons, text ="IV Sweep", command = meas_n,bg="red",fg = "blue",
          font=("Arial",10,"bold"),height=3, width=12).grid(row=3,column=0,padx=5,pady=5)

# tk.Button(subframe_buttons, text ="Gain", command = meas_gain2 ,height = 3, width = 12
#           ).grid(row=4,column=0,padx=5,pady=5)

# tk.Button(subframe_buttons, text ="Gain_vs_power", command = gain_vs_power,height = 3, width = 12
#           ).grid(row=5,column=0,padx=5,pady=5)


#the line that starts the GUI loop itself running.  Congrats we've made the GUI!
master.mainloop()