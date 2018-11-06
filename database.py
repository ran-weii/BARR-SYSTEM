# ====================================================================
''' 
    BARR SYSTEM 
    Database Library 

    Inputs: 
    connection: sqlite connection object 
    table: table name in string, no space allowed, use underscore instead, ie. "Gait_1"
    header: comma separated header names in parenthsis, ie. "(Acc_X, Acc_Y, Acc_Z)"
    values: comma separated question marks in parenthsis, ie. "(?, ?, ?)"
    data: data entry in tuple, ie. (1, 2, 3)
'''
# ====================================================================
import sqlite3 as sql
import numpy as np
# ====================================================================
# Written by Ran Wei @ rw422@rutgers.edu on October 26, 2018 
# Written by Bangaly Diane @ bd332@rutgers.edu
#=====================================================================

def create_table(connection, table, header):
    sql_command = 'CREATE TABLE IF NOT EXISTS ' + table + '' + header

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


def data_entry(connection, table, header, values, data):
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


def data_read(connection, table, header):
    # reads database row wise, concatenate to columns and output np matrix
    sql_command = "SELECT " + header + " FROM " + table

    cur = connection.cursor()
    cur.execute(sql_command)
    rows = cur.fetchall()
    connection.commit()
    cur.close()

    data_size = len(rows[0])
    data = []
    for col in range(data_size):
        column = []
        for row in rows:
            column.append(row[col])
        data.append(column)
    data = np.transpose(np.matrix(data))

    return data


if __name__ == '__main__':
    store_dir = '/Users/apple/Documents/Documents/GitHub/BARR-SYSTEM/output/'
    db_dir = store_dir + 'barr_system.db'
    conn = sql.connect(db_dir)
    data_read(conn, 'Sensor_1', '*')
    conn.close()