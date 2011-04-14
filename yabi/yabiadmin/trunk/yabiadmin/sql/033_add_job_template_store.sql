BEGIN;
ALTER TABLE "yabiengine_job" ADD COLUMN "command_template" text;
COMMIT;
