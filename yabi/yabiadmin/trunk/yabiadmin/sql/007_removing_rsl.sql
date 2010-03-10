BEGIN;
ALTER TABLE yabmin_tool ADD queue varchar(50);
ALTER TABLE yabmin_tool ADD job_type varchar(40);
ALTER TABLE yabmin_tool ADD max_memory integer CHECK ("max_memory" >= 0);
COMMIT;


DROP TABLE yabmin_toolrslargumentorder ;
DROP TABLE yabmin_toolrslextensionmodule ;
DROP TABLE yabmin_toolrslinfo ;