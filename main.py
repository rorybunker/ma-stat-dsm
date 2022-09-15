import subprocess
import pandas as pd

p_list = [i for i in range(1,2)]
agent_list = ["shooter", "lastpasser"]

team_game_ids_df = pd.read_csv('team_game_ids.csv')
team_game_ids_df = team_game_ids_df.reset_index()

for agent in agent_list:
    for p in p_list:
        for index, row in team_game_ids_df.iterrows():
            subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-g", str(row['game_id']), "-t", str(row['team_id'])])
            delta = subprocess.run(["python", "ma_stat_dsm.py", "-d", "1.5", "-l", "5"], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if delta.returncode != 0:
                subprocess.run(["python", "significant_subtrajectories.py", "-d", str(delta)], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif delta.returncode == 1:
                break