CREATE EXTENSION postgis;

DROP TABLE IF EXISTS point;
CREATE TABLE point
(
    id serial NOT NULL,
	tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT point_id PRIMARY KEY (id)
)

CREATE INDEX point_idx
  ON point
  USING GIST (geom);
  
-------------------------------------
DROP TABLE IF EXISTS point_ma;
CREATE TABLE point_ma
(
    id serial NOT NULL,
	aid integer,
	tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT point_ma_id PRIMARY KEY (id)
)

CREATE INDEX point_ma_idx
  ON point_ma
  USING GIST (geom);


-----------------------------------------------------

DROP TABLE IF EXISTS trajectory;
CREATE TABLE trajectory
(
    id serial NOT NULL,
	tid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT trajectory_id PRIMARY KEY (id)
)

CREATE INDEX trajectory_idx
  ON trajectory
  USING GIST (geom);

-----------------------------------------------------
DROP TABLE IF EXISTS trajectory_ma;
CREATE TABLE trajectory_ma
(
    id serial NOT NULL,
	aid integer,
	tid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT trajectory_ma_id PRIMARY KEY (id)
)

CREATE INDEX trajectory_ma_idx
  ON trajectory_ma
  USING GIST (geom);

-----------------------------------------------------

DROP TABLE IF EXISTS candidates;
CREATE TABLE candidates (
 id serial PRIMARY KEY,
 candidate jsonb
);


