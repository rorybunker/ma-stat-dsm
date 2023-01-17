#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preprocess dataset_as_a_file_600_games.pkl dataset file prior to running
Stat-DSM/MA-Stat-DSM

@author: rorybunker
"""

import pickle
from numpy import array
import pandas as pd
import csv
from shapely.geometry import LineString
from shapely.geometry import Point
import psycopg2
import sys
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--label', type=str, required=False, default='effective', help='effective - for effective/ineffective label, or score - for scored/did not score label (default=effective)')
parser.add_argument('-a', '--a_list', action='store', dest='agt_list',
                    type=str, nargs='*', default=['ball', 'shooter', 'lastpasser', 'shooterdefender', 'lastpasserdefender'], help='list of agents from default=ball shooter lastpasser shooterdefender lastpasserdefender')
parser.add_argument('-ti', '--time_int', type=str, required=False, default='t2', help='t1 or t2 (default=t2)')
parser.add_argument('-p', '--xth_point', type=int, required=False, default=1, help='downsample by considering only every xth point from the trajectories (default=1, i.e., include every point)')
parser.add_argument('-g', '--game_id', type=int, required=False, default=0, help='specify a particular match id (default = all matches)')
parser.add_argument('-t', '--team', type=int, required=False, default=0, help='specify a particular team id (default = all teams)')
args, _ = parser.parse_known_args()

# map the agents provided in the arguments to integers
agent_list = args.agt_list
# agent_name_id_dict = {'ball': 0, 'shooter': 1, 'lastpasser': 2, 'shooterdefender': 3, 'lastpasserdefender': 4}
# agent_list_mapped = [agent_name_id_dict[a] for a in list(agent_list)]

downsampling_factor = args.xth_point

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

def create_agent_df(agent_name, t_interval, trajectories, downsampling_factor):
    ball_xy = []
    shooter_xy = []
    lastpasser_xy = []
    shooterdefender_xy = []
    lastpasserdefender_xy = []

    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                if point_num % downsampling_factor == 0:
                    if agent_name == 'ball':
                        ball_xy.append([t_interval.index[play_num][0],
                                        int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][0]),
                                        (trajectories[play_num][point_num][1])])
                    elif agent_name == 'shooter':
                        shooter_xy.append([t_interval.index[play_num][0],
                                                   int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][2]),
                                        (trajectories[play_num][point_num][3])])
                    elif agent_name == 'lastpasser':
                        lastpasser_xy.append([t_interval.index[play_num][0],
                                                       int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][4]),
                                        (trajectories[play_num][point_num][5])])
                    elif agent_name == 'shooterdefender':
                        shooterdefender_xy.append([t_interval.index[play_num][0],
                                                   int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][12]),
                                        (trajectories[play_num][point_num][13])])
                    elif agent_name == 'lastpasserdefender':
                        lastpasserdefender_xy.append([t_interval.index[play_num][0],
                                                       int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][14]),
                                        (trajectories[play_num][point_num][15])])

    if agent_name == 'ball':
        return pd.DataFrame([ball_xy[i][1:4]
                            for i in range(0,len(ball_xy))],
                           columns=['point','x','y'],
                           index=[ball_xy[i][0] for i in range(0,len(ball_xy))])
    elif agent_name == 'shooter':
        return pd.DataFrame([shooter_xy[i][1:4]
                               for i in range(0,len(shooter_xy))],
                           columns=['point','x','y'],
                           index=[shooter_xy[i][0]
                                  for i in range(0,len(shooter_xy))])
    elif agent_name == 'lastpasser':
        return pd.DataFrame([lastpasser_xy[i][1:4]
                               for i in range(0,len(lastpasser_xy))],
                           columns=['point','x','y'],
                           index=[lastpasser_xy[i][0]
                                  for i in range(0,len(lastpasser_xy))])
    elif agent_name == 'shooterdefender':
        return pd.DataFrame([shooterdefender_xy[i][1:4]
                               for i in range(0,len(shooterdefender_xy))],
                           columns=['point','x','y'],
                           index=[shooterdefender_xy[i][0]
                                  for i in range(0,len(shooterdefender_xy))])
    elif agent_name == 'lastpasserdefender':
        return pd.DataFrame([lastpasserdefender_xy[i][1:4]
                                   for i in range(0,len(lastpasserdefender_xy))],
                               columns=['point','x','y'],
                               index=[lastpasserdefender_xy[i][0]
                                      for i in range(0,len(lastpasserdefender_xy))])

def create_agent_ma_df(agent_list, trajectories, t_interval, downsampling_factor):
    ball_xy = []
    shooter_xy = []
    lastpasser_xy = []
    shooterdefender_xy = []
    lastpasserdefender_xy = []

    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                if point_num % downsampling_factor == 0:
                    # ball
                    if 'ball' in agent_list:
                        ball_xy.append([t_interval.index[play_num][0],
                                        int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][0]),
                                        (trajectories[play_num][point_num][1])])
                    # shooter
                    if 'shooter' in agent_list:
                        shooter_xy.append([t_interval.index[play_num][0],
                                                   int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][2]),
                                        (trajectories[play_num][point_num][3])])
                    # last passer
                    if 'lastpasser' in agent_list:
                        lastpasser_xy.append([t_interval.index[play_num][0],
                                                       int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][4]),
                                        (trajectories[play_num][point_num][5])])

                    # defender of shooter
                    if 'shooterdefender' in agent_list:
                        shooterdefender_xy.append([t_interval.index[play_num][0],
                                                   int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][12]),
                                        (trajectories[play_num][point_num][13])])

                    # defender of last passer
                    if 'lastpasserdefender' in agent_list:
                        lastpasserdefender_xy.append([t_interval.index[play_num][0],
                                                       int(point_num/downsampling_factor),
                                        (trajectories[play_num][point_num][14]),
                                        (trajectories[play_num][point_num][15])])


    ball_df = pd.DataFrame([ball_xy[i][1:4]
                            for i in range(0,len(ball_xy))],
                           columns=['point','x','y'],
                           index=[ball_xy[i][0] for i in range(0,len(ball_xy))])

    shooter_df = pd.DataFrame([shooter_xy[i][1:4]
                               for i in range(0,len(shooter_xy))],
                           columns=['point','x','y'],
                           index=[shooter_xy[i][0]
                                  for i in range(0,len(shooter_xy))])
    lastpasser_df = pd.DataFrame([lastpasser_xy[i][1:4]
                               for i in range(0,len(lastpasser_xy))],
                           columns=['point','x','y'],
                           index=[lastpasser_xy[i][0]
                                  for i in range(0,len(lastpasser_xy))])

    shooterdefender_df = pd.DataFrame([shooterdefender_xy[i][1:4]
                               for i in range(0,len(shooterdefender_xy))],
                           columns=['point','x','y'],
                           index=[shooterdefender_xy[i][0]
                                  for i in range(0,len(shooterdefender_xy))])
    lastpasserdefender_df = pd.DataFrame([lastpasserdefender_xy[i][1:4]
                               for i in range(0,len(lastpasserdefender_xy))],
                           columns=['point','x','y'],
                           index=[lastpasserdefender_xy[i][0]
                                  for i in range(0,len(lastpasserdefender_xy))])

    agent_df_list = [ball_df, shooter_df, lastpasser_df, shooterdefender_df, lastpasserdefender_df]
    agent_df_list = [df for df in agent_df_list if not df.empty]

    return [agent_list, agent_df_list]

def create_point_csv(df, label):
    # with open(name + '_point.csv', 'w') as csvfile:
    with open('point.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'tid', 'pid', 'label', 'geom'])
        row_num = 0
        traj_num = 0
        u = 0
        df_index_unique = df.index.drop_duplicates()

        for u in range(0, len(df_index_unique)):
            traj_num = df_index_unique[u]
            df_sub = df.loc[traj_num]
            for p in range(0,len(df_sub)):
                writer.writerow([row_num,
                                         u,
                                         p,
                                         label[(traj_num,)],
                                         Point(df_sub.iloc[p]['x'],
                                               df_sub.iloc[p]['y'])])
                row_num += 1

def create_trajectory_csv(df, label):
    # with open(name + '_trajectory.csv', 'w') as csvfile:
    with open('trajectory.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'tid', 'label','geom'])
        df_index_unique = df.index.drop_duplicates()
        for u in range(0, len(df_index_unique)):
            traj_num = df_index_unique[u]
            df_sub = df.loc[traj_num]
            if len(df_sub) > 0:
                writer.writerow([u, u, label[u],
                                 LineString((df_sub.iloc[:,1:3]).to_numpy())])

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
                    writer.writerow([row_num,
                                             agt,
                                             u,
                                             int(df_sub.iloc[p]['point']),
                                             int(label[(traj_num,)]),
                                             Point(df_sub.iloc[p]['x'],
                                                   df_sub.iloc[p]['y'])])
                    row_num += 1

def create_trajectory_ma_csv(agent_df_list, label):
    with open('trajectory_ma.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'aid', 'tid', 'label','geom'])
        row_num = 0

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

# def import_point_table_into_postgres(os, filename, path):
#     conn = connect(param_dic)
#     cur = conn.cursor()
#     copy_sql = """
#                COPY point(id, tid, pid, label, geom)
#                FROM '""" + os.getcwd() + '/' + filename + """.csv'
#                DELIMITER ','
#                CSV HEADER;
#                """
#     with open(path, 'r') as f:
#         cur.copy_expert(sql=copy_sql, file=f)
#         conn.commit()
#         cur.close()

