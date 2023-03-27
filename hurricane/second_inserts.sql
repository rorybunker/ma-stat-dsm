UPDATE hurricane_point_ma
SET id = id - 7316;

INSERT INTO hurricane_point_ma(id,aid,tid,pid,label,geom) (
  SELECT id+7316, 1, tid, pid, label, geom FROM hurricane_point);
 
 UPDATE hurricane_trajectory_ma
SET id = id - 210;

INSERT INTO hurricane_trajectory_ma(id,aid,tid,label,geom) (
  SELECT id+210, 1, tid, label, geom FROM hurricane_trajectory);
 
