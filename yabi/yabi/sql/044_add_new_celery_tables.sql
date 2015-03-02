BEGIN;

CREATE TABLE "celery_taskmeta" (
    "id" serial NOT NULL PRIMARY KEY,
    "task_id" varchar(255) NOT NULL UNIQUE,
    "status" varchar(50) NOT NULL,
    "result" text,
    "date_done" timestamp with time zone NOT NULL,
    "traceback" text
)
;
CREATE TABLE "celery_tasksetmeta" (
    "id" serial NOT NULL PRIMARY KEY,
    "taskset_id" varchar(255) NOT NULL UNIQUE,
    "result" text NOT NULL,
    "date_done" timestamp with time zone NOT NULL
)
;
CREATE TABLE "djcelery_intervalschedule" (
    "id" serial NOT NULL PRIMARY KEY,
    "every" integer NOT NULL,
    "period" varchar(24) NOT NULL
)
;
CREATE TABLE "djcelery_crontabschedule" (
    "id" serial NOT NULL PRIMARY KEY,
    "minute" varchar(64) NOT NULL,
    "hour" varchar(64) NOT NULL,
    "day_of_week" varchar(64) NOT NULL
)
;
CREATE TABLE "djcelery_periodictasks" (
    "ident" smallint NOT NULL PRIMARY KEY,
    "last_update" timestamp with time zone NOT NULL
)
;
CREATE TABLE "djcelery_periodictask" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL UNIQUE,
    "task" varchar(200) NOT NULL,
    "interval_id" integer REFERENCES "djcelery_intervalschedule" ("id") DEFERRABLE INITIALLY DEFERRED,
    "crontab_id" integer REFERENCES "djcelery_crontabschedule" ("id") DEFERRABLE INITIALLY DEFERRED,
    "args" text NOT NULL,
    "kwargs" text NOT NULL,
    "queue" varchar(200),
    "exchange" varchar(200),
    "routing_key" varchar(200),
    "expires" timestamp with time zone,
    "enabled" boolean NOT NULL,
    "last_run_at" timestamp with time zone,
    "total_run_count" integer CHECK ("total_run_count" >= 0) NOT NULL,
    "date_changed" timestamp with time zone NOT NULL
)
;
CREATE TABLE "djcelery_workerstate" (
    "id" serial NOT NULL PRIMARY KEY,
    "hostname" varchar(255) NOT NULL UNIQUE,
    "last_heartbeat" timestamp with time zone
)
;
CREATE TABLE "djcelery_taskstate" (
    "id" serial NOT NULL PRIMARY KEY,
    "state" varchar(64) NOT NULL,
    "task_id" varchar(36) NOT NULL UNIQUE,
    "name" varchar(200),
    "tstamp" timestamp with time zone NOT NULL,
    "args" text,
    "kwargs" text,
    "eta" timestamp with time zone,
    "expires" timestamp with time zone,
    "result" text,
    "traceback" text,
    "runtime" double precision,
    "retries" integer NOT NULL,
    "worker_id" integer REFERENCES "djcelery_workerstate" ("id") DEFERRABLE INITIALLY DEFERRED,
    "hidden" boolean NOT NULL
)
;
CREATE INDEX "djcelery_periodictask_interval_id" ON "djcelery_periodictask" ("interval_id");
CREATE INDEX "djcelery_periodictask_crontab_id" ON "djcelery_periodictask" ("crontab_id");
CREATE INDEX "djcelery_workerstate_last_heartbeat" ON "djcelery_workerstate" ("last_heartbeat");
CREATE INDEX "djcelery_taskstate_state" ON "djcelery_taskstate" ("state");
CREATE INDEX "djcelery_taskstate_state_like" ON "djcelery_taskstate" ("state" varchar_pattern_ops);
CREATE INDEX "djcelery_taskstate_name" ON "djcelery_taskstate" ("name");
CREATE INDEX "djcelery_taskstate_name_like" ON "djcelery_taskstate" ("name" varchar_pattern_ops);
CREATE INDEX "djcelery_taskstate_tstamp" ON "djcelery_taskstate" ("tstamp");
CREATE INDEX "djcelery_taskstate_worker_id" ON "djcelery_taskstate" ("worker_id");
CREATE INDEX "djcelery_taskstate_hidden" ON "djcelery_taskstate" ("hidden");

COMMIT;


BEGIN;

CREATE TABLE "djkombu_queue" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL UNIQUE
)
;
CREATE TABLE "djkombu_message" (
    "id" serial NOT NULL PRIMARY KEY,
    "visible" boolean NOT NULL,
    "sent_at" timestamp with time zone,
    "payload" text NOT NULL,
    "queue_id" integer NOT NULL REFERENCES "djkombu_queue" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE INDEX "djkombu_message_visible" ON "djkombu_message" ("visible");
CREATE INDEX "djkombu_message_sent_at" ON "djkombu_message" ("sent_at");
CREATE INDEX "djkombu_message_queue_id" ON "djkombu_message" ("queue_id");

COMMIT;
