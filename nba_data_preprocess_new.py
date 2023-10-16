#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preprocess NBA dataset dataset_as_a_file_600_games.pkl file prior to running Stat-DSM/MA-Stat-DSM

@author: rorybunker
"""

import pickle
import pandas as pd
import csv
from shapely.geometry import LineString
from shapely.geometry import Point
import psycopg2
import sys
import argparse
import os
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--label', type=str, required=False, default='effective', help='effective - for effective/ineffective label, score - for scored/did not score label, attempt - for attempted shot/did not attempt shot label (default=effective)')
parser.add_argument('-a', '--a_list', action='store', dest='agt_list',
                    type=str, nargs='*', default=['ball', 'shooter', 'lastpasser', 'shooterdefender', 'lastpasserdefender'], help='list of agents from default=ball shooter lastpasser shooterdefender lastpasserdefender')
parser.add_argument('-i', '--time_int', type=str, required=False, default='T2', help='T1 or T2 (default=T2)')
parser.add_argument('-g', '--game_id', type=int, required=False, default=0, help='specify a particular match id (default = all matches)')
parser.add_argument('-t', '--team', type=int, required=False, default=0, help='specify a particular team id (default = all teams)')
args, _ = parser.parse_known_args()

# Write the arguments to a file
with open('args.txt', 'w') as f:
    f.write(str(args.team) + '\n')
    f.write(str(args.game_id) + '\n')
    # f.write(str(args.downsampling) + '\n')

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

agent_mapping = {
    'ball': [0, 1],
    'shooter': [2, 3],
    'lastpasser': [4, 5],
    'shooterdefender': [12, 13],
    'lastpasserdefender': [14, 15]
}

def create_agent_ma_df(combined_df):
    df_list = []

    for name in args.agt_list:
        if name not in agent_mapping:
            continue
        
        agent_xy = []  # Initialize the agent_xy list here, outside of the loop
        agent_indices = agent_mapping[name]  

        if args.time_int == 'T2':
            t_interval = 'T2'
        elif args.time_int == 'T1':
            t_interval = 'T1'
        
        tid = 0 # tid to start from 0 for postgres
        for index, row in combined_df.iterrows():
            t_interval_start = int(row[t_interval])
            traj_length_value = row['traj_length']
            
            p = 0
            for t in range(t_interval_start, traj_length_value):
                
                agent_coords = row.trajectories[t]
                # remove shot clock and quarter clock (last two elements)
                # shot_clock = agent_coords[-2]
                # qtr_clock = agent_coords[-1]
                agent_coords = agent_coords[:-2]

                # Initialize agent_xy list only once for each row
                agent_row = [index, tid, t, p, args.agt_list.index(name), agent_coords[agent_indices[0]], agent_coords[agent_indices[1]]]
                agent_xy.append(agent_row)  # Append the agent_row to agent_xy list

                p += 1
            
            tid += 1

        df_list.append(pd.DataFrame(agent_xy, columns=['play_index', 'tid', 't', 'pid', 'aid', 'x', 'y']))  # Append to df_list
    
    return pd.concat(df_list, ignore_index=True)  # Concatenate the list of DataFrames and return

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

def import_point_ma_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY point_ma(id, aid, tid, pid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    try:
        with open(path, 'r') as f:
            cur.copy_expert(sql=copy_sql, file=f)
            conn.commit()
    except Exception as e:
        print("Error during import (point_ma):", e)
        conn.rollback()  # Rollback the transaction in case of error
    finally:
        cur.close()
        conn.close()

def import_traj_ma_table_into_postgres(os, filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY trajectory_ma(id, aid, tid, label, geom)
               FROM '""" + os.getcwd() + '/' + filename + """.csv'
               DELIMITER ','
               CSV HEADER;
               """
    try:
        with open(path, 'r') as f:
            cur.copy_expert(sql=copy_sql, file=f)
            conn.commit()
    except Exception as e:
        print("Error during import (trajectory_ma):", e)
        conn.rollback()  # Rollback the transaction in case of error
    finally:
        cur.close()
        conn.close()

