INSERT INTO hurricane_point_ma(id,aid,tid,pid,label,geom) (
  SELECT id+7316, 1, tid, pid, label, geom FROM hurricane_point);
  
 
