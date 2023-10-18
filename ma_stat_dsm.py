import psycopg2
import json
import time
import numpy as np
import pandas as pd
import sys
sys.setrecursionlimit(10000)
import max_euclidean
from scipy.special import comb
from shapely.geometry import LineString
from hausdorff import hausdorff_distance
import argparse
import warnings
import os
import stat_dsm
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--pos_label', type=str, required=False, default='1')
parser.add_argument('-n', '--neg_label', type=str, required=False, default='0')
parser.add_argument('-i', '--max_it', type=int, required=False, default=1000, help='maximum number of iterations (default=1000)')
parser.add_argument('-a', '--alph', type=float, required=False, default=0.05, help='statistical significance level (alpha). default is alpha = 0.05')
parser.add_argument('-l', '--min_l', type=int, required=True, help='minimum trajectory length (required)')
parser.add_argument('-d', '--dist_threshold', type=float, required=True, help='distance threshold (required)')
parser.add_argument('-b', '--hausdorff_base_dist', type=str, required=False, default='euclidean', help='options for base_distance are euclidean, manhattan, chebyshev, or cosine (default is euclidean)')
parser.add_argument('-s', '--seed', type=int, action='store', dest='rseed', required=False, default=0, help='random seed for labels (default = 0 for reproducability)')
args, _ = parser.parse_known_args()

# Write the arguments to a file to use in the next script
with open('args_msdsm.txt', 'w') as f:
    f.write(str(args.min_l) + '\n')
    f.write(str(args.dist_threshold) + '\n')

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='1234'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def calculate_hausdorff_distance(X, Y, base_distance):
    h_dist = hausdorff_distance(np.array(X), np.array(Y), base_distance)
    return h_dist

