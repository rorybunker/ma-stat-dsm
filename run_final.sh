#!/bin/bash
# load virtual environment
source ${HOME}/workspace2/virtualenvs/venv/bin/activate geoenv
# execute python scripts
python -u /home/b_rory/workspace2/work/ma_stat_dsm/calculate_sig_subtraj.py -d 0.0002552756207417909
