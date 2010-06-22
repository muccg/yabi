 BEGIN;
 CREATE TABLE celery_taskmeta (
     id integer NOT NULL,
     task_id character varying(255) NOT NULL,
     status character varying(50) NOT NULL,
     result text NOT NULL,
     date_done timestamp with time zone NOT NULL,
     traceback text
 );
 
 CREATE SEQUENCE celery_taskmeta_id_seq
     INCREMENT BY 1
     NO MAXVALUE
     NO MINVALUE
     CACHE 1;
 
 CREATE TABLE celery_tasksetmeta (
     id integer NOT NULL,
     taskset_id character varying(255) NOT NULL,
     result text NOT NULL,
     date_done timestamp with time zone NOT NULL
 );
 
 
 CREATE SEQUENCE celery_tasksetmeta_id_seq
     START WITH 1
     INCREMENT BY 1
     NO MAXVALUE
     NO MINVALUE
     CACHE 1;
 
 CREATE TABLE ghettoq_message (
     id integer NOT NULL,
     visible boolean NOT NULL,
     "timestamp" timestamp with time zone,
     payload text NOT NULL,
     queue_id integer NOT NULL
 );
 
 
 CREATE SEQUENCE ghettoq_message_id_seq
     INCREMENT BY 1
     NO MAXVALUE
     NO MINVALUE
     CACHE 1;
 
 CREATE TABLE ghettoq_queue (
     id integer NOT NULL,
     name character varying(200) NOT NULL
 );
 
 
 CREATE SEQUENCE ghettoq_queue_id_seq
     INCREMENT BY 1
     NO MAXVALUE
     NO MINVALUE
     CACHE 1;
 
 ALTER TABLE celery_taskmeta ALTER COLUMN id SET DEFAULT nextval('celery_taskmeta_id_seq'::regclass);
 ALTER TABLE celery_tasksetmeta ALTER COLUMN id SET DEFAULT nextval('celery_tasksetmeta_id_seq'::regclass);
 ALTER TABLE ghettoq_message ALTER COLUMN id SET DEFAULT nextval('ghettoq_message_id_seq'::regclass);
 ALTER TABLE ghettoq_queue ALTER COLUMN id SET DEFAULT nextval('ghettoq_queue_id_seq'::regclass);

 ALTER TABLE ONLY celery_taskmeta
     ADD CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id);
 ALTER TABLE ONLY celery_taskmeta
     ADD CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id);
 ALTER TABLE ONLY celery_tasksetmeta
     ADD CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id);
 ALTER TABLE ONLY celery_tasksetmeta
     ADD CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id);
 ALTER TABLE ONLY ghettoq_message
     ADD CONSTRAINT ghettoq_message_pkey PRIMARY KEY (id);
 ALTER TABLE ONLY ghettoq_queue
     ADD CONSTRAINT ghettoq_queue_name_key UNIQUE (name);
 ALTER TABLE ONLY ghettoq_queue
     ADD CONSTRAINT ghettoq_queue_pkey PRIMARY KEY (id);
 CREATE INDEX ghettoq_message_queue_id ON ghettoq_message USING btree (queue_id);
 CREATE INDEX ghettoq_message_timestamp ON ghettoq_message USING btree ("timestamp");
 CREATE INDEX ghettoq_message_visible ON ghettoq_message USING btree (visible);
 ALTER TABLE ONLY ghettoq_message
     ADD CONSTRAINT ghettoq_message_queue_id_fkey FOREIGN KEY (queue_id) REFERENCES ghettoq_queue(id) DEFERRABLE INITIALLY DEFERRED;
END; 
