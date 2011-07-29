BEGIN;

DELETE FROM "yabifeapp_appliance";

INSERT INTO "yabifeapp_appliance" ("url") VALUES ('https://ccg5python.localdomain/yabiadmin/');

INSERT INTO "yabifeapp_user" ("user_id", "appliance_id")
    SELECT "auth_user"."id", "yabifeapp_appliance"."id"
    FROM "auth_user", "yabifeapp_appliance";

COMMIT;
