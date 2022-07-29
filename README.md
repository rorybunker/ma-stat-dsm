# Discriminative sub-trajectory mining of NBA basketball tracking data
This repository contains an extended version of Stat-DSM, the statistically discriminative sub-trajectory mining method of method of Le Vo et al. (2020), which enables Stat-DSM to be run with the trajectories of multiple agents rather than only one (the original Stat-DSM can still be run for a single agent).

The method is illustrated in the context of sports, specificially NBA basketball, where the method can be used to determine discriminative sub-trajectories within labelled trajectories of multiple players and the ball.

## Step 0: Set up PostgreSQL database environment

Anaconda is required. Then, it is recommended to install mamba
```
conda install mamba -n base -c conda-forge
```
Then, create an environment based on the environment.yml file:
```
mamba env create -n geoenv -f environment.yml
```
And then activate the created environment
```
conda activate geoenv
```
Install PostgreSQL and create a PostgreSQL database with: dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port = 5432.\ Then, to create the required database tables necessary to run steps 1 - 3 below, run
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
  -t, --team. Specify a particular team id, e.g., Cleveland 1610612739, Golden State Warriors 1610612744 (default is all teams)
```
python data_preprocess.py -p 4 -t 1610612739 -a shooter lastpasser
```
```
python data_preprocess.py -p 4 -t 1610612744 -a shooter lastpasser
```
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running (MA-)Stat-DSM
If only one agent was specified in -a/--a_list in Step 1, Stat-DSM will be run; otherwise, MA-Stat-DSM will be run.
### ma_stat_dsm.py:  
#### Required:
-l, --min_l. Minimum trajectory length, e.g., 5\
-d, --dist_threshold. Distance threshold, e.g., 1.5

#### Optional:
In principle, these parameters do not need to be changed.\
-p, --pos_label. default='1'\
-n, --neg_label, default='0'\
-i, --max_it. default=1000 maximum number of iterations\
-a, --alph. Statistical significance level (alpha). Default is alpha = 0.05
```
python ma_stat_dsm.py -l 5 -d 1.5
```
## Step 3: Obtaining statistically significant discriminative sub-trajectories
### calculate_sig_subtraj.py:  
#### Required:
-d, --delta. The delta* value that was printed upon completion of ma_stat_dsm.py.
```
python calculate_sig_subtraj.py -d 0.0344542453452345
```

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
