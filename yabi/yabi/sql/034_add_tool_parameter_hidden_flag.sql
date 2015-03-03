BEGIN;
ALTER TABLE "yabi_toolparameter" ADD COLUMN "hidden" boolean NOT NULL DEFAULT 'f';
COMMIT;
