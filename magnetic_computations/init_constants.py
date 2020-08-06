#this file defines global data constants and should be run first
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import random
from math import sqrt
import sys
from mayavi.mlab import quiver3d

#cube version
cubeNumber=2    #or 1...

#parameters for cube calibrationsompareFields(0)
testcurrent_mA=5000     #testcurrent to be applied in each coil
spacer_thickness=3.65   #distance between PCBs
board_thickness=1.16    #PCB thickness
deltaCoordZ=spacer_thickness+board_thickness+3 #describes the z-Coordinate difference between cube coordinate system and mbx coordinate system
delta=5.0               #distance between two sensor (5mm)
n_coils=8               #number of coils in system
sysname="mfg-100"       #name of the magnetic field generator system
sensorDim=(4,4,4)       #describes the number of sensors in the cube (#x,#y,#z)

#parameters for plotting
vecplot_linewidth=1
vecplot_length=1
plotcolor="red"
plotNew=True

#workspace dimensions (in m)
xlim=(-7.5e-3,7.5e-3)
ylim=(-7.5e-3,7.5e-3)
zlim=(-6.65e-3,7.78e-3)
mbx_orientation=False

#parameters for data acquisition
rootDir="/home/magnebotix/Desktop/calibration_cube/"
cyclenumber=64                                  #sets the number of calibration measurments which are done
dataStorageLocation="log/new_cube/"    #sets the location where the measured data is stored
dataLocation=dataStorageLocation
calibration_folder=os.getcwd()+"/"+dataLocation+"calibration_files"
data_directory=rootDir+dataLocation
cube_baudrate=3000000
if "dataMatrices" not in globals():
    print("setting dataMatrices to empty")
    dataMatrices=[]

#parameters for analysis
sensorNumber=64                          #number of sensors, was previously a double !!!!!!!!!!!!!!!!!!!1
dataLocation="/"+dataStorageLocation       #location of the measurement data
baudrateStr="\nBR=19200"
if(dataLocation[-1]=="n"):
    baudrateStr="\nBR=19200"
    
#plotting parameters
maxDeviationScale=50.0
maxMeanScale=200
autoScale=True
if "figCounter" not in locals():
    figCounter=0

#returns position of sensor in MBX coordinate system K
def getGeometricalLocation(i):
    global spacer_thickness, board_thickness
    global mbx_orientation
    boardNum=int(i/16)+1    #number of the PCB with the sensor {1,2,3,4}
    sensorNum=i%16          #sensor number modulo 16 {0,...,15}
    
    boardNum=5-boardNum     #use this line if board #1 is on top  
    
    zPos=boardNum*board_thickness+(boardNum-1)*spacer_thickness #height of the sensor above ground
    xPos=(-1.5+(sensorNum%4))*delta
    yPos=(1.5-int(sensorNum/4))*delta
    
    xPos_mbx=yPos
    yPos_mbx=-xPos
    
    if mbx_orientation:
        return np.array([xPos_mbx,yPos_mbx,zPos])
    else:
        return np.array([xPos,yPos,zPos])

#transforms a field vector from the cube coordinate system K* to the mbx coordinate system K
#dimensions in mm
def cubedirtombxdir(cubePos):
    return np.array([-cubePos[1],cubePos[0],cubePos[2]])

#loads the measurement data located in data_directory into a list of matrices
#returns list of files that were read
def loadDataMatrices(datadir=data_directory,loadAgain=False):
    global dataMatrices
    if not(loadAgain) and len(dataMatrices)!=0:
        return []
    files=[f for f in os.listdir(datadir) if os.path.isfile(os.path.join(datadir,f)) and f[-3:]=="csv" and f!="measurementdata.csv"]
    files.sort()
    counter=0
    for f in files:
        current_file=os.path.join(datadir,f)
        current_pandaframe=pd.read_csv(current_file,sep=",")
        print("loading dataframe #"+str(counter))
        data_matrix=current_pandaframe.values[:,1:4]
        dataMatrices.append(data_matrix)
        counter+=1
    return files
    
