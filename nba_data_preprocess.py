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
parser.add_argument('-i', '--time_int', type=str, required=False, default='t2', help='t1 or t2 (default=t2)')
parser.add_argument('-d', '--downsampling', type=int, required=False, default=1, help='downsample by considering only every xth point from the trajectories (default=1, i.e., include every point)')
parser.add_argument('-g', '--game_id', type=int, required=False, default=0, help='specify a particular match id (default = all matches)')
parser.add_argument('-t', '--team', type=int, required=False, default=0, help='specify a particular team id (default = all teams)')
args, _ = parser.parse_known_args()

# Write the arguments to a file
with open('args.txt', 'w') as f:
    f.write(str(args.team) + '\n')
    f.write(str(args.game_id) + '\n')

agent_list = args.agt_list
downsampling_factor = args.downsampling

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

def create_agent_df(agent_name, t_interval, trajectories, downsampling_factor):
    agent_mapping = {
        'ball': [0, 1],
        'shooter': [2, 3],
        'lastpasser': [4, 5],
        'shooterdefender': [12, 13],
        'lastpasserdefender': [14, 15]
    }
    agent_xy = []
    for play_num in range(0, len(t_interval)):
        for point_num in range(0, len(trajectories[play_num])):
            if point_num % downsampling_factor == 0:
                x, y = trajectories[play_num][point_num][agent_mapping[agent_name]]
                agent_xy.append([t_interval.index[play_num][0], int(point_num/downsampling_factor), x, y])

    return pd.DataFrame([agent_xy[i][1:4] for i in range(0, len(agent_xy))],
                       columns=['point', 'x', 'y'],
                       index=[agent_xy[i][0] for i in range(0, len(agent_xy))])

def create_agent_ma_df(agent_list, trajectories, t_interval, downsampling_factor):
    df_list = []

    for name in ['ball', 'shooter', 'lastpasser', 'shooterdefender', 'lastpasserdefender']:
        if name not in agent_list:
            continue
        
        agent_xy = []
        index = [0, 2, 4, 12, 14][['ball', 'shooter', 'lastpasser', 'shooterdefender', 'lastpasserdefender'].index(name)]
        
        for play_num in range(len(t_interval)):
            for point_num in range(0, len(trajectories[play_num]), downsampling_factor):
                agent_xy.append([t_interval.index[play_num][0], int(point_num/downsampling_factor),
                                 (trajectories[play_num][point_num][index]),
                                 (trajectories[play_num][point_num][index+1])])
        
        df = pd.DataFrame([agent_xy[i][1:4] for i in range(len(agent_xy))],
                         columns=['point', 'x', 'y'],
                         index=[agent_xy[i][0] for i in range(len(agent_xy))])
        
        df_list.append(df)
    
    return [agent_list, df_list]

