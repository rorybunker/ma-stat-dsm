--------------- NEW TABLE WITH LABEL IS STRING --------------


CREATE TABLE public.hurricane_point
(
    id serial NOT NULL,
	tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT hurricane_point_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_point_idx
  ON hurricane_point
  USING GIST (geom);


  CREATE TABLE public.hurricane_point_ma
  (
      id serial NOT NULL,
    aid integer,
  	tid integer,
  	pid integer,
  	label character varying(5),
      geom geometry,
      CONSTRAINT hurricane_point_ma_id PRIMARY KEY (id)
  )

  CREATE INDEX hurricane_point_ma_idx
    ON hurricane_point_ma
    USING GIST (geom);

-------------------------------------

CREATE TABLE public.hurricane_trajectory
(
    id serial NOT NULL,
	tid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT hurricane_trajectory_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_trajectory_idx
  ON hurricane_trajectory
  USING GIST (geom);

  CREATE TABLE public.hurricane_trajectory_ma
  (
      id serial NOT NULL,
    aid integer,
  	tid integer,
  	label character varying(5),
      geom geometry,
      CONSTRAINT hurricane_trajectory_ma_id PRIMARY KEY (id)
  )

  CREATE INDEX hurricane_trajectory_ma_idx
    ON hurricane_trajectory_ma
    USING GIST (geom);

-----------------------------------------------------

 CREATE TABLE public.hurricane_discriminative_point
(
    id serial NOT NULL,
	tid integer,
	original_tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT hurricane_discriminative_point_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_discriminative_point_idx
  ON hurricane_discriminative_point
  USING GIST (geom);


-------------------------------------

CREATE TABLE public.hurricane_discriminative_trajectory
(
    id serial NOT NULL,
	tid integer,
	label character varying(5),
	positive_support integer,
	negative_support integer,
	p_value float(10),
    geom geometry,
    CONSTRAINT hurricane_discriminative_trajectory_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_discriminative_trajectory_idx
  ON hurricane_discriminative_trajectory
  USING GIST (geom);


--------------------------------------

CREATE TABLE public.hurricane_discriminative_point_with_min_length
(
    id serial NOT NULL,
	tid integer,
	original_tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT hurricane_discriminative_point_with_min_length_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_discriminative_point_with_min_length_idx
  ON hurricane_discriminative_point_with_min_length
  USING GIST (geom);


-------------------------------------

CREATE TABLE public.hurricane_discriminative_trajectory_with_min_length
(
    id serial NOT NULL,
	tid integer,
	min_length integer,
	label character varying(5),
	positive_support integer,
	negative_support integer,
	p_value float(10),
    geom geometry,
    CONSTRAINT hurricane_discriminative_trajectory_with_min_length_id PRIMARY KEY (id)
)

CREATE INDEX hurricane_discriminative_trajectory_with_min_length_idx
  ON hurricane_discriminative_trajectory_with_min_length
  USING GIST (geom);


-------------------------------------


CREATE TABLE candidates (
 id serial PRIMARY KEY,
 candidate jsonb
);


CREATE TABLE candidates_test_parallel (
 id serial PRIMARY KEY,
 candidate jsonb
);

CREATE TABLE candidates_test_original_wy (
 id serial PRIMARY KEY,
 candidate jsonb
);

CREATE TABLE candidates_top_k_dist (
 id serial PRIMARY KEY,
 candidate jsonb
);


CREATE TABLE candidates_top_k_dist_for_comparision (
 id serial PRIMARY KEY,
 candidate jsonb
);


select * from hurricane_discriminative_point_with_min_length where tid in
(SELECT tid FROM hurricane_discriminative_trajectory_with_min_length where min_length = 4)



CREATE TABLE public.hurricane_discriminative_point_test
(
    id serial NOT NULL,
	tid integer,
	original_tid integer,
	pid integer,
	label character varying(5),
    geom geometry,
    CONSTRAINT hurricane_discriminative_point_test_id PRIMARY KEY (id)
)


CREATE TABLE public.hurricane_discriminative_trajectory_test
(
    id serial NOT NULL,
	tid integer,
	min_length integer,
	label character varying(5),
	positive_support integer,
	negative_support integer,
	p_value float(10),
    geom geometry,
    CONSTRAINT hurricane_discriminative_trajectory_test_id PRIMARY KEY (id)
)
