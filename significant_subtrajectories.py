# -----------------------------------------------------------------------------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Calculate p-values for each of the candidate sub-trajectories generated from Stat-DSM/MA-Stat-DSM

@author: Rory Bunker
"""
# -----------------------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import psycopg2
import sys
from scipy.special import comb
sys.setrecursionlimit(10000)
from sqlalchemy import create_engine
# import data_preprocess as prep
import argparse
import time
import os
# import warnings
# from shapely.errors import ShapelyDeprecationWarning
# warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

# sys.path.append('court_class.py')

import court_class

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--delta', type=float, required=True, dest='delta_s')
args, _ = parser.parse_known_args()
delta_star = args.delta_s

engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='1234'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

# -----------------------------------------------------------------------------------------------------------------------------------------------------

def count_label_number(trajectory_table, label):
    sql = """select count(distinct tid) from """ + str(trajectory_table) + """ where label = '""" + str(label) + """'"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]

def import_candidate_table(filename):
    """
    imports and processes the candidates.csv file generated from Stat-DSM/MA-Stat-DSM

    Returns
    -------
    df : pandas dataframe with:
        subtraj_se = subtrajectory - tid of candidate, and start and end indices;
        neighb_ids = tids of the epsilon-neighbors to the subtrajectory.

    """

    df = pd.read_csv(filename,
                header=0,
                names=['cid','candidate'])

    if len(df) == 0:
        sys.exit('ERROR: candidates.csv is empty')

    else:
        df = df['candidate'].str.split(':',expand=True)

        df = df[1].str.split('}', expand=True)
        df = df[0].str.split('],', expand=True)

        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df = df.fillna(value=np.nan)

        df.ffill(axis=1).apply(lambda x : x[x.last_valid_index()-1],1)

        # second to last column is the candidate subtrajectory between starting at index s and ending at e
        df['subtraj_se'] = df.apply(lambda x : x[x.last_valid_index()-1],1)
        # second column is the neighbor trajectory ids
        df['neighb_tids'] = df.iloc[:, 1]

        # extract only the two columns of interest
        df = df[['subtraj_se', 'neighb_tids']].copy()

        # remove all square brackets
        df['subtraj_se'] =  df['subtraj_se'].apply(lambda x: x.replace('[','').replace('[[','').replace('[[[',''))
        df['neighb_tids'] =  df['neighb_tids'].apply(lambda x: x.replace('[','').replace(']','').replace(']]','').replace(']]]','').replace(']]]]',''))

        return df


def get_label_of_neighb_id(trajectory_table, eps_id):
    sql = """select label from """ + str(trajectory_table) + """ where id = """ + str(eps_id) + """ """

    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]

# functions to calculate p-values - same as stat-dsm functions except do not use current_min_p
def calculate_upper_p_value(positive_support, negative_support, positive_number, negative_number):

    p_value = 0
    support = positive_support + negative_support

    for i in range(positive_support, min(positive_number, support) + 1):
        a = i
        c = support - i
        b = positive_number - a
        d = negative_number - c
        n = positive_number + negative_number

        p_value = p_value + (comb(support, a, exact=True) * comb(n - support, b, exact=True)) / \
                            (comb(n, positive_number, exact=True))

        # if p_value >= current_min_p:
            # return current_min_p

    return p_value

def calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number):

    p_value = 0
    support = positive_support + negative_support

    for i in range(max(0, support - negative_number), positive_support + 1):
        a = i
        c = support - i
        b = positive_number - a
        d = negative_number - c
        n = positive_number + negative_number

        p_value = p_value + (comb(support, a, exact=True) * comb(n - support, b, exact=True)) / \
                            (comb(n, positive_number, exact=True))

        # if p_value >= current_min_p:
            # return current_min_p

    return p_value

def calculate_p_value(positive_support, negative_support, positive_number, negative_number):

    upper_p = calculate_upper_p_value(positive_support, negative_support, positive_number, negative_number)
    lower_p = calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number)

    p_value = min(1, 2 * min(upper_p, lower_p))

    return p_value

# create the result tables of discriminative subtrajectories and discriminative points in the postgres db
def delete_table(table_name):
    sql = """DROP TABLE IF EXISTS """ + table_name +""";"""
    cur.execute(sql)
    conn.commit()

def change_column_types():
    sql = "ALTER TABLE discriminative_subtraj ALTER COLUMN tid TYPE INTEGER USING (discriminative_subtraj.tid::integer), ALTER COLUMN start_idx TYPE INTEGER USING (discriminative_subtraj.start_idx::integer), ALTER COLUMN end_idx TYPE INTEGER USING (discriminative_subtraj.end_idx::integer);"
    cur.execute(sql)
    conn.commit()

def delete_rows_discriminative_subtraj_table(disc_subtraj_table):
    sql = """DELETE FROM """ + disc_subtraj_table + """;"""
    cur.execute(sql)
    conn.commit()

def create_discriminative_point_table(point_table, ts):
    sql = """CREATE TABLE discriminative_points_""" + ts + """  AS SELECT p.* FROM """ + point_table + """ p INNER JOIN discriminative_subtraj d ON p.tid=d.tid WHERE p.pid BETWEEN d.start_idx AND d.end_idx;"""
    cur.execute(sql)
    conn.commit()

def create_discriminative_subtraj_vis_table(disc_point_table, ts):
    sql = """CREATE TABLE discriminative_sub_traj_vis_""" + ts + """  AS SELECT aid, tid, label, ST_MakeLine(dp.geom ORDER BY pid) AS geom FROM """ + disc_point_table + """_""" + ts + """  AS dp
		GROUP BY aid, tid, label"""
    cur.execute(sql)
    conn.commit()

