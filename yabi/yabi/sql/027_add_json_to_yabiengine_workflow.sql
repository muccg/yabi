BEGIN;
ALTER TABLE yabiengine_workflow ADD json text;
ALTER TABLE yabiengine_workflow ADD original_json text;
COMMIT;
