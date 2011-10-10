BEGIN; 
ALTER TABLE yabiengine_task RENAME COLUMN expected_ip TO tasktag;
ALTER TABLE yabiengine_task DROP COLUMN expected_port;
END;