/**
 * YabiJobStatus
 *
 * Create a Job Status popup.
 */
function YabiJobStatus(job, workflow) {
    this.job = job;

    if (workflow) {
        this.workflow = workflow;
    }
    else {
        this.workflow = job.workflow;
    }
}

/**
 * createPanel
 *
 * Given a header line and a div to act as a body element, creates a
 * YAHOO.widget.Panel and returns it.
 */
YabiJobStatus.prototype.createPanel = function(headerText, bodyEl) {
    var header = document.createElement("div");
    header.className = "hd";
    header.appendChild(document.createTextNode(headerText));

    bodyEl.className = "bd";

    var div = document.createElement("div");
    div.className = "status-overlay";
    div.appendChild(header);
    div.appendChild(bodyEl);

    var panel = new YAHOO.widget.Panel(div, {
        close: true,
        constraintoviewport: true,
        draggable: false,
        fixedcenter: true,
        modal: true,
        underlay: "shadow",
        zIndex: 999
    });

    bodyEl.style.maxHeight = (YAHOO.util.Dom.getViewportHeight() * 0.75) + "px";
    bodyEl.style.maxWidth = (YAHOO.util.Dom.getViewportWidth() * 0.75) + "px";

    return panel;
};

/**
 * show
 *
 * Shows the popup.
 */
YabiJobStatus.prototype.show = function() {
    var self = this;

    var callbacks = {
        success: function(o) { self.showCallback(o); },
        failure: function() {
            YAHOO.ccgyabi.YabiMessage.yabiMessageFail("Error loading job status");
        }
    };

    var url = "engine/job/" + this.workflow.workflowId + "/" + (this.job.jobId - 1);
    var req = YAHOO.util.Connect.asyncRequest("GET", url, callbacks);
};

/**
 * showCallback
 *
 * Called to handle the JSON status information.
 */
YabiJobStatus.prototype.showCallback = function(o) {
    try {
        var obj = YAHOO.lang.JSON.parse(o.responseText);
        var task = obj.tasks[0];

        var body = document.createElement("div");

        var list = document.createElement("dl");
        body.appendChild(list);

        if (task.remote_info) {
            var keys = [];

            for (var key in task.remote_info) {
                if (YAHOO.lang.hasOwnProperty(task.remote_info, key)) {
                    keys.push(key);
                }
            }

            keys.sort();

            for (var i in keys) {
                if (YAHOO.lang.hasOwnProperty(keys, i)) {
                    (function() {
                        var key = keys[i];

                        var title = document.createElement("dt");
                        title.appendChild(document.createTextNode(key));

                        var data = document.createElement("dd");
                        data.appendChild(document.createTextNode(task.remote_info[key]));

                        list.appendChild(title);
                        list.appendChild(data);
                    })();
                }
            }
        }
        else {
            YAHOO.ccgyabi.YabiMessage.yabiMessageWarn("No status information is available for this job");
            return;
        }

        var panel = this.createPanel("job status", body);
        panel.render(document.body);
    }
    catch (e) {
        YAHOO.ccgyabi.YabiMessage.yabiMessageFail("Error loading job status");
    }
};
