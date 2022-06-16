# Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM)
Code for original Stat-DSM, proposed by Le Vo et al. (2020), and a new Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM), which extends Stat-DSM to handle the trajectories of multiple agents (e.g., multiple players and the ball in sport). 

The "ma" in .py filenames denote that it relates to MA-Stat-DSM.

Le Vo, D. N., Sakuma, T., Ishiyama, T., Toda, H., Arai, K., Karasuyama, M., ... & Takeuchi, I. (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering. DOI: 10.1109/TKDE.2020.2994344

## STEP 1: Setup PostgreSQL database environment
1. Install PostgreSQL https://www.postgresql.org/download/, which also includes pgAdmin (on Mac it is recommended to also install https://postgresapp.com/).
2. Create a PostgreSQL database with \\
dbname dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port 5432.\\
Then, in pgadmin, run the queries in 0-create-postgres-database.sql to create the required database tables.

## STEP 2: Running Stat-DSM 
3. In 1-create-point-trajectory-tables.py:    
    - Enter your working directory in line 27.  
    - Enter your Postgres database details in param_dic (lines 166--171).  
    - Uncomment one of the lines 140--144 and lines 159--163 based on the agent you are considering.   
Run 1-create-point-trajectory-tables.py.   
3. In pgAdmin, right click on the database -> Query tool, run the two queries that are commented in lines 211 onwards (update the FROM line based on where your csv files were exported to).  
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

**Instructions for how to run (Multi-Agent) MA-Stat-DSM**.   
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
