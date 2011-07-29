ALTER TABLE yabi_toolparameter ADD COLUMN "extension_param_id" INTEGER REFERENCES "yabi_fileextension" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE yabi_toolparameter DROP COLUMN "source_param_id";
ALTER TABLE yabi_toolparameter ADD use_batch_filename boolean NOT NULL DEFAULT 'N';

--- it may be neccessary to replace the commands in the running jobs on live after deployment of this patch and its release
--- use this sql

---begin;
---update yabiengine_job set command = replace( command, '%', '__yabi_bp') where id in (select id from yabiengine_job where status = 'running');
---end;

---begin;
---update yabiengine_job set command = replace( command, '$', '__yabi_fp') where id in (select id from yabiengine_job where status = 'running');
---end;
