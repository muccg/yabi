BEGIN;
ALTER TABLE yabiengine_task ADD "name" varchar(256) default '';
COMMIT;
