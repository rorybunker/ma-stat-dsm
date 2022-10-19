# Installing PostgreSQL
First, download and install PostgreSQL (https://www.postgresql.org/download/) and pgAdmin (https://www.pgadmin.org/download/).


# Creating the database
Create a database called 'hurricane' with user = 'postgres', host = 'localhost' and password = 1234.

In pgAdmin, run each of the queries in data_structure_for_hurricane_data.sql, then insert the data with hurricane_point_insert.sql and hurricane_trajectory_insert.sql. 

Then, insert the same data into the multi-agent tables but with agent 1 by running the queries in second_inserts.sql. This just inserts the same trajectories and points as agent 0 for agent 1.

# Running (MA-)Stat-DSM
(Single-agent) Stat-DSM can be run by, e.g.,
```
python stat_dsm_hurricane.py -l 5 -d 1.5
```
Or by running ma_stat_dsm_hurricane.py with just one agent:
```
python ma_stat_dsm_hurricane.py -l 5 -d 1.5 -agents 0
```
Multi-agent Stat-DSM (MA-Stat-DSM) can be run by specifying two agents, i.e., -agents 0 1:
```
python ma_stat_dsm_hurricane.py -l 5 -d 1.5 -agents 0 1
```
# Identifying statistically significantly discriminative sub-trajectories (Stat-DSM) or sub-matrices (MA-Stat-DSM):
Run significant_subtrajectories.py using the delta value that was output in stat_dsm_hurricane.py, e.g.,
```
python significant_subtrajectories.py -d 0.001670525211584076
```
Trajectories, points, and statistically significantly discriminative sub-trajectories/sub-matrices can be visualized using QGIS (https://www.qgis.org/)
