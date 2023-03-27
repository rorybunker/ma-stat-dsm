import re
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file_name", type=str, required=True, help="slurm .out file name")
args = parser.parse_args()
filename = args.file_name
number = re.findall(r'slurm-(\d+).out', filename)[0]

# Open the output file
with open(filename, "r") as f:
    data = f.read()

# Use regular expressions to extract the desired information
iterations = re.findall(r"Iteration (\d+)\. Team (\d+) Game (\d+), Distance Threshold (\d+\.\d*|\d+), Min Length (\d+), Downsampling (\d+)", data)
agent_tid_counts = re.findall(r"Final # of agent tids in dataset: (\d+)", data)
distinct_tid_counts = re.findall(r"Final # of plays \(distinct tids\) in dataset: (\d+)", data)
deltas = re.findall(r"output delta was (\d+.\d+)", data)
times = re.findall(r"Iteration (\d+) running time: (\d+) seconds", data)
significance = re.findall(r"Some significant subtrajectories were found", data)

# Create a dictionary to store the extracted information
info = {}
for iteration, team, game, d_threshold, m_length, downsample_f in iterations:
    if iteration not in info.keys():
        info[iteration] = {"iteration": iteration, "distance threshold": d_threshold, "min length": m_length, "downsampling factor": downsample_f, "running time": 0, "team": team, "game": game}
    else:
        info[iteration]["iteration"] = iteration
        info[iteration]["distance threshold"] = d_threshold
        info[iteration]["min length"] = m_length
        info[iteration]["downsampling factor"] = downsample_f
        info[iteration]["team"] = team
        info[iteration]["game"] = game

for i, delta in enumerate(deltas):
    iteration = str(i)
    if iteration in info:
        info[iteration]["delta"] = delta

# Add the running time information to the dictionary
for iteration, time in times:
    if iteration in info:
        info[iteration]["running time"] = time

# Create a dataframe from the dictionary
df = pd.DataFrame.from_dict(info, orient='index')

# Convert the "running time" column to integers
df["running time"] = df["running time"].astype(int)

# Group the data by "distance threshold", "min length", and "downsampling factor"
grouped = df.groupby(["distance threshold", "min length", "downsampling factor"])

# Calculate the average running time for each group
average_time = grouped[["running time"]].mean()

# Create a new dataframe with the grouped data
result = average_time.reset_index()

# Export the dataframe to a csv file
if not os.path.exists("runtimes"):
    os.makedirs("runtimes")

df.to_csv("runtimes/output_old__" + number + "_" + str(len(significance)) + "_" + str(team) + ".csv", sep=",", index=False)
result.to_csv("runtimes/outpu_old_avg_" + number + "_" + str(len(significance)) + "_" + str(team) + ".csv", sep=",", index=False)
