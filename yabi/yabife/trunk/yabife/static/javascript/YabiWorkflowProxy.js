// $Id: YabiWorkflowProxy.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiWorkflowProxy
 * render a single yabi workflow, for use in the search list results. can be used to summon a workflow for view/editing
 * or, ultimately, to re-use an entire workflow within a new workflow as a 'tool'
 */
function YabiWorkflowProxy(obj, collection) {
    
    this.payload = obj;
    this.detailsPayload = { 'name':this.payload.name }; //fallback value in case json parse fails
    this.collection = collection;
    
    this.id = obj.id;
    
    this.el = document.createElement("div");
    this.el.style.position = "relative";
    
    this.proxyEl = document.createElement("div");
    this.proxyEl.className = "workflowProxy";
    
    //parse a better name
    try {
        if (this.payload.json instanceof String) {
            this.detailsPayload = YAHOO.lang.JSON.parse(this.payload.json);
        }
    } catch (e) {}
    
    this.proxyEl.appendChild(document.createTextNode(this.detailsPayload.name));
    
    this.dateEl = document.createElement("div");
    this.dateEl.className = "workflowDate";
    this.dateEl.appendChild(document.createTextNode(this.payload.created_on));
    this.proxyEl.appendChild(this.dateEl);
    
    this.el.appendChild(this.proxyEl);
    
    this.badgeEl = document.createElement("div");
    this.badgeEl.className = "badge"+ obj.status;
    this.proxyEl.appendChild(this.badgeEl);
    
    this.tagEl = document.createElement("div");
    this.tagEl.className = "tagDiv";
    this.tagEl.appendChild(document.createTextNode(this.payload.tags));
    this.proxyEl.appendChild(this.tagEl);
        
    YAHOO.util.Event.addListener(this.proxyEl, "click", collection.selectWorkflowCallback, {"id":this.payload.id, "wfCollection":collection});
}

YabiWorkflowProxy.prototype.toString = function() {
    return this.payload.name;
};

YabiWorkflowProxy.prototype.destroy = function() {
    YAHOO.util.Event.purgeElement(this.proxyEl);
};

YabiWorkflowProxy.prototype.setSelected = function(state) {
    if (state) {
        //blah
        this.proxyEl.className = "selectedWorkflowProxy";
    } else {
        this.proxyEl.className = "workflowProxy";        
    }
};

YabiWorkflowProxy.prototype.setTags = function(tagArray) {
    this.payload.tags = tagArray;
    
    while (this.tagEl.firstChild) {
        this.tagEl.removeChild(this.tagEl.firstChild);
    }
    
    this.tagEl.appendChild( document.createTextNode(tagArray) );
};

/**
 * matchesFilter
 * 
 * returns true/false if it matches text and status
 */
YabiWorkflowProxy.prototype.matchesFilters = function(needle, status) {
    var index;
    var haystack = this.detailsPayload.name.toLowerCase();
    needle = needle.toLowerCase();
    status = status.toLowerCase();
    
    if (haystack.indexOf(needle) != -1) {
        if (status == 'all' || this.payload.status == status) {        
            return true;
        }
    }
    
    //add additional filters here on keywords
    var tagUnified = '' + this.payload.tags;
    tagUnified = tagUnified.toLowerCase();
    if (tagUnified.indexOf(needle) != -1) {
        if (status == 'all' || this.payload.status == status) {        
            return true;
        }
    }
    
    return false;
};
