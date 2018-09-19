# ====================================================================
# 
# BARR SYSTEM 
# Function library 
# 
# PLEASE DO NOT EDIT WITHOUT PROPER DISCUSSION WITH THE GROUP 
# 
# ====================================================================
import csv 
from collections import defaultdict
import matplotlib.animation as animation 

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on July 28, 2018 
#====================================================================

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


def I2Creader(Arduino): 
    # this function reads string from the port, split into sensor 1 & 2, parse by comma, and match with the dictionary 
    line = Arduino.readline().decode('utf-8').replace('\r\n', '')

    # define dict/matching format 
    reading1 = {'t': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}
    reading2 = {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}
    
    if 'y' in line: # identify sensor 2 
        line = line.split('y')
        # if there are multiple sets of sensor 2 readings keep the first one and delete the rest 
        if line.count('y') > 1:
            line = line[:-1]
        
        line2 = line[1].split(',') # sensor 1
        line1 = line[0].split(',') # sensor 2 
        
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
                except ValueError: 
                    value = float('NaN')
                reading1[current_element[0]] = value 
        
        for k in range(len(line2)): # sensor 2
            current_element = line2[k].split(':')
            if current_element[0] in reading2: 
                try:
                    value = float(current_element[1])
                except ValueError: 
                    value = float('NaN')
                    print('value converting mistake, exporting')
                reading2[current_element[0]] = value  
    # print('sensor2:', reading2)
    # convert dict to list 
    record1 = list(reading1.values())
    record2 = list(reading2.values())
    record2.insert(0,tnow)
    # print('current time:', type(tnow), tnow)
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