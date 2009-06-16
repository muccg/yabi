// $Id: listSelector.js 4232 2009-03-04 04:25:25Z ntakayama $

/**
 * ListSelector
 */
function ListSelector(id) {
    if(id){
        this.collectionEl = YAHOO.util.DDM.getElement(id);
        this.optionsCache = new OptionsCache('optionsDiv');
    }
    this.cloneCounter = 0;
    
    //default empty selectors to invalid
    this.containsValidationErrors = true;
}


/**
 * getCloneCounter
 */
ListSelector.prototype.getCloneCounter = function() {
    return this.cloneCounter++;
};


/**
 * update
 * 
 * Should be called whenever a workunit is moved, selected etc
 * delayoptions is used to not load options
 * div when dragging from tools list
 */
ListSelector.prototype.update = function(el, delayOptions) {

    // build array of workflowunit objects
    var units = [];
    var children = this.collectionEl.childNodes;
    var i, j;
    var prevUnit = null;
    var elId = null;
    if (el !== null){
        elId = el.id;
    }

    //abort early if the item clicked is still just a tool template and hasn't been added to the workflow
    if (elId !== null && elId.match('yabi-tool') !== null) {
        return;
    }

    // build an array of workunits, assigning their prev and next units
    // only include valid workunits, not markers etc
    for (i=0;i< children.length;i++) {

        if(children[i].nodeType == 1 && this.isWorkUnit(children[i].id)) {
            workflowUnit = new WorkflowUnit(children[i], this.optionsCache);
            workflowUnit.setBasePath(this.basePath);

            workflowUnit.setPrevUnit(prevUnit);

            if(prevUnit !== null) {
                prevUnit.setNextUnit(workflowUnit);
            }
            prevUnit = workflowUnit;
            units.push(workflowUnit);
        }
    }


    //set form validation to prevent submission of empty workflows and ones with bad filetypes being passed
    var foundInvalid = false;
    
    // update all workunits
    for (i=0; i<units.length; i++) {
        units[i].update(elId, delayOptions);
        if (units[i].validated === false) {
            foundInvalid = true;
        }
    }

    //set an invalid flag for form submission
    if (units.length < 1 || foundInvalid === true) {
        this.containsValidationErrors = true;
    } else {
        this.containsValidationErrors = false;
    }

    // update order in hidden form element
    this.mungeOrder();
};


/**
 * remoteUpdate
 *
 * We now want to call update from elements other than the workflow units
 * i.e. from dropdown menus. As long as you have the id of the corresponding 
 * workflow unit (e.g clone_3) this wrapper function will help you call update
 */
ListSelector.prototype.remoteUpdate = function(elId, delayOptions) {

    if(elId !== null && elId !== "") {
        elem = document.getElementById(elId);
        this.update(elem, delayOptions);
    }
};


/**
 * isWorkUnit
 *
 * Checks the element id and returns true if it is not a marker and is defined
 */
ListSelector.prototype.isWorkUnit = function(id) {

    if(id == 'startMarker' || id == 'cleanup' || id =='endMarker' || id == 'hinting' || id === undefined) {
        return false;
    } else {
        return true;
    }

};


/**
 * mungeOrder
 */
ListSelector.prototype.mungeOrder = function() {
    //used to populate a form field with the ordering of component divs in the workflow
    //to be called whenever a 'select' is called (because select is called whenever a new item is placed or moved)
    //and also whenever 'destruct' is called. this should trap all instances
    var children = this.collectionEl.childNodes;
    var orderField = document.getElementById('workflowOrder');
    var values = "";
    var foundStartMarker = false;
    var elem;
    var toolName;
    var toolNum;
    var dashIndex;
    var displayNum = 1;

    for (var i=0;i<children.length;i++) {
        //skip text elements
        if (children[i].nodeType != 1) {
            continue;
        }

        if (foundStartMarker && children[i].id != 'hinting') {
        	elem = YAHOO.util.Dom.getElementsByClassName('toolName', null, children[i].id )[0];
	        displayNameElem = YAHOO.util.Dom.getElementsByClassName('toolDisplayName', null, children[i].id )[0];

            if (displayNameElem) {
	        	toolNum = displayNameElem.innerHTML.substr(0, 1);
	        	if ((toolNum >= 0) && (toolNum <= 9)) {
	        		// remove the numbering prefix if it already exists
	        		dashIndex = displayNameElem.innerHTML.indexOf('-');
	        		displayNameElem.innerHTML = displayNameElem.innerHTML.slice(dashIndex+2);
	        	}

        		displayNameElem.innerHTML = displayNum + " - " + displayNameElem.innerHTML;

                displayNum++;
	        }

        	if (elem) {
	        	toolName = elem.innerHTML;
                values = values + ',' + displayNameElem.innerHTML + ':' + children[i].id + ':' + toolName;
	        }

        }

        if (children[i].id == 'startMarker') {
            foundStartMarker = true;
            values = "startMarker:start:start";
        }
        if (children[i].id == 'cleanup') {
            values += ",cleanup:cleanup:cleanup";
        }
        if (children[i].id == 'endMarker') {
            values += ",endMarker:end:end";
        }
    }
    orderField.value = values;
};


