// $Id: optionsCache.js 3994 2008-12-11 07:27:23Z ntakayama $

/**
 * OptionsCache
 */
function OptionsCache(id) {
    this.options = [];
    this.optionsElId = id; //a handle on the div to populate with our options
    this.optionsEl = null;
    this.optionsUrl = null;
    this.toolsJson = []; //array to hold all the json data for each tool
}


/**
 * fetchOptionsForIdAndName
 */
OptionsCache.prototype.fetchOptionsForIdAndName = function(el) {

    var sUrl, callback, transaction, id, name;

    id = el.id;
    name = el.name;
    path = el.path;

    //search cache
    if (this.options[id] !== undefined) {
        this.populateOptions(this.options[id]);
    } else {    // else fetch from server
        //ajax request the Options section of the page
        sUrl = this.optionsUrl + "?item="+name+"&id="+id+"&path="+path;
        callback = {
            success: listSelector.optionsCache.stubResponse,
            failure: listSelector.optionsCache.stubResponse,
            argument: [id, name, path] };
        transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, callback, null);

    }
};


/**
 * populateOptions
 */
OptionsCache.prototype.populateOptions = function(id) {

    var child;

    if (this.optionsEl === null ) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }

    //display
    for (var i=0; i<this.optionsEl.childNodes.length; i++) {
        child = null;
        child = this.optionsEl.childNodes[i];
        if (child.id == id) {
            child.style.display = 'block';
        } else {
            if (child.style) {
                child.style.display = 'none';
            }
        }
    }
};


/**
 * stubResponse
 *
 * JS calls to specific method, not object on callbacks. To avoid having anonymous
 * method within ajax call we use this method
 */
OptionsCache.prototype.stubResponse = function(o) {
    if (o.argument[0] == 'js') {
        listSelector.optionsCache.handleJsServerResponse(o);
    } else {
        listSelector.optionsCache.handleServerResponse(o);
    }
};


/**
 * handleServerResponse
 */  
OptionsCache.prototype.handleServerResponse = function(o) {

    //intercept and avoid duplication of tool options (which happens sometimes due to lags in ajax)
    if (this.options[o.argument[0]] !== undefined) {
        return;
    }

    //cache
    var el = document.createElement('div');
    el.innerHTML = o.responseText;
    el.id = o.argument[0] + '_optionsDiv';
    this.options[o.argument[0]] = el.id;
    if (this.optionsEl === null) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }
    el.style.display = "none";
    this.optionsEl.appendChild(el);

    //loadjs
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  this.optionsUrl + "?item="+o.argument[1]+"&id="+o.argument[0]+"&path="+o.argument[2]+"&format=js";
    jsCallback = {
            success: listSelector.optionsCache.stubResponse,
            failure: listSelector.optionsCache.stubResponse,
            argument: ['js', o.argument[0]] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);

};

/**
 * handleServerResponse
 */
OptionsCache.prototype.handleJsServerResponse = function(o) {
    if (o.status == 200) {
        eval(o.responseText); // is this evil eval needed for safari?
    }

    // call update passing the work flow unit that these options are for
    listSelector.update(document.getElementById(o.argument[1]), false);

};


/**
 * createOption
 */
OptionsCache.prototype.createOption = function(id) {

    var el;

    if (this.optionsEl === null ) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }

    if (this.options[id] !== null) {
        el = document.createElement('div');
        el.id = id + '_optionsDiv';
        this.options[id] = el.id;
    }
};


/**
 * deleteOption
 */
OptionsCache.prototype.deleteOption = function(id) {
    if (this.optionsEl === null ) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }
    //locate and destroy optionDiv
    var optionDiv = document.getElementById(id+"_optionsDiv");
    if (optionDiv) {
        this.optionsEl.removeChild(optionDiv);
    }
    //purge from array
    this.options[id] = null;
};


/**
 * setKeyValue
 */
OptionsCache.prototype.setKeyValue = function(id, key, value) {

    // get the main options div
    if (this.optionsEl === null ) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }

    // create option div if not present
    if (this.options[id] === null) {
        this.createOption(id);
    }

    // get the right div
    var optionDiv = document.getElementById(id+"_optionsDiv");


    // work out if the item is there already
    var results = [];
    var children, i;
    var alreadySet = false;
    var el;

    if(optionDiv) {
        children = optionDiv.childNodes;
        for (i=0; i < children.length; i++) {
            if(children[i].type === 'hidden' && children[i].name === key && children[i].value === value) {
                alreadySet = true;
            }
        }
    }

    if(!alreadySet) {

        // add the hidden input node to div
        el = document.createElement('input');
        el.type = 'hidden';
        el.name = key;
        el.value = value;
        optionDiv.appendChild(el);
    }
};


/**
 * removeKeyValue
 */
OptionsCache.prototype.removeKeyValue = function(id, key, value) {

    // get the main options div
    if (this.optionsEl === null ) {
        this.optionsEl = document.getElementById(this.optionsElId);
    }

    // create option div if not present
    if (this.options[id] === null) {
        this.createOption(id);
    }

    // get the right div
    var optionDiv = document.getElementById(id+"_optionsDiv");
    
	//find the right element and remove it
    var results = [];
    var children, i;

    if(optionDiv) {
        children = optionDiv.childNodes;
        for (i=0; i < children.length; i++) {
            if(children[i].type === 'hidden' && children[i].name === key && children[i].value === value) {
                optionDiv.removeChild(children[i]);
            }
        }
    }
};


