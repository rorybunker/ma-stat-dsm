# Multi-agent statistical discriminative sub-trajectory mining
This repository contains the code for Multi-agent Stat-DSM (MA-Stat-DSM), a multi-agent statistical discriminative sub-trajectory mining method for analyzing the trajectories of multiple agents.

The MA-Stat-DSM method is demonstrated on tracking data of five agents from NBA basketball, to determine sub-matrices that discriminate between effective and ineffective plays.

## Requirements
### Create Environment
The required environment can be created using the environment.yml file. If you are running on your local machine, you can use Anaconda, in which case it is recommended to install mamba:
```
conda install mamba -n base -c conda-forge
```
Then, you can create the environment using the environment.yml file:
```
mamba env create -n geoenv -f environment.yml
```

### Create PostgreSQL Database
Install PostgreSQL and create a PostgreSQL database with: dbname = 'postgres', user = 'postgres', host = 'localhost', password = 1234, and port = 5432. 

Then, to create the required database tables, run
```
python create_postgresql_db.py
```

## Data

### NBA Dataset
In the paper (https://www.researchgate.net/publication/370062987_Multi-agent_statistical_discriminative_sub-trajectory_mining_and_an_application_to_NBA_basketball), trajectories for five agents (ball, shooter, shooter defender, last passer, last passer defender) from 600 NBA games in the 2015/2016 season were used.
(Source: this dataset_as_a_file_600_games.pkl file was generated based  ![this code](https://github.com/keisuke198619/team_representation#for-stat-dsm-preprocessing), which uses the basketball movement data from https://github.com/rajshah4/BasketballData)

To use the NBA data, you can use nba_data_preprocess.py to create trajectory_ma.csv and point_ma.csv files, which are then used as input to MA-Stat-DSM.

### Other Dataset
If you have some other multi-agent trajectory dataset, you can create trajectory_ma.csv and point_ma.csv files that have the same structure and use them instead as input to MA-Stat-DSM.

![Alt text](https://drive.google.com/uc?id=1JbXWIkkOEkrzA8rhQ3GO2jVro8zJdkoj)

### nba_data_preprocess.py:
| Argument | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `-y`, `--label` | `str` | Optional | `effective` | Type of label (`effective`, `score`, or `attempt`) |
| `-a`, `--a_list` | `str` | Optional | `['ball', 'shooter', 'lastpasser', 'shooterdefender', 'lastpasserdefender']` | List of agents |
| `-i`, `--time_int` | `str` | Optional | `t2` | Time interval (`t1` or `t2`) |
| `-d`, `--downsampling` | `int` | Optional | `1` | Downsample trajectories |
| `-g`, `--game_id` | `int` | Optional | `0` | Specify a particular match id |
| `-t`, `--team` | `int` | Optional | `0` | Specify a particular team id |

To create trajectory_ma.csv and point_ma.csv files that contain all Cleveland match trajectories (with all points):
```
python nba_data_preprocess.py -t 1610612739
```
To create trajectory_ma.csv and point_ma.csv files that contain all Golden State Warriors match trajectories (with every fourth point, i.e., a downsampling rate of 4):
```
python nba_data_preprocess.py -d 4 -t 1610612744
```
## MA-Stat-DSM
### ma_stat_dsm.py:  
| Argument | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `-l`, `--min_l` | `int` | Required | | Minimum trajectory length |
| `-d`, `--dist_threshold` | `float` | Required | | Distance threshold |
| `-p`, `--pos_label` | `str` | Optional | `1` | Positive label |
| `-n`, `--neg_label` | `str` | Optional | `0` | Negative label |
| `-i`, `--max_it` | `int` | Optional | `1000` | Maximum number of iterations |
| `-a`, `--alph` | `float` | Optional | `0.05` | Statistical significance level (alpha) |
| `-b`, `--hausdorff_base_dist` | `str` | Optional | `euclidean` | Options for base distance are euclidean, manhattan, chebyshev, or cosine |
| `-s`, `--seed` | `int` | Optional | `0` | Random seed for labels |

E.g., running MA-Stat-DSM with minimum length 5 and distance threshold 1.5:
```
python ma_stat_dsm.py -l 5 -d 1.5
```
## Identifying statistically significant discriminative sub-matrices
### significant_subtrajectories.py:  
| Argument | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `-d`, `--delta` | `str` | Yes | | The delta* value that was printed upon completion of ma_stat_dsm.py |

E.g.,
```
python significant_subtrajectories.py -d 0.0344542453452345
```

## Obtaining discriminative trajectory sub-matrices
### run.sh:  
In run.sh, we iterate over different downsampling factors and MA-Stat-DSM parameters and apply to Golden State and Cleveland match trajectory data.

To run as a batch process, where million2 is the name of the server where postgres is installed:
```
sbatch -w million2 ./run.sh
```

# Stat-DSM
Code for the original Stat-DSM method provided by Le Duy et al. (2020).
## stat_dsm.py
| Argument | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `-p`, `--pos_label` | `str` | No | `1` | The label for positive examples |
| `-n`, `--neg_label` | `str` | No | `0` | The label for negative examples |
| `-i`, `--max_it` | `int` | No | `1000` | The maximum number of iterations |
| `-alpha`, `--alph` | `float` | No | `0.05` | The statistical significance level |
| `-l`, `--min_l` | `int` | Yes |  | The minimum trajectory length |
| `-d`, `--dist_threshold` | `float` | Yes |  | The distance threshold |
| `-tr`, `--trajectory_table_name` | `str` | No | `trajectory` | The name of the trajectory table |
| `-po`, `--point_table_name` | `str` | No | `point` | The name of the point table |
| `-s`, `--seed` | `int` | No | `0` | The random seed for labels |

# References

Bunker et al. (2023). Multi-agent statistical discriminative sub-trajectory mining and an application to NBA basketball. Preprint.

Le Duy et al (2020). Stat-DSM: Statistically Discriminative Sub-Trajectory Mining With Multiple Testing Correction. IEEE Transactions on Knowledge and Data Engineering, 34(3), 1477-1488.
