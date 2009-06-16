// $Id: workflowUnit.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * WorkflowUnit
 */
function WorkflowUnit(el, optionsCache) {
    // el - div that this workflow corresponds to
    this.el = el;
    this.optionsCache = optionsCache;
    this.filetypesValid = false;
    this.prevUnit = null;
    this.nextUnit = null;
    this.validated = true;
}


/**
 * setPrevUnit
 *
 * Allows you to pass in another workunit that comes before this one in the list
 */
WorkflowUnit.prototype.setPrevUnit = function(prevUnit) {
    this.prevUnit = prevUnit;
};


/**
 * setNextUnit
 *
 * Allows you to pass in another workunit that comes after this one in the list
 */
WorkflowUnit.prototype.setNextUnit = function(nextUnit) {
    this.nextUnit = nextUnit;
};


/**
 * getId
 */
WorkflowUnit.prototype.getId = function() {
    return this.el.id;
};


/**
 * update
 *
 * Called by listSelector.update which should be called whenever the drag and drop list changes
 * selectedEl is the id of the workunit being dragged or selected
 * delayOptions is true when dragging from tools, false otherwise
 */
WorkflowUnit.prototype.update = function(selectedEl, delayOptions) {

    var toolinfo;
    var paramArray;
    var param;
    var i;
    var elem;

    this.validated = true;

    // set selected
    if(this.el.id == selectedEl) {
        this.setSelected(true);
    } else {
        this.setSelected(false);
    }


    // set display of unit options
    // this fetches the options if they are not there
    if(delayOptions === false) {
        if(this.el.id == selectedEl) {
            this.setDisplay(true);
        } else {
            this.setDisplay(false);
        }
    }


    // check input/output filetypes
    this.filetypesValid = this.checkFiletypes();
    if (this.filetypesValid === false) {
        this.validated = false;
    }


    // check whether unit accepts input
    this.checkAcceptsInput();


    // set this units available files, ie the files it has received from above it on the workflow
    if(delayOptions === false) {
        this.setAvailableFiles();

        // assess validity of data based on tool info
        toolinfo = this.optionsCache.getToolInfo(this.el.id);

        if (toolinfo !== null && toolinfo !== undefined) {
            paramArray = toolinfo.baat.job.parameterList.parameter;
            //in case of single params, the xml to json converter erroneously produces it as an object instead of an array
            //we must repackage it to allow validation on single param nodes
            if (paramArray['inputFile'] !== null && paramArray['inputFile'] !== undefined) {
                param = paramArray;
                paramArray = new Array();
                paramArray.push(param);
            }
            for (i=0;i < paramArray.length;i++) {
                param = paramArray[i];

                if (param.mandatory === "yes") {

                    elem = document.getElementById(this.el.id + ":input:" + param["switch"]);
                    if (elem && elem.value === "") {
                        elem.style.backgroundColor = "#f00000";
                        elem.style.color = "white";

                        this.validated = false;
                    } else if (elem) {
                        elem.style.backgroundColor = "white";
                        elem.style.color = "black";
                    }

                }
            }
        }

        //render borders to show validation errors
        this.renderBorders();

    }

};


/**
 * setKeyValue
 */
WorkflowUnit.prototype.setKeyValue = function(key, value) {

    //alert('WorkflowUnit: setKeyValue');
    //alert('this.el.id: ' +this.el.id + ' : ' + key + '=>' + value);

    this.optionsCache.setKeyValue(this.el.id, key, value);
};

/**
 * removeKeyValue
 */
WorkflowUnit.prototype.removeKeyValue = function(key, value) {

    //alert('ListSelector: removeKeyValue');
    //alert(key + '=>' + value);
    
    this.optionsCache.removeKeyValue(this.el.id, key, value);
};


/**
 * setSelected
 */
