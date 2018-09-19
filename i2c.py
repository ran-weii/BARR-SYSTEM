# ====================================================================
# 
# BARR SYSTEM 
# Arduino - Python communication 
# 
# This script is currently able to read from serial port, saving in csv file,
# and read from csv file
# 
# PLEASE DO NOT EDIT WITHOUT PROPER DISCUSSION WITH THE GROUP 
# 
# ====================================================================

import serial
import re
import time
import numpy as np
from matplotlib import pyplot as plt
import os
import keyboard # for keyboard interruption 
import csv 
from functions import I2Creader, DataRead

# from functions import KalmanFilter # filtering currently disabled

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# establish arduino port
port  = '/dev/cu.usbmodem1421' # 1411/1421 'COM' for windows 
rate = 115200
ard = serial.Serial(port, rate)
print('port')
time.sleep(0.003) # wait 0.003 sec for Arduino

if ard.read():
    print('Arduino active...')
else: 
    print('Arduino not active... system will break')

record_row = [] 

# create output csv file 
title = ['Timestamp', 'Acc X', 'Acc Y', 'Acc Z', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Mag X', 'Mag Y', 'Mag Z']
file_dir1 = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/sensor1.csv'
file_dir2 = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/sensor2.csv'

with open(file_dir1, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)
with open(file_dir2, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)

plt.ion()
plt.figure
start = time.time()
while time.time() - start < 5:
    tnow = time.time() - start 
    # print('current time:', tnow)
    record1, record2 = I2Creader(ard)
    # record1.insert(0, tnow)
    # record2.insert(0, tnow)
    if len(record1) > 1 or len(record2) > 1:
    # print(record_row)
        with open(file_dir1, 'a') as output_file:
            csv.writer(output_file).writerow(record1)     
            # print('Saving to database')       
        with open(file_dir2, 'a') as output_file:
            csv.writer(output_file).writerow(record2)  
            # print('Saving to database')  
    
    # data = DataRead(file_dir1)  
    # print(data)
    # plt.clf()
    # if len(data) > 0:
    
    #     plt.plot(data[0], [i - np.mean(data[1]) for i in data[1]])
    #     plt.plot(data[0], [i - np.mean(data[2]) for i in data[2]])
    #     plt.plot(data[0], [i - np.mean(data[3]) for i in data[3]])
    #     # else: 
    #     #     plt.plot(data[0][-15:], data[1][-15:])
    #     #     plt.plot(data[0][-15:], data[2][-15:])
    #     #     plt.plot(data[0][-15:], data[3][-15:])
    #     plt.xlabel('Time (s)')
    #     plt.ylabel('Acceleration (g)')
    #     # plt.ylim(-2, 2)
    #     plt.legend(['X', 'Y', 'Z'])
    #     plt.title('IMU Acceleration Plot')
    #     plt.pause(0.01)
ard.close() 
