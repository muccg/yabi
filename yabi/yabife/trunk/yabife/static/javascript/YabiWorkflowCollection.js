// $Id: YabiWorkflowCollection.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiWorkflowCollection
 * fetch and render listing/grouping/smart filtering of workflows
 */
function YabiWorkflowCollection() {
    this.workflows = [];
    
    this.containerEl = document.createElement("div");
    this.containerEl.className = "workflowCollection";
    
    this.filterEl = document.createElement("div");
    this.filterEl.className = "filterPanel";
    
    this.searchLabelEl = document.createElement("label");
    this.searchLabelEl.appendChild(document.createTextNode("Find: "));
    this.filterEl.appendChild(this.searchLabelEl);
    
    this.searchEl = document.createElement("input");
    this.searchEl.className = "workflowSearchField";
    
    //attach key events for changes/keypresses
    YAHOO.util.Event.addListener(this.searchEl, "blur", this.filterCallback, this);
    YAHOO.util.Event.addListener(this.searchEl, "keyup", this.filterCallback, this);
    YAHOO.util.Event.addListener(this.searchEl, "change", this.filterCallback, this);
    
    this.filterEl.appendChild(this.searchEl);
    
    this.clearFilterEl = document.createElement("span");
    this.clearFilterEl.className = "fakeButton";
    this.clearFilterEl.appendChild( document.createTextNode(" show all ") );
    this.clearFilterEl.style.visibility = "hidden";
    YAHOO.util.Event.addListener(this.clearFilterEl, "click", this.clearFilterCallback, this);
    
    this.filterEl.appendChild(this.clearFilterEl);
    
    this.statusFilterContainer = document.createElement("div");
    this.statusFilterContainer.className = "filterStatus";
    this.statusFilterContainer.appendChild( document.createTextNode("Filter by status: ") );
    
    this.statusFilter = document.createElement("select");
    var statuses = ['All', 'Design', 'Running', 'Completed'];
    var tmpOpt;
    for (var index in statuses) {
        tmpOpt = document.createElement("option");
        tmpOpt.value = statuses[index];
        tmpOpt.text = statuses[index];
        this.statusFilter.appendChild( tmpOpt );
    }
    YAHOO.util.Event.addListener(this.statusFilter, "change", this.filterCallback, this);
    this.statusFilterContainer.appendChild(this.statusFilter);
    
    this.filterEl.appendChild(this.statusFilterContainer);
    
    this.containerEl.appendChild(this.filterEl);
    
    this.listingEl = document.createElement("div");
    this.listingEl.className = "workflowListing";
    
    this.loadingEl = document.createElement("div");
    this.loadingEl.className = "listingLoading";
    this.loadingEl.appendChild( document.createTextNode( " Loading... " ) );
    this.listingEl.appendChild(this.loadingEl);
    
    this.containerEl.appendChild(this.listingEl);
    
    this.hydrate();
}

YabiWorkflowCollection.prototype.solidify = function(obj) {
    var tempWorkflow;
    
    this.payload = obj;
    
    this.loadingEl.style.display = "none";
    
    var tmpWf;
    
    //clear out existing items
    while (this.workflows.length > 0) {
        tmpWf = this.workflows.pop();
        this.listingEl.removeChild(tmpWf.el);
        
        //remove event listeners etc
        tmpWf.destroy();
    }
    
    //add new items
    for (var index in obj) {
        tempWorkflow = new YabiWorkflowProxy(obj[index], this);
        
        this.listingEl.appendChild(tempWorkflow.el);
        
        this.workflows.push(tempWorkflow);
    }
    
    this.filter();
};

/**
 * hydrate
 * 
 * performs an AJAX json fetch of all the workflow listing details and data
 *
 */
YabiWorkflowCollection.prototype.hydrate = function() {
    var baseURL = "http://127.0.0.1:8002/workflow_query/ntakayama/";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
    success: this.hydrateResponse,
    failure: this.hydrateResponse,
        argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

YabiWorkflowCollection.prototype.toString = function() {
    return "tool collection";
};

/**
 * filter
 * 
 * use the search field to limit visible tools
 */
YabiWorkflowCollection.prototype.filter = function() {
    var filterVal = this.searchEl.value;
    var statusFilterVal = this.statusFilter.value;
    
    if (filterVal === "") {
        this.clearFilterEl.style.visibility = "hidden";
    } else {
        this.clearFilterEl.style.visibility = "visible";
    }
    
    for (var index in this.workflows) {
        if (this.workflows[index].matchesFilters(filterVal, statusFilterVal)) {
            this.workflows[index].el.style.display = "block";
        } else {
            this.workflows[index].el.style.display = "none";
        }
    }
};

/**
 * clearFilter
 */
YabiWorkflowCollection.prototype.clearFilter = function() {
    this.searchEl.value = "";
    this.filter();
};

YabiWorkflowCollection.prototype.select = function(id) {
    for (var i in this.workflows) {
        if (this.workflows[i].id == id) {
            this.workflows[i].setSelected(true);
        } else {
            this.workflows[i].setSelected(false);
        }
    }
};

// --------- callback methods, these require a target via their inputs --------

/**
 * filterCallback
 *
 */
YabiWorkflowCollection.prototype.filterCallback = function(e, target) {
    target.filter();
};

/**
 * clearFilterCallback
 *
 */
YabiWorkflowCollection.prototype.clearFilterCallback = function(e, target) {
    target.clearFilter();
};

/**
 * selectWorkflowCallback
 *
 * callback for selecting a workflow proxy object (and hence, loading the workflow)
 */
YabiWorkflowCollection.prototype.selectWorkflowCallback = function(e, invoker) {
    invoker.wfCollection.select(invoker.id);
};

/**
 * hydrateResponse
 *
 * handle the response
 * parse json, store internally
 */
YabiWorkflowCollection.prototype.hydrateResponse = function(o) {
    var i, json;
    
    try {
        json = o.responseText;
        
        target = o.argument[0];
        
        target.solidify(YAHOO.lang.JSON.parse(json));
    } catch (e) {
        YAHOO.ccgyabi.YabiMessage.yabiMessageFail("Error fetching workflow listing");
    }
};
