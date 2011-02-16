ALTER TABLE yabi_toolparameter ADD COLUMN "extension_param_id" INTEGER REFERENCES "yabi_fileextension" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE yabi_toolparameter DROP COLUMN "source_param_id";
ALTER TABLE yabi_toolparameter ADD use_batch_filename boolean NOT NULL DEFAULT 'N';
