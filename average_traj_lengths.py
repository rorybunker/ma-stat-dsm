import pandas as pd
from shapely.wkt import loads

df = pd.read_csv('trajectory_ma.csv')

# Convert the 'geom' column to shapely geometry objects
df['geom'] = df['geom'].apply(lambda x: loads(x))

# Calculate the average number of points
average_num_points = df['geom'].apply(lambda x: len(x.coords)).mean()
aid_grouped = df.groupby('aid')
# label_grouped = df.groupby('label')
# tid_grouped = df.groupby('tid')

# Calculate average number of points in a trajectory by aid
average_num_points_by_aid = aid_grouped['geom'].apply(lambda x: x.apply(lambda y: len(y.coords)).mean()).reset_index(name='average_num_points')
print(average_num_points_by_aid)

# Calculate average number of points in a trajectory by label
# average_num_points_by_label = label_grouped['geom'].apply(lambda x: x.apply(lambda y: len(y.coords)).mean()).reset_index(name='average_num_points')
# print(average_num_points_by_label)

# # Calculate average number of points in a trajectory by tid
# average_num_points_by_tid = tid_grouped['geom'].apply(lambda x: x.apply(lambda y: len(y.coords)).mean()).reset_index(name='average_num_points')
# print(average_num_points_by_tid)