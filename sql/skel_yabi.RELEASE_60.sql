--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.yabi_user_toolsets DROP CONSTRAINT yabmin_user_toolsets_user_id_fkey;
ALTER TABLE ONLY public.yabi_user_toolsets DROP CONSTRAINT yabmin_user_toolsets_toolset_id_fkey;
ALTER TABLE ONLY public.yabi_user DROP CONSTRAINT yabmin_user_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_user DROP CONSTRAINT yabmin_user_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolset DROP CONSTRAINT yabmin_toolset_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolset DROP CONSTRAINT yabmin_toolset_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabmin_toolparameter_tool_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabmin_toolparameter_switch_use_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabmin_toolparameter_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter_input_extensions DROP CONSTRAINT yabmin_toolparameter_input_extensions_toolparameter_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter_input_extensions DROP CONSTRAINT yabmin_toolparameter_input_extensions_fileextension_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabmin_toolparameter_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter_accepted_filetypes DROP CONSTRAINT yabmin_toolparameter_accepted_filetypes_toolparameter_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter_accepted_filetypes DROP CONSTRAINT yabmin_toolparameter_accepted_filetypes_filetype_id_fkey;
ALTER TABLE ONLY public.yabi_tooloutputextension DROP CONSTRAINT yabmin_tooloutputextension_tool_id_fkey;
ALTER TABLE ONLY public.yabi_tooloutputextension DROP CONSTRAINT yabmin_tooloutputextension_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_tooloutputextension DROP CONSTRAINT yabmin_tooloutputextension_file_extension_id_fkey;
ALTER TABLE ONLY public.yabi_tooloutputextension DROP CONSTRAINT yabmin_tooloutputextension_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT yabmin_toolgrouping_tool_id_fkey;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT yabmin_toolgrouping_tool_group_id_fkey;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT yabmin_toolgrouping_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT yabmin_toolgrouping_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolgroup DROP CONSTRAINT yabmin_toolgroup_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_toolgroup DROP CONSTRAINT yabmin_toolgroup_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_tool DROP CONSTRAINT yabmin_tool_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_tool DROP CONSTRAINT yabmin_tool_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_parameterswitchuse DROP CONSTRAINT yabmin_parameterswitchuse_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_parameterswitchuse DROP CONSTRAINT yabmin_parameterswitchuse_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_parameterfilter DROP CONSTRAINT yabmin_parameterfilter_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_parameterfilter DROP CONSTRAINT yabmin_parameterfilter_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_filetype DROP CONSTRAINT yabmin_filetype_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_filetype_extensions DROP CONSTRAINT yabmin_filetype_extensions_filetype_id_fkey;
ALTER TABLE ONLY public.yabi_filetype_extensions DROP CONSTRAINT yabmin_filetype_extensions_fileextension_id_fkey;
ALTER TABLE ONLY public.yabi_filetype DROP CONSTRAINT yabmin_filetype_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_fileextension DROP CONSTRAINT yabmin_fileextension_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_fileextension DROP CONSTRAINT yabmin_fileextension_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_credential DROP CONSTRAINT yabmin_credential_user_id_fkey;
ALTER TABLE ONLY public.yabi_credential DROP CONSTRAINT yabmin_credential_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_credential DROP CONSTRAINT yabmin_credential_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_backendcredential DROP CONSTRAINT yabmin_backendcredential_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_backendcredential DROP CONSTRAINT yabmin_backendcredential_credential_id_fkey;
ALTER TABLE ONLY public.yabi_backendcredential DROP CONSTRAINT yabmin_backendcredential_created_by_id_fkey;
ALTER TABLE ONLY public.yabi_backendcredential DROP CONSTRAINT yabmin_backendcredential_backend_id_fkey;
ALTER TABLE ONLY public.yabi_backend DROP CONSTRAINT yabmin_backend_last_modified_by_id_fkey;
ALTER TABLE ONLY public.yabi_backend DROP CONSTRAINT yabmin_backend_created_by_id_fkey;
ALTER TABLE ONLY public.yabiengine_workflowtag DROP CONSTRAINT yabiengine_workflowtag_workflow_id_fkey;
ALTER TABLE ONLY public.yabiengine_workflowtag DROP CONSTRAINT yabiengine_workflowtag_tag_id_fkey;
ALTER TABLE ONLY public.yabiengine_workflow DROP CONSTRAINT yabiengine_workflow_user_id_fkey;
ALTER TABLE ONLY public.yabiengine_task DROP CONSTRAINT yabiengine_task_job_id_fkey;
ALTER TABLE ONLY public.yabiengine_stagein DROP CONSTRAINT yabiengine_stagein_task_id_fkey;
ALTER TABLE ONLY public.yabiengine_queuedworkflow DROP CONSTRAINT yabiengine_queuedworkflow_workflow_id_fkey;
ALTER TABLE ONLY public.yabiengine_job DROP CONSTRAINT yabiengine_job_workflow_id_fkey;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabi_toolparameter_extension_param_id_fkey;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT user_id_refs_id_c8665aa;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT tool_set_id_refs_id_47dac439;
ALTER TABLE ONLY public.ghettoq_message DROP CONSTRAINT ghettoq_message_queue_id_fkey;
ALTER TABLE ONLY public.django_evolution DROP CONSTRAINT django_evolution_version_id_fkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT content_type_id_refs_id_728de91f;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT content_type_id_refs_id_288599e6;
ALTER TABLE ONLY public.yabi_tool DROP CONSTRAINT backend_id_refs_id_191701d8;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_fkey;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_permission_id_fkey;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_fkey;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_group_id_fkey;
ALTER TABLE ONLY public.auth_message DROP CONSTRAINT auth_message_user_id_fkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_permission_id_fkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_fkey;
DROP INDEX public.yabmin_user_last_modified_by_id;
DROP INDEX public.yabmin_user_created_by_id;
DROP INDEX public.yabmin_toolset_last_modified_by_id;
DROP INDEX public.yabmin_toolset_created_by_id;
DROP INDEX public.yabmin_toolparameter_tool_id;
DROP INDEX public.yabmin_toolparameter_switch_use_id;
DROP INDEX public.yabmin_toolparameter_last_modified_by_id;
DROP INDEX public.yabmin_toolparameter_extension_param_id;
DROP INDEX public.yabmin_toolparameter_created_by_id;
DROP INDEX public.yabmin_tooloutputextension_tool_id;
DROP INDEX public.yabmin_tooloutputextension_last_modified_by_id;
DROP INDEX public.yabmin_tooloutputextension_file_extension_id;
DROP INDEX public.yabmin_tooloutputextension_created_by_id;
DROP INDEX public.yabmin_toolgrouping_tool_set_id;
DROP INDEX public.yabmin_toolgrouping_tool_id;
DROP INDEX public.yabmin_toolgrouping_tool_group_id;
DROP INDEX public.yabmin_toolgrouping_last_modified_by_id;
DROP INDEX public.yabmin_toolgrouping_created_by_id;
DROP INDEX public.yabmin_toolgroup_last_modified_by_id;
DROP INDEX public.yabmin_toolgroup_created_by_id;
DROP INDEX public.yabmin_tool_last_modified_by_id;
DROP INDEX public.yabmin_tool_fs_backend_id;
DROP INDEX public.yabmin_tool_created_by_id;
DROP INDEX public.yabmin_tool_backend_id;
DROP INDEX public.yabmin_parameterswitchuse_last_modified_by_id;
DROP INDEX public.yabmin_parameterswitchuse_created_by_id;
DROP INDEX public.yabmin_parameterfilter_last_modified_by_id;
DROP INDEX public.yabmin_parameterfilter_created_by_id;
DROP INDEX public.yabmin_filetype_last_modified_by_id;
DROP INDEX public.yabmin_filetype_created_by_id;
DROP INDEX public.yabmin_fileextension_last_modified_by_id;
DROP INDEX public.yabmin_fileextension_created_by_id;
DROP INDEX public.yabmin_credential_user_id;
DROP INDEX public.yabmin_credential_last_modified_by_id;
DROP INDEX public.yabmin_credential_created_by_id;
DROP INDEX public.yabmin_backendcredential_last_modified_by_id;
DROP INDEX public.yabmin_backendcredential_credential_id;
DROP INDEX public.yabmin_backendcredential_created_by_id;
DROP INDEX public.yabmin_backendcredential_backend_id;
DROP INDEX public.yabmin_backend_last_modified_by_id;
DROP INDEX public.yabmin_backend_created_by_id;
DROP INDEX public.yabiengine_workflow_user_id;
DROP INDEX public.yabiengine_task_job_id;
DROP INDEX public.yabiengine_stagein_task_id;
DROP INDEX public.yabiengine_queuedworkflow_workflow_id;
DROP INDEX public.yabiengine_job_workflow_id;
DROP INDEX public.ghettoq_message_visible;
DROP INDEX public.ghettoq_message_sent_at;
DROP INDEX public.ghettoq_message_queue_id;
DROP INDEX public.django_evolution_version_id;
DROP INDEX public.django_admin_log_user_id;
DROP INDEX public.django_admin_log_content_type_id;
DROP INDEX public.auth_permission_content_type_id;
DROP INDEX public.auth_message_user_id;
ALTER TABLE ONLY public.yabi_user_toolsets DROP CONSTRAINT yabmin_user_toolsets_user_id_key;
ALTER TABLE ONLY public.yabi_user_toolsets DROP CONSTRAINT yabmin_user_toolsets_pkey;
ALTER TABLE ONLY public.yabi_user DROP CONSTRAINT yabmin_user_pkey;
ALTER TABLE ONLY public.yabi_user DROP CONSTRAINT yabmin_user_name_key;
ALTER TABLE ONLY public.yabi_toolset DROP CONSTRAINT yabmin_toolset_pkey;
ALTER TABLE ONLY public.yabi_toolset DROP CONSTRAINT yabmin_toolset_name_key;
ALTER TABLE ONLY public.yabi_toolparameter DROP CONSTRAINT yabmin_toolparameter_pkey;
ALTER TABLE ONLY public.yabi_toolparameter_input_extensions DROP CONSTRAINT yabmin_toolparameter_input_extensions_toolparameter_id_key;
ALTER TABLE ONLY public.yabi_toolparameter_input_extensions DROP CONSTRAINT yabmin_toolparameter_input_extensions_pkey;
ALTER TABLE ONLY public.yabi_toolparameter_accepted_filetypes DROP CONSTRAINT yabmin_toolparameter_accepted_filetypes_toolparameter_id_key;
ALTER TABLE ONLY public.yabi_toolparameter_accepted_filetypes DROP CONSTRAINT yabmin_toolparameter_accepted_filetypes_pkey;
ALTER TABLE ONLY public.yabi_tooloutputextension DROP CONSTRAINT yabmin_tooloutputextension_pkey;
ALTER TABLE ONLY public.yabi_toolgrouping DROP CONSTRAINT yabmin_toolgrouping_pkey;
ALTER TABLE ONLY public.yabi_toolgroup DROP CONSTRAINT yabmin_toolgroup_pkey;
ALTER TABLE ONLY public.yabi_toolgroup DROP CONSTRAINT yabmin_toolgroup_name_key;
ALTER TABLE ONLY public.yabi_tool DROP CONSTRAINT yabmin_tool_pkey;
ALTER TABLE ONLY public.yabi_tool DROP CONSTRAINT yabmin_tool_name_key;
ALTER TABLE ONLY public.yabi_parameterswitchuse DROP CONSTRAINT yabmin_parameterswitchuse_pkey;
ALTER TABLE ONLY public.yabi_parameterfilter DROP CONSTRAINT yabmin_parameterfilter_pkey;
ALTER TABLE ONLY public.yabi_filetype DROP CONSTRAINT yabmin_filetype_pkey;
ALTER TABLE ONLY public.yabi_filetype DROP CONSTRAINT yabmin_filetype_name_key;
ALTER TABLE ONLY public.yabi_filetype_extensions DROP CONSTRAINT yabmin_filetype_extensions_pkey;
ALTER TABLE ONLY public.yabi_filetype_extensions DROP CONSTRAINT yabmin_filetype_extensions_filetype_id_key;
ALTER TABLE ONLY public.yabi_fileextension DROP CONSTRAINT yabmin_fileextension_pkey;
ALTER TABLE ONLY public.yabi_fileextension DROP CONSTRAINT yabmin_fileextension_extension_key;
ALTER TABLE ONLY public.yabi_credential DROP CONSTRAINT yabmin_credential_pkey;
ALTER TABLE ONLY public.yabi_backendcredential DROP CONSTRAINT yabmin_backendcredential_pkey;
ALTER TABLE ONLY public.yabi_backend DROP CONSTRAINT yabmin_backend_pkey;
ALTER TABLE ONLY public.yabiengine_workflowtag DROP CONSTRAINT yabiengine_workflowtag_pkey;
ALTER TABLE ONLY public.yabiengine_workflow DROP CONSTRAINT yabiengine_workflow_pkey;
ALTER TABLE ONLY public.yabiengine_task DROP CONSTRAINT yabiengine_task_pkey;
ALTER TABLE ONLY public.yabiengine_tag DROP CONSTRAINT yabiengine_tag_pkey;
ALTER TABLE ONLY public.yabiengine_syslog DROP CONSTRAINT yabiengine_syslog_pkey;
ALTER TABLE ONLY public.yabiengine_stagein DROP CONSTRAINT yabiengine_stagein_pkey;
ALTER TABLE ONLY public.yabiengine_queuedworkflow DROP CONSTRAINT yabiengine_queuedworkflow_pkey;
ALTER TABLE ONLY public.yabiengine_job DROP CONSTRAINT yabiengine_job_pkey;
ALTER TABLE ONLY public.ghettoq_queue DROP CONSTRAINT ghettoq_queue_pkey;
ALTER TABLE ONLY public.ghettoq_queue DROP CONSTRAINT ghettoq_queue_name_key;
ALTER TABLE ONLY public.ghettoq_message DROP CONSTRAINT ghettoq_message_pkey;
ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_pkey;
ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
ALTER TABLE ONLY public.django_project_version DROP CONSTRAINT django_project_version_pkey;
ALTER TABLE ONLY public.django_evolution DROP CONSTRAINT django_evolution_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_key;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
ALTER TABLE ONLY public.celery_tasksetmeta DROP CONSTRAINT celery_tasksetmeta_taskset_id_key;
ALTER TABLE ONLY public.celery_tasksetmeta DROP CONSTRAINT celery_tasksetmeta_pkey;
ALTER TABLE ONLY public.celery_taskmeta DROP CONSTRAINT celery_taskmeta_task_id_key;
ALTER TABLE ONLY public.celery_taskmeta DROP CONSTRAINT celery_taskmeta_pkey;
ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_username_key;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_key;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_pkey;
ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_pkey;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_key;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_pkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_key;
ALTER TABLE ONLY public.auth_message DROP CONSTRAINT auth_message_pkey;
ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_key;
ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
ALTER TABLE public.yabiengine_workflowtag ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_workflow ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_task ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_tag ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_syslog ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_stagein ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_queuedworkflow ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabiengine_job ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_user_toolsets ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolset ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolparameter_input_extensions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolparameter_accepted_filetypes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolparameter ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_tooloutputextension ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolgrouping ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_toolgroup ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_tool ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_parameterswitchuse ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_parameterfilter ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_filetype_extensions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_filetype ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_fileextension ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_credential ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_backendcredential ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabi_backend ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ghettoq_queue ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.ghettoq_message ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_site ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_project_version ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_evolution ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_message ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.yabiengine_workflowtag_id_seq;
DROP TABLE public.yabiengine_workflowtag;
DROP SEQUENCE public.yabiengine_workflow_id_seq;
DROP TABLE public.yabiengine_workflow;
DROP SEQUENCE public.yabiengine_task_id_seq;
DROP TABLE public.yabiengine_task;
DROP SEQUENCE public.yabiengine_tag_id_seq;
DROP TABLE public.yabiengine_tag;
DROP SEQUENCE public.yabiengine_syslog_id_seq;
DROP TABLE public.yabiengine_syslog;
DROP SEQUENCE public.yabiengine_stagein_id_seq;
DROP TABLE public.yabiengine_stagein;
DROP SEQUENCE public.yabiengine_queuedworkflow_id_seq;
DROP TABLE public.yabiengine_queuedworkflow;
DROP SEQUENCE public.yabiengine_job_id_seq;
DROP TABLE public.yabiengine_job;
DROP SEQUENCE public.yabi_user_toolsets_id_seq;
DROP TABLE public.yabi_user_toolsets;
DROP SEQUENCE public.yabi_user_id_seq;
DROP TABLE public.yabi_user;
DROP SEQUENCE public.yabi_toolset_id_seq;
DROP TABLE public.yabi_toolset;
DROP SEQUENCE public.yabi_toolparameter_input_extensions_id_seq;
DROP TABLE public.yabi_toolparameter_input_extensions;
DROP SEQUENCE public.yabi_toolparameter_id_seq;
DROP SEQUENCE public.yabi_toolparameter_accepted_filetypes_id_seq;
DROP TABLE public.yabi_toolparameter_accepted_filetypes;
DROP TABLE public.yabi_toolparameter;
DROP SEQUENCE public.yabi_tooloutputextension_id_seq;
DROP TABLE public.yabi_tooloutputextension;
DROP SEQUENCE public.yabi_toolgrouping_id_seq;
DROP TABLE public.yabi_toolgrouping;
DROP SEQUENCE public.yabi_toolgroup_id_seq;
DROP TABLE public.yabi_toolgroup;
DROP SEQUENCE public.yabi_tool_id_seq;
DROP TABLE public.yabi_tool;
DROP SEQUENCE public.yabi_parameterswitchuse_id_seq;
DROP TABLE public.yabi_parameterswitchuse;
DROP SEQUENCE public.yabi_parameterfilter_id_seq;
DROP TABLE public.yabi_parameterfilter;
DROP SEQUENCE public.yabi_filetype_id_seq;
DROP SEQUENCE public.yabi_filetype_extensions_id_seq;
DROP TABLE public.yabi_filetype_extensions;
DROP TABLE public.yabi_filetype;
DROP SEQUENCE public.yabi_fileextension_id_seq;
DROP TABLE public.yabi_fileextension;
DROP SEQUENCE public.yabi_credential_id_seq;
DROP TABLE public.yabi_credential;
DROP SEQUENCE public.yabi_backendcredential_id_seq;
DROP TABLE public.yabi_backendcredential;
DROP SEQUENCE public.yabi_backend_id_seq;
DROP TABLE public.yabi_backend;
DROP SEQUENCE public.ghettoq_queue_id_seq;
DROP TABLE public.ghettoq_queue;
DROP SEQUENCE public.ghettoq_message_id_seq;
DROP TABLE public.ghettoq_message;
DROP SEQUENCE public.django_site_id_seq;
DROP TABLE public.django_site;
DROP TABLE public.django_session;
DROP SEQUENCE public.django_project_version_id_seq;
DROP TABLE public.django_project_version;
DROP SEQUENCE public.django_evolution_id_seq;
DROP TABLE public.django_evolution;
DROP SEQUENCE public.django_content_type_id_seq;
DROP TABLE public.django_content_type;
DROP SEQUENCE public.django_admin_log_id_seq;
DROP TABLE public.django_admin_log;
DROP TABLE public.celery_tasksetmeta;
DROP SEQUENCE public.celery_tasksetmeta_id_seq;
DROP TABLE public.celery_taskmeta;
DROP SEQUENCE public.celery_taskmeta_id_seq;
DROP SEQUENCE public.auth_user_user_permissions_id_seq;
DROP TABLE public.auth_user_user_permissions;
DROP SEQUENCE public.auth_user_id_seq;
DROP SEQUENCE public.auth_user_groups_id_seq;
DROP TABLE public.auth_user_groups;
DROP TABLE public.auth_user;
DROP SEQUENCE public.auth_permission_id_seq;
DROP TABLE public.auth_permission;
DROP SEQUENCE public.auth_message_id_seq;
DROP TABLE public.auth_message;
DROP SEQUENCE public.auth_group_permissions_id_seq;
DROP TABLE public.auth_group_permissions;
DROP SEQUENCE public.auth_group_id_seq;
DROP TABLE public.auth_group;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: yabiapp
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO yabiapp;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO yabiapp;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO yabiapp;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO yabiapp;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO yabiapp;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_message; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO yabiapp;

