# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 13:05:55 2020

@author: dvarx
"""
import time, pygame, sys
from pygame.locals import *
import pygame
import numpy as np


def ps3_acquisition(send_end_ps3_axes,exit_event):
    """
    while True:
        print("x")
        time.sleep(1)
    """
    
    fp_ps3=open("logfile_ps3.txt","w");
    
    #init pygame and joystick
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    #only allow JOXAXISMOTION changed events
    pygame.event.set_allowed(pygame.JOYAXISMOTION)
    
    currentAct=(0,0)
    
    #we check every 20ms for a new JOYAXISMOTION event, if yes, we read
    # the current position and clear the event queue
    while not exit_event.is_set():
        #get current game events
        events=pygame.event.get()
        #fp_ps3.write("no events: %d\n"%(len(events)))

        for event in events:
            if event.type==pygame.JOYAXISMOTION:
                pygame.event.clear()
                #send first two joystick axes to parent process
                currentAct=np.array([joystick.get_axis(0),joystick.get_axis(1)])
                try:
                    send_end_ps3_axes.send(currentAct)
                except Exception as ex:
                    i+=1
        time.sleep(0.035)
    
    pygame.quit()
    sys.exit()
    fp_ps3.close()
