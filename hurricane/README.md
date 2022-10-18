# Creating the database
Run each of the queries in data_structure_for_hurricane_data.sql, then insert the data with hurricane_point_insert.sql and hurricane_trajectory_insert.sql. Then, insert the same data into the multi-agent tables but with agent 1 by running the queries in second_inserts.sql.  

# Running (MA-)Stat-DSM
```
python stat_dsm_hurricane.py -l 5 -d 1.5
```
Or
```
python ma_stat_dsm_hurricane.py -l 5 -d 1.5 -agents 0 1
```
Then run significant_subtrajectories.py using the delta value that was output in stat_dsm_hurricane.py, e.g.,
```
python significant_subtrajectories.py -d 0.001670525211584076
```
