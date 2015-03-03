BEGIN;
ALTER TABLE yabiengine_task ADD expected_port integer;
ALTER TABLE yabiengine_task ADD expected_ip varchar(256);
COMMIT;