WorkflowUnit.prototype.setSelected = function(selected) {

    var flowtriangle;

    if(selected === true) {
        flowtriangle = YAHOO.util.DDM.getElement(this.el.id + 'flow');
        if (flowtriangle) {
            flowtriangle.style.backgroundImage = 'url(../images/yabi-flow-triangle-selected.gif)';
        }
        this.el.style.background = 'url(../images/node-selected-gradient.png)';
    } else {
        flowtriangle = YAHOO.util.DDM.getElement(this.el.id + 'flow');
        if (flowtriangle) {
            flowtriangle.style.backgroundImage = 'url(../images/yabi-flow-triangle.gif)';
        } 

        if (this.el.style !== undefined) {
            this.el.style.background = 'none';
            this.el.style.backgroundColor = "#ffffff";
        }
    }
};


/**
 * setDisplay
 */
WorkflowUnit.prototype.setDisplay = function(display) {

    var optionsDiv = document.getElementById(this.el.id+"_optionsDiv");

    if(optionsDiv) {

        if (display === true) {

            optionsDiv.style.display = 'block';
        } else {
            if (optionsDiv.style) {
                optionsDiv.style.display = 'none';
            }
        }
    } else {
        // need to check there is an id, this is for startmarker etc, should set these up to have an id?
        if(this.el.id && this.el.name) {

            this.optionsCache.fetchOptionsForIdAndName(this.el);
        }
    }
};


/**
 * getFiles
 *
 * Returns an array of key/value pairs, each record being a file path
 */
WorkflowUnit.prototype.getFiles = function() {
    return this.optionsCache.getFiles(this.el.id);

};


/**
 * setAvailableFiles
 *
 * Selects any fields of class fileSelector and replaces value with comma-separated
 * list of files. The idea here is to build the dropdowns on the fly based on what files
 * are available in previous tools. In addition the code takes into account options sent
 * from the template. This is to allow default options of no file when there is an optional
 * element such as a vector file
 */
WorkflowUnit.prototype.setAvailableFiles = function() {

    var files = [];

    if(this.prevUnit !== null && this.filetypesValid === true) {
        files = this.prevUnit.getOutputfiles();
    }        

    var fileListArray = [];
    var i;
    for (i=0;i< files.length;i++) {
        fileListArray.push(files[i]);
    }

    //fileListArray.unshift("Select input...");

    var fileList = fileListArray.join(',');

	//this sets the hidden input field to contain the files (what the mw sees).
    // fileSelector
    var fields = YAHOO.util.Dom.getElementsByClassName('fileSelector', '', this.el.id + '_optionsDiv');
    if(fields.length !== 0) {
        for (i=0;i< fields.length;i++) {
            fields[i].value = fileList;
        }
    }


    // check to see if there are any fileSelectDropdown elements and add each file as an option
    // to them if they are found
    var dropdowns = YAHOO.util.Dom.getElementsByClassName('fileSelectDropdown', '', this.el.id + '_optionsDiv');
    var selectedValue = "";
    var selectIndex = -1;
    var additionalItemCount = 0;
    var filename;

    var toolDisplayNameLI;
    var toolDisplayNameEl;
    var toolDisplayName;
    var additionalOptions = {}; // object, so we can use it like a hash
    var tempFileList = [];

    if(dropdowns.length !== 0) {

        // for each fileSelectDropdown field
        for (i=0;i< dropdowns.length;i++) {

            // make a copy of the file list for this dropdown and use the additionalOptions object
            // to add any additionalOptions <option> tags sent from the php template
            tempFileList = fileListArray.slice();
            additionalOptions = {};

            // get the select elem
            selectElem = dropdowns[i];

			// remember the selection so that we can restore it after re-creation
            if (selectElem.selectedIndex >= 0) {
			    selectedValue = dropdowns[i].options[selectElem.selectedIndex].value;
            }

            additionalItemCount = 0;

            // remove all old items, but take any sent from php template and add them to
            // the additionalOptions object - test for 0 value to find php template items
            for(j = selectElem.options.length-1; j >= 0; j--) {
                if(selectElem.options[j].value === "0" || selectElem.options[j].value === "") {
                    additionalOptions[selectElem.options[j].value] = selectElem.options[j].text;
                    additionalItemCount++;
                }
                selectElem.options[j] = null;
            }

            // now add each of the additional option tags send from php template onto
            // the list of files we want to see in this drop down; using concat as apparently
            // unshift is not consistent in IE
            // if the user has selected one of added options then set the selectIndex to 0
            // this means we can only add one additional option at the moment which is fine
            // as we are using it to allow non-selection for optional elements
            for (var option in additionalOptions) {
				dropdowns[i].options.add(new Option(additionalOptions[option], option, false, false));
                if(selectedValue == "") {
                    selectIndex = 0;
                }
            }

            // now add each file in the tempFileList to our dropdown
	        for (k=0; k<tempFileList.length;k++) {
	        	// create an option for the file, with the name being either the proper filename or the tool display name
	        	filename = tempFileList[k];
            	if (filename.indexOf('clone_') != -1) {
            		filename = filename.slice(0, -1); // get rid of the trailing slash (/)
                	// the name of the file in this case is the toolDisplayName
                	toolDisplayNameLI = document.getElementById(filename);
                	toolDisplayNameEl = YAHOO.util.Dom.getElementsByClassName('toolDisplayName', null, toolDisplayNameLI)[0];
                	toolDisplayName   = toolDisplayNameEl.innerHTML;
                	filename = toolDisplayName;
                }
				dropdowns[i].options.add(new Option(filename, tempFileList[k], false, false));

                if (tempFileList[k] == selectedValue || tempFileList[k] == selectedValue.slice(0, -1)) {
                    selectIndex = k + additionalItemCount;
                }
            }

            // this is what allows dropdowns to preselect the previous tool by default
            if (selectIndex < 0) {
                selectIndex = tempFileList.length - 1 + additionalItemCount;
            }
	
            // restore the previous selection
            dropdowns[i].selectedIndex = selectIndex;
        }
    }


    //this sets what the user sees in the options. - may not be used now - abm
    var fileDisplay = YAHOO.util.Dom.getElementsByClassName('selectedFileDisplay', '', this.el.id + '_optionsDiv');
    if(fileDisplay.length !== 0) {
        for (i=0;i< fileDisplay.length;i++) {
            if (fileListArray.length !== 0 ){
                fileDisplay[i].innerHTML = fileListArray.join('<br/>');
            }
        }
    }    
};


