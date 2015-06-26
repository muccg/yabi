BEGIN;
ALTER TABLE yabiengine_workflow DROP COLUMN log_file_path;
ALTER TABLE yabiengine_job DROP COLUMN batch_files;
ALTER TABLE yabiengine_job DROP COLUMN parameter_files;
ALTER TABLE yabiengine_job DROP COLUMN other_files;
END;
