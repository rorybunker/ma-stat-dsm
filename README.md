# Discriminative sub-trajectory mining of NBA basketball tracking data
This repository contains an extended version of Stat-DSM, the statistically discriminative sub-trajectory mining method of method of Le Vo et al. (2020), which enables Stat-DSM to be run with the trajectories of multiple agents rather than only one (the original Stat-DSM can still be run for a single agent).

The method is illustrated in the context of sports, specificially NBA basketball, where the method can be used to determine discriminative sub-trajectories within labelled trajectories of multiple players and the ball.

## Step 0: Setup PostgreSQL database environment
1. Install PostgreSQL https://www.postgresql.org/download/, which also includes pgAdmin (on Mac it is recommended to also install https://postgresapp.com/).
2. Create a PostgreSQL database with the following: dbname dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port 5432.
3. In pgadmin, run the queries in 0-create-postgres-database.sql to create the required database tables.

## Step 1: Data preprocessing for Stat-DSM/MA-Stat-DSM 
### 1-data-preprocess.py:    
- In the main() function, update the path to where your dataset_as_a_file_600_games.pkl file is located.
#### Preprocessing parameters: 
- label_variable: 'score' or 'effective'
- agent_name: specify the agent - 'ball', 'shooter', 'shooterdefender', 'lastpasser' or 'lastpasserdefender'
- agent_list = ['ball','shooter','lastpasser','shooterdefender','lastpasserdefender']
- time_inteval: specify the time interval - t1 or t2 (see figure below)
- num_include: number of points to include, e.g., if num_include = 3, include every third point, if num_include = 1, include every point, etc.
- run_type: 'statdsm' or 'mastatdsm', specify based on whichever you will run in Step 2.
- initial_num_rows: run for smaller subset - useful for testing. If initial_num_rows = -1, run on entire dataset.
- team_id: the team ids are in the csv file id_team.csv. Cleveland team_id=1610612739, Golden State Warriors team_id=1610612744. If team_id = 0, run for all teams
![image](https://user-images.githubusercontent.com/29388472/173998123-ad0bade2-e42d-4261-89dd-40a4bc7834d3.png)

## Step 2: Running Stat-DSM/MA-Stat-DSM
### 2-ma-stat-dsm-combined.py:  
- Set your working directory in os.chdir(" ")
- Specify: 
  - min_length (e.g., between 2 and 50)
  - distance_threshold (e.g., between 1.5 and 25)
  - agent_ids: if agent_ids is a list with a single element, e.g., agent_ids = [1], run_type should be 'statdsm'. For run_type = 'mastatdsm', specify multiple agents corresponding to agent_list, e.g., [1, 3] for shooter and last passer, [0, 1, 2, 3, 4] for all agents. 
 (in principle, the other parameters should remain fixed) 

## Step 3: Running Stat-DSM/MA-Stat-DSM
### 3-calculate-candidate-subtraj-pvalues.py:  
- Set the delta* value that was printed at the end of running 2-stat-dsm.py   

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
