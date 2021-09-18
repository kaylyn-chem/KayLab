"""
Haiiiii dis is Kaylyn's python code for analysing Square Wave Voltammetry Files generated by Palmsense potentiostats. It is adapted from Gabi Ortega's matlab code. 
It works for one channel or multi channel. 
If you need help, go find Kaylyn or email kaylyn.leung@gmail.com
"""
autobase=1###1 turns on autobase, 0 you check each baseline######
autosavebase=0###1 all baseline images get saved as a png in path, 0 no images of the baseline are saved
import os
import sys
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

####################Functions needing Definition##################
plt.rcParams["keymap.quit"] = "x"
# a: NumPy 1-D array containing the data to be smoothed
# WSZ: smoothing window size needs, which must be odd number,
# as in the original MATLAB implementation
def smooth(a,WSZ):
    out0 = np.convolve(a,np.ones(WSZ,dtype=int),'valid')/WSZ
    r = np.arange(1,WSZ-1,2)
    start = np.cumsum(a[:WSZ-1])[::2]/r
    stop = (np.cumsum(a[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((  start , out0, stop  ))
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#####Labels#################
E_label="E(V/Ag|AgCl)"
I_label= "I (μA)"
t_label= "Time (min)"
f_label= "Freq (Hz)"
In_label= "Signal"
Ch_label= "Charge (C)"
####Styles#############
color_choice=["red","blue","green","black","magenta","brown","violet","cyan","orange","gold","brown","orchid","gray","olive","darkred","darkblue","darkgreen","dimgrey","darkmagenta","darkgoldenrod","darkviolet","darkcyan","darkorange","darkorchid","darkgray","olivedrab"]

##########################################################
cls()
print('====================================================================== ')
print( '        Hello My Friend, its TIME to Do Data Analysis')
print('======================================================================')
if autobase==1:
    print('Automatic baseline has been turned on. To change autobase to 0')

###########Defining the electrodes to be analyzed, and numelecs as the total # of electrodes via inputs#####################################
shell="a" or input("Anaconda or Ubuntu?(Type a or u):\n")
elec=input('Electrode number (e.g. 1, 2, 4) :\n ') or "1,2"
if len(elec)>1:
    elec=np.sort(eval(elec))
numelecs = len(elec)
sqwvfreqs = input ('At least two Freqs in Hz (e.g. 50 , 300):\n') or "5,7,11, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800"
KDM_Freqs= input('The two frequencies for KDM (e.g. 50,300):\n') or sqwvfreqs
norm_point=input('Normalization point (e.g. 27 for 27th point:\n') or "1"
norm_point=int(norm_point)
KDM_Freqs=np.sort(eval(KDM_Freqs))
f_KDM_high=KDM_Freqs[-1]; f_KDM_low=KDM_Freqs[0]
sqwvfreqs=np.sort(eval(sqwvfreqs))
KDM_hindex=int(np.argwhere(sqwvfreqs==f_KDM_high));KDM_lindex=int(np.argwhere(sqwvfreqs==f_KDM_low))
numfreqs=len(sqwvfreqs)
tit_tot=input('Total Number of Titration points:\n') or "2"
tit_tot=int(tit_tot)+1
titno=list(range(1,tit_tot))
titlength=len(titno)
name = input('Naming Prefix here:\n') or 'E1_'
if 'u' in shell:
    path=input('This will not work')  
if 'a' in shell:
    path=input('Paste your file directory here:\n') 
os.chdir(path)

###Array Building####
filename=np.empty([titlength], dtype=object)
filetime=np.empty([titlength], dtype=object)
timedelta=np.empty([titlength] )

E_array = np.empty([numfreqs,numelecs,titlength], dtype=object)
I_array = np.empty([numfreqs,numelecs,titlength], dtype=object)
I_peak_array=np.empty([numelecs,numfreqs,titlength])
I_charge_array=np.empty([titlength,numelecs,numfreqs])
I_norm_array=np.empty([numelecs,numfreqs,titlength])
I_init=np.empty([numelecs,numfreqs])

Ratio=np.empty([numelecs,titlength])
Avg=np.empty([numelecs,titlength])
Diff=np.empty([numelecs,titlength])
KDM=np.empty([numelecs,titlength])

###########################################################
############Calling up the data############################
###########################################################
for f in range(tit_tot-1):
    titpnt=str(titno[f])
    ##Loop for Frequencies
    for k in range(numfreqs):
        freq= str(sqwvfreqs[k])
        if 'u' in shell:
            myfilename=path+'/'+name+freq+'Hz-'+titpnt+'.csv'
        if 'a' in shell:
            myfilename=path+"\\"+name+freq+'Hz-'+titpnt+'.csv'
        
        #####Stalls loop while waiting for file. Enables real-time analysis
        r=0
        brk=0
        while not os.path.isfile(myfilename):
           cls()
           r=r+1
           maxtime=10#Change me to be at least the time resolution of the measurement.
           r_b=maxtime-r
           print("Wait for "+str(r_b)+" seconds")
           time.sleep(1)
           if r==maxtime:
            print("No more files available")
            brk=1
            break
        if brk==1:
            break#Gets out of loop after search for new datafile times out 
        
        ###Loops for Electrodes############################
        for h in range(numelecs):
            #If data has headers or not.
            pot=np.loadtxt(myfilename,dtype='float', delimiter=',', skiprows=6, usecols=0,encoding='utf-16', comments="\ufeff")
            Idif=np.loadtxt(myfilename,dtype='float',delimiter=',', skiprows=6, usecols=(1+2*(int(elec[h]))),comments="\ufeff",encoding='utf-16')
            ######Smoothing variables. WSZ is window size and must be odd numbers
            if sqwvfreqs[k]<100:
                WSZ=3
            else:
                WSZ=5
            I=smooth(Idif,WSZ)
            E_array[k,h,f]=pot
            I_array[k,h,f]=I
    #Back in Titration Point Loop
    if brk==1:
        break#Gets out of loop after search for new datafile times out 

####################Plotting time##########################################
    if f==0:
        fig,axs=plt.subplots(numelecs,sharex=True,constrained_layout=True, squeeze=False)
        plt.xlabel(E_label)
        print('Plotting time....')
        for h in range(numelecs):
            for k in range(numfreqs):
               axs[h,0].plot(E_array[k,h,f],I_array[k,h,f])
               axs[h,0].set_ylabel(I_label)
               axs[h,0].legend(['E'+str(elec[h])])
        print('press x to close')
        plt.show(block=False)

###########Baseline determination###################/########################
        #This is to preserve the analysis if you accidentally type something incorrectly#
        try:
            limits=input('Lower limit, Higher limit (e.g. -0.36, -0.19):\n')
            limits = np.sort(eval(limits))
            E1 = limits[0]
            E2 = limits[1]
            E1n = E1
            E2n = E2
        except:
            E1 = -0.4; E2 = -0.22
        print('Your baseline: ' +str(E1)+' '+str(E2))
        input('Hit enter to continue')

###################Baseline Correction######################################
    peakcurrent=np.empty(numelecs)
    for h in range(numelecs):
        n=0
        while n<= numfreqs-1:
            #Index where potentials are between E1 and E2##
            peak= np.argwhere((E_array[n,h,f]>= E1)&(E_array[n,h,f]<=E2))
            gofor=1
            p=0
            cls()
            electro_title=("Electrode "+str(elec[h])+ " "+str(sqwvfreqs[n])+" Hz"+" point "+ str(titno[f]))
            electro_pic=("E"+str(elec[h])+ "_"+str(sqwvfreqs[n])+"Hz"+"__"+ str(titno[f]))
            print(electro_title)
            while gofor==1:
                if p==0: #automatic baseline selection
                    p=1
                    peak= np.argwhere((E_array[n,h,f]>= E1)&(E_array[n,h,f]<=E2))#E_array points within E1 and E2
                    nn=int(np.ceil(np.size(peak)/2)) #split in half
                    base1 = np.array(peak[0:nn]); base2 = np.array(peak[nn:])#Split E_array in two parts
                    y=I_array[n,h,f]
                    y_base1=y[int(base1[0]):int(base1[-1]+1)]#Currents in part 1
                    y_base2=y[int(base2[0]):int(base2[-1]+1)]#Currents in part 2
                    #Determine min and min coordinate in total data
                    min1=min(y_base1);min1_index=np.argwhere(y_base1==min1)[0]+base1[0]+1
                    min2=min(y_base2);min2_index=np.argwhere(y_base2==min2)[-1]+base2[0]+1
                    #Corresponding Potentials at peak
                    E_peak=np.array(E_array[n,h,f][int(min1_index):int(min2_index)+1])
                    poly_y1= np.mean(y[int(min1_index-WSZ):int(min1_index+WSZ)])
                    poly_y2= np.mean(y[int(min2_index-WSZ):int(min2_index+WSZ)])
                    basefit =np.polyfit([E_array[n,h,f][int(min1_index)],E_array[n,h,f][int(min2_index)]],[poly_y1, poly_y2],1);
                    baseline = np.polyval(basefit,E_peak)
                    y=y[int(min1_index):int(min2_index)+1]
                else:
                    #Keeps the parameters the same within the while loop after the first frequency
                    peak= np.argwhere((E_array[n,h,f]>= E1n)&(E_array[n,h,f]<=E2n))#E_array points within E1 and E2
                    y=I_array[n,h,f][int(peak[0]):int(peak[-1])]
                    E_peak=E_array[n,h,f][int(peak[0]):int(peak[-1])]
                    basefit =np.polyfit([E_peak[0],E_peak[-1]],[y[0], y[-1]],1)
                    baseline=np.polyval(basefit,E_peak)
                
                #############Visual Inspection time##################
                plt.figure(5)
                plt.figure(5). clear()
                plt.plot(E_array[n,h,f],I_array[n,h,f])
                plt.plot(E_peak,baseline)
                plt.title(electro_title)
                plt.xlabel(E_label);plt.ylabel(I_label)
                if autobase==0:
                    print('press x to close')
                    plt.show(block=False)
                    gofor=input("OK = y; NOT OK =n\n") or "y"
                else:
                    gofor="y"
                if autosavebase==1:
                    plt.savefig(electro_pic)
                #Removed going back function
                if gofor!='y':
                    try:
                        limits=input("Lower limit, Higher limit (e.g. -0.36, -0.19):\n" or "-0.36,-0.19")
                        limits = np.sort(eval(limits))
                        E1n=limits[0]
                        E2n=limits[1]
                    except:
                        print("Don't forget the comma in between")
                        input()
                    gofor=1 #keep in current loop
                else:
                    n=n+1
                    gofor=0
                plt.close(5)

            #Original had another try and catch loop. No second changes here. Sorry :V
            I_peak_array[h,n-1,f]=max(y-baseline)
            I_charge_array[f,h,n-1]=max(y-baseline)*10**-6/int(sqwvfreqs[n-1])
        
        ####KDM Calculation and Ratio Calculation#######
        np_index=int(norm_point-1)#normalization point
        if f==np_index:
            I_init[h]=I_peak_array[h,:,np_index]
            for i in range(norm_point):
                for k in range(numfreqs):
                    I_norm_array[h,k,i]=I_peak_array[h,k,i]/I_init[h,k]
                Diff[h,i]=(I_norm_array[h,KDM_hindex,i])-(I_norm_array[h,KDM_lindex,i])
                Avg[h,i]=0.5*(I_norm_array[h,KDM_hindex,i]+I_norm_array[h,KDM_lindex,i])
                KDM[h,i]=Diff[h,i]/Avg[h,i]
        elif f>np_index:
            for k in range(numfreqs):
                I_norm_array[h,k,f]=I_peak_array[h,k,f]/I_init[h,k]
            Diff[h,f]=I_norm_array[h,KDM_hindex,f]-I_norm_array[h,KDM_lindex,f]
            Avg[h,f]=0.5*(I_norm_array[h,KDM_hindex,f]+I_norm_array[h,KDM_lindex,f])
            KDM[h,f]=Diff[h,f]/Avg[h,f]
        Ratio[h,f]=I_peak_array[h,KDM_hindex,f]/I_peak_array[h,KDM_lindex,f]


#########Recording time of datafile########################################
    filename[f]=myfilename
    filetime=(datetime.fromtimestamp(os.path.getctime(myfilename)))#getctime is for created time, getmtime is for modified time
    if f==0:
        filetime0=filetime
    timediff=filetime-filetime0
    timedelta[f]=timediff.total_seconds() / 60.0

##########Plotting Real-time data at the end of each titration point
#####Plot KDM on frequencies in real time 
    if f>=np_index:
        plt.figure(3)
        plt.ylabel("KDM "+str(f_KDM_high)+"Hz-"+str(f_KDM_low)+"Hz")
        plt.xlabel(t_label)
        for h in range (numelecs):
            if f==np_index:
                for i in range(norm_point):
                    if i==0:
                        plt.scatter(float(timedelta[i]),float(KDM[h,i]),color=color_choice[h],label='E'+str(elec[h]))
                    else:
                        plt.scatter(float(timedelta[i]),float(KDM[h,i]),color=color_choice[h])
            else:
                plt.scatter(float(timedelta[f]),float(KDM[h,f]),color=color_choice[h])
                plt.legend(loc="upper left")
                plt.pause(0.00000001)
plt.savefig("KDM_"+str(f_KDM_high)+"Hz-"+str(f_KDM_low)+"Hz")
plt.show(block=False)

####Deletes the last datapoint because there is nothing there
if brk==1:
    timedelta=timedelta[:-1]
    I_norm_array=I_norm_array[:,:,:-1]
    I_charge_array=I_charge_array[:-1,:,:]
    titlength=int(titlength-1)

#######Plot Normalized Currents vs time not in real time
fig1,axs1=plt.subplots(numelecs, figsize=(12,12), sharex=True, squeeze=False)
plt.xlabel(t_label)
for h in range(numelecs):
    for k in range(numfreqs):
        axs1[h,0].plot(timedelta,I_norm_array[h,k],'o-',color=color_choice[k], label=str(sqwvfreqs[k])+'Hz')
    axs1[h,0].set_ylabel('E'+str(elec[h])+' '+In_label)
    axs1[h,0].legend(loc="lower left",ncol=5)

plt.show(block=False)
fname="NormI"+str(f_KDM_high)+"Hz-"+str(f_KDM_low)+"Hz.png"
plt.savefig(fname)

########Plot Charge vs Freq as time progresses not in real-time
fig3,axs3=plt.subplots(numelecs,sharex=True,constrained_layout=True, squeeze=False)
plt.xlabel(f_label)
for h in range(numelecs):
    for f in range(titlength):
        axs3[h,0].plot(sqwvfreqs,I_charge_array[f,h],'o-')
    axs3[h,0].set_ylabel(Ch_label)
    axs3[h,0].set_xscale('log')
    axs3[h,0].legend(['E'+str(elec[h])],loc="upper right")
plt.savefig("Charge_vs_Freq_Map")
plt.show(block=False)

######Saving Calculated Data in txt files###
####Textfile1. Time, KDM Freqs Raw Frequencies +Normalized
for h in range(numelecs):
    #t_vs_raw_I_file="E"+elec[h]+"_t_vs_Ipk_"+freqstring+"Hz.txt"
    t_vs_I_file="E"+str(elec[h])+"_t_vs_Ipk_"+str(KDM_Freqs[-1])+"Hz-"+str(KDM_Freqs[0])+"Hz.txt"
    textfile1=open(t_vs_I_file, "w")
    #Write header
    textfile1.write("Time(min)"+"\tKDM_no_avg\tKDM\tRatio"+"\tI"+str(sqwvfreqs[KDM_hindex])+"(A)"+"\t"+"I"+str(sqwvfreqs[KDM_lindex])+"(A)"+"\t"+"I_norm"+str(sqwvfreqs[KDM_hindex])+"\tI_norm_"+str(sqwvfreqs[KDM_lindex])+"\n")
    #I can't figure out how to put in all the frequencies in one file
    for f in range(titlength):
        textfile1.write(str(timedelta[f])+"\t"+str(Diff[h,f])+"\t"+str(KDM[h,f])+"\t"+str(Ratio[h,f])+"\t"+str(I_peak_array[h,KDM_lindex,f])+"\t"+str(I_peak_array[h,KDM_hindex,f])+"\t" +str(I_norm_array[h,KDM_lindex,f])+"\t"+str(I_norm_array[h,KDM_hindex,f])+ "\n")
    textfile1.close

####Textfile2. Charge vs Frequency 
freqstring='Hz_'.join([str(elem) for elem in sqwvfreqs])
freqheaderstr='\tCharge_'.join([str(elem) for elem in sqwvfreqs])

for h in range(numelecs):
    Ch_vs_Freq_file="E"+str(elec[h])+"Ch_vs_Freq"+freqstring+"Hz_.txt"
    textfile2=open(Ch_vs_Freq_file,"w")
    textfile2.write("Charge_"+freqheaderstr+"\n")
    textfile2.close
    with open(Ch_vs_Freq_file,"ab") as textfile2:
        for f in range (titlength):
            np.savetxt(textfile2,I_charge_array[f], delimiter="\t", newline="\n")
cls()
print("===============================================")
print("End of the program. All your data is saved now. Goodbye!")
print("===============================================")

