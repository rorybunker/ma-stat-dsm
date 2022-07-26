# Discriminative sub-trajectory mining of NBA basketball tracking data
This repository contains an extended version of Stat-DSM, the statistically discriminative sub-trajectory mining method of method of Le Vo et al. (2020), which enables Stat-DSM to be run with the trajectories of multiple agents rather than only one (the original Stat-DSM can still be run for a single agent).

The method is illustrated in the context of sports, specificially NBA basketball, where the method can be used to determine discriminative sub-trajectories within labelled trajectories of multiple players and the ball.

## Step 0: Setting up PostgreSQL database environment
1. Install PostgreSQL https://www.postgresql.org/download/, which also includes pgAdmin (on Mac it is recommended to also install https://postgresapp.com/).
2. Create a PostgreSQL database with: dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port = 5432.
3. In pgadmin, run the queries in 0-create-postgres-database.sql to create the required database tables.

For all steps below, dataset_as_a_file_600_games.pkl must be in the same directory as the python scripts data_preprocess.py, ma_stat_dsm.py, and calculate_sig_subtraj.py.

## Step 1: Data preprocessing for Stat-DSM/MA-Stat-DSM 
### data_preprocess.py:    
#### Usage:
In terminal, run 
```
python data_preprocess.py -h
```
-h, --help            show this help message and exit\
  -y LABEL, --label LABEL\
                        effective - for effective/ineffective label, or score
                        - for scored/did not score label (default=effective)\
  -r INIT_ROWS, --init_rows INIT_ROWS\
                        set some number - useful for testing\
  -a [AGT_LIST [AGT_LIST ...]], --a_list [AGT_LIST [AGT_LIST ...]]\
                        list of agents from default=ball shooter
                        shooterdefender lastpasser lastpasserdefender\
  -ti TIME_INT, --time_int TIME_INT\
                        t1 or t2 (default=t2)\
  -p XTH_POINT, --xth_point XTH_POINT\
                        downsample by considering only every xth point from
                        the trajectories (default=1, i.e., include every
                        point)\
  -g GAME_ID, --game_id GAME_ID\
                        specify a particular match id (default = all matches)\
  -t TEAM, --team TEAM  specify a particular team id, e.g., Cleveland 1610612739, Golden State Warriors 1610612744 (default = all teams)\
```
python data_preprocess.py -h
```
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running Stat-DSM/MA-Stat-DSM
### ma_stat_dsm.py:  
#### Optional:\
'-p', '--pos_label', type=str, required=False, default='1'\
'-n', '--neg_label', type=str, required=False, default='0'\
'-i', '--max_it', type=int, required=False, default=1000, help='maximum number of iterations (default=1000)'\
'-a', '--alph', type=float, required=False, default=0.05, help='statistical significance level (alpha). default is alpha = 0.05'\
#### Required:\
'-l', '--min_l', type=int, required=True, help='minimum trajectory length (required)'\
'-d', '--dist_threshold', type=float, required=True, help='distance threshold (required)'\

## Step 3: Determining the statitically significant discriminative sub-trajectories
### calculate_sig_subtraj.py:  
Run with the delta* value that was output from ma_stat_dsm.py.\
```
python calculate_sig_subtraj.py -d 0.0344542453452345
```

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
