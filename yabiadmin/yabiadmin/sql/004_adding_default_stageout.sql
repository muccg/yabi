BEGIN;
ALTER TABLE yabmin_backendcredential ADD default_stageout boolean;
COMMIT;
