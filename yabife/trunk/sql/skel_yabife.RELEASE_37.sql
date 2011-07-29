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

ALTER TABLE ONLY public.yabifeapp_user DROP CONSTRAINT yabifeapp_user_user_id_fkey;
ALTER TABLE ONLY public.yabifeapp_user DROP CONSTRAINT yabifeapp_user_appliance_id_fkey;
ALTER TABLE ONLY public.yabifeapp_applianceadministrator DROP CONSTRAINT yabifeapp_applianceadministrator_appliance_id_fkey;
ALTER TABLE ONLY public.registration_request DROP CONSTRAINT registration_request_user_id_fkey;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_fkey;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_content_type_id_fkey;
ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT content_type_id_refs_id_728de91f;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_fkey;
ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_permission_id_fkey;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_fkey;
ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_group_id_fkey;
ALTER TABLE ONLY public.auth_message DROP CONSTRAINT auth_message_user_id_fkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_permission_id_fkey;
ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_fkey;
DROP INDEX public.yabifeapp_user_appliance_id;
DROP INDEX public.django_admin_log_user_id;
DROP INDEX public.django_admin_log_content_type_id;
DROP INDEX public.auth_permission_content_type_id;
DROP INDEX public.auth_message_user_id;
ALTER TABLE ONLY public.yabifeapp_user DROP CONSTRAINT yabifeapp_user_user_id_key;
ALTER TABLE ONLY public.yabifeapp_user DROP CONSTRAINT yabifeapp_user_pkey;
ALTER TABLE ONLY public.yabifeapp_applianceadministrator DROP CONSTRAINT yabifeapp_applianceadministrator_pkey;
ALTER TABLE ONLY public.yabifeapp_appliance DROP CONSTRAINT yabifeapp_appliance_pkey;
ALTER TABLE ONLY public.registration_request DROP CONSTRAINT registration_request_user_id_key;
ALTER TABLE ONLY public.registration_request DROP CONSTRAINT registration_request_pkey;
ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_pkey;
ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_key;
ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
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
ALTER TABLE public.yabifeapp_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabifeapp_applianceadministrator ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.yabifeapp_appliance ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.registration_request ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_site ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_user ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_message ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.yabifeapp_user_id_seq;
DROP TABLE public.yabifeapp_user;
DROP SEQUENCE public.yabifeapp_applianceadministrator_id_seq;
DROP TABLE public.yabifeapp_applianceadministrator;
DROP SEQUENCE public.yabifeapp_appliance_id_seq;
DROP TABLE public.yabifeapp_appliance;
DROP SEQUENCE public.registration_request_id_seq;
DROP TABLE public.registration_request;
DROP SEQUENCE public.django_site_id_seq;
DROP TABLE public.django_site;
DROP TABLE public.django_session;
DROP SEQUENCE public.django_content_type_id_seq;
DROP TABLE public.django_content_type;
DROP SEQUENCE public.django_admin_log_id_seq;
DROP TABLE public.django_admin_log;
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
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO yabifeapp;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO yabifeapp;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO yabifeapp;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO yabifeapp;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_message; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO yabifeapp;

--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO yabifeapp;

--
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- Name: auth_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_message_id_seq', 47, true);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO yabifeapp;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO yabifeapp;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_permission_id_seq', 21, true);


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
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


ALTER TABLE public.auth_user OWNER TO yabifeapp;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO yabifeapp;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO yabifeapp;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 32, true);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO yabifeapp;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO yabifeapp;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO yabifeapp;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
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


ALTER TABLE public.django_admin_log OWNER TO yabifeapp;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO yabifeapp;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 2, true);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO yabifeapp;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO yabifeapp;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('django_content_type_id_seq', 9, true);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO yabifeapp;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO yabifeapp;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO yabifeapp;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('django_site_id_seq', 1, true);


--
-- Name: registration_request; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE registration_request (
    id integer NOT NULL,
    user_id integer NOT NULL,
    state smallint NOT NULL,
    confirmation_key character varying(32) NOT NULL,
    request_time timestamp with time zone NOT NULL,
    CONSTRAINT registration_request_state_check CHECK ((state >= 0))
);


ALTER TABLE public.registration_request OWNER TO yabifeapp;

--
-- Name: registration_request_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE registration_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.registration_request_id_seq OWNER TO yabifeapp;

--
-- Name: registration_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE registration_request_id_seq OWNED BY registration_request.id;


--
-- Name: registration_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('registration_request_id_seq', 1, false);


