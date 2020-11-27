"""
Created on Thu Jul 23 17:00:57 2020

How to use:
    Click on a dark object to reset the AOI (=area of interest) center position in the left image (grayscale)

@author: dvarx
"""

"""
Initialize logging
"""
import logging
global logging_level
logging_level=logging.DEBUG
logging.basicConfig(filename='basictracker.log',level=logging.DEBUG)

"""
Launch PyQt5 GUI process
"""
#imports for GUI
#FIXME : for some reason PyQt5 GUI has to be launched at the beginning otherwise GUI window will not appear
from time import sleep
import multiprocessing as mp
from basic_gui import main_loop

#define the exit event
global exit_event
exit_event=mp.Event()
(recv_end_thres,send_end_thres)=mp.Pipe()
proc_gui=mp.Process(target=main_loop,args=[send_end_thres,exit_event,logging_level])
sleep(1)
proc_gui.start()

"""
set up opencv and main loop
"""

#imports for main loop and opencv
import cv2
from pypylon import pylon
import numpy as np
#from ps3acquisition import ps3_acquisition
from numpy.linalg import norm,pinv
from ECB import *
import sys
sys.path.append("./magnetic_computations")
from actuation_computer import actuationComputer

if __name__=="__main__":
  """
  Global Definitions
  """
  use_camera=False
  roi_upperleft_pos=np.array([300,180])
  act_axes=np.array([0,0])
  alpha=0.5
  LOWER_THRES=100
  AOI_LENGTH=50
  loop_video=True
  center_act_disp=np.array([35,35])
  act_disp_window_halfsize=20
  act_disp_upperleft=center_act_disp-20*np.array([1,1])
  act_disp_lowerright=center_act_disp+20*np.array([1,1])
  maxG=1
  Gz=0
  global cap                    #global variable used when reading from movie file
  global grabResult             #global variable used when using the camera

  """
  Initialization Code
  """

  #mouse callback function, we need it to reset the running_avf when the user clicks the screen
  def mouse_cb(event,x,y,flags,param):
      global roi_upperleft_pos
      if event==cv2.EVENT_LBUTTONDOWN:
          logging.debug("Clicked : (%d,%d)"%(x,y))
          roi_upperleft_pos=np.array([max(0,x-LOWER_THRES/2),max(0,y-LOWER_THRES/2)])

  #initilize actuation computer (magnetic field math)
  comp=actuationComputer(r"./calibration/minimag_calibration/mfg-100_00_meas_vfield_0%i.txt")
  desB=np.array([0,0,1e-3])
  desG=np.array([1,0,0])
  A=comp.getA([0,0,0],[0,0,1])
  ides=np.linalg.pinv(A).dot(np.concatenate((desB,desG)))
  
  #define pipes and events for communication with PS3 controller process
  #(recv_end_ps3_axes,send_end_ps3_axes)=mp.Pipe()
  #proc_ps3=mp.Process(target=ps3_acquisition,args=[send_end_ps3_axes,exit_event])
  #sleep(1)
  #proc_ps3.start()

  #define named window for mouse cb
  cv2.namedWindow("viewing_window")
  cv2.setMouseCallback('viewing_window',mouse_cb)

  #use either camera input or video from file
  if use_camera:
    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
    converter = pylon.ImageFormatConverter()
    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    def acquire_frame():
        #grab frame from camera
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            frame = image.GetArray()
            return (True,frame)
  else:
    cap = cv2.VideoCapture('test_video.m4v')
    if (cap.isOpened()== False):
          logging.error("could not open test video")
    def acquire_frame():
        ret, frame = cap.read()
        return (True,frame)
          

  """
  Main Program Loop
  """
  while(True):
    #print("status of qt process: %s\n"%(str(proc_gui.is_alive())))
    #print("status of ps3 process: %s\n"%(str(proc_ps3.is_alive())))
    #if(len(mp.active_children())<2):
    #    print("active children %s\n"%(str(mp.active_children())))

    #receive actuation from PS3 controller
    #if recv_end_ps3_axes.poll():
    #    act_axes=recv_end_ps3_axes.recv()
        
    #open loop joystick actuation
    desG=maxG*act_axes
    desG=np.concatenate((desG,np.array([0])))
    A=A=comp.getA([0,0,0],desB/norm(desB))
    ides=pinv(A).dot(np.concatenate((desB,desG)))

    #check if threshold has been adjusted in GUI
    if recv_end_thres.poll():
      LOWER_THRES=recv_end_thres.recv()

    #acquire frame
    (frame_acq_succesful,frame)=acquire_frame()

    if frame_acq_succesful:
      #resize image if necessary
      frame=cv2.resize(frame,(int(frame.shape[1]),int(frame.shape[0])))

      #apply threshold and mask
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      appliedthresh,imgmask=cv2.threshold(gray,LOWER_THRES,255,cv2.THRESH_BINARY)
      imgmask=cv2.bitwise_not(imgmask)
      
      #update center of mass and aoi position
      maskaoi=imgmask[int(roi_upperleft_pos[1]):int(roi_upperleft_pos[1])+AOI_LENGTH,int(roi_upperleft_pos[0]):int(roi_upperleft_pos[0])+AOI_LENGTH]
      moments=cv2.moments(maskaoi)
      if(moments["m00"]!=0):
          dpos=np.array([moments["m10"]/moments["m00"],moments["m01"]/moments["m00"]])
          center_position_abs=roi_upperleft_pos+dpos.T
          cv2.circle(frame,(int(center_position_abs[0]),int(center_position_abs[1])),color=(1,1,1),radius=5)
          roi_upperleft_pos=center_position_abs-np.array([AOI_LENGTH/2,AOI_LENGTH/2])

      
      #draw aoi
      frame=cv2.rectangle(frame,(int(roi_upperleft_pos[0]),int(roi_upperleft_pos[1])), \
                          (int(roi_upperleft_pos[0]+AOI_LENGTH),int(roi_upperleft_pos[1]+AOI_LENGTH)),color=(0,0,255))
          
      imgmask_rgb=cv2.cvtColor(imgmask,cv2.COLOR_GRAY2RGB)
      
      imgmask_rgb=cv2.rectangle(imgmask_rgb,(int(roi_upperleft_pos[0]),int(roi_upperleft_pos[1])), \
                      (int(roi_upperleft_pos[0]+AOI_LENGTH),int(roi_upperleft_pos[1]+AOI_LENGTH)),color=(0,0,255))
          
      #draw actuation
      frame=cv2.rectangle(frame,tuple(act_disp_upperleft),tuple(act_disp_lowerright),[1,0,0])
      p1=center_act_disp
      p2=center_act_disp+(act_axes)*act_disp_window_halfsize
      frame=cv2.line(frame,tuple(p1.astype(int)),tuple(p2.astype(int)),[1,0,0])
          
      #concatenate images and show
      concatimage=np.concatenate((frame,imgmask_rgb),axis=1)

      cv2.imshow('viewing_window',concatimage)

      #press Q on keyboard to  exit
      if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    # Break the loop
    else: 
      logging.error("failed to acquire frame")
      break


  """
  Exit Program
  """
  
  # Set the exit_event such that child process will terminate
  exit_event.set()
  sleep(0.5)

  # Closes all the frames
  cv2.destroyAllWindows()
  
  if use_camera:
    grabResult.Release()
    camera.close()
  
  sys.exit()