/**
 * getFiles
 */
OptionsCache.prototype.getFiles = function(id) {

    var optionsDiv = document.getElementById(id+"_optionsDiv");
    var results = [];
    var children, i;

    if(optionsDiv) {
        children = optionsDiv.childNodes;
        for (i=0; i < children.length; i++) {

            if(children[i].type == 'hidden') {

                if(children[i].name == 'file') {
                   	results.push(children[i].value);
                }
            }
        }
    }

    return results;
};


/**
 * setOptionsUrl
 */
OptionsCache.prototype.setOptionsUrl = function(url) {
    this.optionsUrl = url;
};


/**
 * getToolInfo
 *
 * returns the tool info as loaded from the jsonified baat file
 */
OptionsCache.prototype.getToolInfo = function(id) {
    return this.toolsJson[id];

};

OptionsCache.prototype.setToolInfo = function(id, info) {
    this.toolsJson[id] = info;
};


/**
 * getInputFiletypes
 *
 * Finds the appropriate element, gets string contents and splits on ','
 * converts array to object and returns
 */
OptionsCache.prototype.getInputFiletypes = function(id) {

    var elemId = id + ':input:inputFiletypes';
    var inputFiletypes = document.getElementById(elemId);
    var i, inputFiletypesArray;
    var retObj = {};

    if(inputFiletypes) {

        // convert array to object as we can better search the object for presence of key        
        inputFiletypesArray = inputFiletypes.value.split(',');
        for(i=0;i<inputFiletypesArray.length;i++) {
            retObj[inputFiletypesArray[i]] = inputFiletypesArray[i];
        }
    }
    return retObj;
};


/**
 * getOutputFiletypes
 *
 * Finds the appropriate element, gets string contents and splits on ',' to return array
 */
OptionsCache.prototype.getOutputFiletypes = function(id) {
    var elemId = id + ':input:outputFiletypes';
    var outputFiletypes = document.getElementById(elemId);
    var i, outputFiletypesArray;
    var retObj = {};

    if(outputFiletypes) {

        // convert array to object as we can better search the object for presence of key        
        outputFiletypesArray = outputFiletypes.value.split(',');
        for(i=0;i<outputFiletypesArray.length;i++) {
            retObj[outputFiletypesArray[i]] = outputFiletypesArray[i];
        }
    }
    return retObj;
};


/**
 * getFilePassThru
 *
 * Finds appropriate element on id and returns boolean
 */
OptionsCache.prototype.getFilePassThru = function(id) {

    var filePassThru = false;
    var elemId = id + ':input:filePassThru';
    var elem = document.getElementById(elemId);

    if(elem) {
        filePassThru = elem.value === 'true' ? true : false;
    }
    return filePassThru;
};


/**
 * getRequiresInput
 *
 * Finds appropriate element on id and returns boolean
 */
OptionsCache.prototype.getRequiresInput = function(id) {

    var requiresInput = false;
    var elemId = id + ':input:requiresInput';
    var elem = document.getElementById(elemId);

    if(elem) {
        requiresInput = elem.value === 'true' ? true : false;
    }
    return requiresInput;
};


/**
 * getAcceptsInput
 *
 * Finds appropriate element on id and returns boolean
 */
OptionsCache.prototype.getAcceptsInput = function(id) {

    var acceptsInput = false;
    var elemId = id + ':input:acceptsInput';
    var elem = document.getElementById(elemId);

    if(elem) {
        acceptsInput = elem.value === 'true' ? true : false;
    }
    return acceptsInput;
};


/**
 * addOutputFiletype
 *
 * Adds the extension of filename to the appropriate hidden field in optionsdiv
 */
OptionsCache.prototype.addOutputFiletype = function(id, filename) {

    // get the extension and strip off the dot
    var dotIndex = filename.lastIndexOf('.');
    var extensionWithDot = filename.substr(dotIndex);
    var extension = extensionWithDot.replace('.','');

    //an evil assumption, to be sure. files without extensions are not always directories. and directories can have extensions!
    if (dotIndex === -1) {
        extension = 'directory';
	}

    var elemId = id + ':input:outputFiletypes';
    var elem = document.getElementById(elemId);
    var filetypes = [];

    // get the string, turn into array, add the new extension,
    // turn back into string and add back to elem
    if(elem) {

        // if value is * then just replace it, otherwise add to it
        if(elem.value === '*' || elem.value === null || elem.value === "") {
            filetypes = [];
        } else {
            filetypes = elem.value.split(',');
        }

        filetypes.push(extension);
        elem.value = filetypes.join(',');
    }

};


/**
 * removeOutputFiletypes
 *
 * Adds the extension of filename to the appropriate hidden field in optionsdiv
 */
OptionsCache.prototype.removeOutputFiletypes = function(id) {
    var elemId = id + ':input:outputFiletypes';
    var elem = document.getElementById(elemId);
    elem.value = null;
};