--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO yabiapp;

--
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- Name: auth_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_message_id_seq', 1, true);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO yabiapp;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO yabiapp;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_permission_id_seq', 105, true);


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(256) NOT NULL,
    first_name character varying(256) NOT NULL,
    last_name character varying(256) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO yabiapp;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO yabiapp;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO yabiapp;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 2, true);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO yabiapp;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO yabiapp;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO yabiapp;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Name: celery_taskmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE celery_taskmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.celery_taskmeta_id_seq OWNER TO yabiapp;

--
-- Name: celery_taskmeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('celery_taskmeta_id_seq', 1, false);


--
-- Name: celery_taskmeta; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE celery_taskmeta (
    id integer DEFAULT nextval('celery_taskmeta_id_seq'::regclass) NOT NULL,
    task_id character varying(255) NOT NULL,
    status character varying(50) NOT NULL,
    result text NOT NULL,
    date_done timestamp with time zone NOT NULL,
    traceback text
);


ALTER TABLE public.celery_taskmeta OWNER TO yabiapp;

--
-- Name: celery_tasksetmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE celery_tasksetmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.celery_tasksetmeta_id_seq OWNER TO yabiapp;

--
-- Name: celery_tasksetmeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('celery_tasksetmeta_id_seq', 1, false);


--
-- Name: celery_tasksetmeta; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE celery_tasksetmeta (
    id integer DEFAULT nextval('celery_tasksetmeta_id_seq'::regclass) NOT NULL,
    taskset_id character varying(255) NOT NULL,
    result text NOT NULL,
    date_done timestamp with time zone NOT NULL
);


ALTER TABLE public.celery_tasksetmeta OWNER TO yabiapp;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO yabiapp;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO yabiapp;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, true);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO yabiapp;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO yabiapp;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('django_content_type_id_seq', 49, true);


--
-- Name: django_evolution; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_evolution (
    id integer NOT NULL,
    version_id integer NOT NULL,
    app_label character varying(200) NOT NULL,
    label character varying(100) NOT NULL
);


ALTER TABLE public.django_evolution OWNER TO yabiapp;

--
-- Name: django_evolution_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE django_evolution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_evolution_id_seq OWNER TO yabiapp;

--
-- Name: django_evolution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE django_evolution_id_seq OWNED BY django_evolution.id;


--
-- Name: django_evolution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('django_evolution_id_seq', 1, true);


--
-- Name: django_project_version; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_project_version (
    id integer NOT NULL,
    signature text NOT NULL,
    "when" timestamp with time zone NOT NULL
);


ALTER TABLE public.django_project_version OWNER TO yabiapp;

--
-- Name: django_project_version_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE django_project_version_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_project_version_id_seq OWNER TO yabiapp;

--
-- Name: django_project_version_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE django_project_version_id_seq OWNED BY django_project_version.id;


--
-- Name: django_project_version_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('django_project_version_id_seq', 1, true);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO yabiapp;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO yabiapp;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO yabiapp;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('django_site_id_seq', 1, true);


--
-- Name: ghettoq_message; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE ghettoq_message (
    id integer NOT NULL,
    visible boolean NOT NULL,
    sent_at timestamp with time zone,
    payload text NOT NULL,
    queue_id integer NOT NULL
);


ALTER TABLE public.ghettoq_message OWNER TO yabiapp;

--
-- Name: ghettoq_message_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE ghettoq_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.ghettoq_message_id_seq OWNER TO yabiapp;

--
-- Name: ghettoq_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE ghettoq_message_id_seq OWNED BY ghettoq_message.id;


--
-- Name: ghettoq_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('ghettoq_message_id_seq', 1, true);


--
-- Name: ghettoq_queue; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE ghettoq_queue (
    id integer NOT NULL,
    name character varying(200) NOT NULL
);


ALTER TABLE public.ghettoq_queue OWNER TO yabiapp;

--
-- Name: ghettoq_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE ghettoq_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.ghettoq_queue_id_seq OWNER TO yabiapp;

--
-- Name: ghettoq_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE ghettoq_queue_id_seq OWNED BY ghettoq_queue.id;


--
-- Name: ghettoq_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('ghettoq_queue_id_seq', 1, true);


--
-- Name: yabi_backend; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_backend (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(512) NOT NULL,
    hostname character varying(512) NOT NULL,
    port integer,
    path character varying(512) NOT NULL,
    scheme character varying(64),
    max_connections integer,
    lcopy_supported boolean DEFAULT false NOT NULL,
    link_supported boolean DEFAULT false NOT NULL
);


