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

// Globals for workflow design page
var workflow, tools;


var YabiApp = {
  // If initDesignPage is called before it is set up save the argument
  // it has been called with and call after it has been set up.
  _initWithId: -1,
  initDesignPage: function(reuseId) {
    this._initWithId = reuseId;
  }
};

YUI().use(
  'node', 'event', 'io', 'dd', function(Y) {

  function initWorkflow(reuseId) {
    var reusing = reuseId == null ? false : true;
    tools = new YabiToolCollection();

    Y.one("#toolContainer").append(tools.containerNode);

    workflow = new YabiWorkflow(true, reusing);

    if (reusing) {
      workflow.hydrate(reuseId);
      workflow.workflowId = undefined;
    }

    var updateFilter = function(job) {
      if (!tools.autofilter) {
        return;
      }

      var searchFilter = job ? "in:" + job.emittedFileTypes() : "";
      tools.searchNode.set("value", searchFilter);
      tools.filter();

      // Resize the file selector to roughly fit the available space.
      var fs = Y.one(".fileSelector");
      var height = Yabi.util.getViewportHeight();
      if (fs && height) {
        var top = Yabi.util.getElementOffset(fs.getDOMNode()).top;

        // The 30 pixels is pure, unadulterated fudge factor.
        var height = height - top - 30;

        Y.one(".fileSelectorBrowse").setStyle("minHeight", height + "px");
      }
    };

    workflow.afterSelectJob = updateFilter;
    workflow.afterPropagate = updateFilter;

    Y.one("#container").append(workflow.mainEl);
    Y.one("#optionsDiv").append(workflow.optionsEl);

    Y.one("#submitButton").on("click", submitCallback, null, workflow);
  }

  //this function is used after a workflow is submitted,
  //and after the tags have been saved,
  //to redirect the browser to view this particular workflow using a hashtag
  var summonJobsView = function(workflowId) {
    window.location = appURL + 'jobs#' + workflowId;
  };

  function submitCallback(e, wf) {

    // TODO add decent callbacks
    e.halt(true);

    if (!wf.isValid()) {
      var msg = "Workflow isn't valid. Please correct errors before submitting.";
      YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
    } else {

      var baseURL = appURL + "ws/workflows/submit/";

      jsCallback = {
        success: function(transId, obj, args) {
          YAHOO.ccgyabi.widget.YabiMessage.success("Success on submit!");
          workflow.deleteDraft(true);
          workflow.submitSuccessCallback(obj, summonJobsView, args.target);
        },
        failure: function(transId, obj) {
          YAHOO.ccgyabi.widget.YabiMessage.fail("Fail on submit!");
        }
      };
      var data = "username=" + YAHOO.ccgyabi.username +
        "&workflowjson=" + encodeURIComponent(wf.toJSON());
      var cfg = {
        method: 'POST',
        on: jsCallback,
        data: data,
        "arguments": {
          target: wf
        }
      };

      Yabi.util.setCSRFHeader(Y.io);
      jsTransaction = Y.io(baseURL, cfg);
    }
  };

  YabiApp.initDesignPage = function(reuseId) {
    initWorkflow(reuseId);
  };

  // initDesignPage has been called before it was set up
  if (YabiApp._initWithId !== -1) {
    YabiApp.initDesignPage(YabiApp._initWithID);
    YabiApp._initWithId = -1;
  }
 });
