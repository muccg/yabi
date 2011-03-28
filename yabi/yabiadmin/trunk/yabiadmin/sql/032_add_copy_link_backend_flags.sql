BEGIN;
ALTER TABLE "yabi_backend" ADD COLUMN "lcopy_supported" boolean NOT NULL DEFAULT 'T';
ALTER TABLE "yabi_backend" ADD COLUMN "link_supported" boolean NOT NULL DEFAULT 'T';
ALTER TABLE "yabi_tool" ADD COLUMN "lcopy_supported" boolean NOT NULL DEFAULT 'T';
ALTER TABLE "yabi_tool" ADD COLUMN "link_supported" boolean NOT NULL DEFAULT 'T';
ALTER TABLE "yabiengine_stagein" ADD COLUMN "method" varchar(5) NOT NULL DEFAULT 'copy';
ALTER TABLE "yabiengine_job" ADD COLUMN "preferred_stagein_method" varchar(5) NOT NULL DEFAULT 'copy';
ALTER TABLE "yabiengine_job" ADD COLUMN "preferred_stageout_method" varchar(5) NOT NULL DEFAULT 'copy';
COMMIT;
