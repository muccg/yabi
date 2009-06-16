// $Id: YabiTool.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiTool
 * render a single yabi tool
 */
function YabiTool(obj, collection) {

    this.payload = obj;
    this.collection = collection;

    this.el = document.createElement("div");
    this.el.style.position = "relative";
    
    this.toolEl = document.createElement("div");
    this.toolEl.className = "tool";
    this.toolEl.appendChild(document.createTextNode(this.payload.displayName));
    
    this.el.appendChild(this.toolEl);
    
    var addEl = new Image();
    addEl.src = "/static/images/addtool.gif";
    addEl.className = "addLink";
    YAHOO.util.Event.addListener(addEl, "click", collection.addCallback, this.payload.name);
    this.el.appendChild(addEl);
}

YabiTool.prototype.toString = function() {
    return this.payload.name;
};

/**
 * matchesFilter
 * 
 * returns true/false if it matches text
 */
YabiTool.prototype.matchesFilter = function(needle) {
    var index;

    if (this.payload.displayName.indexOf(needle) != -1) {
        return true;
    }
    
    if (needle.indexOf("*.") === 0) {
        needle = needle.substring(2);
        
        for (index in this.payload.inputExtensions) {
            if (this.payload.inputExtensions[index].extension == needle) {
                return true;
            }
        }
        
        for (index in this.payload.outputExtensions) {
            if (this.payload.outputExtensions[index].extension == needle) {
                return true;
            }        
        }
    }
    
    if (needle.indexOf("in:") === 0) {
        needle = needle.substring(3);
        
        for (index in this.payload.inputExtensions) {
            if (this.payload.inputExtensions[index].extension == needle) {
                return true;
            }
        }
    }

    return false;
};