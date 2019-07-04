# ====================================================================
'''
BARR SYSTEM 
Arduino Data Collection

Read and parse data from Arduino serial port, calculate basic 
measurements and store in SQL database 
'''
# ====================================================================

import os
import serial
import urllib
import re
import datetime
import time 
import numpy as np
import math
import os
import functions as barr
import database_gui as db
import sqlite3 as sql
import pandas as pd
from matplotlib import pyplot as plt

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on December 7, 2018
#====================================================================

def record():
    ''' receive start/stop command from gui at file ./comm_center/gui.txt
        stop loop if command stop
    ''' 

    directory = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/'
    
    ''' read name from comm center '''
    comm_center = open(directory + 'comm_center/gui.txt', 'r')
    name = comm_center.read()
    comm_center.close()
    
    conn = db.setup(directory + 'output/')
    raw_table, gait_table = db.create_session(conn, name, 1)
    raw_headers, gait_headers = db.headers()
    
    exercise = 1
    ''' setup arduino communiation ''' 
    try: 
        port = barr.serial_ports()[0]
        print('Connected to port:', port)
    except IndexError: 
        print('No port detected, please plug in the device')
    
    rate = 38400
    arduino = serial.Serial(port, rate)
    arduino.flushInput()
    arduino.flushOutput()
    arduino.flush()
    
    ''' collect data from arduino '''
    counter1 = 1
    while True:
        
        line = arduino.readline().decode('utf-8').replace('\r\n', '').split(' ')

        if len(line) == 33:
            
            try: 
                readings = np.matrix([float(value) for value in line])
                lin1, lin2 = readings[0, 4:7], readings[0,20:23]
                gyr1, gyr2 = readings[0,7:10], readings[0,23:26]
                quat1, quat2 = readings[0,13:17], readings[0,29:33]
                
                try: 
                    # earth-fixed acceleration
                    acc1 = barr.fix_acc(lin1, quat1)
                    acc2 = barr.fix_acc(lin2, quat2)
                    
                    if counter1 == 1:
                        print('Start exercise')
                        initial = readings[0,0]/1000
                        t_last = 0
                    counter1 += 1

                    t_current = readings[0,0]/1000 - initial 
                    # print current time every 1 second
                    if math.floor(t_current) - math.floor(t_last) == 1: 
                        print("Time: ", math.floor(t_current))

                    t_last = t_current
                    angular_speed = gyr1 - gyr2
                    
                    gait_entry = np.concatenate((np.matrix(exercise), np.matrix(counter1), \
                                np.matrix(t_current), acc1, acc2, angular_speed), axis = 1)
                    
                    ''' check comm center '''
                    #====================================================================
                    comm_center = open(directory + 'comm_center/gui.txt', 'r')
                    message = comm_center.read()
                    if 'stop' in message:
                        arduino.close()
                        exit()
                    #====================================================================
                    
                    db.data_entry(conn, raw_table, raw_headers, readings) 
                    db.data_entry(conn, gait_table, gait_headers, gait_entry)
                except np.linalg.linalg.LinAlgError: # singular matrix due to initialization error    
                    pass 
            except ValueError: 
                pass
        else: 
            pass
    arduino.close()
    counter1 += 1
        
    arduino.close()

if __name__ == '__main__':
    record()
