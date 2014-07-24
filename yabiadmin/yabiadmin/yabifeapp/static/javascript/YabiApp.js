// globals for workflow design page
var workflow, tools;

var YabiApp = {};

YUI().use(
  'node', 'event', 'io', 'dd',
  function(Y) {
    YabiApp.initDesignPage = (function() {
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
          YAHOO.ccgyabi.widget.YabiMessage.fail("Workflow isn't valid. Please correct errors before submitting.");
        } else {

          var baseURL = appURL + "ws/workflows/submit/";

          jsCallback = {
            success: function (transId, obj, args) {
              YAHOO.ccgyabi.widget.YabiMessage.success("Success on submit!");
              workflow.deleteDraft(true);
              workflow.submitSuccessCallback(obj, summonJobsView, args.target);
            },
            failure: function (transId, obj) {
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
          jsTransaction = Y.io(baseURL, cfg);
        }
      }

      return initWorkflow;
    })();

  });
