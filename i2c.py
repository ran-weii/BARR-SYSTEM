# ====================================================================
'''
BARR SYSTEM 
This script is customized for testing 2 sensor
'''
# ====================================================================

import serial
import re
import time
import numpy as np
from matplotlib import pyplot as plt
import os
import keyboard # for keyboard interruption 
import csv 
from functions import serial_ports, I2Creader, DataRead

# from functions import KalmanFilter # filtering currently disabled

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# define serial port
port = serial_ports()[0]
print('Current Port:', port)
rate = 9600
ard = serial.Serial(port, rate)
# time.sleep(0.003) # wait 0.003 sec for Arduino

# interactive test set-up
test_name = input('Test Name:')
trial_num = input('Trial Number:')
duration = float(input('Testing Duration:'))

# create output csv file 
title = ['Timestamp', 'Acc X', 'Acc Y', 'Acc Z', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Mag X', 'Mag Y', 'Mag Z']
store_dir = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/'
file1_dir = store_dir + test_name + '_' + trial_num + '_' + 'sensor1.csv'
file2_dir = store_dir + test_name + '_' + trial_num + '_' + 'sensor2.csv'

with open(file1_dir, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)
with open(file2_dir, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')  
    writer.writerow(title)

plt.ion()
plt.figure
start = time.time()
while time.time() - start < duration:
    tnow = time.time() - start 
    print('current time:', round(tnow,2), 's')
    record1, record2 = I2Creader(ard)
    if len(record1) > 1 or len(record2) > 1:
        with open(file1_dir, 'a') as output_file:
            csv.writer(output_file).writerow(record1)       
        with open(file2_dir, 'a') as output_file:
            csv.writer(output_file).writerow(record2)  
    
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
