import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import geopandas as gpd
import shapely
import numpy as np
import os
from shapely.geometry import Point
from matplotlib import cm
from matplotlib.colors import Normalize

class Court:
    # ts_value = None

    def __init__(self, table_name, court_path, engine):
        # if Court.ts_value is None:
        #     Court.ts_value = table_name.rsplit('_', 1)[-1]
        
        self.table_name = table_name
        table_name_suffix = table_name.rsplit('_', 6)[-6:]
        self.table_name_suffix = "_".join(map(str, table_name_suffix))
        self.court_path = court_path
        self.engine = engine
        self.feet_m = 0.3048
        self.img = mpimg.imread(self.court_path)
    
    def plot_multi_agent_trajectories(self):

        feet_m = self.feet_m
        traj_sql = f"SELECT DISTINCT tid FROM {self.table_name};"
        traj_df = pd.read_sql(traj_sql, self.engine)
        traj_ids = list(traj_df.tid)

        for traj_id in traj_ids:
            plt.figure()
            img = mpimg.imread(self.court_path)
            plt.imshow(img, extent=[0,94*feet_m,0,50*feet_m], zorder=0) 
            plt.xlim(0,47*feet_m)  
            plt.ylim(0,50*feet_m)

            # Get original index for traj_id from index_mapping.csv
            index_mapping = pd.read_csv('index_mapping.csv')
            original_index = index_mapping[index_mapping['tid'] == traj_id]['original_index'].values[0]

            combined_df_final = pd.read_csv('combined_df_final.csv', index_col=0)
            combined_df_final = combined_df_final.reset_index(drop=False)
            combined_df_final.index = combined_df_final['index'].astype(str).str.extract('(\d+)').iloc[:, 0].astype(int)

            # Add the information to the figure
            info = combined_df_final.loc[original_index]
            desired_info = info[['effectiveness', 'T1', 'T2', 'shot_attempt', 'score', '2_or_3_point']]
            plt.annotate(f"{desired_info}", xy=(1,0.2), xycoords='axes fraction', xytext=(5,5), textcoords='offset points', fontsize=6,
            bbox=dict(boxstyle='round', fc='white', alpha=0.5), ha='left', va='top')

            # Load and merge the tables
            team_game_ids = pd.read_csv("meta_data/team_game_ids.csv")
            id_team = pd.read_csv("meta_data/id_team.csv")
            team_game_team = pd.merge(team_game_ids, id_team, on="team_id")

            # Get the team names for each game
            teams_per_game = team_game_team.groupby("game_id").team_1.apply(list)
            
            # Concatenate the team names and the game ID into the desired string
            game_info = teams_per_game.apply(lambda x: f"{x[0]} vs {x[1]}")
            plt.annotate(game_info.loc[info['game_id']], xy=(0.5,1), xycoords='axes fraction', xytext=(0,15), textcoords='offset points', fontsize=10, ha='center', va='bottom')

            agt_sql = f"SELECT DISTINCT aid FROM {self.table_name};"
            agt_df = pd.read_sql(agt_sql, self.engine)
            agent_ids = sorted(list(agt_df.aid))

            colors = ['blue', 'red', 'green', 'purple', 'orange']
            color_map = ['Blues', 'Reds', 'Greens', 'Purples', 'Oranges']
            # Create a dictionary that maps agent IDs to labels
            agent_labels = {0: 'ball', 1: 'shooter', 2: 'last passer', 3: 'shooter defender', 4: 'last passer defender'}
            
            # Create handles and labels for each agent
            handles = []
            labels = []
            for i, agent_id in enumerate(agent_ids):
                if agent_id not in agent_labels:
                    continue
                handle, = plt.plot([], color=colors[i], marker='+', label=agent_labels[agent_id])
                handles.append(handle)
                labels.append(agent_labels[agent_id])

                # Discriminative subtrajectory plot
                traj_sql = f"SELECT * FROM {self.table_name} WHERE aid = {agent_id} and tid = {traj_id};"
                trajs = pd.read_sql(traj_sql, self.engine)
                trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
                pt_array = gdf.geometry.apply(lambda g: g.coords[0])
                points = [Point(coord) for coord in pt_array]
                x = [p.x for p in points]
                y = [p.y for p in points]

                # Full trajectory plot
                full_traj_table = f"points_{self.table_name_suffix}"
                full_traj_sql = f"SELECT * FROM {full_traj_table} WHERE aid = {agent_id} and tid = {traj_id};"
                full_trajs = pd.read_sql(full_traj_sql, self.engine)
                full_trajs = full_trajs.sort_values(by='pid')
                full_trajs["geom"] = full_trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=full_trajs["geom"])
                pt_array_full = gdf.geometry.apply(lambda g: g.coords[0])
                points_full = [Point(coord) for coord in pt_array_full]
                x_full = [p.x for p in points_full]
                y_full = [p.y for p in points_full]
                # color scale will go from light to dark
                values = np.linspace(0, len(full_trajs) - 1, len(full_trajs))
                minval = min(values)
                maxval = max(values)
                norm_scores = (values - minval) / (maxval - minval)
                plt.scatter(x_full, y_full, c=norm_scores, cmap=cm.get_cmap(color_map[i], 128), s=3)
                
                # Add the discriminative sub-trajectories to the plot with + marks
                plt.scatter(x, y, c=colors[agent_id], marker='+')
            
                # Add the legend to the plot
                plt.legend(handles, labels, bbox_to_anchor=(1.04,1), loc="upper left", fontsize=6, framealpha=0.5)

            if not os.path.exists("figs"):
                os.makedirs("figs")
            plt.savefig(f"figs/{self.table_name}_{traj_id}_{original_index}.jpg", format='jpg', dpi=300)
            plt.show()
            plt.clf()
        