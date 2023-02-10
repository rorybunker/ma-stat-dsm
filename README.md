# Multi-Agent Discriminative Sub-trajectory Mining
This repository contains the code for a Multi-agent extension of Stat-DSM (Bunker et al., 2022), a statistically discriminative sub-trajectory mining method (Le Vo et al., 2020).

Standard Stat-DSM can still be run by running the method with just a single agent.

The Multi-agent Stat-DSM (MA-Stat-DSM) method is demonstrated on tracking data from NBA basketball to determine sub-matrices, comprised of player (and/or ball) sub-trajectories each of the same length from a matrix representing one play, which discriminate between effective and ineffective plays.

## Dataset
The input NBA dataset, dataset_as_a_file_600_games.pkl was generated based on "for Stat-DSM preprocessing" in https://github.com/keisuke198619/team_representation, which was, in turn, sourced from data from https://github.com/rajshah4/BasketballData

## Environment
Create the environment using the environment.yml file.

If you are running on your local machine, you can use Anaconda. Then, it is recommended to install mamba
```
conda install mamba -n base -c conda-forge
```
Then, create the environment based on the environment.yml file:
```
mamba env create -n geoenv -f environment.yml
```

## Create the PostgreSQL database
Install PostgreSQL and create a PostgreSQL database with: dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port = 5432. 

Then, to create the required database tables necessary to run steps 1 - 3 below, run
```
python create_postgresql_db.py
```
## Data for (MA-)Stat-DSM
You can run nba_data_preprocess.py to generate the point_ma.csv and trajectory_ma.csv files from the NBA data, on which MA-Stat-DSM will be run. 

If nba_data_preprocess.py is run with only one agent, point.csv and trajectory.csv files will be generated and Stat-DSM will be run in the next step.

Alternatively, you can provide your own point and trajectory files with the same structure.

## NBA Data Preprocessing

### nba_data_preprocess.py:    
To reduce run time, we run for a single team and downsample by using, e.g., -d 2, which considers every second point.\
\
'-y', '--label'. Effective - for effective/ineffective label, score - for scored/did not score label, attempt - for attempted shot/did not attempt shot label (default=effective).\
'-a', '--a_list'. List of agents from ball shooter lastpasser shooterdefender lastpasserdefender (default is all agents).
'-i', '--time_int'. t1 or t2 (default=t2). See the diagram below.\
'-d', '--downsampling'. Downsample by considering only every ith point from the trajectories (default=1, i.e., include every point).\
'-g', '--game_id'. Specify a particular match id (default is all matches).\
'-t', '--team. Specify a particular team id, e.g., Cleveland 1610612739 or Golden State Warriors 1610612744 (default = all teams).
  
For example, to create point_ma.csv and trajectory_ma.csv files for one Cleveland match:
```
python -u nba_data_preprocess.py -t 1610612739 -g 21500405
```
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running (MA-)Stat-DSM
The agent list should match the agents that were specified in Step 1 above (data_preprocess.py).

If only one agent is specified, Stat-DSM will be run. If more than one agent is specified, MA-Stat-DSM will be run.

### ma_stat_dsm.py:  
#### Required:
'-p', '--pos_label'. default='1'\
'-n', '--neg_label'. default='0'\
'-i', '--max_it'. Maximum number of iterations (default=1000)\
'-a', '--alph'. Statistical significance level (alpha). default is alpha = 0.05.\
'-l', '--min_l'. Minimum trajectory length, e.g., 5 (required).\
'-d', '--dist_threshold'. Distance threshold, e.g., 1.5 (required).
'-b', '--hausdorff_base_dist'. Options for the base distance are euclidean, manhattan, chebyshev, or cosine (default is euclidean).\
'-s', '--seed'. Random seed (default = 0 for reproducability)')

For example, running MA-Stat-DSM with minimum length 5 and distance threshold 1.5:
```
python -u ma_stat_dsm.py -l 5 -d 1.5
```
## Step 3: Identifying statistically significant discriminative sub-trajectories
### significant_subtrajectories.py:
-d, --delta. The delta* value that was printed upon completion of ma_stat_dsm.py.
```
python -u significant_subtrajectories.py -d 0.0344542453452345
```

## Finding discriminative subtrajectories
### run.sh:  
In run.sh, we iterate over different parameters searching for statistically significant discriminative sub-trajectories.

To run as a batch process, where million2 is the name of the server where postgres is installed, first create the permissions on the shell scipt:
```
chmod 777 run.sh
```
Then run the shell script:
```
sbatch -w million2 ./run.sh
```
# References

Bunker, R. P., Le Vo, D. N., & Fujii, K. (2022). Multi-agent Statistically Discriminative Trajectory Mining and an Application to NBA Basketball. Working Paper.

Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