/**
 * checkFiletypes
 */
WorkflowUnit.prototype.checkFiletypes = function() {

    var inputFiletypes = {};
    var outputFiletypes = {};
    var filetypesValid = true;
    var requiresInput = this.getRequiresInput();
    var temp;

    // get input/output types
    if(this.prevUnit !== null) {
        outputFiletypes = this.prevUnit.getOutputFiletypes();
    }
    inputFiletypes = this.getInputFiletypes();


    // check if input is required but there is no previous unit
    if(requiresInput === true && this.prevUnit === null) {
        filetypesValid = false;
    }


    // check matching output/input by iterating over the output types of prevUnit
    // and ensuring at least one is present in the input types of this unit
    if(requiresInput === true && this.prevUnit !== null) {
        filetypesValid = false;

        // if this unit accepts anything then filetypesValid is true
        if(inputFiletypes['*'] !== undefined) {
            filetypesValid = true;
        } else {
            for(temp in outputFiletypes) {
                if(inputFiletypes[temp] !== undefined || temp == 'zip') {
                    filetypesValid = true;
                }
            }
        }
    }

    return filetypesValid;
};


/**
 * renderBorders
 */
WorkflowUnit.prototype.renderBorders = function() {
    // get all the necessary dom elements
    var prevUnitEl, thisUnitEl;
    if(this.prevUnit !== null) {
        prevUnitEl = YAHOO.util.DDM.getElement(this.prevUnit.getId());
    }
    thisUnitEl = YAHOO.util.DDM.getElement(this.getId());

    // change unit borders as neccessary
    if(this.validated === false) {

        //change the bottom border of the previous element only if there is a filetypes validity issue
        if (prevUnitEl && this.filetypesValid === false) {
            prevUnitEl.style.borderBottom = '4px solid #F00000';
        }

        //for all validation we highlight the top border of the node in question
        if (thisUnitEl) {
            thisUnitEl.style.borderTop = '4px solid #F00000';
        }

    } else {

        if (prevUnitEl) {
            prevUnitEl.style.borderBottom = '2px solid #ff6600';
        }

        if (thisUnitEl) {
            thisUnitEl.style.borderTop = '2px solid #ff6600';
            thisUnitEl.style.borderBottom = '2px solid #ff6600';
        }
    }
};


