# Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM)
Code for original Stat-DSM, proposed by Le Vo et al. (2020), and a new Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM), which extends Stat-DSM to handle the trajectories of multiple agents (e.g., multiple players and the ball in sport). 

The "ma" in .py filenames denote that it relates to MA-Stat-DSM.

## STEP 1: Setup PostgreSQL database environment
1. Install PostgreSQL https://www.postgresql.org/download/, which also includes pgAdmin (on Mac it is recommended to also install https://postgresapp.com/).
2. Create a PostgreSQL database with the following: dbname dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port 5432.
3. In pgadmin, run the queries in 0-create-postgres-database.sql to create the required database tables.

## STEP 2: Running Stat-DSM 
### 1-create-point-trajectory-tables.py:    
- In the main() function, update the path to dataset_as_a_file_600_games.pkl
- If you want to run for a specific team, enter the team ID in the line 
```label_df= label_df[(label_df[6]==1610612739)]```. The team ID 1610612739 is Cleveland.
- specify agent_name as either 'ball', 'shooter', 'shooterdefender', 'lastpasser' or 'lastpasserdefender'
- specify time_interval as either 't1' or 't2'

4. In 2-stat-dsm.py:  
    - Set your working directory in line 9.  
    - Specify your Postgres database details in line 15.  
    - Set the Stat-DSM parameters from lines 469--472.   
Run 2-stat-dsm.py.  
5. In postgres' psql shell, which is a terminal with postgres=# (if on Mac, you can use postgres.app and double click on your postgres database to open the shell), execute the following command:
    \copy (SELECT * FROM candidates) to '/.../candidates.csv' with csv;
6. In 3-calculate-candidate-subtraj-pvalues.py:  
    - Specify lines 18--20 and line 23 - where line 20 is the delta* value that was output from 2-stat-dsm.py.   
Run 3-calculate-candidate-subtraj-pvalues.py

## Running MA-Stat-DSM   
The python scripts relating to MA-Stat-DSM have "ma" in their title.    
3. In 1-ma-create-point-trajectory-tables.py:  
    - Enter your working directory. 
    - Enter your Postgres database details in param_dic.
Run 1-ma-create-point-trajectory-tables.py.   
3. In pgAdmin, right click on the database -> Query tool, run the two queries that are commented at the bottom of 1-ma-create-point-trajectory-tables.py (update the FROM line based on where your csv files were exported to).  
4. In 2-ma-stat-dsm.py:  
    - Set your working directory.  
    - Specify your Postgres database details.
    - Set the MA-Stat-DSM parameters. 
Run 2-ma-stat-dsm.py.  
5. In postgres' psql shell, which is a terminal with postgres=# (if on Mac, you can use postgres.app and double click on your postgres database to open the shell), execute the following command:
    \copy (SELECT * FROM candidates) to '/.../candidates.csv' with csv;
6. In 3-ma-calculate-candidate-subtraj-pvalues.py:  
    - Specify lines 18--20 and line 23 - where line 20 is the delta* value that was output from 2-ma-stat-dsm.py.   
Run 3-ma-calculate-candidate-subtraj-pvalues.py

# References
Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344
