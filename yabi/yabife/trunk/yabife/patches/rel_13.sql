BEGIN;
CREATE TABLE "consumer_useropenid" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "openid_url" varchar(200) NOT NULL UNIQUE
)
;
CREATE TABLE "consumer_openidregistration" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" text,
    "openid_url" text,
    "organisation" text,
    "faculty" text,
    "user_type" text,
    "org_user_id" text,
    "email" text,
    "contact_number" text,
    "supervisor_name" text,
    "supervisor_number" text,
    "supervisor_email" text,
    "project_title" text,
    "project_description" text,
    "rfcd_code_1" text,
    "rfcd_code_1_weight" text,
    "rfcd_code_2" text,
    "rfcd_code_2_weight" text,
    "rfcd_code_3" text,
    "rfcd_code_3_weight" text,
    "resources_compute" text,
    "resources_data" text,
    "resources_network" text,
    "estimate" text,
    "describe" text,
    "software_needs" text,
    "agreement" text
)
;
COMMIT;
