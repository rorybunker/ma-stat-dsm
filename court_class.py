import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import geopandas as gpd
import shapely
import numpy as np
import os
from shapely.geometry import Point
from matplotlib import cm

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

    # To add?:
    # def _score_to_color_attention(self, scores, histogram):
    #     maxval = histogram[1][-1] #max(scores)
    #     minval = 0 #min(scores)
    #     norm_scores = (scores - minval) / (maxval - minval)
    #     cmap1 = cm.get_cmap("Blues",128) # ball: from white to blue # autumn_r yellow to red
    #     cmap2 = cm.get_cmap("Reds",128) # attacker: from white to red
    #     cmap3 = cm.get_cmap("Greens",128) # defender: from white to green
    #     return norm_scores,[cmap1, cmap2, cmap3]

    # def score_to_color_attention(self, layer_name, scorelist, minimum=None, maximum=None):
    #     histogram = self.read_hist_csv_file(layer_name, '0', 10)
    #     if histogram[0] is None:
    #         import pdb; pdb.set_trace()
        
    #     colorlist, cmap = self._score_to_color_attention(scorelist, histogram)

    #     return colorlist, cmap

    def plot_single_agent_trajectories(self):
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

            plt.scatter(x, y)

        plt.xlim(0, 47*self.feet_m) 

        if not os.path.exists("figs"):
            os.makedirs("figs")
        plt.savefig(f"figs/{self.table_name}.jpg", format='jpg')
        plt.imshow(self.img, extent=[0,94*self.feet_m,0,50*self.feet_m], zorder=0) 
        plt.show()

    def plot_multi_agent_trajectories(self):
        colors = ['blue', 'red', 'green', 'purple', 'yellow']
        agt_sql = f"SELECT DISTINCT aid FROM {self.table_name};"
        agt_df = pd.read_sql(agt_sql, self.engine)
        agent_ids = list(agt_df.aid)
        traj_sql = f"SELECT DISTINCT tid FROM {self.table_name};"
        traj_df = pd.read_sql(traj_sql, self.engine)
        traj_ids = list(traj_df.tid)

        # plt.subplots(figsize=(12,6))
        plt.imshow(self.img, extent=[0,94*self.feet_m,0,50*self.feet_m], zorder=0)

        for i, agent_id in enumerate(agent_ids):
            for traj_id in traj_ids:
                traj_sql = f"SELECT * FROM {self.table_name} WHERE aid = {agent_id} and tid = {traj_id};"
                trajs = pd.read_sql(traj_sql, self.engine)
                trajs["geom"] = trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
                gdf = gpd.GeoDataFrame(geometry=trajs["geom"])
                pt_array = gdf.geometry.apply(lambda g: g.coords[0])
                points = [Point(coord) for coord in pt_array]
                x = [p.x for p in points]
                y = [p.y for p in points]
                plt.scatter(x, y, color=colors[i % len(colors)], alpha=0.5)

        full_traj_table = f"points_{Court.ts_value}"
        full_traj_sql = f"SELECT * FROM {full_traj_table} WHERE aid = {agent_id} and tid = {traj_id};"
        full_trajs = pd.read_sql(full_traj_sql, self.engine)
        full_trajs["geom"] = full_trajs["geom"].apply(lambda x: shapely.wkb.loads(x, hex=True))
        gdf = gpd.GeoDataFrame(geometry=full_trajs["geom"])
        pt_array = gdf.geometry.apply(lambda g: g.coords[0])
        points = [Point(coord) for coord in pt_array]
        x = [p.x for p in points]
        y = [p.y for p in points]
        plt.scatter(x, y, color='pink', alpha=0.3)
        # plt.clf()

        plt.xlim(0, 47*self.feet_m)
        
        if not os.path.exists("figs"):
            os.makedirs("figs")
        plt.savefig(f"figs/{self.table_name}.jpg", format='jpg')
        
        plt.show()
