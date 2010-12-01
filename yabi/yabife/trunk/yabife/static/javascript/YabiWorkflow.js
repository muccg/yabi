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
    this.attachedProxies = [];
    
    //util fn
    var dblzeropad = function(number) {
        if (number < 10) {
            number = "0" + number;
        }
        return number;
    };
    var header;
    
    var date = new Date();
    if (editable) {
        this.name = "unnamed (" + date.getFullYear() + "-" + dblzeropad(date.getMonth() + 1) + "-" + dblzeropad(date.getDate()) + " " + dblzeropad(date.getHours()) + ":" + dblzeropad(date.getMinutes()) + ")";
        this.prefillName = this.name;
    }
    
	this.status = "Design";
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
        this.submitEl.appendChild(document.createTextNode("run"));
        this.submitEl.id = "submitButton";
        this.submitEl.className = "fakeButton largeButton";
        this.mainEl.appendChild(this.submitEl);

        this.nameEl = document.createElement('input');
        this.nameEl.className = "workflowName";
        this.nameEl.id = "titleDiv";
        this.nameEl.value = this.name;
    
        YAHOO.util.Event.addListener(this.nameEl, "blur", this.nameBlurCallback, this);
        YAHOO.util.Event.addListener(this.nameEl, "keyup", this.nameChangeCallback, this);
        YAHOO.util.Event.addListener(this.nameEl, "change", this.nameChangeCallback, this);
        YAHOO.util.Event.addListener(this.nameEl, "click", this.nameFocusCallback, this);
    } else {
        this.nameEl = document.createElement('div');
        this.nameEl.className = "workflowName";
        this.nameEl.id = "titleDiv";
    }
    
    this.mainEl.appendChild(this.nameEl);
    
    //tag el
    this.tagEl = document.createElement('div');
    this.tagEl.className = 'tagListContainer';
    this.tagEl.appendChild( document.createTextNode('Tags: ') );
    
    this.tagListEl = document.createElement('span');
    this.tagListEl.className = 'tagList';
    this.tagEl.appendChild( this.tagListEl );
    
    this.tagInputEl = document.createElement('input');
    this.tagInputEl.className = "displayNone";
    this.tagEl.appendChild( this.tagInputEl );
    
    this.tagAddLink = new Image();
    this.tagAddLink.className = "tagAddLink";
    this.tagAddLink.src = appURL + 'static/images/addtag.png';
    YAHOO.util.Event.addListener(this.tagAddLink, "click", this.addTagCallback, this);
    this.tagEl.appendChild(this.tagAddLink);
    
    this.tagHintDiv = document.createElement("div");
    this.tagHintDiv.className = "displayNone";
    
    this.tagCancelEl = document.createElement("span");
    this.tagCancelEl.className = "fakeButton";
    this.tagCancelEl.appendChild( document.createTextNode('cancel') );
    YAHOO.util.Event.addListener(this.tagCancelEl, "click", this.cancelTagsCallback, this);
    
    this.tagSaveEl = document.createElement("span");
    this.tagSaveEl.className = "fakeButton";
    this.tagSaveEl.appendChild( document.createTextNode('save') );
    YAHOO.util.Event.addListener(this.tagSaveEl, "click", this.saveTagsCallback, this);
    
    this.tagHintDiv.appendChild(this.tagCancelEl);
    this.tagHintDiv.appendChild(this.tagSaveEl);
    this.tagEl.appendChild(this.tagHintDiv);
    
    //tag help bubble
    this.tagHelpEl = document.createElement("div");
    this.tagHelpEl.className = "tagHelp";
    var helpImg = new Image();
    helpImg.src = appURL + "static/images/tagHelp.png";
    this.tagHelpEl.appendChild(helpImg);
    this.tagEl.appendChild(this.tagHelpEl);
    YAHOO.util.Event.addListener(this.tagHelpEl, "click", function(e, obj) { var myAnim = new YAHOO.util.Anim(obj.tagHelpEl, { opacity: { to: 0 } }, 0.5, YAHOO.util.Easing.easeOut); myAnim.onComplete.subscribe(function() { this.getEl().style.display = "none"; }); myAnim.animate(); }, this);


    this.mainEl.appendChild(this.tagEl);
    
    if (!this.editable) {
        //actions toolbar
        this.toolbarEl = document.createElement('div');
        this.toolbarEl.className = 'workflowToolbar';
        this.mainEl.appendChild(this.toolbarEl);

        this.reuseButtonEl = document.createElement('span');
        this.reuseButtonEl.className = 'fakeButton';
        this.reuseButtonEl.appendChild( document.createTextNode( 're-use' ) );
        YAHOO.util.Event.addListener(this.reuseButtonEl, "click", this.reuseCallback, this);
        this.toolbarEl.appendChild(this.reuseButtonEl);
    }

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
    this.optionsEl.className = "jobOptionsContainer";
    
    this.statusEl = document.createElement("div");
    this.statusEl.className = "jobStatusContainer";

    if (!editable) {
        this.fileOutputsEl = document.createElement('div');
        this.fileOutputsEl.className = "fileOutputs";
        header = document.createElement('h1');
        header.appendChild( document.createTextNode('File outputs') );
        this.fileOutputsEl.appendChild( header );

        //not editable, create a file selector to point at the stageout directory if it exists
        this.fileOutputsSelector = new YabiFileSelector(null, true);
        this.fileOutputsSelector.homeEl.style.display = 'none';
        this.fileOutputsSelector.uploadEl.style.display = 'none';
        this.fileOutputsEl.appendChild( this.fileOutputsSelector.containerEl );
        this.fileOutputsEl.style.display = 'none';
        this.fileOutputsSelector.containerEl.style.marginLeft = "4px";
    }

    //add an enter key listener for the tags field
    var enterTags = new YAHOO.util.KeyListener(this.tagInputEl, { ctrl:false, keys:13 }, 
                                         { fn:this.saveTags, 
                                         scope:this,
                                         correctScope:true } );
    enterTags.enable();
}

