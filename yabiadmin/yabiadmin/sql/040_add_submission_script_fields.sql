BEGIN;

-- add a submission script field to backend --
ALTER TABLE "yabi_backend" ADD COLUMN "submission" text NOT NULL DEFAULT '';

-- add a submission script field to backendcredential --
ALTER TABLE "yabi_backendcredential" ADD COLUMN "submission" text NOT NULL DEFAULT '';

COMMIT;

