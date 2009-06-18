from CertificateProxy import CertificateProxy
import GlobusURLCopy
import GlobusRun
import Jobs

# module level "singletons"
Copy = GlobusURLCopy.GlobusURLCopy()
Run = GlobusRun.GlobusRun()

def _deprecated_RSL( **kws ):
    return """<?xml version="1.0"?>
<job>
  <factoryEndpoint xmlns:gram="http://www.globus.org/namespaces/2004/10/gram/job" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing">
    <wsa:Address>%(address)s</wsa:Address>
    <wsa:ReferenceProperties>
      <gram:ResourceID>PBS</gram:ResourceID>
    </wsa:ReferenceProperties>
  </factoryEndpoint>
  <executable>%(command)s</executable>
  <directory>%(directory)s</directory>
  <stdout>%(stdout)s</stdout>
  <stderr>%(stderr)s</stderr>
  <count>%(cpus)d</count>
  <queue>%(queue)s</queue>
  <maxWallTime>%(maxWallTime)d</maxWallTime>
  <maxMemory>%(maxMemory)d</maxMemory>
  <jobType>%(jobType)s</jobType>
</job>
"""%(kws)

def RSL( **kws ):
    kws['argument_block']="".join(["  <argument>%s</argument>\n"%ARG for ARG in kws['args']])
    return """<?xml version="1.0"?>
<job>
  <executable>%(command)s</executable>
  <directory>%(directory)s</directory>
%(argument_block)s  <stdout>%(stdout)s</stdout>
  <stderr>%(stderr)s</stderr>
  <count>%(cpus)d</count>
  <queue>%(queue)s</queue>
  <maxWallTime>%(maxWallTime)d</maxWallTime>
  <maxMemory>%(maxMemory)d</maxMemory>
  <jobType>%(jobType)s</jobType>
</job>
"""%(kws)

def ConstructRSL(
    address = 'https://xe-ng2.ivec.org:8443/wsrf/services/ManagedJobFactoryService',
    command = None,
    args = [],
    directory = "/tmp",
    stdout = "/dev/null",
    stderr = "/dev/null",
    maxWallTime = 60,
    maxMemory = 1024,
    cpus = 1,
    queue = "testing",
    jobType = "single"):
    return RSL(address=address, command=command, args=args, directory=directory, stdout=stdout, stderr=stderr, maxWallTime=maxWallTime, maxMemory=maxMemory, cpus=cpus, queue=queue, jobType=jobType)
    
import tempfile
def writersltofile(rsl):
    """Takes an rsl and writes it into a temporary file. Returns the filename"""
    fh = tempfile.NamedTemporaryFile(suffix=".rsl", delete=False)
    fh.write(rsl)
    fh.close()
    
    print "RSL"
    print "============="
    print rsl
    print "============="
    
    return fh.name

                                    