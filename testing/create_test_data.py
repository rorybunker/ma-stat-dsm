import pandas as pd
import psycopg2
import sys
import os

param_dic = {
    "host"      : "localhost",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "1234"
}
os.chdir('/home/b_rory/workspace2/work/ma_stat_dsm/testing/')

run_type = 'mastatdsm'
num_iterations = 10 # number of times to append the same dataset to itself

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

def append_data_to_itself(trajectory, point, num_iterations):
    trajectory_copy = pd.DataFrame.copy(trajectory)
    
    for i in range(num_iterations):
        trajectory_copy['tid'] = trajectory_copy['tid'] + 5
        trajectory = trajectory.append(trajectory_copy, ignore_index=True)
    
    trajectory['id'] = trajectory.index
    
    point_copy = pd.DataFrame.copy(point)
    
    for i in range(num_iterations):
        point_copy['tid'] = point_copy['tid'] + 5
        point = point.append(point_copy, ignore_index=True)
    
    point['id'] = point.index
    
    return trajectory, point

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

    with open(path, 'r') as f:
        cur.copy_expert(sql=copy_sql, file=f)
        conn.commit()
        cur.close()
        
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
    
    if run_type == 'statdsm':
        point = pd.read_csv('point_test_statdsm.csv')
        trajectory = pd.read_csv('trajectory_test_statdsm.csv')
    elif run_type == 'mastatdsm':
        point = pd.read_csv('point_test_mastatdsm.csv')
        trajectory = pd.read_csv('trajectory_test_mastatdsm.csv')

    trajectory, point = append_data_to_itself(trajectory, point, num_iterations)
    
    point.to_csv('point_test_final.csv', index=False)
    trajectory.to_csv('trajectory_test_final.csv', index=False)
    
    file_path = os.getcwd() + '/create_test_data.py'

    if run_type == 'statdsm':
        delete_table_rows('point')
        delete_table_rows('trajectory')
        delete_table_rows('candidates')
        import_point_table_into_postgres(os, 'point_test_final', file_path)
        import_traj_table_into_postgres(os, 'trajectory_test_final', file_path) 
    elif run_type == 'mastatdsm':
        delete_table_rows('point_ma')
        delete_table_rows('trajectory_ma')
        delete_table_rows('candidates')
        import_point_ma_table_into_postgres(os, 'point_test_final', file_path)
        import_traj_ma_table_into_postgres(os, 'trajectory_test_final', file_path) 
        
if __name__ == '__main__':
    main()