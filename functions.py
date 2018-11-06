'''
====================================================================
BARR SYSTEM 
Function library 

PLEASE DO NOT EDIT WITHOUT PROPER DISCUSSION WITH THE GROUP 
====================================================================
'''

import sys 
import glob 
import serial 
import csv 
import math
import numpy as np
from collections import defaultdict
import matplotlib.animation as animation 

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
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
    
    return result


def I2Creader(Arduino): 
    # this function reads string from the port, split into sensor 1 & 2, parse by comma, and match with the dictionary 
    flag = 0
    try: 
        line = Arduino.readline().decode('utf-8').replace('\r\n', '')
        line = line.replace(' ', '')
        line = line.replace('\t', '')
        # print('raw:', line)
        # log only when there is 1 x and 1 y)
        if line.count('y') == 1 and line.count('x') == 1 and line.count('t') == 1:
            line = line.split('y')
            line1 = line[0].split(',') # sensor 1
            line2 = line[1].split(',') # sensor 2
            # print('sensor1:', line1)
            # print('sensor2:', line2)
            flag = 1
        else: 
            pass
    except UnicodeDecodeError: 
        pass 
    # print(line)
    # define dict/matching format 
    reading1 = {'t': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None}
    reading2 = {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None}
    tnow = None
    # print('flag:', flag)
    if flag == 1:
        # match column title and update dict 
        for k in range(len(line1)): # sensor 1
            current_element = line1[k].split(':')
            header = current_element[0]
            if header in reading1: 
                try:
                    value = float(current_element[1])
                    if 't' in current_element[0]: 
                        tnow = value
                        print('current time:', tnow, 's')
                except ValueError: 
                    value = None 
                reading1[header] = value 
        
        for k in range(len(line2)): # sensor 2
            current_element = line2[k].split(':')
            header = current_element[0].replace(' ', '')
            if header in reading2: 
                try:
                    value = float(current_element[1])
                except ValueError: 
                    value = None
                    print('value converting mistake, exporting')
                reading2[header] = value  
    else: 
        pass 
    # convert dict to list 
    record1 = list(reading1.values())
    record2 = list(reading2.values())
    record2.insert(0,tnow)
    print('Sensor1:', record1, 'Sensor2:', record2)
    
    return tnow, record1, record2


def DataRead(file_dir): 
    # read raw reading from local csv files 
    with open(file_dir, 'r') as input_file: 
        headers = next(csv.reader(input_file)) 
    columns = defaultdict(list)
    # print('Pulling from database')
    # read into dict 
    with open(file_dir, 'r') as input_file: 
        for row in csv.DictReader(input_file): # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                columns[k].append(v)
    raw = []
    for j in range(len(headers)): 
        current = []
        # print('column', j)
        for i in columns[headers[j]]: 
            # print(i)
            try: 
                current.append(float(i))
            except ValueError: 
                current.append(float('NaN'))
                print('value converting mistake, importing')
            except TypeError: 
                current.append(float('NaN'))
                print('type converting mistake, importing')
        raw.append(current)
    return raw


def quaternion_to_rot_mat(quaternion):
    a, b, c, d = quaternion[0,0], quaternion[0,1], quaternion[0,2], quaternion[0,3]
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


def integrate(time, data):
    # integration uses trapezoid rule 
    # assume measurement is at the beginning of each second
    # result is the speed at the beginning of each second
    sides = data[1:,:] + data[0:data.shape[0] - 1]
    height = time[1:,:] - time[0:time.shape[0]-1]
    data_int = np.multiply(sides, height)/2
    zeros = np.matrix(np.zeros(data_int.shape[1]))
    data_int = np.concatenate((zeros, np.cumsum(data_int, axis = 0)), axis = 0)
    return data_int


def fix_acc(acceleration, quaternion):
    # fix body frame acceleration to earth frame acceleration
    # use lin_acc as imput for calculation
    # use acc for trouble shooting 
    acc_earth = np.empty(acceleration.shape)
    for i in range(len(quaternion)):
        rot_mat = quaternion_to_rot_mat(quaternion[i,:])
        acc_fixed = np.dot(acceleration[i,:],  np.linalg.inv(rot_mat)) 
        acc_earth[i,:] = acc_fixed
    return acc_earth


if __name__ == '__main__':
    print('COM Port:', serial_ports())
    # test integration module
    a = np.matrix('3;3;-3;-3;0')
    b = np.matrix('1;2;3;4;5')
    v = integrate(b,a)
    print(integrate(b,a))
