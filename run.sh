#!/bin/bash

# load virtual environment
source ${HOME}/workspace2/virtualenvs/venv/bin/activate geoenv

# Golden State (1610612744): 21500504 21500520 21500524 21500548 21500556 21500568 21500583 21500592 21500622 21500003 21500035 21500051 21500069 21500083 21500092 21500104 21500120 21500125 21500144 21500164 21500177 21500187 21500200 21500214 21500236 21500245 21500259 21500268 21500300 21500314 21500336 21500351 21500381 21500397 21500434 21500438 21500468 21500480 21500485 21500290 
# Cleveland (1610612739): 21500499 21500511 21500527 21500543 21500559 21500575 21500601 21500622 21500011 21500021 21500046 21500063 21500078 21500094 21500106 21500130 21500141 21500160 21500176 21500191 21500203 21500219 21500227 21500262 21500288 21500313 21500334 21500367 21500384 21500405 21500424 21500438 21500453 21500466 21500473 21500291

# parameter setting from Le Vo et al 2020
# L = 5, 8, 10
# D = 1.5, 4, 20
# B = 250, 500, 750, 1000
# A = 0.05

T=1610612744
A=0.05
gameArray=(21500504 21500520 21500524 21500548 21500556 21500568 21500583 21500592 21500622 21500003 21500035 21500051 21500069 21500083 21500092 21500104 21500120 21500125 21500144 21500164 21500177 21500187 21500200 21500214 21500236 21500245 21500259 21500268 21500300 21500314 21500336 21500351 21500381 21500397 21500434 21500438 21500468 21500480 21500485 21500290)
downsamplingFactor=4
iter=0

# Get the start time
start_time=$(date +%s)

for G in ${gameArray[@]}; do
    for D in 1.5 4; do
        for L in 5 8 10; do
            echo --------------------------
            echo Iteration $iter. Team $T Game $G, Distance Threshold $D, Min Length $L, Downsampling $downsamplingFactor...
                            
            # Get the start time for the current iteration
            iter_start_time=$(date +%s)
            
            if python -u nba_data_preprocess.py -d $downsamplingFactor -g $G -t $T; then # 2>&1 >/dev/null; then
                echo 'Successfully completed data preprocessing'
            fi

            echo Running MA stat dsm...
            outputDelta="$(python -u ma_stat_dsm.py -a $A -d $D -l $L)"
            echo Finished running MA stat dsm and the output delta was $outputDelta

            if [ "$outputDelta" == "FAIL" ]; then
                echo "Since the output delta was $outputDelta significant_subtrajectories.py will not be run."
            else
                echo Checking significant subtrajectories...
                if python -u significant_subtrajectories.py -d $outputDelta 2>&1 >/dev/null; then
                    echo 'Some significant subtrajectories were found.'
                fi
            fi
                        
            # Get the end time for the current iteration
            iter_end_time=$(date +%s)
            
            # Calculate the running time for the current iteration
            iter_running_time=$((iter_end_time-iter_start_time))
            
            # Print the running time for the current iteration
            echo "Iteration $iter running time: $iter_running_time seconds"
            
            ((iter++))
        done
    done
done

# Get the end time
end_time=$(date +%s)

# Calculate the total running time
total_running_time=$((end_time-start_time))

# Print the total running time
echo "Total running time: $total_running_time seconds"

# psql -U postgres postgres
# \dt