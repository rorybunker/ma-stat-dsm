import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', password='1234')
cur = conn.cursor()

table_definitions = [
    "DROP TABLE IF EXISTS hurricane_point",
    "DROP TABLE IF EXISTS hurricane_point_ma",
    "DROP TABLE IF EXISTS hurricane_trajectory",
    "DROP TABLE IF EXISTS hurricane_trajectory_ma",
    "DROP TABLE IF EXISTS hurricane_candidates",
    "DROP TABLE IF EXISTS hurricane_discriminative_subtraj",
    "CREATE TABLE IF NOT EXISTS hurricane_point (id serial NOT NULL, tid integer, pid integer, label character varying(5), geom geometry, CONSTRAINT hurricane_point_id PRIMARY KEY (id))",
    "CREATE TABLE IF NOT EXISTS hurricane_point_ma (id serial NOT NULL, aid integer, tid integer, pid integer, label character varying(5), geom geometry, CONSTRAINT hurricane_point_ma_id PRIMARY KEY (id))",
    "CREATE TABLE IF NOT EXISTS hurricane_trajectory (id serial NOT NULL, tid integer, label character varying(5), geom geometry, CONSTRAINT hurricane_trajectory_id PRIMARY KEY (id))",
    "CREATE TABLE IF NOT EXISTS hurricane_trajectory_ma (id serial NOT NULL, aid integer, tid integer, label character varying(5), geom geometry, CONSTRAINT hurricane_trajectory_ma_id PRIMARY KEY (id))",
    "CREATE TABLE IF NOT EXISTS hurricane_candidates (id serial PRIMARY KEY, candidate json)",
    "CREATE TABLE IF NOT EXISTS hurricane_discriminative_subtraj (index bigint, subtraj json, traj_id bigint, label character varying(5), CONSTRAINT hurricane_discriminative_subtraj_id PRIMARY KEY (index))",
    "CREATE EXTENSION IF NOT EXISTS postgis",
    "CREATE INDEX IF NOT EXISTS hurricane_point_idx ON hurricane_point USING GIST (geom)",
    "CREATE INDEX IF NOT EXISTS hurricane_point_ma_idx ON hurricane_point_ma USING GIST (geom)",
    "CREATE INDEX IF NOT EXISTS hurricane_trajectory_idx ON hurricane_trajectory USING GIST (geom)",
    "CREATE INDEX IF NOT EXISTS hurricane_trajectory_ma_idx ON hurricane_trajectory_ma USING GIST (geom)"
]

for table_definition in table_definitions:
    cur.execute(table_definition)
    conn.commit()

def run_sql_inserts(insert_script1, insert_script2, insert_script3):
    # Create a cursor object
    c = conn.cursor()

    # Open and read the file as a single buffer
    with open(insert_script1, 'r') as f:
        sql_script1 = f.read()
    with open(insert_script2, 'r') as f:
        sql_script2 = f.read()
    with open(insert_script3, 'r') as f:
        sql_script2 = f.read()

    # Execute the script
    c.execute(sql_script1)
    c.execute(sql_script2)

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    c.close()
    conn.close()

run_sql_inserts('hurricane/hurricane_point_insert.sql', 'hurricane/hurricane_trajectory_insert.sql', 'hurricane/second_inserts.sql')

conn.close()
