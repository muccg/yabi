BEGIN;
ALTER TABLE "yabi_credential" ADD "expires_on" timestamp with time zone;
ALTER TABLE "yabi_credential" ADD "encrypted" boolean NOT NULL DEFAULT False;
COMMIT;

