import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import geopandas as gpd
import shapely
import numpy as np
import os

class Court:
    def __init__(self, table_name, court_path, engine):
        self.table_name = table_name
        self.court_path = court_path
        self.engine = engine
        self.feet_m = 0.3048
        self.img = mpimg.imread(self.court_path)

    def plot_single_agent_trajectories(self):
        traj_sql = f"SELECT DISTINCT tid FROM {self.table_name};"
        traj_df = pd.read_sql(traj_sql, self.engine)
        traj_ids = list(traj_df.tid)

        for traj_id in traj_ids:
            traj_sql = f"SELECT * FROM {self.table_name} WHERE tid = {traj_id};"
            trajs = pd.read_sql(traj_sql, self.engine)

            trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
            gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
            pt_array = np.concatenate(gdf.geometry)

            x = pt_array[::2]
            y = pt_array[1::2]

            plt.scatter(x, y)

        plt.imshow(self.img, extent=[0,94*self.feet_m,0,50*self.feet_m], zorder=0) 
        plt.xlim(0, 47*self.feet_m) 

        if not os.path.exists("figs"):
            os.makedirs("figs")
        plt.savefig(f"figs/{self.table_name}.jpg", format='jpg')
        
        plt.show()

    def plot_multi_agent_trajectories(self):
        colors = ['blue', 'red', 'green', 'purple']
        agt_sql = f"SELECT DISTINCT aid FROM {self.table_name};"
        agt_df = pd.read_sql(agt_sql, self.engine)
        agent_ids = list(agt_df.aid)
        traj_sql = f"SELECT DISTINCT tid FROM {self.table_name};"
        traj_df = pd.read_sql(traj_sql, self.engine)
        traj_ids = list(traj_df.tid)

        for i, agent_id in enumerate(agent_ids):
            for traj_id in traj_ids:
                traj_sql = f"SELECT * FROM {self.table_name} WHERE aid = {agent_id} and tid = {traj_id};"
                trajs = pd.read_sql(traj_sql, self.engine)
                trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
                pt_array = np.concatenate(gdf.geometry)
                x = pt_array[::2]
                y = pt_array[1::2]
                plt.scatter(x, y, color=colors[i % len(colors)])
        plt.imshow(self.img, extent=[0,94*self.feet_m,0,50*self.feet_m], zorder=0) 
        plt.xlim(0, 47*self.feet_m)
        
        if not os.path.exists("figs"):
            os.makedirs("figs")
        plt.savefig(f"figs/{self.table_name}.jpg", format='jpg')

        plt.show()
