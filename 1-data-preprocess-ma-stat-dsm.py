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
t1 = label_df.iloc[:,1]
t2 = label_df.iloc[:,2]
t2 = label_df.iloc[:,2][t2>0]

scored = label_df.iloc[:,3]
scored_df = pd.DataFrame(scored, index=scored.index)
shooter_id = label_df.iloc[:,4]
passer_id = label_df.iloc[:,5]
team_id = label_df.iloc[:,6]

ball_xy = []
offense_xy_shooter = []
offense_xy_last_passer = []
defense_xy_shooter = []
defense_xy_last_passer = []

play_num = 0
point_num = 0
for play_num in range(0,len(t2)):
        for point_num in range(0,len(trajectories[play_num])):
            #ball
            ball_xy.append([t2.index[play_num][0], 
                            point_num,
                            (trajectories[play_num][point_num][0]),
                            (trajectories[play_num][point_num][1])])
            #shooter
            offense_xy_shooter.append([t2.index[play_num][0], 
                                       point_num,
                            (trajectories[play_num][point_num][2]),
                            (trajectories[play_num][point_num][3])])
            #last passer
            offense_xy_last_passer.append([t2.index[play_num][0], 
                                           point_num,
                            (trajectories[play_num][point_num][4]),
                            (trajectories[play_num][point_num][5])])
            
            #defender of shooter
            defense_xy_shooter.append([t2.index[play_num][0], 
                                       point_num,
                            (trajectories[play_num][point_num][12]),
                            (trajectories[play_num][point_num][13])])
            
            #defender of last passer
            defense_xy_last_passer.append([t2.index[play_num][0], 
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
agent_name_list = ["ball", "shooter", "lp", "shooter_defender", "lp_defender"]

def create_point_csv(agent_df_list):
    with open('point.csv', 'w') as csvfile:
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
                                             int(effective[(traj_num,)]),
                                             Point(df_sub.iloc[p]['x'],
                                                   df_sub.iloc[p]['y'])])
                    row_num+=1

create_point_csv(agent_df_list)

def create_trajectory_csv(agent_df_list):
    with open('trajectory.csv', 'w') as csvfile:
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
                    writer.writerow([row_num, a, u, int(effective[u]),
                                         LineString((df_sub.iloc[:,1:3]).to_numpy())])
                row_num+=1

create_trajectory_csv(agent_df_list)

# enter your postgres database details in param_dic
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "9408"
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
    sql = """DELETE FROM """ + table_name +""";"""
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

# delete the table rows that were in the postgres database tables previously
delete_table_rows('phase_point_ma')
delete_table_rows('phase_trajectory_ma')
delete_table_rows('candidates') 
    
# now, in pgadmin, run these commands to import the csv files generated 
# into postgres database:
# COPY phase_point_ma(id, aid, tid, pid, label, geom)
# FROM '.../point.csv'
# DELIMITER ',' 
# CSV HEADER;

# COPY phase_trajectory_ma(id, aid, tid, label, geom)
# FROM '.../trajectory.csv'
# DELIMITER ',' 
# CSV HEADER;
