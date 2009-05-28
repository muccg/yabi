import os, os.path, sys, fnmatch

install_prefix = "/tmp"

##
## SVN utils
##
import xml.dom.minidom

def Subversion(env=None):
    if env:
        return env.WhereIs('svn')
    else:
        return os.popen('/usr/bin/which svn').read().strip()


def SubversionReposInfo():
    subversion = Subversion()
    if subversion:
        dom = xml.dom.minidom.parseString(
            os.popen('%s info --xml .' % subversion).read())
        e = dom.getElementsByTagName('entry')[0]
        package_repository_version = int(e.getAttribute('revision'))
        package_repository_url = dom.getElementsByTagName('url')[0].childNodes[0].data
        package_repository_root = dom.getElementsByTagName('root')[0].childNodes[0].data
        package_repository_uuid = dom.getElementsByTagName('uuid')[0].childNodes[0].data
        
        dom.unlink()
        
    return {    'version':package_repository_version, 
                'url':package_repository_url, 
                'root':package_repository_root, 
                'uuid':package_repository_uuid
            }

def SvnPathToTags(path):
    """Given an svn path, return the svn path to the associated tags directory for this repository project.
    It does this by searching the path for 'trunk', and changes that to 'tags' and returns that path
    """
    # forward and reverse list
    parts = path.split('/')
    rparts = parts[:]
    rparts.reverse()
    
    # work back from the tail until we find the 'trunk' item
    for bit in rparts:
        if bit=="trunk":
            parts.pop()
            return "/".join(parts+['tags'])
        else:
            parts.pop()
    
    return None
        
def SvnTagName(path):
    """Given an svn path, return the tag we are in, or None if not in a tag dir
    """
    # forward and reverse list
    parts = path.split('/')
    
    if "tags" not in parts:
        return None
    
    return parts[parts.index("tags")+1]
        

        
def SubversionList(path):
    subversion = Subversion()
    if subversion:
        command = '%s list %s --xml' % (subversion,path)
        dom = xml.dom.minidom.parseString(os.popen(command).read())
        entries = dom.getElementsByTagName('entry')
        out=[]
        for entry in entries:
            name = entry.getElementsByTagName('name')[0].childNodes[0].data
            author = entry.getElementsByTagName('author')[0].childNodes[0].data
            date = entry.getElementsByTagName('date')[0].childNodes[0].data
            revision = int(entry.getElementsByTagName('commit')[0].getAttribute('revision'))
            out.append( (revision, name, author, date) )
        
        out.sort()
        return out

##
## Recursive funcs
##
def GetFiles(env, dir, includes, excludes=None):
      files = []
      for file in os.listdir(env.Dir(dir).srcnode().abspath):
          for pattern in includes:
             if fnmatch.fnmatchcase(file, pattern):
                 files.append(file)
      if not excludes is None:
        for file in files:
           for pattern in excludes:
              if fnmatch.fnmatchcase(file, pattern):
                  files.remove(file)
      return files

def InstallFiles(env, dest_dir, src_dir, includes, excludes):
   src = GetFiles(env, src_dir, includes, excludes)
   #print "x=" + `src`
   dest = env.Dir(dest_dir)
   result = []
   for f in src:
      result.append(env.InstallPerm(env, dest, src_dir + '/' + f, 0664))
   return result

def RecursiveInstallFiles(env, dest_dir, src_dir, includes, excludes):
    """Recursively install all the source directories into dest in the same direectory hierachy"""
    #print "RIF",env,dest_dir,src_dir,includes,excludes,"..."
    parts = os.listdir( str(src_dir) )           # all the files and directories in this directory
    installer = []
    
    installer.extend(InstallFiles(env, dest_dir, src_dir, includes, excludes))
    
    # recurse into directories
    for part in parts:
        if os.path.isdir(os.path.join(str(src_dir),part)) and part not in excludes and part!="tmp":
            results = RecursiveInstallFiles(env, os.path.join(str(dest_dir),part), os.path.join(str(src_dir),part), includes, excludes)
            installer += results
    
    #print [str(s) for s in installer]
    return installer

