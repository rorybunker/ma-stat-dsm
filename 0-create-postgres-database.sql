CREATE EXTENSION postgis;

DROP TABLE IF EXISTS phase_point;
CREATE TABLE phase_point
(
    id serial NOT NULL,
	tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT phase_point_id PRIMARY KEY (id)
)

CREATE INDEX phase_point_idx
  ON phase_point
  USING GIST (geom);
  
-------------------------------------
DROP TABLE IF EXISTS phase_point_ma;
CREATE TABLE phase_point_ma
(
    id serial NOT NULL,
	aid integer,
	tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT phase_point_ma_id PRIMARY KEY (id)
)

CREATE INDEX phase_point_ma_idx
  ON phase_point_ma
  USING GIST (geom);


-----------------------------------------------------

DROP TABLE IF EXISTS phase_trajectory;
CREATE TABLE phase_trajectory
(
    id serial NOT NULL,
	tid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT phase_trajectory_id PRIMARY KEY (id)
)

CREATE INDEX phase_trajectory_idx
  ON phase_trajectory
  USING GIST (geom);

-----------------------------------------------------
DROP TABLE IF EXISTS phase_trajectory_ma;
CREATE TABLE phase_trajectory_ma
(
    id serial NOT NULL,
	aid integer,
	tid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT phase_trajectory_ma_id PRIMARY KEY (id)
)

CREATE INDEX phase_trajectory_ma_idx
  ON phase_trajectory_ma
  USING GIST (geom);

-----------------------------------------------------

DROP TABLE IF EXISTS candidates;
CREATE TABLE candidates (
 id serial PRIMARY KEY,
 candidate jsonb
);


