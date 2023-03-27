# Discriminative sub-trajectory mining of NBA basketball tracking data
This repository contains the code for a Multi-agent extension of Stat-DSM (Bunker et al., 2022), a statistically discriminative sub-trajectory mining method (Le Vo et al., 2020).

Standard Stat-DSM can still be run by running the method with just a single agent.

The Multi-agent Stat-DSM (MA-Stat-DSM) method is demonstrated on tracking data from NBA basketball to determine sub-matrices, comprised of player (and/or ball) sub-trajectories each of the same length from a matrix representing one play, which discriminate between effective and ineffective plays.

## Input Dataset
The input dataset, dataset_as_a_file_600_games.pkl, which is included in this repository, was generated based on "for Stat-DSM preprocessing" in https://github.com/keisuke198619/team_representation, which was, in turn, sourced from data from https://github.com/rajshah4/BasketballData

## Create the Environment
Create the environment using the environment.yml file.

If you are running on your local machine you can use Anaconda. Then, it is recommended to install mamba
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

## Step 1: Data Preprocessing

For all steps below, dataset_as_a_file_600_games.pkl must be in the same directory as the python scripts data_preprocess.py, ma_stat_dsm.py, and calculate_sig_subtraj.py as well as max_euclidean.py.

### data_preprocess.py:    
All arguments are optional, however, to reduce run time, it is recommended to run for a single team and to downsample by using, e.g., -p 4.\
\
  -y, --label. Set to effective for effective/ineffective or to scored for scored/did not score label (default is effective)\
  -r, --init_rows. Set some number of initial rows, which is useful for testing (the final number of plays in the dataset will be less, and will be printed once the script has finished running).\
  -a, --a_list. List of agents from ball shooter
                        shooterdefender lastpasser lastpasserdefender\
  -ti, --time_int. The time interval, t1 or t2, as shown in the diagram below (default is t2)\
  -p, --xth_point. Downsample by considering only every xth point from
                        the trajectories (the default is 1, i.e., include every
                        point)\
  -g, --game_id. Specify a particular match id (default is all matches)\
  -t, --team. Specify a particular team id, e.g., Cleveland 1610612739, Golden State Warriors 1610612744 (default is all teams)\
  -i, --import_only. If this is set to Y, the csv files to run MA-Stat-DSM are not created from the dataset_as_a_file_600_games.pkl file - only the importing takes place. This is useful if you want to run the process on test/synthetic trajectories, or trajectories other than the basketball trajectories from dataset_as_a_file_600_games.pkl.
  
To run for Cleveland attacking player trajectories, with every fourth point, from all Cleveland matches:
```
python data_preprocess.py -p 4 -t 1610612739 -a shooter lastpasser
```
To run for defending player trajectories, with every fifth point, from all Golden State Warriors matches:
```
python data_preprocess.py -p 5 -t 1610612744 -a shooterdefender lastpasserdefender
```
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running (MA-)Stat-DSM
The agent list should match the agents that were specified in Step 1 above (data_preprocess.py).

If only one agent is specified, Stat-DSM will be run. If more than one agent is specified, MA-Stat-DSM will be run.

### ma_stat_dsm.py:  
#### Required:
-agents --a_list. List of agents from 0 1 2 3 4 corresponding to ball, shooter, lastpasser, shooterdefender, lastpasserdefender (should match the agents that were specified in Step 1 (data_preprocess.py).  \
-l, --min_l. Minimum trajectory length, e.g., 5\
-d, --dist_threshold. Distance threshold, e.g., 1.5

#### Optional:
In principle, these parameters do not need to be changed.\
-p, --pos_label. default='1'\
-n, --neg_label, default='0'\
-i, --max_it. default=1000 maximum number of iterations\
-a, --alph. Statistical significance level (alpha). Default is alpha = 0.05

E.g., running MA-Stat-DSM with minimum length 5 and distance threshold 1.5 for the attacking players (specifying -agents 1 2 matches -a shooter lastpasser from Step 1):
```
python ma_stat_dsm.py -l 5 -d 1.5 -agents 1 2
```
## Step 3: Identifying statistically significant discriminative sub-trajectories
### significant_subtrajectories.py:  
#### Required:
-d, --delta. The delta* value that was printed upon completion of ma_stat_dsm.py.
```
python significant_subtrajectories.py -d 0.0344542453452345
```

## Finding discriminative subtrajectories
### run.sh:  
Running steps 1 to 3 on for an ad-hoc team or match will be unlikely to discover statistically significant subtrajectories.

In run.sh, we iterate over different parameters until a statistically singificant subtrajectories are found — at which point the process stops (TO DO: continue the process to discover additional statistically singificant subtrajectories). 

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
