#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create the PostgreSQL database prior to running data_preprocess.py,
ma_stat_dsm.py, and calculate_sig_subtraj.py

Created on Fri Jul 29 16:14:20 2022

@author: rorybunker
"""

import psycopg2
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')

try:
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='1234'")
except Exception as e:
    print(e)

cur = conn.cursor()

def delete_table(table_name):
    sql = """DROP TABLE IF EXISTS """ + table_name +""";"""
    cur.execute(sql)
    conn.commit()

def create_postgis_extension():
    sql = """CREATE EXTENSION IF NOT EXISTS postgis;"""
    cur.execute(sql)
    conn.commit()

def create_point_table():
    sql = """CREATE TABLE point (
            id serial NOT NULL,
            	tid integer,
        	pid integer,
        	label character varying(5),
            geom geometry,
            CONSTRAINT point_id PRIMARY KEY (id)
        )"""
    cur.execute(sql)
    conn.commit()

def create_point_table_idx():
    sql = """CREATE INDEX point_idx
                  ON point
                  USING GIST (geom)"""
    cur.execute(sql)
    conn.commit()

def create_point_ma_table():
    sql = """CREATE TABLE point_ma
                (
                    id serial NOT NULL,
                	aid integer,
                	tid integer,
                	pid integer,
                	label character varying(5),
                    geom geometry,
                    CONSTRAINT point_ma_id PRIMARY KEY (id)
                )"""
    cur.execute(sql)
    conn.commit()

def create_point_ma_table_idx():
    sql = """CREATE INDEX point_ma_idx
              ON point_ma
              USING GIST (geom)"""
    cur.execute(sql)
    conn.commit()


def create_trajectory_table():
    sql = """CREATE TABLE trajectory
                (
                    id serial NOT NULL,
                	tid integer,
                	label character varying(5),
                    geom geometry,
                    CONSTRAINT trajectory_id PRIMARY KEY (id)
                )"""
    cur.execute(sql)
    conn.commit()

def create_trajectory_table_idx():
    sql = """CREATE INDEX trajectory_idx
              ON trajectory
              USING GIST (geom)"""
    cur.execute(sql)
    conn.commit()

def create_trajectory_ma_table():
    sql = """CREATE TABLE trajectory_ma
                (
                    id serial NOT NULL,
                	aid integer,
                	tid integer,
                	label character varying(5),
                    geom geometry,
                    CONSTRAINT trajectory_ma_id PRIMARY KEY (id)
                )
                """
    cur.execute(sql)
    conn.commit()

def create_trajectory_ma_table_idx():
    sql = """CREATE INDEX trajectory_ma_idx
              ON trajectory_ma
              USING GIST (geom)"""
    cur.execute(sql)
    conn.commit()

def create_candidates_table():
    sql = """CREATE TABLE candidates (
             id serial PRIMARY KEY,
             candidate json
            )"""
    cur.execute(sql)
    conn.commit()

    conn.close()

def create_discriminative_subtraj_table():
    sql = """create table discriminative_subtraj (
    	index bigint,
    	subtraj_se text,
    	neigh_tids text,
    	pvalue double precision,
    	tid integer,
    	start_idx integer,
    	end_idx integer)"""
    cur.execute(sql)
    conn.commit()

    conn.close()

def main():
    create_postgis_extension()

    delete_table('point')
    create_point_table()
    create_point_table_idx()

    delete_table('point_ma')
    create_point_ma_table()
    create_point_ma_table_idx()

    delete_table('trajectory')
    create_trajectory_table()
    create_trajectory_table_idx()

    delete_table('trajectory_ma')
    create_trajectory_ma_table()
    create_trajectory_ma_table_idx()

    delete_table('candidates')
    create_candidates_table()

    delete_table('discriminative_subtraj')
    create_discriminative_subtraj_table()

if __name__ == '__main__':
    main()