/**
 * checkAcceptsInput
 */
WorkflowUnit.prototype.checkAcceptsInput = function() {

    var acceptsInput = this.getRequiresInput();

    // get all the necessary dom elements
    var prevUnitEl, thisUnitEl;
    if(this.prevUnit !== null) {
        prevUnitEl = YAHOO.util.DDM.getElement(this.prevUnit.getId());
    } else {
        //if this is the first work unit, don't pad the space above
        acceptsInput = true;
    }
    thisUnitEl = YAHOO.util.DDM.getElement(this.getId());

    // change unit borders as neccessary
    if(acceptsInput === false) {

        if (thisUnitEl) {
            thisUnitEl.style.marginTop = '20px';
        }

    } else {

        if (thisUnitEl) {
            thisUnitEl.style.marginTop = '0px';
        }
    }

    return acceptsInput;
};


/**
 * getInputFiletypes
 *
 * Queries options cache and returns an array of file extensions
 * that this unit can accept
 */
WorkflowUnit.prototype.getInputFiletypes = function() {

    var optionsDiv = document.getElementById(this.el.id+"_optionsDiv");
    var inputFiletypes = {};

    // check there is already an optionsDiv (optionsCache might still be retrieving it)
    // then get filetypes
    if(optionsDiv) {
        inputFiletypes = this.optionsCache.getInputFiletypes(this.el.id);
    }
    return inputFiletypes;
};


/**
 * getOutputFiletypes
 *
 * Queries options cache and returns an array of file extensions
 * that this unit outputs
 */
WorkflowUnit.prototype.getOutputFiletypes = function() {

    var optionsDiv = document.getElementById(this.el.id+"_optionsDiv");
    var outputFiletypes = {};

    // check there is already an optionsDiv (optionsCache might still be retrieving it)
    // then get filetypes
    if(optionsDiv) {
        outputFiletypes = this.optionsCache.getOutputFiletypes(this.el.id);
    }
    return outputFiletypes;
};


/**
 * getOutputfiles
 *
 * Queries options cache and returns an array of file paths
 * that this unit has or will output
 */
WorkflowUnit.prototype.getOutputfiles = function () {

    var prevUnitFiles = [];
    var thisUnitFiles = [];
    var allFiles = [];

    if(this.prevUnit !== null) {// && this.filetypesValid === true && this.prevUnit.getFilePassThru() === true) {

        //if prevunit not null then get files from that too
            prevUnitFiles = this.prevUnit.getOutputfiles();
    }

    // get this unit's files
    thisUnitFiles = this.optionsCache.getFiles(this.el.id);


    // combine the two if this unit passes thru files otherwise return this unit's files only
    if(this.getFilePassThru() === true) {
        allFiles = prevUnitFiles.concat(thisUnitFiles);
    } else {
        allFiles = thisUnitFiles;
    }

    return allFiles;
};


/**
 * getFilePassThru
 *
 * Queries optionscache to determine whether this unit should include
 * any input files among its output files
 */
WorkflowUnit.prototype.getFilePassThru = function () {
    return this.optionsCache.getFilePassThru(this.el.id);
};


/**
 * getRequiresInput
 *
 * Queries optionscache to determine whether this unit requires an input file
 */
WorkflowUnit.prototype.getRequiresInput = function () {
    return this.optionsCache.getRequiresInput(this.el.id);
};


/**
 * getAcceptsInput
 *
 * Queries optionscache to determine whether this unit will accept an input file
 */
WorkflowUnit.prototype.getAcceptsInput = function () {
    return this.optionsCache.getAcceptsInput(this.el.id);
};


/**
 * addOutputFiletype
 */
WorkflowUnit.prototype.addOutputFiletype = function(filename) {
    this.optionsCache.addOutputFiletype(this.el.id, filename);
};


/**
 * removeOutputFiletypes
 */
WorkflowUnit.prototype.removeOutputFiletypes = function() {
    this.optionsCache.removeOutputFiletypes(this.el.id);
};


/**
 * setBasePath
 */
WorkflowUnit.prototype.setBasePath = function(path) {
    this.basePath = path;
};