YabiWorkflow.prototype.setStatus = function(statusText) {
    this.status = statusText.toLowerCase();
    
    //update proxies
    var proxy;
    for (index in this.attachedProxies) {
        proxy = this.attachedProxies[index];
        proxy.badgeEl.className = "badge"+this.status;
        proxy.payload.status = this.status;
    }
    
    if (this.editable) {
        return;
    }
    
    var loadImg;
    if (this.status !== "complete" && this.status !== "error") {
        if (YAHOO.lang.isUndefined(this.loadingEl) || this.loadingEl === null) {
            this.loadingEl = document.createElement("div");
            this.loadingEl.className = "workflowLoading";
            loadImg = new Image();
            loadImg.src = appURL + "static/images/processing.gif";
            this.loadingEl.appendChild(loadImg);
            
            this.loadingTextEl = document.createElement("span");
        }
        
        this.loadingTextEl.innerHTML = "workflow running, waiting for completion...";
        this.loadingEl.appendChild( this.loadingTextEl );
        
        this.mainEl.appendChild(this.loadingEl);
    } else {
        //completed or error, remove the loadingEl
        if (YAHOO.lang.isUndefined(this.loadingEl) || this.loadingEl === null) {
        } else {
            this.mainEl.removeChild(this.loadingEl);
            this.loadingEl = null;
        }
    }
};

/**
 * addJob
 *
 * adds a job to the end of the workflow
 */
YabiWorkflow.prototype.addJob = function(toolName, preloadValues, shouldFadeIn) {

    if (this.processing) {
        return;
    }
    this.processing = true;
    
    this.hintEl.style.display = "none";
    
    var invoke, destroyEl, destroyImg;

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
        destroyImg = new Image();
        destroyImg.title = 'delete tool';
        destroyImg.alt = destroyImg.title;
        destroyImg.src = appURL + "static/images/delnode.png";
        destroyEl.appendChild( destroyImg );
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

    if (YAHOO.lang.isUndefined(shouldFadeIn)) {
        shouldFadeIn = true;
    }

    if (shouldFadeIn) {
        //start off the opacity at 0.0
        job.containerEl.style.opacity = 0.0;
    }

    //add into the DOM    
    this.containerEl.appendChild(job.containerEl);
    this.optionsEl.appendChild(job.optionsEl);
    this.statusEl.appendChild(job.statusEl);
    
    var anim;
    if (shouldFadeIn) {
        anim = new YAHOO.util.Anim(job.containerEl, { opacity: { from: 0.0, to: 1.0 } }, 1.0, YAHOO.util.Easing.Linear);
        anim.animate();
    }

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
        
        this.afterSelectJob(null);
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
    this.statusEl.removeChild(job.statusEl);
    
    YAHOO.util.Event.purgeElement(job.containerEl);
    
    //force propagate
    this.propagateFiles();
    
    this.deleting = false;
};

