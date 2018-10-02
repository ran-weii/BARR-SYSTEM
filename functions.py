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


if __name__ == '__main__':
    print(serial_ports())

def IMUreader(Arduino):
    while True: 
        try: 
            line = Arduino.readline().decode('utf-8').replace('\r\n', '')
        except UnicodeDecodeError: 
            pass 
    
    line = line.split(',')
    reading = {'t': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None}
    
    for k in range(len(line)): 
            current_element = line[k].split(':')
            if current_element[0] in reading: 
                try:
                    value = float(current_element[1])
                except ValueError: 
                    value = None
                    print('value converting mistake, exporting')
                reading[current_element[0]] = value 
    record = list(reading.values()) 
    return record

def I2Creader(Arduino): 
    # this function reads string from the port, split into sensor 1 & 2, parse by comma, and match with the dictionary 
    try: 
        line = Arduino.readline().decode('utf-8').replace('\r\n', '')
    except UnicodeDecodeError: 
        pass 
    print(line)
    # define dict/matching format 
    reading1 = {'t': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None}
    reading2 = {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None}
    
    if 'y' in line: # identify sensor 2 
        line = line.split('y')
        # if there are multiple sets of sensor 2 readings keep the first one and remove the rest 
        if line.count('y') > 1:
            line = line[:-1]
        line2 = line[1].split(',') # sensor 1
        line1 = line[0].split(',') # sensor 2 
        # print('sensor1:', line1)
        # print('sensor2:', line2)
        tnow = 0 
        # match column title and update dict 
        for k in range(len(line1)): # sensor 1
            current_element = line1[k].split(':')
            if current_element[0] in reading1: 
                try:
                    value = float(current_element[1])
                    if 't' in current_element[0]: 
                        current_element[0]
                        value = value/1000
                        tnow = value
                        # print('current time:', tnow)
                except ValueError: 
                    value = None 
                reading1[current_element[0]] = value 
        
        for k in range(len(line2)): # sensor 2
            current_element = line2[k].split(':')
            if current_element[0] in reading2: 
                try:
                    value = float(current_element[1])
                except ValueError: 
                    value = None
                    print('value converting mistake, exporting')
                reading2[current_element[0]] = value  
    # convert dict to list 
    record1 = list(reading1.values())
    record2 = list(reading2.values())
    record2.insert(0,tnow)
    print('Sensor1:', record1, 'Sensor2:', record2)
    
    return record1, record2

def DataRead(file_dir): 
    # read raw reading from local csv files 
    with open(file_dir, 'r') as input_file: 
        headers = next(csv.reader(input_file)) 
    columns = defaultdict(list)
    print('Pulling from database')
    # read into dict 
    with open(file_dir, 'r') as input_file: 
        for row in csv.DictReader(input_file): # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                columns[k].append(v)
    raw = []
    for j in range(len(headers)): 
        current = []
        for i in columns[headers[j]]: 
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

class KalmanFilter(object):
# kalman filter copied from web 
    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate
