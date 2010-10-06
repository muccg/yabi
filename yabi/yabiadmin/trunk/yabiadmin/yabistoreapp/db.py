# -*- coding: utf-8 -*-
"""
Support library to create and access the users personal history database
"""

import sqlite3, os

try:
    import json
except ImportError, ie:
    import simplejson as json

import settings

try:
    USERS_HOME = settings.YABISTORE_HOME
except AttributeError, ae:
    USERS_HOME = "/tmp"
    
HISTORY_FILE = "history.sqlite3"

DB_CREATE = """
CREATE TABLE "yabistoreapp_tag" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "value" varchar(255) NOT NULL
)
;
CREATE TABLE "yabistoreapp_workflow" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(255) NOT NULL,
    "json" text NOT NULL,
    "last_modified_on" datetime,
    "created_on" datetime NOT NULL,
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
    os.chmod(db,0777)                   # we need to write to the file as another user
    os.chmod(home,0777)                 # AND we need to write to the directory as another user for the -journal sqlite file
    
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

def save_workflow(username, workflow_id, workflow_json, status, name, taglist=[]):
    """place a row in the workflow table"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute('INSERT INTO "yabistoreapp_workflow" (id, name, json, status, created_on, last_modified_on) VALUES (?, ?,?,?,julianday("now"),julianday("now"))',(workflow_id, name, workflow_json,status))
        
    for tag in taglist:
        # see if the tag already exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        assert len(data)==0 or len(data)==1, "Database corruption: Denormalised database! Tag '%s' has multiple entries in the tag table for user '%s'"%(tag,username)
        
        if len(data)==0:
            c.execute('INSERT INTO "yabistoreapp_tag" (value) VALUES (?)',(tag,) )
        
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, last_insert_rowid())', (workflow_id,))
        else:
            # link the many to many
            c.execute('INSERT INTO "yabistoreapp_workflowtag" (workflow_id, tag_id) VALUES (?, ?)', (workflow_id,data[0][0]))
    
    conn.commit()
    c.close()

def update_workflow(username, id, updateset, taglist=None):
    """update a row in the workflow table"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    # update the actual workflow
    assert 'id' not in updateset, "id should not be updated in a workflow"
    c = conn.cursor()
    
    if len(updateset):
        command = 'UPDATE "yabistoreapp_workflow" SET '
        for key in updateset:
            command+="%s = ?, "%key
        command += ' last_modified_on=julianday("now") WHERE id = ?'
        c.execute(command,updateset.values()+[id])
    
    if taglist is not None:
        # now update the taglist. Lets get the existing taglist
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
    
    assert len(data)==1, "Database corruption: Denormalised database! Workflow id %d has more than one occurance"%(workflow_id)
    
    for tag in taglist:
        # see if the tag already exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        assert len(data)==0 or len(data)==1, "Database corruption: Denormalised database! Tag '%s' has multiple entries in the tag table for user '%s'"%(tag,username)
        
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
    
    assert len(data)==1, "Database corruption: Denormalised database! Workflow id %d has more than one occurance"%(workflow_id)
    
    for tag in taglist:
        # see if the tag  exists
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        assert len(data)==0 or len(data)==1, "Database corruption: Denormalised database! Tag '%s' has multiple entries in the tag table for user '%s'"%(tag,username)

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
            
def delete_tag(username, taglist):
    """delete all links to tags in taglist and the tags themselves"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    
    for tag in taglist:
        print "deleting",tag
        
        # get tag id
        c.execute('SELECT id FROM yabistoreapp_tag WHERE value = ?', (tag,) )
        data = c.fetchall()
        assert len(data)==0 or len(data)==1, "Database corruption: Denormalised database! Tag '%s' has multiple entries in the tag table for user '%s'"%(tag,username)
        
        if len(data):
            tag_id = data[0][0]
            print "id=",tag_id
            
            c.execute('DELETE FROM yabistoreapp_workflowtag WHERE tag_id=?',(tag_id,))
            c.execute('DELETE FROM yabistoreapp_tag WHERE id=?',(tag_id,))
        
    conn.commit()
    c.close()

def delete_workflow(username, workflow_id, delete_empty=True):
    """delete the specified workflow and all its tag links, and if delete_empty is set, all empty tags"""
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    # find all the tag links and their ids
    c.execute("""SELECT DISTINCT yabistoreapp_workflowtag.tag_id 
        FROM yabistoreapp_workflow, yabistoreapp_workflowtag 
        WHERE yabistoreapp_workflow.id = yabistoreapp_workflowtag.workflow_id
        AND yabistoreapp_workflow.id = ?""", (workflow_id,) )
    tag_ids = [X[0] for X in c]
    
    # delete all the link table entries
    c.execute("DELETE FROM yabistoreapp_workflowtag WHERE workflow_id = ?",(workflow_id,))
    
    # for each tag
    if delete_empty:
        for tag_id in tag_ids:
            # is the tag now empty?
            c.execute('SELECT count() FROM yabistoreapp_workflowtag WHERE yabistoreapp_workflowtag.tag_id = ?',(tag_id,))
            data = c.fetchall()
    
            if data[0][0]==0:
                # no more tag links left. delete.
                c.execute('DELETE FROM yabistoreapp_tag WHERE id = ?',(tag_id,))
     
    # delete workflow itself
    # TODO: check if workflow exists
    c.execute("DELETE FROM yabistoreapp_workflow WHERE id = ?",(workflow_id,))
    
    conn.commit()
    c.close()

