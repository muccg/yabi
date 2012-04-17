import sys
import utils
import settings
import os
import subprocess


def get_db():
    rdbms_name = utils.detect_rdbms()
    if rdbms_name == 'sqlite':
        return SqliteDB()
    elif rdbms_name == 'postgres':
        return PostgresDB()
    elif rdbms_name == 'mysql':
        return MySQLDB()
    else:
        raise StandardError("You are using an unknown RDBMS")

def touch(fname, times = None):
    with file(fname, 'a'):
        os.utime(fname, times)

class DB(object):
    def __init__(self, rdbms_name):
        self.rdbms_name = rdbms_name
        self.dbsettings = settings.DATABASES['default']

    def dropdb(self):
        raise NotImplementedError()

    def createdb(self):
        raise NotImplementedError()

    def recreatedb(self):
        self.dropdb()
        self.createdb()

class SqliteDB(DB):
    def __init__(self, *args, **kwargs):
        DB.__init__(self, 'sqlite', *args, **kwargs)
        self.filename = self.dbsettings['NAME']
        
    def dropdb(self):
        print 'Unlinking ' + self.filename
        os.unlink(self.filename) 

    def createdb(self):
        print 'Touching ' + self.filename
        touch(self.filename)

class PostgresDB(DB):
    def __init__(self, *args, **kwargs):
        DB.__init__(self, 'postgres', *args, **kwargs)
        self.dbname = self.dbsettings['NAME']
        self.user = self.dbsettings['USER']

    def psql_command(self):
        command = 'psql'
        if self.dbsettings['USER']:
            command += " -U " + self.dbsettings['USER']
        if self.dbsettings['HOST']:
            command += " -h " + self.dbsettings['HOST']
        if self.dbsettings['PORT']:
            command += " -p " + self.dbsettings['PORT']
        if self.dbsettings['PASSWORD']:
            command = "PGPASSWORD=" + self.dbsettings['PASSWORD'] + " " + command
        command += ' postgres'
        return command
        
    def dropdb(self):
        command = ('echo "DROP DATABASE IF EXISTS %s" | ' % self.dbname) + self.psql_command() 
        os.system(command)

    def createdb(self):
        command = ('echo "CREATE DATABASE %s OWNER %s" | ' % (self.dbname, self.user)) + self.psql_command()
        os.system(command)


class MySQLDB(DB):
    def __init__(self, *args, **kwargs):
        DB.__init__(self, 'mysql', *args, **kwargs)
        self.dbname = self.dbsettings['NAME']
        self.hostname = self.dbsettings['HOST']
        self.user = self.dbsettings['USER']

    def mysql_command(self):
        command = 'mysql'
        db = self.dbsettings.get('NAME')
        user = self.dbsettings.get('USER')
        passwd = self.dbsettings.get('PASSWORD')
        host = self.dbsettings.get('HOST')
        port = self.dbsettings.get('PORT')
        defaults_file = self.dbsettings.get('read_default_file')
  
        if defaults_file:
            command += " --defaults-file=%s" % defaults_file
        if user:
            command += " --user=%s" % user
        if passwd:
            command += " --password=%s" % passwd
        if host:
            if '/' in host:
               command += " --socket=%s" % host
            else:
               command += " --host=%s" % host
        if port:
            command += " --port=%s" % port
        return command
   

    def createdb(self):
        create_command = ('echo "create database %s default charset=UTF8" | ' % self.dbname) + self.mysql_command()
        grant_command = ('echo "grant all privileges on %s.* to %s@%s" | ' % (self.dbname, self.user, self.hostname)) + self.mysql_command()
        os.system(create_command)
        # TODO doesn't work, revisit
        #os.system(grant_command)

    def dropdb(self):
        command = ('echo "drop database if exists %s" | ' % self.dbname) + self.mysql_command()
        os.system(command)


def main():
    VALID_ARGS = ('dropdb', 'createdb', 'recreatedb')
    if len(sys.argv) != 2:
        print "Please specify one of %s as argument" % ", ".join(VALID_ARGS)
        return

    arg = sys.argv[1]
    if arg not in VALID_ARGS:
        print "Only one of %s can be used as argument" % ", ".join(VALID_ARGS)
        return

    db = get_db()
    getattr(db, arg)() 

if __name__ == "__main__":
    main()

