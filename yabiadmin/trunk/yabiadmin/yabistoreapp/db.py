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
"""
Support library to create and access the users personal history database
"""

import sqlite3, os
from datetime import datetime as datetime

try:
    import json
except ImportError, ie:
    import simplejson as json

import settings

USERS_HOME = settings.YABISTORE_HOME
    
HISTORY_FILE = "history.sqlite3"

DB_CREATE = """
CREATE TABLE "yabistoreapp_tag" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "value" varchar(255) NOT NULL UNIQUE
)
;
CREATE TABLE "yabistoreapp_workflow" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(255) NOT NULL,
    "json" text NOT NULL,
    "last_modified_on" datetime,
    "created_on" datetime NOT NULL,
    "archived_on" datetime NOT NULL,
    "status" text NOT NULL
)
;
CREATE TABLE "yabistoreapp_workflowtag" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "workflow_id" integer NOT NULL REFERENCES "yabistoreapp_workflow" ("id"),
    "tag_id" integer NOT NULL REFERENCES "yabistoreapp_tag" ("id")
)
;
CREATE INDEX "yabistoreapp_workflowtag_workflow_id" ON "yabistoreapp_workflowtag" ("workflow_id");
CREATE INDEX "yabistoreapp_workflowtag_tag_id" ON "yabistoreapp_workflowtag" ("tag_id");
"""

VALID_USERNAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.@"

WORKFLOW_VARS = ['id','name','json','last_modified_on','created_on','status']
WORKFLOW_QUERY_LINE = "id,name,json,date(last_modified_on),date(created_on),status"

##
## Errors
##
class NoSuchWorkflow(Exception): pass

def user_fs_home(username):
    """Return users home directory path. creates it if it doesn't exist"""
    
    # sanity check username. Just to catch any problems that might rise defesively
    assert False not in [c in VALID_USERNAME_CHARS for c in username], "Invalid username '%s'"%username
    
    dir = os.path.join(USERS_HOME,username)
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir

def create_user_db(username):
    """Create the sqlite database to store the users history in"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    for command in DB_CREATE.split(';'):
        c.execute(command)
    conn.commit()
    c.close()

    # now chmod the file to make it writable by celeryd
    # TODO: Fix this permissions issue. Celeryd is running as user and yabiadmin is running as 'apache' and both need to write to this database
    #os.chmod(db,0777)                   # we need to write to the file as another user
    #os.chmod(home,0777)                 # AND we need to write to the directory as another user for the -journal sqlite file

    # these should no longer be needed as celeryd should not be writing directly to the sqlite file, only admin should (remove these lines at a later time)
    
    
def ensure_user_db(username):
    """if the users db doesn't exist, create it"""
    if not does_db_exist(username):
        create_user_db(username)
    
