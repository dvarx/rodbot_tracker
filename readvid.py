import cv2
import numpy as np
from time import sleep


#upper-left corner of AOI
running_avg=np.array([300,180])
alpha=0.5
LOWER_THRES=100
AOI_LENGTH=50

cap = cv2.VideoCapture('test1.m4v')

def mouse_cb(event,x,y,flags,param):
    global running_avg
    if event==cv2.EVENT_LBUTTONDOWN:
        print("CLicked : (%d,%d)"%(x,y))
        running_avg=np.array([x,y])
    
cv2.namedWindow("viewing_window")
cv2.setMouseCallback('viewing_window',mouse_cb)

# Check if camera opened succeqssfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")


while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  sleep(0.2)
  if ret == True:
    #aoi = frame[int(running_avg[0]):int(running_avg[0])+AOI_LENGTH,int(running_avg[1]):int(running_avg[1])+AOI_LENGTH]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    appliedthresh,imgmask=cv2.threshold(gray,LOWER_THRES,255,cv2.THRESH_BINARY)
    imgmask=cv2.bitwise_not(imgmask)
    
    maskaoi=imgmask[int(running_avg[1]):int(running_avg[1])+AOI_LENGTH,int(running_avg[0]):int(running_avg[0])+AOI_LENGTH]
    moments=cv2.moments(maskaoi)
    if(moments["m00"]!=0):
        dpos=np.array([moments["m10"]/moments["m00"],moments["m01"]/moments["m00"]])
        center_position_abs=running_avg+dpos.T
        cv2.circle(frame,(int(center_position_abs[0]),int(center_position_abs[1])),color=(1,1,1),radius=5)
        running_avg=center_position_abs-np.array([AOI_LENGTH/2,AOI_LENGTH/2])
        #cv2.circle(frame,(int(running_avg[0]),int(running_avg[1])),color=(1,1,1),radius=5)

    
    #draw aoi
    frame=cv2.rectangle(frame,(int(running_avg[0]),int(running_avg[1])), \
                        (int(running_avg[0]+AOI_LENGTH),int(running_avg[1]+AOI_LENGTH)),color=(255,0,0))
    imgmask=cv2.rectangle(imgmask,(int(running_avg[0]),int(running_avg[1])), \
                        (int(running_avg[0]+AOI_LENGTH),int(running_avg[1]+AOI_LENGTH)),color=(255,255,255))
        
    imgmask_rgb=cv2.cvtColor(imgmask,cv2.COLOR_GRAY2RGB)
        
    #concatenate images and show
    concatimage=np.concatenate((frame,imgmask_rgb),axis=1)

    cv2.imshow('viewing_window',concatimage)
    
    #wait for input
    #x=input("Click Enter For Next Frame")

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else: 
    break



# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
