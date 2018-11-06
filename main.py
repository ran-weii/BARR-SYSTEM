# ====================================================================
'''
BARR SYSTEM 
This script is customized for testing 2 sensor
'''
# ====================================================================

import serial
import re
import datetime
import numpy as np
import os
import keyboard # for keyboard interruption 
import csv 
import functions as barr
import database as db
import sqlite3 as sql
# from functions import KalmanFilter # filtering currently disabled

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

# interactive test set-up
test_name = input('Test Name:')
trial_num = input('Trial Number:')
duration = float(input('Testing Duration:'))

# define serial port
try:
    port = barr.serial_ports()[0]
except IndexError: 
    print('No port detected, program exit')
    exit()

rate = 115200
ard = serial.Serial(port, rate)
# ard.reset_input_buffer()

# create output csv file 
store_dir = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/'
db_dir = store_dir + 'barr_system.db'

conn = sql.connect(db_dir)
db.delete_table(conn, 'Sensor_1')
db.delete_table(conn, 'Sensor_2')
db.delete_table(conn, 'Gait_1')
db.delete_table(conn, 'Gait_2')

titles = ("(Datetime, Timestamp, "
"Acc_X, Acc_Y, Acc_Z, "
"Lin_X, Lin_Y, Lin_Z, "
"Gyr_X, Gyr_Y, Gyr_Z, "
"Euler_X, Euler_Y, Euler_Z, "
"Quat_W, Quat_X, Quat_Y, Quat_Z)")
values = "(" + "?, "*titles.count(',') + "?)"

gait_titles = ("(Datetime, Timestamp, "
"Acc_Forward, Acc_Right, Acc_Down, "
"Speed_Forward, Speed_Right, Speed_Down, "
"Distance_Forward, Distance_Right, Distance_Down, "
"Rotspeed_X, Rotspeed_Y, Rotspeed_Z, "
"Angle_X, Angle_Y, Angle_Z")
gait_values = "(" + "?, "*gait_titles.count(',') + "?)"

db.create_table(conn, 'Sensor_1', titles)
db.create_table(conn, 'Sensor_2', titles)
db.create_table(conn, 'Gait_1', gait_titles)
db.create_table(conn, 'Gait_2', gait_titles)

initial_time = datetime.datetime.now()
tnow = 0
while tnow < duration:
    tnow, record1, record2 = barr.I2Creader(ard)
    tnow = datetime.timedelta(seconds = tnow)
    current_time = (initial_time + tnow).strftime("%B %d, %Y %I:%M:%S%p")
    db.data_entry(conn, 'Sensor_1', titles, values, record1.insert(0,current_time)) 
    db.data_entry(conn, 'Sensor_2', titles, values, record2.insert(0,current_time))

    db.delete_all_entry(conn, 'Gait_1')
    db.delete_all_entry(conn, 'Gait_2')
    sensor1 = db.data_read(conn, 'sensor_1', '*')[5:,:]
    sensor2 = db.data_read(conn, 'sensor_2', '*')[5:,:] 

    timestamp1 = sensor1[:,0]
    timestamp2 = sensor2[:,0]
    acc1 = sensor1[:,1:4]
    acc2 = sensor2[:,4:7]
    gyro1 = sensor1[:,7:10]
    gyro2 = sensor2[:,7:10]
    quat1 = sensor1[:,13:17]
    quat2 = sensor2[:,13:17]

    # angle
    length = min(gyro1.shape[0], gyro2.shape[0])
    angula_speed = gyro1[:length, :] - gyro2[:length, :]
    angle_change = barr.integrate(timestamp1[:length, :], angula_speed) 
    # acceleration
    acc_earth1 = barr.fix_acc(acc1,quat1)
    speed_earth1 = barr.integrate(timestamp1, acc_earth1)
    distance_earth1 = barr.integrate(timestamp1, speed_earth1)

    acc_earth2 = barr.fix_acc(acc2,quat2)
    speed_earth2 = barr.integrate(timestamp2, acc_earth2)
    distance_earth2 = barr.integrate(timestamp2, speed_earth2)

    gait_entry1 = np.concatenate((timestamp1, acc_earth1, speed_earth1, distance_earth1, angula_speed, angle_change), axis = 1)
    gait_entry2 = np.concatenate((timestamp2, acc_earth2, speed_earth2, distance_earth2, angula_speed, angle_change), axis = 1)
    
    db.data_entry(conn, 'Gait_1', gait_titles, gait_values, gait_entry1)
    db.data_entry(conn, 'Gait_2', gait_titles, gait_values, gait_entry2) 

ard.close() 