def InstallTree(env, dest_dir, src_dir, includes, excludes):
    destnode = env.Dir(dest_dir)
    dirs = []
    dirs.append(src_dir)
    while len(dirs) > 0:
      currdir = dirs.pop(0)
      currdestdir = dest_dir + currdir[len(src_dir):]
      #print "c=" + currdestdir
      flist = os.listdir(currdir)
      for currfile in flist:
         currpath = currdir + '/' + currfile
         match = 0
         for pattern in includes:
            if fnmatch.fnmatchcase(currfile, pattern):
              match = 1
         if (match == 1):
            for pattern in excludes:
               if fnmatch.fnmatchcase(currfile, pattern):
                  match = 0
            if (match == 1):
               if (os.path.isdir(currpath)):
                  #print "d=" + currpath
                  dirs.append(currpath)
               else:
                  #print "f=" + currpath
                  env.Install(currdestdir, currpath)
      #print "x= len=" + str(len(dirs))
    return destnode

##
## CCG stuff
##
def virtual_python(target, source, env):
    """Installs virtual python in target, then easy install, then each requested egg"""
    for t in target:
        # install virtual python
        command = 'python  virtual-python.py --no-site-packages --prefix=%s' % (t)
        print command
        print os.popen(command).read()
        
        # install ez_setup
        pythonbin = os.path.join(str(t),"bin","python")
        command = '%s ez_setup.py' % (pythonbin)
        print command
        print os.popen(command).read()
        
        # install each egg
        pythonbin = os.path.join(str(t),"bin","easy_install")
        for egg in source:
            command = '%s %s' % (pythonbin,egg)
            print command
            print os.popen(command).read()
        
    return None

def apache_wsgi_file(target, source, env):
    """Writes into the target WSGI file, the relevant commands"""
    source = source[0]
    for t in target:
        fname = os.path.basename(str(t))
        base,tag = fname.rsplit(":",1)          # base is the project name. tag is the release tag, or 'trunk' or 'release'
        
        fh = open(str(t),'w')
        fh.write("WSGIScriptAlias /%s/%s %s/%s/%s/%s/%s\n"%(base,tag,install_prefix,base,tag,base,source))
        fh.close()
        
    return None
    
def apache_alias_file(target, source, env):
    """Writes into the target WSGI file, the relevant commands. sources are our server directories"""
    SUFFIX = "-aliases"
    for t in target:
        assert str(t).endswith(SUFFIX)
        fname = os.path.basename(str(t))[:-len(SUFFIX)]
        base,tag = fname.rsplit(":",1)          # base is the project name. tag is the release tag, or 'trunk' or 'release'
        
        fh = open(str(t),'w')
        for s in source:
            fh.write("Alias /%s/%s/%s %s/%s/%s/%s/%s\n"%(base,tag,s,install_prefix,base,tag,base,s))
        fh.close()
        
    return None
    
    
def symlink(target, source, env):
    """Note: target is the symlink itself
    source is what it points at"""
    src = str(source[0])
    for t in target:
        prefix = os.path.commonprefix([os.path.dirname(str(src)),os.path.dirname(str(t))]) + "/"
        source = str(src)[len(prefix):]
        os.symlink(source,str(t))
        
    return None
    
def InstallPerm(env, dest, files, perm):
    obj = env.Install(dest, files)
    for i in obj:
        env.AddPostAction(i, env.Chmod(str(i), perm))
    return dest

##
## Build our environment
##
def EnvironmentFactory( env, Builder, environ ):
    vpb = Builder(action=virtual_python)
    awb = Builder(action=apache_wsgi_file)
    apa = Builder(action=apache_alias_file)
    slb = Builder(action=symlink)
    e = env( ENV = environ, BUILDERS = { 'VirtualPython':vpb, "ApacheWSGI":awb, "ApacheAlias":apa, "SymLink":slb } )
    import SCons
    e.Chmod = SCons.Action.ActionFactory(os.chmod, lambda dest, mode: 'Chmod("%s", 0%o)' % (dest, mode))
    e.InstallPerm = InstallPerm
    return e
