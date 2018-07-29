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
from functions import IMUreader, DataRead
# from functions import KalmanFilter # filtering currently disabled

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# establish connection with arduino
port  = '/dev/cu.usbmodem1411' #'COM' for windows
rate = 115200
ard = serial.Serial(port, rate)
# check arduino status 
if ard.read():
    print('Arduino active...')
else: 
    print('Arduino not active... system will break')

record_row = [] 

# create output csv file 
title = ['Timestamp(ms)', 'Acc X', 'Acc Y', 'Acc Z', 'Acc Sqrt', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Mag X', 'Mag Y', 'Mag Z', 'Horz DIR']
file_dir = '/Users/apple/Documents/GitHub/BARR-SYSTEM/output/record.csv'

with open(file_dir, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)

plt.ion()
plt.figure
start = time.time()
while time.time() - start < 30:
    record_row = IMUreader(ard)
    if len(record_row) == 12: 
        with open(file_dir, 'a') as ourput_file:
            csv.writer(ourput_file).writerow(record_row)     
            print('Saving to database')       
                
    data = DataRead(file_dir)  
    plt.clf()
    # if len(data[0]) <= 15:
    
    plt.plot(data[0], [i - np.mean(data[1]) for i in data[1]])
    plt.plot(data[0], [i - np.mean(data[2]) for i in data[2]])
    plt.plot(data[0], [i - np.mean(data[3]) for i in data[3]])
    # else: 
    #     plt.plot(data[0][-15:], data[1][-15:])
    #     plt.plot(data[0][-15:], data[2][-15:])
    #     plt.plot(data[0][-15:], data[3][-15:])
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (g)')
    plt.ylim(-2, 2)
    plt.legend(['X', 'Y', 'Z'])
    plt.title('IMU Acceleration Plot')
    plt.pause(0.01)



# actual_values = [0 for j in range(iteration_c)]
# print(actual_values)

# measurement_standard_deviation = np.std(gyr[0])
# noisy_measurement = acc[0]
# print(noisy_measurement)

# for j in range(iteration_c):
#    process_variance = 1e-3
#    estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
#    kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
  
#    posteri_estimate_graph = []

#    for iteration in range(1, iteration_c-1):
#        kalman_filter.input_latest_noisy_measurement(noisy_measurement[iteration])
#        posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())


#    pylab.figure()
#    pylab.plot(noisy_measurement, color='r', label='noisy measurements')
#    pylab.plot(posteri_estimate_graph, 'b-', label='a posteri estimate')
#    pylab.plot(actual_values, color='g', label='truth value')
#    pylab.legend()
#    pylab.xlabel('Iteration')
#    pylab.ylabel('Acceleration-X')
#    pylab.show()

ard.close()


