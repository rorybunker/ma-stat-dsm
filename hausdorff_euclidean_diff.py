#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 15:43:48 2021

@author: rorybunker
"""

import numpy as np
from hausdorff import hausdorff_distance
import csv
import max_euclidean

def calculate_hausdorff_distance(agent_df, play_indx1, play_indx2, base_distance):
  # options for base_distance are 'euclidean', 'manhattan', 'chebyshev', 'cosine'
  h = hausdorff_distance(np.array(agent_df.loc[play_indx1][['x','y']]), 
                     np.array(agent_df.loc[play_indx2][['x','y']]), 
                     distance=base_distance)
  return h


def write_dist_diff_csv(agent_df):
    # create unique index list for the agent dataframe
    indx_list = []
    for indx in agent_df.index:
        if indx not in indx_list:
            indx_list.append(indx)

    i = 0
    j = 1
    with open('hausdorff_euclidean_diffs.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        # csv column header names
        writer.writerow(['traj1', 'traj2', 'hausd', 'eucld', 'diff'])
        for i in range(0,len(indx_list)-1):
            for j in range(1,len(indx_list)):
                if i == j:
                    continue
                else:
                    hd = calculate_hausdorff_distance(agent_df, 
                                                 indx_list[i], 
                                                 indx_list[j], 
                                                 'euclidean')
                    
                    list_max, ed = max_euclidean.calculate_top_k(1,
                                   np.array(agent_df.loc[indx_list[i]][['x','y']]), 
                                   np.array(agent_df.loc[indx_list[j]][['x','y']]))
                    
                    writer.writerow([indx_list[i], indx_list[j], hd, ed, hd-ed])
                

write_dist_diff_csv(offense_df)
