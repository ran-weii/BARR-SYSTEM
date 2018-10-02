# ====================================================================
'''
BARR SYSTEM 
This script is customized for testing 1 sensor
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
from functions import serial_ports, IMUreader, DataRead

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# define serial port
port = serial_ports()[0]
if port: 
    pass 
else: 
    exit()

print('Current Port:', port)
rate = 9600
ard = serial.Serial(port, rate)

test_name = input('Test Name:')
trial_num = input('Trial Number:')
# create output csv file 
title = ['Timestamp', 'Acc X', 'Acc Y', 'Acc Z', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Mag X', 'Mag Y', 'Mag Z', 'Quat 1', 'Quat 2', 'Quat 3', 'Quat 4', 'L Acc X', 'L Acc Y', 'L Acc Z']
store_dir = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/'
file_dir = store_dir + test_name + '_' + trial_num + '_' + 'sensor.csv'

with open(file_dir, 'w') as ourput_file:
    writer = csv.writer(ourput_file, delimiter = ',', lineterminator='\n')
    writer.writerow(title)

plt.ion()
plt.figure
start = time.time()
while time.time() - start < 15:
    tnow = time.time() - start 
    print('current time:', round(tnow,2), 's')
    record = IMUreader(ard)
    if len(record) > 1:
        with open(file_dir, 'a') as output_file:
            csv.writer(output_file).writerow(record)
ard.close() 