#plots the cube field in the mbx coordinate system K
def plotCubeField(field):
    global plotcolor
    fig = plt.figure(random.randint(1,1000))
    ax = fig.add_subplot(111,projection='3d')
    Bx,By,Bz=field[:,0],field[:,1],field[:,2]
    locations=[np.array(getGeometricalLocation(i)) for i in range(0,64)]
  #  locations=[np.array(getGeometricalLocation(i))+np.array([0,0,-8]) for i in range(0,64)]
#    for i in range(0,len(locations)):
#        loc=locations[i]
#        ax.scatter(loc[0],loc[1],loc[2],color="blue",alpha=0.25)
#        ax.text(loc[0],loc[1],loc[2],str(i),alpha=0.25)
    
    ax.quiver(xSensorPositions, ySensorPositions, zSensorPositions, Bx, By, Bz, length=vecplot_length ,color=plotcolor,linewidths=vecplot_linewidth)
    ax.quiver([0,0,0],[0,0,0],[0,0,0],[1.5,0,0],[0,1.5,0],[0,0,1.5], length=2, color="red", pivot="tail")
    ax.text(2,0,0,"x")
    ax.text(0,2,0,"y")
    ax.text(0,0,2,"z")
    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)
    ax.set_ylim(-7,10)
    plt.show()
    plt.title("Field Plot in MBX Coordinate System K")
    
#plots the field from a file in the mbx coordinate system K
def plotField(x,y,z,Bx,By,Bz,plotcolor="blue",ax=0,scaleFactor=1,limits=None):
#    if limits==None:
#        limits=((min(x),max(x)),(min(y),max(y)),(min(z),max(z)))
#    ax.quiver(x, y, z, Bx*scaleFactor, By*scaleFactor, Bz*scaleFactor, color=plotcolor,linewidths=vecplot_linewidth,length=vecplot_length)
#    ax.quiver([0,0,0],[0,0,0],[0,0,0],[max(x)/5,0,0],[0,max(y)/5,0],[0,0,max(z)/5], length=2, color="red", pivot="tail")
#    ax.text(max(x)/5,0,0,"x")
#    ax.text(0,max(y)/5,0,"y")
#    ax.text(0,0,max(z)/5,"z")
#    ax.set_xlim(limits[0])
#    ax.set_ylim(limits[1])
#    ax.set_zlim(limits[2])
#    plt.title("Dimensions: [m],[mA/mm] | ScaleFactor=%f"%scaleFactor)
#    plt.show()
    quiver3d(x, y, z, Bx,By,Bz, line_width=2, scale_factor=scaleFactor)
    
#plt.title("Field Plot in MBX Coordinate System K")
    
def plotFieldNarr(pos,field,color="blue",axis=0,scaleFactor=1):
    plotField(pos[0,:],pos[1,:],pos[2,:],field[0,:],field[1,:],field[2,:],color,axis,scaleFactor)
    
def compareFields():
    global plotNew
    plotNew=False
    exec(open("plotFileField").read())
    plotNew=True
    exec(open("plotFileField").read())
    
xSensorPositions=[]
ySensorPositions=[]
zSensorPositions=[]
for i in range(0,64):
    pos=getGeometricalLocation(i)
    xSensorPositions.append(pos[0])
    ySensorPositions.append(pos[1])
    zSensorPositions.append(pos[2]-deltaCoordZ)
    
def compareFields(coilnum):
    fig=plt.figure(random.randint(1,1000))
    ax = fig.add_subplot(111,projection='3d')
    plotFileField(False,coilnum,ax)
    plotFileField(True,coilnum,ax)

