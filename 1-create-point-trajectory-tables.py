#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import 600-game NBA dataset .plk file, export point-level and trajectory-level 
csv files for each agent which are then created in the PostgreSQL database, 
which then are inputs to the Stat-DSM algorithm.

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

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

def create_agent_df(agent_name, t_interval, trajectories):
    ball_xy = []
    offense_xy_shooter = []
    offense_xy_last_passer = []
    defense_xy_shooter = []
    defense_xy_last_passer = []

    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                if agent_name == 'ball':
                    ball_xy.append([t_interval.index[play_num][0], 
                                    point_num,
                                    (trajectories[play_num][point_num][0]),
                                    (trajectories[play_num][point_num][1])])
                elif agent_name == 'shooter':
                    offense_xy_shooter.append([t_interval.index[play_num][0], 
                                               point_num,
                                    (trajectories[play_num][point_num][2]),
                                    (trajectories[play_num][point_num][3])])
                elif agent_name == 'lastpasser':
                    offense_xy_last_passer.append([t_interval.index[play_num][0], 
                                                   point_num,
                                    (trajectories[play_num][point_num][4]),
                                    (trajectories[play_num][point_num][5])])
                elif agent_name == 'shooterdefender':
                    defense_xy_shooter.append([t_interval.index[play_num][0], 
                                               point_num,
                                    (trajectories[play_num][point_num][12]),
                                    (trajectories[play_num][point_num][13])])
                elif agent_name == 'lastpasserdefender':
                    defense_xy_last_passer.append([t_interval.index[play_num][0], 
                                                   point_num,
                                    (trajectories[play_num][point_num][14]),
                                    (trajectories[play_num][point_num][15])])
                    
    if agent_name == 'ball':            
        return pd.DataFrame([ball_xy[i][1:4] 
                            for i in range(0,len(ball_xy))], 
                           columns=['point','x','y'], 
                           index=[ball_xy[i][0] for i in range(0,len(ball_xy))])
    elif agent_name == 'shooter':
        return pd.DataFrame([offense_xy_shooter[i][1:4] 
                               for i in range(0,len(offense_xy_shooter))], 
                           columns=['point','x','y'], 
                           index=[offense_xy_shooter[i][0] 
                                  for i in range(0,len(offense_xy_shooter))])
    elif agent_name == 'lastpasser':
        return pd.DataFrame([offense_xy_last_passer[i][1:4] 
                               for i in range(0,len(offense_xy_last_passer))], 
                           columns=['point','x','y'], 
                           index=[offense_xy_last_passer[i][0] 
                                  for i in range(0,len(offense_xy_last_passer))])
    elif agent_name == 'shooterdefender':
        return pd.DataFrame([defense_xy_shooter[i][1:4] 
                               for i in range(0,len(defense_xy_shooter))], 
                           columns=['point','x','y'], 
                           index=[defense_xy_shooter[i][0] 
                                  for i in range(0,len(defense_xy_shooter))])
    elif agent_name == 'lastpasserdefender':
        return pd.DataFrame([defense_xy_last_passer[i][1:4] 
                                   for i in range(0,len(defense_xy_last_passer))], 
                               columns=['point','x','y'], 
                               index=[defense_xy_last_passer[i][0] 
                                      for i in range(0,len(defense_xy_last_passer))])
    
def create_point_csv(df, name, effective):
    with open(name + '_point.csv', 'w') as csvfile:
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
                                         int(df_sub.iloc[1]['point']),
                                         effective[(traj_num,)],
                                         Point(df_sub.iloc[p]['x'],
                                               df_sub.iloc[p]['y'])])
                row_num += 1

def create_trajectory_csv(df, name, effective):
    with open(name + '_trajectory.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'tid', 'label','geom'])
        df_index_unique = df.index.drop_duplicates()
        for u in range(0, len(df_index_unique)):
            traj_num = df_index_unique[u]
            df_sub = df.loc[traj_num]
            if len(df_sub) > 0:
                writer.writerow([u, u, effective[u],
                                 LineString((df_sub.iloc[:,1:3]).to_numpy())])

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
    sql = """DELETE FROM """ + table_name +""";"""
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def import_point_table_into_postgres(filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY point(id, tid, pid, label, geom)
               FROM '/Users/rorybunker/""" + filename + """.csv' 
               DELIMITER ',' 
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def import_traj_table_into_postgres(filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY trajectory(id, tid, label, geom)
               FROM '/Users/rorybunker/""" + filename + """.csv' 
               DELIMITER ',' 
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()
        
def main():
    path = '/Users/rorybunker/dataset_as_a_file_600_games.pkl'
    f = open(path, 'rb')
    data = pickle.load(f)
    
    # data is in the format [feature, label, index]
    # feature: Position(23:OFxy,DFxy,Ballxyz), player_ID(10), Clock, ShotClock, 
    # Ball_OF, Ball_Hold
    # label: effective attack (1) or ineffective attack (0), T1, T2, score or not
    # index: corresponding to the file at root\nba_attack2\nba_datalength.csv

    indices = array(data[2].astype(int), dtype=object)
    trajectories = array(data[0], dtype=object)
    label = array(data[1], dtype=object)
    
    id_team_df = pd.read_csv('id_team.csv')
    
    #pd.merge(product,customer,on='Product_ID',how='left')
    
    label_df = pd.DataFrame(label, index=indices)
    # or if you want to select specific teams e.g. Golden state warriors and 
    # Cleveland: 1610612739, Golden State Warriors 1610612744
    label_df= label_df[(label_df[6]==1610612739)]
    # label_df = label_df[0:1000]
    
    # label data is in the format [label_i,t1,t2,score,shooterID,passerID,team_ID]
    effective = label_df.iloc[:,0]
    
    # specify the agent - 'ball', 'shooter', 'shooterdefender', 'lastpasser' 
    # or 'lastpasserdefender'
    agent_name = 'shooter'
    # specify the time interval - t1 or t2
    time_interval = 't2'
    
    if time_interval == 't1':
        t_interval = label_df.iloc[:,1]
    elif time_interval == 't2':
        t2 = label_df.iloc[:,2]
        t_interval = label_df.iloc[:,2][t2>0]
    
    # create dataframe for agent with time interval specified 
    agent_df = create_agent_df(agent_name, t_interval, trajectories)
    
    # create point and trajectory csv files
    create_point_csv(agent_df, agent_name, effective)
    create_trajectory_csv(agent_df, agent_name, effective)
    
    # delete the existing  table rows in the postgres database tables
    delete_table_rows('point')
    delete_table_rows('trajectory')
    delete_table_rows('candidates') 
    # import the newly created csv files into postgres database
    import_point_table_into_postgres(agent_name + '_point', path)
    import_traj_table_into_postgres(agent_name + '_trajectory', path)
    
if __name__ == '__main__':
    main()
