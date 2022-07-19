import psycopg2
import json
import time
import numpy as np
import pandas as pd
import sys
sys.setrecursionlimit(10000)

import os
os.chdir("/Users/rorybunker")

import max_euclidean
from scipy.special import comb
from shapely.geometry import LineString
from hausdorff import hausdorff_distance

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='1234'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def calculate_hausdorff_distance(X, Y, base_dist = 'euclidean'):
    h_dist = hausdorff_distance(np.array(X), np.array(Y), base_dist)
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

def get_list_phase_tid(table_name):
    sql = """select distinct tid from """ + str(table_name) + """ order by tid asc"""

    cur.execute(sql)
    rows = cur.fetchall()
    return rows

def get_trajectory(trajectory_table, tid, agent_ids):
    if len(agent_ids) == 1:
        sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + ""
    elif len(agent_ids) > 1:
        sql = """select ST_AsGeoJSON(geom) from """ + str(trajectory_table) + """ where tid = """ + str(tid) + """ and aid in (""" + ', '.join(map(str, agent_ids)) + ")"

    cur.execute(sql)
    rows = cur.fetchall()

    if len(agent_ids) == 1:
        return json.loads(rows[0][0])['coordinates']
    elif len(agent_ids) > 1:
        return [json.loads(rows[a][0])['coordinates'] for a in range(len(agent_ids))]