def create_full_traj_table(point_table_name, subtraj_table_name, ts):
    table_name = "points_" + str(ts)
    sql = """CREATE TABLE """ + table_name + """ AS SELECT p.* FROM """ + point_table_name + """ p INNER JOIN  """ + subtraj_table_name + """ d on ((p.aid = d.aid)) and ((p.tid = d.tid));"""
    cur.execute(sql)
    conn.commit()

def drop_all_discriminative_tables(engine):
    # from db import connections
    from sqlalchemy.sql import text
    sql =   '''SELECT tablename FROM pg_catalog.pg_tables 
        WHERE schemaname='public'
        AND tablename LIKE 'discriminative_%%';'''
    temp_tables = pd.read_sql(sql, engine)['tablename']
    
    with engine.connect() as con:

        for table in temp_tables:
            sql = text(f"DROP table {table}")
            con.execute(sql)
            print(f"Dropped table {table}.")

def main():
    disc_subtraj_table = 'discriminative_subtraj'
    disc_point_table = 'discriminative_points'
    candidate_table = 'candidates'
    positive_label = '1'
    negative_label = '0'

    if os.path.getmtime('trajectory_ma.csv') > os.path.getmtime('trajectory.csv'):
        num_agents = len(pd.unique(pd.read_csv('trajectory_ma.csv')['aid']))
    elif os.path.getmtime('trajectory.csv') > os.path.getmtime('trajectory_ma.csv'):
        num_agents = 1
    
    if num_agents == 1:
        trajectory_table = 'trajectory'
        point_table = 'point'
    elif num_agents > 1:
        trajectory_table = 'trajectory_ma'
        point_table = 'point_ma'

    # drop all database tables from previous runs that start with discriminative
    # drop_all_discriminative_tables(engine)

    positive_number = count_label_number(trajectory_table, positive_label)
    negative_number = count_label_number(trajectory_table, negative_label)

    candidate_df = import_candidate_table(candidate_table + '.csv')

    eps_neighb_ids = candidate_df['neighb_tids'].values.tolist()

    eps_neighb_ids = [i.split(',') for i in eps_neighb_ids]

    # convert the id strings to integers and create list of lists of epsilon neighbors
    eps_neighb_ids = [[int(num) for num in sub] for sub in eps_neighb_ids]

    # create list of lists of labels of each of the epsilon neighbors
    eps_neighb_ids_labels_list = [[get_label_of_neighb_id(trajectory_table, eps_id) for eps_id in sub] for sub in eps_neighb_ids]

    # convert the list of lists to a dataframe with the labels as the values for each candidate row
    eps_neighb_labels_df = pd.DataFrame(eps_neighb_ids_labels_list)

    # add label count columns to the dataframe
    eps_neighb_labels_df['label_count'] = eps_neighb_labels_df.count(axis='columns')
    eps_neighb_labels_df['label_0_count'] = eps_neighb_labels_df.apply(lambda s : s.value_counts().get(key='0',default='0'), axis=1)
    eps_neighb_labels_df['label_1_count'] = eps_neighb_labels_df.apply(lambda s : s.value_counts().get(key='1',default='1'), axis=1)


    # calculate the p-value for each candidate based on the label counts and total # of instances under each label
    eps_neighb_labels_df['pvalue'] = eps_neighb_labels_df.apply(lambda row:
                                                                calculate_p_value(int(row['label_1_count']),
                                                                                  int(row['label_0_count']),
                                                                                  positive_number,
                                                                                  negative_number),
                                                                axis=1)

    # merge the calculated p-values with the original sub-trajectory and neighbor ids
    final_df = pd.merge(candidate_df, eps_neighb_labels_df['pvalue'], left_index=True, right_index=True)

    # then, filter to only include those with p-values less than the delta* value calculated from stat-dsm
    result_df = final_df.loc[final_df['pvalue'] < delta_star]

    if result_df.empty == True:
        print("The lowest p-value for any sub-trajectory is " + str(min(eps_neighb_labels_df['pvalue'])) + ". There are no significant sub-trajectories that have p-values below delta *")
        conn.close()
        sys.exit(1)
        
    elif result_df.empty == False:
        # extract the subtrajectory tid and its start and end index as columns
        result_df = pd.concat([result_df, result_df['subtraj_se'].str.split(', ', expand=True)], axis=1)
        result_df = result_df.rename(columns={0: 'tid', 1: 'start_idx', 2: 'end_idx'})

        result_df.to_sql(disc_subtraj_table, engine, if_exists='replace')

        change_column_types()

        # get current timestamp to append to database table names
        ts = time.gmtime()
        ts_value = time.strftime("%s", ts)

        # delete_table(disc_point_table)
        create_discriminative_point_table(point_table, ts_value)
        
        # create table to visualize the discriminative subtrajectories
        # delete_table('discriminative_sub_traj_vis')
        # create_discriminative_subtraj_vis_table(disc_point_table, ts_value)
        
        # plot the discriminative subtrajectories
        court_path = 'nba_court_T.png'
        table_name = 'discriminative_points_' + str(ts_value)

        # create the full trajectory table to underlay the full trajectories under the discriminative subtrajectories
        create_full_traj_table(point_table, table_name, ts_value)

        court = court_class.Court(table_name, court_path, engine)
        
        if num_agents == 1:
            court.plot_single_agent_trajectories()
        elif num_agents > 1:
            court.plot_multi_agent_trajectories()

        conn.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