def create_point_csv(agent_df, label):
    with open('point.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'tid', 'pid', 'label', 'geom'])
        row_num = 0
        traj_num = 0
        u = 0
        df_index_unique = agent_df.index.drop_duplicates()

        for u in range(0, len(df_index_unique)):
            traj_num = df_index_unique[u]
            df_sub = agent_df.loc[traj_num]
            
            for p in range(0,len(df_sub)):
                writer.writerow([row_num,u,p,label[(traj_num,)],Point(df_sub.iloc[p]['x'],df_sub.iloc[p]['y'])])
                row_num += 1
            
def create_trajectory_csv(df, label):
    with open('trajectory.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'tid', 'label','geom'])
        df_index_unique = df.index.drop_duplicates()
        index_mapping = []

        for u in range(0, len(df_index_unique)):
            traj_num = df_index_unique[u]
            df_sub = df.loc[traj_num]
            index_mapping.append([traj_num, u])

            if len(df_sub) > 0:
                writer.writerow([u, u, label[u],
                                 LineString((df_sub.iloc[:,1:3]).to_numpy())])

    with open('index_mapping.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['original_index', 'tid'])
        for mapping in index_mapping:
            writer.writerow(mapping)

def create_point_ma_csv(agent_df_list, label):
    with open('point_ma.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'aid', 'tid', 'pid', 'label', 'geom'])
        row_num = 0

        for agt in range(0,len(agent_df_list)):
            df = agent_df_list[agt]
            traj_num = 0
            u = 0
            df_index_unique = df.index.drop_duplicates()

            for u in range(0, len(df_index_unique)):
                traj_num = df_index_unique[u]
                df_sub = df.loc[traj_num]
                
                for p in range(0,len(df_sub)):
                    writer.writerow([row_num,agt,u,int(df_sub.iloc[p]['point']),int(label[(traj_num,)]),Point(df_sub.iloc[p]['x'],df_sub.iloc[p]['y'])])
                    row_num += 1

def create_trajectory_ma_csv(agent_df_list, label):
    with open('trajectory_ma.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'aid', 'tid', 'label','geom'])
        row_num = 0
        index_mapping = []

        for agt in range(0,len(agent_df_list)):
            df = agent_df_list[agt]
            df_index_unique = df.index.drop_duplicates()

            for u in range(0, len(df_index_unique)):
                traj_num = df_index_unique[u]
                df_sub = df.loc[traj_num]
                
                if len(df_sub) > 0:
                    writer.writerow([row_num, agt, u, int(label[u]),
                                         LineString((df_sub.iloc[:,1:3]).to_numpy())])
                row_num += 1

                index_mapping.append([traj_num, agt, u])

    with open('index_mapping.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['original_index', 'aid', 'tid'])
        for mapping in index_mapping:
            writer.writerow(mapping)

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
    # \\spica\workspace4\fujii\work\team_representation_data\data\all_attacks2_nba_games_30_VTEP_val5Fs10\dataset_as_a_file_600_games.pkl
    path = os.getcwd() + '/dataset_as_a_file_600_games.pkl'

    if len(agent_list) > 1:
        run_type = 'mastatdsm'
    elif len(agent_list) == 1:
        run_type = 'statdsm'

    f = open(path, 'rb')
    data = pickle.load(f)

    # data = [feature, label, index, game_id, quarter]
    # feature: Position(23:OFxy,DFxy,Ballxyz), player_ID(10), Clock, ShotClock,
    # Ball_OF, Ball_Hold
    # label data is in the format [label_i,t1,t2,shot attempt, score, 2 or 3 point,shooterID,passerID,team_ID]
    # index: corresponding to the file at root\nba_attack2\nba_datalength.csv

    trajectories, label, indices, game_id, quarter = np.array(data[0], dtype=object), np.array(data[1], dtype=object), np.array(data[2].astype(int), dtype=object), np.array(data[3].astype(int), dtype=object), np.array(data[4].astype(int), dtype=object)

    label_df, game_id_df, quarter_df = [pd.DataFrame(data, index=indices) for data in (label, game_id, quarter)]

    # join dataframes on index
    combined_df = pd.concat([label_df, game_id_df, quarter_df], axis=1, join='inner')
    # set column names
    combined_df.columns = ['effectiveness', 'T1', 'T2', 'shot_attempt','score', '2_or_3_point', 'ID1', 'ID2', 'team_id', 'game_id', 'quarter']
    
    # subset the data if team_id is specified above
    if args.team != 0:
        combined_df = combined_df[(combined_df['team_id'] == float(args.team))]
    
    if args.game_id != 0:
        combined_df = combined_df[(combined_df['game_id'] == args.game_id)]
    
    # columns 3,4,5 are shot attempt, score, 2 or 3 point.
    combined_df['score_binary'] = np.where(combined_df['score'] == 0, 0, 1)
    combined_df['attempt_binary'] = np.where(combined_df['shot_attempt'] == 0, 0, 1)

    if args.label == 'score':
        label = combined_df['score_binary']
    elif args.label == 'effective':
        label = combined_df['effectiveness']
    elif args.label == 'attempt':
        label = combined_df['attempt_binary']
    
    if args.time_int == 't1':
        t_interval = combined_df[combined_df['T1']>0]['T1']
    elif args.time_int == 't2':
        t_interval = combined_df[combined_df['T2']>0]['T2']
    
    combined_df.to_csv('combined_df_final.csv')

    if run_type == 'statdsm':
        # create dataframe for the specified agent
        agent_df = create_agent_df(agent_list[0], t_interval, trajectories, downsampling_factor)
        
        # create point.csv, trajectory.csv, and index_mapping.csv files
        create_point_csv(agent_df, label)
        create_trajectory_csv(agent_df, label)

        # delete the existing table rows in the postgres database tables
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates')

        # import the newly created csv files into postgres database
        import_point_table_into_postgres(os, 'point', path)
        import_traj_table_into_postgres(os, 'trajectory', path)

        print('Final # of plays (tids/distinct tids) in dataset: ' + str(len(pd.read_csv('trajectory.csv'))))
        sys.exit(0)

    elif run_type == 'mastatdsm':
        # create dataframe for the specified agents
        agent_df_list = create_agent_ma_df(agent_list, trajectories, t_interval, downsampling_factor)

        # create point_ma.csv, trajectory_ma.csv, and index_mapping.csv files
        create_point_ma_csv(agent_df_list[1], label)
        create_trajectory_ma_csv(agent_df_list[1], label)

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
