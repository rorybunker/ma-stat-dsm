import subprocess
import pandas as pd
import sys
import io
import itertools

p = 5 # 1, 2, 3, 4, 5
agent_type = 'attackers' # 'attackers' or 'defenders'
dist_threshold_list = [1.5, 4, 20] # max is 21.21320344
min_length_list = [5, 8, 10] #[5, 8, 10]
run = 'mastatdsm' # 'mastatdsm' or 'statdsm'
team_id = 1610612744 # Cleveland 1610612739, Golden State Warriors 1610612744
max_iterations_list = [250, 500, 750, 1000]

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

print('Running data_preprocess.py...')
if run == 'mastatdsm':
    subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], agent_list[1], "-p", str(p), "-t", str(team_id)])
elif run == 'statdsm':
    subprocess.run(["python", "data_preprocess.py", "-a", agent_list[0], "-p", str(p), "-t", str(team_id)])
print('Finished data_preprocess.py.')

for dist_threshold, min_length, max_iteration in itertools.product(dist_threshold_list, min_length_list, max_iterations_list):
    print('Running ma_stat_dsm.py...')
    proc = subprocess.run(["python", "ma_stat_dsm.py", "-d", str(dist_threshold), "-l", str(min_length), "-agents", ' '.join(str(agent_list_ints)), "-i", str(max_iteration)], capture_output=True, text=True)
    result = proc.stdout.strip("\n")
    delta = '\n'.join(result.splitlines()[-2:-1])
    print(result)
    print('Finished ma_stat_dsm.py.')
    if delta != 'FAIL':
        print('Running significant_subtrajectories.py...')
        subprocess.run(["python", "significant_subtrajectories.py", "-d", delta], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.exit("Finished significant_subtrajectories.py. Significant subtrajectories were found with delta: " + str(delta))
    else:
        print("Finished significant_subtrajectories.py. No significant subtrajectories were found.")
