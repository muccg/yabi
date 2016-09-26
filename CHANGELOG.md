# Change Log

## [9.9.4](https://github.com/muccg/yabi/tree/9.9.4) (2016-09-26)
[Full Changelog](https://github.com/muccg/yabi/compare/9.9.3...9.9.4)

**Implemented enhancements:**

- django-anymail for email [\#527](https://github.com/muccg/yabi/issues/527)
- deprecate django secure [\#525](https://github.com/muccg/yabi/issues/525)

**Fixed bugs:**

- mime types for docker installation [\#524](https://github.com/muccg/yabi/issues/524)

## [9.9.3](https://github.com/muccg/yabi/tree/9.9.3) (2016-09-23)
[Full Changelog](https://github.com/muccg/yabi/compare/9.9.2...9.9.3)

**Implemented enhancements:**

- \[YABI-147\] Make the admin unit tests part of the test suite ran from yabictl.sh [\#520](https://github.com/muccg/yabi/issues/520)
- \[YABI-173\] remove source parameter from yabi config defaults [\#519](https://github.com/muccg/yabi/issues/519)
- python-ldap==2.4.27 [\#209](https://github.com/muccg/yabi/issues/209)
- pykerberos==1.1.13 [\#208](https://github.com/muccg/yabi/issues/208)
- ccg-django-utils==0.4.2 [\#207](https://github.com/muccg/yabi/issues/207)
- paramiko==1.16.3 [\#206](https://github.com/muccg/yabi/issues/206)
- celery==3.1.23 [\#205](https://github.com/muccg/yabi/issues/205)
- psycopg2==2.6.2 [\#204](https://github.com/muccg/yabi/issues/204)
- python-memcached==1.58 [\#203](https://github.com/muccg/yabi/issues/203)
- uwsgi 2.0.13.1 [\#202](https://github.com/muccg/yabi/issues/202)
- Remove reference to JIRA [\#133](https://github.com/muccg/yabi/issues/133)
- Django 1.8.14 [\#95](https://github.com/muccg/yabi/issues/95)
- Remove references to the Bitbucket repository [\#4](https://github.com/muccg/yabi/issues/4)

**Fixed bugs:**

- correct uwsgi static map [\#523](https://github.com/muccg/yabi/issues/523)
- Workflow reuse fails if a tool is renamed [\#3](https://github.com/muccg/yabi/issues/3)

**Closed issues:**

- \[YABI-3\] Yabi-be gsi-ssh [\#521](https://github.com/muccg/yabi/issues/521)
- \[YABI-186\] deprecate paramiko-1.7.7.1-fifopatch2 and upgrade to paramiko==1.10.1 [\#518](https://github.com/muccg/yabi/issues/518)
- \[YABI-190\] add ssh+torque section to config [\#517](https://github.com/muccg/yabi/issues/517)
- \[YABI-209\] RPM does not create certificates directory for backend [\#516](https://github.com/muccg/yabi/issues/516)
- \[YABI-8\] Kerberos authentication for front end [\#515](https://github.com/muccg/yabi/issues/515)
- \[YABI-22\] Thick finger support [\#511](https://github.com/muccg/yabi/issues/511)
- \[YABI-10\] Yabi-fe Encrypted credential passphrase popup entry widget [\#510](https://github.com/muccg/yabi/issues/510)
- \[YABI-2\] Yabi-fe user account registration [\#509](https://github.com/muccg/yabi/issues/509)
- \[YABI-104\] Update Status page to show backend [\#507](https://github.com/muccg/yabi/issues/507)
- \[YABI-36\] Flash uploader broken [\#505](https://github.com/muccg/yabi/issues/505)
- \[YABI-59\] Separate Frontend web and ws views [\#504](https://github.com/muccg/yabi/issues/504)
- \[YABI-27\] Yabi-admin - Split data and execution backends [\#501](https://github.com/muccg/yabi/issues/501)
- \[YABI-163\] Trouble interpreting pattern with no \* [\#500](https://github.com/muccg/yabi/issues/500)
- \[YABI-61\] Display images in html file preview [\#498](https://github.com/muccg/yabi/issues/498)
- \[YABI-267\] Support zip encoding for directory downloads [\#497](https://github.com/muccg/yabi/issues/497)
- \[YABI-241\] Enable the option to use an existing copy of an input file instead of creating a new copy using "Select file" [\#495](https://github.com/muccg/yabi/issues/495)
- \[YABI-242\] Cannot make tool where number of cpus and/or walltime is user configurable [\#494](https://github.com/muccg/yabi/issues/494)
- \[YABI-74\] Optional parameters with limited values [\#489](https://github.com/muccg/yabi/issues/489)
- \[YABI-66\] Take parameter value from defaults or custom [\#488](https://github.com/muccg/yabi/issues/488)
- \[YABI-178\] Separation of qsub permanent and qsub temporary errors [\#484](https://github.com/muccg/yabi/issues/484)
- \[YABI-196\] http://pypi.python.org/pypi/django-kombu [\#483](https://github.com/muccg/yabi/issues/483)
- \[YABI-116\] Add ability to run tests from yabictl.sh  [\#482](https://github.com/muccg/yabi/issues/482)
- \[YABI-118\] Remove restart and database initialisation between each nose test [\#481](https://github.com/muccg/yabi/issues/481)
- \[YABI-119\] Login is slow via Yabish adding overhead to tests [\#480](https://github.com/muccg/yabi/issues/480)
- \[YABI-124\] BE + Admin are creating many session files in yabiadmin/scratch [\#479](https://github.com/muccg/yabi/issues/479)
- \[YABI-138\] remove duplicate settings import that creates havoc [\#478](https://github.com/muccg/yabi/issues/478)
- \[YABI-139\] move workflow status call from model up to view alongside job status update call [\#477](https://github.com/muccg/yabi/issues/477)
- \[YABI-141\] improve the be restriction test [\#476](https://github.com/muccg/yabi/issues/476)
- \[YABI-142\] test improvements [\#475](https://github.com/muccg/yabi/issues/475)
- \[YABI-136\] deprecate quickstart [\#474](https://github.com/muccg/yabi/issues/474)
- \[YABI-131\] deprecate fabric [\#473](https://github.com/muccg/yabi/issues/473)
- \[YABI-135\] deprecate grid-ftp [\#472](https://github.com/muccg/yabi/issues/472)
- \[YABI-134\] deprecate globus [\#471](https://github.com/muccg/yabi/issues/471)
- \[YABI-143\] deprecate sql lite usage outside yabistoreapp [\#470](https://github.com/muccg/yabi/issues/470)
- \[YABI-146\] Fix the unit tests in yabiadmin [\#469](https://github.com/muccg/yabi/issues/469)
- \[YABI-152\] Fix yabitests/simple\_tool\_tests to drop the hostname -\> alltools associations it created [\#468](https://github.com/muccg/yabi/issues/468)
- \[YABI-169\] paramiko-ssh.py remote\_unlink not respecting known\_hosts, incorrect parameter order [\#467](https://github.com/muccg/yabi/issues/467)
- \[YABI-168\] verbose logging of task data in Tasklets.py when loading pickled tasks [\#466](https://github.com/muccg/yabi/issues/466)
- \[YABI-132\] Create setup.py and deprecate requirements files [\#465](https://github.com/muccg/yabi/issues/465)
- \[YABI-154\] gevent reactor is external module [\#464](https://github.com/muccg/yabi/issues/464)
- \[YABI-145\] Upgrade celery to 2.5.5 [\#463](https://github.com/muccg/yabi/issues/463)
- \[YABI-187\] latest version of Celery init.d script [\#462](https://github.com/muccg/yabi/issues/462)
- \[YABI-171\] upgrade twisted to 12.3.0 [\#461](https://github.com/muccg/yabi/issues/461)
- \[YABI-174\] Remove hard coded references to /tmp use config variable temp [\#460](https://github.com/muccg/yabi/issues/460)
- \[YABI-133\] create develop.sh script for controlling development stack [\#459](https://github.com/muccg/yabi/issues/459)
- \[YABI-184\] Add simple tool test for ssh ex backend [\#458](https://github.com/muccg/yabi/issues/458)
- \[YABI-191\] BaseShellProcessProtocol and BaseShell are defined three times [\#457](https://github.com/muccg/yabi/issues/457)
- \[YABI-193\] add simple tool test for ssh+pbspro [\#456](https://github.com/muccg/yabi/issues/456)
- \[YABI-197\] Implement retry controller for SSHTorque backend [\#455](https://github.com/muccg/yabi/issues/455)
- \[YABI-194\] add simple tool test for ssh+torque [\#454](https://github.com/muccg/yabi/issues/454)
- \[YABI-203\] escape sequences in shell prompt string kill rewalk tests [\#453](https://github.com/muccg/yabi/issues/453)
- \[YABI-208\] backend unhandled error - stopping before the tasklets have initialised [\#452](https://github.com/muccg/yabi/issues/452)
- \[YABI-214\] Recursive file copy resource does not fall back to manual copy [\#451](https://github.com/muccg/yabi/issues/451)
- \[YABI-213\] paramiko does not pass through std error [\#450](https://github.com/muccg/yabi/issues/450)
- \[YABI-207\] merge backend\_restart\_tests and backend\_execution\_restriction\_tests [\#449](https://github.com/muccg/yabi/issues/449)
- \[YABI-126\] Backend end-to-end test improvements [\#448](https://github.com/muccg/yabi/issues/448)
- \[YABI-272\] Admin - can't delete workflows via admin [\#447](https://github.com/muccg/yabi/issues/447)
- \[YABI-270\] pyOpenSSL==0.12 python2.7 [\#446](https://github.com/muccg/yabi/issues/446)
- \[YABI-254\] Status Errors on SSH+SGE [\#445](https://github.com/muccg/yabi/issues/445)
- \[YABI-182\] SSH+SGE not reporting running state [\#444](https://github.com/muccg/yabi/issues/444)
- \[YABI-222\] request\_next\_task view is inefficient [\#443](https://github.com/muccg/yabi/issues/443)
- \[YABI-250\] Fix Deprecation Warnings for manage.py [\#440](https://github.com/muccg/yabi/issues/440)
- \[YABI-120\] backend nosetests should be moved to top level yabitest directory [\#439](https://github.com/muccg/yabi/issues/439)
- \[YABI-123\] backend is taking a long time to process tasks, tests are slow [\#438](https://github.com/muccg/yabi/issues/438)
- \[YABI-14\] Non-ASCII Unicode characters unsupported in yabi-be-twisted [\#434](https://github.com/muccg/yabi/issues/434)
- \[YABI-95\] Yabi Backend Task request not using http [\#433](https://github.com/muccg/yabi/issues/433)
- \[YABI-199\] Make ssh exec submission scripts report their output/error streams to syslog for debugging [\#432](https://github.com/muccg/yabi/issues/432)
- \[YABI-117\] Backend should post credential errors to Admin [\#431](https://github.com/muccg/yabi/issues/431)
- \[YABI-228\] Monitoring for celery queue [\#430](https://github.com/muccg/yabi/issues/430)
- \[YABI-202\] retry window in config is not respected [\#429](https://github.com/muccg/yabi/issues/429)
- \[YABI-271\] Change Backend logging to respect config file [\#428](https://github.com/muccg/yabi/issues/428)
- \[YABI-127\] Status and Log WS calls to Admin slows down Execution when multiple tasks are running concurrently [\#427](https://github.com/muccg/yabi/issues/427)
- \[YABI-264\] logfile in yabi.conf not honoured if --logfile not passed in on twistd command line [\#426](https://github.com/muccg/yabi/issues/426)
- \[YABI-110\] Job resumption error [\#425](https://github.com/muccg/yabi/issues/425)
- \[YABI-31\] Yabibe - make status page [\#424](https://github.com/muccg/yabi/issues/424)
- \[YABI-400\] yabiadmin/yabiadmin/backend/utils.py:234:1: F821 undefined name 'hostname' [\#422](https://github.com/muccg/yabi/issues/422)
- \[YABI-37\] Yabife - indicate blocked jobs in UI [\#414](https://github.com/muccg/yabi/issues/414)
- \[YABI-97\] backend-credential submission script not used [\#413](https://github.com/muccg/yabi/issues/413)
- \[YABI-175\] FE displays erred workflow as running if worflow erred in build\(\) phase [\#412](https://github.com/muccg/yabi/issues/412)
- \[YABI-125\] Add facility to remove workflow [\#411](https://github.com/muccg/yabi/issues/411)
- \[YABI-195\] SSHTorqueConnector needs to use make\_script \(submission template\) [\#410](https://github.com/muccg/yabi/issues/410)
- \[YABI-276\] LocalEX backend can not run commands with \> [\#409](https://github.com/muccg/yabi/issues/409)
- \[YABI-262\] Summitting a PBSPro job that exceeds resources produces no error [\#408](https://github.com/muccg/yabi/issues/408)
- \[YABI-257\] Make tasks appear as "Queued" not "Unsubmitted" [\#407](https://github.com/muccg/yabi/issues/407)
- \[YABI-52\] Remove or handle file select as options widget [\#406](https://github.com/muccg/yabi/issues/406)
- \[YABI-269\] Yabi User needs search field in Admin [\#398](https://github.com/muccg/yabi/issues/398)
- \[YABI-231\] Can't delete Auth user [\#397](https://github.com/muccg/yabi/issues/397)
- \[YABI-224\] Deleting Tool parameters error [\#396](https://github.com/muccg/yabi/issues/396)
- \[YABI-211\] Admin line in Backend conf requires trailing slash [\#395](https://github.com/muccg/yabi/issues/395)
- \[YABI-77\] Walltime field should be in one unit of time [\#394](https://github.com/muccg/yabi/issues/394)
- \[YABI-98\] Custom file types lost when exporting tools with yabi [\#393](https://github.com/muccg/yabi/issues/393)
- \[YABI-215\] Error deleting some workflows in Admin [\#392](https://github.com/muccg/yabi/issues/392)
- \[YABI-501\] Staging out at the same location [\#383](https://github.com/muccg/yabi/issues/383)
- \[YABI-225\] Template error on Tool View [\#382](https://github.com/muccg/yabi/issues/382)
- \[YABI-545\] When saving a workflow, 'SPAdes wrapper' tool is replaced by 'SPAdes\_3.0.0' tool \(they used the same tool description, SPAdes\_3.0.0\). I have created a new tool description 'SPAdes w' to overcome the issue. [\#374](https://github.com/muccg/yabi/issues/374)
- \[YABI-68\] Error on file upload too verbose when globus cert error [\#373](https://github.com/muccg/yabi/issues/373)
- \[YABI-128\] yabitests config for yabidemo at ccg using wrong test\_data directory [\#372](https://github.com/muccg/yabi/issues/372)
- \[YABI-115\] The tests are broken, slow, have crazy dependencies and generally a hassle to use [\#371](https://github.com/muccg/yabi/issues/371)
- \[YABI-140\] development tests various issues [\#370](https://github.com/muccg/yabi/issues/370)
- \[YABI-137\] yabibe is not using hmac on all calls to admin [\#369](https://github.com/muccg/yabi/issues/369)
- \[YABI-150\] daily log file rotation for yabibe [\#368](https://github.com/muccg/yabi/issues/368)
- \[YABI-148\] Hotfix - SGE Connector is broken. Qstat broken - fall through to qacct [\#367](https://github.com/muccg/yabi/issues/367)
- \[YABI-151\] yabibe respect log file setting in config file [\#366](https://github.com/muccg/yabi/issues/366)
- \[YABI-153\] Test failure - Backend restart test [\#365](https://github.com/muccg/yabi/issues/365)
- \[YABI-167\] tasktools LCopy logging after errors references link, target - copy paste error [\#364](https://github.com/muccg/yabi/issues/364)
- \[YABI-166\] SSHSGEConnector does not define SSHQacctSoftException SSHQacctHardException [\#363](https://github.com/muccg/yabi/issues/363)
- \[YABI-165\] SSHTorqueConnector resume does not define modules [\#362](https://github.com/muccg/yabi/issues/362)
- \[YABI-164\] FileCopyResource attempts to purge copies\_in\_progress with undefined key [\#361](https://github.com/muccg/yabi/issues/361)
- \[YABI-162\] LocalFileSystem rm does not release lock [\#360](https://github.com/muccg/yabi/issues/360)
- \[YABI-160\] geventtools dead code path GETFailed undefined [\#359](https://github.com/muccg/yabi/issues/359)
- \[YABI-157\] geventtools dead code path in \_doFailure, undefined variables [\#358](https://github.com/muccg/yabi/issues/358)
- \[YABI-158\] PEP8 style conventions for yabibe [\#357](https://github.com/muccg/yabi/issues/357)
- \[YABI-161\] Turn debug off by default [\#356](https://github.com/muccg/yabi/issues/356)
- \[YABI-170\] django-kombu is deprecated [\#355](https://github.com/muccg/yabi/issues/355)
- \[YABI-172\] rename yabiadmin url 'error' to 'syslog' to reflect function [\#354](https://github.com/muccg/yabi/issues/354)
- \[YABI-176\] Update yabibe init script for centos [\#353](https://github.com/muccg/yabi/issues/353)
- \[YABI-183\] unit tests for torque backend [\#352](https://github.com/muccg/yabi/issues/352)
- \[YABI-180\] Add torque section to config [\#351](https://github.com/muccg/yabi/issues/351)
- \[YABI-181\] Add simple tool test for torque backend [\#350](https://github.com/muccg/yabi/issues/350)
- \[YABI-185\] ssh ex backend does not capture stdout or stderr [\#349](https://github.com/muccg/yabi/issues/349)
- \[YABI-188\] add ssh+pbspro section to config [\#348](https://github.com/muccg/yabi/issues/348)
- \[YABI-177\] create spec files for Yabi [\#347](https://github.com/muccg/yabi/issues/347)
- \[YABI-256\] Add retry around qstat calls [\#346](https://github.com/muccg/yabi/issues/346)
- \[YABI-210\] S3 backend regression - not listing [\#345](https://github.com/muccg/yabi/issues/345)
- \[YABI-217\] SSHSGEConnector tasklet dies if qacct throws a hard error [\#344](https://github.com/muccg/yabi/issues/344)
- \[YABI-218\] SSHSGEConnector calling qacct directly after qstat can yield missing jobs [\#343](https://github.com/muccg/yabi/issues/343)
- \[YABI-216\] SSHSGEConnector incorrect exception handling [\#342](https://github.com/muccg/yabi/issues/342)
- \[YABI-230\] PBSPro jobs completing but not reported by Yabi [\#341](https://github.com/muccg/yabi/issues/341)
- \[YABI-232\] Error running migration when starting tests:  [\#340](https://github.com/muccg/yabi/issues/340)
- \[YABI-255\] convert add.html [\#316](https://github.com/muccg/yabi/issues/316)
- \[YABI-252\] convert base\_site\_mako.html [\#313](https://github.com/muccg/yabi/issues/313)
- \[YABI-251\] convert base\_mako.html [\#298](https://github.com/muccg/yabi/issues/298)
- \[YABI-259\] Add custom tag to emulate mako ${} python evaluation [\#296](https://github.com/muccg/yabi/issues/296)
- \[YABI-306\] Fix duplicated tab block  [\#287](https://github.com/muccg/yabi/issues/287)
- \[YABI-336\] Credential error after initial unprotect causing error in chain [\#279](https://github.com/muccg/yabi/issues/279)
- \[YABI-344\] If worker dies after db tasks created, workflow errors on worker restart. [\#263](https://github.com/muccg/yabi/issues/263)
- \[YABI-179\] tests for s3 fail - incorrect admin setup [\#259](https://github.com/muccg/yabi/issues/259)
- \[YABI-236\] Add Yabish documentation [\#258](https://github.com/muccg/yabi/issues/258)
- \[YABI-355\] Jobs are not respecting walltime [\#252](https://github.com/muccg/yabi/issues/252)
- \[YABI-359\] Error when calling sshclient  when credential not cached [\#244](https://github.com/muccg/yabi/issues/244)
- \[YABI-149\] SGEConnector - Qstat broken [\#242](https://github.com/muccg/yabi/issues/242)
- \[YABI-335\] LCopy is not supported in SFTPBackend \( throws Assertion errors\) [\#241](https://github.com/muccg/yabi/issues/241)
- \[YABI-417\] Don't calculate and save stagein files destinations at DB creation time. [\#217](https://github.com/muccg/yabi/issues/217)
- \[YABI-433\] Archiving a Workflow and then listing Jobs in the FE causes an error [\#195](https://github.com/muccg/yabi/issues/195)
- \[YABI-263\] Type error on workflow search [\#188](https://github.com/muccg/yabi/issues/188)
- \[YABI-360\] Intermittent 500 error  /files [\#173](https://github.com/muccg/yabi/issues/173)
- \[YABI-121\] There are lot of old bugs on google code, this is they. [\#172](https://github.com/muccg/yabi/issues/172)
- \[YABI-377\] Incorrect Behaviour handling Jobs that fail to submit to cluster [\#171](https://github.com/muccg/yabi/issues/171)
- \[YABI-414\] submission errors are not being fully logged [\#170](https://github.com/muccg/yabi/issues/170)
- \[YABI-471\] Error when trying to upload \*.fa files to Yabi [\#161](https://github.com/muccg/yabi/issues/161)
- \[YABI-461\] .rsa file not being read in properly [\#160](https://github.com/muccg/yabi/issues/160)
- \[YABI-443\] paramiko performance [\#156](https://github.com/muccg/yabi/issues/156)
- \[YABI-462\] Download of large file interrupted after around 1.1GB on ccg.murdoch [\#155](https://github.com/muccg/yabi/issues/155)
- \[YABI-466\] Celery option CELERYD\_FORCE\_EXECV [\#138](https://github.com/muccg/yabi/issues/138)
- \[YABI-493\] Stagein method is always determined as symlink on selectfile tool [\#136](https://github.com/muccg/yabi/issues/136)
- \[YABI-504\] trouble with submission script for the sge schedular, Yabi jobs running on head node [\#129](https://github.com/muccg/yabi/issues/129)
- \[YABI-515\] ccg.murdoch.edu.au YABI not queueing up jobs [\#122](https://github.com/muccg/yabi/issues/122)
- \[YABI-378\] Integrate selenium tests into Bamboo [\#121](https://github.com/muccg/yabi/issues/121)
- \[YABI-376\] Add admin feature file [\#120](https://github.com/muccg/yabi/issues/120)
- \[YABI-372\] Add login feature file [\#119](https://github.com/muccg/yabi/issues/119)
- \[YABI-374\] Add design feature file [\#118](https://github.com/muccg/yabi/issues/118)
- \[YABI-373\] Add jobs feature file [\#117](https://github.com/muccg/yabi/issues/117)
- \[YABI-371\] Add Basic Lettuce Tests to Yabi [\#116](https://github.com/muccg/yabi/issues/116)
- \[YABI-375\] Add account feature file [\#115](https://github.com/muccg/yabi/issues/115)
- \[YABI-514\] Expose R Bioconductor package xcms in Yabi [\#113](https://github.com/muccg/yabi/issues/113)
- \[YABI-513\] Add PyMS Base Line Correction to Yabi [\#112](https://github.com/muccg/yabi/issues/112)
- \[YABI-520\] Celery tasks failing at below Workflow level and above Task level aren't retried at all and Workflow isn't marked as errored [\#110](https://github.com/muccg/yabi/issues/110)
- \[YABI-527\] DirEntry.is\_symlink should be a boolean [\#105](https://github.com/muccg/yabi/issues/105)
- \[YABI-538\] Cannot load old workflows on ccg.murdoch.edu.au/yabi [\#87](https://github.com/muccg/yabi/issues/87)
- \[YABI-561\] workflows will not start [\#74](https://github.com/muccg/yabi/issues/74)
- \[YABI-567\] Trnasfer EGA Downlaod tool [\#55](https://github.com/muccg/yabi/issues/55)
- \[YABI-585\] Switch to boto3 \(from boto\) [\#43](https://github.com/muccg/yabi/issues/43)
- \[YABI-586\] Upgrade to Django 1.8.4 [\#42](https://github.com/muccg/yabi/issues/42)
- \[YABI-583\] Run "yabi checksecure" on the servers and make sure it passes all checks [\#41](https://github.com/muccg/yabi/issues/41)
- \[YABI-558\] CCGAPPS YABi - Apps do not load in design view [\#37](https://github.com/muccg/yabi/issues/37)
- \[YABI-599\] Remove Yabi's dependency on the yaphc project [\#29](https://github.com/muccg/yabi/issues/29)
- \[YABI-600\] Make yaphc an internal module of yabish [\#28](https://github.com/muccg/yabi/issues/28)
- \[YABI-606\] Yabi workflows not running- pending since ~May 2 [\#22](https://github.com/muccg/yabi/issues/22)
- \[YABI-144\] upgrade django to 1.3.7 [\#21](https://github.com/muccg/yabi/issues/21)
- \[YABI-189\] Inconsistent exception/error handling killing ssh+xxx tasklets  [\#20](https://github.com/muccg/yabi/issues/20)
- \[YABI-192\] PBSPro jobs disappear from queue, no status change in admin [\#19](https://github.com/muccg/yabi/issues/19)
- \[YABI-156\] Acknowledge code from twisted [\#18](https://github.com/muccg/yabi/issues/18)
- \[YABI-529\] Fix Michael Blacks EPIC yabi credentials [\#13](https://github.com/muccg/yabi/issues/13)
- \[YABI-539\] Jobs do not load, old workflows not available [\#12](https://github.com/muccg/yabi/issues/12)
- \[YABI-129\] Change the code in SSH+PBSPro to work with the new code [\#9](https://github.com/muccg/yabi/issues/9)
- \[YABI-212\] SSH+SGE regression - incorrect remote temporary directory [\#8](https://github.com/muccg/yabi/issues/8)
- \[YABI-464\] ccgapps.com.au yabi adding user is not functioning properly [\#7](https://github.com/muccg/yabi/issues/7)

## [9.9.2](https://github.com/muccg/yabi/tree/9.9.2) (2016-04-08)
[Full Changelog](https://github.com/muccg/yabi/compare/9.9.1...9.9.2)

**Closed issues:**

- \[YABI-605\] Remove all python \* imports [\#25](https://github.com/muccg/yabi/issues/25)
- \[YABI-604\] The addtool form to add JSON tools fails on CSRF verification [\#24](https://github.com/muccg/yabi/issues/24)
- \[YABI-603\] Change tool description- Tool output extensions is not deleting correctly [\#23](https://github.com/muccg/yabi/issues/23)

## [9.9.1](https://github.com/muccg/yabi/tree/9.9.1) (2016-02-17)
[Full Changelog](https://github.com/muccg/yabi/compare/9.9.0...9.9.1)

**Closed issues:**

- \[YABI-601\] Add custom command to add users from the command line [\#27](https://github.com/muccg/yabi/issues/27)
- \[YABI-602\] Add csrf token to admin views [\#26](https://github.com/muccg/yabi/issues/26)

## [9.9.0](https://github.com/muccg/yabi/tree/9.9.0) (2016-02-16)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.5...9.9.0)

## [9.8.5](https://github.com/muccg/yabi/tree/9.8.5) (2016-02-10)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.4...9.8.5)

**Closed issues:**

- \[YABI-597\] Remove unused CCG SSL middleware settings [\#31](https://github.com/muccg/yabi/issues/31)
- \[YABI-598\] Upgrade pykerberos to 1.1.10 to fix upstream bug [\#30](https://github.com/muccg/yabi/issues/30)

## [9.8.4](https://github.com/muccg/yabi/tree/9.8.4) (2016-01-19)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.3...9.8.4)

**Closed issues:**

- \[YABI-595\] S3 directories are url encoded with boto3 [\#35](https://github.com/muccg/yabi/issues/35)
- \[YABI-594\] Empty file with the same name as the directory is returned when listing a directory on S3 [\#34](https://github.com/muccg/yabi/issues/34)
- \[YABI-593\] File upload to S3 fails for empty files [\#33](https://github.com/muccg/yabi/issues/33)

## [9.8.3](https://github.com/muccg/yabi/tree/9.8.3) (2016-01-19)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.2...9.8.3)

**Closed issues:**

- \[YABI-592\] yabish over HTTPS fails CSRF validation [\#36](https://github.com/muccg/yabi/issues/36)

## [9.8.2](https://github.com/muccg/yabi/tree/9.8.2) (2016-01-15)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.1...9.8.2)

**Closed issues:**

- \[YABI-591\] Upgrade Django and other packages to their latest version [\#32](https://github.com/muccg/yabi/issues/32)

## [9.8.1](https://github.com/muccg/yabi/tree/9.8.1) (2015-11-12)
[Full Changelog](https://github.com/muccg/yabi/compare/9.8.0...9.8.1)

**Closed issues:**

- \[YABI-590\] Receiving 'Fail on submit!' message when submitting yabi jobs [\#6](https://github.com/muccg/yabi/issues/6)

## [9.8.0](https://github.com/muccg/yabi/tree/9.8.0) (2015-10-12)
[Full Changelog](https://github.com/muccg/yabi/compare/9.7.0...9.8.0)

**Closed issues:**

- \[YABI-587\] Add CSRF protection to Yabi [\#40](https://github.com/muccg/yabi/issues/40)
- \[YABI-588\] Enable clickjacking protection in Yabi [\#39](https://github.com/muccg/yabi/issues/39)
- \[YABI-589\] Upgrade to Django 1.8.5 [\#38](https://github.com/muccg/yabi/issues/38)

## [9.7.0](https://github.com/muccg/yabi/tree/9.7.0) (2015-09-05)
[Full Changelog](https://github.com/muccg/yabi/compare/9.6.0...9.7.0)

**Closed issues:**

- \[YABI-584\] S3 Upload file improvements [\#47](https://github.com/muccg/yabi/issues/47)
- \[YABI-581\] Improve LDAP get\_user\(\) error if more than one object matches [\#46](https://github.com/muccg/yabi/issues/46)
- \[YABI-582\] In some LDAP setups the group membership attribute could contain the username not the user DN [\#45](https://github.com/muccg/yabi/issues/45)
- \[YABI-580\] Tools in Tool Grouping Admin page should be ordered [\#44](https://github.com/muccg/yabi/issues/44)

## [9.6.0](https://github.com/muccg/yabi/tree/9.6.0) (2015-08-17)
[Full Changelog](https://github.com/muccg/yabi/compare/9.5.1...9.6.0)

**Closed issues:**

- \[YABI-573\] Tool's View JSON link is broken [\#54](https://github.com/muccg/yabi/issues/54)
- \[YABI-574\] Access to Tools \(/ws/tool/\) should alway be allowed for admins [\#53](https://github.com/muccg/yabi/issues/53)
- \[YABI-575\] Make timezone settable from yabi.conf [\#52](https://github.com/muccg/yabi/issues/52)
- \[YABI-576\] Improve error messages if authentication backends aren't configured properly [\#51](https://github.com/muccg/yabi/issues/51)
- \[YABI-577\] Upgrade to Django 1.8.3 [\#50](https://github.com/muccg/yabi/issues/50)
- \[YABI-578\] LDAP group membership should be definable on the User object as well [\#49](https://github.com/muccg/yabi/issues/49)
- \[YABI-579\] Change license to GNU Affero GPL [\#48](https://github.com/muccg/yabi/issues/48)

## [9.5.1](https://github.com/muccg/yabi/tree/9.5.1) (2015-07-07)
[Full Changelog](https://github.com/muccg/yabi/compare/9.5.0...9.5.1)

**Closed issues:**

- \[YABI-571\] Recursive local copy on SFTP doesn't behave like cp source\_dir/\* dest\_dir [\#57](https://github.com/muccg/yabi/issues/57)
- \[YABI-570\] Delete QueuedWorkflow model from db [\#56](https://github.com/muccg/yabi/issues/56)
- \[YABI-568\] File I/O in Magnus creates unwated 'output' folder [\#11](https://github.com/muccg/yabi/issues/11)
- \[YABI-569\] CCGAPPS YABI - Jobs do not progress [\#10](https://github.com/muccg/yabi/issues/10)

## [9.5.0](https://github.com/muccg/yabi/tree/9.5.0) (2015-06-26)
[Full Changelog](https://github.com/muccg/yabi/compare/9.4.0...9.5.0)

**Closed issues:**

- \[YABI-551\] Don't poll Workflow anymore after Workflow finished [\#73](https://github.com/muccg/yabi/issues/73)
- \[YABI-549\] User abort and delete their own workflows [\#72](https://github.com/muccg/yabi/issues/72)
- \[YABI-553\] Toolsets should be based on tools not tool descriptions [\#71](https://github.com/muccg/yabi/issues/71)
- \[YABI-554\] Support for Univa Grid Engine [\#70](https://github.com/muccg/yabi/issues/70)
- \[YABI-556\] Local copy in sftp backends doesn't work for many files [\#69](https://github.com/muccg/yabi/issues/69)
- \[YABI-555\] Update docs with how to set up users for successful execution on backends [\#68](https://github.com/muccg/yabi/issues/68)
- \[YABI-440\] Reuse Workflow URL accessible by all users [\#67](https://github.com/muccg/yabi/issues/67)
- \[YABI-557\] Allow users to share their workflows for reuse by other users  [\#66](https://github.com/muccg/yabi/issues/66)
- \[YABI-559\] Add support for Kerberos authentification [\#65](https://github.com/muccg/yabi/issues/65)
- \[YABI-560\] Replace and improve ccg\_auth LDAP auth  [\#64](https://github.com/muccg/yabi/issues/64)
- \[YABI-562\] Tools created by default \(quickstart\) should allow symlinking and local copy [\#63](https://github.com/muccg/yabi/issues/63)
- \[YABI-441\] Review security in frontend WSs [\#62](https://github.com/muccg/yabi/issues/62)
- \[YABI-563\] Don't try to symlink stageins on Backends that don't support it [\#61](https://github.com/muccg/yabi/issues/61)
- \[YABI-564\] Implement temporary solution to avoid changes on next release breaking running workflows [\#60](https://github.com/muccg/yabi/issues/60)
- \[YABI-565\] "Workflow running, waiting for completion" message doesn't disappear for completed workflow [\#59](https://github.com/muccg/yabi/issues/59)
- \[YABI-566\] django-secure [\#58](https://github.com/muccg/yabi/issues/58)

## [9.4.0](https://github.com/muccg/yabi/tree/9.4.0) (2015-02-03)
[Full Changelog](https://github.com/muccg/yabi/compare/9.3.0...9.4.0)

**Closed issues:**

- \[YABI-548\] Support for SLURM backends [\#78](https://github.com/muccg/yabi/issues/78)
- \[YABI-547\] Return 404 when downloading files that don't exist instead of 500 [\#77](https://github.com/muccg/yabi/issues/77)

## [9.3.0](https://github.com/muccg/yabi/tree/9.3.0) (2015-01-15)
[Full Changelog](https://github.com/muccg/yabi/compare/9.2.0...9.3.0)

**Closed issues:**

- \[YABI-502\] Select multiple files to upload  [\#80](https://github.com/muccg/yabi/issues/80)
- \[YABI-546\] model error in on\_job\_finished [\#79](https://github.com/muccg/yabi/issues/79)

## [9.2.0](https://github.com/muccg/yabi/tree/9.2.0) (2014-11-19)
[Full Changelog](https://github.com/muccg/yabi/compare/9.1.2...9.2.0)

**Closed issues:**

- \[YABI-238\] Inform users when mandatory options are missing during design [\#487](https://github.com/muccg/yabi/issues/487)
- \[YABI-62\] Allow hrefs in tool descriptions [\#486](https://github.com/muccg/yabi/issues/486)
- \[YABI-26\] Yabish - add support for optional positional arguments [\#485](https://github.com/muccg/yabi/issues/485)
- \[YABI-38\] Lowercase Yabi usernames [\#375](https://github.com/muccg/yabi/issues/375)
- \[YABI-543\]  add-tool interface broken, missing path key [\#86](https://github.com/muccg/yabi/issues/86)
- \[YABI-544\] Upgrade to Django 1.6.x [\#85](https://github.com/muccg/yabi/issues/85)
- \[YABI-342\] Re-implement Backends."Tasks per User" feature [\#84](https://github.com/muccg/yabi/issues/84)
- \[YABI-542\] Yabish - support redirect [\#83](https://github.com/muccg/yabi/issues/83)
- \[YABI-540\] When workflows are re-used, selected files disappear [\#82](https://github.com/muccg/yabi/issues/82)
- \[YABI-541\] Design window sometimes blank  [\#81](https://github.com/muccg/yabi/issues/81)

## [9.1.2](https://github.com/muccg/yabi/tree/9.1.2) (2014-09-24)
[Full Changelog](https://github.com/muccg/yabi/compare/9.0.1...9.1.2)

**Closed issues:**

- \[YABI-72\] Keep track of filetype through generic tool [\#491](https://github.com/muccg/yabi/issues/491)
- \[YABI-247\] Centralise log management [\#376](https://github.com/muccg/yabi/issues/376)
- \[YABI-535\] Admin view User's Tools doesn't show the same tools as the FE menu [\#91](https://github.com/muccg/yabi/issues/91)
- \[YABI-13\] Some characters are disallowed in file names [\#90](https://github.com/muccg/yabi/issues/90)
- \[YABI-537\] Add support for filenames including Unicode characters [\#89](https://github.com/muccg/yabi/issues/89)
- \[YABI-536\] Upgrade Yabi's dependencies [\#88](https://github.com/muccg/yabi/issues/88)

## [9.0.1](https://github.com/muccg/yabi/tree/9.0.1) (2014-09-03)
[Full Changelog](https://github.com/muccg/yabi/compare/8.0.0...9.0.1)

**Closed issues:**

- \[YABI-253\] Not supplying password for private key gives misleading message [\#377](https://github.com/muccg/yabi/issues/377)
- \[YABI-528\] Terminate Dynamic Backends even if tasks got aborted or errored [\#99](https://github.com/muccg/yabi/issues/99)
- \[YABI-523\] Don't mandate creating Backend Credentials for Null Backends [\#98](https://github.com/muccg/yabi/issues/98)
- \[YABI-532\] OpenStack support for Dynamic Backends [\#97](https://github.com/muccg/yabi/issues/97)
- \[YABI-533\] Display last login of Yabi users in Admin [\#96](https://github.com/muccg/yabi/issues/96)
- \[YABI-530\] Previewing of files makes Yabi hang many times  [\#94](https://github.com/muccg/yabi/issues/94)
- \[YABI-495\] Separate tool definitions from tools to make them easily reusable for multiple backends [\#93](https://github.com/muccg/yabi/issues/93)
- \[YABI-367\] Add back test backend link and fix test backend code [\#92](https://github.com/muccg/yabi/issues/92)

## [8.0.0](https://github.com/muccg/yabi/tree/8.0.0) (2014-08-13)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.7...8.0.0)

**Closed issues:**

- \[YABI-526\] Update Yabi documentation [\#104](https://github.com/muccg/yabi/issues/104)
- \[YABI-524\] Switch from django.utils.simplejson to Python's json module [\#103](https://github.com/muccg/yabi/issues/103)
- \[YABI-522\] Change all SSH tests to use the same test SSH key [\#102](https://github.com/muccg/yabi/issues/102)
- \[YABI-521\] Improve Syslog \(DB\) logger to log even if a DB error happened before [\#101](https://github.com/muccg/yabi/issues/101)
- \[YABI-399\] Add support for Dynamic Backends [\#100](https://github.com/muccg/yabi/issues/100)

## [7.2.7](https://github.com/muccg/yabi/tree/7.2.7) (2014-07-31)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.6...7.2.7)

**Closed issues:**

- \[YABI-518\] Don't lose workflow when navigating away from design tab [\#111](https://github.com/muccg/yabi/issues/111)
- \[YABI-370\] New Yabi option to save workflows without running [\#109](https://github.com/muccg/yabi/issues/109)
- \[YABI-519\] Design tab - "drag tools here" element inconsistencies [\#108](https://github.com/muccg/yabi/issues/108)
- \[YABI-517\] Get rid of the concept of local remnant directory [\#107](https://github.com/muccg/yabi/issues/107)
- \[YABI-516\] Add a config param to be able to set the niceness of the celeryd workers [\#106](https://github.com/muccg/yabi/issues/106)

## [7.2.6](https://github.com/muccg/yabi/tree/7.2.6) (2014-06-26)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.5...7.2.6)

**Closed issues:**

- \[YABI-510\] Add ability to mark tool parameters as sensitive [\#114](https://github.com/muccg/yabi/issues/114)

## [7.2.5](https://github.com/muccg/yabi/tree/7.2.5) (2014-06-20)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.4...7.2.5)

**Closed issues:**

- \[YABI-507\] No logs on production Yabi  [\#381](https://github.com/muccg/yabi/issues/381)
- \[YABI-503\] Importing tools - common and fe\_rank fe\_rank not being carried over [\#380](https://github.com/muccg/yabi/issues/380)
- \[YABI-113\] When a tool is disabled, it appears 'broken' in the front end [\#379](https://github.com/muccg/yabi/issues/379)
- \[YABI-511\] Front page: Give initial keyboard focus to login form [\#378](https://github.com/muccg/yabi/issues/378)
- \[YABI-505\] File extension support for a set of characters [\#128](https://github.com/muccg/yabi/issues/128)
- \[YABI-506\] LDAP settings uses wrong module [\#127](https://github.com/muccg/yabi/issues/127)
- \[YABI-496\] Display retry count on Tasks [\#126](https://github.com/muccg/yabi/issues/126)
- \[YABI-508\] If submit\_workflow fails return an error JSON response instead of Internal Server Error [\#125](https://github.com/muccg/yabi/issues/125)
- \[YABI-509\] Upgrade celery and related packages [\#123](https://github.com/muccg/yabi/issues/123)

## [7.2.4](https://github.com/muccg/yabi/tree/7.2.4) (2014-05-30)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.3...7.2.4)

**Closed issues:**

- \[YABI-489\] Make first link in engine workflow admin show summary [\#386](https://github.com/muccg/yabi/issues/386)
- \[YABI-88\] Form validation for Tool parameter possible values [\#385](https://github.com/muccg/yabi/issues/385)
- \[YABI-498\] Install yabish in /opt, install symlink in /usr/bin [\#384](https://github.com/muccg/yabi/issues/384)
- \[YABI-494\] Make the filesystem LS webservice of unexisting files behave consistently across Backends [\#135](https://github.com/muccg/yabi/issues/135)
- \[YABI-490\] When workflows are re-used keep the selected file arguments \(if valid\) [\#134](https://github.com/muccg/yabi/issues/134)
- \[YABI-492\] Use simple config file for settings \(ccgplatform 1.10\) [\#132](https://github.com/muccg/yabi/issues/132)
- \[YABI-499\] Ensure logging from yabiadmin.\* packages get written the celery log file [\#131](https://github.com/muccg/yabi/issues/131)
- \[YABI-500\] LocalFS symlink should fail if target doesn't exist [\#130](https://github.com/muccg/yabi/issues/130)

## [7.2.3](https://github.com/muccg/yabi/tree/7.2.3) (2014-05-08)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.2...7.2.3)

**Closed issues:**

- \[YABI-487\] Celery user gets removed on RPM upgrade [\#389](https://github.com/muccg/yabi/issues/389)
- \[YABI-454\] Re-implement download directory as zipped file functionality [\#388](https://github.com/muccg/yabi/issues/388)
- \[YABI-488\] Delete the temp files created on clusters to submit, poll, and abort jobs [\#387](https://github.com/muccg/yabi/issues/387)
- \[YABI-486\] Improve backend/credential usability in admin [\#140](https://github.com/muccg/yabi/issues/140)
- \[YABI-60\] Tool Parameter order in Frontend [\#137](https://github.com/muccg/yabi/issues/137)
- \[YABI-58\] Introduce the concept of commonly used tool parameters in the Frontend [\#14](https://github.com/muccg/yabi/issues/14)

## [7.2.2](https://github.com/muccg/yabi/tree/7.2.2) (2014-04-17)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.1...7.2.2)

**Closed issues:**

- \[YABI-476\] Make rpm install the celery-flower init script  [\#154](https://github.com/muccg/yabi/issues/154)
- \[YABI-477\] Make MySQL case-sensitive by default [\#153](https://github.com/muccg/yabi/issues/153)
- \[YABI-474\] Optimise the loading of Tools on the Design tab [\#152](https://github.com/muccg/yabi/issues/152)
- \[YABI-478\] Disallow FS Backends LocalLink and Symlink for Backends that don't support them \(ex. S3\) [\#151](https://github.com/muccg/yabi/issues/151)
- \[YABI-479\] Clean up VALID\_SCHEMES in yabiadmin.constants and drop it from settings [\#150](https://github.com/muccg/yabi/issues/150)
- \[YABI-475\] Switch to postgres by default, make it clear that we suggest it over MySQL [\#149](https://github.com/muccg/yabi/issues/149)
- \[YABI-480\] Make a python logging handler that logs to yabiengine.Syslog [\#148](https://github.com/muccg/yabi/issues/148)
- \[YABI-482\] Add a Celery Task that removes Syslog rows of Workflows that completed successfully [\#147](https://github.com/muccg/yabi/issues/147)
- \[YABI-484\] Change the YabiDBHandler to log tracebacks too if logger.exception\(msg\) has been called [\#146](https://github.com/muccg/yabi/issues/146)
- \[YABI-481\] Log more with the new Contextual Loggers so we get log messages in yabiengine.Syslog [\#145](https://github.com/muccg/yabi/issues/145)
- \[YABI-444\] Swift storage backend [\#144](https://github.com/muccg/yabi/issues/144)
- \[YABI-485\] Update docs and admin helptexes with information about Swift [\#143](https://github.com/muccg/yabi/issues/143)
- \[YABI-483\] Add error handling for FS backend upload/download/copy [\#142](https://github.com/muccg/yabi/issues/142)
- \[YABI-324\] Fix dangling FIFOs [\#141](https://github.com/muccg/yabi/issues/141)

## [7.2.1](https://github.com/muccg/yabi/tree/7.2.1) (2014-04-03)
[Full Changelog](https://github.com/muccg/yabi/compare/7.2.0...7.2.1)

**Closed issues:**

- \[YABI-467\] Add celery flower to installation, remove django-celery [\#167](https://github.com/muccg/yabi/issues/167)
- \[YABI-463\] Create init.d script to start up celery flower [\#166](https://github.com/muccg/yabi/issues/166)
- \[YABI-469\] Remove unused CCG util dependencies [\#165](https://github.com/muccg/yabi/issues/165)
- \[YABI-468\] Deleting an Auth User on AWS \(staging and live\) throws an Error [\#164](https://github.com/muccg/yabi/issues/164)
- \[YABI-470\] Remove unused yabiadmin/registration Django app [\#163](https://github.com/muccg/yabi/issues/163)
- \[YABI-460\] SSLMiddleware is copied into Yabi, use it from ccg-django-utils instead [\#162](https://github.com/muccg/yabi/issues/162)
- \[YABI-473\] Next= not working properly when connection times out in FE [\#159](https://github.com/muccg/yabi/issues/159)
- \[YABI-465\] Celery Caveats - Long running tasks [\#158](https://github.com/muccg/yabi/issues/158)
- \[YABI-472\] "Error loading file listing" FE error is displayed for jobs that aren't completed yet [\#157](https://github.com/muccg/yabi/issues/157)

## [7.2.0](https://github.com/muccg/yabi/tree/7.2.0) (2014-03-24)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.10...7.2.0)

**Closed issues:**

- \[YABI-219\] ?next= not working post login [\#503](https://github.com/muccg/yabi/issues/503)
- \[YABI-455\] Yabi is logging almost each log entry twice in the log files [\#502](https://github.com/muccg/yabi/issues/502)
- \[YABI-235\] Enable previsualization of a large fasta file using 'head -50' [\#403](https://github.com/muccg/yabi/issues/403)
- \[YABI-221\] Add tool - extension param drop down needs ordering [\#402](https://github.com/muccg/yabi/issues/402)
- \[YABI-220\] Admin - add filetype [\#401](https://github.com/muccg/yabi/issues/401)
- \[YABI-227\] S3 Backend - cannot copy directory [\#400](https://github.com/muccg/yabi/issues/400)
- \[YABI-237\] Change YABI\_DEFAULT\_URL to something sensible [\#399](https://github.com/muccg/yabi/issues/399)
- \[YABI-445\] S3 backend deletes using prefix [\#186](https://github.com/muccg/yabi/issues/186)
- \[YABI-435\] Remove the "Archive Workflow" functionality [\#185](https://github.com/muccg/yabi/issues/185)
- \[YABI-452\] Remove download zipped directory functionality as it is broken in the File Browser [\#184](https://github.com/muccg/yabi/issues/184)
- \[YABI-453\] Remove deprecated views from yabiengine that were used by the old BE [\#183](https://github.com/muccg/yabi/issues/183)
- \[YABI-350\] Remove deprecated hmac authentication [\#182](https://github.com/muccg/yabi/issues/182)
- \[YABI-351\] Remove tasktag [\#181](https://github.com/muccg/yabi/issues/181)
- \[YABI-369\] New Yabi option to select directory / file [\#180](https://github.com/muccg/yabi/issues/180)
- \[YABI-451\] Deleting a symlink to a directory in the File Browser errors [\#179](https://github.com/muccg/yabi/issues/179)
- \[YABI-352\] Review VALID\_SCHEMES in settings.py [\#178](https://github.com/muccg/yabi/issues/178)
- \[YABI-442\] Show confirmation dialog in the File Browser before deleting files/directories [\#177](https://github.com/muccg/yabi/issues/177)
- \[YABI-449\] Make a separate Celery queue for copying files [\#176](https://github.com/muccg/yabi/issues/176)
- \[YABI-458\] Downgrade paramiko to 1.12.1 [\#175](https://github.com/muccg/yabi/issues/175)
- \[YABI-457\] YABI create new or change existing Celery init scripts to start up two sets of workers [\#174](https://github.com/muccg/yabi/issues/174)
- \[YABI-432\] Upgrade to Celery 3.1.9 [\#169](https://github.com/muccg/yabi/issues/169)
- \[YABI-459\] Use Python 2.7 in development and RPM [\#168](https://github.com/muccg/yabi/issues/168)

## [7.1.10](https://github.com/muccg/yabi/tree/7.1.10) (2014-02-28)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.9...7.1.10)

**Closed issues:**

- \[YABI-439\] remove reference to crate.io in spec file [\#415](https://github.com/muccg/yabi/issues/415)
- \[YABI-434\] Make local execution use the command submission template for execution [\#194](https://github.com/muccg/yabi/issues/194)
- \[YABI-436\] "Workflow/Job errored, Yabi is retrying" message isn't cleared if Yabi gives up on retrying and errors [\#193](https://github.com/muccg/yabi/issues/193)
- \[YABI-447\] Create RetryPollingException and drop the TYPE and BACKOFF\_STRATEGY\_ fields from RetryException [\#192](https://github.com/muccg/yabi/issues/192)
- \[YABI-446\] Put the celerytasks.retry\_on\_error decorator function under tests and refactor it [\#191](https://github.com/muccg/yabi/issues/191)
- \[YABI-438\] use https in dependency links in yabish [\#190](https://github.com/muccg/yabi/issues/190)
- \[YABI-437\] SSH+SGE backend doesn't allow qstat path to be configured [\#189](https://github.com/muccg/yabi/issues/189)

## [7.1.9](https://github.com/muccg/yabi/tree/7.1.9) (2014-02-13)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.8...7.1.9)

**Closed issues:**

- \[YABI-424\] Fix up old reference to Google Code on the main login page [\#513](https://github.com/muccg/yabi/issues/513)
- \[YABI-423\] Fix copyright year and inconsistency on all pages [\#512](https://github.com/muccg/yabi/issues/512)
- \[YABI-428\] Provide some indication to the user if there is some problem \(Celery is retrying on some error\) with their Workflow [\#210](https://github.com/muccg/yabi/issues/210)
- \[YABI-429\] Add Tooltips for status icons in the Frontend [\#201](https://github.com/muccg/yabi/issues/201)
- \[YABI-427\] "Workflow running, waiting for completion" message doesn't disappear after Workflow completes [\#200](https://github.com/muccg/yabi/issues/200)
- \[YABI-426\] Selecting a directory as a job's input param raises an exception in create\_db\_tasks [\#199](https://github.com/muccg/yabi/issues/199)
- \[YABI-425\] Files selected as Tool options directly from the file browser \(ie. not coming from another job\) doesn't get added to the command line [\#198](https://github.com/muccg/yabi/issues/198)
- \[YABI-430\] Upgrade to paramiko 1.12.1 [\#197](https://github.com/muccg/yabi/issues/197)
- \[YABI-431\] Upgrade to boto 2.25 [\#196](https://github.com/muccg/yabi/issues/196)

## [7.1.8](https://github.com/muccg/yabi/tree/7.1.8) (2014-01-30)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.7...7.1.8)

**Closed issues:**

- \[YABI-421\] Remove unused six.moves.zip imports and make sure six.moves.map didn't cause any issues [\#213](https://github.com/muccg/yabi/issues/213)
- \[YABI-422\] Aborting of workflows works, but a logging statement throws an exception [\#212](https://github.com/muccg/yabi/issues/212)
- \[YABI-397\] Optimise SFTP copying of large number of small files [\#211](https://github.com/muccg/yabi/issues/211)

## [7.1.7](https://github.com/muccg/yabi/tree/7.1.7) (2014-01-16)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.6...7.1.7)

**Closed issues:**

- \[YABI-420\] When copying a directory using the File Browser only the nested files inside are copied [\#216](https://github.com/muccg/yabi/issues/216)
- \[YABI-419\] Yabi should preserve file modification time when copying files [\#215](https://github.com/muccg/yabi/issues/215)
- \[YABI-418\] Tools can't be added to Tool Grouping [\#214](https://github.com/muccg/yabi/issues/214)

## [7.1.6](https://github.com/muccg/yabi/tree/7.1.6) (2013-12-21)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.5-2...7.1.6)

**Closed issues:**

- \[YABI-413\] Run all the tests \(end-to-end and unit tests\) on "./develop.sh test\_X" commands [\#416](https://github.com/muccg/yabi/issues/416)
- \[YABI-415\] set SESSION\_COOKIE\_HTTPONLY by default [\#219](https://github.com/muccg/yabi/issues/219)
- \[YABI-416\] preview sanitizer accepts URLs with the javascript pseudo protocol [\#218](https://github.com/muccg/yabi/issues/218)

## [7.1.5-2](https://github.com/muccg/yabi/tree/7.1.5-2) (2013-12-11)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.5...7.1.5-2)

## [7.1.5](https://github.com/muccg/yabi/tree/7.1.5) (2013-12-11)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.4...7.1.5)

**Closed issues:**

- \[YABI-403\] yabiadmin/yabiadmin/backend/s3backend.py:112:1: F821 undefined name 'RuntimeException' [\#421](https://github.com/muccg/yabi/issues/421)
- \[YABI-402\] undefined name 'self' [\#420](https://github.com/muccg/yabi/issues/420)
- \[YABI-401\] yabiadmin/yabiadmin/backend/utils.py:188:1: F841 local variable 'host\_keys' is assigned to but never used [\#419](https://github.com/muccg/yabi/issues/419)
- \[YABI-409\] Write a mini-DSL to test Backend parsers [\#418](https://github.com/muccg/yabi/issues/418)
- \[YABI-405\] Error templates not displaying correctly. [\#417](https://github.com/muccg/yabi/issues/417)
- \[YABI-408\] Torque qstat parser incorrect when multiple job entries are returned [\#225](https://github.com/muccg/yabi/issues/225)
- \[YABI-404\] Broken Symlinks in a dir make the ls on the dir fail [\#224](https://github.com/muccg/yabi/issues/224)
- \[YABI-398\] Credential double-encryption [\#223](https://github.com/muccg/yabi/issues/223)
- \[YABI-410\] Yabi encryption security improvement [\#222](https://github.com/muccg/yabi/issues/222)
- \[YABI-411\] Incorrect credential breaking other credentials [\#221](https://github.com/muccg/yabi/issues/221)
- \[YABI-412\] Error in backend.clean\_up\_task\(\) when trying to get credential [\#220](https://github.com/muccg/yabi/issues/220)

## [7.1.4](https://github.com/muccg/yabi/tree/7.1.4) (2013-12-02)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.3...7.1.4)

**Closed issues:**

- \[YABI-395\] Change Backends to be Job Array aware [\#227](https://github.com/muccg/yabi/issues/227)
- \[YABI-394\] Add dynamic environment variables to command submission templates [\#226](https://github.com/muccg/yabi/issues/226)

## [7.1.3](https://github.com/muccg/yabi/tree/7.1.3) (2013-11-13)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.2...7.1.3)

**Closed issues:**

- \[YABI-388\] Create migrations for the on\_delete=models.SET\_NULL changes made in yabiadmin.yabi models in May 2012 [\#390](https://github.com/muccg/yabi/issues/390)
- \[YABI-392\] Job status could be set to complete despite having aborted tasks [\#233](https://github.com/muccg/yabi/issues/233)
- \[YABI-390\] Workflow status is never set to 'running', jumps from 'ready' to terminating status [\#232](https://github.com/muccg/yabi/issues/232)
- \[YABI-389\] Workflow status not updated to 'complete' when all jobs completed [\#231](https://github.com/muccg/yabi/issues/231)
- \[YABI-386\] Make ssh exec\_script upload the script we run to TMPDIR before executing it [\#230](https://github.com/muccg/yabi/issues/230)
- \[YABI-387\] Make ssh exec\_script return the scripts exit code in addition to stdout and stderr [\#229](https://github.com/muccg/yabi/issues/229)
- \[YABI-391\] Job will be marked as completed if some task are aborted and some completed [\#228](https://github.com/muccg/yabi/issues/228)

## [7.1.2](https://github.com/muccg/yabi/tree/7.1.2) (2013-11-06)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.1...7.1.2)

**Closed issues:**

- \[YABI-384\] Implement abort of jobs for Torque Backends [\#237](https://github.com/muccg/yabi/issues/237)
- \[YABI-383\] Implement abort of jobs for SGE Backends [\#236](https://github.com/muccg/yabi/issues/236)
- \[YABI-382\] Implement abort of jobs for PBS Pro Backends [\#235](https://github.com/muccg/yabi/issues/235)
- \[YABI-385\] String Job Param value containing the substring 'type' is interpreted as dictionary and causes TypeError [\#234](https://github.com/muccg/yabi/issues/234)

## [7.1.1](https://github.com/muccg/yabi/tree/7.1.1) (2013-10-17)
[Full Changelog](https://github.com/muccg/yabi/compare/7.1.0...7.1.1)

**Closed issues:**

- \[YABI-304\] Make tasks, jobs and workflows abortable [\#423](https://github.com/muccg/yabi/issues/423)
- \[YABI-381\] Fix logging deprecation warning for mail\_admins handler [\#240](https://github.com/muccg/yabi/issues/240)
- \[YABI-379\] Change SSH Backend submission to start commands in the background and don't wait for them to complete [\#239](https://github.com/muccg/yabi/issues/239)
- \[YABI-380\] Implement Lcopy and Link for SFTP Backend [\#238](https://github.com/muccg/yabi/issues/238)

## [7.1.0](https://github.com/muccg/yabi/tree/7.1.0) (2013-09-26)
[Full Changelog](https://github.com/muccg/yabi/compare/7.0.0...7.1.0)

**Closed issues:**

- \[YABI-366\] Drag'n'Drop in the file browser is broken [\#247](https://github.com/muccg/yabi/issues/247)
- \[YABI-223\] Upgrade Yabi to Django 1.5.4 [\#246](https://github.com/muccg/yabi/issues/246)
- \[YABI-365\] Add backend for Amazon S3 [\#245](https://github.com/muccg/yabi/issues/245)
- \[YABI-248\] Remove dependency on Mako templates [\#243](https://github.com/muccg/yabi/issues/243)

## [7.0.0](https://github.com/muccg/yabi/tree/7.0.0) (2013-09-19)
[Full Changelog](https://github.com/muccg/yabi/compare/6.15.1...7.0.0)

**Closed issues:**

- \[YABI-233\] Remove print statements from YabiAdmin [\#514](https://github.com/muccg/yabi/issues/514)
- \[YABI-240\] changes for beautifulsoup4 [\#442](https://github.com/muccg/yabi/issues/442)
- \[YABI-239\] Upgrade remaining dependencies in yabiadmin [\#441](https://github.com/muccg/yabi/issues/441)
- \[YABI-331\] Default tool "cat" is failing to load [\#437](https://github.com/muccg/yabi/issues/437)
- \[YABI-338\] give remote job meaningful name  [\#436](https://github.com/muccg/yabi/issues/436)
- \[YABI-345\] Make tests run on gunicorn but use runserver\_plus for development [\#435](https://github.com/muccg/yabi/issues/435)
- \[YABI-245\] Error resolving url for /favicon.ico  [\#339](https://github.com/muccg/yabi/issues/339)
- \[YABI-234\]  Error importing template source loader ccg.template.loaders.makoloader.filesystem.Loader [\#338](https://github.com/muccg/yabi/issues/338)
- \[YABI-229\] Error importing middleware ccg.middleware.ssl [\#337](https://github.com/muccg/yabi/issues/337)
- \[YABI-249\] Failing test: ERROR: test\_user\_creation \(yabiadmin.yabi.tests.CreateUserFromAdminTest\) [\#336](https://github.com/muccg/yabi/issues/336)
- \[YABI-258\] convert login.httml [\#335](https://github.com/muccg/yabi/issues/335)
- \[YABI-278\] convert yabi 404.html [\#334](https://github.com/muccg/yabi/issues/334)
- \[YABI-279\] convert yabi 500.html [\#333](https://github.com/muccg/yabi/issues/333)
- \[YABI-282\] convert noprofile.txt [\#332](https://github.com/muccg/yabi/issues/332)
- \[YABI-283\] convert yabifeapp 401.html [\#331](https://github.com/muccg/yabi/issues/331)
- \[YABI-285\] convert yabi fe 403.html  [\#330](https://github.com/muccg/yabi/issues/330)
- \[YABI-286\] convert yabi fe 404.html [\#329](https://github.com/muccg/yabi/issues/329)
- \[YABI-287\] convert yabi fe app 500.html [\#328](https://github.com/muccg/yabi/issues/328)
- \[YABI-289\] convert yabi fe app preview\_unavailable.html [\#327](https://github.com/muccg/yabi/issues/327)
- \[YABI-290\] convert registration email approve.txt [\#326](https://github.com/muccg/yabi/issues/326)
- \[YABI-291\] convert yabi fe registration email approved.txt [\#325](https://github.com/muccg/yabi/issues/325)
- \[YABI-292\] convert yabi fe app registration email confirm.txt [\#324](https://github.com/muccg/yabi/issues/324)
- \[YABI-294\] convert yabi fe registration confirm.html [\#323](https://github.com/muccg/yabi/issues/323)
- \[YABI-295\] convert yabi fe app registration index.html [\#322](https://github.com/muccg/yabi/issues/322)
- \[YABI-288\] convert yabi fe app base.html [\#321](https://github.com/muccg/yabi/issues/321)
- \[YABI-297\] convert yabi fe app base.html [\#320](https://github.com/muccg/yabi/issues/320)
- \[YABI-302\] convert fe feapp jobs.html [\#319](https://github.com/muccg/yabi/issues/319)
- \[YABI-281\] Add "\<% import " custom tag to import module and add to current context [\#318](https://github.com/muccg/yabi/issues/318)
- \[YABI-303\] Template Syntax Load Test [\#317](https://github.com/muccg/yabi/issues/317)
- \[YABI-260\] convert admin\_status [\#315](https://github.com/muccg/yabi/issues/315)
- \[YABI-261\] convert backend.html [\#314](https://github.com/muccg/yabi/issues/314)
- \[YABI-266\] convert crypt\_password.html [\#312](https://github.com/muccg/yabi/issues/312)
- \[YABI-268\] convert ldap\_not\_in\_use.html [\#311](https://github.com/muccg/yabi/issues/311)
- \[YABI-265\] convert backend\_cred\_test.html [\#310](https://github.com/muccg/yabi/issues/310)
- \[YABI-273\] convert ldap\_users.html [\#309](https://github.com/muccg/yabi/issues/309)
- \[YABI-274\] convert tool.html [\#308](https://github.com/muccg/yabi/issues/308)
- \[YABI-275\] convert user\_backends.html [\#307](https://github.com/muccg/yabi/issues/307)
- \[YABI-277\] convert user\_tools.html [\#306](https://github.com/muccg/yabi/issues/306)
- \[YABI-280\] convert workflow\_summary.html [\#305](https://github.com/muccg/yabi/issues/305)
- \[YABI-293\] convert yabi fe app registration email denied.txt [\#304](https://github.com/muccg/yabi/issues/304)
- \[YABI-296\] convert yabi fe app registration success.html  [\#303](https://github.com/muccg/yabi/issues/303)
- \[YABI-298\] convert yabi fe feapp account.html [\#302](https://github.com/muccg/yabi/issues/302)
- \[YABI-300\] convert yabi fe feapp design.html [\#301](https://github.com/muccg/yabi/issues/301)
- \[YABI-301\] convert yabi feapp files.html [\#300](https://github.com/muccg/yabi/issues/300)
- \[YABI-299\] convert yabi fe feapp admin.html [\#299](https://github.com/muccg/yabi/issues/299)
- \[YABI-305\] fix template loading [\#297](https://github.com/muccg/yabi/issues/297)
- \[YABI-307\] Fix profile reference in account template [\#295](https://github.com/muccg/yabi/issues/295)
- \[YABI-308\] remove comments from base [\#294](https://github.com/muccg/yabi/issues/294)
- \[YABI-310\] Fix css load error on account page [\#293](https://github.com/muccg/yabi/issues/293)
- \[YABI-312\] Fix show dev warning on login [\#292](https://github.com/muccg/yabi/issues/292)
- \[YABI-311\] Fix Javascript error on account page [\#291](https://github.com/muccg/yabi/issues/291)
- \[YABI-317\] Change after review - remove all py tag method calls if possible [\#290](https://github.com/muccg/yabi/issues/290)
- \[YABI-309\] make copyright an include [\#289](https://github.com/muccg/yabi/issues/289)
- \[YABI-313\] Changes After Code Review [\#288](https://github.com/muccg/yabi/issues/288)
- \[YABI-316\] Changes after review - fix to status colour method access in work flow summary template [\#286](https://github.com/muccg/yabi/issues/286)
- \[YABI-319\] Complete Status updates for new backend [\#285](https://github.com/muccg/yabi/issues/285)
- \[YABI-320\] Make Celery Tasks Idempotent [\#284](https://github.com/muccg/yabi/issues/284)
- \[YABI-323\] Refactor walk to prevent concurrent running of same tasks [\#283](https://github.com/muccg/yabi/issues/283)
- \[YABI-325\] Refactor ls parse code [\#282](https://github.com/muccg/yabi/issues/282)
- \[YABI-329\] Create Torque backend [\#281](https://github.com/muccg/yabi/issues/281)
- \[YABI-334\] Front end is not indicating failed workflow when job submission fails [\#280](https://github.com/muccg/yabi/issues/280)
- \[YABI-330\] Create PBS Pro backend [\#278](https://github.com/muccg/yabi/issues/278)
- \[YABI-337\] Refactor ssh exec backends \( SGE , Torque and PBS Pro \) [\#277](https://github.com/muccg/yabi/issues/277)
- \[YABI-333\] STDERR being lost on epic jobs [\#276](https://github.com/muccg/yabi/issues/276)
- \[YABI-332\] Fix workaround \(key written to temp file\) in sshclient [\#275](https://github.com/muccg/yabi/issues/275)
- \[YABI-327\] Rename the celery tasks to describe what they are doing [\#274](https://github.com/muccg/yabi/issues/274)
- \[YABI-326\] Make creation of tasks work on a job not instead of a workflow [\#273](https://github.com/muccg/yabi/issues/273)
- \[YABI-322\] Make all celery tasks that work on yabi tasks consistent in retry behaviour [\#272](https://github.com/muccg/yabi/issues/272)
- \[YABI-321\] Review transaction management in new BE [\#271](https://github.com/muccg/yabi/issues/271)
- \[YABI-314\] Make all ERROR level log messages show up in console and mailed to admin [\#270](https://github.com/muccg/yabi/issues/270)
- \[YABI-328\] Create SGE Exec Backend [\#269](https://github.com/muccg/yabi/issues/269)
- \[YABI-341\] Qsub  submission error stream not being logged [\#268](https://github.com/muccg/yabi/issues/268)
- \[YABI-339\] Module load problem  [\#267](https://github.com/muccg/yabi/issues/267)
- \[YABI-340\] Temporarily ignore  lcopy and link flags  in  backends [\#266](https://github.com/muccg/yabi/issues/266)
- \[YABI-343\] Remove backend execution restriction tests for now [\#265](https://github.com/muccg/yabi/issues/265)
- \[YABI-226\] Upgrade celery to 3.0.22 [\#264](https://github.com/muccg/yabi/issues/264)
- \[YABI-347\] Replace subprocess.Popen.wait\(\) calls with subprocess.Popen.communicate\(\) [\#262](https://github.com/muccg/yabi/issues/262)
- \[YABI-346\] Job Name too long causes  submission error  [\#261](https://github.com/muccg/yabi/issues/261)
- \[YABI-349\] Exception previewing file on remote backend [\#260](https://github.com/muccg/yabi/issues/260)
- \[YABI-353\] Make sftp.mkdir in sftpbackend work like mkdir -p [\#257](https://github.com/muccg/yabi/issues/257)
- \[YABI-354\] Show Task id in Admin and provide direct link to Workflow from Task [\#256](https://github.com/muccg/yabi/issues/256)
- \[YABI-356\] qsub and qstat are assumed to be in the path of remote user account [\#255](https://github.com/muccg/yabi/issues/255)
- \[YABI-358\] Error stream of qsub on SchedulerExecBackend is not logged [\#254](https://github.com/muccg/yabi/issues/254)
- \[YABI-357\] TypeError concatenating tuple and list when selecting file and running blast [\#253](https://github.com/muccg/yabi/issues/253)
- \[YABI-362\] fsbackend.remote\_copy failing for nested directories [\#251](https://github.com/muccg/yabi/issues/251)
- \[YABI-363\] Make all exceptioning tasks retry [\#250](https://github.com/muccg/yabi/issues/250)
- \[YABI-361\] Remove RetryException for polling from logs [\#249](https://github.com/muccg/yabi/issues/249)
- \[YABI-364\] Error rendering commandlinetemplate: KeyError accessing batchfiles dictionary [\#248](https://github.com/muccg/yabi/issues/248)
- \[YABI-284\] Switch from gunicorn to Werkzeug based web server in DEV [\#17](https://github.com/muccg/yabi/issues/17)
- \[YABI-315\] Rewrite backend using message queue [\#16](https://github.com/muccg/yabi/issues/16)
- \[YABI-348\] Update readme.txt for next\_release [\#15](https://github.com/muccg/yabi/issues/15)



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*