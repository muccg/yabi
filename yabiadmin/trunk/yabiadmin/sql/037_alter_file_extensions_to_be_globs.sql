BEGIN;
ALTER TABLE yabi_fileextension ALTER COLUMN extension TYPE character varying(64);
ALTER TABLE yabi_fileextension RENAME COLUMN extension TO pattern;
UPDATE yabi_fileextension SET pattern='*.'||pattern;
COMMIT;