--
-- Name: yabifeapp_appliance; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE yabifeapp_appliance (
    id integer NOT NULL,
    url character varying(200) NOT NULL,
    name character varying(50) DEFAULT ''::character varying NOT NULL,
    tos text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.yabifeapp_appliance OWNER TO yabifeapp;

--
-- Name: yabifeapp_appliance_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE yabifeapp_appliance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabifeapp_appliance_id_seq OWNER TO yabifeapp;

--
-- Name: yabifeapp_appliance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE yabifeapp_appliance_id_seq OWNED BY yabifeapp_appliance.id;


--
-- Name: yabifeapp_appliance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('yabifeapp_appliance_id_seq', 1, true);


--
-- Name: yabifeapp_applianceadministrator; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE yabifeapp_applianceadministrator (
    id integer NOT NULL,
    appliance_id integer NOT NULL,
    name character varying(200) NOT NULL,
    email character varying(75) NOT NULL
);


ALTER TABLE public.yabifeapp_applianceadministrator OWNER TO yabifeapp;

--
-- Name: yabifeapp_applianceadministrator_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE yabifeapp_applianceadministrator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabifeapp_applianceadministrator_id_seq OWNER TO yabifeapp;

--
-- Name: yabifeapp_applianceadministrator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE yabifeapp_applianceadministrator_id_seq OWNED BY yabifeapp_applianceadministrator.id;


--
-- Name: yabifeapp_applianceadministrator_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('yabifeapp_applianceadministrator_id_seq', 1, false);


--
-- Name: yabifeapp_user; Type: TABLE; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE TABLE yabifeapp_user (
    id integer NOT NULL,
    user_id integer NOT NULL,
    appliance_id integer NOT NULL,
    user_option_access boolean DEFAULT true NOT NULL,
    credential_access boolean DEFAULT true NOT NULL
);


ALTER TABLE public.yabifeapp_user OWNER TO yabifeapp;

--
-- Name: yabifeapp_user_id_seq; Type: SEQUENCE; Schema: public; Owner: yabifeapp
--

CREATE SEQUENCE yabifeapp_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.yabifeapp_user_id_seq OWNER TO yabifeapp;

--
-- Name: yabifeapp_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yabifeapp
--

ALTER SEQUENCE yabifeapp_user_id_seq OWNED BY yabifeapp_user.id;


--
-- Name: yabifeapp_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yabifeapp
--

SELECT pg_catalog.setval('yabifeapp_user_id_seq', 2, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE registration_request ALTER COLUMN id SET DEFAULT nextval('registration_request_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE yabifeapp_appliance ALTER COLUMN id SET DEFAULT nextval('yabifeapp_appliance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE yabifeapp_applianceadministrator ALTER COLUMN id SET DEFAULT nextval('yabifeapp_applianceadministrator_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: yabifeapp
--

ALTER TABLE yabifeapp_user ALTER COLUMN id SET DEFAULT nextval('yabifeapp_user_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_group (id, name) FROM stdin;
1	baseuser
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_message; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_message (id, user_id, message) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add permission	1	add_permission
2	Can change permission	1	change_permission
3	Can delete permission	1	delete_permission
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add user	3	add_user
8	Can change user	3	change_user
9	Can delete user	3	delete_user
10	Can add message	4	add_message
11	Can change message	4	change_message
12	Can delete message	4	delete_message
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
19	Can add site	7	add_site
20	Can change site	7	change_site
21	Can delete site	7	delete_site
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) FROM stdin;
1	django			techs@ccg.murdoch.edu.au	sha1$33d5e$decb15515dfb367b5122eb3af8ed66f19fa7f07a	t	t	t	2009-06-16 11:31:36.613084+08	2009-06-16 11:31:36.613084+08
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY django_admin_log (id, action_time, user_id, content_type_id, object_id, object_repr, action_flag, change_message) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	permission	auth	permission
2	group	auth	group
3	user	auth	user
4	message	auth	message
5	content type	contenttypes	contenttype
6	session	sessions	session
7	site	sites	site
8	appliance	yabifeapp	appliance
9	user	yabifeapp	user
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY django_site (id, domain, name) FROM stdin;
1	example.com	example.com
\.


--
-- Data for Name: registration_request; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY registration_request (id, user_id, state, confirmation_key, request_time) FROM stdin;
\.


--
-- Data for Name: yabifeapp_appliance; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY yabifeapp_appliance (id, url, name, tos) FROM stdin;
\.


--
-- Data for Name: yabifeapp_applianceadministrator; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY yabifeapp_applianceadministrator (id, appliance_id, name, email) FROM stdin;
\.


--
-- Data for Name: yabifeapp_user; Type: TABLE DATA; Schema: public; Owner: yabifeapp
--

COPY yabifeapp_user (id, user_id, appliance_id, user_option_access, credential_access) FROM stdin;
\.


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: registration_request_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY registration_request
    ADD CONSTRAINT registration_request_pkey PRIMARY KEY (id);


--
-- Name: registration_request_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY registration_request
    ADD CONSTRAINT registration_request_user_id_key UNIQUE (user_id);


--
-- Name: yabifeapp_appliance_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY yabifeapp_appliance
    ADD CONSTRAINT yabifeapp_appliance_pkey PRIMARY KEY (id);


--
-- Name: yabifeapp_applianceadministrator_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY yabifeapp_applianceadministrator
    ADD CONSTRAINT yabifeapp_applianceadministrator_pkey PRIMARY KEY (id);


--
-- Name: yabifeapp_user_pkey; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY yabifeapp_user
    ADD CONSTRAINT yabifeapp_user_pkey PRIMARY KEY (id);


--
-- Name: yabifeapp_user_user_id_key; Type: CONSTRAINT; Schema: public; Owner: yabifeapp; Tablespace: 
--

ALTER TABLE ONLY yabifeapp_user
    ADD CONSTRAINT yabifeapp_user_user_id_key UNIQUE (user_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: yabifeapp_user_appliance_id; Type: INDEX; Schema: public; Owner: yabifeapp; Tablespace: 
--

CREATE INDEX yabifeapp_user_appliance_id ON yabifeapp_user USING btree (appliance_id);


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: registration_request_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY registration_request
    ADD CONSTRAINT registration_request_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabifeapp_applianceadministrator_appliance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY yabifeapp_applianceadministrator
    ADD CONSTRAINT yabifeapp_applianceadministrator_appliance_id_fkey FOREIGN KEY (appliance_id) REFERENCES yabifeapp_appliance(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabifeapp_user_appliance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY yabifeapp_user
    ADD CONSTRAINT yabifeapp_user_appliance_id_fkey FOREIGN KEY (appliance_id) REFERENCES yabifeapp_appliance(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: yabifeapp_user_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: yabifeapp
--

ALTER TABLE ONLY yabifeapp_user
    ADD CONSTRAINT yabifeapp_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

