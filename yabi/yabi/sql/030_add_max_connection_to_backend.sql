BEGIN;
ALTER TABLE "yabi_backend" ADD COLUMN "max_connections" integer;
COMMIT;
