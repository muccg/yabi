BEGIN;
ALTER TABLE yabiengine_job RENAME COLUMN input_filetype_extensions TO parameter_files;
ALTER TABLE yabiengine_job RENAME COLUMN job_stageins TO other_files;
COMMIT;
