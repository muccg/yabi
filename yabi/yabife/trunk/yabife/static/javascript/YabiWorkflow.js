// $Id: YabiWorkflow.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiWorkflow
 * create a new workflow, which handles overall validation status as well as ordering/sequencing and ensuring that file inputs are
 * managed in a sequential, logical manner
 */
function YabiWorkflow(editable) {
    this.payload = {};
    this.isPropagating = false; //recursion protection
    this.tags = [];
    
    //util fn
    var dblzeropad = function(number) {
        if (number < 10) {
            number = "0" + number;
        }
        return number;
    };
    
    var date = new Date();
    if (editable) {
        this.name = "unnamed (" + date.getFullYear() + "-" + dblzeropad(date.getMonth()) + "-" + dblzeropad(date.getDate()) + " " + dblzeropad(date.getHours()) + ":" + dblzeropad(date.getMinutes()) + ")";
    }
    
	this.status = "Design";
	this.refreshTimer = null;
	this.selectedJob = null;
    
    this.editable = true;
    if (editable !== null && editable === false) {
        this.editable = false;
    }
    
    this.jobs = [];

    this.containerEl = document.createElement('div');
    this.containerEl.className = "workflowContainer";

    //construct the main dom, including title, submit (if editable) and bookends
    this.mainEl = document.createElement('div');

    if (this.editable) {
        this.submitEl = document.createElement('button');
        this.submitEl.appendChild(document.createTextNode("submit"));
        this.submitEl.id = "submitButton";
        this.mainEl.appendChild(this.submitEl);

        this.nameEl = document.createElement('input');
        this.nameEl.className = "workflowName";
        this.nameEl.id = "titleDiv";
        this.nameEl.value = this.name;
    
        YAHOO.util.Event.addListener(this.nameEl, "blur", this.nameChangeCallback, this);
        YAHOO.util.Event.addListener(this.nameEl, "keyup", this.nameChangeCallback, this);
        YAHOO.util.Event.addListener(this.nameEl, "change", this.nameChangeCallback, this);
    } else {
        this.nameEl = document.createElement('div');
        this.nameEl.className = "workflowName";
        this.nameEl.id = "titleDiv";
    }
    
    this.mainEl.appendChild(this.nameEl);
    
    //tag el
    this.tagEl = document.createElement('div');
    this.tagEl.className = 'tagList';
    this.tagEl.appendChild( document.createTextNode('Tags: ') );
    
    this.tagListEl = document.createElement('span');
    this.tagEl.appendChild( this.tagListEl );
    
    this.tagInputEl = document.createElement('input');
    this.tagInputEl.className = "displayNone";
    this.tagEl.appendChild( this.tagInputEl );
    
    this.tagAddLink = new Image();
    this.tagAddLink.src = appURL + 'static/images/addtag.png';
    YAHOO.util.Event.addListener(this.tagAddLink, "click", this.addTagCallback, this);
    this.tagEl.appendChild(this.tagAddLink);
    
    this.tagHintDiv = document.createElement("div");
    this.tagHintDiv.className = "displayNone";
    this.tagSaveEl = document.createElement("a");
    this.tagSaveEl.appendChild( document.createTextNode('save') );
    YAHOO.util.Event.addListener(this.tagSaveEl, "click", this.saveTagsCallback, this);
    this.tagHintDiv.appendChild(this.tagSaveEl);
    this.tagEl.appendChild(this.tagHintDiv);

    this.mainEl.appendChild(this.tagEl);
    
    this.startEl = document.createElement("div");
    this.startEl.appendChild(document.createTextNode("start"));
    this.startEl.className = "workflowStartBookend";
    
    this.mainEl.appendChild(this.startEl);
    
    //add empty workflow marker
    this.hintEl = document.createElement('div');
    this.hintEl.className = 'workflowHint';
    if (this.editable) {
        this.mainEl.appendChild(this.hintEl);
    }
        
    this.mainEl.appendChild(this.containerEl);

    this.endEl = document.createElement("div");
    this.endEl.appendChild(document.createTextNode("end"));
    this.endEl.className = "workflowEndBookend";
    
    this.mainEl.appendChild(this.endEl);

    if (this.editable) {    
        this.dd = new YAHOO.util.DDTarget(this.containerEl);
    }
    
    this.optionsEl = document.createElement('div');

}

/**
 * addJob
 *
 * adds a job to the end of the workflow
 */
YabiWorkflow.prototype.addJob = function(toolName, preloadValues) {

    if (this.processing) {
        return;
    }
    this.processing = true;
    
    this.hintEl.style.display = "none";
    
    var invoke, destroyEl;

    var job = new YabiJob(toolName, this.jobs.length + 1, preloadValues);
    job.editable = this.editable;
    if (!this.editable) {
        job.inputsEl.style.display = "none";
        job.outputsEl.style.display = "none";
    }
    job.workflow = this;
    this.jobs.push(job);

    job.hydrate();

    if (!this.editable) {
        //attach events    
        invoke = {"target":this, "object":job};
        YAHOO.util.Event.addListener(job.containerEl, "click", this.selectJobCallback, invoke);    
        
        //don't select any job (ie select null)
        this.selectJob(null);
    } else {
        //decorate the job with a 'destroy' link
        destroyEl = document.createElement("div");
        destroyEl.setAttribute("class", "destroyDiv");
        job.jobEl.appendChild(destroyEl);
    
        //attach events    
        invoke = {"target":this, "object":job};
        YAHOO.util.Event.addListener(destroyEl, "click", this.delJobCallback, invoke);
        YAHOO.util.Event.addListener(job.containerEl, "click", this.selectJobCallback, invoke);
        
        //drag drop
        job.dd = new YAHOO.util.DDProxy(job.containerEl);
        job.dd.startDrag = this.startDragJobCallback;
        job.dd.endDrag = this.endDragJobCallback;
        job.dd.onDrag = this.onDragJobCallback;
        job.dd.onDragOver = this.onDragOverJobCallback;
    
        //select the new item but only if we are editable
        this.selectJob(job);
    }

    //add into the DOM    
    this.containerEl.appendChild(job.containerEl);
    this.optionsEl.appendChild(job.optionsEl);
        
    this.processing = false;
    
    return job;
};

/**
 * deleteJob
 *
 * this uses simple locking to prevent multiple deletes happening concurrently, which causes validation errors
 */
YabiWorkflow.prototype.deleteJob = function(job) {
    if (this.deleting) {
        return;
    }
    
    this.deleting = true;
    var counter = 1;
    var delIndex = -1;

    if (job == this.selectedJob) {
        this.selectedJob = null;
    }

    //iterate jobs array, leaving out this item
    //reassigning jobId
    for (var index in this.jobs) {
        if (this.jobs[index] == job) {
            delIndex = index;
            continue;
        }
        
        this.jobs[index].jobId = counter++;
        this.jobs[index].updateTitle();
    }
    
    this.jobs.splice(delIndex, 1);

    if (this.jobs.length === 0) {
        this.hintEl.style.display = "block";
    }
    
    job.destroy();

    this.containerEl.removeChild(job.containerEl);
    this.optionsEl.removeChild(job.optionsEl);
    
    YAHOO.util.Event.purgeElement(job.containerEl);
    
    //force propagate
    this.propagateFiles();
    
    this.deleting = false;
};

/**
 * propagateFiles
 *
 * iterates over the jobs, querying the jobs for their emittedOutputs, using those outputs to prefill following jobs
 * the optional 'sender' param is to specify which node to start propagating from, to prevent trying to cause that and previous
 * jobs from consuming their own values into oblivion
 */
YabiWorkflow.prototype.propagateFiles = function(sender) {
    //recursion protection
    if (this.isPropagating) {
        return;
    }
    
    var subEmitted;
    
    this.isPropagating = true;
    var emittedFiles = [];
    var emittedKeys = []; //used for duplicate protection
    var foundSender = false;
    //if we have no sender, then we are propagating the whole workflow
    if (YAHOO.lang.isUndefined(sender)) {
        foundSender = true;
    }
        
    //iterate
    for (var index in this.jobs) {
        //do not allow the sender or above to consume
        if (foundSender) {
            this.jobs[index].optionallyConsumeFiles(emittedFiles, false);
        }
        //flag that the sender is found, after the optional consume, so the sender doesn't consume
        if (this.jobs[index] == sender) {
            foundSender = true;
        }
        
        subEmitted = this.jobs[index].emittedFiles().slice();
        if (subEmitted.length > 0) {
            for (var subindex in subEmitted) {
                if (!emittedKeys.hasOwnProperty(subEmitted[subindex])) { //duplicates have a value
                    emittedFiles.push( subEmitted[subindex] );
                    emittedKeys[subEmitted[subindex]] = 1;
                }
            }
        }
    }
    this.isPropagating = false;
};

/**
 * selectJob
 *
 * tells a job to render as selected, and tells all other jobs to render deselected
 */
YabiWorkflow.prototype.selectJob = function(object) {
    //iterate
    for (var index in this.jobs) {
        if (this.jobs[index] == object) {
            if (object == this.selectedJob) {
                this.jobs[index].deselectJob();
                this.selectedJob = null;
            } else {
                this.jobs[index].selectJob();
                this.selectedJob = object;
            }
        } else {
            this.jobs[index].deselectJob();
        }
    }
};

/**
 * updateName
 *
 * updates the workflow name and rendering
 */
