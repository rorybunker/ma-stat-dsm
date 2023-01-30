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
    ts_value = None

    def __init__(self, table_name, court_path, engine):
        if Court.ts_value is None:
            Court.ts_value = table_name.rsplit('_', 1)[-1]
        self.table_name = table_name
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

                traj_sql = f"SELECT * FROM {self.table_name} WHERE aid = {agent_id} and tid = {traj_id};"
                trajs = pd.read_sql(traj_sql, self.engine)
                trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
                pt_array = gdf.geometry.apply(lambda g: g.coords[0])
                points = [Point(coord) for coord in pt_array]
                x = [p.x for p in points]
                y = [p.y for p in points]

                full_traj_table = f"points_{Court.ts_value}"
                full_traj_sql = f"SELECT * FROM {full_traj_table} WHERE aid = {agent_id} and tid = {traj_id};"
                full_trajs = pd.read_sql(full_traj_sql, self.engine)
                full_trajs = full_trajs.sort_values(by='pid')
                full_trajs["geom"] = full_trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=full_trajs["geom"])
                pt_array_full = gdf.geometry.apply(lambda g: g.coords[0])
                points_full = [Point(coord) for coord in pt_array_full]
                x_full = [p.x for p in points_full]
                y_full = [p.y for p in points_full]

                values = np.linspace(0, len(full_trajs) - 1, len(full_trajs))
                norm = Normalize(vmin=min(values), vmax=max(values))
                plt.scatter(x_full, y_full, c=values, cmap=cm.get_cmap(color_map[i],128), norm=norm,s=3)
                
                plt.scatter(x, y, c=colors[agent_id], marker='+')
                
                # Add the legend to the plot
                plt.legend(handles, labels, bbox_to_anchor=(1.04,1), loc="upper left", fontsize=6, framealpha=0.5)

            if not os.path.exists("figs"):
                os.makedirs("figs")
            plt.savefig(f"figs/{self.table_name}_{traj_id}.jpg", format='jpg', dpi=300)
            plt.show()
            plt.clf()

    def plot_single_agent_trajectories(self):
        plt.imshow(self.img, extent=[0,94*self.feet_m,0,50*self.feet_m], zorder=0)
        traj_sql = f"SELECT DISTINCT tid FROM {self.table_name};"
        traj_df = pd.read_sql(traj_sql, self.engine)
        traj_ids = list(traj_df.tid)

        for traj_id in traj_ids:
            traj_sql = f"SELECT * FROM {self.table_name} WHERE tid = {traj_id};"
            trajs = pd.read_sql(traj_sql, self.engine)

            trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
            gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
            pt_array = gdf.geometry.apply(lambda g: g.coords[0])

            points = [Point(coord) for coord in pt_array]
            x = [p.x for p in points]
            y = [p.y for p in points]

            plt.plot(x, y, color='black', linewidth=0.5)
            plt.scatter(x, y)

        plt.xlim(0, 47*self.feet_m) 

        if not os.path.exists("figs"):
            os.makedirs("figs")
        plt.savefig(f"figs/{self.table_name}.jpg", format='jpg', dpi=300)
        plt.show()
        plt.clf()
