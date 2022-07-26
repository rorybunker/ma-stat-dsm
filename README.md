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
All arguments are optional:\
  -y/--label. Set to effective for effective/ineffective or to scored for scored/did not score label (default is effective)\
  -r/--init_rows. Set some number of initial rows, which is useful for testing (the final number of plays in the dataset will be less, and will be printed once the script has finished running).\
  -a/--a_list. List of agents from ball shooter
                        shooterdefender lastpasser lastpasserdefender\
  -ti/--time_int. The time interval, t1 or t2, as shown in the diagram below (default is t2)\
  -p/--xth_point. Downsample by considering only every xth point from
                        the trajectories (the default is 1, i.e., include every
                        point)\
  -g/--game_id. Specify a particular match id (default is all matches)\
  -t/--team. Specify a particular team id, e.g., Cleveland 1610612739, Golden State Warriors 1610612744 (default is all teams)
```
python data_preprocess.py -p 4 -t 1610612739 -a shooter lastpasser
```
```
python data_preprocess.py -p 4 -t 1610612744 -a shooter lastpasser
```
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running Stat-DSM/MA-Stat-DSM
### ma_stat_dsm.py:  
#### Optional:
These parameters don't need to be changed in principle.\
-p/--pos_label. default='1'\
-n/--neg_label, default='0'\
-i/--max_it. default=1000 maximum number of iterations\
-a/--alph. Statistical significance level (alpha). Default is alpha = 0.05
#### Required:
-l/--min_l. Minimum trajectory length, e.g., 5\
-d/--dist_threshold. Distance threshold, e.g., 1.5
```
python ma_stat_dsm.py -l 5 -d 1.5
```
## Step 3: Determining the statitically significant discriminative sub-trajectories
### calculate_sig_subtraj.py:  
Run with the delta* value that was output from running ma_stat_dsm.py.
```
python calculate_sig_subtraj.py -d 0.0344542453452345
```

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
