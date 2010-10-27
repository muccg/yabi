BEGIN;

CREATE TABLE "yabifeapp_appliance" (
    "id" serial NOT NULL PRIMARY KEY,
    "url" varchar(200) NOT NULL
);

CREATE TABLE "yabifeapp_user" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "appliance_id" integer NOT NULL REFERENCES "yabifeapp_appliance" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX "yabifeapp_user_appliance_id" ON "yabifeapp_user" ("appliance_id");

COMMIT;
