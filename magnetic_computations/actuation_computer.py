from init_constants import plotFileField
from calibration_postprocessing import kernelAveraging
import numpy as np
from numpy.linalg import pinv,norm
import matplotlib.pyplot as plt
from init_constants import plotField

#kernel averaging
smoothingField=False
smoothingGradient=False

"""
-This script should be used in conjunction with calib_definitions.py

-This script computes actuation matrices from calibration files. The files should contain N*N*N values,
the order of the position vectors should not play a role

-The end of this script contains code to compute the currents required to
generate a field B and a (projected) gradient gradB. The code also generates a
quiver plot to show the resulting field distribution in the magnetic work space

Inputs:    
    calibrationFileString       string describing the format of the names of the calibration files
    limits                      the limits of the magnetic working space ((xmin,xmax),(ymin,ymax),(zmin,zmax)) [mm]
    plotExampleWorkspace        if this is set to True, the code at the end of the script which plots the field in the entire workspace
                                for a certain desired (field,gradient) combination is executed
"""

class actuationComputer:
    def __init__(self,calibrationFileString):
        self.calibMatrices=[]
        self.limits=[]
        self.plotExampleWorkspace=True
        self.calibrationFileString=calibrationFileString

        for i in range(0,8):
            (self.mat,self.dims,self.limits)=plotFileField(filename=self.calibrationFileString%(i),loadFlag=True,storeLoc=True)
            self.calibMatrices.append(self.mat)

        self.dims=[int(x) for x in self.dims]
        self.deltas=[(self.limits[i][1]-self.limits[i][0])/(self.dims[i]-1) for i in range(0,3)]
        self.N=self.dims[0]*self.dims[1]*self.dims[2]

        #some helper functions to convert integer indices and real coordinates
        self.toIndex=lambda r:[int(round((r[i]-self.limits[i][0])/self.deltas[i])) for i in range(0,3)]
        self.toLowestIndex=lambda r:[int((r[i]-self.limits[i][0])/self.deltas[i]) for i in range(0,3)]
        self.toPosition=lambda index:[self.limits[i][0]+index[i]*self.deltas[i] for i in range(0,3)]
        self.toLinearIndex=lambda cubeindex:cubeindex[0]*self.dims[2]*self.dims[1]+cubeindex[1]*self.dims[2]+cubeindex[2]
    
        #index usage: shapeCube[coiln][i][j][k]
        self.shapeCubesRaw=[np.zeros((self.dims[0],self.dims[1],self.dims[2],3)) for i in range(0,8)]

        for cuben in range(0,8):
            for i in range(0,self.N):
                calibMatrix=self.calibMatrices[cuben]
                index=self.toIndex(calibMatrix[i][3:6])
                #print("location "+str(calibMatrix[i][3:6]))
                #print("index "+str(index))
                self.shapeCubesRaw[cuben][index[0]][index[1]][index[2]][:]=calibMatrix[i][0:3]
    
        self.shapeCubes=kernelAveraging(self.shapeCubesRaw) if smoothingField else self.shapeCubesRaw 
   
        #compute the derivative actuation matrices dB/dx,dB/dy,dB/dz
        #units T/m
        #indices of shapeCubesDer: shapeCubesDer[dervn][coiln][i][j][k]
        self.shapeCubesDerRaw=[[np.zeros((self.dims[0],self.dims[1],self.dims[2],3)) for coiln in range(0,8)] for dervn in range(0,3)]
        for coiln in range(0,8):
            for dervn in range(0,3):
                deltaIndex=np.zeros(3)
                deltaIndex[dervn]=1
                for i in range(0,self.dims[0]):
                    for j in range(0,self.dims[1]):
                        for k in range(0,self.dims[2]):
                            index=np.array([i,j,k])
                            indexp=index+deltaIndex
                            indexm=index-deltaIndex
                            index=tuple(index.astype(int))
                            indexp=tuple(indexp.astype(int))
                            indexm=tuple(indexm.astype(int))
                            #if on a face of the cube, use the one-sided difference quotient
                            if(index[dervn]==0):
                                self.shapeCubesDerRaw[dervn][coiln][index]=(self.shapeCubes[coiln][indexp]-self.shapeCubes[coiln][index])/self.deltas[dervn]
                            elif (index[dervn]==self.dims[dervn]-1):
                                self.shapeCubesDerRaw[dervn][coiln][index]=(self.shapeCubes[coiln][index]-self.shapeCubes[coiln][indexm])/self.deltas[dervn]
                            else:
                               self.shapeCubesDerRaw[dervn][coiln][index]=(self.shapeCubes[coiln][indexp]-self.shapeCubes[coiln][indexm])/(2*self.deltas[dervn])

        if not smoothingGradient:
            self.shapeCubesDer=self.shapeCubesDerRaw
        else:  
            self.shapeCubesDer=[] 
            for dervn in range(0,3):
                self.shapeCubesDer.append(kernelAveraging(self.shapeCubesDerRaw[dervn]))

    #use this function to get the interpolated actuation matrix A in R^(3,8) at position r from a list of shapefield cubes     
    def interpolateCubes(self,CubeList,r):
        #check if r is within limits, if not raise error
        limitError=False
        for i in range(0,3):
            limitError = limitError or (r[i]<self.limits[i][0])
            limitError = limitError or (r[i]>self.limits[i][1])
        if limitError:
            raise Exception("PositionOutOfBounds Error: The positional vector r passed to the Interpolation routine is out of the calibration space")
        A=np.zeros((3,8))
        lowestIndex=self.toLowestIndex(r)
        x=lowestIndex[0]
        y=lowestIndex[1]
        z=lowestIndex[2]
        #compute the indices of the neighbors
        indices=[(x,y,z),(x+1,y,z),(x+1,y+1,z),(x,y+1,z),(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)]
        for i in range(0,8):
            relX=(r[0]-(self.limits[0][0]+self.deltas[0]*x))/self.deltas[0]
            relY=(r[1]-(self.limits[1][0]+self.deltas[1]*y))/self.deltas[1]
            relZ=(r[2]-(self.limits[2][0]+self.deltas[2]*z))/self.deltas[2]
            #compute the trilinear interpolation
            c03=(1-relY)*CubeList[i][indices[0]]+relY*CubeList[i][indices[3]]
            c12=(1-relY)*CubeList[i][indices[1]]+relY*CubeList[i][indices[2]]
            c56=(1-relY)*CubeList[i][indices[5]]+relY*CubeList[i][indices[6]]
            c47=(1-relY)*CubeList[i][indices[4]]+relY*CubeList[i][indices[7]]
            c0312=(1-relX)*c03+relX*c12
            c5647=(1-relX)*c47+relX*c56
            A[:,i]=(1-relZ)*c0312+relZ*c5647
        return A

    def getB(self,r):
        return self.interpolateCubes(self.shapeCubes,r)
        
    def getBx(self,r):
        return self.interpolateCubes(self.shapeCubesDer[0],r)
        
    def getBy(self,r):
        return self.interpolateCubes(self.shapeCubesDer[1],r)
        
    def getBz(self,r):
        return self.interpolateCubes(self.shapeCubesDer[2],r)

    #computes the actuation matrix at position r associated with the magnetiztation m
    def getA(self,r,m):
        if(not type(m)==np.ndarray and m!=None):
            m=np.array(m)
        matB=self.getB(r)
        Bx=self.getBx(r)
        By=self.getBy(r)
        Bz=self.getBz(r)
        if type(m)==type(None):
            A=np.concatenate((matB,Bx,By,Bz),axis=0)
        else:
            matBx=m.dot(Bx).reshape(1,8)
            matBy=m.dot(By).reshape(1,8)
            matBz=m.dot(Bz).reshape(1,8)
            A=np.concatenate((matB,matBx,matBy,matBz),axis=0)
        return A

    def getAalt(self,r,m):
        delta=1e-6
        m=np.array(m)
        r=np.array(r)
        matB=self.getB(r)
        Bx=(self.getB(r+np.array([delta,0,0]))-self.getB(r+np.array([-delta,0,0])))/(2*delta)
        By=(self.getB(r+np.array([0,delta,0]))-self.getB(r+np.array([0,-delta,0])))/(2*delta)
        Bz=(self.getB(r+np.array([0,0,delta]))-self.getB(r+np.array([0,0,-delta])))/(2*delta)
        if m.size<3:
            A=np.concatenate((matB,Bx,By,Bz),axis=0)
        else:
            A=np.concatenate((matB,m.dot(Bx).reshape(1,8),m.dot(By).reshape(1,8),m.dot(Bz).reshape(1,8)),axis=0)
        return A


"""
Plot field in workspace for a certain desired (field,gradient) combination
"""
if __name__=="__main__":
    calibrationFileString=r"../calibration/minimag_calibration/mfg-100_00_meas_vfield_0%i.txt"
    act_computer=actuationComputer(calibrationFileString)
    desB=np.array([5e-3,0,0])   #in [mT]
    desG=np.array([1,0,0])      #in [mT/mm]
    
    A=act_computer.getA([0,0,0],[1,0,0])
    i=np.linalg.pinv(A).dot(np.concatenate((desB,desG),0))
    
    print("%-40s%s"%("Desired Magnetic Flux 'B':",str(desB)))
    print("%-40s%s"%("Desired Magnetic Flux Gradient 'G':",str(desG)))
    print("%-40s%s"%("Necessary Currents 'i':",str(i)))