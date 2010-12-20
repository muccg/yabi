BEGIN;

CREATE TABLE "registration_request" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "state" smallint CHECK ("state" >= 0) NOT NULL,
    "confirmation_key" varchar(32) NOT NULL,
    "request_time" timestamp with time zone NOT NULL
);

CREATE TABLE "yabifeapp_applianceadministrator" (
    "id" serial NOT NULL PRIMARY KEY,
    "appliance_id" integer NOT NULL REFERENCES "yabifeapp_appliance" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(200) NOT NULL,
    "email" varchar(75) NOT NULL
);

ALTER TABLE "yabifeapp_appliance" ADD COLUMN "name" VARCHAR(50) NOT NULL DEFAULT '';
ALTER TABLE "yabifeapp_appliance" ADD COLUMN "tos" TEXT NOT NULL DEFAULT '';

COMMIT;
