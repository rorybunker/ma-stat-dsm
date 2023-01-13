#!/bin/bash

# load virtual environment
source ${HOME}/workspace2/virtualenvs/venv/bin/activate geoenv
# python -u main.py


# iter=0
# for T in 1610612739 1610612744; do
#      for P in 5 4 3 2 1; do
#         for A in 0.05 0.1 0.2 0.5; do
#             for D in 1.5 5 10 20; do
#                 for L in 10 5 2; do
#                     echo --------------------------
#                     echo Iteration $iter. Running for team $T p $P alpha $A dist threshold $D and min length $L...
                    
#                     if python data_preprocess.py -p $P -t $T -a shooter lastpasser 2>&1 >/dev/null; then
#                         echo 'Successfully completed data preprocessing'
#                     fi

#                     echo Running MA stat dsm...
#                     outputDelta="$(python -u ma_stat_dsm.py -alpha $A -d $D -l $L -agents 1 2)"
#                     echo Finished running MA stat dsm and the output delta was $outputDelta

#                     echo Checking significant subtrajectories...
#                     if python significant_subtrajectories.py -d $outputDelta 2>&1 >/dev/null; then
#                         echo 'Significant subtrajectories found. Finishing processing.'
#                         exit
#                     fi
#                     echo No significant subtrajectories found. Continuing to the next iteration.
#                     ((iter++))
#                 done
#             done
#         done
#     done
# done

# Golden State (1610612744): 21500504 21500520 21500524 21500548 21500556 21500568 21500583 21500592 21500622 21500003 21500035 21500051 21500069 21500083 21500092 21500104 21500120 21500125 21500144 21500164 21500177 21500187 21500200 21500214 21500236 21500245 21500259 21500268 21500300 21500314 21500336 21500351 21500381 21500397 21500434 21500438 21500468 21500480 21500485 21500290 
# Cleveland (1610612739): 21500499 21500511 21500527 21500543 21500559 21500575 21500601 21500622 21500011 21500021 21500046 21500063 21500078 21500094 21500106 21500130 21500141 21500160 21500176 21500191 21500203 21500219 21500227 21500262 21500288 21500313 21500334 21500367 21500384 21500405 21500424 21500438 21500453 21500466 21500473 21500291

# parameter setting from Le Vo et al 2020
# L = 5, 8, 10
# D = 1.5, 4, 20
# B = 250, 500, 750, 1000
# A = 0.05
iter=0
teamID=1610612744
pointIntArray=(5 4 3 2 1)
A=0.05
B=1000
# sigLevelArray=(0.05 0.1 0.2)
gameArray=(21500504 21500520 21500524 21500548 21500556 21500568 21500583 21500592 21500622 21500003 21500035 21500051 21500069 21500083 21500092 21500104 21500120 21500125 21500144 21500164 21500177 21500187 21500200 21500214 21500236 21500245 21500259 21500268 21500300 21500314 21500336 21500351 21500381 21500397 21500434 21500438 21500468 21500480 21500485 21500290)
for G in ${gameArray[@]}; do
    for pointInt in ${pointIntArray[@]}; do
        for D in 1.5 4; do
            for L in 5 8 10; do
                echo --------------------------
                echo Iteration $iter. Parameters: game $G, downsampling $pointInt, alpha $A, distance threshold $D, min length $L, max iterations $B...
                            
                if python -u data_preprocess.py -g $G -p $pointInt -t $teamID -a shooter lastpasser 2>&1 >/dev/null; then
                    echo 'Successfully completed data preprocessing'
                fi

                echo Running MA stat dsm...
                outputDelta="$(python -u ma_stat_dsm.py -alpha $A -d $D -l $L -agents 1 2 -i $B)"
                echo Finished running MA stat dsm and the output delta was $outputDelta

                echo Checking significant subtrajectories...
                if python -u significant_subtrajectories.py -d $outputDelta 2>&1 >/dev/null; then
                    echo 'Some significant subtrajectories were found.'
                    dt=$(date '+%d/%m/%Y %H:%M:%S');
                    echo "$dt"
                    # exit
                fi
                echo Continuing to the next iteration.
                        
                dt=$(date '+%d/%m/%Y %H:%M:%S');
                echo "$dt"

                ((iter++))
            done
        done
    done
done
# psql -U postgres postgres
# \dt
