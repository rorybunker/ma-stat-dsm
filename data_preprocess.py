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
parser.add_argument('-r', '--init_rows', type=int, required=False, default=-1, help='set some number - useful for testing')
parser.add_argument('-a', '--a_list', action='store', dest='agt_list',
                    type=str, nargs='*', default=['ball', 'shooter', 'shooterdefender', 'lastpasser', 'lastpasserdefender'], help='list of agents from default=ball shooter shooterdefender lastpasser lastpasserdefender')
parser.add_argument('-ti', '--time_int', type=str, required=False, default='t2', help='t1 or t2 (default=t2)')
parser.add_argument('-p', '--xth_point', type=int, required=False, default=1, help='downsample by considering only every xth point from the trajectories (default=1, i.e., include every point)')
parser.add_argument('-g', '--game_id', type=int, required=False, default=0, help='specify a particular match id (default = all matches)')
parser.add_argument('-t', '--team', type=int, required=False, default=0, help='specify a particular team id (default = all teams)')
args, _ = parser.parse_known_args()

agent_list = args.agt_list

# enter your postgres database details
param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}

def create_agent_df(agent_name, t_interval, trajectories, num_include):
    ball_xy = []
    shooter_xy = []
    lastpasser_xy = []
    shooterdefender_xy = []
    lastpasserdefender_xy = []

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
                        shooter_xy.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
                                        (trajectories[play_num][point_num][2]),
                                        (trajectories[play_num][point_num][3])])
                    elif agent_name == 'lastpasser':
                        lastpasser_xy.append([t_interval.index[play_num][0], 
                                                       int(point_num/num_include),
                                        (trajectories[play_num][point_num][4]),
                                        (trajectories[play_num][point_num][5])])
                    elif agent_name == 'shooterdefender':
                        shooterdefender_xy.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
                                        (trajectories[play_num][point_num][12]),
                                        (trajectories[play_num][point_num][13])])
                    elif agent_name == 'lastpasserdefender':
                        lastpasserdefender_xy.append([t_interval.index[play_num][0], 
                                                       int(point_num/num_include),
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
    else:
        sys.exit("ERROR: agents must be from: ball shooter lastpasser shooterdefender lastpasserdefender")

def create_agent_ma_df(agent_list, trajectories, t_interval, num_include):
    ball_xy = []
    shooter_xy = []
    lastpasser_xy = []
    shooterdefender_xy = []
    lastpasserdefender_xy = []
    
    play_num = 0
    point_num = 0
    for play_num in range(0,len(t_interval)):
            for point_num in range(0,len(trajectories[play_num])):
                if point_num % num_include == 0:
                    #ball
                    ball_xy.append([t_interval.index[play_num][0], 
                                    int(point_num/num_include),
                                    (trajectories[play_num][point_num][0]),
                                    (trajectories[play_num][point_num][1])])
                    #shooter
                    shooter_xy.append([t_interval.index[play_num][0], 
                                               int(point_num/num_include),
                                    (trajectories[play_num][point_num][2]),
                                    (trajectories[play_num][point_num][3])])
                    #last passer
                    lastpasser_xy.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
                                    (trajectories[play_num][point_num][4]),
                                    (trajectories[play_num][point_num][5])])
                    
                    #defender of shooter
                    shooterdefender_xy.append([t_interval.index[play_num][0], 
                                               int(point_num/num_include),
                                    (trajectories[play_num][point_num][12]),
                                    (trajectories[play_num][point_num][13])])
                    
                    #defender of last passer
                    lastpasserdefender_xy.append([t_interval.index[play_num][0], 
                                                   int(point_num/num_include),
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
    
    return [['ball','shooter','lastpasser','shooterdefender','lastpasserdefender'],agent_df_list]

def create_point_csv(df, name, label):
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
                                         label[(traj_num,)],
                                         Point(df_sub.iloc[p]['x'],
                                               df_sub.iloc[p]['y'])])
                row_num += 1

def create_trajectory_csv(df, name, label):
    with open(name + '_trajectory.csv', 'w') as csvfile:
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

def create_trajectory_ma_csv(agent_df_list, label):
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
   
    path = os.getcwd() + '/dataset_as_a_file_600_games.pkl'

    # ---- DATA PRE-PROCESSING PARAMETERS ----
    label_variable = args.label  
    time_interval = args.time_int
    num_include = args.xth_point
    team_id = args.team
    match_id = args.game_id

    if args.init_rows > 0:
        initial_num_rows = args.init_rows
    else:
        initial_num_rows = -1
    
    if len(agent_list) > 1:
        run_type = 'mastatdsm'
    elif len(agent_list) == 1:
        run_type = 'statdsm'
    else:
        sys.exit("ERROR: please specify the agent list as a list containing at least one of ['ball', 'shooter', 'shooterdefender', 'lastpasser', 'lastpasserdefender]")
        
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
    
    # subset the data if team_id's are specified above 
    if team_id != 0:
        combined_df= combined_df[(combined_df[6] == team_id)]
    
    if match_id != 0:
        combined_df= combined_df[(combined_df['game_id'] == match_id)]
        
    # take the first initial_num_rows from the dataset (useful for testing)
    if initial_num_rows != -1:
        combined_df = combined_df[0:initial_num_rows]

    effective = combined_df.iloc[:,0]
    
    # convert 2- and 3-pointer score variable to binary 1/0 = score/didn't score
    combined_df.iloc[combined_df[3] == 2 , 3] = 1.0
    combined_df.iloc[combined_df[3] == 3 , 3] = 1.0
    score = combined_df.iloc[:,3]
    
    if label_variable == 'score':
        label = score
    elif label_variable == 'effective':
        label = effective
    else:
        sys.exit("ERROR: please specify the label_variable parameter to be either score or effective")

    if time_interval == 't1':
        t1 = combined_df.iloc[:,1]
        t_interval = combined_df.iloc[:,2][t1>0]
    elif time_interval == 't2':
        t2 = combined_df.iloc[:,2]
        t_interval = combined_df.iloc[:,2][t2>0]
    else:
        sys.exit("ERROR: please specify the time interval as either t1 or t2")
    
    if run_type == 'statdsm':
        # create dataframe for the specified agent
        agent_df = create_agent_df(agent_list[0], t_interval, trajectories, num_include)
        # create point and trajectory csv files
        create_point_csv(agent_df, agent_list[0], label)
        create_trajectory_csv(agent_df, agent_list[0], label)
        
        # delete the existing table rows in the postgres database tables
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates') 
        
        # import the newly created csv files into postgres database
        import_point_table_into_postgres(os, agent_list[0] + '_point', path)
        import_traj_table_into_postgres(os, agent_list[0] + '_trajectory', path)
    
    elif run_type == 'mastatdsm':
        agent_df_list = create_agent_ma_df(agent_list, trajectories, t_interval, num_include)
    
        create_point_ma_csv(agent_df_list[1], effective)
        create_trajectory_ma_csv(agent_df_list[1], effective)
        
        # delete the table rows that were in the postgres database tables previously
        delete_table_rows('point_ma')
        delete_table_rows('trajectory_ma')
        delete_table_rows('candidates') 
        
        # import the newly created csv files into postgres database
        import_point_ma_table_into_postgres(os, 'point_ma', path)
        import_traj_ma_table_into_postgres(os, 'trajectory_ma', path)
    else:
        sys.exit("ERROR: please specify the run_type parameter to be either statdsm or mastatdsm")
    
    print('Final # of plays in dataset: ' + str(len(t_interval)))
    
if __name__ == '__main__':
    main()