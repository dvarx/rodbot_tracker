# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:21:39 2020

@author: dvarx
"""

from PyQt5.QtWidgets import QApplication,QLabel,QWidget,QVBoxLayout,QPushButton,QHBoxLayout,QSlider,QMainWindow
from PyQt5.QtCore import Qt,QTimer
import multiprocessing as mp
import logging
import sys

"""
Global Variables
"""
send_end_thres=0

class MainWindow(QMainWindow):
    def check_exit_event(self):
        logging.debug("checked exit event")
        if self.exit_event.is_set():
            logging.debug("exit event received")
            self.close()

    def __init__(self,send_end_thres_,exit_event_,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)

        self.send_end_thres=send_end_thres_
        self.exit_event=exit_event_

        self.setWindowTitle("Control")
        self.layout=QVBoxLayout()

        self.toplayout=QHBoxLayout()
        self.bottomlayout=QHBoxLayout()

        try:
            self.topbutton=QPushButton("Top")
        except Exception as e:
            logging.error("Error: %s"%str(e))
        self.toplabel=QLabel("Top-Button: ")
        self.toplayout.addWidget(self.toplabel)
        self.toplayout.addWidget(self.topbutton)

        self.bottombutton=QPushButton("Bottom")
        self.bottomlabel=QLabel("Bottom-Button: ")
        self.bottomlayout.addWidget(self.bottomlabel)
        self.bottomlayout.addWidget(self.bottombutton)


        self.sliderlabel=QLabel("Current Value:%-3d"%(100))
        self.slider=QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.slider_val_chgd)
        self.sliderlayout=QVBoxLayout()
        self.sliderlayout.addWidget(self.slider)
        self.sliderlayout.addWidget(self.sliderlabel)

        self.topbutton.clicked.connect(self.top_btn_cb)

        self.layout.addLayout(self.toplayout)
        self.layout.addLayout(self.bottomlayout)
        self.layout.addLayout(self.sliderlayout)

        self.mainwidget=QWidget()
        self.mainwidget.setLayout(self.layout)
        self.resize(500,250)
        self.setCentralWidget(self.mainwidget)

        self.exit_timer=QTimer()
        self.exit_timer.timeout.connect(self.check_exit_event)
        self.exit_timer.start(1000)

    def top_btn_cb(self):
        self.topbutton.setText("Clicked Top")

    def slider_val_chgd(self,val):
        self.sliderlabel.setText("Value changed:%-3d"%(val))
        #self.send_end_thres.send(val)

    def set_send_pipe(self,send_end_thres_):
        print("x")
        #self.send_end_thres=send_end_thres_



def main_loop(send_end_thres_,exit_event,logging_level):
    logging.basicConfig(filename='gui.log', level=logging_level)

    app=QApplication([])

    logging.debug("entered main loop")
    try:
        mainwindow=MainWindow(send_end_thres_,exit_event)
    except Exception:
        logging.error("error creating main window")
    mainwindow.show()
    logging.debug("showed main window")

    app.exec_()