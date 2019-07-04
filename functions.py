'''
====================================================================
BARR SYSTEM 
Basic Functions library 

====================================================================
'''
import os
import pandas as pd
import urllib
import sys 
import glob 
import serial 
import time
import csv 
import math
import numpy as np
from collections import defaultdict
import matplotlib.animation as animation 
from matplotlib import pyplot as plt
import database_gui as db

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on December 7, 2018
#====================================================================

def serial_ports():
    """ list avaliable non bluetooth serial port 

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            if 'Bluetooth' not in port:
                result.append(port)
        except (OSError, serial.SerialException):
            pass
    # print(result)
    return result


#=====================================================================
#   Calibration Related Functions 
#=====================================================================

def manual_calibration(obj, com):
    ''' arduino in calibration mode, print raw readings 
    ''' 
    counter = 0
    while True: 
        if com == 'Serial':
            line = obj.readline().decode('utf-8').replace('\r\n', '')
        else: 
            line = urllib.request.urlopen(obj).read().decode('utf-8').replace('\r', '')
        print(line)
        if 'Calibration Results:' in line: 
            counter +=1 
            print('One sensor calibrated')
        if counter == 2:
            print('Done calibrating')
            break


#=====================================================================
#   Gait Calculations 
#=====================================================================

def quaternion_to_rot_mat(quaternion):
    a, b, c, d = float(quaternion[:,0]), float(quaternion[:,1]), float(quaternion[:,2]), float(quaternion[:,3])
    r11 = a*a + b*b - c*c - d*d
    r12 = 2*b*c - 2*a*d
    r13 = 2*b*d + 2*a*c
    r21 = 2*b*c + 2*a*d 
    r22 = a*a - b*b + c*c - d*d 
    r23 = 2*c*d - 2*a*b
    r31 = 2*b*d - 2*a*c 
    r32 = 2*c*d + 2*a*b 
    r33 = a*a - b*b - c*c +d*d 
    rot_mat = np.matrix([[r11, r12, r13], [r21, r22, r23], [r31, r32, r33]])
    return rot_mat


def fix_acc(acceleration, quaternion):
    ''' fix body frame acceleration to earth frame acceleration
        use lin_acc as imput for calculation
        use acc for trouble shooting 
    '''
    rotmat = quaternion_to_rot_mat(quaternion)
    acc = np.transpose(np.dot(np.linalg.inv(rotmat), np.transpose(acceleration)))
    ''' uncomment for matrix calculation ''' 
    # acc_earth = np.empty(acceleration.shape)
    # for i in range(len(quaternion)):
    #     rot_mat = quaternion_to_rot_mat(quaternion[i,:])
    #     acc_fixed = np.dot(acceleration[i,:],  np.linalg.inv(rot_mat)) 
    #     acc_earth[i,:] = acc_fixed
    return acc


def integrate(time, data):
    ''' integration uses trapezoid rule 
        assume measurement is at the beginning of each second
        result is the speed at the beginning of each second
    '''
    sides = data[1:,:] + data[0:data.shape[0] - 1,:]
    height = time[1:,:] - time[0:time.shape[0]-1,:]
    data_int = np.multiply(sides, height)/2
    zeros = np.matrix(np.zeros(data_int.shape[1]))
    data_int = np.concatenate((zeros, np.cumsum(data_int, axis = 0)), axis = 0)
    return data_int
        

#=====================================================================
#   file content retrival functions 
#=====================================================================

def get_files(path, extension):
    ''' get list of files in path with extension
    '''
    os.chdir(path)
    list_files = [i for i in glob.glob('*.{}'.format(extension))]
    return list_files

def csv_read(filename, data_type):
    ''' read csv files and save in list or dictionary
        list is good for numerical 
        dictionary is good for tables with headers
    '''
    data = pd.read_csv(filename)
    df = pd.DataFrame(data)
    if data_type == 'list':
        raw = np.transpose(np.matrix(df.values.T.tolist()))
    elif data_type == 'dict':
        raw = df.to_dict()
    else:
        print('ERROR: Wrong data type')
        return None
    return raw 

def csv_write(filename, data):
    df = pd.DataFrame(data)
    df.to_csv(filename)

if __name__ == '__main__':
    squat = os.path.dirname(os.path.realpath(__file__)) + '/output/Squat/'
    list_files = get_files(squat, 'csv')
    data = csv_read(list_files[0], 'list')
