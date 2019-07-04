# ====================================================================
'''
BARR SYSTEM 
Knee Angle Analysis 

For detail in this script please see project report link on:
https://github.com/rw422scarlet/BARR-SYSTEM
'''
# ====================================================================

import os
import re
import datetime
import numpy as np
import math
import os
import functions as barr
import database_gui as db
import sqlite3 as sql
import pandas as pd
from matplotlib import pyplot as plt
from peak_detect.peakdetect import peakdet
import json
from joblib import dump, load
from PIL import Image, ImageDraw, ImageFont

#====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on December 7, 2018
#====================================================================

def moving_average(x, n):
    ''' moving average of np matrix x
        the first n - 1 values of means of its own sample size 
    '''
    mov_mean = np.zeros(x.shape)
    for row in range(x.shape[0]):
        if row == 0: 
            mov_mean[row,:] = x[0, :]
        elif row > 0 and row <= n:
            mov_mean[row,:] = np.mean(x[0:row, :], axis = 0)
        else: 
            mov_mean[row,:] = np.mean(x[row - n:row, :], axis = 0)
    return mov_mean 


def txt_read():
    ''' read from local directory 
    '''
    directory = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/'
    with open(directory + 'result.txt', 'r') as f:
        result = f.read()
    print(result)


def txt_write(max_angle, form):
    ''' write max angle and form result in text to local txt document
    '''
    directory = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/'
    ''' write '''
    result = max_angle + ',' + form
    with open(directory + 'result.txt', 'w') as f:
        f.write(result)


#=====================================================================
#   Main Analysis Function
#=====================================================================

