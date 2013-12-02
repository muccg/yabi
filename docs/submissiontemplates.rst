.. _submissiontemplates:

Submission Templates
====================

Yabi uses a submission template every time it submits a job.
The submission template allows the user to customise the command according to the needs of the backend or tool.

Here is an example submission template for a PBS execution backend::

    #!/bin/sh
    #PBS -l walltime=${walltime}
    #PBS -l mem=${memory}
    #PBS -l nodes=1:ppn=${cpus}
    %if queue == 'debugq':
    #PBS -q debugq
    %else:
    #PBS -q routequeue
    %endif
    #PBS -W group_list=my_account_id
    % for module in modules:
        module load ${module}
    % endfor
    cd '${working}'
    ${command}


As you can see, the template is a script that will be passed to qsub and it allows us to use PBS directives, load modules etc.

The variables placed inside `${}` are Submission Template Variables that Yabi makes available for each template. Please refer
to :ref:`submissiontemplatevariables` for a description of variables available and their meaning.

The submission templates are using the `Mako templating system <http://www.makotemplates.org/>`.

Submission Template Lookup Order
--------------------------------

Submission templates can be defined on any of the Tools, Backend Credentials or Backends.
When a task is submitted Yabi will use the following lookup order to decide which submission template to use:

#. Tool submission template used if defined
#. Backend Credential submission template used if defined
#. Backend submission template used

Usually only Backend submission templates are defined and used for most Tools.
Tools that need further customisation will define their own submission template.

.. _submissiontemplatevariables:

Submission Template Variables
-----------------------------

The following is a table of the variables available in the template, and their meaning. Variables are to be placed inside `${}` in the template.

+--------------+----------------------------------------------------------------------------------------------------------+
| Key          | Value                                                                                                    |
+==============+==========================================================================================================+
| working      | The full path of the working directory for the job.                                                      |
+--------------+----------------------------------------------------------------------------------------------------------+
| command      | The full command line for the final task. The executable and all its passed in arguments.                |
+--------------+----------------------------------------------------------------------------------------------------------+
| modules      | A list of all the modules that need loading.                                                             |
+--------------+----------------------------------------------------------------------------------------------------------+
| cpus         | Number of cpus that should be utilised.                                                                  |
+--------------+----------------------------------------------------------------------------------------------------------+
| memory       | The amount of RAM that should be partitioned for the job.                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| walltime     | The walltime for the job.                                                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| yabiusername | The username of the yabi user that submitted the job. Can be different from the backend username.        |
+--------------+----------------------------------------------------------------------------------------------------------+
| username     | The username the job is to be run as                                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| host         | The hostname the job is being run on                                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| queue        | The name of the queue the job should be submitted to                                                     |
+--------------+----------------------------------------------------------------------------------------------------------+
| tasknum      | The number (from 1 to tasktotal) of this particular task in the job set.                                 |
+--------------+----------------------------------------------------------------------------------------------------------+
| tasktotal    | The total number of tasks in the job set.                                                                |
+--------------+----------------------------------------------------------------------------------------------------------+
| envvars      | User suppled environment variables. Please see :ref:`yabi-envvars`                                       |
+--------------+----------------------------------------------------------------------------------------------------------+

.. _yabi-envvars:

User-supplied Environment Variables
-----------------------------------

Yabi allows further customisation of the submission template by using user-supplied submission template variables.

Any tool can define an input file parameter called ``.envvars.yabi`` which is a *special* file. If a job has an input file
called ``.envvars.yabi`` all the variables in it will be made available in the submission template variable ``envvars``.

The format of the ``.envvars.yabi`` file is JSON.

For example, if the following ``.envvars.yabi`` is passed to a Job::

   {
      "aMap":
            ["first", "second"],
      "anotherMap": {
            "nestedMapKey": "nestedValue"
      }
   }

In the submission template you could use::

   echo "This will evaluate to     'second'      : ${envvars['aMap'][1]}"
   echo "And this will evaluate to 'nestedValue' : ${envvars['anotherMap']['nestedMapKey']}"

Allowing any valid JSON in the environment file and Mako syntax in the submission template allows a lot of flexibility when running jobs through Yabi.

Furthermore, the ``.envvars.yabi`` file doesn't have to be static, it can be dynamically generated on the server by another Tool.
This way you can have a Tool that runs on the server and by writing out the environment file it can effect how a subsequent Tool is executed.

The following example ``count-files.sh`` is a simple bash script that counts the number of arguments passed to it and writes it to the Yabi environment file::

    #!/bin/bash

    cat <<EOS > .envvars.yabi
    {
      "job_array": "1-$#"
    }
    EOS

Then another Yabi Tool *"cp Job Array on Torque"* can be set up for the standard UNIX tool ``cp`` with the following Submission Template::

    #!/bin/sh
    #PBS -t ${envvars['job_array']}
    cd '${working}'
    ${command} ../input/testfile_$PBS_ARRAYID.txt testfile_$PBS_ARRAYID.COPY.txt

The two Tools above can be combined together to run a Job Array of the size determined dynamically by ``count-files.sh`` based on the number of files passed to it.

The Job Array will have consist of one Subjob for each file of the form ``testfile_INDEX.txt`` (where INDEX is 1,2,3,...) and it will make a copy for each file named ``testfile_INDEX.COPY.txt``.

