BEGIN;
UPDATE yabi_fileextension SET pattern='*' WHERE pattern = '*.*';
COMMIT;
