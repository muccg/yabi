// $Id: YabiJob.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiJob
 * create a new yabi job (node) corresponding to a tool
 */
function YabiJob(toolName, jobId, preloadValues) {
    this.loaded = false;
    this.toolName = toolName;
    this.displayName = toolName; //temporary while loading
    this.jobId = jobId;
    this.payload = {};
    this.preloadValues = preloadValues;
    if (this.preloadValues !== null && !YAHOO.lang.isArray(this.preloadValues)) {
        this.preloadValues = [this.preloadValues];
    }
    this.params = [];
    this.valid = false;
    this.acceptsInput = false;
    this.outputExtensions = [];
    this.nonMandatoryOptionsShown = false;
    this.editable = true; //default true
    this.showingProgress = false;
    this.progress = 0;
    this.workflow = null; //set later by the workflow
    this.batchParameter = null;
    
    //___CONTAINER EL___
    //this is used to retain the job's position in a workflow while alowing us to replace the jobEl
    this.containerEl = document.createElement("div");
    this.containerEl.className = "jobSuperContainer";
    
    //___JOB EL___
    this.jobEl = document.createElement("div");
    this.jobEl.setAttribute("class", "jobContainer");
    
    this.titleEl = document.createElement('h1');
    this.titleEl.appendChild(document.createTextNode("loading..."));
    this.jobEl.appendChild(this.titleEl);
    
    this.inputsEl = document.createElement('div');
    this.inputsEl.className = "jobInputs";
    this.inputsEl.appendChild(document.createTextNode("accepts: *"));
    this.jobEl.appendChild(this.inputsEl);
    
    this.outputsEl = document.createElement('div');
    this.outputsEl.className = "jobOutputs";
    this.outputsEl.appendChild(document.createTextNode("outputs: *"));
    this.jobEl.appendChild(this.outputsEl);

    //add the job el to the container    
    this.containerEl.appendChild(this.jobEl);
    
    //___OPTIONS EL___
    this.optionsEl = document.createElement('div');
    this.optionsEl.setAttribute("class", "jobOptionsContainer");
    
    this.optionsToggleEl = document.createElement('div');
    this.optionsToggleEl.className = "optionsToggle fakeButton";
    this.optionsToggleEl.appendChild(document.createTextNode('show all options'));
    YAHOO.util.Event.addListener(this.optionsToggleEl, "click", this.toggleOptionsCallback, this);
    this.optionsEl.appendChild(this.optionsToggleEl);
    
    this.optionsTitlePlaceholderEl = document.createTextNode('...');
    this.optionsTitleEl = document.createElement('h1');
    this.optionsTitleEl.appendChild(document.createTextNode('Options for '));
    this.optionsTitleEl.appendChild(this.optionsTitlePlaceholderEl);
    this.optionsEl.appendChild(this.optionsTitleEl);

}

/**
 * emittedFiles
 *
 * produces a list of files emitted from this job
 */
YabiJob.prototype.emittedFiles = function() {
    var files =  [];
    var subFiles;

    if (this.valid) {
        //console.log("valid");
        for (var index in this.params) {
            subFiles = this.params[index].emittedFiles();
            if (subFiles.length > 0) {
                files = files.concat(subFiles.slice());
            }
        }
    }
    
    //append the job to the end, so that any valid outputs take precedence over inputs
    files.push(this);
    
    //console.log(this + " emitting " + files);
    
    return files;
};

/**
 * emittedFileTypes
 *
 * produces a list of file types emitted by this job
 */
YabiJob.prototype.emittedFileTypes = function() {
    //if the tool outputs '*' then try to return instead a list of actual file extensions from param inputs
    var ef = this.emittedFiles();
    var finalExtension, value;
    var actualExtensions = [];
    if (this.outputExtensions.length === 1 && this.outputExtensions[0] === "*") {
        for (var index in ef) {
            if (ef[index] instanceof YabiJob) {
                continue;
            }

            value = ef[index].filename;
            if (value.lastIndexOf(".") < 0) {
                //skip this item if there is no extension
                continue;
            }

            finalExtension = value.substr( value.lastIndexOf(".") + 1 );
            actualExtensions.push(finalExtension);
        }
    }
    if (actualExtensions.length > 0) {
        return actualExtensions;
    }
    
    return this.outputExtensions;
};

/**
 * hydrate
 * 
 * performs an AJAX json fetch of all the tool details and data
 */
YabiJob.prototype.hydrate = function() {

    var baseURL = appURL + "ws/tool/";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL + this.toolName;
    jsCallback = {
            success: this.hydrateResponse,
            failure: this.hydrateResponse,
            argument: [this] };
    this.jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

/**
 * updateTitle
 *
 * used to update the node title (eg when re-ordering)
 */
YabiJob.prototype.updateTitle = function() {
    //TODO update this to use sequence instead of jobId
    var updatedTitle = this.toString();
    var updatedEl = document.createTextNode(updatedTitle);
    
    this.optionsTitleEl.replaceChild(updatedEl, this.optionsTitlePlaceholderEl);
    this.optionsTitlePlaceholderEl = updatedEl;
    
    //update job title too
    this.titleEl.replaceChild(document.createTextNode(updatedTitle), this.titleEl.firstChild);
    
    //update our name dependents and clear them
    if (!YAHOO.lang.isUndefined(this.nameDependents)) {
        for (var index in this.nameDependents) {
            this.nameDependents[index].appendChild(document.createTextNode(updatedTitle));
        }
        
        this.nameDependents = [];
    }
};

/**
 * checkValid
 *
 * iterates over params and checks their .valid flag
 */
YabiJob.prototype.checkValid = function(propagate) {
     this.valid = true;
     
     for (var param in this.params) {
         if (!this.params[param].valid) {
             this.valid = false;
         }
     }
     
     if (!this.valid) {
//        this.inputsEl.style.backgroundColor = "#ffefef";
        this.inputsEl.removeChild(this.acceptedExtensionEl);
        this.acceptedExtensionEl.setAttribute("class", "invalidAcceptedExtensionList");
        this.inputsEl.appendChild(this.acceptedExtensionEl);
    } else {
//        this.inputsEl.style.backgroundColor = "transparent";
        this.inputsEl.removeChild(this.acceptedExtensionEl);
        this.acceptedExtensionEl.setAttribute("class", "acceptedExtensionList");
        this.inputsEl.appendChild(this.acceptedExtensionEl);
    }
    
    if (propagate) {
        this.propagateFiles();
    }
};

/**
 * propagateFiles
 */
YabiJob.prototype.propagateFiles = function() {
    this.workflow.propagateFiles(this);
};
 
/**
 * optionallyConsumeFiles
 *
 * given an array of files, filter them down to each param to consume
 */
YabiJob.prototype.optionallyConsumeFiles = function(fileArray, propagate) {
    if (!this.acceptsInput) {
        return;
    }

    for (var index in this.params) {
         this.params[index].optionallyConsumeFiles(fileArray);
     }
     
     this.checkValid(propagate);
};

/**
 * selectJob
 */
YabiJob.prototype.selectJob = function() {
    if (this.failLoad) {
        return;
    }

    var child;
    var newEl = document.createElement("div");
    newEl.className = "selectedJobContainer";

    var count = this.jobEl.childNodes.length;
    for (var i = 0; i < count; i++) {
        child = this.jobEl.childNodes[0];
        this.jobEl.removeChild( child );
        newEl.appendChild( child );
    }
    
    this.containerEl.replaceChild(newEl, this.jobEl);
    
    this.jobEl = newEl;
    
    //show the options panel
    this.optionsEl.style.display = "block";
    
    //put focus on the first invalid param
    if (!this.valid) {
        for (var index in this.params) {
            if (!this.params[index].valid) {
                this.params[index].focus();
                break;
            }
        }
    }
};

/**
 * deselectJob
 */
YabiJob.prototype.deselectJob = function() {
    if (this.failLoad) {
        return;
    }

    var child;
    var newEl = document.createElement("div");
    newEl.className = "jobContainer";

    var count = this.jobEl.childNodes.length;
    for (var i = 0; i < count; i++) {
        child = this.jobEl.firstChild;
        this.jobEl.removeChild( child );
        newEl.appendChild( child );
    }
    
    this.containerEl.replaceChild(newEl, this.jobEl);
    
    this.jobEl = newEl;
    
    //hide the options panel
    this.optionsEl.style.display = "none";
};

/**
 * renderLoadFailJob
 */
YabiJob.prototype.renderLoadFailJob = function() {
    var newEl = document.createElement("div");
    newEl.className = "loadFailJobContainer";

    var child;
    var count = this.jobEl.childNodes.length;
    for (var i = 0; i < count; i++) {
        child = this.jobEl.childNodes[0];
        this.jobEl.removeChild( child );
        
        //skip the inputs and outputs elements as we are rendering this invalid
        if (child != this.inputsEl && child != this.outputsEl) {
            newEl.appendChild( child );
        }
    }
    
    this.containerEl.replaceChild(newEl, this.jobEl);
    
    this.jobEl = newEl;
    
    //hide the options panel
    this.optionsEl.style.display = "none";
};

/**
 * destroy
 *
 * cleans up properly
 */
YabiJob.prototype.destroy = function() {
    if (YAHOO.util.Connect.isCallInProgress( this.jsTransaction )) {
        YAHOO.util.Connect.abort( this.jsTransaction, null, false );
    }
    
    for (var param in this.params) {
        this.params[param].destroy();
    }
};

/**
 * toString
 */
YabiJob.prototype.toString = function() {
    return this.jobId + " - " + this.displayName;
};

YabiJob.prototype.toJSON = function() {
    var result = {  "toolName":this.toolName,
                    "jobId":this.jobId,
                    "valid":this.valid };
            
    var params = [];        
    for (var index in this.params) {
        if (this.params[index].toJSON() !== null) {
            params.push(this.params[index].toJSON());
        }
    }
    
    result.parameterList = {"parameter":params};
                    
    return result;
};

/**
 * isEqual
 *
 * simple comparison
 */
YabiJob.prototype.isEqual = function(b) {
    return this == b;
};

/**
 * toggleOptions
 *
 * show/hide all parameters
 */
YabiJob.prototype.toggleOptions = function() {
    if (this.nonMandatoryOptionsShown) {
        this.nonMandatoryOptionsShown = false;
        this.optionsToggleEl.innerHTML = "show all options";
        for (var index in this.params) {
            this.params[index].toggleDisplay(false);
        }
    } else {
        this.nonMandatoryOptionsShown = true;
        this.optionsToggleEl.innerHTML = "hide non-mandatory options";
        for (var bindex in this.params) {
            this.params[bindex].toggleDisplay(true);
        }
    }
};

/**
 * paramValue
 *
 * get the value of param
 */
YabiJob.prototype.paramValue = function(switchName) {
    for (var index in this.params) {
        if (this.params[index].switchName == switchName) {
            return this.params[index].getValue();
        }
    }
    
    return null;
};

/**
 * getParam
 *
 * get param object
 */
YabiJob.prototype.getParam = function(switchName) {
    for (var index in this.params) {
        if (this.params[index].switchName == switchName) {
            return this.params[index];
        }
    }
    
    return null;
};

/**
 * renderProgress
 *
 * render progress bar/badges
 */
YabiJob.prototype.renderProgress = function(status, completed, total, message) {
    if (YAHOO.lang.isUndefined(status)) {
        return;
    }

    if (!this.showingProgress) {
        this.renderStatus(status);

        this.progressContainerEl = document.createElement("div");
        this.progressContainerEl.className = "progressBarContainer";
        
        this.progressEl = document.createElement("div");
        this.progressEl.className = "progressBar";
        this.progressContainerEl.appendChild(this.progressEl);
        
        this.jobEl.appendChild(this.progressContainerEl);
        
        this.showingProgress = true;
    }
    
    //update status badge
    if (this.jobEl.removeChild(this.statusEl)) {
        this.renderStatus(status);
    }
    
    
    //if error
    if (status == 'error') {
        if (YAHOO.lang.isUndefined(message)) {
            message = '';
        } else {
            message = "\n" + message;
        }
        if (YAHOO.lang.isUndefined(this.errorEl)) {
            this.errorEl = document.createElement("div");
            this.errorEl.className = "jobErrorMsg";
            this.errorEl.appendChild( document.createTextNode("error running job "+message) );
            this.jobEl.appendChild(this.errorEl);
        }
    }

    if (YAHOO.lang.isUndefined(completed) || YAHOO.lang.isUndefined(total)) {
        return;
    }

    try {
        completed = parseFloat(completed);
        total = parseFloat(total);
    } catch (e) {
        return;
    }

    this.progress = 100 * completed / total;

    //update progress bar
    this.progressEl.style.width = this.progress + "%";
    
    //change color if in error
    if (status == "error") {
        this.progressEl.className = "progressBar errorBar";
    }
    
    //and hide the progress bar if the progress is 100%
    if (this.progress >= 100) {
        this.progressContainerEl.style.display = "none";
    }

};

/**
 * renderStatus
 *
 * Render the current status as a badge.
 */
YabiJob.prototype.renderStatus = function(status) {
    this.statusEl = document.createElement("div");
    this.statusEl.className = "badge" + status;
    this.jobEl.appendChild(this.statusEl);

    if (status != "pending") {
        this.statusTooltip = new YAHOO.widget.Tooltip("status-" + this.workflow.workflowId + "-" + this.jobId, {
            context: this.statusEl,
            text: "job status (click for more information)"
        });

        YAHOO.util.Event.addListener(this.statusEl, "click", this.showStatusCallback, this);
    }
};

/**
 * showStatus
 *
 * Shows the current job status in a popover element.
 */
YabiJob.prototype.showStatus = function() {
    var jobStatus = new YabiJobStatus(this);
    jobStatus.show();
};

/**
 * solidify
 *
 * takes a json object and uses it to populate/render all the job components
 */
YabiJob.prototype.solidify = function(obj) {
    this.payload = obj;

    var ext, spanEl, content, paramObj, index, paramIndex;
    
    this.titleEl.removeChild(this.titleEl.childNodes[0]);
    this.titleEl.appendChild(document.createTextNode(this.payload.tool.display_name));
    this.displayName = this.payload.tool.display_name;
    
    this.inputsEl.removeChild(this.inputsEl.childNodes[0]);
    var label = document.createElement("label");
    label.appendChild(document.createTextNode("accepts: "));
    this.inputsEl.appendChild(label);
    
    //input filetypes
    this.acceptedExtensionEl = document.createElement("div");
    this.acceptedExtensionEl.setAttribute("class", "acceptedExtensionList");
    this.inputsEl.appendChild(this.acceptedExtensionEl);
    
    if (!YAHOO.lang.isArray(this.payload.tool.inputExtensions)) {
        this.payload.tool.inputExtensions = [this.payload.tool.inputExtensions];
    }
    
    for (index in this.payload.tool.inputExtensions) {
        ext = document.createTextNode(this.payload.tool.inputExtensions[index]);
        spanEl = document.createElement("span");
        spanEl.setAttribute("class", "acceptedExtension");
        spanEl.appendChild(ext);
        this.acceptedExtensionEl.appendChild(spanEl);
    
        this.acceptedExtensionEl.appendChild(document.createTextNode(" "));
    }
    
    if (this.payload.tool.inputExtensions.length === 0) {
        ext = document.createTextNode("user input");
        spanEl = document.createElement("span");
        spanEl.setAttribute("class", "acceptedExtension");
        spanEl.appendChild(ext);
        this.acceptedExtensionEl.appendChild(spanEl);
        
        this.acceptedExtensionEl.appendChild(document.createTextNode(" "));
    }
    
    //output filetypes
    this.outputsEl.removeChild(this.outputsEl.childNodes[0]);
    label = document.createElement("label");
    label.appendChild(document.createTextNode("outputs: "));
    this.outputsEl.appendChild(label);


    this.outputExtensionEl = document.createElement("div");
    this.outputExtensionEl.setAttribute("class", "acceptedExtensionList");
    this.outputsEl.appendChild(this.outputExtensionEl);

    if (! YAHOO.lang.isUndefined(this.payload.tool.outputExtensions)) {

        if (!YAHOO.lang.isArray(this.payload.tool.outputExtensions)) {
            this.payload.tool.outputExtensions = [this.payload.tool.outputExtensions];
        }
        
        for (index in this.payload.tool.outputExtensions) {
            
            //add to the outputextensionsarray
            this.outputExtensions.push(this.payload.tool.outputExtensions[index].file_extension__extension);
            
            ext = document.createTextNode(this.payload.tool.outputExtensions[index].file_extension__extension);
            spanEl = document.createElement("span");
            spanEl.setAttribute("class", "acceptedExtension");
            spanEl.appendChild(ext);
            this.outputExtensionEl.appendChild(spanEl);
            
            this.outputExtensionEl.appendChild(document.createTextNode(" "));

        }
    }
    
    //batch on parameter
    if (! YAHOO.lang.isUndefined(this.payload.tool.batch_on_param)) {
        this.batchParameter = this.payload.tool.batch_on_param;
    }
    
    //does it accept inputs?
     if (this.payload.tool.accepts_input === true) {
         this.acceptsInput = true;
     }
    
    //generate parameter objects
    var params = this.payload.tool.parameter_list; //array

    var allMandatory = true;
    if (YAHOO.lang.isArray(params)) {
        for (paramIndex in params) {
            
            paramObj = new YabiJobParam(target, params[paramIndex], (params[paramIndex]["switch"] == this.batchParameter), this.editable, this.preloadValueFor(params[paramIndex]["switch"]));

            this.params.push(paramObj);
            this.optionsEl.appendChild(paramObj.containerEl);

            if (paramObj.payload.mandatory !== true) {
                allMandatory = false;
            }
        }
    } else {
        paramObj = new YabiJobParam(target, params, (params["switch"] == this.batchParameter), this.editable, this.preloadValueFor(params["switch"]));
        this.params.push(paramObj);
        this.optionsEl.appendChild(paramObj.containerEl);
        if (paramObj.payload.mandatory !== true) {
            allMandatory = false;
        }
    }
    
    //if all params are mandatory, hide the optionsToggle div
    if (allMandatory) {
        this.optionsToggleEl.style.display = "none";
    }
   
    //after first hydration, need to update validity
    if (this.editable) {
        this.checkValid();
    }
    
    //update the options title
    this.updateTitle();
    
    if (this.editable) {
        //tell workflow to propagate new variable info
        this.workflow.propagateFiles();
        
        //workflow delayed selectjob callback to allow propagation after this job is loaded
        this.workflow.delayedSelectJob(this);
    } 
    
    //now we are finished loading
    this.loaded = true;
};

/**
 * registerNameDependency
 *
 * allows spans or divs in other elements to be updated with the displayName of this job when it has loaded properly
 */
YabiJob.prototype.registerNameDependency = function(element) {
    if (YAHOO.lang.isUndefined(this.nameDependents)) {
        this.nameDependents = [];
    }
    
    this.nameDependents.push(element);
};

/**
 * preloadValueFor
 *
 * identifies the preload values for a given parameter
 */
YabiJob.prototype.preloadValueFor = function(switchName) {
    if (! YAHOO.lang.isUndefined(this.preloadValues) && this.preloadValues.length > 0) {
        for (var index in this.preloadValues) {
            if (! YAHOO.lang.isUndefined(this.preloadValues[index]) && this.preloadValues[index].switchName == switchName) {
                return this.preloadValues[index].value;
            }
        }
    }
    
    return null;
};

// --------- callback methods, these require a target via their inputs --------

/**
 * hydrateResponse
 *
 * handle the response
 * parse json, store internally
 */
YabiJob.prototype.hydrateResponse = function(o) {
    var i, json;

    try {
        json = o.responseText;
        
        target = o.argument[0];
        
        target.solidify(YAHOO.lang.JSON.parse(json));
        target.failLoad = false;
    } catch (e) {
        target.valid = false;
        target.failLoad = true;
        target.displayName = "(tool '"+ target.toolName +"' failed to load)";
        target.updateTitle();
        target.renderLoadFailJob();
        
        YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
    }
};

/**
 * toggleOptionsCallback
 *
 * callback when the show all options link is clicked
 */
YabiJob.prototype.toggleOptionsCallback = function(e, job) {
    job.toggleOptions();
};

/**
 * showStatusCallback
 *
 * Pop up a panel showing the current remote status of the selected job.
 */
YabiJob.prototype.showStatusCallback = function(e, job) {
    job.showStatus();
    YAHOO.util.Event.stopEvent(e);
};