#returns positions and fieldvalues in two numpy arrays
#positions,fieldvalues=loadCalibrationFile(filename)
def loadCalibrationFile(filename):
    if(not os.path.isfile(filename)):
        print("Invalid Filename.\n")
        return 0
    fptr=open(filename)
    data=[[],[],[],[],[],[]]
    #for i in range(0,5):#!!!!!!!!!!!!!!!!!!!!!!!!!
    for i in range(0,1):
        fptr.readline()
    for line in fptr:
        linecontents=line.split(",")#!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for j in range(0,6):
            data[j].append(float(linecontents[j]))
    fptr.close()
    positions=np.array([data[0],data[1],data[2]])
    fieldvalues=np.array([data[3],data[4],data[5]])
    #sortedpos,sortedfield=sortMeasurement(positions,fieldvalues)
    return positions,fieldvalues
    #return sortedpos,sortedfield#!!!!!!!!!!!!!!!!!!!!!!!!!!
    
def sortMeasurement(pos,field):
    sortedpos,sortedfield=np.zeros(pos.shape),np.zeros(field.shape)
    for i in range(0,pos.shape[1]):
        x,y,z=xSensorPositions[i],ySensorPositions[i],zSensorPositions[i]
        for j in range(0,pos.shape[1]):
            if(abs(x*1e-3-pos[0,j])<1e-4 and abs(y*1e-3-pos[1,j])<1e-4 and abs(z*1e-3-pos[2,j])<1e-4):
                sortedpos[:,i]=pos[:,j]
                sortedfield[:,i]=field[:,j]
                break
    return sortedpos,sortedfield
        
    
def plotFileField(filename="/home/magnebotix/Desktop/calibration_cube/new/calibrationFile0.txt",axis=0,modValue=1,nplotcolor="blue",pltnum=0,lenUnit="m",fieldUnit="mT/mA",_scaleFactor=1,loadFlag=False,storeLoc=False):
    #/home/magnebotix/Desktop/calibration_cube/log/fulltest/calibration_files/mfg-100_coil_00
    #/home/magnebotix/Desktop/calibration_cube/metrolab_meas/calibrationFile0.txt
    try:
        fptr=open(filename,"r")
    except Exception as ex:
        print(ex)
        return
    counter=0
    counter_skip=0
    xs,ys,zs=[],[],[]
    Bx,By,Bz=[],[],[]
    facLen={"m":1,"mm":1e3,"um":1e6}
    facField={"mT/mA":1,"mT/A":1e-3}
    for line in fptr:
        #read the dimensions from the 2nd line
        if counter==1:
            contents=line.split(" ")
            dims=[float(dat) for dat in contents]
        #discard the first 5 lines
        if counter<5:
            counter+=1
            continue
        else:
            if counter_skip==0:
                datastr=line.split(" ") #!!!!!!!!!!!!!!!!!
                data=[float(x) for x in datastr]
                #plot dimensions in [mm]
                xs.append(data[0]*facLen[lenUnit])
                ys.append(data[1]*facLen[lenUnit])
                zs.append(data[2]*facLen[lenUnit])
                #the dimension of the field shape values is given by [mT/A]
                Bx.append(data[3]*facField[fieldUnit])
                By.append(data[4]*facField[fieldUnit])
                Bz.append(data[5]*facField[fieldUnit])
            counter_skip+=1
            counter+=1
            counter_skip%=modValue
    
    fptr.close()
    
    if loadFlag:
        limits=[(min(xs),max(xs)),(min(ys),max(ys)),(min(zs),max(zs))]
        if(not storeLoc):
            matrix=np.zeros((counter-5,3))
        else:
            matrix=np.zeros((counter-5,6))
        for i in range(0,counter-5):
            matrix[i][0]=Bx[i]
            matrix[i][1]=By[i]
            matrix[i][2]=Bz[i]
            if(storeLoc):
                matrix[i][3]=xs[i]
                matrix[i][4]=ys[i]
                matrix[i][5]=zs[i]
        return (matrix,dims,limits)

    #fig=plt.figure(random.randint(1,1000))
    #axis = fig.add_subplot(111,projection='3d')

    _limits=((min(xs),max(xs)),(min(ys),max(ys)),(min(zs),max(zs)))         
    
    plotField(xs,ys,zs,np.array(Bx),np.array(By),np.array(Bz),plotcolor="blue",ax=axis,scaleFactor=_scaleFactor,limits=_limits)