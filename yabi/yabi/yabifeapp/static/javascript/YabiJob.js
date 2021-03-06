/*
 * Yabi - a sophisticated online research environment for Grid, High Performance
 * and Cloud computing.
 * Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  */


/**
 * YabiJob
 * create a new yabi job (node) corresponding to a tool
 */
function YabiJob(toolName, toolId, jobId, preloadValues) {
  this.loaded = false;
  this.toolName = toolName;
  this.displayName = toolName; //temporary while loading
  this.toolId = toolId;
  this.jobId = jobId;
  this.payload = {};
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
  this.nameDependents = [];
  this.errorNode = null;

  // make preloadValues a map from switch name to switch value
  var listify = function(ob) { return Y.Lang.isArray(ob) ? ob : [ob]; };
  this.preloadValues = _(preloadValues ? listify(preloadValues) : [])
    .indexBy("switchName").mapValues("value").value();

  //___CONTAINER NODE___
  // this is used to retain the job's position in a workflow while
  // allowing us to replace the jobEl
  this.container = Y.Node.create('<div class="jobSuperContainer"/>');

  //___JOB NODE___
  this.jobNode = Y.Node.create('<div class="jobContainer"/>')
    .appendTo(this.container);
  this.titleNode = Y.Node.create('<span>loading...</span>');
  this.backendNode = Y.Node.create('<span class="backend"/>');
  Y.Node.create('<h1/>')
    .append(this.titleNode)
    .append(this.backendNode)
    .appendTo(this.jobNode);

  this.inputsNode = Y.Node.create('<div class="jobInputs">accepts: *</div>')
    .appendTo(this.jobNode);
  this.outputsNode = Y.Node.create('<div class="jobOutputs">outputs: *</div>')
    .appendTo(this.jobNode);
  var optionsHtml = '<div class="jobOptionsMissing">options: ' +
    '<span class="invalidInput">mandatory options are missing</span></div>';
  this.optionsMissingNode = Y.Node.create(optionsHtml)
    .appendTo(this.jobNode).hide();

  //___OPTIONS NODE___
  this.optionsNode = Y.Node.create('<div class="jobOptionsContainer"/>');

  this.optionsToggle = Y.Node.create('<div class="optionsToggle fakeButton">show all options</div>')
    .appendTo(this.optionsNode);
  this.optionsToggle.on('click', function(e, job) {
    job.nonMandatoryOptionsShown = !job.nonMandatoryOptionsShown;
    _.forEach(job.params, function(param) {
      param.toggleDisplay(job.nonMandatoryOptionsShown);
    });

    this.set("text", job.nonMandatoryOptionsShown ?
             'hide non-mandatory and uncommon options' :
             'show all options');
  }, null, this);

  this.optionsTitle = Y.Node.create("<h1>Options for ...</h1>")
    .appendTo(this.optionsNode);

  //___STATUS NODE___
  this.statusNode = Y.Node.create('<div class="jobStatus"/>');

  this.statusTitle = Y.Node.create('<h1>Remote status</h1>')
    .appendTo(this.statusNode);

  this.statusError = Y.Node.create('<div/>')
    .set("text", 'No status information is available for this job.')
    .appendTo(this.statusNode);

  this.statusList = Y.Node.create('<dl/>').appendTo(this.statusNode);
}


/**
 * emittedFiles
 *
 * produces a list of files emitted from this job
 */
YabiJob.prototype.emittedFiles = function() {
  var files = [];
  var subFiles;

  if (this.valid) {
    _.forEach(this.params, function(param) {
      subFiles = param.emittedFiles();
      if (subFiles.length > 0) {
        files = files.concat(subFiles.slice());
      }
    });
  }

  // append the job to the end, so that any valid outputs take
  // precedence over inputs
  files.push(this);

  return files;
};


/**
 * emittedFileTypes
 *
 * produces a list of file types emitted by this job
 */
YabiJob.prototype.emittedFileTypes = function() {
  // if the tool outputs '*' then try to return instead a list of actual
  // file extensions from param inputs
  var ef = this.emittedFiles();
  var finalExtension, value;
  var actualExtensions = [];
  if (this.outputExtensions.length === 1 && this.outputExtensions[0] === '*') {
    for (var index in ef) {
      if (ef[index] instanceof YabiJob) {
        continue;
      }

      value = ef[index].filename;
      if (value.lastIndexOf('.') < 0) {
        //skip this item if there is no extension
        continue;
      }

      finalExtension = '*.' + value.substr(value.lastIndexOf('.') + 1);
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
  YabiToolCache.get(this.toolId,
                    _.bind(this.hydrateResponse, this),
                    _.bind(this.hydrateResponseFailed, this));
};


/**
 * updateTitle
 *
 * used to update the node title (eg when re-ordering)
 */
YabiJob.prototype.updateTitle = function() {
  // TODO update this to use sequence instead of jobId
  var updatedTitle = this.toString();

  this.optionsTitle.set("text", "Options for " + updatedTitle);

  // update job title too
  this.titleNode.set("text", updatedTitle);

  // update our name dependents and clear them
  _.forEach(this.nameDependents, function(dep) {
    Y.Node.create(updatedTitle).appendTo(dep);
  });

  this.nameDependents = [];
};


/**
 * checkValid
 *
 * iterates over params and checks their .valid flag
 */
YabiJob.prototype.checkValid = function(propagate) {
  var invalidParams = _.reject(this.params, "valid");
  var inputFilesInvalid = _.any(invalidParams, "isInputFile");
  var otherParamsInvalid = !_.every(invalidParams, "isInputFile");

  this.valid = invalidParams.length == 0;

  this.inputsNode.all(".acceptedExtensionList")
    .toggleClass("invalidAcceptedExtensionList", inputFilesInvalid);

  this.optionsMissingNode.toggleView(otherParamsInvalid);

  if (propagate) {
    this.propagateFiles();
    this.workflow.onJobChanged(this);
  }
  if (this.valid) {
    this.valid = this.payload.tool.enabled;
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

  _.forEach(this.params, function(param) {
    param.optionallyConsumeFiles(fileArray);
  });

  this.checkValid(propagate);
};


/**
 * selectJob
 */
YabiJob.prototype.selectJob = function() {
  if (this.failLoad) {
    return;
  }

  this.jobNode.addClass("selectedJobContainer");

  //show the options panel
  if (this.editable) {
    this.optionsNode.show();
    this.statusNode.hide();
  }
  else {
    this.optionsNode.addClass('active');
    this.statusNode.addClass('active');
  }

  //put focus on the first invalid param
  _(this.params).reject("valid").forEach(function(param) {
    param.focus();
    return false;
  });
};


/**
 * deselectJob
 */
YabiJob.prototype.deselectJob = function() {
  if (this.failLoad) {
    return;
  }

  this.jobNode.removeClass("selectedJobContainer");

  //hide the options panel
  if (this.editable) {
    this.optionsNode.hide();
    this.statusNode.hide();
  }
  else {
    this.optionsNode.removeClass('active');
    this.statusNode.removeClass('active');
  }
};


/**
 * renderLoadFailJob
 */
YabiJob.prototype.renderLoadFailJob = function() {
  this.jobNode.replaceClass("jobContainer", "loadFailJobContainer");
  this.jobNode.removeClass("selectedJobContainer");
  //hide the options panel
  this.optionsNode.hide();
  this.statusNode.hide();
};


/**
 * destroy
 *
 * cleans up properly
 */
YabiJob.prototype.destroy = function() {
  _.forEach(this.params, function(param) { param.destroy(); });
};


/**
 * toString
 */
YabiJob.prototype.toString = function() {
  return this.jobId + ' - ' + this.displayName;
};

YabiJob.prototype.toJSON = function() {
  return {
    toolName: this.toolName,
    toolId: this.toolId,
    jobId: this.jobId,
    valid: this.valid,
    parameterList: {
      parameter: _(this.params)
        .map(function(param) { return param.toJSON(); })
        .compact().valueOf()
    }
  };
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
 * renderJobStatus
 *
 * Render job status.
 */
YabiJob.prototype.renderJobStatus = function() {
  // Get job status, if we can.
  var self = this;

  var callbacks = {
    success: function(transId, o) {
      var obj = Y.JSON.parse(o.responseText);
      self.renderJobStatusResponse(obj);
    },
    failure: function(transId, o) {
      self.renderJobStatusError();
    }
  };

  this.statusList.hide();
  this.statusError.hide();
  this.statusLoading = new YAHOO.ccgyabi.widget.Loading(this.statusNode.getDOMNode());
  this.statusLoading.show();

  var url = 'engine/job/' + this.workflow.workflowId + '/' + (this.jobId - 1);
  Y.io(url, {on: callbacks});
};


/**
 * renderJobStatusError
 *
 * Render the job status error message.
 */
YabiJob.prototype.renderJobStatusError = function() {
  this.statusLoading.destroy();
  this.statusList.hide();
  this.statusError.show();
};


/**
 * renderJobStatusResponse
 *
 * Render job status.
 */
YabiJob.prototype.renderJobStatusResponse = function(obj) {
  var task = obj.tasks[0];

  this.statusList.empty();

  if (task && task.remote_info) {
    var keys = [];

    for (var key in task.remote_info) {
      if (task.remote_info.hasOwnProperty(key)) {
        keys.push(key);
      }
    }

    keys.sort();

    _.forEach(keys, function(key) {
      this.statusList
        .append(Y.Node.create('<dt/>').set("text", key))
        .append(Y.Node.create('<dd/>').set("text", task.remote_info[key]));
    }, this);

    this.statusLoading.destroy();

    this.statusList.show();
    this.statusError.hide();
  }
  else {
    this.renderJobStatusError();
  }
};


/**
 * renderProgress
 *
 * render progress bar/badges
 */
YabiJob.prototype.renderProgress = function(status, is_retrying, completed,
                                            total, message) {
  if (Y.Lang.isUndefined(status)) {
    return;
  }

  if (!this.showingProgress) {
    this.renderStatusBadge(status, is_retrying);

    this.progressContainer = Y.Node.create('<div class="progressBarContainer"/>')
      .appendTo(this.jobNode);
    this.progressNode = Y.Node.create('<div class="progressBar"/>')
      .appendTo(this.progressContainer);

    this.showingProgress = true;
  }

  //update status badge
  if (this.badgeNode.remove()) {
    this.renderStatusBadge(status, is_retrying);
  }

  //if error
  if (status == 'error') {
    this.addErrorMsg('error running job' + (message ? '\n' + message : ''));
  }

  if (status == 'aborted') {
    this.addErrorMsg('job aborted');
  }

  if (Y.Lang.isUndefined(completed) || Y.Lang.isUndefined(total)) {
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
  this.progressNode.setStyle("width", this.progress + '%');

  //change color if in error
  this.progressNode.toggleClass('errorBar', status == 'error');

  //and hide the progress bar if the progress is 100%
  this.progressContainer.toggleView(this.progress < 100);
};

/**
 * addErrorMsg
 *
 * Puts red text on the job.
 */
YabiJob.prototype.addErrorMsg = function(text) {
  if (!this.errorNode) {
    this.errorNode = Y.Node.create('<div class="jobErrorMsg"/>')
      .set("text", text).appendTo(this.jobNode);
  }
};


/**
 * renderStatusBadge
 *
 * Render the current status as a badge.
 */
YabiJob.prototype.renderStatusBadge = function(status, is_retrying) {
  if (is_retrying) {
      status = 'retrying';
  }
  this.badgeNode = Y.Node.create('<img class="badge"/>')
    .set("title", 'Job ' + Yabi.util.Status.getStatusDescription(status))
    .set("src", imagesURL + Yabi.util.Status.getStatusImage(status))
    .appendTo(this.jobNode);
};


YabiJob.prototype.fixPayload = function(obj) {
  if (!Y.Lang.isArray(obj.tool.inputExtensions)) {
    obj.tool.inputExtensions = [obj.tool.inputExtensions];
  }
  if (Y.Lang.isUndefined(obj.tool.outputExtensions)) {
    obj.tool.outputExtensions = [];
  } else if (!Y.Lang.isArray(obj.tool.outputExtensions)) {
    obj.tool.outputExtensions = [obj.tool.outputExtensions];
  }
  if (!Y.Lang.isArray(obj.tool.parameter_list)) {
    obj.tool.parameter_list = [obj.tool.parameter_list];
  }
  if (obj.tool.backend == "nullbackend") {
    obj.tool.backend = null;
  }
  return obj;
};

/**
 * solidify
 *
 * takes a json object and uses it to populate/render all the job components
 */
YabiJob.prototype.solidify = function(obj) {
  this.payload = this.fixPayload(obj);

  var ext, spanEl, content, paramObj, index, paramIndex;

  this.titleNode.set("text", this.payload.tool.display_name);
  this.backendNode
    .set("text", this.payload.tool.backend)
    .toggleView(this.payload.tool.backend ? true : false);
  this.displayName = this.payload.tool.display_name;
  if (!this.payload.tool.enabled) {
      this.displayName = 'Disabled Tool: ' + this.displayName;
      this.valid = false;
      this.jobNode.addClass("disabled");
  }

  var setupExtensions = function(title, node, extensions) {
    node.empty();
    var label = Y.Node.create('<label/>').set("text", title + ": ")
      .appendTo(node);

    var extList = Y.Node.create('<span class="acceptedExtensionList"/>')
      .appendTo(node);

    var acceptedExtension = function(text) {
      return Y.Node.create('<span class="acceptedExtension"/>')
        .set("text", text);
    };

    var addExt = function(text) {
      extList.append(acceptedExtension(text))
        .append(document.createTextNode(" "));
    };

    if (extensions.length === 0) {
      addExt("user input");
    } else {
      _.forEach(extensions, function(ext) {
        addExt(ext.file_extension__pattern || ext);
      });
    }
    return node;
  };

  setupExtensions("accepts", this.inputsNode, this.payload.tool.inputExtensions);
  setupExtensions("outputs", this.outputsNode, this.payload.tool.outputExtensions);

  //add to the outputextensionsarray
  this.outputExtensions = _.pluck(this.payload.tool.outputExtensions,
                                  "file_extension__pattern");

  //batch on parameter
  this.batchParameter = this.payload.tool.batch_on_param || null;

  //does it accept inputs?
  this.acceptsInput = this.payload.tool.accepts_input ? true : false;

  //generate parameter objects
  var allShown = true;

  _.forEach(this.payload.tool.parameter_list, function(param) {
    var preloadValue = this.preloadValues[param['switch']] || null;

    if (this.editable || preloadValue) {
      var paramObj = new YabiJobParam(this, param,
            (param['switch'] == this.batchParameter),
            this.editable, preloadValue);
      this.params.push(paramObj);

      if (!param.hidden) {
        this.optionsNode.append(paramObj.containerEl);
      }

      if (!(paramObj.payload.mandatory || paramObj.payload.common)) {
        allShown = false;
      }
    }
  }, this);

  //if all params are shown, hide the optionsToggle div
  this.optionsToggle.toggleView(!allShown);

  //after first hydration, need to update validity
  if (this.editable) {
    this.checkValid();
  }

  // update the options title
  this.updateTitle();

  if (this.editable) {
    // tell workflow to propagate new variable info
    this.workflow.propagateFiles();

    // workflow delayed selectjob callback to allow propagation after
    // this job is loaded
    this.workflow.delayedSelectJob(this);
  }

  // now we are finished loading
  this.loaded = true;

  this.workflow.onJobLoaded(this);
};


/**
 * registerNameDependency
 *
 * allows spans or divs in other elements to be updated with the displayName
 * of this job when it has loaded properly
 */
YabiJob.prototype.registerNameDependency = function(element) {
  this.nameDependents.push(element);
};


// --------- callback methods, these require a target via their inputs --------


/**
 * hydrateResponse
 *
 * handle the response
 * parse json, store internally
 */
YabiJob.prototype.hydrateResponse = function(o) {
  var payload = null;

  try {
    payload = Y.JSON.parse(o.responseText);
    this.failLoad = false;
    this.solidify(payload);
  } catch (e) {
    this.hydrateResponseFailed(o);
  }
};


YabiJob.prototype.hydrateResponseFailed = function(o) {
  var payload = null;
  this.valid = false;
  this.failLoad = true;
  var msg = "Tool '" + this.toolName + "' failed to load";
  if (o.status === 403) {
      var msg = "You don't have access to tool '" + this.toolName + "'";
  } else if (o.status === 404) {
      var msg = "Tool '" + this.toolName + "' not found";
  }
  this.displayName = "(" + msg + ")";
  this.updateTitle();
  this.renderLoadFailJob();

  YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
};
