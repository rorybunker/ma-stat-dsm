import psycopg2
import json
import time
import numpy as np
import sys
sys.setrecursionlimit(10000)

import os
os.chdir("/Users/rorybunker/")

from scipy.special import comb
from shapely.geometry import MultiLineString
from hausdorff import hausdorff_distance
from shapely.geometry import LineString
from shapely.geometry import Point

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='1234'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def calculate_hausdorff_distance(X, Y, base_dist = 'euclidean'):
    h_dist = hausdorff_distance(np.array(X), np.array(Y), base_dist)
    return h_dist

def count_label_number(trajectory_table, label):
    sql = """select count(distinct tid) from """ + str(trajectory_table) + """ where label = '""" + str(label) + """'"""
    
    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]

def get_list_label(trajectory_table):
    sql = """select label from """ + str(trajectory_table) + """ group by tid, label order by tid asc"""
    
    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_list_phase_tid(table_name):
    sql = """select distinct tid from """ + str(table_name) + """ order by tid asc"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_list_agent_aid(table_name):
    sql = """select distinct aid from """ + str(table_name) + """ order by aid asc"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_trajectory_matrix(trajectory_table, tid, num_agents):
    sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + """ """

    cur.execute(sql)
    rows = cur.fetchall()
    return [json.loads(rows[i][0])['coordinates'] for i in range(0,num_agents)]

def get_agent_trajectory(trajectory_table, tid, aid):
    
    sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + """ and aid = """ + str(aid) + """ """
    cur.execute(sql)
    rows = cur.fetchall()

    return json.loads(rows[0][0])['coordinates']

def convert_list_of_lists_to_mls(play_list_of_lists):
    lol = [[]]
    if len(play_list_of_lists) > 1:
        for x in play_list_of_lists:
            lol[0].append(x[0])
        coords = lol
    else:
        coords = [tuple(tuple(point) for point in agent_traj) for agent_traj in play_list_of_lists]
    if len(coords) == 1:
        return Point(coords[0][0])
    elif len(coords) == 2:
        return LineString(coords)
    else:
        return MultiLineString(coords)

def get_all_traj_matrices_list_of_lists(trajectory_table, num_agents):
    trajectory_matrices_all_lol = []
    
    for tid in range(count_label_number(trajectory_table, 0) + count_label_number(trajectory_table, 1)):
        trajectory_matrices_all_lol.append([tid, get_trajectory_matrix(trajectory_table, tid, num_agents)])
    
    return trajectory_matrices_all_lol
        
def get_all_traj_matrices_shapely_fmt(trajectory_matrices_all_lol):
    return [[[str(point[0]) + ' ' + str(point[1]) for point in agent_traj] for agent_traj in trajectory_matrix] for trajectory_matrix in trajectory_matrices_all_lol]
    
def find_length_k_potential_neighbor(trajectory_tid, length_k_sub_matrix, length_k_sub_matrix_lol, trajectory_table, distance_threshold, num_agents):#, top_k):
    #distance_threshold = distance_threshold * top_k

    total_length_k_potential_neighbor = [] # [[tid, ma_trajectory_matrix], ...]

    length = len(length_k_sub_matrix[0])
    
    traj_matrices_all_lol = get_all_traj_matrices_list_of_lists(trajectory_table, num_agents)
    # traj_matrices_all_shapely = get_all_traj_matrices_shapely_fmt(traj_matrices_all_lol)
    
    length_k_sub_matrix_mls = convert_list_of_lists_to_mls(length_k_sub_matrix_lol)
    
    nearest_columns = [] # matrix columns that are within distance threshold 
    
    for traj in traj_matrices_all_lol:
        mid = traj[0] # matrix id
        matrix = traj[1]
        cid = 0 # column id
        
        if mid != trajectory_tid:
            for agent_traj in matrix:
                column_list = []
                for cid in range(len(agent_traj)):
                    column_list.append([tuple(agent_traj[cid]) for agent_traj in matrix])
    
                    if len(column_list[0]) == 1:
                        haus_dist = (Point(column_list[0])).hausdorff_distance(length_k_sub_matrix_mls)
                    else:
                        haus_dist = (LineString(column_list[0])).hausdorff_distance(length_k_sub_matrix_mls)
                        
                    if haus_dist < distance_threshold:
                        nearest_columns.append([mid, cid, column_list[cid]])
                    # column_list = []
        
    s = -1
    e = 0

    #potential_neighbor = [[] for _ in range(num_agents)]
    potential_neighbor = []
    
    while s < (len(nearest_columns) - length):
        s = s + 1
        current_column = list(nearest_columns[s])

        if len(potential_neighbor) == 0:
            potential_neighbor.append(current_column[2])

        while (e - s + 1) < length:
            e = e + 1

            end_column = list(nearest_columns[e])
            if (list(nearest_columns[e - 1])[0] == end_column[0]) and (end_column[1] == list(nearest_columns[e - 1])[1] + 1):
                potential_neighbor.append(end_column[2])
            else:
                break

        if len(potential_neighbor) == length:
            total_length_k_potential_neighbor.append([[current_column[0], current_column[1], list(nearest_columns[e])[1]],
                                                      potential_neighbor])
            potential_neighbor = potential_neighbor[1:]
        else:
            s = e - 1
            potential_neighbor = []
       
    return total_length_k_potential_neighbor