def analysis():
    ''' Variables: 
        alpha: rotational speed (deg/sec)
        theta: rotation angle 
        gait_table: gait table name in database
        max_angle: maximum angle in each direction +/-, angle z is -
        neutural position: time of maximum point between every 2 max z angle, sign of standing straight
        neutural: angle xyz at neutural position
        start & end: where the scatter plot start to curve significantly 
        rep_interval: time between every 2 peaks in angle z
        valugs: data feature of knee caving in 
    '''
    max_angle = None
    valgus_pause = None
    reptime = None

    directory = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/'
    
    ''' setup database connection '''
    conn = db.setup(directory+'output/')
    last_registration = db.data_read(conn, 'Registration', '*', '', '')[-1,:]
    print('Name: ', last_registration)
    gait_table = last_registration[0,2] + '_' + last_registration[0,0] + 'x' + \
                last_registration[0,1] + '_' + 'Gait'
    gait = db.data_read(conn, gait_table, '*', 'Exercise', 1)
    timestamp = gait[:,2] - gait[0,2]
    alpha = np.array(moving_average(gait[:,9:12],3))
    theta = np.array(barr.integrate(timestamp, alpha))

    flag = 1
    
    ''' find peaks (theta Z > 45) '''
    if flag == 1:
        theta_peak = theta[np.abs(theta[:,2]) > 45]
        time_peak = timestamp[np.abs(theta[:,2]) > 45]

        if theta_peak.shape[0] > 1:
            cutoff = np.where(np.diff(time_peak, axis = 0) > 0.3)[0]
            idx_cutoff = np.zeros((cutoff.shape[0]+1, 2))
            for i in range(cutoff.shape[0] + 1):
                if i == 0:
                    idx_cutoff[i,:] = [1, cutoff[i]]
                elif i == cutoff.shape[0]:
                    idx_cutoff[i,:] = [cutoff[i-1]+1, time_peak.shape[0]]
                else:
                    idx_cutoff[i,:] = [cutoff[i-1]+1, cutoff[i]]
            flag = 1
    else: 
        flag = 0 # mark quit analysis 
    
    
    if flag == 1:
        ''' find max knee angles '''
        max_angle = []
        idx_max = []
        for j in range(3):
            max_angle_ax = []
            idx_max_ax = []
            for i in range(idx_cutoff.shape[0]):
                current_theta = theta_peak[int(idx_cutoff[i][0]):int(idx_cutoff[i][1]), j]
                first_half = current_theta[0:int(np.floor(current_theta.shape[0]/2))]
                last_half = current_theta[-int(np.floor(current_theta.shape[0]/2)):]
                try: 
                    slope_first = np.polyfit(np.arange(len(first_half)), first_half, 1)[0]
                    slope_last = np.polyfit(np.arange(len(last_half)), last_half, 1)[0]
                    if slope_first < 0 or slope_last > 0:
                        max_index = np.where(theta[:,j] == np.min(current_theta))[0][0]
                        max_theta_ax = np.min(current_theta)
                    else: 
                        max_index = np.where(theta[:,j] == np.max(current_theta))[0][0]
                        max_theta_ax = np.max(current_theta)
                except ValueError:
                    pass

                idx_max_ax.append(max_index)
                max_angle_ax.append(float(max_theta_ax))
            idx_max.append(idx_max_ax)
            max_angle.append(max_angle_ax)
        max_angle = np.transpose(np.matrix(max_angle))

        ''' find max theta time and index '''
        idx_max_z = idx_max[2]
        time_max = timestamp[idx_max[2],0]

        ''' find neutural points '''
        idx_neutural = []
        for i in range(len(idx_max_z) + 1):
            if i == 0:
                current_window = theta[0:idx_max_z[0], 2]
            elif i == len(idx_max_z):
                current_window = theta[idx_max_z[i-1]:, 2]
            else: 
                current_window = theta[idx_max_z[i-1]:idx_max_z[i], 2]
            theta_neutural = np.max(current_window)
            idx_neutural.append(np.where(theta[:,2] == theta_neutural)[0][0])

        ''' find rep start index '''
        idx_start = []
        for i in range(len(idx_neutural) - 1):
            current_neutural = idx_neutural[i]
            idx_peak = idx_max_z[i]
            alpha_window = alpha[current_neutural:idx_peak, 2]
            greater15 = np.abs(alpha_window) > 15
            greater15 = greater15.astype(np.int)
            # find first squat window with 5 alpha > 15
            counter = 1
            while counter < len(greater15):
                greater15_window = greater15[counter:counter+5]
                if sum(greater15_window) == 5:
                    break
                else:
                    counter += 1
            idx_start.append(current_neutural + counter)
        
        ''' find rep end index '''
        idx_end = []
        for i in range(1,len(idx_neutural)):
            current_neutural = idx_neutural[i]
            idx_peak = idx_max_z[i-1]
            alpha_window = alpha[idx_peak:current_neutural, 2]
            greater15 = np.abs(alpha_window) > 15
            greater15 = np.flip(greater15.astype(np.int), axis = 0) # flip array
            # find last squat window with 5 alpha > 15
            counter = 1
            while counter < len(greater15):
                greater15_window = greater15[counter:counter+5]
                if sum(greater15_window) == 5:
                    break
                else:
                    counter += 1
            idx_end.append(current_neutural - counter)

        ''' find max angle again in y ''' 
        max_y = []
        for i in range(len(idx_neutural)-1):
            current_start = idx_start[i]
            current_end = idx_end[i]
            current_y = np.max(theta[current_start:current_end, 1])
            max_y.append(current_y)
        
        ''' find max valgus and pause time '''
        valgus_pause = []
        for i in range(len(idx_start)):
            theta_current = theta[idx_start[i]:idx_end[i],1]
            time_current = timestamp[idx_start[i]:idx_end[i]]
            # find peaks
            maxtab, mintab = peakdet(theta_current.tolist(), 0.1)
            peaks = np.concatenate((maxtab, mintab), axis = 0) 
            peaks = peaks[peaks[:,0].argsort()]

            # remove max from peak tab 
            try: 
                idx_peak_max = np.where(peaks[:,1] == np.max(theta_current))[0][0]
            except IndexError:
                idx_peak_max = peaks.shape[0]-1
            first_half = peaks[0:idx_peak_max,:]
            last_half = peaks[idx_peak_max+1:,:]
            # find pause 
            idx_pause1 = np.where(np.abs(np.diff(first_half[:,1])) < 2)[0]
            idx_pause2 = np.where(np.abs(np.diff(last_half[:,1])) < 2)[0]
            # accumulate pause time and delete
            pause_time = 0
            pause_del_idx = []
            for idx in idx_pause1:
                pause_time += time_current[int(first_half[idx + 1,0])] - time_current[int(first_half[idx,0])]
                pause_del_idx.append(idx)
                pause_del_idx.append(idx+1)
            first_half = np.delete(first_half, (pause_del_idx), axis = 0)
            
            pause_del_idx = []
            for idx in idx_pause2:
                pause_time += time_current[int(last_half[idx + 1,0])] - time_current[int(last_half[idx,0])]
                pause_del_idx.append(idx)
                pause_del_idx.append(idx+1)
            last_half = np.delete(last_half, (pause_del_idx), axis = 0)
            # find valgus 
            valgus1 = np.abs(np.diff(first_half[:,1]))
            valgus2 = np.abs(np.diff(last_half[:,1]))
            try: 
                valgus = np.max(np.concatenate((valgus1, valgus2), axis = 0))
            except ValueError:
                valgus = 0
            
            valgus_pause.append([valgus, pause_time]) 
        valgus_pause = np.matrix(valgus_pause)
        
        ''' prepare output '''
        time_start = timestamp[idx_start,0]
        time_end = timestamp[idx_end,0]
        time_down =  time_max - time_start
        time_up = time_end - time_max
        time_between = time_start[1:,0] - time_end[0:-1,0]
        time_between = np.concatenate((time_start[0] - timestamp[1], time_between),axis = 0)
        reptime = np.concatenate((time_down, time_up, time_between), axis = 1)

        angle_start = theta[idx_start,:]
        max_angle[:,0:1] = max_angle[:,0:1] - angle_start[:,0:1]
        max_angle = np.abs(max_angle)
    else: 
        pass 
    
    ''' svm predict '''
    # import trained svm model from local
    # ====================================================================================
    svm_input = np.concatenate((max_angle[:,0:2], valgus_pause[:,0]), axis = 1)
    svm_dir = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/svm/' 
    model = load(svm_dir + 'barr_svm.joblib')
    pred_label = model.predict(svm_input)
    
    if np.sum(pred_label == 'good') >= 0.8 * pred_label.shape[0]:
        form = 'good'
    else:
        form = 'bad'

    min_depth = int(np.floor(np.min(np.abs(max_angle[:,2]))))
    
    ''' make image for gui '''
    # make result text picture
    # ====================================================================================
    result_angle = "Minimum Squat Depth: " + str(min_depth)
    result_form = "Exercise Technique: " + form
    # min angle
    if min_depth >= 85: 
        img_angle = Image.new('RGB', (300, 70), color = (141,213,93)) # green
    else:
        img_angle = Image.new('RGB', (300, 70), color = (223,219,93)) # yellow
    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 24)
    d = ImageDraw.Draw(img_angle)
    d.text((15,10), result_angle, font=fnt, fill=(0, 0, 0))
    img_angle.save(os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/result_angle.png') 
    
    # form
    if form == 'good': 
        img_form = Image.new('RGB', (300, 60), color = (141,213,93)) # yellow
    else:
        img_form = Image.new('RGB', (300, 60), color = (223,219,93)) # red
    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 24)
    d = ImageDraw.Draw(img_form)
    d.text((10,10), result_form, font=fnt, fill=(0, 0, 0))
    img_form.save(os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/result_form.png') 

    # make result graph 
    # ====================================================================================
    fig_dir = os.path.dirname(os.path.realpath(__file__)) + '/gui_final/resources/'
    fig = plt.figure(figsize=(6,3))
    ax = fig.add_subplot(111)
    ax.plot(np.arange(max_angle.shape[0]), max_angle[:,2], '-go', label = 'Squat Depth')
    ax.plot(np.arange(max_angle.shape[0]), max_angle[:,1], '-ro', label = 'Instability')
    ax.plot(np.arange(max_angle.shape[0]), max_angle[:,0], '-yo', label = 'Stiffness')
    ax.legend(loc = 'right', shadow = True, fontsize = 18)
    fig.savefig(fig_dir + 'result.png')
    # plt.show()
    # ====================================================================================
    
    ''' print results '''
    print(' ')
    print('max_angle')
    print(max_angle)
    print('valgus_pause')
    print(valgus_pause)
    print('squat_time')
    print(reptime)
    print('svm prediction')
    print(pred_label)
    print('min depth')
    print(min_depth)
    print('form')
    print(form)
    return min_depth, form

if __name__ == '__main__':
    min_depth, form = analysis()

