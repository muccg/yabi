BEGIN;
ALTER TABLE yabi_tool ADD COLUMN new_max_memory VARCHAR(64);
UPDATE yabi_tool SET new_max_memory = max_memory::varchar WHERE max_memory IS NOT NULL;
ALTER TABLE yabi_tool DROP COLUMN max_memory;
ALTER TABLE yabi_tool RENAME COLUMN new_max_memory TO max_memory;
commit;
