"""
This script is used to post-process the calibration fiel data received from either a FEM simulation
or measurements with the Metrolab sensor
"""

import numpy as np
from scipy import ndimage

#indices of shapeCubesDer: shapeCubesDer[coiln][dervn][i][j][k]
#index usageof shapeCube: shapeCube[coiln][i][j][k]
#shapeCubes=[]

width=3                       #number of averaging layers around point
weight = lambda r : 1/r
centerweight = 1/3            #relative weight of the center point

kernel=np.zeros((1+2*width,1+2*width,1+2*width))
weightsum=0                     #we keep track of the sum of weight in order to normalize later

for x in range(0,2*width+1):
    for y in range(0,2*width+1):
        for z in range(0,2*width+1):
            (symx,symy,symz)=(x-width,y-width,z-width) #symmetric indices, the center point has symmetric index (0,0,0)
            if(symx==0 and symy==0 and symz==0):
                print("(%d,%d,%d"%(x,y,z))
                continue
            layern=max([abs(ind) for ind in (symx,symy,symz)]) #determine the layer of the current node
            currentweight=weight(layern) #weighting factor for the current node, depends only on the distance from the center
            kernel[x,y,z]=currentweight
            weightsum+=currentweight
kernel=(kernel/weightsum)*(1-centerweight)
kernel[width,width,width]=centerweight

def kernelAveraging(shapeCubes):
    shapeCubesNew=[]
    for cuben in range(0,8):
        componentCubes=[shapeCubes[cuben][:,:,:,i] for i in range(0,3)] #this contains cubes of the components of the fields (e.g. B[0],B[1],B[2])
        componentCubesConvd=[ndimage.convolve(componentCubes[i], kernel, mode='nearest') for i in range(0,3)] #convolute each component cube seperately
        #assemble the convoluted component cube to a vectorial cube
        convdCube=np.zeros(shapeCubes[0].shape)
        for i in range(0,3):
            convdCube[:,:,:,i]=componentCubesConvd[i]
        shapeCubesNew.append(convdCube)
    return shapeCubesNew

def simpleAveraging(shapeCubes):
    dims=shapeCubes[0].shape[0:3]
    print(dims)
    shapeCubesNew=[]
    for i in range(0,8):
        shapeCubesNew.append(np.zeros(shapeCubes[0].shape))
    #compute average for all inner points
    for cuben in range(0,len(shapeCubes)):
        for x in range(1,dims[0]-1):
            for y in range(1,dims[1]-1):
                for z in range(1,dims[2]-1):
                    #shapeCubesNew[cuben][x,y,z]=np.ones((3))
                    shapeCubesNew[cuben][x,y,z]=(1/3*shapeCubes[cuben][x,y,z]+1/(3*6)*(   shapeCubes[cuben][x+1,y,z]
                                                                                    +shapeCubes[cuben][x-1,y,z]
                                                                                    +shapeCubes[cuben][x,y+1,z]
                                                                                    +shapeCubes[cuben][x,y-1,z]
                                                                                    +shapeCubes[cuben][x,y,z+1]
                                                                                    +shapeCubes[cuben][x,y,z-1]))
    return shapeCubesNew