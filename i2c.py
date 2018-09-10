# ====================================================================
# 
# BARR SYSTEM 
# Arduino - Python communication 
# 
# PLEASE DO NOT EDIT WITHOUT PROPER DISCUSSION WITH THE GROUP 
# 
# ====================================================================

import serial
import re
import time
import numpy as np
from matplotlib import pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import os
import pyqtgraph.console
import PyQt5
import pylab
import keyboard # for keyboard interruption 
import csv 
from functions import I2Creader, DataRead

# from functions import KalmanFilter # filtering currently disabled

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# establish arduino port
port  = '/dev/cu.usbmodem1411' #'COM' for windows
rate = 115200
ard = serial.Serial(port, rate)

if ard.read():
    print('Arduino active...')
else: 
    print('Arduino not active... system will break')

record_row = [] 

# create output csv file 
title = ['Timestamp', 'Acc X1', 'Acc X2', 'Acc X3', 'Acc Y1', 'Acc Y2', 'Acc Y3', 'Acc Z1', 'Acc Z2', 'Acc Z3']
file_dir = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/record.csv'

with open(file_dir, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)

plt.ion()
plt.figure
start = time.time()
while time.time() - start < 5:
    tnow = time.time() - start 
    record_row = I2Creader(ard)
    record_row.insert(0, tnow)
    print(record_row)
    with open(file_dir, 'a') as output_file:
        csv.writer(output_file).writerow(record_row)     
        print('Saving to database')       

    data = DataRead(file_dir)  

    plt.clf()
    # if len(data[0]) <= 15:
    
    plt.plot(data[0], [i - np.mean(data[1]) for i in data[1]])
    plt.plot(data[0], [i - np.mean(data[2]) for i in data[4]])
    plt.plot(data[0], [i - np.mean(data[3]) for i in data[7]])
    # else: 
    #     plt.plot(data[0][-15:], data[1][-15:])
    #     plt.plot(data[0][-15:], data[2][-15:])
    #     plt.plot(data[0][-15:], data[3][-15:])
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (g)')
    # plt.ylim(-2, 2)
    plt.legend(['X', 'Y', 'Z'])
    plt.title('IMU Acceleration Plot')
    plt.pause(0.01)
ard.close() 