YabiWorkflow.prototype.updateName = function(value) {
	this.name = value;
	
	if (this.editable) {
		this.nameEl.value = value;
    } else {
		while (this.nameEl.firstChild) {
			this.nameEl.removeChild(this.nameEl.firstChild);
		}
		
		this.nameEl.appendChild(document.createTextNode(value));
	}
};

/**
 * getName
 *
 */
YabiWorkflow.prototype.getName = function() {
    if (this.editable) {
        return this.nameEl.value;
    } else {
        return this.name;
    }
};


/**
 * getDisplayNameForJobId
 */
YabiWorkflow.prototype.getDisplayNameForJobId = function(jobId) {
    var num = parseInt(jobId);
    num = num - 1;
    
    if (num < this.jobs.length) {
        return this.jobs[num].toString();
    } else {
        return "unknown";
    }
};


/**
 * isJobIdLoaded
 */
YabiWorkflow.prototype.isJobIdLoaded = function(jobId) {
    var num = parseInt(jobId);
    num = num - 1;
    
    if (num < this.jobs.length) {
        return this.jobs[num].loaded;
    } else {
        //no such jobId, so, uh, yes it is
        return true;
    }
};

/**
 * getJobForId
 */
YabiWorkflow.prototype.getJobForId = function(jobId) {
    var num = parseInt(jobId);
    num = num - 1;
    
    if (num < this.jobs.length) {
        return this.jobs[num];
    } else {
        //no such jobId, so, uh, oops
        return null;
    }
};

/**
 * isValid
 *
 * verify validity of all jobs before proceeding
 */
YabiWorkflow.prototype.isValid = function() {
    if (this.jobs.length < 1) {
        return false;
    }
    
    if (this.getName() === "") {
        this.nameEl.className = "invalidWorkflowName";
        return false;
    } else {
        this.nameEl.className = "workflowName";
    }
    
    for (var index in this.jobs) {
        if (!this.jobs[index].valid) {
            return false;
        }
    }
    
    return true;
};

/**
 * toJSON
 *
 * produces a json string for this workflow
 */
YabiWorkflow.prototype.toJSON = function() {
    var result = {  "name":this.name };
    
    var jobs = [];
    for (var index in this.jobs) {
        jobs.push(this.jobs[index].toJSON());
    }
    
    result.jobs = jobs;
    return YAHOO.lang.JSON.stringify(result);
};

/**
 * hydrate
 *
 * fetch workflow definition from the server
 */
