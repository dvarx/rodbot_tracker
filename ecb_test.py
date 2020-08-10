# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 06:37:55 2020

@author: dvarx
"""

from ECB import *
import sys
sys.path.append("./magnetic_computations")
from actuation_computer import actuationComputer
import numpy as np
from numpy.linalg import pinv

comp=actuationComputer(r"./calibration/minimag_calibration/mfg-100_00_meas_vfield_0%i.txt")
desB=np.array([0,0,5e-3])
desG=np.array([1,0,0])
A=comp.getA([0,0,0],[0,0,1])
ides=pinv(A).dot(np.concatenate((desB,desG)))
ides=list((ides*1000).astype(int))
ides=[0,0,0,0,5000,0,0,0]
     
initECBapi("192.168.237.47", "7070")
setDesCurrents(ides,b'1')
enableECBCurrents()
     
x=input("type some input")
     
disableECBCurrents()
     
exitECBapi()
