#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import 600-game NBA dataset .pkl file, export point-level and trajectory-level 
csv files, containing all agent points and trajectories, 
which are then created in the PostgreSQL database, 
and are then used as inputs to the MA-Stat-DSM algorithm.

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

# enter your postgres database details in param_dic
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "9408"
}

def create_df(trajectories, t_interval):
    ball_xy = []
    offense_xy_shooter = []
    offense_xy_last_passer = []
    defense_xy_shooter = []
    defense_xy_last_passer = []
    
    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                #ball
                ball_xy.append([t_interval.index[play_num][0], 
                                point_num,
                                (trajectories[play_num][point_num][0]),
                                (trajectories[play_num][point_num][1])])
                #shooter
                offense_xy_shooter.append([t_interval.index[play_num][0], 
                                           point_num,
                                (trajectories[play_num][point_num][2]),
                                (trajectories[play_num][point_num][3])])
                #last passer
                offense_xy_last_passer.append([t_interval.index[play_num][0], 
                                               point_num,
                                (trajectories[play_num][point_num][4]),
                                (trajectories[play_num][point_num][5])])
                
                #defender of shooter
                defense_xy_shooter.append([t_interval.index[play_num][0], 
                                           point_num,
                                (trajectories[play_num][point_num][12]),
                                (trajectories[play_num][point_num][13])])
                
                #defender of last passer
                defense_xy_last_passer.append([t_interval.index[play_num][0], 
                                               point_num,
                                (trajectories[play_num][point_num][14]),
                                (trajectories[play_num][point_num][15])])
                
                
    ball_df = pd.DataFrame([ball_xy[i][1:4] 
                            for i in range(0,len(ball_xy))], 
                           columns=['point','x','y'], 
                           index=[ball_xy[i][0] for i in range(0,len(ball_xy))])
    
    offense_df = pd.DataFrame([offense_xy_shooter[i][1:4] 
                               for i in range(0,len(offense_xy_shooter))], 
                           columns=['point','x','y'], 
                           index=[offense_xy_shooter[i][0] 
                                  for i in range(0,len(offense_xy_shooter))])
    offense_lp_df = pd.DataFrame([offense_xy_last_passer[i][1:4] 
                               for i in range(0,len(offense_xy_last_passer))], 
                           columns=['point','x','y'], 
                           index=[offense_xy_last_passer[i][0] 
                                  for i in range(0,len(offense_xy_last_passer))])
    
    defense_df = pd.DataFrame([defense_xy_shooter[i][1:4] 
                               for i in range(0,len(defense_xy_shooter))], 
                           columns=['point','x','y'], 
                           index=[defense_xy_shooter[i][0] 
                                  for i in range(0,len(defense_xy_shooter))])
    defense_lp_df = pd.DataFrame([defense_xy_last_passer[i][1:4] 
                               for i in range(0,len(defense_xy_last_passer))], 
                           columns=['point','x','y'], 
                           index=[defense_xy_last_passer[i][0] 
                                  for i in range(0,len(defense_xy_last_passer))])
    
    agent_df_list = [ball_df, offense_df, offense_lp_df, defense_df, defense_lp_df]
    
    return agent_df_list

def create_point_csv(agent_df_list, label):
    with open('point_ma.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'aid', 'tid', 'pid', 'label', 'geom'])
        row_num = 0
        for a in range(0,len(agent_df_list)):
            df = agent_df_list[a]

            traj_num = 0
            u = 0
            df_index_unique = df.index.drop_duplicates()
            
            for u in range(0, len(df_index_unique)):

                traj_num = df_index_unique[u]
                df_sub = df.loc[traj_num]
                for p in range(0,len(df_sub)):
                    writer.writerow([row_num,
                                             a,
                                             u,
                                             int(df_sub.iloc[p]['point']),
                                             int(label[(traj_num,)]),
                                             Point(df_sub.iloc[p]['x'],
                                                   df_sub.iloc[p]['y'])])
                    row_num+=1

def create_trajectory_csv(agent_df_list, label):
    with open('trajectory_ma.csv', 'w') as csvfile:
        writer= csv.writer(csvfile)
        writer.writerow(['id', 'aid', 'tid', 'label','geom'])
        row_num = 0
        for a in range(0,len(agent_df_list)):
            df = agent_df_list[a]

            df_index_unique = df.index.drop_duplicates()
            for u in range(0, len(df_index_unique)):
                traj_num = df_index_unique[u]
                df_sub = df.loc[traj_num]
                if len(df_sub) > 0:
                    writer.writerow([row_num, a, u, int(label[u]),
                                         LineString((df_sub.iloc[:,1:3]).to_numpy())])
                row_num+=1

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
    
def import_point_ma_table_into_postgres(filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY point_ma(id, aid, tid, pid, label, geom)
               FROM '/Users/rorybunker/""" + filename + """.csv' 
               DELIMITER ',' 
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()

def import_traj_ma_table_into_postgres(filename, path):
    conn = connect(param_dic)
    cur = conn.cursor()
    copy_sql = """
               COPY trajectory_ma(id, aid, tid, label, geom)
               FROM '/Users/rorybunker/""" + filename + """.csv' 
               DELIMITER ',' 
               CSV HEADER;
               """
    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()
 
def main():
    # data is in the format [feature, label, index]
    #feature: Position(23:OFxy,DFxy,Ballxyz), player_ID(10), Clock, ShotClock, 
    # Ball_OF, Ball_Hold
    #label: effective attack (1) or ineffective attack (0), T1, T2, score or not
    #index: corresponding to the file at root\nba_attack2\nba_datalength.csv
    
    # enter your working directory under path:
    path = '/Users/rorybunker/dataset_as_a_file_600_games.pkl'
    
    f = open(path, 'rb')
    data = pickle.load(f)
    
    indices = array(data[2].astype(int), dtype=object)
    trajectories = array(data[0], dtype=object)
    label = array(data[1], dtype=object)
    
    label_df = pd.DataFrame(label, index=indices)
    # or if you want to select specific teams e.g. Golden state warriors
    nba_team_id = 1610612744
    label_df = label_df[(label_df[6]==nba_team_id)] 
    # and or fixed number of plays e.g. for testing purposes
    number_of_plays = 100
    label_df = label_df.iloc[0:number_of_plays]
    
    #label data is in the format [label_i,t1,t2,score,shooterID,passerID,team_ID]
    effective = label_df.iloc[:,0]
    scored = label_df.iloc[:,3]
    
    time_interval = 't2'
    if time_interval == 't1':
        t_interval = label_df.iloc[:,1]
    elif time_interval == 't2':
        t2 = label_df.iloc[:,2]
        t_interval = label_df.iloc[:,2][t2>0]
    
    agent_df_list = create_df(trajectories, t_interval)
    
    create_point_csv(agent_df_list, effective)
    create_trajectory_csv(agent_df_list, effective)
    
    # delete the table rows that were in the postgres database tables previously
    delete_table_rows('point_ma')
    delete_table_rows('trajectory_ma')
    delete_table_rows('candidates_ma') 
    
    # import the newly created csv files into postgres database
    import_point_ma_table_into_postgres('point_ma', path)
    import_traj_ma_table_into_postgres('trajectory_ma', path)
    
if __name__ == '__main__':
    main()