def does_db_exist(username):
    """does the users database exist. 0 byte files don't count"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    if not os.path.exists(db):
        return False
    
    st = os.stat(db)
    if not st.st_size:
        # zero size
        os.unlink(db)
        return False
    
    return True

def does_workflow_exist(username, **kwargs):
    assert len(kwargs) == 1
    assert kwargs.keys()[0] in ('id', 'name')
    ensure_user_db(username)

    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
        
    conn = sqlite3.connect(db)
    c = conn.cursor()

    field = kwargs.keys()[0]
    c.execute('SELECT * FROM yabistoreapp_workflow WHERE %s = ?' % field,
              (kwargs[field],))
    data = c.fetchall()

    c.close()
    return (len(data) >= 1)

def workflow_names_starting_with(username, base):
    ensure_user_db(username)

    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
        
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('SELECT name FROM yabistoreapp_workflow WHERE name like ?',
              (base + '%',))
    result = [r[0] for r in c]

    c.close()
    return result
   
    
def save_workflow(username, workflow, taglist=[]):
    """place a row in the workflow table"""
    ensure_user_db(username)
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
   
    c = conn.cursor()
    c.execute('INSERT INTO "yabistoreapp_workflow" ' +
            '(id, name, json, status, created_on, last_modified_on, archived_on) ' +
            'VALUES (?,?,?,?,?,?,julianday("now"))',
            (workflow.id, workflow.name, workflow.json, workflow.status, workflow.created_on, workflow.last_modified_on))
        
    for tag in taglist:
        # see if the tag already exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        
        if len(data)==0:
            c.execute('INSERT INTO "yabistoreapp_tag" (value) VALUES (?)',(tag,) )
        
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, last_insert_rowid())', (workflow.id,))
        else:
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, ?)', (workflow.id,data[0][0]))
    
    conn.commit()
    c.close()

def change_workflow_tags(username, id, taglist=None):
    """Change the tags of a given workflow"""
    ensure_user_db(username)
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    if taglist is not None:
        c.execute("""SELECT DISTINCT yabistoreapp_tag.value 
                    FROM yabistoreapp_workflowtag, yabistoreapp_tag 
                    WHERE yabistoreapp_tag.id = yabistoreapp_workflowtag.tag_id 
                    AND yabistoreapp_workflowtag.workflow_id = ?""", (id,) )
    
        oldtaglist=[]
        for row in c:
            oldtaglist.append(row[0])
            
        # delete the old taglist
        detag_workflow(username, id, oldtaglist, cursor=c)
        
        # now add the new taglist in
        tag_workflow(username, id, taglist, cursor=c)
        
    conn.commit()
    c.close()
    
def tag_workflow(username,workflow_id,taglist=[], cursor=None):
    """add tags to an existing workflow"""
    ensure_user_db(username)
    if cursor is None:
        home = user_fs_home(username)
        db = os.path.join(home, HISTORY_FILE)
        
        conn = sqlite3.connect(db)
        
        c = conn.cursor()
    else:
        c = cursor
        conn = None
        
    c.execute('SELECT * FROM yabistoreapp_workflow WHERE id=?',(workflow_id,))
    
    data = c.fetchall()
    
    # check for no workflow
    if len(data)==0:
        raise NoSuchWorkflow, "Workflow id %d not found for user %s"%(workflow_id,username)
    
    for tag in taglist:
        # see if the tag already exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        
        if len(data)==0:
            c.execute('INSERT INTO "yabistoreapp_tag" (value) VALUES (?)',(tag,) )
        
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, last_insert_rowid())', (workflow_id,))
        else:
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, ?)', (workflow_id,data[0][0]))
        
    if conn is not None:
        conn.commit()
        c.close()
    
def detag_workflow(username, workflow_id, taglist=[], delete_empty=True, cursor=None):
    """Unlinks the list of tags from a workflow.
    if delete_empty is True (default), then the tag will be deleted if it tags nothing
    """
    ensure_user_db(username)
    if cursor is None:
        home = user_fs_home(username)
        db = os.path.join(home, HISTORY_FILE)
        
        conn = sqlite3.connect(db)
        
        c = conn.cursor()
    else:
        c = cursor
        conn = None
        
    c.execute('SELECT * FROM yabistoreapp_workflow WHERE id=?',(workflow_id,))
    
    data = c.fetchall()
    
    # check for no workflow
    if len(data)==0:
        raise NoSuchWorkflow, "Workflow id %d not found for user %s"%(workflow_id,username)
    
    
    for tag in taglist:
        # see if the tag  exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()

        if len(data)==1:
            tag_id = data[0][0]
            # delete any many to many links
            c.execute('DELETE FROM yabistoreapp_workflowtag WHERE workflow_id = ? AND tag_id = ?', (workflow_id, tag_id) )
            
            if delete_empty:
                # is the tag now empty
                c.execute('SELECT count() FROM yabistoreapp_workflowtag WHERE yabistoreapp_workflowtag.tag_id = ?',(tag_id,))
                data = c.fetchall()
        
                if data[0][0]==0:
                    # no more tag links left. delete.
                    c.execute('DELETE FROM yabistoreapp_tag WHERE id = ?',(tag_id,))
        
    if conn is not None:
        conn.commit()
        c.close()
            
def get_tags_for_workflow(username, id, cursor=None):
    ensure_user_db(username)
    if cursor is None:
        home = user_fs_home(username)
        db = os.path.join(home, HISTORY_FILE)
        
        conn = sqlite3.connect(db)
        
        c = conn.cursor()
    else:
        c = cursor
        conn = None
    
    c.execute('SELECT yabistoreapp_tag.value FROM yabistoreapp_tag, yabistoreapp_workflowtag WHERE yabistoreapp_workflowtag.tag_id = yabistoreapp_tag.id AND yabistoreapp_workflowtag.workflow_id = ?',(id,))
    
    data = [X[0] for X in c]
    
    if conn is not None: 
        conn.commit()
        c.close()
    
    return data

def find_workflow_by_date(username, start, end='now', sort="created_on", dir="DESC", get_tags=True):
    """find all the users workflows between the 'start' date and the 'end' date
    sort is an optional parameter to sort by
    if end is ommitted, it refers to now.
    returns a list of workflow hashes
    """
    assert sort in WORKFLOW_VARS
    assert dir in ('ASC','DESC')
    ensure_user_db(username)
    
    # TODO: sanity check julianday field 'start' and 'end'
    
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
   
    query_line = '%s as sort_key, %s' % (sort, WORKFLOW_QUERY_LINE)
    c = conn.cursor()
    c.execute("""SELECT %s FROM yabistoreapp_workflow
        WHERE created_on >= date(?)
        AND created_on <= date(?)
        ORDER BY %s %s"""%(query_line,sort,dir),
        (start,end) )
   
    rows = []
    for row in c:
        rows.append( dict( zip( ['sort_key'] + WORKFLOW_VARS, row ) ) )

    if get_tags:
        for row in rows:
            row['tags'] = get_tags_for_workflow(username, int(row['id']), cursor = c)
            # AH When I successfully broke admin and put broken workflows in the store
            # this code was exploding when trying to json.loads, so try/catch/pass
            try:
                row['json'] = json.loads(row['json'])
            except ValueError:
                pass

    conn.commit()
    c.close()
   
    def get_sort_key_val(row):
        val = row['sort_key']
        if sort in ('last_modified_on', 'created_on'):
            val = datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
        return val

    remove_sort_key = lambda d: dict(filter(lambda x: x[0] != 'sort_key', d.items()))
 
    return [(get_sort_key_val(r), remove_sort_key(r)) for r in rows]

def get_workflow(username, id, get_tags=True):
    """Return workflow with id 'id'
    """
    ensure_user_db(username)
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT %s FROM yabistoreapp_workflow
        WHERE id = ? """%WORKFLOW_QUERY_LINE,
        (id,) )
    
    rows = c.fetchall()
    
    if len(rows)==0:
        raise NoSuchWorkflow, "Workflow %d for user %s does not exist"%(id,username)
        
    result = dict( zip( WORKFLOW_VARS, rows[0] ) )
    if get_tags:
        result['tags'] = get_tags_for_workflow(username, int(result['id']), cursor = c)
    
    # decode the json object
    result['json']=json.loads(result['json'])
    
    conn.commit()
    c.close()
    
    return result

# This function is needed just by migration script in scripts
# TODO delete after users have been migrated
def get_workflows(username, get_tags=True, sort="last_modified_on", dir="DESC"):
    """Return all users workflows
    If get_tags is true, also returns the taglist with each workflow
    """
    assert dir in ('ASC','DESC')
    assert sort in WORKFLOW_VARS
    ensure_user_db(username)
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT %s FROM yabistoreapp_workflow ORDER BY %s %s"""%(WORKFLOW_QUERY_LINE,sort,dir))
    
            # columns on workflow table
    result =[]
    for row in c:
        result.append( dict( zip( WORKFLOW_VARS, row ) ) )
    
    if get_tags:
        for row in result:
            #print row
            row['tags'] = get_tags_for_workflow(username, int(row['id']), cursor = c)
            
            # decode the json object
            row['json']=json.loads(row['json'])
    
    
    conn.commit()
    c.close()
    
    return result

