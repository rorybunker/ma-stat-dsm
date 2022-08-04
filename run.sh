#!/bin/bash
# load virtual environment
source ${HOME}/workspace2/virtualenvs/venv/bin/activate geoenv
# execute python scripts sequentially
python -u /home/b_rory/workspace2/work/ma_stat_dsm/create_postgresql_db.py
python -u /home/b_rory/workspace2/work/ma_stat_dsm/data_preprocess.py -p 4 -t 1610612744 -a shooter lastpasser
python -u /home/b_rory/workspace2/work/ma_stat_dsm/ma_stat_dsm.py -l 5 -d 1.5
