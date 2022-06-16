import numpy as np
import math
from hausdorff import hausdorff_distance

def calculate_hausdorff_distance(agent_df, play_indx1, play_indx2, base_distance):
  # options for base_distance are 'euclidean', 'manhattan', 'chebyshev', 'cosine'
  d = hausdorff_distance(np.array(agent_df.loc[play_indx1][['x','y']]), 
                     np.array(agent_df.loc[play_indx2][['x','y']]), 
                     distance=base_distance)
  return d

# example
# hausdorff_d = calculate_hausdorff_distance(offense_df, 1040, 1042, 'euclidean')
