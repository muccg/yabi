BEGIN;

-- add a submission script field to backend --
ALTER TABLE "yabi_backend" ADD COLUMN "submission" text NOT NULL DEFAULT '';

-- add a submission script field to backendcredential --
ALTER TABLE "yabi_backendcredential" ADD COLUMN "submission" text NOT NULL DEFAULT '';

-- set the default backend submission scripts

-- ssh+pbspro
UPDATE "yabi_backend" 
    SET "submission" = E'#!/bin/sh\n#PBS -l walltime=${walltime}\n#PBS -l mem=${memory}\n#PBS -l ncpus=${cpus}\n% for module in modules:\n    module load ${module}\n% endfor\ncd \'${working}\'\n${command}\n' 
    WHERE "yabi_backend"."scheme"='ssh+pbspro';

-- torque
UPDATE "yabi_backend" 
    SET "submission" = E'#!/bin/sh\n% for module in modules:\n    module load ${module}\n% endfor\ncd \'${working}\'\n${command}\n' 
    WHERE "yabi_backend"."scheme"='torque';

-- ssh+torque
UPDATE "yabi_backend" 
    SET "submission" = E'#!/bin/sh\n% for module in modules:\n    module load ${module}\n% endfor\ncd \'${working}\'\n${command}\n' 
    WHERE "yabi_backend"."scheme"='ssh+torque';

-- globus
UPDATE "yabi_backend" 
    SET "submission" = 
E'<?xml version="1.0"?>\n'
'<%\n'
'  import shlex\n'
'  lexer = shlex.shlex(command, posix=True)\n'
'  lexer.wordchars += r"-.:;/="\n'
'  arguments = list(lexer)\n'
'%>\n'
'<job>\n'
'<executable>${arguments[0]}</executable>\n'
'<directory>${working}</directory>\n'
'%for arg in arguments[1:]:\n'
'  <argument>${arg}</argument>\n'
'%endfor\n'
'<stdout>${stdout}</stdout>\n'
'<stderr>${stderr}</stderr>\n'
'<count>${cpus}</count>\n'
'<queue>${queue}</queue>\n'
'<maxWallTime>${walltime}</maxWallTime>\n'
'<maxMemory>${memory}</maxMemory>\n'
'<jobType>single</jobType>\n'
'<extensions>\n'
'%for module in modules:\n'
'<module>${module}</module>\n'
'%endfor\n'
'</extensions>\n'
'</job>\n' 
    WHERE "yabi_backend"."scheme"='globus';


COMMIT;
