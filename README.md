# Multi-Agent Statistically Discriminative Sub-trajectory Mining (MA-Stat-DSM)
Code for original (Single-agent) Statistically Discriminative Sub-trajectory Mining and Multi-Agent Statistically Discriminative Sub-trajectory Mining

Stat-DSM was proposed by Le Vo et al. (2020): https://ieeexplore.ieee.org/abstract/document/9093199

**Instructions**
1. Install PostgreSQL https://www.postgresql.org/download/ (this installer includes pgAdmin). You need to be able to run queries in this database and access the postgres shell (on Mac it is recommended to also install https://postgresapp.com/ since it provides quick access to the postgres shell).
2. In 1-create-point-trajectory-tables.py:  
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
