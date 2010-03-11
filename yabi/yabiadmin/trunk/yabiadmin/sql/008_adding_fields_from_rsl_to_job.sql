BEGIN;
ALTER TABLE yabiengine_job ADD job_type varchar(40);
ALTER TABLE yabiengine_job ADD module text;
ALTER TABLE yabiengine_job ADD queue varchar(50);
ALTER TABLE yabiengine_job ADD max_memory integer CHECK ("max_memory" >= 0);
COMMIT;
