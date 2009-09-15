// $Id: YabiToolCollection.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiToolCollection
 * fetch and render listing/grouping/smart filtering of tools
 */
function YabiToolCollection() {
    this.tools = [];

    this.containerEl = document.createElement("div");
    this.containerEl.className = "toolCollection";
    
    this.filterEl = document.createElement("div");
    this.filterEl.className = "filterPanel";
    
    this.searchLabelEl = document.createElement("label");
    this.searchLabelEl.appendChild(document.createTextNode("Find tool: "));
    this.filterEl.appendChild(this.searchLabelEl);
    
    this.searchEl = document.createElement("input");
    this.searchEl.className = "toolSearchField";
    
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
    
    this.containerEl.appendChild(this.filterEl);
    
    this.listingEl = document.createElement("div");
    this.listingEl.className = "toolListing";
    
    this.loadingEl = document.createElement("div");
    this.loadingEl.className = "listingLoading";
    this.loadingEl.appendChild( document.createTextNode( " Loading... " ) );
    this.listingEl.appendChild(this.loadingEl);
    
    this.containerEl.appendChild(this.listingEl);

    this.hydrate();
}

YabiToolCollection.prototype.solidify = function(obj) {
    var tempTool;
    
    this.payload = obj;
    
    this.loadingEl.style.display = "none";

    for (var toolsetindex in obj.menu.toolsets) {

        for (var index in obj.menu.toolsets[toolsetindex].toolgroups) {

            var toolgroup = obj.menu.toolsets[toolsetindex].toolgroups[index];

            tempGroupEl = document.createElement("div");
            tempGroupEl.className = "toolGroup";
            tempGroupEl.appendChild(document.createTextNode(toolgroup.name));
            this.listingEl.appendChild(tempGroupEl);
        
            for (var subindex in toolgroup.tools) {
                tempTool = new YabiTool(toolgroup.tools[subindex], this);
            
                this.listingEl.appendChild(tempTool.el);
            
                //drag drop
                tempTool.dd = new YAHOO.util.DDProxy(tempTool.el);
                tempTool.dd.startDrag = this.startDragToolCallback;
                tempTool.dd.endDrag = workflow.endDragJobCallback;
                tempTool.dd.onDrag = workflow.onDragJobCallback;
                tempTool.dd.onDragOver = workflow.onDragOverJobCallback;

                this.tools.push(tempTool);
            }
        }
    }
};

/**
 * hydrate
 * 
 * performs an AJAX json fetch of all the tool details and data
 *
 */
YabiToolCollection.prototype.hydrate = function() {
    var baseURL = "http://127.0.0.1:8000/ws/menu/andrew/";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
            success: this.hydrateResponse,
            failure: this.hydrateResponse,
            argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

YabiToolCollection.prototype.toString = function() {
    return "tool collection";
};

/**
 * filter
 * 
 * use the search field to limit visible tools
 */
YabiToolCollection.prototype.filter = function() {
    var filterVal = this.searchEl.value;
    
    if (filterVal === "") {
        this.clearFilterEl.style.visibility = "hidden";
    } else {
        this.clearFilterEl.style.visibility = "visible";
    }
    
    for (var index in this.tools) {
        if (this.tools[index].matchesFilter(filterVal)) {
            this.tools[index].el.style.display = "block";
        } else {
            this.tools[index].el.style.display = "none";
        }
    }
};

/**
 * clearFilter
 */
YabiToolCollection.prototype.clearFilter = function() {
    this.searchEl.value = "";
    this.filter();
};

// --------- callback methods, these require a target via their inputs --------

/**
 * filterCallback
 *
 */
YabiToolCollection.prototype.filterCallback = function(e, target) {
    target.filter();
};

/**
 * clearFilterCallback
 *
 */
YabiToolCollection.prototype.clearFilterCallback = function(e, target) {
    target.clearFilter();
};

/**
 * addCallback
 *
 * local callback for adding a tool
 */
YabiToolCollection.prototype.addCallback = function(e, obj) {
    workflow.addJob(obj);
};

/**
 * hydrateResponse
 *
 * handle the response
 * parse json, store internally
 */
YabiToolCollection.prototype.hydrateResponse = function(o) {
    var i, json;

    try {
        json = o.responseText;
        
        target = o.argument[0];
        
        target.solidify(YAHOO.lang.JSON.parse(json));
    } catch (e) {
        console.log(e);
    }
};

YabiToolCollection.prototype.startDragToolCallback = function(x, y) {
    var tool;

    //work out which tool it is
    for (var index in tools.tools) {
        console.log("comparing "+tools.tools[index].toString());
        if (this.getEl() == tools.tools[index].el) {
            tool = tools.tools[index];
            break;
        }
    }
    
    if (YAHOO.lang.isUndefined(tool)) {
        console.log("failed to find tool");
        return false;
    }

    var job = workflow.addJob(tool.toString());
    job.containerEl.style.visibility = "hidden";
    job.optionsEl.style.display = "none";
    
    this.jobEl = job.containerEl;
    this.optionsEl = job.optionsEl;

    this.getDragEl().style.border = "none";
    this.getDragEl().style.textAlign = "left";
    this.getDragEl().innerHTML = this.getEl().innerHTML;
    this.getDragEl().removeChild(YAHOO.util.Dom.getLastChild(this.getDragEl())); //remove the 'add' image from the dragged item
    
    this.dragType = "tool";
    this.lastY = y;
};