/**
 * attachProxy
 *
 * attaches a workflowProxy to this workflow, so that changes in this workflow are propagated back to the proxy
 */
YabiWorkflow.prototype.attachProxy = function(proxy) {
    this.attachedProxies.push(proxy);
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

    //afterPropagate call for other objects to hook in to
    if (!YAHOO.lang.isUndefined(this.afterPropagate) && !YAHOO.lang.isUndefined(sender)) {
        this.afterPropagate(sender);
    }
};

/**
 * selectJob
 *
 * tells a job to render as selected, and tells all other jobs to render deselected
 */
YabiWorkflow.prototype.selectJob = function(object) {
    if (!this.editable) {
        this.fileOutputsEl.style.display = "none";
    }

    //iterate
    var selectedIndex = null;
    for (var index in this.jobs) {
        if (this.jobs[index] == object) {
            if (object == this.selectedJob) {
                this.jobs[index].deselectJob();
                this.selectedJob = null;
                
                //callback hook to allow other elements to hook in when jobs are selected/deselected
                if (!YAHOO.lang.isUndefined(this.afterSelectJob) && object.loaded) {
                    this.afterSelectJob(null);
                }
            } else {
                selectedIndex = index;
            }
        } else {
            this.jobs[index].deselectJob();
        }
    }

    if (selectedIndex !== null) {
        this.jobs[selectedIndex].selectJob();
        this.selectedJob = object;
        
        if (!this.editable && !YAHOO.lang.isUndefined(this.payload.jobs[selectedIndex].stageout)) {
            this.fileOutputsEl.style.display = "block";
            this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue([this.payload.jobs[selectedIndex].stageout], ''));
        }

        //callback hook to allow other elements to hook in when jobs are selected/deselected
        if (!YAHOO.lang.isUndefined(this.afterSelectJob) && object.loaded) {
            this.afterSelectJob(object);
        }
    }
};

/**
 * delayedSelectJob
 *
 * exists for the purpose of allowing an afterSelectJob callback after a tool has loaded
 */
YabiWorkflow.prototype.delayedSelectJob = function(job) {
    this.afterSelectJob(job);
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
    var num = parseInt(jobId, 10);
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
    var num = parseInt(jobId, 10);
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
    var num = parseInt(jobId, 10);
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
    
    if (this.getName() === "" || this.getName().indexOf("?") != -1) {
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
    var result = {  "name":this.name, "tags":this.tags };
    
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
    var loadImg;
    
    if (YAHOO.lang.isUndefined(this.workflowId)) {
        this.hydrateDiv = document.createElement("div");
        this.hydrateDiv.className = "workflowHydrating";
        loadImg = new Image();
        loadImg.src = appURL + "static/images/largeLoading.gif";
        this.hydrateDiv.appendChild( loadImg );
        document.body.appendChild(this.hydrateDiv);
    }

    this.workflowId = workflowId;
    var baseURL = appURL + "workflows/" + workflowId;
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
            success: this.hydrateCallback,
            failure: YAHOO.ccgyabi.widget.YabiMessage.handleResponse,
            argument: [this] };
    this.jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);

};

YabiWorkflow.prototype.fadeHydratingDiv = function() {
    //fade out and remove the loading element   
    var anim = new YAHOO.util.Anim(this.hydrateDiv, { opacity: { to: 0.0 } }, 0.3, YAHOO.util.Easing.Linear);
    anim.onComplete.subscribe(function() { document.body.removeChild(this.getEl()); });
    anim.animate();

};

/**
 * reuse
 *
 * reload the whole page with a reuse URL
 */
YabiWorkflow.prototype.reuse = function() {
    var baseURL = appURL + "design/reuse/" + this.workflowId;

    window.location = baseURL;
};


/**
 * saveTags
 *
 * save tags
 */
