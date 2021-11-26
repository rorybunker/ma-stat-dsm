#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 13:21:31 2021

@author: rorybunker
"""
import 1_create_point_and_trajectory_tables

def plot_trajectory_on_court(phase_num, index_array, save_fig=False):
    if phase_num not in indices:
        print('Cannot plot that play')
    else:
        court_path ='/Users/rorybunker/Google Drive/Research/Applying discriminative sub-trajectory mining to spatio-temporal data in sport/data/basketball_scoring/nba_court_T.png'
        feet_m = 0.3048 
        img = mpimg.imread(court_path) 
        plt.imshow(img, extent=[0,94*feet_m,0,50*feet_m], zorder=0) 
        plt.xlim(0,47*feet_m)  
        plt.ylim(0,50*feet_m)   
      
        plt.plot((ball_df.loc[phase_num]['x']).interpolate()
                 ,(ball_df.loc[phase_num]['y']).interpolate(),label='b',zorder=1)
        plt.plot((offense_df.loc[phase_num]['x']).interpolate()
                 ,(offense_df.loc[phase_num]['y']).interpolate(),label='s',zorder=1)
        plt.plot((defense_df.loc[phase_num]['x']).interpolate()
                 ,(defense_df.loc[phase_num]['y']).interpolate(),label='sd',zorder=1)
        plt.plot((offense_lp_df.loc[phase_num]['x']).interpolate()
                 ,(offense_lp_df.loc[phase_num]['y']).interpolate(),label='lp',zorder=1)
        plt.plot((defense_lp_df.loc[phase_num]['x']).interpolate()
                 ,(defense_lp_df.loc[phase_num]['y']).interpolate(),label='lpd',zorder=1)
        
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.annotate("b", ((ball_df.loc[phase_num]['x']).iloc[0],
                            (ball_df.loc[phase_num]['y']).iloc[0]), zorder=2)
        plt.annotate("s", ((offense_df.loc[phase_num]['x']).iloc[0],
                            (offense_df.loc[phase_num]['y']).iloc[0]), zorder=2)
        plt.annotate("sd", ((defense_df.loc[phase_num]['x']).iloc[0],
                            (defense_df.loc[phase_num]['y']).iloc[0]), zorder=2)
        plt.annotate("lp", ((offense_lp_df.loc[phase_num]['x']).iloc[0],
                            (offense_lp_df.loc[phase_num]['y']).iloc[0]), zorder=2)
        plt.annotate("lpd", ((defense_lp_df.loc[phase_num]['x']).iloc[0],
                            (defense_lp_df.loc[phase_num]['y']).iloc[0]), zorder=2)

        if int(effective[(phase_num,)])==1 and int(scored[(phase_num,)])>0:
            plt.title("play #" + str(phase_num) + " " + "(effective, scored" + " " 
                      + str(int(scored[(phase_num,)])) + " pts)")
        elif int(effective[(phase_num,)])==0 and int(scored[(phase_num,)])>0:
            plt.title("play #" + str(phase_num) + " " + "(ineffective, scored" + " " 
                      + str(int(scored[(phase_num,)])) + " pts)")
        elif int(effective[(phase_num,)])==0 and int(scored[(phase_num,)])==0:
            plt.title("play #" + str(phase_num) + " " + "(ineffective, no score)")
        elif int(effective[(phase_num,)])==1 and int(scored[(phase_num,)])==0:
            plt.title("play #" + str(phase_num) + " " + "(effective, no score)")
        #plt.show()
        
        if save_fig == True:
            plt.savefig(str(phase_num) + '.png')
            plt.show()
        else:
            plt.show()
        plt.clf()
        
plot_trajectory_on_court(2444, indices, True)