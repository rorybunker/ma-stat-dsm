import subprocess
import pandas as pd
import sys
import io
import itertools

p = 5 # 1, 2, 3, 4, 5
agent_type = 'attackers' # 'defenders'
# dist_threshold_list = [1.5, 4, 20] # 21.21320344
dist_threshold = 1.5
min_length = 5
# min_length_list = [5, 8, 10] #[5, 8, 10]
run = 'mastatdsm' # 'mastatdsm' or 'statdsm'
team_id = 1610612739 # Cleveland 1610612739, Golden State Warriors 1610612744
# max_iterations_list = [250, 500, 750, 1000]
max_iteration = 1000
sig_level_list = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
game_id_list = [21500499,
21500511,
21500527,
21500543,
21500559,
21500575,
21500601,
21500622,
21500011,
21500021,
21500046,
21500063,
21500078,
21500094,
21500106,
21500130,
21500141,
21500160,
21500176,
21500191,
21500203,
21500219,
21500227,
21500262,
21500288,
21500313,
21500334,
21500367,
21500384,
21500405,
21500424,
21500438,
21500453,
21500466,
21500473,
21500291]

if agent_type == 'attackers':
    if run == 'mastatdsm':
        agent_list = ["shooter", "lastpasser"]
        agent_list_ints = [1, 2]
    elif run == 'statdsm':
        agent_list = ["shooter"]
        agent_list_ints = [1]
elif agent_type == 'defenders':
    if run == 'mastatdsm':
        agent_list = ["shooterdefender", "lastpasserdefender"]
        agent_list_ints = [3, 4]
    elif run == 'statdsm':
        agent_list = ["shooterdefender"]
        agent_list_ints = [3]
else:
    sys.exit("ERROR: agent_type must be attackers or defenders")

# for game_id in game_id_list:
print(game_id_list[0])
print('Running data_preprocess.py...')
if run == 'mastatdsm':
    completed_process = subprocess.run(["python", "data_preprocess.py", "-g", str(game_id_list[0]), "-a", agent_list[0], agent_list[1], "-p", str(p), "-t", str(team_id)], shell=True, check=True, cwd='/home/b_rory/workspace2/work/ma_stat_dsm')
elif run == 'statdsm':
    completed_process = subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], "-p", str(p), "-t", str(team_id)], shell=True, check=True, cwd='/home/b_rory/workspace2/work/ma_stat_dsm')
if completed_process.returncode == 0:
    print('Finished data_preprocess.py.')

# for dist_threshold, min_length, max_iteration in itertools.product(dist_threshold_list, min_length_list, max_iterations_list):
# for sig_level in sig_level_list:
# python data_preprocess.py -g 21500511 -a shooter lastpasser -p 5  -t 1610612739
# python ma_stat_dsm.py -alpha 0.5 -d 21 -l 2 -agents 1 2 -i 1000
print(sig_level_list[5])
print('Running ma_stat_dsm.py...')
completed_process = subprocess.run(["python", "ma_stat_dsm.py", "-alpha", str(sig_level_list[5]), "-d", str(dist_threshold), "-l", str(min_length), "-agents", ' '.join(str(agent_list_ints)), "-i", str(max_iteration)], capture_output=True, text=True)
result = completed_process.stdout.strip("\n")
delta = '\n'.join(result.splitlines()[-2:-1])
print(result)
print('Finished ma_stat_dsm.py.')

if delta != 'FAIL':
    print('Running significant_subtrajectories.py...')
    completed_process = subprocess.run(["python", "significant_subtrajectories.py", "-d", delta], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    sys.exit("Finished significant_subtrajectories.py. Significant subtrajectories were found with delta: " + str(delta))
else:
    print("Finished significant_subtrajectories.py. No significant subtrajectories were found.")