YabiWorkflow.prototype.saveTags = function(postRelocate) {
    this.tagInputEl.blur();

    if (YAHOO.lang.isUndefined(this.workflowId)) {
        this.tagsFinishedSaving();
        return;
    }
    
    var baseURL = appURL + "workflows/" + this.workflowId + "/tags";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
    success: this.saveTagsResponseCallback,
    failure: this.saveTagsResponseCallback,
        argument: [this, postRelocate] };
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
	
	var job, index, oldJobStatus;
	
	this.updateName(obj.name);

	if (this.jobs.length > 0) {
	    updateMode = true;
	}
	
    while (this.tagListEl.firstChild) {
        this.tagListEl.removeChild(this.tagListEl.firstChild);
    }
    this.tagListEl.appendChild( document.createTextNode(this.tags) );
    
	for (index in obj.jobs) {
		if (updateMode) {
		    job = this.jobs[index];
	    } else {
	        job = this.addJob(obj.jobs[index].toolName, obj.jobs[index].parameterList.parameter);
        }
        if (!this.editable) {
    		oldJobStatus = job.status;
            
            job.renderProgress(obj.jobs[index].status, obj.jobs[index].tasksComplete, obj.jobs[index].tasksTotal);
            
            if (this.selectedJob == job && oldJobStatus != job.status) {
                this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue([this.payload.jobs[index].stageout], ''));
            }
		}
	}
    
};

/**
 * fetchProgress
 *
 * one-time fetch current workflow status
 */
YabiWorkflow.prototype.fetchProgress = function(callback) {
    //console.log("fetch progress");
    if (this.status.toLowerCase() !== "completed" && this.status.toLowerCase() !== "error") {
        this.hydrate(this.workflowId);
    } 
    
    if (callback !== null) {
        callback(this.status);
    }
};

/**
 * setTags
 *
 * update tags array and input field simultaneously
 */
YabiWorkflow.prototype.setTags = function(tagArray) {
    if (this.tagInputEl.style.display != "inline") {
        this.tags = tagArray;
        this.tagInputEl.value = tagArray;
    } //dont set the tags if they are being edited
};

/**
 * cancelTagEditing
 *
 * reset tag input to the same as the tags array, hide editing fields
 */
YabiWorkflow.prototype.cancelTagEditing = function() {
    this.tagInputEl.value = this.tags;
    this.tagHintDiv.className = "displayNone";
    this.tagInputEl.style.display = "none";
    this.tagListEl.style.display = "inline";
    this.tagAddLink.style.display = "block";
    var myAnim = new YAHOO.util.Anim(this.tagHelpEl, { opacity: { to: 0 } }, 0.5, YAHOO.util.Easing.easeOut);
    myAnim.onComplete.subscribe(function() { this.getEl().style.display = "none"; });
    myAnim.animate();
};

/**
 * tagsFinishedSaving
 *
 * hide editing fields, solidify tags editing field into an array
 */
YabiWorkflow.prototype.tagsFinishedSaving = function(postRelocate) {
    this.tags = this.tagInputEl.value.split(",");
    while (this.tagListEl.firstChild) {
        this.tagListEl.removeChild(this.tagListEl.firstChild);
    }
    this.tagListEl.appendChild( document.createTextNode('' + this.tags) );    
    
    //notify attached proxies
    for (var index in this.attachedProxies) {
        this.attachedProxies[index].setTags(this.tags);
    }

    this.tagHintDiv.className = "displayNone";
    this.tagInputEl.style.display = "none";
    this.tagListEl.style.display = "inline";
    this.tagAddLink.style.display = "block";
    var myAnim = new YAHOO.util.Anim(this.tagHelpEl, { opacity: { to: 0 } }, 0.5, YAHOO.util.Easing.easeOut);
    myAnim.onComplete.subscribe(function() { this.getEl().style.display = "none"; });
    myAnim.animate();
    
    //if postRelocate != undefined then redirect user to the jobs tab
    if (!YAHOO.lang.isUndefined(postRelocate)) {
        postRelocate(this.workflowId);
    }
};

/**
 * destroy
 *
 * delete any internal variables and dom handlers
 */