ALTER TABLE public.yabi_backend OWNER TO yabiapp;

--
-- Name: yabi_backend_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_backend_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_backend_id_seq OWNER TO yabiapp;

--
-- Name: yabi_backend_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_backend_id_seq OWNED BY yabi_backend.id;


--
-- Name: yabi_backend_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_backend_id_seq', 1, true);


--
-- Name: yabi_backendcredential; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_backendcredential (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    backend_id integer NOT NULL,
    credential_id integer NOT NULL,
    homedir character varying(512),
    visible boolean DEFAULT false NOT NULL,
    default_stageout boolean
);


ALTER TABLE public.yabi_backendcredential OWNER TO yabiapp;

--
-- Name: yabi_backendcredential_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_backendcredential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_backendcredential_id_seq OWNER TO yabiapp;

--
-- Name: yabi_backendcredential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_backendcredential_id_seq OWNED BY yabi_backendcredential.id;


--
-- Name: yabi_backendcredential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_backendcredential_id_seq', 1, true);


--
-- Name: yabi_credential; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_credential (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    description character varying(512) NOT NULL,
    username character varying(512) NOT NULL,
    password character varying(512) NOT NULL,
    cert text NOT NULL,
    key text NOT NULL,
    user_id integer NOT NULL,
    expires_on timestamp with time zone,
    encrypted boolean DEFAULT false NOT NULL,
    encrypt_on_login boolean DEFAULT false NOT NULL
);


ALTER TABLE public.yabi_credential OWNER TO yabiapp;

--
-- Name: yabi_credential_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_credential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_credential_id_seq OWNER TO yabiapp;

--
-- Name: yabi_credential_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_credential_id_seq OWNED BY yabi_credential.id;


--
-- Name: yabi_credential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_credential_id_seq', 1, true);


--
-- Name: yabi_fileextension; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_fileextension (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    extension character varying(10) NOT NULL
);


ALTER TABLE public.yabi_fileextension OWNER TO yabiapp;

--
-- Name: yabi_fileextension_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_fileextension_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_fileextension_id_seq OWNER TO yabiapp;

--
-- Name: yabi_fileextension_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_fileextension_id_seq OWNED BY yabi_fileextension.id;


--
-- Name: yabi_fileextension_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_fileextension_id_seq', 102, true);


--
-- Name: yabi_filetype; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_filetype (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(255) NOT NULL,
    description text
);


ALTER TABLE public.yabi_filetype OWNER TO yabiapp;

--
-- Name: yabi_filetype_extensions; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_filetype_extensions (
    id integer NOT NULL,
    filetype_id integer NOT NULL,
    fileextension_id integer NOT NULL
);


ALTER TABLE public.yabi_filetype_extensions OWNER TO yabiapp;

--
-- Name: yabi_filetype_extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_filetype_extensions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_filetype_extensions_id_seq OWNER TO yabiapp;

--
-- Name: yabi_filetype_extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_filetype_extensions_id_seq OWNED BY yabi_filetype_extensions.id;


--
-- Name: yabi_filetype_extensions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_filetype_extensions_id_seq', 174, true);


--
-- Name: yabi_filetype_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_filetype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_filetype_id_seq OWNER TO yabiapp;

--
-- Name: yabi_filetype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_filetype_id_seq OWNED BY yabi_filetype.id;


--
-- Name: yabi_filetype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_filetype_id_seq', 66, true);


--
-- Name: yabi_parameterfilter; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_parameterfilter (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    display_text character varying(30) NOT NULL,
    value character varying(20) NOT NULL,
    description text
);


ALTER TABLE public.yabi_parameterfilter OWNER TO yabiapp;

--
-- Name: yabi_parameterfilter_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_parameterfilter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_parameterfilter_id_seq OWNER TO yabiapp;

--
-- Name: yabi_parameterfilter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_parameterfilter_id_seq OWNED BY yabi_parameterfilter.id;


--
-- Name: yabi_parameterfilter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_parameterfilter_id_seq', 4, true);


--
-- Name: yabi_parameterswitchuse; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_parameterswitchuse (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    display_text character varying(30) NOT NULL,
    formatstring character varying(256),
    description text
);


ALTER TABLE public.yabi_parameterswitchuse OWNER TO yabiapp;

--
-- Name: yabi_parameterswitchuse_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_parameterswitchuse_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_parameterswitchuse_id_seq OWNER TO yabiapp;

--
-- Name: yabi_parameterswitchuse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_parameterswitchuse_id_seq OWNED BY yabi_parameterswitchuse.id;


--
-- Name: yabi_parameterswitchuse_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_parameterswitchuse_id_seq', 13, true);


--
-- Name: yabi_tool; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_tool (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    path character varying(512),
    description text,
    enabled boolean NOT NULL,
    backend_id integer NOT NULL,
    accepts_input boolean NOT NULL,
    walltime character varying(64),
    cpus character varying(64),
    fs_backend_id integer NOT NULL,
    module text,
    queue character varying(50),
    job_type character varying(40),
    max_memory integer,
    lcopy_supported boolean DEFAULT false NOT NULL,
    link_supported boolean DEFAULT false NOT NULL,
    CONSTRAINT yabmin_tool_max_memory_check CHECK ((max_memory >= 0))
);


ALTER TABLE public.yabi_tool OWNER TO yabiapp;

--
-- Name: yabi_tool_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_tool_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_tool_id_seq OWNER TO yabiapp;

--
-- Name: yabi_tool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_tool_id_seq OWNED BY yabi_tool.id;


--
-- Name: yabi_tool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_tool_id_seq', 1, true);


