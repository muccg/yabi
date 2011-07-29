BEGIN;

ALTER TABLE "yabifeapp_user" ADD COLUMN "user_option_access" BOOLEAN DEFAULT 't' NOT NULL;
ALTER TABLE "yabifeapp_user" ADD COLUMN "credential_access" BOOLEAN DEFAULT 't' NOT NULL;

COMMIT;
