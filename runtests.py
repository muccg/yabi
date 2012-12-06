import os, subprocess

def tests(dryrun=False):
    '''Run end to end YABI tests in the yabitests project'''
    cmd = "nosetests -v"
    if dryrun:
        cmd += " --collect-only"
    _virtualenv('virt_yabiadmin', cmd)

def _virtualenv(project, command):
    with lcd('yabitests'):
        print command
        local("source ../%s/bin/activate && %s" % (project, command))


# Run a command emulating fabric's local()
def local(command):
    subprocess.call(command, stderr=subprocess.STDOUT, shell=True)

# Context manager to switch to a directory like fab's lcd()
class lcd():
    def __init__(self, local_directory):
        self.local_directory = local_directory
    def __enter__(self):
        self.return_directory = os.getcwd()
        os.chdir(self.local_directory)
    def __exit__(self, type, value, traceback):
        os.chdir(self.return_directory)  

# Make this module runnable and behave as if it was run via fabric
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2: sys.exit(1)
    operation = sys.argv[1]
    kwargs = {}
    if ':' in sys.argv[1]:
        (operation, args) = operation.split(':')
        kwargs = dict(item.split("=") if '=' in item else (item,True) for item in args.split(","))
        print "Running:", operation, kwargs
        locals()[operation](kwargs)
    else:
        print "Running:", operation
        locals()[operation]()
    
    