# def import_traj_table_into_postgres(os, filename, path):
#     conn = connect(param_dic)
#     cur = conn.cursor()
#     copy_sql = """
#                COPY trajectory(id, tid, label, geom)
#                FROM '""" + os.getcwd() + '/' + filename + """.csv'
#                DELIMITER ','
#                CSV HEADER;
#                """
#     with open(path, 'r') as f:
#         cur.copy_expert(sql=copy_sql, file=f)
#         conn.commit()
#         cur.close()

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
    # label data is in the format [label_i,t1,t2,score,shooterID,passerID,team_ID]
    # index: corresponding to the file at root\nba_attack2\nba_datalength.csv

    trajectories = array(data[0], dtype=object)
    label = array(data[1], dtype=object)
    indices = array(data[2].astype(int), dtype=object)
    game_id = array(data[3].astype(int), dtype=object)
    quarter = array(data[4].astype(int), dtype=object)

    label_df = pd.DataFrame(label, index=indices)
    game_id_df = pd.DataFrame(game_id, index=indices).rename(columns={0:'game_id'})
    quarter_df = pd.DataFrame(quarter, index=indices).rename(columns={0:'quarter'})

    combined_df = pd.concat([label_df, game_id_df, quarter_df], axis=1, join='inner')

    # subset the data if team_id is specified above
    if args.team != 0:
        combined_df = combined_df[(combined_df[6] == args.team)]

    if args.game_id != 0:
        combined_df = combined_df[(combined_df['game_id'] == args.game_id)]

    effective = combined_df.iloc[:,0]

    # convert 2- and 3-pointer score variable to binary 1/0 = score/didn't score
    combined_df.iloc[combined_df[3]==2, 3] = 1.0
    combined_df.iloc[combined_df[3]==3, 3] = 1.0
    score = combined_df.iloc[:,3]

    if args.label == 'score':
        label = score
    elif args.label == 'effective':
        label = effective

    if args.time_int == 't1':
        t1 = combined_df.iloc[:,1]
        t_interval = combined_df.iloc[:,2][t1>0]
    elif args.time_int == 't2':
        t2 = combined_df.iloc[:,2]
        t_interval = combined_df.iloc[:,2][t2>0]

    if run_type == 'statdsm':
        # create dataframe for the specified agent
        agent_df = create_agent_df(agent_list[0], t_interval, trajectories, downsampling_factor)
  
        # create point and trajectory csv files
        # create_point_csv(agent_df, agent_list[0], label)
        # create_trajectory_csv(agent_df, agent_list[0], label)
        create_point_csv(agent_df, label)
        create_trajectory_csv(agent_df, label)

        # delete the existing table rows in the postgres database tables
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates')

        # import the newly created csv files into postgres database
        # import_point_table_into_postgres(os, agent_list[0] + '_point', path)
        # import_traj_table_into_postgres(os, agent_list[0] + '_trajectory', path)
        import_point_table_into_postgres(os, 'point', path)
        import_traj_table_into_postgres(os, 'trajectory', path)
        
        # print('Final # of plays in dataset: ' + str(len(pd.read_csv(agent_list[0] + '_trajectory.csv'))))
        print('Final # of plays in dataset: ' + str(len(pd.read_csv('trajectory.csv'))))
        sys.exit(0)

    elif run_type == 'mastatdsm':
        # create dataframe for the specified agents
        agent_df_list = create_agent_ma_df(agent_list, trajectories, t_interval, downsampling_factor)
        
        # create ma point and trajectory csv files
        create_point_ma_csv(agent_df_list[1], label)
        create_trajectory_ma_csv(agent_df_list[1], label)

        # delete the existing table rows in the postgres database tables
        delete_table_rows('point_ma')
        delete_table_rows('trajectory_ma')
        delete_table_rows('candidates')

        # import the newly created csv files into postgres database
        import_point_ma_table_into_postgres(os, 'point_ma', path)
        import_traj_ma_table_into_postgres(os, 'trajectory_ma', path)

        print('Final # of rows in dataset: ' + str(len(pd.read_csv('trajectory_ma.csv'))))
        print('Final # of plays (distinct tids) in dataset: ' + str(len(pd.unique(pd.read_csv('trajectory_ma.csv')['tid']))))
        sys.exit(0)

if __name__ == '__main__':
    main()