def main():
    # \\spica\workspace4\fujii\work\team_representation_data\data\all_attacks2_nba_games_30_VTEP_val5Fs10\dataset_as_a_file_600_games.pkl
    path = os.getcwd() + '/dataset_as_a_file_600_games.pkl'

    f = open(path, 'rb')
    data = pickle.load(f)

    # data = [feature, label, index, game_id, quarter]
    # Position(23:OFxy,DFxy,Ballxyz), player_ID(10), Clock, ShotClock, Ball_OF, Ball_Hold
    # label data is in the format [label_i,t1,t2,shot attempt, score, 2 or 3 point,shooterID,passerID,team_ID]
    # index: corresponding to the file at root\nba_attack2\nba_datalength.csv
    
    trajectories, label, indices, game_id, quarter = np.array(data[0], dtype=object), np.array(data[1], dtype=object), np.array(data[2].astype(int), dtype=object), np.array(data[3].astype(int), dtype=object), np.array(data[4].astype(int), dtype=object)
    trajectories_df, label_df, game_id_df, quarter_df = [pd.DataFrame(data, index=indices) for data in (trajectories, label, game_id, quarter)]
    
    # join dataframes on index
    combined_df = pd.concat([label_df, game_id_df, quarter_df, trajectories_df], axis=1, join='inner')
    
    # set column names
    combined_df.columns = ['effectiveness', 'T1', 'T2', 'shot_attempt','score', '2_or_3_point', 'ID1', 'ID2', 'team_id', 'game_id', 'quarter','trajectories']
    
    # subset the data if team_id is specified above
    if args.team != 0:
        combined_df = combined_df[(combined_df['team_id'] == float(args.team))]
    # also subset the data if game_id is specified above
    if args.game_id != 0:
        combined_df = combined_df[(combined_df['game_id'] == args.game_id)]
    
    # columns 3,4,5 are shot attempt, score, 2 or 3 point.
    combined_df['score_binary'] = np.where(combined_df['score'] == 0, 0, 1)
    combined_df['attempt_binary'] = np.where(combined_df['shot_attempt'] == 0, 0, 1)
    
    # create label variable
    if args.label == 'score':
        combined_df['label'] = combined_df['score_binary']
    elif args.label == 'effective':
        combined_df['label'] = combined_df['effectiveness']
    elif args.label == 'attempt':
        combined_df['label'] = combined_df['attempt_binary']

    # remove where T2 = 0
    combined_df = combined_df[combined_df['T2']>0]

    combined_df['traj_length'] = 0  # Create the 'traj_length' column and initialize all values to 0

    # create a column for the length of the trajectory (to get time in seconds, divide this by 10)
    for index, row in combined_df.iterrows():
        traj_length = len(row['trajectories'])
        combined_df.at[index, 'traj_length'] = traj_length
    # combined_df['traj_length'] = [len(row['trajectories']) for index, row in combined_df.iterrows()]
    combined_df.to_csv('combined_df_final.csv')

    # create dataframe for the specified agents
    agent_df_list = create_agent_ma_df(combined_df)
    label_only_df = combined_df['label']
    
    agent_df_list = agent_df_list.merge(label_only_df, left_on='play_index', right_index=True, how='left')
    
    point_ma_df = pd.DataFrame({
        'id': agent_df_list.index,
        'aid': agent_df_list['aid'],
        'tid': agent_df_list['tid'],
        'pid': agent_df_list['pid'],
        'label': agent_df_list['label'],
        'geom': agent_df_list.apply(lambda row: Point(row['x'], row['y']), axis=1)
    })

    point_ma_df.to_csv('point_ma.csv', index=False)

    # Group by 'tid' and 'aid', aggregate 'geom' points as a list
    grouped_points = point_ma_df.groupby(['tid', 'aid', 'label'])['geom'].apply(list).reset_index()

    # Create 'geom' column by applying LineString constructor to 'geom' lists
    grouped_points['geom'] = grouped_points['geom'].apply(lambda points: LineString(points))

    # Select only required columns: 'tid', 'aid', and 'geom'
    traj_ma_df = grouped_points[['aid', 'tid', 'label', 'geom']]

    # Convert label to string in traj_ma_df
    traj_ma_df['label'] = traj_ma_df['label'].astype(str)

    # Add 'id' column and set it as the first column
    traj_ma_df.insert(0, 'id', range(len(traj_ma_df)))

    # Save the traj_ma_df to CSV
    traj_ma_df.to_csv('trajectory_ma.csv', index=False)
    
    index_mapping = agent_df_list[['play_index', 'aid', 'tid']].drop_duplicates().rename(columns={'play_index': 'original_index'})
    index_mapping.to_csv('index_mapping.csv', index=False)

    # delete the existing table rows in the postgres database tables
    delete_table_rows('point_ma')
    delete_table_rows('trajectory_ma')
    delete_table_rows('candidates')

    # import the newly created csv files into postgres database
    import_point_ma_table_into_postgres(os, 'point_ma', path)
    import_traj_ma_table_into_postgres(os, 'trajectory_ma', path)
    
    print('Final # of agent tids in dataset: ' + str(len(pd.read_csv('trajectory_ma.csv'))))
    print('Final # of plays (distinct tids) in dataset: ' + str(len(pd.unique(pd.read_csv('trajectory_ma.csv')['tid']))))
    
    sys.exit(0)

if __name__ == '__main__':
    main()
