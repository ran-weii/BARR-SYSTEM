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

def IMUreader(Arduino): 
    record_row = []
    while True: 
        line = Arduino.readline().decode('utf-8')
        if 'sensorId' in line: 
            while len(record_row) < 12: 
                line = Arduino.readline().decode('utf-8')
                if 'sensorId' in line: 
                    pass 
                elif ':' in line: 
                    IMUreading = float(line.split(':')[1])
                    record_row.append(IMUreading)
                elif 'ms' in line: 
                    t = float(line.split(' ')[1].split('ms')[0])/1000
                    record_row = [t] + record_row 
        break
    return record_row

def DataRead(file_dir): 
    with open(file_dir, 'r') as input_file: 
        headers = next(csv.reader(input_file)) 

    columns = defaultdict(list)
    print('Pulling from database')
    with open(file_dir, 'r') as input_file: 
        for row in csv.DictReader(input_file): # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                columns[k].append(v)

    raw = []
    for j in range(len(headers) - 1): 
        raw.append([float(i) for i in columns[headers[j]]])
    return raw