YabiWorkflow.prototype.destroy = function() {
    if (YAHOO.util.Connect.isCallInProgress( this.jsTransaction )) {
        YAHOO.util.Connect.abort( this.jsTransaction, null, false );
    }
    
    var job;
    
    for (var index in this.jobs) {
        job = this.jobs[index];
    
        job.destroy();
        
        this.containerEl.removeChild(job.containerEl);
        this.optionsEl.removeChild(job.optionsEl);
        this.statusEl.removeChild(job.statusEl);
    
        YAHOO.util.Event.purgeElement(job.containerEl);
    }
    
    //purge all listeners on nameEl
    YAHOO.util.Event.purgeElement(this.nameEl);
    
    //remove the workflow from its container
    this.mainEl.parentNode.removeChild(this.mainEl);
    
    if (!YAHOO.lang.isUndefined(this.fileOutputsEl)) {
        this.fileOutputsEl.parentNode.removeChild(this.fileOutputsEl);
    }

    if (!YAHOO.lang.isUndefined(this.hydrateDiv)) {
        try {
            document.body.removeChild(this.hydrateDiv);
            this.hydrateDiv = null;
        } catch (e) {}
    }
};

//---- CALLBACKS ----
YabiWorkflow.prototype.hydrateCallback = function(o) {
    var json = o.responseText;
    var i;
    var obj;
 
    o.argument[0].fadeHydratingDiv();

    target = o.argument[0];
    
    obj = YAHOO.lang.JSON.parse(json);
    
    //preprocess wrapper meta data
    target.setTags(obj.tags);
    
    target.setStatus(obj.status);
    
    target.solidify(obj.json);
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
    var anim;
    
    if (this.dragType == "job") {
        this.getEl().style.visibility = "";
    } else {
        this.jobEl.style.visibility = "";
        //this.jobEl.style.opacity = "1.0";

        anim = new YAHOO.util.Anim(this.jobEl, { opacity: { to: 1.0 } }, 0.3, YAHOO.util.Easing.Linear);
        anim.animate();

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
    var srcEl, midY;
    if (this.dragType == "job") {
        srcEl = this.getEl();
    } else {
        srcEl = this.jobEl;
    }

    if (destEl.className == "jobSuperContainer") {
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

YabiWorkflow.prototype.nameBlurCallback = function(e, obj) {
    if (obj.nameEl.value === "") {
        obj.nameEl.value = obj.prefillName;
    }
    obj.name = obj.nameEl.value;
};

YabiWorkflow.prototype.nameFocusCallback = function(e, obj) {
    if (obj.nameEl.value == obj.prefillName) {
        obj.nameEl.value = '';
    }
    
    return true;
};

YabiWorkflow.prototype.addTagCallback = function(e, obj) {
    //do stuff
    obj.tagAddLink.style.display = 'none';
    obj.tagListEl.style.display = 'none';
    obj.tagInputEl.style.display = 'inline';
    obj.tagHintDiv.className = "tagHint";
    obj.tagHelpEl.style.display = "block";
    var myAnim = new YAHOO.util.Anim(obj.tagHelpEl, { opacity: { to: 1 } }, 0.5, YAHOO.util.Easing.easeOut);
    myAnim.animate();
    obj.tagInputEl.focus();
};

YabiWorkflow.prototype.cancelTagsCallback = function(e, obj) {
    obj.cancelTagEditing();
};

YabiWorkflow.prototype.saveTagsCallback = function(e, obj) {
    //do stuff
    obj.saveTags();
};

YabiWorkflow.prototype.reuseCallback = function(e, obj) {
    //do stuff
    obj.reuse();
};

YabiWorkflow.prototype.saveTagsResponseCallback = function(o) {
    //do stuff
    YAHOO.ccgyabi.widget.YabiMessage.success("tags saved");
    var obj;
    
    try {
        obj = o.argument[0];
        obj.tagsFinishedSaving(o.argument[1]);
    } catch (e) {
        //do nothing
    }
};

YabiWorkflow.prototype.submitSuccessCallback = function(o, postRelocateCallback) {
    var json = o.responseText;
    var i;
    var obj;
 
    try {
        target = o.argument[0];
        
        obj = YAHOO.lang.JSON.parse(json);
        
        //we should have received an id
        if (!YAHOO.lang.isUndefined(obj.id)) { 
            target.workflowId = obj.id;
        
            target.saveTags(postRelocateCallback);
        }
        
    } catch (e) {
        YAHOO.ccgyabi.widget.YabiMessage.fail("Error loading workflow");
    }
};