/**
 * destruct
 */
ListSelector.prototype.destruct = function(id) {

    var el = YAHOO.util.DDM.getElement(id);
    
    var workflow;

    if (el !== null) {
        workflow = YAHOO.util.DDM.getElement('yabi-design-dropzone');
        workflow.removeChild(el);
        
        // remove options
        this.optionsCache.deleteOption(el.id);
        
        // spit hint if no tools left
        if (workflow.childNodes.length <= 4) {
            this.spitHint();
        }
        this.update(el, false);
    }

    return false;
};


/**
 * swallowHint
 */
ListSelector.prototype.swallowHint = function() {
    hintEl = YAHOO.util.DDM.getElement('hinting');
    var dropzone;
    if (hintEl) {
        this.hintEl = hintEl.cloneNode(true);
        dropzone = YAHOO.util.DDM.getElement('yabi-design-dropzone');
        dropzone.removeChild(hintEl);
    }
};


/**
 * spitHint
 */
ListSelector.prototype.spitHint = function() {
    var dropzone, cleanup;
    if (this.hintEl) {
        dropzone = YAHOO.util.DDM.getElement('yabi-design-dropzone');
        cleanup = YAHOO.util.DDM.getElement('cleanup');
        dropzone.insertBefore(this.hintEl.cloneNode(true), cleanup);
    }
};


/**
 * setKeyValue
 */
ListSelector.prototype.setKeyValue = function(workflowUnitId, key, value) {

    var el = YAHOO.util.DDM.getElement(workflowUnitId);
    if (el !== null) {
        workflowUnit = new WorkflowUnit(el, this.optionsCache);
        workflowUnit.setBasePath(this.basePath);
        workflowUnit.setKeyValue(key,value);
        this.update(el, false);
    }
};


/**
 * removeKeyValue
 */
ListSelector.prototype.removeKeyValue = function(workflowUnitId, key, value) {

    //alert('ListSelector: removeKeyValue');
    //alert(key + '=>' + value);

    var el = YAHOO.util.DDM.getElement(workflowUnitId);
    if (el !== null) {
        workflowUnit = new WorkflowUnit(el, this.optionsCache);
        workflowUnit.setBasePath(this.basePath);
        workflowUnit.removeKeyValue(key,value);
        this.update(el, false); 
 
    }
};


/**
*
*
* Takes a filename and adds its extension to the workflow units output file types
*/
ListSelector.prototype.addOutputFiletype = function(workflowUnitId, filename) {

    var el = YAHOO.util.DDM.getElement(workflowUnitId);
    if (el !== null) {
        workflowUnit = new WorkflowUnit(el, this.optionsCache);
        workflowUnit.setBasePath(this.basePath);
        workflowUnit.addOutputFiletype(filename);
        this.update(el, false);
    }

};


/**
*
*
* Takes a filename and adds its extension to the workflow units output file types
*/
ListSelector.prototype.removeOutputFiletypes = function(workflowUnitId, filename) {

    var el = YAHOO.util.DDM.getElement(workflowUnitId);
    if (el !== null) {
        workflowUnit = new WorkflowUnit(el, this.optionsCache);
        workflowUnit.setBasePath(this.basePath);
        workflowUnit.removeOutputFiletypes();
        this.update(el, true);
    }

};



/**
 * setOptionsUrl
 *
 * Sets the url that the optionsCache object should use to fetch tool options from
 */
ListSelector.prototype.setOptionsUrl = function(url) {
    this.optionsCache.setOptionsUrl(url);
};

/**
 * setBasePath
 */
ListSelector.prototype.setBasePath = function(path) {
    this.basePath = path;
};
