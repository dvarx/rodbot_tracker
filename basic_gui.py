# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:21:39 2020

@author: dvarx
"""

from PyQt5.QtWidgets import QApplication,QLabel,QWidget,QVBoxLayout,QPushButton,QHBoxLayout,QSlider,QMainWindow
from PyQt5.QtCore import Qt
import multiprocessing as mp

app=QApplication([])

"""
Global Variables
"""
send_end_thres=0

class MainWindow(QMainWindow):
    def __init__(self,send_end_thres_,exit_event_,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)

        self.send_end_thres=send_end_thres_
        self.exit_event=exit_event_

        self.setWindowTitle("Control")
        self.layout=QVBoxLayout()

        self.toplayout=QHBoxLayout()
        self.bottomlayout=QHBoxLayout()

        self.topbutton=QPushButton("Top")
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

    def top_btn_cb(self):
        self.topbutton.setText("Clicked Top")

    def slider_val_chgd(self,val):
        self.sliderlabel.setText("Value changed:%-3d"%(val))
        self.send_end_thres.send(val)

    def set_send_pipe(self,send_end_thres_):
        self.send_end_thres=send_end_thres_


def main_loop(send_end_thres_,exit_event):
    mainwindow=MainWindow(send_end_thres_,exit_event)
    mainwindow.show()

    app.exec_()