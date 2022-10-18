INSERT INTO hurricane_point_ma(id,aid,tid,pid,label,geom) (
  SELECT id+7316, 1, tid, pid, label, geom FROM hurricane_point);
 
INSERT INTO hurricane_trajectory_ma(id,aid,tid,label,geom) (
  SELECT id+210, 1, tid, label, geom FROM hurricane_trajectory);
 
