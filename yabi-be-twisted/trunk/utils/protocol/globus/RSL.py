# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-

PRINT_RSL = False

def RSL( **kws ):
    kws['argument_block']="".join(["  <argument>%s</argument>\n"%ARG for ARG in kws['args']])
    kws['module_block']="".join(["   <module>%s</module>\n"%ARG for ARG in kws['modules']])
    rsl = """<?xml version="1.0"?>
<job>
  <executable>%(command)s</executable>
  <directory>%(directory)s</directory>
%(argument_block)s  <stdout>%(stdout)s</stdout>
  <stderr>%(stderr)s</stderr>
  <count>%(cpus)d</count>
  <queue>%(queue)s</queue>
  <maxWallTime>%(maxWallTime)s</maxWallTime>
  <maxMemory>%(maxMemory)d</maxMemory>
  <jobType>%(jobType)s</jobType>
  <extensions>
%(module_block)s
  </extensions>

</job>
"""%(kws)
    return rsl

def ConstructRSL(
    address = 'https://xe-gt4.ivec.org:8443/wsrf/services/ManagedJobFactoryService',
    command = None,
    args = [],
    directory = "/tmp",
    stdout = "/dev/null",
    stderr = "/dev/null",
    maxWallTime = "60:00:00",
    maxMemory = 1024,
    cpus = 1,
    queue = "testing",
    jobType = "single",
    modules = []):
    return RSL(address=address, command=command, args=args, directory=directory, stdout=stdout, stderr=stderr, maxWallTime=maxWallTime, maxMemory=maxMemory, cpus=cpus, queue=queue, jobType=jobType, modules=modules)
    
import tempfile
def writersltofile(rsl):
    """Takes an rsl and writes it into a temporary file. Returns the filename"""
    fh = tempfile.NamedTemporaryFile(suffix=".rsl", delete=False)
    fh.write(rsl)
    fh.close()
    
    if PRINT_RSL:
        print "RSL"
        print "============="
        print rsl
        print "============="
    
    return fh.name

                                    