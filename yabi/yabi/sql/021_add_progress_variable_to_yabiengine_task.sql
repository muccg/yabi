BEGIN;

ALTER TABLE yabiengine_task ADD "percent_complete" double precision;

COMMIT;