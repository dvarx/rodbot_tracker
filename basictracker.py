import cv2
from pypylon import pylon
import numpy as np
from time import sleep
import multiprocessing as mp
from basic_gui import main_loop

"""
Created on Thu Jul 23 17:00:57 2020

How to use:
    Click on a dark object to reset the AOI (=area of interest) center position in the left image (grayscale)

@author: dvarx
"""
if __name__=="__main__":
  """
  Global Definitions
  """
  roi_upperleft_pos=np.array([300,180])
  alpha=0.5
  LOWER_THRES=100
  AOI_LENGTH=50
  loop_video=True

  """
  Initialization Code
  """
  cap = cv2.VideoCapture('test1.m4v')

  #mouse callback function, we need it to reset the running_avf when the user clicks the screen
  def mouse_cb(event,x,y,flags,param):
      global roi_upperleft_pos
      if event==cv2.EVENT_LBUTTONDOWN:
          print("CLicked : (%d,%d)"%(x,y))
          roi_upperleft_pos=np.array([max(0,x-LOWER_THRES/2),max(0,y-LOWER_THRES/2)])

  #define pipes for communication with GUI process
  (recv_end_thres,send_end_thres)=mp.Pipe()
  proc_gui=mp.Process(target=main_loop,args=[send_end_thres])
  sleep(1)
  proc_gui.start()

  #define named window for mouse cb
  cv2.namedWindow("viewing_window")
  cv2.setMouseCallback('viewing_window',mouse_cb)

  # conecting to the first available camera
  camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
  # Grabing Continusely (video) with minimal delay
  camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
  converter = pylon.ImageFormatConverter()
  # converting to opencv bgr format
  converter.OutputPixelFormat = pylon.PixelType_BGR8packed
  converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

  """
  Main Program Loop
  """
  while(cap.isOpened()):
    #grab frame from camera
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    #check if threshold has been adjusted in GUI
    if recv_end_thres.poll():
      LOWER_THRES=recv_end_thres.recv()

    if grabResult.GrabSucceeded():
      #access image data
      image = converter.Convert(grabResult)
      frame = image.GetArray()

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
          
      #concatenate images and show
      concatimage=np.concatenate((frame,imgmask_rgb),axis=1)

      cv2.imshow('viewing_window',concatimage)

      # Press Q on keyboard to  exit
      if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    # Break the loop
    else: 
      break


  """
  Exit Program
  """
  # When everything done, release the video capture object
  cap.release()

  # Closes all the frames
  cv2.destroyAllWindows()
