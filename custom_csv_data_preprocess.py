#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preprocess other csv files prior to running Stat-DSM/MA-Stat-DSM

@author: rorybunker
"""

import pandas as pd
import psycopg2
import sys
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--downsampling', type=int, required=False, default=1, help='downsample by considering only every ith point from the trajectories (default=1, i.e., include every point)')
args, _ = parser.parse_known_args()

# Write the arguments to a file
with open('args.txt', 'w') as f:
    f.write(str(args.downsampling) + '\n')

downsampling_factor = args.downsampling

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    
    return conn

def delete_table_rows(table_name):
    conn = connect(param_dic)
    cur = conn.cursor()
    sql = """DELETE FROM """ + table_name + """;"""
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def import_point_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY point(id, tid, pid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def import_traj_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY trajectory(id, tid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def import_point_ma_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY point_ma(id, aid, tid, pid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def import_traj_ma_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY trajectory_ma(id, aid, tid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def main():
    path = os.getcwd() + '/ma_stat_dsm.py'

    if os.path.getmtime('trajectory_ma.csv') > os.path.getmtime('trajectory.csv'):
        len_agent_ids = len(pd.unique(pd.read_csv('trajectory_ma.csv')['aid']))
    elif os.path.getmtime('trajectory.csv') > os.path.getmtime('trajectory_ma.csv'):
        len_agent_ids = 1

    if len_agent_ids == 1: # statdsm
        # delete the existing table rows in the postgres database tables
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates')

        # import the newly created csv files into postgres database
        import_point_table_into_postgres(os, 'point', path)
        import_traj_table_into_postgres(os, 'trajectory', path)

        print('Final # of tids/distinct tids in dataset: ' + str(len(pd.read_csv('trajectory.csv'))))
        sys.exit(0)

    elif len_agent_ids > 1: # mastatdsm
        # delete the existing table rows in the postgres database tables
        delete_table_rows('point_ma')
        delete_table_rows('trajectory_ma')
        delete_table_rows('candidates')

        # import the newly created csv files into postgres database
        import_point_ma_table_into_postgres(os, 'point_ma', path)
        import_traj_ma_table_into_postgres(os, 'trajectory_ma', path)
        
        print('Final # of tids in dataset: ' + str(len(pd.read_csv('trajectory_ma.csv'))))
        print('Final # of istinct tids in dataset: ' + str(len(pd.unique(pd.read_csv('trajectory_ma.csv')['tid']))))
        sys.exit(0)

if __name__ == '__main__':
    main()