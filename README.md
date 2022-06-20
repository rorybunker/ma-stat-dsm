# Discriminative sub-trajectory mining of NBA basketball tracking data
Code for original Stat-DSM, proposed by Le Vo et al. (2020) and a new Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM), which extends Stat-DSM to handle the trajectories of multiple agents (e.g., multiple players and the ball in sport), are provided. 

The "ma" in .py filenames denote that it relates to MA-Stat-DSM.

## Step 1: Setup PostgreSQL database environment
1. Install PostgreSQL https://www.postgresql.org/download/, which also includes pgAdmin (on Mac it is recommended to also install https://postgresapp.com/).
2. Create a PostgreSQL database with the following: dbname dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port 5432.
3. In pgadmin, run the queries in 0-create-postgres-database.sql to create the required database tables.

## Step 2: Running Stat-DSM 
### 1-data-preprocess-stat-dsm.py:    
- In the main() function, update the path to dataset_as_a_file_600_games.pkl
#### Preprocessing parameters: 
- agent_name: specify the agent - 'ball', 'shooter', 'shooterdefender', 'lastpasser' or 'lastpasserdefender'
- time_inteval: specify the time interval - t1 or t2 (see figure below)
- num_include: number of points to include, e.g., if num_include = 3, include every third point, if num_include = 1, include every point, etc.
- run_type: 'statdsm' or (to add) 'mastatdsm'
- initial_num_rows: run for smaller subset - useful for testing. If initial_num_rows = -1, run on entire dataset.
- team_id: the team ids are in the csv file id_team.csv. Cleveland team_id=1610612739, Golden State Warriors team_id=1610612744. If team_id = 0, run for all teams
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

### 2-stat-dsm.py:  
- Set your working directory in os.chdir(" ")
- Specify min_length and distance_threshold (in principle, the other parameters should remain fixed) 

### 3-calculate-candidate-subtraj-pvalues.py:  
- Set the delta* value that was printed at the end of running 2-stat-dsm.py   

## Running MA-Stat-DSM   

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
