import numpy as np
import math
from hausdorff import hausdorff_distance

def calculate_hausdorff_distance(agent_df):
  d = hausdorff_distance(np.array(agent_df.loc[play_indx][['x','y']]), 
                     np.array(agent_df.loc[play_indx][['x','y']]), 
                     distance='euclidean')
  return d