def find_length_k_potential_neighbor(trajectory_tid, length_k_sub_trajectory, point_table, distance_threshold, top_k, agent_ids):
    distance_threshold = distance_threshold * top_k
    total_length_k_potential_neighbor = [] # [[tid, trajectory], ...]
    length = len(length_k_sub_trajectory)

    if len(agent_ids) == 1:

        sql = """select tid, pid, label, ST_AsGeoJSON(geom) from """ + str(point_table) + """
                where tid != """ + str(trajectory_tid) + """
                and """
            
        count = 0
        for point in length_k_sub_trajectory:
            count = count + 1
    
            if count == 1:
                sql = sql + """ (ST_DWithin('POINT(""" + str(point[0]) + " " + str(
                    point[1]) + """)'::geometry, geom, """ + str(
                    distance_threshold) + """) or """
    
                continue
    
            if count == length:
                sql = sql + """ ST_DWithin('POINT(""" + str(point[0]) + " " + str(
                    point[1]) + """)'::geometry, geom, """ + str(
                    distance_threshold) + """)) ORDER BY tid ASC, pid ASC;"""
    
                break
    
            sql = sql + """ ST_DWithin('POINT(""" + str(point[0]) + " " + str(point[1]) + """)'::geometry, geom, """ + str(
                distance_threshold) + """) or """

    elif len(agent_ids) > 1:
        
        sql = """select tid, aid, pid, label, ST_AsGeoJSON(geom) from """ + str(point_table) + """
                where aid in (""" + ', '.join(map(str, agent_ids)) + ")"" and tid != """ + str(trajectory_tid) + """
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
    
    if len(agent_ids) > 1:
        length = len(length_k_sub_trajectory[0])
    
    while s < (len(nearest_points) - length):
        s = s + 1
        current_point = list(nearest_points[s])

        if len(potential_neighbor) == 0:
            if len(agent_ids) > 1:
                potential_neighbor.append(json.loads(current_point[4])['coordinates'])
            elif len(agent_ids) == 1:
                potential_neighbor.append(json.loads(current_point[3])['coordinates'])
                
        while (e - s + 1) < length:
            e = e + 1

            end_point = list(nearest_points[e])
            if len(agent_ids) == 1:
                if (list(nearest_points[e - 1])[0] == end_point[0]) and (end_point[1] == list(nearest_points[e - 1])[1] + 1):
                    potential_neighbor.append(json.loads(end_point[3])['coordinates'])
            elif len(agent_ids) > 1:
                if (list(nearest_points[e - 1])[0] == end_point[0]) and (end_point[2] == list(nearest_points[e - 1])[2] + 1):
                    potential_neighbor.append(json.loads(end_point[4])['coordinates'])
            else:
                break

        if len(potential_neighbor) == length:
            if len(agent_ids) == 1:
                total_length_k_potential_neighbor.append([[current_point[0], current_point[1], list(nearest_points[e])[1]],
                                                          potential_neighbor])
            elif len(agent_ids) > 1:
                total_length_k_potential_neighbor.append([[current_point[0], current_point[1], current_point[2], list(nearest_points[e])[2]],
                                                          potential_neighbor])
            potential_neighbor = potential_neighbor[1:]
        else:
            s = e - 1
            potential_neighbor = []

    return total_length_k_potential_neighbor


def confirm_neighbor_hausdorff(length_k_sub_trajectory, list_potential_neighbor, distance_threshold):
    list_neighbor = []
    # Each potential neighbor: [[2, 0, 1], [[5.5, 14], [7, 14]]]

    for potential_neighbor in list_potential_neighbor:
            max_distance = calculate_hausdorff_distance(np.array(length_k_sub_trajectory).reshape(np.array(length_k_sub_trajectory).shape[0]*np.array(length_k_sub_trajectory).shape[1], np.array(length_k_sub_trajectory).shape[2]),
                                                                potential_neighbor[1])
            if max_distance <= distance_threshold:
                list_neighbor.append(potential_neighbor[0])
                #list_top_k_max.append(top_k_max)
            
    return list_neighbor

def confirm_neighbor_euclidean(top_k, length_k_sub_trajectory, list_potential_neighbor, distance_threshold):
    list_neighbor = []
    list_top_k_max = []

    # Each potential neighbor: [[2, 0, 1], [[5.5, 14], [7, 14]]]

    for potential_neighbor in list_potential_neighbor:
            top_k_max, max_distance = max_euclidean.calculate_top_k(top_k, length_k_sub_trajectory,
                                                                    potential_neighbor[1])
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


def calculate_lower_p_value(positive_support, negative_support, positive_number, negative_number, current_min_p):

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


def stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, parameter):
    min_length = parameter["min_length"]
    distance_threshold = parameter["distance_threshold"]
    top_k = parameter["top_k"]
    positive_number = parameter["positive_number"]
    negative_number = parameter["negative_number"]
    max_iter = parameter["max_iter"]
    alpha = parameter["alpha"]
    positive_label = parameter["positive_label"]
    agent_ids = parameter["agent_ids"]
    
    dict_lower_bound = {}

    for trajectory_tid in list_phase_tid:
        print(trajectory_tid)

        list_tree = []

        trajectory = get_trajectory(trajectory_table, trajectory_tid, agent_ids)
        
        if len(agent_ids) == 1:
            trajectory_length = len(trajectory)
        elif len(agent_ids) > 1:
            trajectory_length = len(trajectory[0])
        
        trajectory_label = original_list_label[trajectory_tid]

        if trajectory_length < min_length:
            continue

        for i in range(trajectory_length - min_length + 1):
            if len(agent_ids) == 1:
                length_k_sub_trajectory = []
            elif len(agent_ids) > 1:
                length_k_sub_trajectory = [[] for a in range(len(agent_ids))]
      
            for j in range(min_length):
                if len(agent_ids) == 1:
                    length_k_sub_trajectory.append(trajectory[i + j])
                elif len(agent_ids) > 1:   
                    [length_k_sub_trajectory[a].append(trajectory[a][i + j]) for a in range(len(agent_ids))]

            potential_neighbor = find_length_k_potential_neighbor(trajectory_tid, length_k_sub_trajectory, point_table, distance_threshold, top_k, agent_ids)
            
            if len(agent_ids) == 1:
                list_top_k_max, list_neighbor = confirm_neighbor_euclidean(top_k, length_k_sub_trajectory, potential_neighbor,
                                                                 distance_threshold)
            elif len(agent_ids) > 1:
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
            if len(agent_ids) == 1:
                current_list_top_k_max = list_top_k_max
                dict_neighbor_full_trajectory = get_neighbor_trajectories(trajectory_table, current_list_neighbor_tid)
            if len(agent_ids) > 1:
                dict_neighbor_full_trajectory_ma = get_neighbor_ma_trajectories(trajectory_table, current_list_neighbor_tid)
            
            root = []
            root.append([[trajectory_tid, candidate_start_idx, candidate_end_idx], current_list_neighbor_tid])

            while True:
                if candidate_end_idx == (trajectory_length - 1):
                    break

                candidate_end_idx = candidate_end_idx + 1

                list_new_candidate_neighbor = []
                if len(agent_ids) == 1:
                    temp_list_top_k_max = []

                for neighbor_index in range(len(current_list_neighbor)):

                    neighbor = current_list_neighbor[neighbor_index]
                    if len(agent_ids) == 1:
                        local_top_k_max = current_list_top_k_max[neighbor_index]

                    neighbor_tid = neighbor[0]
                    neighbor_start_idx = neighbor[1]
                    neighbor_end_idx = neighbor[2]
                    
                    if len(agent_ids) == 1:
                        if neighbor_end_idx == (len(dict_neighbor_full_trajectory[neighbor_tid]) - 1):
                        # del dict_neighbor_full_trajectory[neighbor_tid]
                            continue
                    elif len(agent_ids) > 1:
                        if neighbor_end_idx == (len(dict_neighbor_full_trajectory_ma[(neighbor_tid,0)]) - 1):
                        # del dict_neighbor_full_trajectory[neighbor_tid]
                            continue

                    new_neighbor_start_idx = neighbor_start_idx
                    new_neighbor_end_idx = neighbor_end_idx + 1

                    if len(agent_ids) == 1:
                        last_point_distance = max_euclidean. \
                            calculate_point_distance(trajectory[candidate_end_idx],
                                                     dict_neighbor_full_trajectory[neighbor_tid][new_neighbor_end_idx])
                    elif len(agent_ids) > 1:
                        last_point_distance_h = calculate_hausdorff_distance([trajectory[a][candidate_end_idx] for a in range(len(agent_ids))],
                                                 [dict_neighbor_full_trajectory_ma[(neighbor_tid,a)][new_neighbor_end_idx] for a in range(len(agent_ids))])
                    
                    if len(agent_ids) == 1:
                        if last_point_distance > local_top_k_max[0]:
                            local_top_k_max.append(last_point_distance)
                            local_top_k_max.sort()
                            local_top_k_max = local_top_k_max[1:]

                    # dist = sum(local_top_k_max) / min_length
                    if len(agent_ids) == 1:
                        dist = sum(local_top_k_max) / top_k
                    elif len(agent_ids) > 1:
                        dist = last_point_distance_h

                    # _, dist = max_euclidean.calculate_top_k(top_k,
                    #                                         trajectory[candidate_start_idx:(candidate_end_idx + 1)],
                    #                                         dict_neighbor_full_trajectory[neighbor_tid][
                    #                                             new_neighbor_start_idx:(new_neighbor_end_idx + 1)])

                    if dist <= distance_threshold:
                        list_new_candidate_neighbor.append(
                            [neighbor_tid, new_neighbor_start_idx, new_neighbor_end_idx])
                        
                        if len(agent_ids) == 1:
                            temp_list_top_k_max.append(local_top_k_max)

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
                if len(agent_ids) == 1:
                    current_list_top_k_max = temp_list_top_k_max

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
    
    positive_label = '1'
    negative_label = '0'
    max_iter = 1000
    # set min_length, e.g., between 2 and 50
    min_length = 5
    alpha = 0.05
    # set distance_threshold, e.g., between 1.5 and 25
    distance_threshold = 1.5
    top_k = 1
    # set agent_ids to a list with a single element if running for statdsm or any subset from [0, 1, 2, 3, 4] for mastatdsm
    agent_ids = [1, 3]
    
    candidate_table = 'candidates'

    if len(agent_ids) == 1:
        point_table = 'point'
        trajectory_table = 'trajectory'
    elif len(agent_ids) > 1:
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

    for i in range(max_iter):
        list_idx = np.random.permutation(len(original_list_label))
        permutation_list_label = original_list_label[list_idx]
        list_permuted_dataset.append(permutation_list_label)
        list_min_p.append(alpha)
        
    list_phase_tid = get_list_phase_tid(trajectory_table)
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
        "agent_ids": agent_ids
    }

    delta = stat_dsm(trajectory_table, point_table, candidate_table, original_list_label, list_permuted_dataset, list_min_p, list_phase_tid, parameter)

    print(delta)
    
    candidates_df = pd.read_sql("SELECT * FROM candidates", conn)
    candidates_df.to_csv('candidates.csv')
    
    cur.close()
    conn.close()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
