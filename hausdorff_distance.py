import numpy as np
import math
from hausdorff import hausdorff_distance

def calculate_hausdorff_distance(agent_df, play_indx1, play_indx2):
  d = hausdorff_distance(np.array(agent_df.loc[play_indx1][['x','y']]), 
                     np.array(agent_df.loc[play_indx2][['x','y']]), 
                     distance='euclidean')
  return d
