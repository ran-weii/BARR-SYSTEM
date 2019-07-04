# ====================================================================
''' 
    BARR SYSTEM 
    Database Library for GUI 

    Inputs: 
    connection: sqlite connection object 
    table: table name in string, no space allowed, use underscore instead, ie. "Gait_1"
    header: comma separated header names in parenthsis, ie. "(Acc_X, Acc_Y, Acc_Z)"
    values: comma separated question marks in parenthsis, ie. "(?, ?, ?)"
    data: data entry in tuple, ie. (1, 2, 3)
'''
# ====================================================================

import os
import sqlite3 as sql
import numpy as np
import datetime

# ====================================================================
#   Written by Ran Wei @ rw422@rutgers.edu on December 7, 2018
#   Written by Bangaly Diane @ bd332@rutgers.edu on December 7, 2018
#=====================================================================

def headers():
    ''' define database raw and gait table column headers
    '''
    raw_header = ("(Timestamp, "
    "Acc_X1, Acc_Y1, Acc_Z1, "
    "Lin_X1, Lin_Y1, Lin_Z1, "
    "Gyr_X1, Gyr_Y1, Gyr_Z1, "
    "Euler_X1, Euler_Y1, Euler_Z1, "
    "Quat_W1, Quat_X1, Quat_Y1, Quat_Z1, "
    "Acc_X2, Acc_Y2, Acc_Z2, "
    "Lin_X2, Lin_Y2, Lin_Z2, "
    "Gyr_X2, Gyr_Y2, Gyr_Z2, "
    "Euler_X2, Euler_Y2, Euler_Z2, "
    "Quat_W2, Quat_X2, Quat_Y2, Quat_Z2 )")

    gait_header = ("(Exercise, Counter, Timestamp, "
    "Acc_X1, Acc_Y1, Acc_Z1, "
    "Acc_X2, Acc_Y2, Acc_Z2, "
    "Rotspeed_X, Rotspeed_Y, Rotspeed_Z)")

    return raw_header, gait_header


#=====================================================================
#   Basic Data Fetching & Storing Functions
#=====================================================================

def create_table(connection, table, header):
    sql_command = 'CREATE TABLE IF NOT EXISTS ' + table + ' ' + header
    
    cur = connection.cursor()
    cur.execute(sql_command)
    connection.commit()
    cur.close()


def delete_table(connection, table):
    sql_command = "DROP TABLE " + table

    cur = connection.cursor()
    cur.execute(sql_command)
    connection.commit()
    cur.close()


def data_entry(connection, table, header, data):
    ''' entery data row by row in a for loop 
    '''
    values = "(" + "?, "*header.count(',') + "?)"
    sql_command = "INSERT INTO " + table + ' ' + header + " VALUES " + values

    cur = connection.cursor()
    mat = 0
    try: 
        n_row = data.shape[0]
        mat = 1
    except AttributeError:
        pass  
    
    if mat == 1: 
        for i in range(n_row):
            cur.execute(sql_command, np.matrix.tolist(data[i,:])[0])
    else: 
        cur.execute(sql_command, data)
    
    connection.commit()
    cur.close()


def delete_all_entry(connection, table):
    sql_command = 'DELETE FROM ' + table

    cur = connection.cursor()
    cur.execute(sql_command)
    connection.commit()
    cur.close()


def data_read(connection, table, header, column, value):
    ''' reads database row wise, concatenate to columns and output np matrix
        return empty result as an empty list
    '''
    if column != '':
        sql_command = "SELECT " + header + " FROM " + table +' WHERE ' + column + ' == ' + str(value)
    else: 
        sql_command = "SELECT " + header + " FROM " + table

    cur = connection.cursor()
    cur.execute(sql_command)
    rows = cur.fetchall()
    connection.commit()
    cur.close()
    if len(rows) == 0: 
        return rows
    else: 
        data_size = len(rows[0])
        data = []
        for col in range(data_size):
            column = []
            for row in rows:
                column.append(row[col])
            data.append(column)
        data = np.transpose(np.matrix(data))

        return data


#=====================================================================
#   BARR-SYSTEM Application Specific Functions
#=====================================================================

def setup(store_dir): 
    ''' setup database registration page if not exist
        columns: (date, time, name)
    '''
    if len(store_dir) == 0:
        store_dir = os.path.dirname(os.path.realpath(__file__)) + '/output/'
    else: 
        pass 
    db_dir = store_dir + 'barr_system.db'
    conn = sql.connect(db_dir)

    # create registration page 
    header = "(Date, Time, Name)"
    create_table(conn, 'Registration', header)

    return conn 

def create_session(connection, Name, print_ln):
    ''' read last entry in registration
        enter new registration if not exist or > 2 hours
        create new raw and gait tables 
    '''
    table = 'Registration'
    header = "(Data, Time, Name)"
    row = data_read(connection, table, '*', '', '')
    row  = row.tolist() if len(row) > 0 else row

    Name = Name.replace(' ', '_')
    t_now = datetime.datetime.now() 
    if len(row) > 0: # registration page not empty 
        row = list(row[-1]) # last row
        patient_name = row[2]

        t_last = row[0] + 'x' + row[1]
        t_last = datetime.datetime.strptime(t_last, "%B_%d_%Yx%I_%M_%S%p")
        t_diff = t_now - t_last
        t_diff = t_diff.total_seconds() / 3600
        
        is_most_recent = 1 if patient_name == Name else 0

        if is_most_recent == 0: # if not most recent user
            patient_name = Name
            t_entry = t_now.strftime("%B_%d_%Yx%I_%M_%S%p")
            entry = t_entry.split('x')
            entry.append(patient_name)
            data_entry(connection, table, header, entry)
            if print_ln == 1:
                print('New session registered!')

            raw_table = patient_name + '_' + t_entry + '_' + 'Raw'
            gait_table = patient_name + '_' + t_entry + '_' + 'Gait'
        else: # you are the last entry
            if t_diff > 2: # time difference more than 2 hours
                t_entry = t_now.strftime("%B_%d_%Yx%I_%M_%S%p")
                entry = t_entry.split('x')
                entry.append(patient_name)
                data_entry(connection, table, header, entry)
                if print_ln == 1:
                    print('New session registered!')

                raw_table = patient_name + '_' + t_entry + '_' + 'Raw'
                gait_table = patient_name + '_' + t_entry + '_' + 'Gait'
            else: # time difference less than 2 hours
                t_entry = t_last.strftime("%B_%d_%Yx%I_%M_%S%p")
                if print_ln == 1:
                    print('Welcome back!')

                raw_table = patient_name + '_' + t_entry + '_' + 'Raw'
                gait_table = patient_name + '_' + t_entry + '_' + 'Gait'

    else: # page empty
        patient_name = Name
        t_entry = t_now.strftime("%B_%d_%Yx%I_%M_%S%p")
        entry = t_entry.split('x')
        entry.append(patient_name)
        data_entry(connection, table, header, entry)
        if print_ln == 1:
            print('New session registered!')

        raw_table = patient_name + '_' + t_entry + '_' + 'Raw'
        gait_table = patient_name + '_' + t_entry + '_' + 'Gait'

    raw_header, gait_header = headers()
    create_table(connection, raw_table, raw_header)
    create_table(connection, gait_table, gait_header)

    return raw_table, gait_table
    


if __name__ == '__main__':
    conn = setup('') # create registration page if not exist
    create_session(conn, 'Ran', 1)
