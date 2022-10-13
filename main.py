import subprocess
import pandas as pd
import sys
import io
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('-f', '--file', type=str, required=True, dest='file_iterate')
# parser.add_argument('-r', '--run_type', type=str, required=True, , dest='run', help='mastatdsm or statdsm')
# parser.add_argument('-a', '--agents', type=str, required=True, , dest='agent_type', help='attackers or defenders')
# parser.add_argument('-p_min', '--p_minimum', type=int, required=True)
# parser.add_argument('-p_max', '--p_maximum', type=int, required=True)
# parser.add_argument('-d', '--dist_thresh', type=int, required=True, dest='distance_threshold')
# parser.add_argument('-l', '--min_l', type=int, required=True, dest='min_length')
# args, _ = parser.parse_known_args()
# file_to_iterate_over = args.file_iterate

# p of 2 means every second point from the original trajectory will be taken, p of 1 means every point from the original trajectory is retained, etc.
file_to_iterate_over = 'team_game_ids.csv' # 'team_game_ids.csv' or 'id_team.csv'
p_min = 4
p_max = 4
agent_type = 'attackers'
dist_threshold =  1.5 # 21.21320344
min_length = 5
run = 'mastatdsm'

p_list = [i for i in range(1,p_max+1)]
# set agent_list = ["shooter", "lastpasser"] to consider attackers, or set to agent_list = ["shooterdefender", "lastpasserdefender"] to consider defenders
if agent_type == 'attackers':
    if run == 'mastatdsm':
        agent_list = ["shooter", "lastpasser"]
    elif run == 'statdsm':
        agent_list = ["shooter"]
elif agent_type == 'defenders':
    if run == 'mastatdsm':
        agent_list = ["shooterdefender", "lastpasserdefender"]
    elif run == 'statdsm':
        agent_list = ["shooterdefender"]
else:
    sys.exit("ERROR: agent_type must be attackers or defenders")

# df consisting of all combinations of team_id and game_id from the original dataset, dataset_as_a_file_600_games.pkl
team_game_ids_df = pd.read_csv(file_to_iterate_over)
team_game_ids_df = team_game_ids_df.reset_index()

# iterate over all agents and all p parameter options, and all team_id/game_id combinations
for p in p_list:
    print(p)
    for index, row in team_game_ids_df.iterrows():
        print(index, row)
        if file_to_iterate_over == 'team_game_ids.csv':
            if run == 'mastatdsm':
                subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-g", str(row['game_id']), "-t", str(row['team_id'])])
            elif run == 'statdsm':
                subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], "-p", str(p), "-g", str(row['game_id']), "-t", str(row['team_id'])])
        elif file_to_iterate_over == 'id_team.csv':
            if run == 'mastatdsm':
                subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-t", str(row['team_id'])])
            elif run == 'statdsm':
                subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], "-p", str(p), "-t", str(row['team_id'])])
        else:
            sys.exit("ERROR: file_to_iterate_over must be team_game_ids.csv or id_team.csv.")

        proc = subprocess.run(["python", "ma_stat_dsm.py", "-d", str(dist_threshold), "-l", str(min_length)], capture_output=True, text=True)
        result = proc.stdout.strip("\n")
        delta = '\n'.join(result.splitlines()[-2:-1])

        if proc.returncode == 0:
            subprocess.run(["python", "significant_subtrajectories.py", "-d", delta], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # sys.exit("FINISHED. Significant subtrajectories found with delta: " + str(delta))
        #elif delta.returncode == 1:
