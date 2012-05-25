YUI().use('node', 'event', 'dd-drag', 'dd-proxy', 'dd-drop', 'io', 'json', 'anim', function(Y) {

/**
 * YabiWorkflow
 * create a new workflow, which handles overall validation status as well
 * as ordering/sequencing and ensuring that file inputs are
 * managed in a sequential, logical manner
 */
YabiWorkflow = function(editable) {
  this.payload = {};
  this.isPropagating = false; //recursion protection
  this.tags = [];
  this.attachedProxies = [];

  //util fn
  var dblzeropad = function(number) {
    if (number < 10) {
      number = '0' + number;
    }
    return number;
  };
  var header;

  var date = new Date();
  if (editable) {
    this.name = 'unnamed (' +
        date.getFullYear() + '-' + dblzeropad(date.getMonth() + 1) + '-' +
        dblzeropad(date.getDate()) + ' ' +
        dblzeropad(date.getHours()) + ':' + dblzeropad(date.getMinutes()) +
        ')';
    this.prefillName = this.name;
  }

  this.status = 'Design';
  this.selectedJob = null;

  this.editable = true;
  if (editable !== null && editable === false) {
    this.editable = false;
  }

  this.jobs = [];

  this.containerEl = document.createElement('div');
  this.containerEl.className = 'workflowContainer';

  //construct the main dom, including title, submit (if editable) and bookends
  this.mainEl = document.createElement('div');

  if (this.editable) {
    this.submitEl = document.createElement('button');
    this.submitEl.appendChild(document.createTextNode('run'));
    this.submitEl.id = 'submitButton';
    this.submitEl.className = 'fakeButton largeButton';
    this.mainEl.appendChild(this.submitEl);

    this.nameEl = document.createElement('input');
    this.nameEl.className = 'workflowName';
    this.nameEl.id = 'titleDiv';
    this.nameEl.value = this.name;

    Y.one(this.nameEl).on('blur', this.nameBlurCallback, null, this);
    Y.one(this.nameEl).on('keyup', this.nameChangeCallback, null, this);
    Y.one(this.nameEl).on('change', this.nameChangeCallback, null, this);
    Y.one(this.nameEl).on('click', this.nameFocusCallback, null, this);
  } else {
    this.nameEl = document.createElement('div');
    this.nameEl.className = 'workflowName';
    this.nameEl.id = 'titleDiv';
  }

  this.mainEl.appendChild(this.nameEl);

  //tag el
  this.tagEl = document.createElement('div');
  this.tagEl.className = 'tagListContainer';
  this.tagEl.appendChild(document.createTextNode('Tags: '));

  this.tagListEl = document.createElement('span');
  this.tagListEl.className = 'tagList';
  this.tagEl.appendChild(this.tagListEl);

  this.tagInputEl = document.createElement('input');
  this.tagInputEl.className = 'displayNone';
  this.tagEl.appendChild(this.tagInputEl);

  this.tagAddLink = document.createElement('div');
  this.tagAddLink.className = 'tagAddLink';
  Y.one(this.tagAddLink).on('click', this.addTagCallback, null, this);
  this.tagEl.appendChild(this.tagAddLink);

  this.tagHintDiv = document.createElement('div');
  this.tagHintDiv.className = 'displayNone';

  this.tagCancelEl = document.createElement('span');
  this.tagCancelEl.className = 'fakeButton';
  this.tagCancelEl.appendChild(document.createTextNode('cancel'));
  Y.one(this.tagCancelEl).on('click', this.cancelTagsCallback, null, this);

  this.tagSaveEl = document.createElement('span');
  this.tagSaveEl.className = 'fakeButton';
  this.tagSaveEl.appendChild(document.createTextNode('save'));
  Y.one(this.tagSaveEl).on('click', this.saveTagsCallback, null, this);

  this.tagHintDiv.appendChild(this.tagCancelEl);
  this.tagHintDiv.appendChild(this.tagSaveEl);
  this.tagEl.appendChild(this.tagHintDiv);

  //tag help bubble
  this.tagHelpEl = document.createElement('div');
  this.tagHelpEl.className = 'tagHelp';
  var helpImg = new Image();
  helpImg.src = appURL + 'static/images/tagHelp.png';
  this.tagHelpEl.appendChild(helpImg);
  this.tagEl.appendChild(this.tagHelpEl);
  Y.one(this.tagHelpEl).on('click', function(e, obj) {
    var myAnim = new Y.Anim({
        node: Y.one(obj.tagHelpEl),
        to: { opacity: 0 },
        easing: 'easeOut',
        duration: 0.5
    });
    myAnim.on('end', function() {
        obj.tagHelpEl.style.display = 'none';
    }, this);
    myAnim.run();
  }, null, this);


  this.mainEl.appendChild(this.tagEl);

  if (!this.editable) {
    //actions toolbar
    this.toolbarEl = document.createElement('div');
    this.toolbarEl.className = 'workflowToolbar';
    this.mainEl.appendChild(this.toolbarEl);

    this.reuseButtonEl = document.createElement('span');
    this.reuseButtonEl.className = 'fakeButton';
    this.reuseButtonEl.appendChild(document.createTextNode('re-use'));
    Y.one(this.reuseButtonEl).on('click', this.reuseCallback, null, this);
    this.toolbarEl.appendChild(this.reuseButtonEl);
  }

  this.startEl = document.createElement('div');
  this.startEl.appendChild(document.createTextNode('start'));
  this.startEl.className = 'workflowStartBookend';

  this.mainEl.appendChild(this.startEl);

  //add empty workflow marker
  this.hintEl = document.createElement('div');
  this.hintEl.className = 'workflowHint';
  if (this.editable) {
    this.hintEl.innerHTML = '<div>drag tools here to begin<br />' +
        '(or use the <span>add</span> buttons)</div>';
    this.mainEl.appendChild(this.hintEl);
  }

  this.mainEl.appendChild(this.containerEl);

  this.endEl = document.createElement('div');
  this.endEl.appendChild(document.createTextNode('end'));
  this.endEl.className = 'workflowEndBookend';

  this.mainEl.appendChild(this.endEl);

  if (this.editable) {
    this.dd = new Y.DD.Drop({
        node: this.containerEl
    });
    this.dd.on('drop:over', this.onDragOverJobCallback);

    // TODO - see other registerDDTarget for TODO expl.
    YabiToolCollection.registerDDTarget(this.containerEl);
  }

  this.optionsEl = document.createElement('div');
  this.optionsEl.className = 'jobOptionsContainer';

  this.statusEl = document.createElement('div');
  this.statusEl.className = 'jobStatusContainer';

  if (!editable) {
    this.fileOutputsEl = document.createElement('div');
    this.fileOutputsEl.className = 'fileOutputs';
    header = document.createElement('h1');
    header.appendChild(document.createTextNode('File outputs'));
    this.fileOutputsEl.appendChild(header);

    // not editable, create a file selector to point at the
    // stageout directory if it exists
    this.fileOutputsSelector = new YabiFileSelector(null, true, null, true);
    this.fileOutputsSelector.homeEl.style.display = 'none';
    this.fileOutputsEl.appendChild(this.fileOutputsSelector.containerEl);
    this.fileOutputsEl.style.display = 'none';
    this.fileOutputsSelector.containerEl.style.marginLeft = '4px';
  }

  //add an enter key listener for the tags field
  Y.one(this.tagInputEl).on('keypress', function(e) {
    if (e.keyCode !== 13) {
      return;
    }
    this.saveTags();
  }, this);
}

YabiWorkflow.prototype.setStatus = function(statusText) {
  this.status = statusText.toLowerCase();

  //update proxies
  var proxy;
  for (index in this.attachedProxies) {
    proxy = this.attachedProxies[index];
    proxy.badgeEl.className = 'badge' + this.status;
    proxy.payload.status = this.status;
  }

  if (this.editable) {
    return;
  }

  var loadImg;
  if (this.status !== 'complete') {
    if (Y.Lang.isUndefined(this.loadingEl) || this.loadingEl === null) {
      this.loadingEl = document.createElement('div');
      this.loadingEl.className = 'workflowLoading';
      loadImg = new Image();
      loadImg.src = appURL + 'static/images/processing.gif';
      this.loadingEl.appendChild(loadImg);

      this.loadingTextEl = document.createElement('span');
    }

    this.loadingTextEl.innerHTML = 'workflow running, ' +
                                   'waiting for completion...';
    this.loadingEl.appendChild(this.loadingTextEl);

    this.mainEl.appendChild(this.loadingEl);
  } else {
    //completed or error, remove the loadingEl
    if (Y.Lang.isUndefined(this.loadingEl) ||
        this.loadingEl === null) {
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
YabiWorkflow.prototype.addJob = function(toolName,
                                         preloadValues, shouldFadeIn) {

  if (this.processing) {
    return;
  }
  this.processing = true;

  this.hintEl.style.display = 'none';

  var invoke, destroyEl, destroyImg;

  var job = new YabiJob(toolName, this.jobs.length + 1, preloadValues);
  job.editable = this.editable;
  if (!this.editable) {
    job.inputsEl.style.display = 'none';
    job.outputsEl.style.display = 'none';
  }
  job.workflow = this;
  this.jobs.push(job);

  job.hydrate();

  if (!this.editable) {
    //attach events
    invoke = {'target': this, 'object': job};
    Y.one(job.containerEl).on('click', this.selectJobCallback, null, invoke);

    //don't select any job (ie select null)
    this.selectJob(null);
  } else {
    //decorate the job with a 'destroy' link
    destroyEl = document.createElement('div');
    destroyEl.setAttribute('class', 'destroyDiv');
    destroyImg = new Image();
    destroyImg.title = 'delete tool';
    destroyImg.alt = destroyImg.title;
    destroyImg.src = appURL + 'static/images/delnode.png';
    destroyEl.appendChild(destroyImg);
    job.jobEl.appendChild(destroyEl);

    //attach events
    invoke = {'target': this, 'object': job};
    Y.one(destroyEl).on('click', this.delJobCallback, null, invoke);
    Y.one(job.containerEl).on('click', this.selectJobCallback, null, invoke);

    //drag drop
    job.dd = new Y.DD.Drag({
        node: job.containerEl,
        target: {}
    }).plug(Y.Plugin.DDProxy, {
        moveOnEnd:false
    });

    // TODO
    // We are registering this as DD.Drops in the YUI instance of the tool
    // collection, otherwise the tools can't be dropped on top of the job
    // elements. There has to be a better way to do this!
    YabiToolCollection.registerDDTarget(job.containerEl);

    job.dd.on('drag:start', this.startDragJobCallback);
    job.dd.on('drag:end', this.endDragJobCallback);
    job.dd.on('drag:drag', this.onDragJobCallback);
    job.dd.on('drag:over', this.onDragOverJobCallback);

   //select the new item but only if we are editable
    this.selectJob(job);
  }

  if (Y.Lang.isUndefined(shouldFadeIn)) {
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
    var anim = new Y.Anim({
        node: Y.one(job.containerEl),
        to: { opacity: 1.0 },
        duration: 1.0
    });
    anim.run();
  }

  this.processing = false;

  return job;
};


/**
 * deleteJob
 *
 * this uses simple locking to prevent multiple deletes happening concurrently,
 * which causes validation errors
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
    this.hintEl.style.display = 'block';
  }

  job.destroy();

  this.containerEl.removeChild(job.containerEl);
  this.optionsEl.removeChild(job.optionsEl);
  this.statusEl.removeChild(job.statusEl);

  Y.one(job.containerEl).detachAll();

  //force propagate
  this.propagateFiles();

  this.deleting = false;
};


/**
 * attachProxy
 *
 * attaches a workflowProxy to this workflow, so that changes in this workflow
 * are propagated back to the proxy
 */
YabiWorkflow.prototype.attachProxy = function(proxy) {
  this.attachedProxies.push(proxy);
};


/**
 * propagateFiles
 *
 * iterates over the jobs, querying the jobs for their emittedOutputs, using
 * those outputs to prefill following jobs the optional 'sender' param is to
 * specify which node to start propagating from, to prevent trying to cause
 * that and previous jobs from consuming their own values into oblivion
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
  if (Y.Lang.isUndefined(sender)) {
    foundSender = true;
  }

  // iterate
  for (var index in this.jobs) {
    // do not allow the sender or above to consume
    if (foundSender) {
      this.jobs[index].optionallyConsumeFiles(emittedFiles, false);
    }
    // flag that the sender is found, after the optional consume, so the
    //  sender doesn't consume
    if (this.jobs[index] == sender) {
      foundSender = true;
    }

    subEmitted = this.jobs[index].emittedFiles().slice();
    if (subEmitted.length > 0) {
      for (var subindex in subEmitted) {
        // duplicates have a value
        if (!emittedKeys.hasOwnProperty(subEmitted[subindex])) {
          emittedFiles.push(subEmitted[subindex]);
          emittedKeys[subEmitted[subindex]] = 1;
        }
      }
    }
  }
  this.isPropagating = false;

  //afterPropagate call for other objects to hook in to
  if (!Y.Lang.isUndefined(this.afterPropagate) &&
      !Y.Lang.isUndefined(sender)) {
    this.afterPropagate(sender);
  }
};


/**
 * selectJob
 *
 * tells a job to render as selected, and tells all other jobs to render
 * deselected
 */
YabiWorkflow.prototype.selectJob = function(object) {
  if (!this.editable) {
    this.fileOutputsEl.style.display = 'none';
  }

  //iterate
  var selectedIndex = null;
  for (var index in this.jobs) {
    if (this.jobs[index] == object) {
      if (object == this.selectedJob) {
        this.jobs[index].deselectJob();
        this.selectedJob = null;

        // callback hook to allow other elements to hook in when jobs are
        // selected/deselected
        if (!Y.Lang.isUndefined(this.afterSelectJob) && object.loaded) {
          this.afterSelectJob(null);
        }
      } else {
        selectedIndex = index;
      }
    } else {
      this.jobs[index].deselectJob();
    }
  }

  /* Firing selectJob() used to occur within the for loop, but it's more
     * logically sensible (and makes it easier to write code handling
     * deselection and selection) to make all the deselectJob() calls above and
     * then fire selectJob() last. */
  if (selectedIndex !== null) {
    this.jobs[selectedIndex].selectJob();
    this.selectedJob = object;

    if (!this.editable &&
        !Y.Lang.isUndefined(this.payload.jobs[selectedIndex].stageout)) {
      this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue(
          [this.payload.jobs[selectedIndex].stageout], ''));
    }

    // callback hook to allow other elements to hook in when jobs are
    // selected/deselected
    if (!Y.Lang.isUndefined(this.afterSelectJob) && object.loaded) {
      this.afterSelectJob(object);
    }
  }
};


/**
 * delayedSelectJob
 *
 * exists for the purpose of allowing an afterSelectJob callback after a
 * tool has loaded
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
    return 'unknown';
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

  if (this.getName() === '' || this.getName().indexOf('?') != -1) {
    this.nameEl.className = 'invalidWorkflowName';
    return false;
  } else {
    this.nameEl.className = 'workflowName';
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
  var result = { 'name': this.name, 'tags': this.tags };

  var jobs = [];
  for (var index in this.jobs) {
    jobs.push(this.jobs[index].toJSON());
  }

  result.jobs = jobs;
  return Y.JSON.stringify(result);
};


/**
 * hydrate
 *
 * fetch workflow definition from the server
 */
YabiWorkflow.prototype.hydrate = function(workflowId) {
  var loadImg;

  if (Y.Lang.isUndefined(this.workflowId)) {
    this.hydrateDiv = document.createElement('div');
    this.hydrateDiv.className = 'workflowHydrating';
    loadImg = new Image();
    loadImg.src = appURL + 'static/images/largeLoading.gif';
    this.hydrateDiv.appendChild(loadImg);
    document.body.appendChild(this.hydrateDiv);
  }

  this.workflowId = workflowId;
  var baseURL = appURL + 'ws/workflows/get/' + workflowId;

  //load json
  var jsUrl, jsCallback, jsTransaction;
  jsUrl = baseURL;
  jsCallback = {
    success: this.hydrateCallback,
    failure: function(transId, o) {
      YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
    }
  };
  var cfg = {
    on: jsCallback,
    "arguments": {
        target: this
    }
  };
  this.jsTransaction = Y.io(jsUrl, cfg);

};

YabiWorkflow.prototype.fadeHydratingDiv = function() {
  //fade out and remove the loading element
  var anim = new Y.Anim({
      node: Y.one(this.hydrateDiv),
      to: { opacity: 0 },
      duration: 0.3
  });
//  anim.on('end', function() {
//    document.body.removeChild(this.hydrateDiv);
//  }, this);
  anim.run();
};


/**
 * reuse
 *
 * reload the whole page with a reuse URL
 */
YabiWorkflow.prototype.reuse = function() {
  var baseURL = appURL + 'design/reuse/' + this.workflowId;

  window.location = baseURL;
};


/**
 * saveTags
 *
 * save tags
 */
YabiWorkflow.prototype.saveTags = function(postRelocate) {
  this.tagInputEl.blur();

  if (Y.Lang.isUndefined(this.workflowId)) {
    this.tagsFinishedSaving();
    return;
  }

  var baseURL = appURL + 'ws/workflows/' + this.workflowId + '/tags';

  //load json
  var jsUrl, jsCallback, jsTransaction;
  jsUrl = baseURL;
  jsCallback = {
    success: this.saveTagsResponseCallback,
    failure: function(transId, o) { 
        YAHOO.ccgyabi.widget.YabiMessage.fail(
            'Error saving tags'); }
  };
  var cfg = {
    method: 'POST',
    data: 'taglist=' + escape(this.tagInputEl.value),
    on: jsCallback,
    "arguments": {
        target: this,
        callback: postRelocate
    }
  };
  Y.io(jsUrl, cfg);
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
  this.tagListEl.appendChild(document.createTextNode(this.tags));

  for (index in obj.jobs) {
    if (updateMode) {
      job = this.jobs[index];
    } else {
      job = this.addJob(obj.jobs[index].toolName,
                        obj.jobs[index].parameterList.parameter);
    }
    if (!this.editable) {
      oldJobStatus = job.status;

      job.renderProgress(obj.jobs[index].status, obj.jobs[index].tasksComplete,
                         obj.jobs[index].tasksTotal);

      if (this.selectedJob == job && oldJobStatus != job.status) {
        this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue(
            [this.payload.jobs[index].stageout], ''));
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
  if (this.status.toLowerCase() !== 'completed') {
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
  if (this.tagInputEl.style.display != 'inline') {
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
  this.tagHintDiv.className = 'displayNone';
  this.tagInputEl.style.display = 'none';
  this.tagListEl.style.display = 'inline';
  this.tagAddLink.style.display = 'block';
  var anim = new Y.Anim({
      node: Y.one(this.tagHelpEl),
      to: { opacity: 0 },
      easing: 'easeOut',
      duration: 0.5
  });
  anim.on('end', function() {
    this.tagHelpEl.style.display = 'none';
  }, this);
  anim.run();
};


/**
 * tagsFinishedSaving
 *
 * hide editing fields, solidify tags editing field into an array
 */
YabiWorkflow.prototype.tagsFinishedSaving = function(postRelocate) {
  this.tags = this.tagInputEl.value.split(',');
  while (this.tagListEl.firstChild) {
    this.tagListEl.removeChild(this.tagListEl.firstChild);
  }
  this.tagListEl.appendChild(document.createTextNode('' + this.tags));

  //notify attached proxies
  for (var index in this.attachedProxies) {
    this.attachedProxies[index].setTags(this.tags);
  }

  this.tagHintDiv.className = 'displayNone';
  this.tagInputEl.style.display = 'none';
  this.tagListEl.style.display = 'inline';
  this.tagAddLink.style.display = 'block';
  var anim = new Y.Anim({
      node: Y.one(this.tagHelpEl),
      to: { opacity: 0 },
      easing: 'easeOut',
      duration: 0.5
  });
  anim.on('end', function() {
    this.tagHelpEl.style.display = 'none';
  }, this);
  anim.run();

  //if postRelocate != undefined then redirect user to the jobs tab
  if (!Y.Lang.isUndefined(postRelocate)) {
    postRelocate(this.workflowId);
  }
};


/**
 * destroy
 *
 * delete any internal variables and dom handlers
 */
YabiWorkflow.prototype.destroy = function() {
  if (!Y.Lang.isUndefined(this.jsTransaction) && 
      this.jsTransaction.isInProgress()) {
    this.jsTransaction.abort();
  }

  var job;

  for (var index in this.jobs) {
    job = this.jobs[index];

    job.destroy();

    this.containerEl.removeChild(job.containerEl);
    this.optionsEl.removeChild(job.optionsEl);
    this.statusEl.removeChild(job.statusEl);

    Y.one(job.containerEl).detachAll();
  }

  //purge all listeners on nameEl
  Y.one(this.nameEl).detachAll();

  //remove the workflow from its container
  this.mainEl.parentNode.removeChild(this.mainEl);

  if (!Y.Lang.isUndefined(this.fileOutputsEl)) {
    this.fileOutputsEl.parentNode.removeChild(this.fileOutputsEl);
  }

  if (!Y.Lang.isUndefined(this.hydrateDiv)) {
    try {
      document.body.removeChild(this.hydrateDiv);
      this.hydrateDiv = null;
    } catch (e) {}
  }
};

//---- CALLBACKS ----
YabiWorkflow.prototype.hydrateCallback = function(transId, o, args) {
  var json = o.responseText;
  var i;
  var obj;

  args.target.fadeHydratingDiv();

  target = args.target;

  obj = Y.JSON.parse(json);

  //preprocess wrapper meta data
  target.setTags(obj.tags);

  target.setStatus(obj.status);

  target.solidify(obj.json);
};

YabiWorkflow.prototype.delJobCallback = function(e, invoke) {
  e.halt(true);
  invoke.target.deleteJob(invoke.object);
  //prevent propagation of the event to select/deselecting the job
};

YabiWorkflow.prototype.selectJobCallback = function(e, invoke) {
  e.halt(true);
  var workflow = invoke.target;

  workflow.selectJob(invoke.object);

};

YabiWorkflow.prototype.startDragJobCallback = function(e) {
  var dragNode = e.target.get('dragNode');
  var node = e.target.get('node');

  node.setStyle('visibility', 'hidden');
  dragNode.set('innerHTML', node.get('innerHTML'));
  dragNode.setStyles({
        border: 'none',
        textAlign: 'left'
  });

  this.dragType = 'job';
  this.lastY = dragNode.getY();
};

YabiWorkflow.prototype.endDragJobCallback = function(e) {
  var anim;
  var drag = e.target.get('node');

  if (this.dragType == 'job') {
    drag.setStyle('visibility', '');
  } else {
    this.jobEl.style.visibility = '';
    //this.jobEl.style.opacity = "1.0";

    var anim = new Y.Anim({
      node: Y.one(this.jobEl),
      to: { opacity: 1.0 },
      duration: 0.3
    });
    anim.run();

    this.optionsEl.style.display = 'block';
  }
  //this.getDragEl().style.visibility = 'hidden';

  // identify the new location, recreating the jobs array based on
  // current div locations
  var alteredJobs = [];
  var counter = 1;
  var job;
  for (var index in workflow.containerEl.childNodes) {
    var childNode = workflow.containerEl.childNodes[index];
    for (var jobindex in workflow.jobs) {
      if (workflow.jobs[jobindex].containerEl == childNode) {
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
  var y = e.target.get('dragNode').getY();

  if (y < this.lastY) {
    this.goingUp = true;
  } else if (y > this.lastY) {
    this.goingUp = false;
  }
  this.lastY = y;
};


YabiWorkflow.prototype.onDragOverJobCallback = function(e) {
  e.halt(true);
  var drag = e.drag.get('node'),
      drop = e.drop.get('node');

  if (this.dragType !== 'job') {
    drag = Y.one(this.jobEl);
  }  
  
  if (drop.hasClass('jobSuperContainer')) {
        //Are we not going up?
      if (!this.goingUp) {
        drop = drop.get('nextSibling');
      }
      //Add the node to this list
      e.drop.get('node').get('parentNode').insertBefore(drag, drop);
      //Resize this nodes shim, so we can drop on it later.
      e.drop.sizeShim();
  }
};

YabiWorkflow.prototype.nameChangeCallback = function(e, obj) {
  obj.name = obj.nameEl.value;
};

YabiWorkflow.prototype.nameBlurCallback = function(e, obj) {
  if (obj.nameEl.value === '') {
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
  obj.tagHintDiv.className = 'tagHint';
  obj.tagHelpEl.style.display = 'block';
  var anim = new Y.Anim({
      node: Y.one(obj.tagHelpEl),
      to: { opacity: 1 },
      easing: 'easeOut',
      duration: 0.5
  });
  anim.run();
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

YabiWorkflow.prototype.saveTagsResponseCallback = function(transId, o, args) {
  //do stuff
  YAHOO.ccgyabi.widget.YabiMessage.success('tags saved');
  var obj;

  try {
    obj = args.target;
    obj.tagsFinishedSaving(args.callback);
  } catch (e) {
    //do nothing
  }
};

YabiWorkflow.prototype.submitSuccessCallback = function(o,
    postRelocateCallback, target) {
  var json = o.responseText;
  var i;
  var obj;

  try {
    obj = Y.JSON.parse(json);

    //we should have received an id
    if (!Y.Lang.isUndefined(obj.id)) {
      target.workflowId = obj.id;

      target.saveTags(postRelocateCallback);
    }

  } catch (e) {
    YAHOO.ccgyabi.widget.YabiMessage.fail('Error loading workflow');
  }
};

}); // end of YUI().use(...