def get_tags(username, offset=0, limit=None):
    """return a list of tags. pass in offset and limit if you want to get a subset of the total
    
    TODO: offset and limits
    """
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute('SELECT value FROM yabistoreapp_tag')
    
    data = [X[0] for X in c]
    
    conn.commit()
    c.close()
    
    return data

def get_tags_for_workflow(username, id, cursor=None):
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

    
def find_workflow_by_tag(username, tag, sort="created_on"):
    """find all the workflows specified by a tag 'tag'
    returns a list of workflows. The workflows are represented by a hash of key/value pairs
    sort is an optional parameter which takes the workflow column to sort by
    """
    assert sort in WORKFLOW_VARS
    
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT yabistoreapp_workflow.* FROM yabistoreapp_workflow,yabistoreapp_tag,yabistoreapp_workflowtag 
        WHERE yabistoreapp_workflow.id = yabistoreapp_workflowtag.workflow_id 
        AND yabistoreapp_tag.id = yabistoreapp_workflowtag.tag_id
        AND yabistoreapp_tag.value = ?
        ORDER BY yabistoreapp_workflow.%s"""%sort,
        (tag,) )
    
    rows = []
    for row in c:
        rows.append( dict( zip( WORKFLOW_VARS, row ) ) )
        
    for row in rows:
        row['json']=json.loads(row['json'])
        
    conn.commit()
    c.close()
    
    return rows
    
def find_workflow_by_date(username, start, end='now', sort="created_on", dir="DESC", get_tags=True):
    """find all the users workflows between the 'start' date and the 'end' date
    sort is an optional parameter to sort by
    if end is ommitted, it refers to now.
    returns a list of workflow hashes
    """
    assert sort in WORKFLOW_VARS
    assert dir in ('ASC','DESC')
    
    # TODO: sanity check julianday field 'start' and 'end'
    
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT %s FROM yabistoreapp_workflow
        WHERE created_on >= julianday(?)
        AND created_on <= julianday(?)
        ORDER BY %s %s"""%(WORKFLOW_QUERY_LINE,sort,dir),
        (start,end) )
    
    rows = []
    for row in c:
        rows.append( dict( zip( WORKFLOW_VARS, row ) ) )
    
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
    
    return rows

def find_workflow_by_search(username, search, field="name", sort="created_on", operator="LIKE", dir="DESC"):
    """find all the users workflows matching search
    sort is an optional parameter to sort by
    field is the field to search. defaults to 'name'
    operator is overridable to implement regexp etc. Should be 'like','glob','regexp' or 'match'
    returns a list of workflow hashes
    """
    operator = operator.upper()
    assert operator in ('LIKE','GLOB','REGEXP','MATCH')
    
    if operator=='LIKE':
        search = "%"+search+"%"
    
    assert sort in WORKFLOW_VARS
    assert field in WORKFLOW_VARS
    
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT * FROM yabistoreapp_workflow
        WHERE %s %s ? 
        ORDER BY %s %s"""%(field,operator,sort,dir),
        (search,) )
    
    rows = []
    for row in c:
        # decode the json object
        row['json']=json.loads(row['json'])
    
    for row in rows:
        row['json']=json.loads(row['json'])
        
    conn.commit()
    c.close()
    
    return rows
    
def find_tag_by_search(username, search, operator="LIKE"):
    """find all the users workflows matching search
    sort is an optional parameter to sort by
    field is the field to search. defaults to 'name'
    operator is overridable to implement regexp etc. Should be 'like','glob','regexp' or 'match'
    returns a list of workflow hashes
    """
    operator = operator.upper()
    assert operator in ('LIKE','GLOB','REGEXP','MATCH')
    
    if operator=='LIKE':
        search = "%"+search+"%"
    
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT * FROM yabistoreapp_tag
        WHERE value %s ? """%(operator),
        (search,) )
    
    rows = [X[1] for X in c.fetchall()]
    
    conn.commit()
    c.close()
    
    return rows
    
    
def get_workflow(username, id, get_tags=True):
    """Return workflow with id 'id'
    """
    home = user_fs_home(username)
    db = os.path.join(home, HISTORY_FILE)
    
    conn = sqlite3.connect(db)
    
    c = conn.cursor()
    c.execute("""SELECT %s FROM yabistoreapp_workflow
        WHERE id = ? """%WORKFLOW_QUERY_LINE,
        (id,) )
    
    rows = c.fetchall()
    
    assert len(rows)==0 or len(rows)==1, "Database corruption: Denormalised database! user %s workflow id:%d has multiple entries!"%(username,id)
        
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

def get_workflows(username, get_tags=True, sort="last_modified_on", dir="DESC"):
    """Return all users workflows
    If get_tags is true, also returns the taglist with each workflow
    """
    assert dir in ('ASC','DESC')
    assert sort in WORKFLOW_VARS
    
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
            print row
            row['tags'] = get_tags_for_workflow(username, int(row['id']), cursor = c)
            
            # decode the json object
            row['json']=json.loads(row['json'])
    
    
    conn.commit()
    c.close()
    
    return result

