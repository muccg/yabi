Get all workflows for a user:

$ curl http://localhost:8000/workflows/{username}

--------------------------------------------------------------------------

Save a workflow for a user. taglist is optional.

$ curl -d workflow_host=faramir\&workflow_id=413\&json=json\&name=myname\&status=status\&taglist=blah,blah2,another http://localhost:8000/workflows/{username}
2    <----- returns json encoded workflow_id

--------------------------------------------------------------------------

Get a particular workflow for a user. Does not return tags.

$ curl http://localhost:8000/workflows/{username}/2
{"status": "status", "name": "myname", "tags": ["blah", "blah2", "another"], "json": {"jobs": [{"parameterList": {"parameter": [{"valid": true, "value": [{"path": [], "type": "file", "filename": "AA123456.fa", "root": "yabifs://cwellington@localhost.localdomain:8000/cwellington/", "pathComponents": ["yabifs://cwellington@localhost.localdomain:8000/cwellington/"]}], "switchName": "files"}]}, "toolName": "fileselector", "valid": true, "jobId": 1}, {"parameterList": {"parameter": [{"valid": true, "value": ["blastp"], "switchName": "-p"}, {"valid": true, "value": ["aa"], "switchName": "-d"}, {"valid": true, "value": [{"type": "job", "jobId": 1}], "switchName": "-i"}]}, "toolName": "blast.xe.ivec.org", "valid": true, "jobId": 2}], "name": "unnamed (2009-09-01 11:51)", "tags": []}, "workflow_host": "test", "workflow_id": 200, "created_on": "2009-10-06", "id": 3, "last_modified_on": "2009-10-06"}

--------------------------------------------------------------------------

Update a workflow for a user. all params are optional. 'id' is the workflow id. if taglist is not specified, the taglist is left alone. If it is specified, the taglist is completely replaced.

$ curl -d json=json\&name=myname\&status=status\&taglist=blah,blah2,another http://localhost:8000/workflows/{username}/{id}

--------------------------------------------------------------------------

return the tags for a particular workflow

$ curl http://localhost:8000/workflows/{username}/{id}/tags
["blah", "blah2"]

--------------------------------------------------------------------------

reset the tags on a workflow

$ curl -d taglist=blah3,blah4 http://localhost:8000/workflows/{username}/{id}/tags

--------------------------------------------------------------------------

add some tags to a workflow

$ curl -d taglist=blah3,blah4 http://localhost:8000/workflows/{username}/{id}/tags/add

--------------------------------------------------------------------------

delete some tags from a workflow

$ curl -d taglist=blah3,blah4 http://localhost:8000/workflows/{username}/{id}/tags/remove

--------------------------------------------------------------------------

get all the workflows matching a tag

$ curl http://localhost:8000/workflows/{username}/tag/{tagvalue}

--------------------------------------------------------------------------

Get all workflows between two dates. compulsory param: start - the start date
optional params: end, sort.
end defaults to 'now'
sort defaults to 'created_on'

$ curl http://localhost:8000/workflows/{username}/datesearch?start=2009-01-25\&end=2009-02-01
[{"status": "status", "name": "myname", "created_on": 2455089.7961860239, "json": "json", "id": 1, "last_modified_on": 2455089.7961860239}, {"status": "status", "name": "yourname", "created_on": 2455089.8416402335, "json": "json", "id": 2, "last_modified_on": 2455089.8881653887}]
^
|
json encoded list of workflows returned

--------------------------------------------------------------------------

Do a search for workflows matching certain keywords.
keyword: the keyword to search for (compulsory)
field: the workflow field to search. default is 'name'. one of ['id','name','json','last_modified_on','created_on','status']
sort: the field to sort by. default is 'created_on'. one of ['id','name','json','last_modified_on','created_on','status']
operator: the sqlite3 operator to seach by. default is 'LIKE'. one of ('LIKE','GLOB','REGEXP','MATCH')

$ curl http://localhost:8000/workflows/{username}/search?keyword=name
[{"status": "status", "name": "myname", "created_on": 2455089.7961860239, "json": "json", "id": 1, "last_modified_on": 2455089.7961860239}, {"status": "status", "name": "yourname", "created_on": 2455089.8416402335, "json": "json", "id": 2, "last_modified_on": 2455089.8881653887}]
^
|
json encoded list of workflows returned

--------------------------------------------------------------------------

Search for a tag
keyword is a compulsory GET parameter

curl http://localhost:8000/workflows/bpower/tags/search?keyword=tag
["tagone", "tagtwo"]


--------------------------------------------------------------------------

Set the task execution status on a workflow "job"

$ curl -d status="running"\&tasksComplete=64\&tasksTotal=1000 http://localhost:8000/workflows/{username}/{id}/status/{jobid}
TODO: implement

--------------------------------------------------------------------------









##
## yabi fe javascript snippets. Why are they here?
##
workflow.addJob('fileselector', true);
workflow.jobs[0].params[0].fileSelector.selectFile(new YabiSimpleFileValue(['workspace'], 'sample.fa'));