def count_label_number(trajectory_table, label):
    sql = """select count(*) from """ + str(trajectory_table) + """ where label = '""" + str(label) + """'"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]

def get_list_label(trajectory_table):
    sql = """select label from """ + str(trajectory_table) + """ order by tid asc"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_list_phase_tid(table_name, len_agent_ids):
    if len_agent_ids == 1:
        sql = """select tid from """ + str(table_name) + """ order by tid asc"""
    elif len_agent_ids > 1:
        sql = """select distinct tid from """ + str(table_name) + """ order by tid asc"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_trajectory(trajectory_table, tid, len_agent_ids):
    #if len(agent_ids) == 1:
    sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + ""
    #elif len(agent_ids) > 1:
        #sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + """ and aid in (""" + ', '.join(map(str, agent_ids)) + ")"

    cur.execute(sql)
    rows = cur.fetchall()

    return [json.loads(rows[a][0])['coordinates'] for a in range(len_agent_ids)]

def find_length_k_potential_neighbor(trajectory_tid, length_k_sub_trajectory, point_table, distance_threshold, top_k):
    distance_threshold = distance_threshold * top_k
    total_length_k_potential_neighbor = [] # [[tid, trajectory], ...]
    length = len(length_k_sub_trajectory)

    sql = """select tid, aid, pid, label, ST_AsGeoJSON(geom) from """ + str(point_table) + """
            where tid != """ + str(trajectory_tid) + """
            and """         
    
    count = 0
    for agent_traj in length_k_sub_trajectory:
        count = count + 1

        if count == 1:
            sql = sql + """ (ST_DWithin('""" + LineString(agent_traj).wkt + """'::geometry, geom, """ + str(
                distance_threshold) + """) or """

            continue

        if count == length:
            sql = sql + """ ST_DWithin('""" + LineString(agent_traj).wkt + """'::geometry, geom, """ + str(
                distance_threshold) + """)) ORDER BY tid ASC, aid ASC, pid ASC;"""

            break

        sql = sql + """ ST_DWithin('""" + LineString(agent_traj).wkt + """'::geometry, geom, """ + str(
            distance_threshold) + """) or """

    cur.execute(sql)
    nearest_points = cur.fetchall()
    
    s = -1
    e = 0

    potential_neighbor = []

    length = len(length_k_sub_trajectory[0])

    while s < (len(nearest_points) - length):
        s = s + 1
        current_point = list(nearest_points[s])

        if len(potential_neighbor) == 0:
            potential_neighbor.append(json.loads(current_point[4])['coordinates'])


        while (e - s + 1) < length:
            e = e + 1

            end_point = list(nearest_points[e])

            if (list(nearest_points[e - 1])[0] == end_point[0]) and (end_point[2] == list(nearest_points[e - 1])[2] + 1):
                potential_neighbor.append(json.loads(end_point[4])['coordinates'])
            else:
                break
              
        if len(potential_neighbor) == length:
            total_length_k_potential_neighbor.append([[current_point[0], current_point[1], current_point[2], list(nearest_points[e])[2]],
                                                        potential_neighbor])
            potential_neighbor = potential_neighbor[1:]
        else:
            s = e - 1
            potential_neighbor = []
    
    return total_length_k_potential_neighbor


def confirm_neighbor_hausdorff(length_k_sub_trajectory, list_potential_neighbor, distance_threshold):
    list_neighbor = []

    n_agent = np.array(length_k_sub_trajectory).shape[0]
    minimum_l = np.array(length_k_sub_trajectory).shape[1]
    num_coords = np.array(length_k_sub_trajectory).shape[2]

    for potential_neighbor in list_potential_neighbor:
            # Reshapes the 3D array into a 2D array where each row represents a point in space. Total of number of agents * min trajectory length points with 2 coordinates each.
            # Allows to work with a consistent 2D array format, even if the individual trajectories have varying lengths in oder to calculate Hausdorff distance
            length_k_sub_trajectory_flattened = np.array(length_k_sub_trajectory).reshape(n_agent*minimum_l, num_coords)
            max_distance = calculate_hausdorff_distance(length_k_sub_trajectory_flattened, potential_neighbor[1], args.hausdorff_base_dist)

            if max_distance <= distance_threshold:
                list_neighbor.append(potential_neighbor[0])

    return list_neighbor

def confirm_neighbor_euclidean(top_k, length_k_sub_trajectory, list_potential_neighbor, distance_threshold):
    list_neighbor = []
    list_top_k_max = []

    # Each potential neighbor: [[2, 0, 1], [[5.5, 14], [7, 14]]]

    for potential_neighbor in list_potential_neighbor:
        top_k_max, max_distance = max_euclidean.calculate_top_k(top_k, length_k_sub_trajectory,potential_neighbor[1])
        
        if max_distance <= distance_threshold:
            list_neighbor.append(potential_neighbor[0])
            list_top_k_max.append(top_k_max)

    return list_top_k_max, list_neighbor


def get_list_neighbor_tid(list_neighbor):
    list_neighbor_tid = []
    for neighbor in list_neighbor:
        neighbor_tid = neighbor[0]
        if neighbor_tid not in list_neighbor_tid:
            list_neighbor_tid.append(neighbor_tid)

    return list_neighbor_tid


def calculate_upper_lower_bound(support, positive_number, negative_number):
    n = positive_number + negative_number
    if support <= positive_number:
        x = support
        y = support
    else:
        x = positive_number
        y = positive_number

    lower_bound = (comb(positive_number, y, exact=True) * comb(negative_number, (x - y), exact=True)) / \
                  comb(n, x, exact=True)

    return lower_bound


def calculate_lower_lower_bound(support, positive_number, negative_number):
    n = positive_number + negative_number
    if support <= negative_number:
        x = support
        y = 0
    else:
        x = negative_number
        y = 0

    lower_bound = (comb(positive_number, y, exact=True) * comb(negative_number, (x - y), exact=True)) / \
                  comb(n, x, exact=True)

    return lower_bound


def calculate_lower_bound(support, positive_number, negative_number):
    upper_lower_bound = calculate_upper_lower_bound(support, positive_number, negative_number)
    lower_lower_bound = calculate_lower_lower_bound(support, positive_number, negative_number)

    lower_bound = min(upper_lower_bound, lower_lower_bound)

    return lower_bound


def calculate_upper_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p):
    
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

        if p_value >= current_min_p:
            return current_min_p

    return p_value



def calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p=None):

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

        if p_value >= current_min_p:
            return current_min_p

    return p_value


def calculate_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p=None):

    upper_p = calculate_upper_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p)
    lower_p = calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p)

    p_value = min(1, 2 * min(upper_p, lower_p))

    return p_value


def update_list_min_p(list_min_p, list_permuted_dataset, list_neighbor_tid, current_node_lower_bound, max_iter,
                      candidate_label, positive_number, negative_number, positive_label):

    for iteration in range(max_iter):
        permutation_list_label = list_permuted_dataset[iteration]
        current_min_p = list_min_p[iteration]

        if current_node_lower_bound < current_min_p:

            number_of_same_label = 0
            number_of_different_label = 0

            for element_tid in list_neighbor_tid:

                element_label = permutation_list_label[element_tid]

                if candidate_label == element_label:
                    number_of_same_label = number_of_same_label + 1
                else:
                    number_of_different_label = number_of_different_label + 1

            if candidate_label == str(positive_label):
                a = number_of_same_label
                c = number_of_different_label
            else:
                a = number_of_different_label
                c = number_of_same_label

            current_node_p_value = calculate_p_value(a, c, positive_number, negative_number, current_min_p)

            if current_node_p_value < current_min_p:
                list_min_p[iteration] = current_node_p_value

    return list_min_p


def get_neighbor_trajectories(trajectory_table, list_tid):
    if len(list_tid) == 1:
        sql = """select tid, ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(list_tid[0]) + """ """
    else:
        sql = """select tid, ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid in """ + str(
            tuple(list_tid)) + """ """

    cur.execute(sql)
    rows = cur.fetchall()

    list_trajectory = {}
    for row in rows:
        list_trajectory.update({row[0] : json.loads(row[1])['coordinates']})

    return list_trajectory

def get_neighbor_ma_trajectories(trajectory_table, list_tid):
    if len(list_tid) == 1:
        sql = """select tid, aid, ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(list_tid[0]) + """ """
    else:
        sql = """select tid, aid, ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid in """ + str(
            tuple(list_tid)) + """ order by tid asc, aid asc"""

    cur.execute(sql)
    rows = cur.fetchall()

    list_trajectory = {}
    for row in rows:
        list_trajectory.update({(row[0],row[1]) : json.loads(row[2])['coordinates']})
    
    return list_trajectory

def insert_list_tree(candidate_table, list_tree):
    sql = """INSERT INTO """ + str(candidate_table) + """ (candidate) VALUES (%(candidate)s)"""
    cur.executemany(sql, tuple(list_tree))
    conn.commit()


def ma_stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, parameter):
    min_length = parameter["min_length"]
    distance_threshold = parameter["distance_threshold"]
    top_k = parameter["top_k"]
    positive_number = parameter["positive_number"]
    negative_number = parameter["negative_number"]
    max_iter = parameter["max_iter"]
    alpha = parameter["alpha"]
    positive_label = parameter["positive_label"]
    num_agents = parameter["num_agents"]
    dict_lower_bound = {}

    for trajectory_tid in list_phase_tid:
        # print(trajectory_tid)

        list_tree = []
        trajectory = get_trajectory(trajectory_table, trajectory_tid, num_agents)
        trajectory_length = len(trajectory[0])
        trajectory_label = original_list_label[trajectory_tid]

        if trajectory_length < min_length:
            continue
        
        for i in range(trajectory_length - min_length + 1):
            length_k_sub_trajectory = [[] for a in range(num_agents)]
            
            for j in range(min_length):
                [length_k_sub_trajectory[a].append(trajectory[a][i + j]) for a in range(num_agents)]
            
            potential_neighbor = find_length_k_potential_neighbor(trajectory_tid, length_k_sub_trajectory, point_table, distance_threshold, top_k)
            
            list_neighbor = confirm_neighbor_hausdorff(length_k_sub_trajectory, potential_neighbor,
                                                                distance_threshold)
            
            if len(list_neighbor) == 0:
                continue

            list_neighbor_tid = get_list_neighbor_tid(list_neighbor)

            try:
                lower_bound = dict_lower_bound[len(list_neighbor_tid)]
            except:
                lower_bound = calculate_lower_bound(len(list_neighbor_tid), positive_number, negative_number)
                dict_lower_bound.update({len(list_neighbor_tid): lower_bound})

            sorted_list_min_p = list_min_p[:]
            sorted_list_min_p.sort()

            if lower_bound >= sorted_list_min_p[int(max_iter * alpha)]:
                continue

            list_min_p = update_list_min_p(list_min_p, list_permuted_dataset, list_neighbor_tid, lower_bound, max_iter,
                                           trajectory_label, positive_number, negative_number, positive_label)

            candidate_start_idx = i
            candidate_end_idx = i + min_length - 1

            current_list_neighbor = list_neighbor
            current_list_neighbor_tid = list_neighbor_tid

            dict_neighbor_full_trajectory_ma = get_neighbor_ma_trajectories(trajectory_table, current_list_neighbor_tid)
            
            root = []
            root.append([[trajectory_tid, candidate_start_idx, candidate_end_idx], current_list_neighbor_tid])

            while True:
                if candidate_end_idx == (trajectory_length - 1):
                    break

                candidate_end_idx = candidate_end_idx + 1

                list_new_candidate_neighbor = []

                for neighbor_index in range(len(current_list_neighbor)):

                    neighbor = current_list_neighbor[neighbor_index]

                    neighbor_tid = neighbor[0]
                    neighbor_start_idx = neighbor[1]
                    neighbor_end_idx = neighbor[2]

                    if neighbor_end_idx == (len(dict_neighbor_full_trajectory_ma[(neighbor_tid,0)]) - 1):
                    # del dict_neighbor_full_trajectory[neighbor_tid]
                        continue

                    new_neighbor_start_idx = neighbor_start_idx
                    new_neighbor_end_idx = neighbor_end_idx + 1

                    dist = calculate_hausdorff_distance([trajectory[a][candidate_end_idx] for a in range(num_agents)],
                                                [dict_neighbor_full_trajectory_ma[(neighbor_tid,a)][new_neighbor_end_idx] for a in range(num_agents)], args.hausdorff_base_dist)
                    
                    if dist <= distance_threshold:
                        list_new_candidate_neighbor.append(
                            [neighbor_tid, new_neighbor_start_idx, new_neighbor_end_idx])

                if len(list_new_candidate_neighbor) == 0:
                    break

                list_new_neighbor_tid = get_list_neighbor_tid(list_new_candidate_neighbor)

                try:
                    lower_bound = dict_lower_bound[len(list_new_neighbor_tid)]
                except:
                    lower_bound = calculate_lower_bound(len(list_new_neighbor_tid), positive_number, negative_number)
                    dict_lower_bound.update({len(list_new_neighbor_tid): lower_bound})

                # lower_bound = calculate_lower_bound(len(list_new_neighbor_tid), positive_number, negative_number)

                sorted_list_min_p = list_min_p[:]
                sorted_list_min_p.sort()

                if lower_bound >= sorted_list_min_p[int(max_iter * alpha)]:
                    break

                list_min_p = update_list_min_p(list_min_p, list_permuted_dataset, list_neighbor_tid, lower_bound,
                                               max_iter, trajectory_label, positive_number, negative_number, positive_label)

                current_list_neighbor = list_new_candidate_neighbor
                current_list_neighbor_tid = list_new_neighbor_tid

                root.append([[trajectory_tid, candidate_start_idx, candidate_end_idx], current_list_neighbor_tid])
                
            list_tree.append({"candidate": json.dumps({'candidates': root})})

        insert_list_tree(candidate_table, list_tree)

    # print(list_min_p)
    np.savetxt('list_min_p.txt', list_min_p, delimiter=',')

    list_min_p_value = list_min_p[:]
    list_min_p_value.sort()
    idx = int(alpha * max_iter)
    
    while idx > 0:
        if list_min_p_value[idx - 1] < list_min_p_value[idx]:
            return list_min_p_value[idx - 1]

        idx = idx - 1

    return 'FAIL'

def main():
    start_time = time.time()

    if os.path.getmtime('trajectory_ma.csv') > os.path.getmtime('trajectory.csv'):
        len_agent_ids = len(pd.unique(pd.read_csv('trajectory_ma.csv')['aid']))
    elif os.path.getmtime('trajectory.csv') > os.path.getmtime('trajectory_ma.csv'):
        len_agent_ids = 1
    
    positive_label = args.pos_label
    negative_label = args.neg_label
    max_iter = args.max_it
    min_length = args.min_l
    alpha = args.alph
    distance_threshold = args.dist_threshold
    rand_seed = args.rseed
    top_k = 1

    candidate_table = 'candidates'

    if len_agent_ids == 1:
        point_table = 'point'
        trajectory_table = 'trajectory'
    elif len_agent_ids > 1:
        point_table = 'point_ma'
        trajectory_table = 'trajectory_ma'

    positive_number = count_label_number(trajectory_table, positive_label)
    negative_number = count_label_number(trajectory_table, negative_label)
    
    original_list_label = get_list_label(trajectory_table)
    original_list_label = np.array(original_list_label)
    original_list_label = original_list_label[:, 0].tolist()
    original_list_label = np.array(original_list_label)
    
    list_permuted_dataset = []
    list_min_p = []

    np.random.seed(rand_seed)
    for i in range(max_iter):
        list_idx = np.random.permutation(len(original_list_label))
        # list_idx = np.random.RandomState(seed=rand_seed).permutation(len(original_list_label))
        permutation_list_label = original_list_label[list_idx]
        list_permuted_dataset.append(permutation_list_label)
        list_min_p.append(alpha)

    list_phase_tid = get_list_phase_tid(trajectory_table, len_agent_ids)
    list_phase_tid = np.array(list_phase_tid)
    list_phase_tid = list_phase_tid[:, 0].tolist()
    
    parameter = {
        "positive_label": positive_label,
        "negative_label": negative_label,
        "max_iter": max_iter,
        "min_length": min_length,
        "alpha": alpha,
        "distance_threshold": distance_threshold,
        "top_k": top_k,
        "positive_number": positive_number,
        "negative_number": negative_number,
        "num_agents": len_agent_ids
    }
    
    if len_agent_ids == 1:
        delta = stat_dsm.stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, parameter)
    elif len_agent_ids > 1:
        delta = ma_stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, parameter)
    
    print(delta)

    candidates_df = pd.read_sql("SELECT * FROM candidates", conn)
    candidates_df.to_csv('candidates.csv')

    cur.close()
    conn.close()

    # print("--- %s seconds ---" % (time.time() - start_time))

    # return(delta)

if __name__ == "__main__":
    main()
