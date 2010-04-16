ALTER TABLE yabmin_parameterswitchuse RENAME COLUMN value TO formatstring;
ALTER TABLE yabmin_parameterswitchuse ALTER COLUMN formatstring DROP NOT NULL;