def confirm_neighbor(length_k_sub_matrix_mls, list_potential_neighbor, distance_threshold):
    list_neighbor = []

    # Each potential neighbor: [[2, 0, 1], [[5.5, 14], [7, 14]]]

    for potential_neighbor in list_potential_neighbor:
        
        if len(potential_neighbor[1][0]) == 1:
            haus_dist = (Point(potential_neighbor[1][0])).hausdorff_distance(length_k_sub_matrix_mls)
        else:
            haus_dist = (MultiLineString(potential_neighbor[1])).hausdorff_distance(length_k_sub_matrix_mls)
        
        if haus_dist <= distance_threshold:
            list_neighbor.append(potential_neighbor[0])

    return list_neighbor

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
        #c = support - i
        b = positive_number - a
        #d = negative_number - c
        n = positive_number + negative_number

        p_value = p_value + (comb(support, a, exact=True) * comb(n - support, b, exact=True)) / \
                            (comb(n, positive_number, exact=True))

        if p_value >= current_min_p:
            return current_min_p

    return p_value

def calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p):

    p_value = 0
    support = positive_support + negative_support

    for i in range(max(0, support - negative_number), positive_support + 1):
        a = i
        #c = support - i
        b = positive_number - a
        #d = negative_number - c
        n = positive_number + negative_number

        p_value = p_value + (comb(support, a, exact=True) * comb(n - support, b, exact=True)) / \
                            (comb(n, positive_number, exact=True))

        if p_value >= current_min_p:
            return current_min_p

    return p_value

def calculate_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p):

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

