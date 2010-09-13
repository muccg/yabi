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

                                    