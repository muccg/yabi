// $Id: YabiToolCollection.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiToolCollection
 * fetch and render listing/grouping/smart filtering of tools
 */
function YabiToolCollection() {
    this.tools = [];
    this.groupEls = [];
    this.autofilter = true;
    
    this.containerEl = document.createElement("div");
    this.containerEl.className = "toolCollection";
    
    this.filterEl = document.createElement("div");
    this.filterEl.className = "filterPanel";
    
    this.searchLabelEl = document.createElement("label");
    this.searchLabelEl.appendChild(document.createTextNode("Find tool: "));
    this.filterEl.appendChild(this.searchLabelEl);
    
    this.searchEl = document.createElement("input");
    this.searchEl.setAttribute("type", "search");
    this.searchEl.className = "toolSearchField";
    
    //attach key events for changes/keypresses
    YAHOO.util.Event.addListener(this.searchEl, "blur", this.filterCallback, this);
    YAHOO.util.Event.addListener(this.searchEl, "keyup", this.filterCallback, this);
    YAHOO.util.Event.addListener(this.searchEl, "change", this.filterCallback, this);
    YAHOO.util.Event.addListener(this.searchEl, "search", this.filterCallback, this);
    
    this.filterEl.appendChild(this.searchEl);
    
    this.clearFilterEl = document.createElement("span");
    this.clearFilterEl.className = "fakeButton";
    this.clearFilterEl.appendChild( document.createTextNode(" show all ") );
    this.clearFilterEl.style.visibility = "hidden";
    YAHOO.util.Event.addListener(this.clearFilterEl, "click", this.clearFilterCallback, this);

    this.filterEl.appendChild(this.clearFilterEl);
    
    //autofilter
    this.autofilterContainer = document.createElement('div');
    this.autofilterContainer.className = "autofilterContainer";
    this.autofilterContainer.appendChild( document.createTextNode('Use selection to auto-filter?') );
    
    this.autofilterEl = document.createElement("span");
    this.autofilterEl.className = "virtualCheckboxOn";
    this.autofilterEl.appendChild( document.createTextNode('on') );

    YAHOO.util.Event.addListener(this.autofilterEl, "click", this.autofilterCallback, this);
    this.autofilterContainer.appendChild(this.autofilterEl);
    
    this.filterEl.appendChild(this.autofilterContainer);
    
    this.containerEl.appendChild(this.filterEl);
    
    //no results div
    this.noResultsDiv = document.createElement("div");
    this.noResultsDiv.className = 'wfNoResultsDiv';
    this.noResultsDiv.appendChild(document.createTextNode('no matching tools'));
    this.containerEl.appendChild(this.noResultsDiv);
    
    this.listingEl = document.createElement("div");
    this.listingEl.className = "toolListing";
    
    this.loading = new YAHOO.ccgyabi.widget.Loading(this.listingEl);
    this.loading.show();
    
    this.containerEl.appendChild(this.listingEl);

    this.searchEl.value = "select";
    this.filter();
    
    this.hydrate();
}

YabiToolCollection.prototype.solidify = function(obj) {
    var tempTool;
    var toolgroup;
    
    this.payload = obj;
    
    this.loading.hide();

    for (var toolsetindex in obj.menu.toolsets) {

        for (var index in obj.menu.toolsets[toolsetindex].toolgroups) {

            toolgroup = obj.menu.toolsets[toolsetindex].toolgroups[index];

            tempGroupEl = document.createElement("div");
            tempGroupEl.className = "toolGroup";
            tempGroupEl.appendChild(document.createTextNode(toolgroup.name));
            this.listingEl.appendChild(tempGroupEl);
            
            this.groupEls.push(tempGroupEl);
            
            for (var subindex in toolgroup.tools) {
                tempTool = new YabiTool(toolgroup.tools[subindex], this, tempGroupEl);
            
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
    
    this.filter();
};

/**
 * hydrate
 * 
 * performs an AJAX json fetch of all the tool details and data
 *
 */
YabiToolCollection.prototype.hydrate = function() {
    var baseURL = appURL + "ws/menu/";
    
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
    var visibleCount = 0;
    
    if (filterVal === "") {
        this.clearFilterEl.style.visibility = "hidden";
    } else {
        this.clearFilterEl.style.visibility = "visible";
    }
    
    for (var gindex in this.groupEls) {
        this.groupEls[gindex].style.display = "none";
    }
    
    for (var index in this.tools) {
        if (this.tools[index].matchesFilter(filterVal)) {
            this.tools[index].el.style.display = "block";
            this.tools[index].groupEl.style.display = "block";
            visibleCount++;
        } else {
            this.tools[index].el.style.display = "none";
        }
    }

    if (visibleCount === 0) {
        if (this.tools.length !== 0) {
            this.noResultsDiv.style.display = "block";
        }
    } else {
        this.noResultsDiv.style.display = "none";
    }
};

/**
 * clearFilter
 */
YabiToolCollection.prototype.clearFilter = function() {
    this.searchEl.value = "";
    this.filter();
};

/**
 * autofilterToggle
 */
YabiToolCollection.prototype.autofilterToggle = function() {
    this.autofilter = !this.autofilter;
    
    if (this.autofilter) {
        this.autofilterEl.className = "virtualCheckboxOn";
        this.autofilterEl.innerHTML = "on";
    } else {
        this.autofilterEl.className = "virtualCheckbox";
        this.autofilterEl.innerHTML = "off";
    }
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
 * autofilterCallback
 *
 * toggle autofiltering
 */
YabiToolCollection.prototype.autofilterCallback = function(e, target) {
    target.autofilterToggle();
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
        YAHOO.ccgyabi.widget.YabiMessage.fail("Error fetching tools listing");
        target.solidify({'menu':{'toolsets':[]}});
    }
};

YabiToolCollection.prototype.startDragToolCallback = function(x, y) {
    var tool;

    //work out which tool it is
    for (var index in tools.tools) {
        //console.log("comparing "+tools.tools[index].toString());
        if (this.getEl() == tools.tools[index].el) {
            tool = tools.tools[index];
            break;
        }
    }
    
    if (YAHOO.lang.isUndefined(tool)) {
        YAHOO.ccgyabi.widget.YabiMessage.fail("Failed to find tool");
        return false;
    }

    var job = workflow.addJob(tool.toString(), undefined, false);
    //job.containerEl.style.visibility = "hidden";
    job.containerEl.style.opacity = "0.1";
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
