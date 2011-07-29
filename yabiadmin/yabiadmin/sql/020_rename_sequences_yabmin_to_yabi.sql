
BEGIN

-- rename all sequences

ALTER TABLE yabmin_backend_id_seq RENAME TO yabi_backend_id_seq;
ALTER TABLE yabmin_backendcredential_id_seq RENAME TO yabi_backendcredential_id_seq;
ALTER TABLE yabmin_credential_id_seq RENAME TO yabi_credential_id_seq;
ALTER TABLE yabmin_fileextension_id_seq RENAME TO yabi_fileextension_id_seq;
ALTER TABLE yabmin_filetype_extensions_id_seq RENAME TO yabi_filetype_extensions_id_seq;
ALTER TABLE yabmin_filetype_id_seq RENAME TO yabi_filetype_id_seq;
ALTER TABLE yabmin_parameterfilter_id_seq RENAME TO yabi_parameterfilter_id_seq;
ALTER TABLE yabmin_parameterswitchuse_id_seq RENAME TO yabi_parameterswitchuse_id_seq;
ALTER TABLE yabmin_tool_id_seq RENAME TO yabi_tool_id_seq;
ALTER TABLE yabmin_toolgroup_id_seq RENAME TO yabi_toolgroup_id_seq;
ALTER TABLE yabmin_toolgrouping_id_seq RENAME TO yabi_toolgrouping_id_seq;
ALTER TABLE yabmin_tooloutputextension_id_seq RENAME TO yabi_tooloutputextension_id_seq;
ALTER TABLE yabmin_toolparameter_accepted_filetypes_id_seq RENAME TO yabi_toolparameter_accepted_filetypes_id_seq;
ALTER TABLE yabmin_toolparameter_id_seq RENAME TO yabi_toolparameter_id_seq;
ALTER TABLE yabmin_toolparameter_input_extensions_id_seq RENAME TO yabi_toolparameter_input_extensions_id_seq;
ALTER TABLE yabmin_toolset_id_seq RENAME TO yabi_toolset_id_seq;
ALTER TABLE yabmin_user_toolsets_id_seq RENAME TO yabi_user_toolsets_id_seq;
ALTER TABLE yabmin_user_id_seq RENAME TO yabi_user_id_seq;

-- reset PK defaults to use new sequence names

ALTER TABLE yabi_backend ALTER COLUMN id SET DEFAULT nextval('yabi_backend_id_seq');
ALTER TABLE yabi_backendcredential ALTER COLUMN id SET DEFAULT nextval('yabi_backendcredential_id_seq');
ALTER TABLE yabi_credential ALTER COLUMN id SET DEFAULT nextval('yabi_credential_id_seq');
ALTER TABLE yabi_fileextension ALTER COLUMN id SET DEFAULT nextval('yabi_fileextension_id_seq');
ALTER TABLE yabi_filetype_extensions ALTER COLUMN id SET DEFAULT nextval('yabi_filetype_extensions_id_seq');
ALTER TABLE yabi_filetype ALTER COLUMN id SET DEFAULT nextval('yabi_filetype_id_seq');
ALTER TABLE yabi_parameterfilter ALTER COLUMN id SET DEFAULT nextval('yabi_parameterfilter_id_seq');
ALTER TABLE yabi_parameterswitchuse ALTER COLUMN id SET DEFAULT nextval('yabi_parameterswitchuse_id_seq');
ALTER TABLE yabi_tool ALTER COLUMN id SET DEFAULT nextval('yabi_tool_id_seq');
ALTER TABLE yabi_toolgroup ALTER COLUMN id SET DEFAULT nextval('yabi_toolgroup_id_seq');
ALTER TABLE yabi_toolgrouping ALTER COLUMN id SET DEFAULT nextval('yabi_toolgrouping_id_seq');
ALTER TABLE yabi_tooloutputextension ALTER COLUMN id SET DEFAULT nextval('yabi_tooloutputextension_id_seq');
ALTER TABLE yabi_toolparameter_accepted_filetypes ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_accepted_filetypes_id_seq');
ALTER TABLE yabi_toolparameter ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_id_seq');
ALTER TABLE yabi_toolparameter_input_extensions ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_input_extensions_id_seq');
ALTER TABLE yabi_toolset ALTER COLUMN id SET DEFAULT nextval('yabi_toolset_id_seq');
ALTER TABLE yabi_user_toolsets ALTER COLUMN id SET DEFAULT nextval('yabi_user_toolsets_id_seq');
ALTER TABLE yabi_user ALTER COLUMN id SET DEFAULT nextval('yabi_user_id_seq');

COMMIT;

