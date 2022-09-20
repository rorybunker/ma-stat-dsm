import subprocess
import pandas as pd
import sys

# p of 2 means every second point from the original trajectory will be taken, p of 1 means every point from the original trajectory is retained, etc.
file_to_iterate_over = 'id_team.csv' # 'team_game_ids.csv' or 'id_team.csv'
p_min = 1
p_max = 10
p_list = [i for i in range(1,p_max+1)]
agent_type = 'defenders'
# set agent_list = ["shooter", "lastpasser"] to consider attackers, or set to agent_list = ["shooterdefender", "lastpasserdefender"] to consider defenders
if agent_type == 'attackers':
    agent_list = ["shooter", "lastpasser"]
elif agent_type == 'defenders':
    agent_list = ["shooterdefender", "lastpasserdefender"]
else:
    sys.exit("ERROR: agent_type must be attackers or defenders")

# df consisting of all combinations of team_id and game_id from the original dataset, dataset_as_a_file_600_games.pkl
team_game_ids_df = pd.read_csv(file_to_iterate_over)
team_game_ids_df = team_game_ids_df.reset_index()

# iterate over all agents and all p parameter options, and all team_id/game_id combinations
for p in p_list:
    for index, row in team_game_ids_df.iterrows():
        # subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-g", str(row['game_id']), "-t", str(row['team_id'])])
        subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-t", str(row['team_id'])])
        delta = subprocess.run(["python", "ma_stat_dsm.py", "-d", "1.5", "-l", "5"], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if delta.returncode != 0:
            subprocess.run(["python", "significant_subtrajectories.py", "-d", str(delta)], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif delta.returncode == 1:
            sys.exit("FINISHED. Significant subtrajectories found with delta: " + str(delta))
            # append record(s) to discriminative_subtraj postgres table and continue processing
