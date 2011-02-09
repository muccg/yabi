BEGIN;
ALTER TABLE "yabi_credential" ADD COLUMN "encrypt_on_login" boolean NOT NULL DEFAULT 'N';
COMMIT;