def ma_stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, list_agent_aid, parameter):
    min_length = parameter["min_length"]
    distance_threshold = parameter["distance_threshold"]
    # top_k = parameter["top_k"]
    positive_number = parameter["positive_number"]
    negative_number = parameter["negative_number"]
    max_iter = parameter["max_iter"]
    alpha = parameter["alpha"]
    positive_label = parameter["positive_label"]
    num_agents = parameter["num_agents"]

    dict_lower_bound = {}

    for trajectory_tid in list_phase_tid:
        print(trajectory_tid)

        list_tree = []

        trajectory_matrix = get_trajectory_matrix(trajectory_table, trajectory_tid, num_agents)
        trajectory_length = len(trajectory_matrix[0])
        trajectory_label = original_list_label[trajectory_tid]

        if trajectory_length < min_length:
            continue

        for i in range(trajectory_length - min_length + 1):
            
            length_k_sub_matrix_lol = [[] for _ in range(num_agents)]
        
            for j in range(min_length):
                for a in range(num_agents):
                    #list of lists format
                    length_k_sub_matrix_lol[a].append(trajectory_matrix[a][i + j])
            
            #shapely format
            length_k_sub_matrix = [[str(point[0]) + ' ' + str(point[1]) for point in agent_traj] for agent_traj in length_k_sub_matrix_lol]
            
            length_k_sub_matrix_mls = convert_list_of_lists_to_mls(length_k_sub_matrix_lol)
            
            potential_neighbor = find_length_k_potential_neighbor(trajectory_tid,
                                                                  length_k_sub_matrix,
                                                                  length_k_sub_matrix_lol,
                                                                  trajectory_table, 
                                                                  distance_threshold,
                                                                  num_agents)#, top_k)
            #print(potential_neighbor)
            
            list_neighbor = confirm_neighbor(length_k_sub_matrix_mls, potential_neighbor,
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
            #current_list_top_k_max = list_top_k_max

            dict_neighbor_full_trajectory = get_neighbor_trajectories(trajectory_table, current_list_neighbor_tid)

            root = []
            root.append([[trajectory_tid, candidate_start_idx, candidate_end_idx], current_list_neighbor_tid])

            while True:
                if candidate_end_idx == (trajectory_length - 1):
                    break

                candidate_end_idx = candidate_end_idx + 1

                list_new_candidate_neighbor = []
                # temp_list_top_k_max = []

                for neighbor_index in range(len(current_list_neighbor)):

                    neighbor = current_list_neighbor[neighbor_index]
                    #local_top_k_max = current_list_top_k_max[neighbor_index]

                    neighbor_tid = neighbor[0]
                    neighbor_start_idx = neighbor[1]
                    neighbor_end_idx = neighbor[2]

                    if neighbor_end_idx == (len(dict_neighbor_full_trajectory[(neighbor_tid,0)]) - 1):
                        # del dict_neighbor_full_trajectory[neighbor_tid]
                        continue

                    new_neighbor_start_idx = neighbor_start_idx
                    new_neighbor_end_idx = neighbor_end_idx + 1
                    
                    if num_agents == 1:
                        dist = np.linalg.norm(np.array(trajectory_matrix[0][candidate_end_idx]) - np.array(dict_neighbor_full_trajectory[(neighbor_tid,0)][new_neighbor_end_idx]))
                    elif num_agents > 1:
                        dist = calculate_hausdorff_distance([trajectory_matrix[a][candidate_end_idx] for a in range(num_agents)],
                                                 [dict_neighbor_full_trajectory[(neighbor_tid,a)][new_neighbor_end_idx] for a in range(num_agents)])

                    #if last_point_distance > local_top_k_max[0]:
                    #    local_top_k_max.append(last_point_distance)
                    #    local_top_k_max.sort()
                    #    local_top_k_max = local_top_k_max[1:]

                    # dist = sum(local_top_k_max) / min_length
                    #dist = sum(local_top_k_max) / top_k

                    # _, dist = max_euclidean.calculate_top_k(top_k,
                    #                                         trajectory[candidate_start_idx:(candidate_end_idx + 1)],
                    #                                         dict_neighbor_full_trajectory[neighbor_tid][
                    #                                             new_neighbor_start_idx:(new_neighbor_end_idx + 1)])

                    if dist <= distance_threshold:
                        list_new_candidate_neighbor.append(
                            [neighbor_tid, new_neighbor_start_idx, new_neighbor_end_idx])

                        # temp_list_top_k_max.append(local_top_k_max)

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
                # current_list_top_k_max = temp_list_top_k_max

                root.append([[trajectory_tid, candidate_start_idx, candidate_end_idx], current_list_neighbor_tid])

            list_tree.append({"candidate": json.dumps({'candidates_ma': root})})

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

    trajectory_table = 'trajectory_ma'
    point_table = 'point_ma'
    candidate_table = 'candidates_ma'

    positive_label = '1'
    negative_label = '0'
    max_iter = 1000
    min_length = 5
    alpha = 0.05
    distance_threshold = 7
    # top_k = 1
    num_agents = 1
    
    positive_number = count_label_number(trajectory_table, positive_label)
    negative_number = count_label_number(trajectory_table, negative_label)

    original_list_label = get_list_label(trajectory_table)
    original_list_label = np.array(original_list_label)
    original_list_label = original_list_label[:, 0].tolist()
    original_list_label = np.array(original_list_label)

    list_permuted_dataset = []
    list_min_p = []

    for i in range(max_iter):
        list_idx = np.random.permutation(len(original_list_label))
        permutation_list_label = original_list_label[list_idx]
        list_permuted_dataset.append(permutation_list_label)
        list_min_p.append(alpha)

    list_phase_tid = get_list_phase_tid(trajectory_table)
    list_phase_tid = np.array(list_phase_tid)
    list_phase_tid = list_phase_tid[:, 0].tolist()
    
    list_agent_aid = get_list_agent_aid(trajectory_table)
    list_agent_aid = np.array(list_agent_aid)
    list_agent_aid = list_agent_aid[:, 0].tolist()
    
    parameter = {
        "positive_label": positive_label,
        "negative_label": negative_label,
        "max_iter": max_iter,
        "min_length": min_length,
        "alpha": alpha,
        "distance_threshold": distance_threshold,
        # "top_k": top_k,
        "positive_number": positive_number,
        "negative_number": negative_number,
        "num_agents": num_agents
    }

    delta = ma_stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, list_agent_aid, parameter)

    print(delta)

    cur.close()
    conn.close()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
    
# TO EXPORT THE candidates_ma TABLE FROM POSTGRES TO A CSV FILE
# In postgres' psql shell, execute the following command \copy (SELECT * FROM candidates_ma) to '/.../candidates_ma.csv' with csv;
