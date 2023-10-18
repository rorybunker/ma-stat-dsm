import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pickle
import numpy as np
import pandas as pd
from nba_data_preprocess_new import create_agent_ma_df
import os

data = pickle.load(open('dataset_as_a_file_600_games.pkl', 'rb'))

trajectories, label, indices, game_id, quarter = np.array(data[0], dtype=object), np.array(data[1], dtype=object), np.array(data[2].astype(int), dtype=object), np.array(data[3].astype(int), dtype=object), np.array(data[4].astype(int), dtype=object)
trajectories_df, label_df, game_id_df, quarter_df = [pd.DataFrame(data, index=indices) for data in (trajectories, label, game_id, quarter)]

# join dataframes on index
combined_df = pd.concat([label_df, game_id_df, quarter_df, trajectories_df], axis=1, join='inner')

# set column names
combined_df.columns = ['effectiveness', 'T1', 'T2', 'shot_attempt','score', '2_or_3_point', 'ID1', 'ID2', 'team_id', 'game_id', 'quarter','trajectories']

# subset the data if team_id is specified above
# if args.team != 0:
#     combined_df = combined_df[(combined_df['team_id'] == float(args.team))]
# # also subset the data if game_id is specified above
# if args.game_id != 0:
#     combined_df = combined_df[(combined_df['game_id'] == args.game_id)]

# columns 3,4,5 are shot attempt, score, 2 or 3 point.
combined_df['score_binary'] = np.where(combined_df['score'] == 0, 0, 1)
combined_df['attempt_binary'] = np.where(combined_df['shot_attempt'] == 0, 0, 1)

# create label variable
# if args.label == 'score':
combined_df['score_binary'] = combined_df['score_binary']
# elif args.label == 'effective':
combined_df['effectiveness'] = combined_df['effectiveness']
# elif args.label == 'attempt':
combined_df['attempt_binary'] = combined_df['attempt_binary']

# remove where T2 = 0
combined_df = combined_df[combined_df['T2']>0]

combined_df['traj_length'] = 0  # Create the 'traj_length' column and initialize all values to 0

# create a column for the length of the trajectory (to get time in seconds, divide this by 10)
for index, row in combined_df.iterrows():
    traj_length = len(row['trajectories'])
    combined_df.at[index, 'traj_length'] = traj_length
# combined_df['traj_length'] = [len(row['trajectories']) for index, row in combined_df.iterrows()]
combined_df.to_csv('combined_df_final.csv')

# create dataframe for the specified agents
agent_df_list = create_agent_ma_df(combined_df)
effectiveness_only_df = combined_df['effectiveness']
score_binary_only_df = combined_df['score_binary']
attempt_binary_only_df = combined_df['attempt_binary']

agent_df_list = agent_df_list.merge(effectiveness_only_df, left_on='play_index', right_index=True, how='left')
agent_df_list = agent_df_list.merge(score_binary_only_df, left_on='play_index', right_index=True, how='left')
agent_df_list = agent_df_list.merge(attempt_binary_only_df, left_on='play_index', right_index=True, how='left')

def plot_trajectory_on_court(specified_play_index, agent_df_list, effectiveness, score_binary, attempt_binary, save_fig=False):
    if specified_play_index[0] not in agent_df_list['play_index']:
        print(f'Play index {specified_play_index} not found in the DataFrame.')
    else:
        court_path = 'nba_court_T.png'
        feet_to_meters = 0.3048 
        img = mpimg.imread(court_path)
        plt.imshow(img, extent=[0, 94 * feet_to_meters, 0, 50 * feet_to_meters], zorder=0) 
        plt.xlim(0, 47 * feet_to_meters)  
        plt.ylim(0, 50 * feet_to_meters)

        # Define agent labels
        agent_labels = {
            0: 'ball',
            1: 'shooter',
            2: 'lastpasser',
            3: 'shooterdefender',
            4: 'lastpasserdefender'
        }

        # Use tab10 colormap for distinct agent colors
        colors = plt.cm.tab10.colors

        for idx, aid in enumerate(agent_df_list['aid'].unique()):
            agent_data = agent_df_list[(agent_df_list['play_index'] == specified_play_index) & (agent_df_list['aid'] == aid)]
            if not agent_data.empty:
                x = agent_data['x']
                y = agent_data['y']

                # Get unique color for each agent
                color = colors[idx % len(colors)]

                # Normalize pid values and use them to adjust alpha (transparency)
                pid_values = agent_data['pid']
                normalized_pid = (pid_values - pid_values.min()) / (pid_values.max() - pid_values.min())
                alphas = 0.2 + 0.8 * normalized_pid  # Adjust alpha between 0.2 and 1

                # Decrease marker size and draw points and lines
                plt.scatter(x, y, label=f'{agent_labels.get(aid, str(aid))}', marker='o', s=10, color=color, alpha=alphas)
                plt.plot(x, y, color=color, alpha=0.5, linewidth=0.5)  # Line connecting the points
            else:
                print(f'No data found for Play Index: {specified_play_index}, Agent ID: {aid}')

        plt.legend()
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(f'Play {specified_play_index}.Effectiveness: {effectiveness}, Score: {score_binary}, Attempt: {attempt_binary}')

        if save_fig:
            plt.savefig(os.path.join('figs', f'trajectories_play_{specified_play_index[0]}.png'))
            print(f'Figure saved as trajectories_play_{specified_play_index[0]}.png')
        else:
            plt.show()

# Call the function with the specified play index, effectiveness, score_binary, attempt_binary, and save the figure
specified_play_index = (1044,)
effectiveness_value = agent_df_list.loc[agent_df_list['play_index'] == specified_play_index, 'effectiveness'].iloc[0]
score_binary_value = agent_df_list.loc[agent_df_list['play_index'] == specified_play_index, 'score_binary'].iloc[0]
attempt_binary_value = agent_df_list.loc[agent_df_list['play_index'] == specified_play_index, 'attempt_binary'].iloc[0]

plot_trajectory_on_court(specified_play_index, agent_df_list, effectiveness_value, score_binary_value, attempt_binary_value, save_fig=True)
