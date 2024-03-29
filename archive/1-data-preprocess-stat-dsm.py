#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import 600-game NBA dataset .pkl file, export point-level and trajectory-level 
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

def create_agent_df(agent_name, t_interval, trajectories, num_include):
    ball_xy = []
    offense_xy_shooter = []
    offense_xy_last_passer = []
    defense_xy_shooter = []
    defense_xy_last_passer = []

    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                if point_num % num_include == 0:
                    if agent_name == 'ball':
                        ball_xy.append([t_interval.index[play_num][0], 
                                        int(point_num/num_include),
                                        (trajectories[play_num][point_num][0]),
                                        (trajectories[play_num][point_num][1])])
                    elif agent_name == 'shooter':
                        offense_xy_shooter.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
                                        (trajectories[play_num][point_num][2]),
                                        (trajectories[play_num][point_num][3])])
                    elif agent_name == 'lastpasser':
                        offense_xy_last_passer.append([t_interval.index[play_num][0], 
                                                       int(point_num/num_include),
                                        (trajectories[play_num][point_num][4]),
                                        (trajectories[play_num][point_num][5])])
                    elif agent_name == 'shooterdefender':
                        defense_xy_shooter.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
                                        (trajectories[play_num][point_num][12]),
                                        (trajectories[play_num][point_num][13])])
                    elif agent_name == 'lastpasserdefender':
                        defense_xy_last_passer.append([t_interval.index[play_num][0], 
                                                       int(point_num/num_include),
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
                                         #int(df_sub.iloc[1]['point']),
                                         p,
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
    # ---- DATA PRE-PROCESSING PARAMETERS ----
    # label variable definition - 'score' for score/did not score or 'effective' for effective/ineffective play
    label_variable = 'effective'    
    # specify the agent: 'ball', 'shooter', 'shooterdefender', 'lastpasser' or 'lastpasserdefender'
    agent_name = 'shooter'
    # specify the time interval - t1 or t2
    time_interval = 't2'
    # number of points to include, e.g., if num_include = 3, include every third point, etc.
    num_include = 5
    # 'statdsm' or 'mastatdsm'
    run_type = 'statdsm' # to add: run_type = 'mastatdsm'
    # run for smaller subset - useful for testing. If initial_num_rows = -1, run on entire dataset
    initial_num_rows = -1 
    # team ids are in id_team.csv. Cleveland 1610612739, GSW 1610612744. If team_id = 0, run for all teams
    team_id = 1610612744 
    
    path = '/Users/rorybunker/dataset_as_a_file_600_games.pkl'
    f = open(path, 'rb')
    data = pickle.load(f)
    
    # data is in the format [feature, label, index]
    # feature: Position(23:OFxy,DFxy,Ballxyz), player_ID(10), Clock, ShotClock, 
    # Ball_OF, Ball_Hold
    # label: effective attack (1) or ineffective attack (0), T1, T2, score or not
    # index: corresponding to the file at root\nba_attack2\nba_datalength.csv

    trajectories = array(data[0], dtype=object)
    label = array(data[1], dtype=object)
    indices = array(data[2].astype(int), dtype=object)
    
    label_df = pd.DataFrame(label, index=indices)
    
    if initial_num_rows != -1:
        label_df = label_df[0:initial_num_rows]
        
    if team_id > 0:
        label_df= label_df[(label_df[6]==team_id)]
    
    # label data is in the format [label_i,t1,t2,score,shooterID,passerID,team_ID]
    effective = label_df.iloc[:,0]
    
    # convert 2- and 3-pointer score variable to binary 1/0 = score/didn't score
    label_df.iloc[label_df[3] == 2 , 3] = 1.0
    label_df.iloc[label_df[3] == 3 , 3] = 1.0
    score = label_df.iloc[:,3]
    
    if label_variable == 'score':
        label = score
    elif label_variable == 'effective':
        label = effective

    if time_interval == 't1':
        t1 = label_df.iloc[:,1]
        t_interval = label_df.iloc[:,2][t1>0]
    elif time_interval == 't2':
        t2 = label_df.iloc[:,2]
        t_interval = label_df.iloc[:,2][t2>0]
    
    # create dataframe for the specified agent
    agent_df = create_agent_df(agent_name, t_interval, trajectories, num_include)
    
    if run_type == 'statdsm':
        # create point and trajectory csv files
        create_point_csv(agent_df, agent_name, label)
        create_trajectory_csv(agent_df, agent_name, label)
        
        # delete the existing table rows in the postgres database tables
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates') 
        
        # import the newly created csv files into postgres database
        import_point_table_into_postgres(agent_name + '_point', path)
        import_traj_table_into_postgres(agent_name + '_trajectory', path)
    
if __name__ == '__main__':
    main()
