BEGIN;

-- prevent 'cannot ALTER TABLE "yabi_*" because it has pending trigger events' error --
SET CONSTRAINTS ALL IMMEDIATE;

-- add the new parameters --
ALTER TABLE "yabi_toolparameter" ADD COLUMN "batch_param" boolean NOT NULL DEFAULT 'F';
ALTER TABLE "yabi_toolparameter" ADD COLUMN "batch_bundle_files" boolean NOT NULL DEFAULT 'F';

-- change the output filename base boolean to a foreign key --
ALTER TABLE "yabi_toolparameter" ADD COLUMN "use_output_filename_id" integer NULL;

-- set the right tool parameters to boolean --
UPDATE "yabi_toolparameter" SET "batch_param" = 'T' WHERE id IN ( SELECT "batch_on_param_id" FROM "yabi_tool" WHERE NOT "batch_on_param_id" IS NULL  );
UPDATE "yabi_toolparameter" SET "batch_bundle_files" = 'T' WHERE id IN ( SELECT "batch_on_param_id" FROM "yabi_tool" WHERE NOT "batch_on_param_id" IS NULL AND "batch_on_param_bundle_files"='T' );

-- set this column to the right id for those tool_params set to use_batch_filename --
UPDATE "yabi_toolparameter" SET "use_output_filename_id" = "subquery"."batch_on_param_id" FROM (
    SELECT  "yabi_tool"."id" AS "tool",
            "yabi_tool"."name",
            "yabi_toolparameter"."id" AS "output_param",
            "yabi_tool"."batch_on_param_id"
    FROM "yabi_tool" 
    LEFT JOIN "yabi_toolparameter" 
    ON "yabi_toolparameter"."tool_id" = "yabi_tool"."id" 
    WHERE "yabi_toolparameter"."use_batch_filename"='T'
) AS "subquery" WHERE "yabi_toolparameter"."id" = "subquery"."output_param";

-- drop the old obsolete columns --
ALTER TABLE "yabi_tool" DROP COLUMN "batch_on_param_id";
ALTER TABLE "yabi_tool" DROP COLUMN "batch_on_param_bundle_files";
ALTER TABLE "yabi_toolparameter" DROP COLUMN "use_batch_filename";

COMMIT;