YabiWorkflow.prototype.hydrate = function(workflowId) {
    this.workflowId = workflowId;
    var baseURL = appURL + "workflows/" + YAHOO.ccgyabi.username + "/" + workflowId;
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
            success: this.hydrateCallback,
            failure: this.hydrateCallback,
            argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

/**
 * saveTags
 *
 * save tags
 */
YabiWorkflow.prototype.saveTags = function() {
    var baseURL = appURL + "workflows/" + YAHOO.ccgyabi.username + "/" + workflowId + "/tags/add";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
    success: this.saveTagsResponseCallback,
    failure: this.saveTagsResponseCallback,
        argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('POST', jsUrl, jsCallback, "taglist="+escape(this.tagInputEl.value));
};

/**
 * solidify
 *
 * handle json response, populating object and rendering as required
 */
YabiWorkflow.prototype.solidify = function(obj) {
	this.payload = obj;
	var updateMode = false;
	
	var job;
	
	this.updateName(obj.name);

	if (this.jobs.length > 0) {
	    updateMode = true;
	}
	
    while (this.tagListEl.firstChild) {
        this.tagListEl.removeChild(this.tagListEl.firstChild);
    }
    this.tagListEl.appendChild( document.createTextNode(this.tags) );
    
	for (var index in obj.jobs) {
		if (updateMode) {
		    job = this.jobs[index];
	    } else {
	        job = this.addJob(obj.jobs[index].toolName, obj.jobs[index].parameterList.parameter);
        }
        
        if (!this.editable) {
    		job.renderProgress(obj.jobs[index].status, obj.jobs[index].progress);
		}
	}
};

/**
 * waitForJob
 *
 * start an interval to continuously refresh this workflow until completed
 */
YabiWorkflow.prototype.waitForJob = function() {
    this.refreshTimer = window.setInterval(function() { workflow.fetchProgress(); }, 5000);
};

/**
 * fetchProgress
 *
 * one-time fetch current workflow status
 */
YabiWorkflow.prototype.fetchProgress = function() {
    //console.log("fetch progress");

    this.hydrate(this.workflowId);
    
    if (this.status == "Completed") {
        window.clearInterval(this.refreshTimer);
    }
};

/**
 * setTags
 *
 * update tags array and input field simultaneously
 */
YabiWorkflow.prototype.setTags = function(tagArray) {
    this.tags = tagArray;
    this.tagInputEl.value = tagArray;
};

/**
 * destroy
 *
 * delete any internal variables and dom handlers
 */
YabiWorkflow.prototype.destroy = function() {
    if (this.refreshTimer !== null) {
        window.clearInterval(this.refreshTimer);
    }
    
    var job;
    
    for (var index in this.jobs) {
        job = this.jobs[index];
    
        job.destroy();
        
        this.containerEl.removeChild(job.containerEl);
        this.optionsEl.removeChild(job.optionsEl);
    
        YAHOO.util.Event.purgeElement(job.containerEl);
    }
    
    //purge all listeners on nameEl
    YAHOO.util.Event.purgeElement(this.nameEl);
    
    //remove the workfow from its container
    this.mainEl.parentNode.removeChild(this.mainEl);
};

//---- CALLBACKS ----
YabiWorkflow.prototype.hydrateCallback = function(o) {
    var json = o.responseText;
    var i;
    var obj;
    
    try {
        target = o.argument[0];
        
        obj = YAHOO.lang.JSON.parse(json);
        
        //preprocess wrapper meta data
        target.setTags(obj.tags);
        
        target.solidify(YAHOO.lang.JSON.parse(obj.json));
    } catch (e) {
        YAHOO.ccgyabi.YabiMessage.yabiMessageFail("Error loading workflow");
    }
};

YabiWorkflow.prototype.delJobCallback = function(e, invoke) {
    invoke.target.deleteJob(invoke.object);
    //prevent propagation of the event to select/deselecting the job
    YAHOO.util.Event.stopEvent(e);
};

YabiWorkflow.prototype.selectJobCallback = function(e, invoke) {
    var workflow = invoke.target;
    
    workflow.selectJob(invoke.object);

    YAHOO.util.Event.stopEvent(e);
};

YabiWorkflow.prototype.startDragJobCallback = function(x, y) {
    this.getEl().style.visibility = "hidden";
    this.getDragEl().style.border = "none";
    this.getDragEl().style.textAlign = "left";
    this.getDragEl().innerHTML = this.getEl().innerHTML;
    
    this.dragType = "job";
    this.lastY = y;
};

YabiWorkflow.prototype.endDragJobCallback = function(e) {
    if (this.dragType == "job") {
        this.getEl().style.visibility = "";
    } else {
        this.jobEl.style.visibility = "";
        this.optionsEl.style.display = "block";
    }
    this.getDragEl().style.visibility = "hidden";
    
    //identify the new location, recreating the jobs array based on current div locations
    var alteredJobs = [];
    var counter = 1;
    var job;
    for (var index in workflow.containerEl.childNodes) {
        for (var jobindex in workflow.jobs) {
            if (workflow.jobs[jobindex].containerEl == workflow.containerEl.childNodes[index]) {
                job = workflow.jobs[jobindex];
                job.jobId = counter++;
                job.updateTitle();
                alteredJobs.push(job);
            }
        }
    }
    
    //replace jobs array with newly re-ordered items
    workflow.jobs = alteredJobs;
        
    //re-propagate files
    workflow.propagateFiles();
};

YabiWorkflow.prototype.onDragJobCallback = function(e) {
        // Keep track of the direction of the drag for use during onDragOver 
        var y = YAHOO.util.Event.getPageY(e); 
 
        if (y < this.lastY) { 
            this.goingUp = true; 
        } else if (y > this.lastY) { 
            this.goingUp = false; 
        } 
        this.lastY = y; 
};


YabiWorkflow.prototype.onDragOverJobCallback = function(e, id) {
    var destEl = YAHOO.util.Dom.get(id);
    var srcEl;
    if (this.dragType == "job") {
        srcEl = this.getEl();
    } else {
        srcEl = this.jobEl;
    }

    if (destEl.className == "jobSuperContainer") {
        //TODO use mid-point to determine if they are going up and have gone past the mid-point of destEl

        if (this.goingUp) {
            srcEl.parentNode.insertBefore(srcEl, destEl);
        } else {
            srcEl.parentNode.insertBefore(srcEl, destEl.nextSibling);
        }
    }
};

YabiWorkflow.prototype.nameChangeCallback = function(e, obj) {
    obj.name = obj.nameEl.value;
};

YabiWorkflow.prototype.addTagCallback = function(e, obj) {
    //do stuff
    obj.tagListEl.style.display = 'none';
    obj.tagInputEl.style.display = 'inline';
    obj.tagHintDiv.className = "fakeButton";
};

YabiWorkflow.prototype.saveTagsCallback = function(e, obj) {
    //do stuff
    obj.saveTags();
};

YabiWorkflow.prototype.saveTagsResponseCallback = function(e, obj) {
    //do stuff
    YAHOO.ccgyabi.YabiMessage.yabiMessageSuccess("tags saved");
};