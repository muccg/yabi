BEGIN;
UPDATE "yabi_credential" SET password = '' WHERE password is NULL;
UPDATE "yabi_credential" SET cert = '' WHERE cert is NULL;
UPDATE "yabi_credential" SET key = '' WHERE key is NULL;

ALTER TABLE "yabi_credential" ALTER COLUMN "password" SET NOT NULL;
ALTER TABLE "yabi_credential" ALTER COLUMN "cert" SET NOT NULL;
ALTER TABLE "yabi_credential" ALTER COLUMN "key" SET NOT NULL;

COMMIT;

