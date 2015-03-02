BEGIN;

SET CONSTRAINTS ALL IMMEDIATE;

-- add a submission script field to backend --
ALTER TABLE "yabi_toolparameter" ADD COLUMN "file_assignment" varchar(5) NOT NULL DEFAULT 'none';

-- set the field to 'batch' where appropriate --
UPDATE "yabi_toolparameter" SET "file_assignment" = 'batch' WHERE "input_file" = 't' AND "batch_param" = 't';

-- set the field to 'none' where appropriate --
UPDATE "yabi_toolparameter" SET "file_assignment" = 'none' WHERE "input_file" = 'f';

-- set the field to 'all' where appropriate --
UPDATE "yabi_toolparameter" SET "file_assignment" = 'batch' WHERE "input_file" = 't' AND "batch_param" = 'f';

-- remove old columns
ALTER TABLE "yabi_toolparameter" DROP COLUMN "input_file";
ALTER TABLE "yabi_toolparameter" DROP COLUMN "batch_param";

COMMIT;
