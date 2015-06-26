BEGIN;

CREATE TABLE "yabiengine_tag" (
    "id" serial NOT NULL PRIMARY KEY,
    "value" varchar(255) NOT NULL
)
;
CREATE TABLE "yabiengine_workflowtag" (
    "id" serial NOT NULL PRIMARY KEY,
    "workflow_id" integer NOT NULL REFERENCES "yabiengine_workflow" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tag_id" integer NOT NULL REFERENCES "yabiengine_tag" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
COMMIT;