--
-- Name: yabi_toolgroup; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolgroup (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.yabi_toolgroup OWNER TO yabiapp;

--
-- Name: yabi_toolgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolgroup_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolgroup_id_seq OWNED BY yabi_toolgroup.id;


--
-- Name: yabi_toolgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolgroup_id_seq', 1, true);


--
-- Name: yabi_toolgrouping; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolgrouping (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    tool_id integer NOT NULL,
    tool_set_id integer NOT NULL,
    tool_group_id integer NOT NULL
);


ALTER TABLE public.yabi_toolgrouping OWNER TO yabiapp;

--
-- Name: yabi_toolgrouping_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolgrouping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolgrouping_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolgrouping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolgrouping_id_seq OWNED BY yabi_toolgrouping.id;


--
-- Name: yabi_toolgrouping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolgrouping_id_seq', 1, true);


--
-- Name: yabi_tooloutputextension; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_tooloutputextension (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    tool_id integer NOT NULL,
    file_extension_id integer NOT NULL,
    must_exist boolean,
    must_be_larger_than integer,
    CONSTRAINT yabmin_tooloutputextension_must_be_larger_than_check CHECK ((must_be_larger_than >= 0))
);


ALTER TABLE public.yabi_tooloutputextension OWNER TO yabiapp;

--
-- Name: yabi_tooloutputextension_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_tooloutputextension_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_tooloutputextension_id_seq OWNER TO yabiapp;

--
-- Name: yabi_tooloutputextension_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_tooloutputextension_id_seq OWNED BY yabi_tooloutputextension.id;


--
-- Name: yabi_tooloutputextension_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_tooloutputextension_id_seq', 1, true);


--
-- Name: yabi_toolparameter; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolparameter (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    tool_id integer NOT NULL,
    rank integer,
    mandatory boolean NOT NULL,
    input_file boolean NOT NULL,
    output_file boolean NOT NULL,
    switch character varying(64) NOT NULL,
    switch_use_id integer NOT NULL,
    extension_param_id integer,
    possible_values text,
    default_value text,
    helptext text,
    hidden boolean DEFAULT false NOT NULL,
    batch_param boolean DEFAULT false NOT NULL,
    batch_bundle_files boolean DEFAULT false NOT NULL,
    use_output_filename_id integer
);


ALTER TABLE public.yabi_toolparameter OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_accepted_filetypes; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolparameter_accepted_filetypes (
    id integer NOT NULL,
    toolparameter_id integer NOT NULL,
    filetype_id integer NOT NULL
);


ALTER TABLE public.yabi_toolparameter_accepted_filetypes OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_accepted_filetypes_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolparameter_accepted_filetypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolparameter_accepted_filetypes_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_accepted_filetypes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolparameter_accepted_filetypes_id_seq OWNED BY yabi_toolparameter_accepted_filetypes.id;


--
-- Name: yabi_toolparameter_accepted_filetypes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolparameter_accepted_filetypes_id_seq', 1, true);


--
-- Name: yabi_toolparameter_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolparameter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolparameter_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolparameter_id_seq OWNED BY yabi_toolparameter.id;


--
-- Name: yabi_toolparameter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolparameter_id_seq', 1, true);


--
-- Name: yabi_toolparameter_input_extensions; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolparameter_input_extensions (
    id integer NOT NULL,
    toolparameter_id integer NOT NULL,
    fileextension_id integer NOT NULL
);


ALTER TABLE public.yabi_toolparameter_input_extensions OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_input_extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolparameter_input_extensions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolparameter_input_extensions_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolparameter_input_extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolparameter_input_extensions_id_seq OWNED BY yabi_toolparameter_input_extensions.id;


--
-- Name: yabi_toolparameter_input_extensions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolparameter_input_extensions_id_seq', 1, true);


--
-- Name: yabi_toolset; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_toolset (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.yabi_toolset OWNER TO yabiapp;

--
-- Name: yabi_toolset_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_toolset_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_toolset_id_seq OWNER TO yabiapp;

--
-- Name: yabi_toolset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_toolset_id_seq OWNED BY yabi_toolset.id;


--
-- Name: yabi_toolset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_toolset_id_seq', 1, true);


--
-- Name: yabi_user; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_user (
    id integer NOT NULL,
    last_modified_by_id integer,
    last_modified_on timestamp with time zone,
    created_by_id integer,
    created_on timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.yabi_user OWNER TO yabiapp;

--
-- Name: yabi_user_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_user_id_seq OWNER TO yabiapp;

--
-- Name: yabi_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_user_id_seq OWNED BY yabi_user.id;


--
-- Name: yabi_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_user_id_seq', 1, true);


--
-- Name: yabi_user_toolsets; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabi_user_toolsets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    toolset_id integer NOT NULL
);


ALTER TABLE public.yabi_user_toolsets OWNER TO yabiapp;

--
-- Name: yabi_user_toolsets_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabi_user_toolsets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabi_user_toolsets_id_seq OWNER TO yabiapp;

--
-- Name: yabi_user_toolsets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabi_user_toolsets_id_seq OWNED BY yabi_user_toolsets.id;


--
-- Name: yabi_user_toolsets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabi_user_toolsets_id_seq', 1, true);


--
-- Name: yabiengine_job; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_job (
    id integer NOT NULL,
    workflow_id integer NOT NULL,
    "order" integer NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    cpus character varying(64),
    walltime character varying(64),
    status character varying(64) NOT NULL,
    command text NOT NULL,
    batch_files text,
    exec_backend character varying(256),
    fs_backend character varying(256),
    parameter_files text,
    stageout character varying(1000),
    job_type character varying(40),
    module text,
    queue character varying(50),
    max_memory integer,
    other_files text,
    preferred_stagein_method character varying(5) DEFAULT 'copy'::character varying NOT NULL,
    preferred_stageout_method character varying(5) DEFAULT 'copy'::character varying NOT NULL,
    command_template text,
    CONSTRAINT yabiengine_job_max_memory_check CHECK ((max_memory >= 0)),
    CONSTRAINT yabiengine_job_order_check CHECK (("order" >= 0))
);


ALTER TABLE public.yabiengine_job OWNER TO yabiapp;

--
-- Name: yabiengine_job_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_job_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_job_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_job_id_seq OWNED BY yabiengine_job.id;


--
-- Name: yabiengine_job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_job_id_seq', 1, true);


--
-- Name: yabiengine_queuedworkflow; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_queuedworkflow (
    id integer NOT NULL,
    workflow_id integer NOT NULL,
    created_on timestamp with time zone NOT NULL
);


ALTER TABLE public.yabiengine_queuedworkflow OWNER TO yabiapp;

--
-- Name: yabiengine_queuedworkflow_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_queuedworkflow_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_queuedworkflow_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_queuedworkflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_queuedworkflow_id_seq OWNED BY yabiengine_queuedworkflow.id;


--
-- Name: yabiengine_queuedworkflow_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_queuedworkflow_id_seq', 1, false);


--
-- Name: yabiengine_stagein; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_stagein (
    id integer NOT NULL,
    "order" integer NOT NULL,
    task_id integer NOT NULL,
    src character varying(256),
    dst character varying(256),
    method character varying(5) DEFAULT 'copy'::character varying NOT NULL
);


ALTER TABLE public.yabiengine_stagein OWNER TO yabiapp;

--
-- Name: yabiengine_stagein_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_stagein_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_stagein_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_stagein_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_stagein_id_seq OWNED BY yabiengine_stagein.id;


--
-- Name: yabiengine_stagein_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_stagein_id_seq', 1, true);


--
-- Name: yabiengine_syslog; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_syslog (
    id integer NOT NULL,
    message text NOT NULL,
    table_name character varying(64),
    table_id integer,
    created_on timestamp with time zone
);


ALTER TABLE public.yabiengine_syslog OWNER TO yabiapp;

--
-- Name: yabiengine_syslog_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_syslog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_syslog_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_syslog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_syslog_id_seq OWNED BY yabiengine_syslog.id;


--
-- Name: yabiengine_syslog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_syslog_id_seq', 1, true);


--
-- Name: yabiengine_tag; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_tag (
    id integer NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.yabiengine_tag OWNER TO yabiapp;

--
-- Name: yabiengine_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_tag_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_tag_id_seq OWNED BY yabiengine_tag.id;


--
-- Name: yabiengine_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_tag_id_seq', 1, true);


--
-- Name: yabiengine_task; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_task (
    id integer NOT NULL,
    job_id integer NOT NULL,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    job_identifier text NOT NULL,
    command text NOT NULL,
    exec_backend character varying(256) NOT NULL,
    fs_backend character varying(256) NOT NULL,
    error_msg character varying(1000),
    status character varying(64) NOT NULL,
    working_dir character varying(256),
    name character varying(256) DEFAULT ''::character varying,
    expected_port integer,
    expected_ip character varying(256),
    remote_id character varying(256),
    remote_info character varying(2048),
    percent_complete double precision
);


ALTER TABLE public.yabiengine_task OWNER TO yabiapp;

--
-- Name: yabiengine_task_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_task_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_task_id_seq OWNED BY yabiengine_task.id;


--
-- Name: yabiengine_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_task_id_seq', 1, true);


--
-- Name: yabiengine_workflow; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_workflow (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    user_id integer NOT NULL,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    log_file_path character varying(1000),
    last_modified_on timestamp with time zone,
    created_on timestamp with time zone NOT NULL,
    status text NOT NULL,
    stageout character varying(1000),
    json text,
    original_json text
);


ALTER TABLE public.yabiengine_workflow OWNER TO yabiapp;

--
-- Name: yabiengine_workflow_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_workflow_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_workflow_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_workflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_workflow_id_seq OWNED BY yabiengine_workflow.id;


--
-- Name: yabiengine_workflow_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_workflow_id_seq', 1, true);


--
-- Name: yabiengine_workflowtag; Type: TABLE; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE TABLE yabiengine_workflowtag (
    id integer NOT NULL,
    workflow_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.yabiengine_workflowtag OWNER TO yabiapp;

--
-- Name: yabiengine_workflowtag_id_seq; Type: SEQUENCE; Schema: public; Owner: yabiapp
--

CREATE SEQUENCE yabiengine_workflowtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabiengine_workflowtag_id_seq OWNER TO yabiapp;

--
-- Name: yabiengine_workflowtag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabiapp
--

ALTER SEQUENCE yabiengine_workflowtag_id_seq OWNED BY yabiengine_workflowtag.id;


--
-- Name: yabiengine_workflowtag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabiapp
--

SELECT pg_catalog.setval('yabiengine_workflowtag_id_seq', 1, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE django_evolution ALTER COLUMN id SET DEFAULT nextval('django_evolution_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE django_project_version ALTER COLUMN id SET DEFAULT nextval('django_project_version_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE ghettoq_message ALTER COLUMN id SET DEFAULT nextval('ghettoq_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE ghettoq_queue ALTER COLUMN id SET DEFAULT nextval('ghettoq_queue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_backend ALTER COLUMN id SET DEFAULT nextval('yabi_backend_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_backendcredential ALTER COLUMN id SET DEFAULT nextval('yabi_backendcredential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_credential ALTER COLUMN id SET DEFAULT nextval('yabi_credential_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_fileextension ALTER COLUMN id SET DEFAULT nextval('yabi_fileextension_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_filetype ALTER COLUMN id SET DEFAULT nextval('yabi_filetype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_filetype_extensions ALTER COLUMN id SET DEFAULT nextval('yabi_filetype_extensions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_parameterfilter ALTER COLUMN id SET DEFAULT nextval('yabi_parameterfilter_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_parameterswitchuse ALTER COLUMN id SET DEFAULT nextval('yabi_parameterswitchuse_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_tool ALTER COLUMN id SET DEFAULT nextval('yabi_tool_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolgroup ALTER COLUMN id SET DEFAULT nextval('yabi_toolgroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolgrouping ALTER COLUMN id SET DEFAULT nextval('yabi_toolgrouping_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_tooloutputextension ALTER COLUMN id SET DEFAULT nextval('yabi_tooloutputextension_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolparameter ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolparameter_accepted_filetypes ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_accepted_filetypes_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolparameter_input_extensions ALTER COLUMN id SET DEFAULT nextval('yabi_toolparameter_input_extensions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_toolset ALTER COLUMN id SET DEFAULT nextval('yabi_toolset_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_user ALTER COLUMN id SET DEFAULT nextval('yabi_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabi_user_toolsets ALTER COLUMN id SET DEFAULT nextval('yabi_user_toolsets_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_job ALTER COLUMN id SET DEFAULT nextval('yabiengine_job_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_queuedworkflow ALTER COLUMN id SET DEFAULT nextval('yabiengine_queuedworkflow_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_stagein ALTER COLUMN id SET DEFAULT nextval('yabiengine_stagein_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_syslog ALTER COLUMN id SET DEFAULT nextval('yabiengine_syslog_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_tag ALTER COLUMN id SET DEFAULT nextval('yabiengine_tag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_task ALTER COLUMN id SET DEFAULT nextval('yabiengine_task_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_workflow ALTER COLUMN id SET DEFAULT nextval('yabiengine_workflow_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabiapp
--

ALTER TABLE yabiengine_workflowtag ALTER COLUMN id SET DEFAULT nextval('yabiengine_workflowtag_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_group (id, name) FROM stdin;
1	baseuser
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_message; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_message (id, user_id, message) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
7	Can add group	3	add_group
13	Can add message	5	add_message
4	Can add permission	2	add_permission
10	Can add user	4	add_user
8	Can change group	3	change_group
14	Can change message	5	change_message
5	Can change permission	2	change_permission
11	Can change user	4	change_user
9	Can delete group	3	delete_group
15	Can delete message	5	delete_message
6	Can delete permission	2	delete_permission
12	Can delete user	4	delete_user
16	Can add content type	6	add_contenttype
17	Can change content type	6	change_contenttype
18	Can delete content type	6	delete_contenttype
28	Can add evolution	10	add_evolution
25	Can add version	9	add_version
29	Can change evolution	10	change_evolution
26	Can change version	9	change_version
30	Can delete evolution	10	delete_evolution
27	Can delete version	9	delete_version
19	Can add session	7	add_session
20	Can change session	7	change_session
21	Can delete session	7	delete_session
22	Can add site	8	add_site
23	Can change site	8	change_site
24	Can delete site	8	delete_site
85	Can add job	29	add_job
94	Can add queued workflow	32	add_queuedworkflow
91	Can add stage in	31	add_stagein
97	Can add sys log	33	add_syslog
100	Can add task	34	add_task
82	Can add workflow	28	add_workflow
86	Can change job	29	change_job
95	Can change queued workflow	32	change_queuedworkflow
92	Can change stage in	31	change_stagein
98	Can change sys log	33	change_syslog
101	Can change task	34	change_task
83	Can change workflow	28	change_workflow
87	Can delete job	29	delete_job
96	Can delete queued workflow	32	delete_queuedworkflow
93	Can delete stage in	31	delete_stagein
99	Can delete sys log	33	delete_syslog
102	Can delete task	34	delete_task
84	Can delete workflow	28	delete_workflow
79	Can add backend	27	add_backend
103	Can add backend credential	35	add_backendcredential
76	Can add credential	26	add_credential
31	Can add file extension	11	add_fileextension
34	Can add file type	12	add_filetype
46	Can add parameter filter	16	add_parameterfilter
43	Can add parameter switch use	15	add_parameterswitchuse
40	Can add tool	14	add_tool
64	Can add tool group	22	add_toolgroup
67	Can add tool grouping	23	add_toolgrouping
61	Can add tool output extension	21	add_tooloutputextension
49	Can add tool parameter	17	add_toolparameter
58	Can add tool rsl argument order	20	add_toolrslargumentorder
55	Can add tool rsl extension module	19	add_toolrslextensionmodule
52	Can add tool rsl info	18	add_toolrslinfo
70	Can add tool set	24	add_toolset
73	Can add user	25	add_user
80	Can change backend	27	change_backend
104	Can change backend credential	35	change_backendcredential
77	Can change credential	26	change_credential
32	Can change file extension	11	change_fileextension
35	Can change file type	12	change_filetype
47	Can change parameter filter	16	change_parameterfilter
44	Can change parameter switch use	15	change_parameterswitchuse
41	Can change tool	14	change_tool
65	Can change tool group	22	change_toolgroup
68	Can change tool grouping	23	change_toolgrouping
62	Can change tool output extension	21	change_tooloutputextension
50	Can change tool parameter	17	change_toolparameter
59	Can change tool rsl argument order	20	change_toolrslargumentorder
56	Can change tool rsl extension module	19	change_toolrslextensionmodule
53	Can change tool rsl info	18	change_toolrslinfo
71	Can change tool set	24	change_toolset
74	Can change user	25	change_user
81	Can delete backend	27	delete_backend
105	Can delete backend credential	35	delete_backendcredential
78	Can delete credential	26	delete_credential
33	Can delete file extension	11	delete_fileextension
36	Can delete file type	12	delete_filetype
48	Can delete parameter filter	16	delete_parameterfilter
45	Can delete parameter switch use	15	delete_parameterswitchuse
42	Can delete tool	14	delete_tool
66	Can delete tool group	22	delete_toolgroup
69	Can delete tool grouping	23	delete_toolgrouping
63	Can delete tool output extension	21	delete_tooloutputextension
51	Can delete tool parameter	17	delete_toolparameter
60	Can delete tool rsl argument order	20	delete_toolrslargumentorder
57	Can delete tool rsl extension module	19	delete_toolrslextensionmodule
54	Can delete tool rsl info	18	delete_toolrslinfo
72	Can delete tool set	24	delete_toolset
75	Can delete user	25	delete_user
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) FROM stdin;
1	django			techs@ccg.murdoch.edu.au	sha1$33d5e$decb15515dfb367b5122eb3af8ed66f19fa7f07a	t	t	t	2009-06-18 16:23:33+08	2009-06-18 15:49:33+08
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: celery_taskmeta; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY celery_taskmeta (id, task_id, status, result, date_done, traceback) FROM stdin;
\.


--
-- Data for Name: celery_tasksetmeta; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY celery_tasksetmeta (id, taskset_id, result, date_done) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_admin_log (id, action_time, user_id, content_type_id, object_id, object_repr, action_flag, change_message) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	log entry	admin	logentry
2	permission	auth	permission
3	group	auth	group
4	user	auth	user
5	message	auth	message
6	content type	contenttypes	contenttype
7	session	sessions	session
8	site	sites	site
9	version	django_evolution	version
10	evolution	django_evolution	evolution
11	file extension	yabmin	fileextension
12	file type	yabmin	filetype
14	tool	yabmin	tool
15	parameter switch use	yabmin	parameterswitchuse
16	parameter filter	yabmin	parameterfilter
17	tool parameter	yabmin	toolparameter
18	tool rsl info	yabmin	toolrslinfo
19	tool rsl extension module	yabmin	toolrslextensionmodule
20	tool rsl argument order	yabmin	toolrslargumentorder
21	tool output extension	yabmin	tooloutputextension
22	tool group	yabmin	toolgroup
23	tool grouping	yabmin	toolgrouping
24	tool set	yabmin	toolset
25	user	yabmin	user
26	credential	yabmin	credential
27	backend	yabmin	backend
28	workflow	yabiengine	workflow
29	job	yabiengine	job
31	stage in	yabiengine	stagein
32	queued workflow	yabiengine	queuedworkflow
33	sys log	yabiengine	syslog
34	task	yabiengine	task
35	backend credential	yabmin	backendcredential
36	user	yabi	user
37	credential	yabi	credential
38	tool output extension	yabi	tooloutputextension
39	tool parameter	yabi	toolparameter
40	tool	yabi	tool
41	backend	yabi	backend
42	backend credential	yabi	backendcredential
43	tool set	yabi	toolset
44	tool grouping	yabi	toolgrouping
45	tool group	yabi	toolgroup
46	queue	ghettoq	queue
47	file type	yabi	filetype
48	file extension	yabi	fileextension
49	parameter switch use	yabi	parameterswitchuse
\.


--
-- Data for Name: django_evolution; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_evolution (id, version_id, app_label, label) FROM stdin;
\.


--
-- Data for Name: django_project_version; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_project_version (id, signature, "when") FROM stdin;
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY django_site (id, domain, name) FROM stdin;
1	localhost.localdomain:8000	localhost.localdomain:8000
\.


--
-- Data for Name: ghettoq_message; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY ghettoq_message (id, visible, sent_at, payload, queue_id) FROM stdin;
\.


--
-- Data for Name: ghettoq_queue; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY ghettoq_queue (id, name) FROM stdin;
1	yabiadmin-live
\.


--
-- Data for Name: yabi_backend; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_backend (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name, description, hostname, port, path, scheme, max_connections, lcopy_supported, link_supported) FROM stdin;
\.


--
-- Data for Name: yabi_backendcredential; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_backendcredential (id, last_modified_by_id, last_modified_on, created_by_id, created_on, backend_id, credential_id, homedir, visible, default_stageout) FROM stdin;
\.


--
-- Data for Name: yabi_credential; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_credential (id, last_modified_by_id, last_modified_on, created_by_id, created_on, description, username, password, cert, key, user_id, expires_on, encrypted, encrypt_on_login) FROM stdin;
\.


--
-- Data for Name: yabi_fileextension; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_fileextension (id, last_modified_by_id, last_modified_on, created_by_id, created_on, extension) FROM stdin;
1	\N	2009-06-26 12:44:17.327744+08	\N	2009-06-26 12:44:17.327773+08	t2m
2	\N	2009-06-26 12:44:17.389955+08	\N	2009-06-26 12:44:17.389984+08	zip
3	\N	2009-06-26 12:44:17.479281+08	\N	2009-06-26 12:44:17.479308+08	afg
4	\N	2009-06-26 12:44:17.511638+08	\N	2009-06-26 12:44:17.511665+08	frg
5	\N	2009-06-26 12:44:17.529002+08	\N	2009-06-26 12:44:17.529029+08	list
6	\N	2009-06-26 12:44:17.536991+08	\N	2009-06-26 12:44:17.537016+08	gz
7	\N	2009-06-26 12:44:17.602448+08	\N	2009-06-26 12:44:17.602473+08	*
8	\N	2009-06-26 12:44:17.619817+08	\N	2009-06-26 12:44:17.619844+08	fa
9	\N	2009-06-26 12:44:17.627693+08	\N	2009-06-26 12:44:17.627718+08	fna
10	\N	2009-06-26 12:44:17.635309+08	\N	2009-06-26 12:44:17.635333+08	faa
11	\N	2009-06-26 12:44:17.731008+08	\N	2009-06-26 12:44:17.731034+08	bls
12	\N	2009-06-26 12:44:17.766491+08	\N	2009-06-26 12:44:17.766518+08	gb
13	\N	2009-06-26 12:44:18.127897+08	\N	2009-06-26 12:44:18.127922+08	html
14	\N	2009-06-26 12:44:18.163332+08	\N	2009-06-26 12:44:18.163363+08	seq
15	\N	2009-06-26 12:44:18.555328+08	\N	2009-06-26 12:44:18.555366+08	xml
16	\N	2009-06-26 12:44:18.787113+08	\N	2009-06-26 12:44:18.78714+08	psl
18	\N	2009-06-26 12:44:19.245153+08	\N	2009-06-26 12:44:19.24518+08	bfa
19	\N	2009-06-26 12:44:19.25291+08	\N	2009-06-26 12:44:19.252936+08	map
20	\N	2009-06-26 12:44:19.352347+08	\N	2009-06-26 12:44:19.352373+08	cns
21	\N	2009-06-26 12:44:20.402509+08	\N	2009-06-26 12:44:20.402536+08	aln
22	\N	2009-06-26 12:44:20.407364+08	\N	2009-06-26 12:44:20.40739+08	dnd
23	\N	2009-06-26 12:44:20.459546+08	\N	2009-06-26 12:44:20.459577+08	snp
24	\N	2009-06-26 12:44:20.564372+08	\N	2009-06-26 12:44:20.564398+08	fsa
25	\N	2009-06-26 12:44:20.63487+08	\N	2009-06-26 12:44:20.634897+08	fq
26	\N	2009-06-26 12:44:20.646175+08	\N	2009-06-26 12:44:20.646202+08	fastq
27	\N	2009-06-26 12:44:20.684341+08	\N	2009-06-26 12:44:20.684366+08	bfq
28	\N	2009-06-26 12:44:20.715563+08	\N	2009-06-26 12:44:20.71559+08	fasta
29	\N	2009-06-26 12:44:20.767794+08	\N	2009-06-26 12:44:20.767818+08	summary
30	\N	2009-06-26 12:44:20.772444+08	\N	2009-06-26 12:44:20.772472+08	vectorcuts
31	\N	2009-06-26 12:44:20.794031+08	\N	2009-06-26 12:44:20.794059+08	qul
32	\N	2009-06-26 12:44:20.839385+08	\N	2009-06-26 12:44:20.839413+08	qual
33	\N	2009-06-26 12:44:21.076146+08	\N	2009-06-26 12:44:21.076173+08	longorfs
34	\N	2009-06-26 12:44:21.081029+08	\N	2009-06-26 12:44:21.081056+08	icm
35	\N	2009-06-26 12:44:21.08586+08	\N	2009-06-26 12:44:21.085886+08	detail
36	\N	2009-06-26 12:44:21.090485+08	\N	2009-06-26 12:44:21.09051+08	predict
37	\N	2009-06-26 12:44:21.126562+08	\N	2009-06-26 12:44:21.126595+08	gff
38	\N	2009-06-26 12:44:21.134065+08	\N	2009-06-26 12:44:21.134094+08	masked
39	\N	2009-06-26 12:44:21.24053+08	\N	2009-06-26 12:44:21.240556+08	indelpe
40	\N	2009-06-26 12:44:21.390817+08	\N	2009-06-26 12:44:21.390843+08	ebixml
41	\N	2009-06-26 12:44:21.401829+08	\N	2009-06-26 12:44:21.401854+08	raw
42	\N	2009-06-26 12:44:21.967023+08	\N	2009-06-26 12:44:21.967048+08	project
43	\N	2009-06-26 12:44:21.982857+08	\N	2009-06-26 12:44:21.982883+08	nov
44	\N	2009-06-26 12:44:22.067943+08	\N	2009-06-26 12:44:22.068015+08	prb
45	\N	2009-06-26 12:44:22.390883+08	\N	2009-06-26 12:44:22.390911+08	tar
46	\N	2009-06-26 12:44:23.018642+08	\N	2009-06-26 12:44:23.018667+08	psa
47	\N	2009-06-26 12:44:23.02329+08	\N	2009-06-26 12:44:23.023314+08	msa
48	\N	2009-06-26 12:44:23.03097+08	\N	2009-06-26 12:44:23.030995+08	pff
49	\N	2009-06-26 12:44:23.035384+08	\N	2009-06-26 12:44:23.035438+08	epff
50	\N	2009-06-26 12:44:23.425166+08	\N	2009-06-26 12:44:23.425192+08	cat
51	\N	2009-06-26 12:44:23.430053+08	\N	2009-06-26 12:44:23.430079+08	log
52	\N	2009-06-26 12:44:23.437776+08	\N	2009-06-26 12:44:23.437802+08	out
53	\N	2009-06-26 12:44:23.442273+08	\N	2009-06-26 12:44:23.442297+08	tbl
54	\N	2009-06-26 12:44:23.562205+08	\N	2009-06-26 12:44:23.562231+08	hmmreport
55	\N	2009-06-26 12:44:23.779458+08	\N	2009-06-26 12:44:23.779488+08	sff
56	\N	2009-06-26 12:44:25.531094+08	\N	2009-06-26 12:44:25.53112+08	found
57	\N	2009-06-26 12:44:25.535715+08	\N	2009-06-26 12:44:25.535741+08	idx
58	\N	2009-06-26 12:44:26.165244+08	\N	2009-06-26 12:44:26.165272+08	vector
59	\N	2009-06-26 12:44:26.475666+08	\N	2009-06-26 12:44:26.475698+08	embl
60	\N	2009-06-26 12:44:27.325965+08	\N	2009-06-26 12:44:27.325997+08	genbank
61	\N	2009-06-26 12:44:27.467775+08	\N	2009-06-26 12:44:27.467907+08	genscan
62	\N	2009-06-26 12:44:27.865538+08	\N	2009-06-26 12:44:27.865564+08	train
63	\N	2009-06-26 12:44:29.445647+08	\N	2009-06-26 12:44:29.445674+08	new
65	\N	2009-06-26 12:44:29.497474+08	\N	2009-06-26 12:44:29.497509+08	hssp
66	\N	2009-06-26 12:44:29.505232+08	\N	2009-06-26 12:44:29.505257+08	mips
67	\N	2009-06-26 12:44:29.513105+08	\N	2009-06-26 12:44:29.513131+08	msf
68	\N	2009-06-26 12:44:29.520719+08	\N	2009-06-26 12:44:29.520745+08	multas
69	\N	2009-06-26 12:44:29.527668+08	\N	2009-06-26 12:44:29.527695+08	pir
70	\N	2009-06-26 12:44:30.386601+08	\N	2009-06-26 12:44:30.386628+08	htm
71	\N	2009-06-26 12:44:30.742983+08	\N	2009-06-26 12:44:30.743014+08	png
72	\N	2009-06-26 12:44:30.74791+08	\N	2009-06-26 12:44:30.747937+08	ps
73	\N	2009-06-26 12:44:31.212282+08	\N	2009-06-26 12:44:31.212316+08	wiff
74	\N	2009-10-26 11:46:24.332343+08	\N	2009-10-26 11:46:24.332377+08	geo
75	\N	2009-10-26 11:48:30.016374+08	\N	2009-10-26 11:48:30.016413+08	hdf
76	\N	2009-10-26 12:05:10.825305+08	\N	2009-10-26 12:05:10.825343+08	1km
77	\N	2009-10-27 09:11:35.988424+08	\N	2009-10-27 09:11:35.988515+08	index
78	\N	2009-10-27 09:55:05.35726+08	\N	2009-10-27 09:55:05.357299+08	bar
79	\N	2009-10-27 13:49:15.84221+08	\N	2009-10-27 13:49:15.842258+08	cod
80	\N	2009-10-27 14:01:45.623897+08	\N	2009-10-27 14:01:45.62393+08	peak
81	\N	2009-10-27 14:06:33.298274+08	\N	2009-10-27 14:06:33.298321+08	fdr
82	\N	2010-09-14 11:28:10.872618+08	\N	2010-09-14 11:28:10.872653+08	jpg
83	\N	2010-09-27 16:58:19.527366+08	\N	2010-09-27 16:58:19.52741+08	L1B_LAC
84	\N	2010-09-27 16:58:32.150087+08	\N	2010-09-27 16:58:32.150146+08	GEO
85	\N	2010-09-28 09:08:27.206709+08	\N	2010-09-28 09:08:27.206752+08	L1B_QKM
86	\N	2010-09-28 09:08:34.484464+08	\N	2010-09-28 09:08:34.484507+08	L1B_HKM
87	\N	2010-11-16 14:42:06.995923+08	\N	2010-11-16 14:42:06.995961+08	mgf
88	\N	2010-11-16 14:43:45.064226+08	\N	2010-11-16 14:43:45.064262+08	dat
89	\N	2010-11-16 15:12:45.287421+08	\N	2010-11-16 15:12:45.287456+08	xsl
90	\N	2010-11-30 14:26:47.849226+08	\N	2010-11-30 14:26:47.849283+08	eprimer3
91	\N	2010-12-01 15:27:47.748594+08	\N	2010-12-01 15:27:47.748632+08	genemark
92	\N	2010-12-16 16:18:45.354462+08	\N	2010-12-16 16:18:45.354515+08	screen
93	\N	2011-02-02 15:26:25.206297+08	\N	2011-02-02 15:26:25.206358+08	cvs
94	\N	2011-03-07 12:21:26.306205+08	\N	2011-03-07 12:21:26.306262+08	R
95	\N	2011-04-05 15:25:44.049937+08	\N	2011-04-05 15:25:44.050002+08	csv
96	\N	2011-04-27 14:55:33.575252+08	\N	2011-04-27 14:55:33.57531+08	svg
97	\N	2011-04-27 15:07:03.70897+08	\N	2011-04-27 15:07:03.709033+08	ffn
98	\N	2011-04-27 15:07:11.294254+08	\N	2011-04-27 15:07:11.294312+08	frn
99	\N	2011-04-27 15:53:57.007985+08	\N	2011-04-27 15:53:57.008021+08	clustalw
17	\N	2011-04-28 16:30:16.786013+08	\N	2009-06-26 12:44:19.224189+08	txt
100	\N	2011-05-03 16:42:30.610391+08	\N	2011-05-03 16:42:30.610437+08	pepinfo
101	\N	2011-05-03 16:46:36.079133+08	\N	2011-05-03 16:46:36.07917+08	sirna
102	\N	2011-05-06 16:44:54.307174+08	\N	2011-05-06 16:44:54.307246+08	pep
\.


--
-- Data for Name: yabi_filetype; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_filetype (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name, description) FROM stdin;
1	\N	2009-06-26 12:44:17.332881+08	\N	2009-06-26 12:44:17.33291+08	t2m (GEN)	\N
2	\N	2009-06-26 12:44:17.482754+08	\N	2009-06-26 12:44:17.482785+08	afg (GEN)	\N
3	\N	2009-06-26 12:44:17.532605+08	\N	2009-06-26 12:44:17.532631+08	list (GEN)	\N
4	\N	2009-06-26 12:44:17.540662+08	\N	2009-06-26 12:44:17.540689+08	gz (GEN)	\N
5	\N	2009-06-26 12:44:17.623524+08	\N	2009-06-26 12:44:17.623551+08	fa (GEN)	\N
6	\N	2009-06-26 12:44:17.631082+08	\N	2009-06-26 12:44:17.631108+08	fna (GEN)	\N
7	\N	2009-06-26 12:44:17.638868+08	\N	2009-06-26 12:44:17.6389+08	faa (GEN)	\N
8	\N	2009-06-26 12:44:17.773162+08	\N	2009-06-26 12:44:17.774113+08	gb (GEN)	\N
9	\N	2009-06-26 12:44:18.113099+08	\N	2009-06-26 12:44:18.113126+08	bls (GEN)	\N
10	\N	2009-06-26 12:44:18.166853+08	\N	2009-06-26 12:44:18.16688+08	seq (GEN)	\N
11	\N	2009-06-26 12:44:19.24875+08	\N	2009-06-26 12:44:19.248777+08	bfa (GEN)	\N
12	\N	2009-06-26 12:44:19.256238+08	\N	2009-06-26 12:44:19.256264+08	map (GEN)	\N
13	\N	2009-06-26 12:44:20.430338+08	\N	2009-06-26 12:44:20.430366+08	cns (GEN)	\N
14	\N	2009-06-26 12:44:20.642112+08	\N	2009-06-26 12:44:20.642145+08	fq (GEN)	\N
15	\N	2009-06-26 12:44:20.649451+08	\N	2009-06-26 12:44:20.649476+08	fastq (GEN)	\N
17	\N	2009-06-26 12:44:20.797384+08	\N	2009-06-26 12:44:20.797411+08	qul (GEN)	\N
18	\N	2009-06-26 12:44:20.803631+08	\N	2009-06-26 12:44:20.803657+08	vectorcuts (GEN)	\N
19	\N	2009-06-26 12:44:20.842979+08	\N	2009-06-26 12:44:20.843006+08	qual (GEN)	\N
20	\N	2009-06-26 12:44:21.129918+08	\N	2009-06-26 12:44:21.129947+08	gff (GEN)	\N
21	\N	2009-06-26 12:44:21.137807+08	\N	2009-06-26 12:44:21.137842+08	masked (GEN)	\N
22	\N	2009-06-26 12:44:21.625776+08	\N	2009-06-26 12:44:21.625804+08	bfq (GEN)	\N
24	\N	2009-06-26 12:44:21.987883+08	\N	2009-06-26 12:44:21.987919+08	nov (GEN)	\N
25	\N	2009-06-26 12:44:22.071463+08	\N	2009-06-26 12:44:22.071502+08	prb (GEN)	\N
26	\N	2009-06-26 12:44:22.394356+08	\N	2009-06-26 12:44:22.394382+08	tar (GEN)	\N
27	\N	2009-06-26 12:44:23.483279+08	\N	2009-06-26 12:44:23.483308+08	fsa (GEN)	\N
28	\N	2009-06-26 12:44:23.782685+08	\N	2009-06-26 12:44:23.78271+08	sff (GEN)	\N
29	\N	2009-06-26 12:44:23.789709+08	\N	2009-06-26 12:44:23.789751+08	project (GEN)	\N
30	\N	2009-06-26 12:44:24.031302+08	\N	2009-06-26 12:44:24.031328+08	frg (GEN)	\N
31	\N	2009-06-26 12:44:26.101271+08	\N	2009-06-26 12:44:26.101299+08	aln (GEN)	\N
32	\N	2009-06-26 12:44:26.169052+08	\N	2009-06-26 12:44:26.169079+08	vector (GEN)	\N
33	\N	2009-06-26 12:44:26.39991+08	\N	2009-06-26 12:44:26.399946+08	* (GEN)	\N
34	\N	2009-06-26 12:44:26.479734+08	\N	2009-06-26 12:44:26.479763+08	embl (GEN)	\N
35	\N	2009-06-26 12:44:27.329478+08	\N	2009-06-26 12:44:27.329507+08	genbank (GEN)	\N
36	\N	2009-06-26 12:44:27.377163+08	\N	2009-06-26 12:44:27.37719+08	xml (GEN)	\N
38	\N	2009-06-26 12:44:29.500986+08	\N	2009-06-26 12:44:29.501013+08	hssp (GEN)	\N
39	\N	2009-06-26 12:44:29.508703+08	\N	2009-06-26 12:44:29.508731+08	mips (GEN)	\N
40	\N	2009-06-26 12:44:29.516576+08	\N	2009-06-26 12:44:29.516602+08	msf (GEN)	\N
41	\N	2009-06-26 12:44:29.524177+08	\N	2009-06-26 12:44:29.524207+08	multas (GEN)	\N
42	\N	2009-06-26 12:44:29.531072+08	\N	2009-06-26 12:44:29.531096+08	pir (GEN)	\N
43	\N	2009-06-26 12:44:30.347117+08	\N	2009-06-26 12:44:30.347145+08	new (GEN)	\N
44	\N	2009-06-26 12:44:30.382498+08	\N	2009-06-26 12:44:30.382524+08	html (GEN)	\N
45	\N	2009-06-26 12:44:30.390092+08	\N	2009-06-26 12:44:30.39012+08	htm (GEN)	\N
46	\N	2009-06-26 12:44:31.215771+08	\N	2009-06-26 12:44:31.215797+08	wiff (GEN)	\N
47	\N	2009-06-26 12:44:32.80548+08	\N	2009-06-26 12:44:32.805507+08	raw (GEN)	\N
48	\N	2009-10-26 11:48:55.782144+08	\N	2009-10-26 11:48:55.782179+08	hdf	
60	\N	2010-11-16 16:46:44.292272+08	\N	2010-11-16 16:46:44.292324+08	xsl	
61	\N	2010-12-16 16:18:48.203472+08	\N	2010-12-16 16:18:48.203524+08	screen	
51	\N	2009-10-27 09:41:57.986253+08	\N	2009-10-27 09:41:57.986302+08	index	
52	\N	2009-10-27 13:50:44.42767+08	\N	2009-10-27 13:37:31.821061+08	bar	
53	\N	2009-10-27 13:52:07.388923+08	\N	2009-10-27 13:52:07.388956+08	cod	cis genome peak detection https://ccg.murdoch.edu.au/trac/yabi/ticket/436
54	\N	2009-10-27 14:06:55.840657+08	\N	2009-10-27 14:06:55.840694+08	fdr	
55	\N	2010-09-14 11:28:16.48589+08	\N	2010-09-14 11:28:16.485924+08	jpeg	
62	\N	2011-01-31 14:22:58.624709+08	\N	2011-01-31 14:22:58.624768+08	geo	
63	\N	2011-03-07 12:21:27.928876+08	\N	2011-03-07 12:21:27.928937+08	R	
64	\N	2011-04-04 15:00:10.271715+08	\N	2011-04-04 15:00:10.271774+08	genscan	
65	\N	2011-04-05 15:25:45.768863+08	\N	2011-04-05 15:25:45.768922+08	csv	
16	\N	2011-04-27 15:07:12.988851+08	\N	2009-06-26 12:44:20.719199+08	fasta	
23	\N	2011-04-28 16:30:03.801752+08	\N	2009-06-26 12:44:21.635938+08	txt (GEN)	
37	\N	2011-05-02 15:18:22.985025+08	\N	2009-06-26 12:44:29.478001+08	clustalw	
58	\N	2010-09-28 09:11:30.314837+08	\N	2010-09-28 09:10:35.175856+08	250m resolution L1B file	
57	\N	2010-09-28 09:11:44.666758+08	\N	2010-09-28 09:10:16.56612+08	500m resolution L1B file	
56	\N	2010-09-28 09:12:09.886076+08	\N	2010-09-28 09:10:05.509427+08	1km resolution L1B file	
59	\N	2010-09-28 09:21:12.168998+08	\N	2010-09-28 09:11:13.832482+08	GEO file	
66	\N	2011-05-06 16:44:55.902411+08	\N	2011-05-06 16:44:55.902487+08	pep	
\.


--
-- Data for Name: yabi_filetype_extensions; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_filetype_extensions (id, filetype_id, fileextension_id) FROM stdin;
1	1	1
2	2	3
3	3	5
4	4	6
5	5	8
6	6	9
7	7	10
8	8	12
9	9	11
10	10	14
11	11	18
12	12	19
13	13	20
14	14	25
15	15	26
17	17	31
18	18	30
19	19	32
20	20	37
21	21	38
22	22	27
24	24	43
25	25	44
26	26	45
27	27	24
28	28	55
29	29	42
30	30	4
31	31	21
32	32	58
33	33	7
34	34	59
35	35	60
36	36	15
38	38	65
39	39	66
40	40	67
41	41	68
42	42	69
43	43	63
44	44	13
45	45	70
46	46	73
47	47	41
100	48	75
144	60	89
106	51	77
108	52	78
110	53	79
112	54	81
114	55	82
146	61	92
149	62	74
150	62	84
152	63	94
154	64	61
156	65	95
163	16	97
164	16	98
165	16	8
166	16	9
136	58	85
167	16	10
138	57	86
168	16	28
140	56	83
142	59	84
170	23	17
172	37	99
174	66	102
\.


--
-- Data for Name: yabi_parameterfilter; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_parameterfilter (id, last_modified_by_id, last_modified_on, created_by_id, created_on, display_text, value, description) FROM stdin;
1	\N	2009-03-31 16:43:22+08	\N	2009-03-31 16:43:22+08	prepend string	prependString	Prepends the string in filterValue to the parameter value.
2	\N	2009-03-31 16:43:22+08	\N	2009-03-31 16:43:22+08	append string	appendString	Appends the string in filterValue to the parameter value.
3	\N	2009-03-31 16:43:22+08	\N	2009-03-31 16:43:22+08	prepend root directory	prependRootDir	Prepends the root directory to the parameter value.
4	\N	2009-03-31 16:43:22+08	\N	2009-03-31 16:43:22+08	remove path	removePath	Removes the path component from the parameter value.
\.


--
-- Data for Name: yabi_parameterswitchuse; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_parameterswitchuse (id, last_modified_by_id, last_modified_on, created_by_id, created_on, display_text, formatstring, description) FROM stdin;
7	\N	2010-04-21 11:26:24.24346+08	\N	2010-04-21 11:26:24.243486+08	combined with equals	%(switch)s=%(value)s	Both the switch and the value will be passed in the argument list. They will be separated joined with an equals(=) character with no spaces.
3	\N	2010-04-21 12:22:22.821777+08	\N	2009-03-31 16:42:10+08	both	%(switch)s %(value)s	Both the switch and the value will be passed in the argument list. They will be separated by a space.
4	\N	2010-04-21 12:23:49.39616+08	\N	2009-03-31 16:43:22+08	combined	%(switch)s%(value)s	Both the switch and the value will be passed in the argument list. They will be joined together with no space between them.
10	\N	2010-08-12 16:11:14.52882+08	\N	2010-08-12 16:11:14.528883+08	valueOnly	%(value)s	Only the value will be passed in the argument list (ie. the switch won't be used)
11	\N	2010-08-12 16:11:14.567704+08	\N	2010-08-12 16:11:14.567727+08	switchOnly	%(switch)s	Only the switch will be passed in the argument list.
12	\N	2010-12-02 14:29:01.147936+08	\N	2010-12-02 14:29:01.147971+08	redirect	>%(value)s	Use this to redirect the output of stdout into a file.
5	\N	2011-04-05 15:18:06.639043+08	\N	2009-03-31 16:44:23+08	nothing		The switch and the value won't be passed in the argument list.
\.


--
-- Data for Name: yabi_tool; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_tool (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name, display_name, path, description, enabled, backend_id, accepts_input, walltime, cpus, fs_backend_id, module, queue, job_type, max_memory, lcopy_supported, link_supported) FROM stdin;
\.


--
-- Data for Name: yabi_toolgroup; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolgroup (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name) FROM stdin;
\.


--
-- Data for Name: yabi_toolgrouping; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolgrouping (id, last_modified_by_id, last_modified_on, created_by_id, created_on, tool_id, tool_set_id, tool_group_id) FROM stdin;
\.


--
-- Data for Name: yabi_tooloutputextension; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_tooloutputextension (id, last_modified_by_id, last_modified_on, created_by_id, created_on, tool_id, file_extension_id, must_exist, must_be_larger_than) FROM stdin;
\.


--
-- Data for Name: yabi_toolparameter; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolparameter (id, last_modified_by_id, last_modified_on, created_by_id, created_on, tool_id, rank, mandatory, input_file, output_file, switch, switch_use_id, extension_param_id, possible_values, default_value, helptext, hidden, batch_param, batch_bundle_files, use_output_filename_id) FROM stdin;
\.


--
-- Data for Name: yabi_toolparameter_accepted_filetypes; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolparameter_accepted_filetypes (id, toolparameter_id, filetype_id) FROM stdin;
\.


--
-- Data for Name: yabi_toolparameter_input_extensions; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolparameter_input_extensions (id, toolparameter_id, fileextension_id) FROM stdin;
\.


--
-- Data for Name: yabi_toolset; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_toolset (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name) FROM stdin;
\.


--
-- Data for Name: yabi_user; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_user (id, last_modified_by_id, last_modified_on, created_by_id, created_on, name) FROM stdin;
\.


--
-- Data for Name: yabi_user_toolsets; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabi_user_toolsets (id, user_id, toolset_id) FROM stdin;
\.


--
-- Data for Name: yabiengine_job; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_job (id, workflow_id, "order", start_time, end_time, cpus, walltime, status, command, batch_files, exec_backend, fs_backend, parameter_files, stageout, job_type, module, queue, max_memory, other_files, preferred_stagein_method, preferred_stageout_method, command_template) FROM stdin;
\.


--
-- Data for Name: yabiengine_queuedworkflow; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_queuedworkflow (id, workflow_id, created_on) FROM stdin;
\.


--
-- Data for Name: yabiengine_stagein; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_stagein (id, "order", task_id, src, dst, method) FROM stdin;
\.


--
-- Data for Name: yabiengine_syslog; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_syslog (id, message, table_name, table_id, created_on) FROM stdin;
\.


--
-- Data for Name: yabiengine_tag; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_tag (id, value) FROM stdin;
\.


--
-- Data for Name: yabiengine_task; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_task (id, job_id, start_time, end_time, job_identifier, command, exec_backend, fs_backend, error_msg, status, working_dir, name, expected_port, expected_ip, remote_id, remote_info, percent_complete) FROM stdin;
\.


--
-- Data for Name: yabiengine_workflow; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_workflow (id, name, user_id, start_time, end_time, log_file_path, last_modified_on, created_on, status, stageout, json, original_json) FROM stdin;
\.


--
-- Data for Name: yabiengine_workflowtag; Type: TABLE DATA; Schema: public; Owner: yabiapp
--

COPY yabiengine_workflowtag (id, workflow_id, tag_id) FROM stdin;
\.


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: celery_taskmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_taskmeta_task_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id);


--
-- Name: celery_tasksetmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_tasksetmeta_taskset_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_evolution_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_evolution
    ADD CONSTRAINT django_evolution_pkey PRIMARY KEY (id);


--
-- Name: django_project_version_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_project_version
    ADD CONSTRAINT django_project_version_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: ghettoq_message_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY ghettoq_message
    ADD CONSTRAINT ghettoq_message_pkey PRIMARY KEY (id);


--
-- Name: ghettoq_queue_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY ghettoq_queue
    ADD CONSTRAINT ghettoq_queue_name_key UNIQUE (name);


--
-- Name: ghettoq_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY ghettoq_queue
    ADD CONSTRAINT ghettoq_queue_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_job_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_job
    ADD CONSTRAINT yabiengine_job_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_queuedworkflow_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_queuedworkflow
    ADD CONSTRAINT yabiengine_queuedworkflow_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_stagein_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_stagein
    ADD CONSTRAINT yabiengine_stagein_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_syslog_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_syslog
    ADD CONSTRAINT yabiengine_syslog_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_tag
    ADD CONSTRAINT yabiengine_tag_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_task_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_task
    ADD CONSTRAINT yabiengine_task_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_workflow_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_workflow
    ADD CONSTRAINT yabiengine_workflow_pkey PRIMARY KEY (id);


--
-- Name: yabiengine_workflowtag_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabiengine_workflowtag
    ADD CONSTRAINT yabiengine_workflowtag_pkey PRIMARY KEY (id);


--
-- Name: yabmin_backend_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_backend
    ADD CONSTRAINT yabmin_backend_pkey PRIMARY KEY (id);


--
-- Name: yabmin_backendcredential_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_backendcredential
    ADD CONSTRAINT yabmin_backendcredential_pkey PRIMARY KEY (id);


--
-- Name: yabmin_credential_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_credential
    ADD CONSTRAINT yabmin_credential_pkey PRIMARY KEY (id);


--
-- Name: yabmin_fileextension_extension_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_fileextension
    ADD CONSTRAINT yabmin_fileextension_extension_key UNIQUE (extension);


--
-- Name: yabmin_fileextension_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_fileextension
    ADD CONSTRAINT yabmin_fileextension_pkey PRIMARY KEY (id);


--
-- Name: yabmin_filetype_extensions_filetype_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_filetype_extensions
    ADD CONSTRAINT yabmin_filetype_extensions_filetype_id_key UNIQUE (filetype_id, fileextension_id);


--
-- Name: yabmin_filetype_extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_filetype_extensions
    ADD CONSTRAINT yabmin_filetype_extensions_pkey PRIMARY KEY (id);


--
-- Name: yabmin_filetype_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_filetype
    ADD CONSTRAINT yabmin_filetype_name_key UNIQUE (name);


--
-- Name: yabmin_filetype_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_filetype
    ADD CONSTRAINT yabmin_filetype_pkey PRIMARY KEY (id);


--
-- Name: yabmin_parameterfilter_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_parameterfilter
    ADD CONSTRAINT yabmin_parameterfilter_pkey PRIMARY KEY (id);


--
-- Name: yabmin_parameterswitchuse_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_parameterswitchuse
    ADD CONSTRAINT yabmin_parameterswitchuse_pkey PRIMARY KEY (id);


--
-- Name: yabmin_tool_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_tool
    ADD CONSTRAINT yabmin_tool_name_key UNIQUE (name);


--
-- Name: yabmin_tool_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_tool
    ADD CONSTRAINT yabmin_tool_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolgroup_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolgroup
    ADD CONSTRAINT yabmin_toolgroup_name_key UNIQUE (name);


--
-- Name: yabmin_toolgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolgroup
    ADD CONSTRAINT yabmin_toolgroup_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolgrouping_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT yabmin_toolgrouping_pkey PRIMARY KEY (id);


--
-- Name: yabmin_tooloutputextension_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_tooloutputextension
    ADD CONSTRAINT yabmin_tooloutputextension_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolparameter_accepted_filetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolparameter_accepted_filetypes
    ADD CONSTRAINT yabmin_toolparameter_accepted_filetypes_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolparameter_accepted_filetypes_toolparameter_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolparameter_accepted_filetypes
    ADD CONSTRAINT yabmin_toolparameter_accepted_filetypes_toolparameter_id_key UNIQUE (toolparameter_id, filetype_id);


--
-- Name: yabmin_toolparameter_input_extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolparameter_input_extensions
    ADD CONSTRAINT yabmin_toolparameter_input_extensions_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolparameter_input_extensions_toolparameter_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolparameter_input_extensions
    ADD CONSTRAINT yabmin_toolparameter_input_extensions_toolparameter_id_key UNIQUE (toolparameter_id, fileextension_id);


--
-- Name: yabmin_toolparameter_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabmin_toolparameter_pkey PRIMARY KEY (id);


--
-- Name: yabmin_toolset_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolset
    ADD CONSTRAINT yabmin_toolset_name_key UNIQUE (name);


--
-- Name: yabmin_toolset_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_toolset
    ADD CONSTRAINT yabmin_toolset_pkey PRIMARY KEY (id);


--
-- Name: yabmin_user_name_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_user
    ADD CONSTRAINT yabmin_user_name_key UNIQUE (name);


--
-- Name: yabmin_user_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_user
    ADD CONSTRAINT yabmin_user_pkey PRIMARY KEY (id);


--
-- Name: yabmin_user_toolsets_pkey; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_user_toolsets
    ADD CONSTRAINT yabmin_user_toolsets_pkey PRIMARY KEY (id);


--
-- Name: yabmin_user_toolsets_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabiapp; Tablespace: 
--

ALTER TABLE ONLY yabi_user_toolsets
    ADD CONSTRAINT yabmin_user_toolsets_user_id_key UNIQUE (user_id, toolset_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: django_evolution_version_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX django_evolution_version_id ON django_evolution USING btree (version_id);


--
-- Name: ghettoq_message_queue_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX ghettoq_message_queue_id ON ghettoq_message USING btree (queue_id);


--
-- Name: ghettoq_message_sent_at; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX ghettoq_message_sent_at ON ghettoq_message USING btree (sent_at);


--
-- Name: ghettoq_message_visible; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX ghettoq_message_visible ON ghettoq_message USING btree (visible);


--
-- Name: yabiengine_job_workflow_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabiengine_job_workflow_id ON yabiengine_job USING btree (workflow_id);


--
-- Name: yabiengine_queuedworkflow_workflow_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabiengine_queuedworkflow_workflow_id ON yabiengine_queuedworkflow USING btree (workflow_id);


--
-- Name: yabiengine_stagein_task_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabiengine_stagein_task_id ON yabiengine_stagein USING btree (task_id);


--
-- Name: yabiengine_task_job_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabiengine_task_job_id ON yabiengine_task USING btree (job_id);


--
-- Name: yabiengine_workflow_user_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabiengine_workflow_user_id ON yabiengine_workflow USING btree (user_id);


--
-- Name: yabmin_backend_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backend_created_by_id ON yabi_backend USING btree (created_by_id);


--
-- Name: yabmin_backend_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backend_last_modified_by_id ON yabi_backend USING btree (last_modified_by_id);


--
-- Name: yabmin_backendcredential_backend_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backendcredential_backend_id ON yabi_backendcredential USING btree (backend_id);


--
-- Name: yabmin_backendcredential_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backendcredential_created_by_id ON yabi_backendcredential USING btree (created_by_id);


--
-- Name: yabmin_backendcredential_credential_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backendcredential_credential_id ON yabi_backendcredential USING btree (credential_id);


--
-- Name: yabmin_backendcredential_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_backendcredential_last_modified_by_id ON yabi_backendcredential USING btree (last_modified_by_id);


--
-- Name: yabmin_credential_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_credential_created_by_id ON yabi_credential USING btree (created_by_id);


--
-- Name: yabmin_credential_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_credential_last_modified_by_id ON yabi_credential USING btree (last_modified_by_id);


--
-- Name: yabmin_credential_user_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_credential_user_id ON yabi_credential USING btree (user_id);


--
-- Name: yabmin_fileextension_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_fileextension_created_by_id ON yabi_fileextension USING btree (created_by_id);


--
-- Name: yabmin_fileextension_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_fileextension_last_modified_by_id ON yabi_fileextension USING btree (last_modified_by_id);


--
-- Name: yabmin_filetype_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_filetype_created_by_id ON yabi_filetype USING btree (created_by_id);


--
-- Name: yabmin_filetype_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_filetype_last_modified_by_id ON yabi_filetype USING btree (last_modified_by_id);


--
-- Name: yabmin_parameterfilter_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_parameterfilter_created_by_id ON yabi_parameterfilter USING btree (created_by_id);


--
-- Name: yabmin_parameterfilter_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_parameterfilter_last_modified_by_id ON yabi_parameterfilter USING btree (last_modified_by_id);


--
-- Name: yabmin_parameterswitchuse_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_parameterswitchuse_created_by_id ON yabi_parameterswitchuse USING btree (created_by_id);


--
-- Name: yabmin_parameterswitchuse_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_parameterswitchuse_last_modified_by_id ON yabi_parameterswitchuse USING btree (last_modified_by_id);


--
-- Name: yabmin_tool_backend_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tool_backend_id ON yabi_tool USING btree (backend_id);


--
-- Name: yabmin_tool_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tool_created_by_id ON yabi_tool USING btree (created_by_id);


--
-- Name: yabmin_tool_fs_backend_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tool_fs_backend_id ON yabi_tool USING btree (fs_backend_id);


--
-- Name: yabmin_tool_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tool_last_modified_by_id ON yabi_tool USING btree (last_modified_by_id);


--
-- Name: yabmin_toolgroup_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgroup_created_by_id ON yabi_toolgroup USING btree (created_by_id);


--
-- Name: yabmin_toolgroup_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgroup_last_modified_by_id ON yabi_toolgroup USING btree (last_modified_by_id);


--
-- Name: yabmin_toolgrouping_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgrouping_created_by_id ON yabi_toolgrouping USING btree (created_by_id);


--
-- Name: yabmin_toolgrouping_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgrouping_last_modified_by_id ON yabi_toolgrouping USING btree (last_modified_by_id);


--
-- Name: yabmin_toolgrouping_tool_group_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgrouping_tool_group_id ON yabi_toolgrouping USING btree (tool_group_id);


--
-- Name: yabmin_toolgrouping_tool_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgrouping_tool_id ON yabi_toolgrouping USING btree (tool_id);


--
-- Name: yabmin_toolgrouping_tool_set_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolgrouping_tool_set_id ON yabi_toolgrouping USING btree (tool_set_id);


--
-- Name: yabmin_tooloutputextension_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tooloutputextension_created_by_id ON yabi_tooloutputextension USING btree (created_by_id);


--
-- Name: yabmin_tooloutputextension_file_extension_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tooloutputextension_file_extension_id ON yabi_tooloutputextension USING btree (file_extension_id);


--
-- Name: yabmin_tooloutputextension_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tooloutputextension_last_modified_by_id ON yabi_tooloutputextension USING btree (last_modified_by_id);


--
-- Name: yabmin_tooloutputextension_tool_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_tooloutputextension_tool_id ON yabi_tooloutputextension USING btree (tool_id);


--
-- Name: yabmin_toolparameter_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolparameter_created_by_id ON yabi_toolparameter USING btree (created_by_id);


--
-- Name: yabmin_toolparameter_extension_param_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolparameter_extension_param_id ON yabi_toolparameter USING btree (extension_param_id);


--
-- Name: yabmin_toolparameter_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolparameter_last_modified_by_id ON yabi_toolparameter USING btree (last_modified_by_id);


--
-- Name: yabmin_toolparameter_switch_use_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolparameter_switch_use_id ON yabi_toolparameter USING btree (switch_use_id);


--
-- Name: yabmin_toolparameter_tool_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolparameter_tool_id ON yabi_toolparameter USING btree (tool_id);


--
-- Name: yabmin_toolset_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolset_created_by_id ON yabi_toolset USING btree (created_by_id);


--
-- Name: yabmin_toolset_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_toolset_last_modified_by_id ON yabi_toolset USING btree (last_modified_by_id);


--
-- Name: yabmin_user_created_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_user_created_by_id ON yabi_user USING btree (created_by_id);


--
-- Name: yabmin_user_last_modified_by_id; Type: INDEX; Schema: public; Owner: yabiapp; Tablespace: 
--

CREATE INDEX yabmin_user_last_modified_by_id ON yabi_user USING btree (last_modified_by_id);


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_id_refs_id_191701d8; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tool
    ADD CONSTRAINT backend_id_refs_id_191701d8 FOREIGN KEY (backend_id) REFERENCES yabi_backend(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_288599e6; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT content_type_id_refs_id_288599e6 FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_evolution_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY django_evolution
    ADD CONSTRAINT django_evolution_version_id_fkey FOREIGN KEY (version_id) REFERENCES django_project_version(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ghettoq_message_queue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY ghettoq_message
    ADD CONSTRAINT ghettoq_message_queue_id_fkey FOREIGN KEY (queue_id) REFERENCES ghettoq_queue(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tool_set_id_refs_id_47dac439; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT tool_set_id_refs_id_47dac439 FOREIGN KEY (tool_set_id) REFERENCES yabi_toolset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_c8665aa; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT user_id_refs_id_c8665aa FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabi_toolparameter_extension_param_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabi_toolparameter_extension_param_id_fkey FOREIGN KEY (extension_param_id) REFERENCES yabi_fileextension(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_job_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_job
    ADD CONSTRAINT yabiengine_job_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES yabiengine_workflow(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_queuedworkflow_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_queuedworkflow
    ADD CONSTRAINT yabiengine_queuedworkflow_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES yabiengine_workflow(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_stagein_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_stagein
    ADD CONSTRAINT yabiengine_stagein_task_id_fkey FOREIGN KEY (task_id) REFERENCES yabiengine_task(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_task_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_task
    ADD CONSTRAINT yabiengine_task_job_id_fkey FOREIGN KEY (job_id) REFERENCES yabiengine_job(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_workflow_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_workflow
    ADD CONSTRAINT yabiengine_workflow_user_id_fkey FOREIGN KEY (user_id) REFERENCES yabi_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_workflowtag_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_workflowtag
    ADD CONSTRAINT yabiengine_workflowtag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES yabiengine_tag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabiengine_workflowtag_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabiengine_workflowtag
    ADD CONSTRAINT yabiengine_workflowtag_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES yabiengine_workflow(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backend_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backend
    ADD CONSTRAINT yabmin_backend_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backend_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backend
    ADD CONSTRAINT yabmin_backend_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backendcredential_backend_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backendcredential
    ADD CONSTRAINT yabmin_backendcredential_backend_id_fkey FOREIGN KEY (backend_id) REFERENCES yabi_backend(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backendcredential_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backendcredential
    ADD CONSTRAINT yabmin_backendcredential_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backendcredential_credential_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backendcredential
    ADD CONSTRAINT yabmin_backendcredential_credential_id_fkey FOREIGN KEY (credential_id) REFERENCES yabi_credential(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_backendcredential_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_backendcredential
    ADD CONSTRAINT yabmin_backendcredential_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_credential_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_credential
    ADD CONSTRAINT yabmin_credential_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_credential_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_credential
    ADD CONSTRAINT yabmin_credential_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_credential_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_credential
    ADD CONSTRAINT yabmin_credential_user_id_fkey FOREIGN KEY (user_id) REFERENCES yabi_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_fileextension_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_fileextension
    ADD CONSTRAINT yabmin_fileextension_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_fileextension_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_fileextension
    ADD CONSTRAINT yabmin_fileextension_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_filetype_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_filetype
    ADD CONSTRAINT yabmin_filetype_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_filetype_extensions_fileextension_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_filetype_extensions
    ADD CONSTRAINT yabmin_filetype_extensions_fileextension_id_fkey FOREIGN KEY (fileextension_id) REFERENCES yabi_fileextension(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_filetype_extensions_filetype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_filetype_extensions
    ADD CONSTRAINT yabmin_filetype_extensions_filetype_id_fkey FOREIGN KEY (filetype_id) REFERENCES yabi_filetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_filetype_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_filetype
    ADD CONSTRAINT yabmin_filetype_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_parameterfilter_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_parameterfilter
    ADD CONSTRAINT yabmin_parameterfilter_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_parameterfilter_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_parameterfilter
    ADD CONSTRAINT yabmin_parameterfilter_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_parameterswitchuse_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_parameterswitchuse
    ADD CONSTRAINT yabmin_parameterswitchuse_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_parameterswitchuse_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_parameterswitchuse
    ADD CONSTRAINT yabmin_parameterswitchuse_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tool_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tool
    ADD CONSTRAINT yabmin_tool_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tool_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tool
    ADD CONSTRAINT yabmin_tool_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgroup_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgroup
    ADD CONSTRAINT yabmin_toolgroup_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgroup_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgroup
    ADD CONSTRAINT yabmin_toolgroup_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgrouping_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT yabmin_toolgrouping_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgrouping_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT yabmin_toolgrouping_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgrouping_tool_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT yabmin_toolgrouping_tool_group_id_fkey FOREIGN KEY (tool_group_id) REFERENCES yabi_toolgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolgrouping_tool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolgrouping
    ADD CONSTRAINT yabmin_toolgrouping_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES yabi_tool(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tooloutputextension_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tooloutputextension
    ADD CONSTRAINT yabmin_tooloutputextension_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tooloutputextension_file_extension_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tooloutputextension
    ADD CONSTRAINT yabmin_tooloutputextension_file_extension_id_fkey FOREIGN KEY (file_extension_id) REFERENCES yabi_fileextension(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tooloutputextension_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tooloutputextension
    ADD CONSTRAINT yabmin_tooloutputextension_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_tooloutputextension_tool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_tooloutputextension
    ADD CONSTRAINT yabmin_tooloutputextension_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES yabi_tool(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_accepted_filetypes_filetype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter_accepted_filetypes
    ADD CONSTRAINT yabmin_toolparameter_accepted_filetypes_filetype_id_fkey FOREIGN KEY (filetype_id) REFERENCES yabi_filetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_accepted_filetypes_toolparameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter_accepted_filetypes
    ADD CONSTRAINT yabmin_toolparameter_accepted_filetypes_toolparameter_id_fkey FOREIGN KEY (toolparameter_id) REFERENCES yabi_toolparameter(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabmin_toolparameter_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_input_extensions_fileextension_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter_input_extensions
    ADD CONSTRAINT yabmin_toolparameter_input_extensions_fileextension_id_fkey FOREIGN KEY (fileextension_id) REFERENCES yabi_fileextension(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_input_extensions_toolparameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter_input_extensions
    ADD CONSTRAINT yabmin_toolparameter_input_extensions_toolparameter_id_fkey FOREIGN KEY (toolparameter_id) REFERENCES yabi_toolparameter(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabmin_toolparameter_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_switch_use_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabmin_toolparameter_switch_use_id_fkey FOREIGN KEY (switch_use_id) REFERENCES yabi_parameterswitchuse(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolparameter_tool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolparameter
    ADD CONSTRAINT yabmin_toolparameter_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES yabi_tool(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolset_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolset
    ADD CONSTRAINT yabmin_toolset_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_toolset_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_toolset
    ADD CONSTRAINT yabmin_toolset_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_user_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_user
    ADD CONSTRAINT yabmin_user_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_user_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_user
    ADD CONSTRAINT yabmin_user_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_user_toolsets_toolset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_user_toolsets
    ADD CONSTRAINT yabmin_user_toolsets_toolset_id_fkey FOREIGN KEY (toolset_id) REFERENCES yabi_toolset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabmin_user_toolsets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabiapp
--

ALTER TABLE ONLY yabi_user_toolsets
    ADD CONSTRAINT yabmin_user_toolsets_user_id_fkey FOREIGN KEY (user_id) REFERENCES yabi_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

