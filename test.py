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
from collections import defaultdict
from functions import IMUreader, ColumnRead

# if __name__ == "__main__":
#     import random
#     iteration_count = 500

#     actual_values = [-0.37727 + j * j * 0.00001 for j in range(iteration_count)]
#     noisy_measurement = [random.random() * 2.0 - 1.0 + actual_val for actual_val in actual_values]
#     print(noisy_measurement)

port  = '/dev/cu.usbmodem1411' #'COM' for windows
rate = 115200
ard = serial.Serial(port, rate)
ard.close()
# counter = 1
# iteration_c = 30 

# while True:
#     if (ard.inWaiting() > 0): # check port input nonempty 
#         counter += 1
  
#         line = ard.readline().decode('utf-8')
#         print(line)

#     if keyboard.is_pressed('p'):
#             print('Recording ended')
#             break
file_dir = '/Users/apple/Desktop/BARR SYSTEM/record.csv'
columns = defaultdict(list) # each value in each column is appended to a list

with open(file_dir) as f:
    headers = next(csv.reader(f))
    # print(len(headers))
with open(file_dir) as f:
    reader = csv.DictReader(f) # read rows into a dictionary format
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        for (k,v) in row.items(): # go over each column name and value 
            columns[k].append(v)
# print([float(i)/1000 for i in columns[headers[0]]])

data = ColumnRead(file_dir)  
print(data) 


# pull values from database - currently csv file

columns = defaultdict(list)
# with open(file_dir, 'r') as input_file: 
#     print('open reader')
#     # while True: 
#     now = time.time()
#     print(time.time() - now)
#     if time.time() >= now + 2: 
#         now = time.time() 
#         for row in csv.DictReader(input_file): # read a row as {column1: value1, column2: value2,...}
#             for (k,v) in row.items(): # go over each column name and value 
#                 columns[k].append(v)
#         # print(columns['Timestamp'])
#         print('Pulling data from database')
#         t = [float(i)/1000 for i in columns['Timestamp']]

#         accx = [float(i) for i in columns['Acc X']]
#         accy = [float(i) for i in columns['Acc Y']]
#         accz = [float(i) for i in columns['Acc Z']]

#         gyrx = [float(i) for i in columns['Gyr X']]
#         gyry = [float(i) for i in columns['Gyr Y']]
#         gyrz = [float(i) for i in columns['Gyr Z']]

#         magx = [float(i) for i in columns['Mag X']]
#         magy = [float(i) for i in columns['Mag Y']]
#         magz = [float(i) for i in columns['Mag Z']]

#         # plot, organize as a function later 
#         print('Start plotting')
#         if len(t) <= 10: 
#             plt.figure(1)
#             plt.subplot(311)
#             plt.plot(t, accx, 'r', t, accy, 'b', t, accz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Acceleration')

#             plt.subplot(312)
#             plt.plot(t, gyrx, 'r', t, gyry, 'b', t, gyrz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Gyroscope')

#             plt.subplot(313)
#             plt.plot(t, magx, 'r', t, magy, 'b', t, magz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Magnatometer')
#             plt.show()
#         else: 
#             t = t[-10:]

#             accx = accx[-10:]
#             accy = accy[-10:]
#             accz = accz[-10:]

#             gyrx = gyrx[-10:]
#             gyry = gyry[-10:]
#             gyrz = gyrz[-10:]

#             magx = magx[-10:]
#             magy = magy[-10:]
#             magz = magz[-10:]

#             plt.figure(1)
#             plt.subplot(311)
#             plt.plot(t, accx, 'r', t, accy, 'b', t, accz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Acceleration')

#             plt.subplot(312)
#             plt.plot(t, gyrx, 'r', t, gyry, 'b', t, gyrz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Gyroscope')

#             plt.subplot(313)
#             plt.plot(t, magx, 'r', t, magy, 'b', t, magz, 'g')
#             plt.legend(['X', 'Y', 'Z'], loc = 'upper right')
#             plt.title('Magnatometer')
#             plt.show()