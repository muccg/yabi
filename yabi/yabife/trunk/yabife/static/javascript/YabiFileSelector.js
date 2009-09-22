// $Id: YabiFileSelector.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiFileSelector
 * create a new file selector object, to allow selection of files from yabi, or via upload
 */
function YabiFileSelector(param, isBrowseMode) {
    this.selectedFiles = [];
    this.pathComponents = [];
    this.browseListing = [];
    this.param = param;
    this.isBrowseMode = isBrowseMode;
    
    this.containerEl = document.createElement("div");
    this.containerEl.className = "fileSelector";
    
    // the selected files element
    this.selectedFilesEl = document.createElement("div");
    this.selectedFilesEl.className = "validInput";
    this.containerEl.appendChild(this.selectedFilesEl);
    
    // the yabi browser
    this.browseEl = document.createElement("div");
    this.browseEl.className = "fileSelectorBrowse";
    
    // the breadcrumb div
    this.breadcrumbContainerEl = document.createElement("div");
    this.breadcrumbContainerEl.className = "fileSelectorBreadcrumb";
    this.browseEl.appendChild(this.breadcrumbContainerEl);

    //the file list div
    this.fileListEl = document.createElement("div");
    this.fileListEl.className = "fileSelectorListing";
    this.browseEl.appendChild(this.fileListEl);

    this.containerEl.appendChild(this.browseEl);
    
    //file upload component
    this.uploadEl = document.createElement("div");
    this.uploadEl.className = "fileSelectorUpload";

    this.uploadFormEl = document.createElement("form");
    this.uploadFormEl.setAttribute("ENCTYPE", "multipart/form-data");
    this.uploadFormEl.setAttribute("METHOD", "POST");
    
    //this.uploadLabelEl = document.createElement("label");
//    this.uploadLabelEl.appendChild(document.createTextNode("upload a file to 'workspace': "));
//    this.uploadFormEl.appendChild(this.uploadLabelEl);
    
    var msgEl = document.createElement("input");
    msgEl.setAttribute("type", "hidden");
    msgEl.setAttribute("name", "yabiMessage");
    msgEl.value = "ajax";
    this.uploadFormEl.appendChild(msgEl);
    
    this.formFileEl = document.createElement("input");
    this.formFileEl.setAttribute("type", "file");
    this.formFileEl.setAttribute("name", "file");
    this.uploadFormEl.appendChild(this.formFileEl);

    //the uploading mask is only used to temporarily replace the uploadFormEl when submitted    
    this.uploadMaskEl = document.createElement("div");
    this.uploadMaskEl.className = "uploadingMask";
    this.uploadMaskEl.appendChild(document.createTextNode(" ... uploading ... "));
    
    this.uploadButtonEl = document.createElement("span");
    this.uploadButtonEl.className = "fakeButton fakeUploadButton";
    this.uploadButtonEl.appendChild(document.createTextNode("Upload"));
    this.uploadFormEl.appendChild(this.uploadButtonEl);
    
    YAHOO.util.Event.addListener(this.uploadButtonEl, "click", this.uploadClickCallback, this);
    YAHOO.util.Event.addListener(this.uploadFormEl, "submit", this.uploadClickCallback, this);
    
    this.uploadEl.appendChild(this.uploadFormEl);

    this.browseEl.appendChild(this.uploadEl);
    
    // update the browser
    this.updateBrowser(new YabiSimpleFileValue(['/workspace'], ''));
}

/**
 * updateBrowser
 *
 * fetches updated file listing based on a new browse location
 */
YabiFileSelector.prototype.updateBrowser = function(location) {
    //console.log(location);
    this.pathComponents = location.path.slice();
    if (location.filename !== '') {
        this.pathComponents.push(location.filename);
    }
    
    //clear existing files
    while (this.fileListEl.firstChild) {
        YAHOO.util.Event.purgeElement(this.fileListEl.firstChild);
        this.fileListEl.removeChild(this.fileListEl.firstChild);
    }

    this.hydrate(location.toString());
    
    this.updateBreadcrumbs();
};

/**
 * hydrateProcess
 *
 * processes the results of a file listing json response
 */
YabiFileSelector.prototype.hydrateProcess = function(jsonObj) {
    this.browseListing = jsonObj;
    var fileEl, invoker, expandEl, index;
    
    // new style 20090921 has the path as the key for the top level, then files as an array and directories as an array
    // each file and directory is an array of [fname, size in bytes, date]
    for (var toplevelindex in this.browseListing) {
        for (index in this.browseListing[toplevelindex].directories) {
            fileEl = document.createElement("div");
            fileEl.className = "dirItem";
            fileEl.appendChild(document.createTextNode(this.browseListing[toplevelindex].directories[index][0]));
            this.fileListEl.appendChild(fileEl);
            
            invoker = {"target":this, "object":new YabiSimpleFileValue(this.pathComponents, this.browseListing[toplevelindex].directories[index][0])};
            
            expandEl = document.createElement("a");
            expandEl.appendChild(document.createTextNode(" (browse)"));
            fileEl.appendChild(expandEl);
            YAHOO.util.Event.addListener(expandEl, "click", this.expandCallback, invoker);
            
            if (!this.isBrowseMode) {
                YAHOO.util.Event.addListener(fileEl, "click", this.selectFileCallback, invoker);
            }
        }
        for (index in this.browseListing[toplevelindex].files) {
            fileEl = document.createElement("div");
            fileEl.className = "fileItem";
            fileEl.appendChild(document.createTextNode(this.browseListing[toplevelindex].files[index][0]));
            this.fileListEl.appendChild(fileEl);
            
            invoker = {"target":this, "object":new YabiSimpleFileValue(this.pathComponents, this.browseListing[toplevelindex].files[index][0])};
            
            if (!this.isBrowseMode) {
                YAHOO.util.Event.addListener(fileEl, "click", this.selectFileCallback, invoker);
            }
            
            tempDD = new YAHOO.util.DDProxy(fileEl);
            //                tempDD.startDrag = startDragToolCallback;
            //                tempDD.endDrag = workflow.endDragJobCallback;
            //                tempDD.onDrag = workflow.onDragJobCallback;
            //                tempDD.onDragOver = workflow.onDragOverJobCallback;
            
        }
    }
    
//OLD STYLE PARSING    
//    for (var index in this.browseListing) {
//        fileEl = document.createElement("div");
//        if (this.browseListing[index].isDir && this.browseListing[index].isDir == "true") {
//            fileEl.className = "dirItem";
//        } else {
//            fileEl.className = "fileItem";
//        }
//        fileEl.appendChild(document.createTextNode(this.browseListing[index].filename));
//        this.fileListEl.appendChild(fileEl);
//
//        invoker = {"target":this, "object":new YabiSimpleFileValue(this.pathComponents, this.browseListing[index].filename)};
//        
//        if (this.browseListing[index].isDir && this.browseListing[index].isDir == "true") {
//            expandEl = document.createElement("a");
//            expandEl.appendChild(document.createTextNode(" (browse)"));
//            fileEl.appendChild(expandEl);
//            YAHOO.util.Event.addListener(expandEl, "click", this.expandCallback, invoker);
//        }
//        
//        YAHOO.util.Event.addListener(fileEl, "click", this.selectFileCallback, invoker);
//    }
};

/**
 * updateBreadcrumbs
 *
 * updates the rendered breadcrumb elements for navigating the file hierarchy
 */
YabiFileSelector.prototype.updateBreadcrumbs = function() {
    var spanEl, invoker;

    while (this.breadcrumbContainerEl.firstChild) {
        this.breadcrumbContainerEl.removeChild(this.breadcrumbContainerEl.firstChild);
    }
    
    //a single space acts as a spacer node to prevent the container collapsing around the breadcrumbs
    this.breadcrumbContainerEl.appendChild(document.createTextNode(" "));
    
    var prevpath = [];
    for (var index in this.pathComponents) {
        spanEl = document.createElement("span");
        spanEl.appendChild(document.createTextNode("> " + this.pathComponents[index]));
        this.breadcrumbContainerEl.appendChild(spanEl);
        
        invoker = {"target":this, "object":new YabiSimpleFileValue(prevpath.slice(), this.pathComponents[index])};
        
        YAHOO.util.Event.addListener(spanEl, "click", this.expandCallback, invoker);
        
        prevpath.push(this.pathComponents[index]);
    }
};

/**
 * getValues
 *
 * returns YabiJobFileValue objects, unless useInternal is true, when it returns YabiSimpleFileValue objects
 */
YabiFileSelector.prototype.getValues = function(useInternal) {
    if (useInternal === null) {
        useInternal = false;
    }
    
    var yjfv;

    if (useInternal) {
        return this.selectedFiles.slice();
    }

    var sanitizedValues = []; //this will be a new array of YabiJobFileValues
    
    for (var index in this.selectedFiles) {
        yjfv = new YabiJobFileValue(this.param.job, this.selectedFiles[index].filename);
        sanitizedValues.push(yjfv);
    }
    
    return sanitizedValues;
};

/**
 * renderInvalid
 *
 * changes the display classes to indicate invalid selection
 */
YabiFileSelector.prototype.renderInvalid = function() {
    while (this.selectedFilesEl.firstChild) {
        this.selectedFilesEl.removeChild(this.selectedFilesEl.firstChild);
    }

    this.selectedFilesEl.className = "invalidAcceptedExtensionList";
    var nofilesEl = document.createElement("span");
    nofilesEl.className = "acceptedExtension";
    
    nofilesEl.appendChild(document.createTextNode("no files selected"));
    
    this.selectedFilesEl.appendChild(nofilesEl);
};

/**
 * renderValid
 *
 * changes display classes to indicate valid selections
 */
YabiFileSelector.prototype.renderValid = function() {
    this.selectedFilesEl.className = "validInput";
};

/**
 * selectFile
 *
 * adds a file to the selectedFiles array
 */
YabiFileSelector.prototype.selectFile = function(file) {
    //duplicate detection
    for (var index in this.selectedFiles) {
        if (this.selectedFiles[index].isEqual(file)) {
            return;
        }
    }
    
    this.selectedFiles.push(file);
    
    this.renderSelectedFiles();
};

/**
 * deleteFileAtIndex
 *
 * removes file from selectedFiles array and re-renders list
 */
YabiFileSelector.prototype.deleteFileAtIndex = function(index) {
    this.selectedFiles.splice(index, 1);
    
    this.renderSelectedFiles();
};

/**
 * renderSelectedFiles
 *
 * renders the list of selected files
 */
YabiFileSelector.prototype.renderSelectedFiles = function() {
    while (this.selectedFilesEl.firstChild) {
        this.selectedFilesEl.removeChild(this.selectedFilesEl.firstChild);
    }
    
    var wrapperEl, fileEl, delEl, invoker;
    
    for (var index in this.selectedFiles) {
        wrapperEl = document.createElement("div");
        wrapperEl.className = "filePadding";
        
        fileEl = document.createElement("span");
        fileEl.className = "selectedFile";
        fileEl.appendChild(document.createTextNode(this.selectedFiles[index].filename));
        
        delEl = document.createElement("div");
        delEl.className = "destroyDiv";
        fileEl.appendChild(delEl);
        
        invoker = {"target":this, "object":index};
        YAHOO.util.Event.addListener(delEl, "click", this.deleteFileCallback, invoker);
    
        wrapperEl.appendChild(fileEl);
        
        this.selectedFilesEl.appendChild(wrapperEl);
    }
    
    //use the param callback to force the whole workflow to revalidate
    this.param.userValidate(null, this.param);
};

/**
 * hydrate
 *
 * fetches file listing from server
 */
YabiFileSelector.prototype.hydrate = function(path) {
    var baseURL = appURL + "ws/fs/list";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL + "?uri=" + escape(path);
    jsCallback = {
            success: this.hydrateResponse,
            failure: this.hydrateResponse,
            argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

// ==== CALLBACKS ====
YabiFileSelector.prototype.selectFileCallback = function(e, invoker) {
    var target = invoker.target;
    target.selectFile(invoker.object);
};

YabiFileSelector.prototype.deleteFileCallback = function(e, invoker) {
    var target = invoker.target;
    target.deleteFileAtIndex(invoker.object);
};

YabiFileSelector.prototype.expandCallback = function(e, invoker) {
    var target = invoker.target;
    target.updateBrowser(invoker.object);
    
    //prevent propagation from passing on to selectFileCallback
    YAHOO.util.Event.stopEvent(e);
};

YabiFileSelector.prototype.uploadClickCallback = function(e, target) {
    var baseURL = appURL + "ws/fs/upload";
    
    YAHOO.util.Event.stopEvent(e);
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
            upload: target.uploadResponse,
            argument: [target] };
    YAHOO.util.Connect.setForm(target.uploadFormEl, true);
    jsTransaction = YAHOO.util.Connect.asyncRequest('POST', jsUrl, jsCallback);
    
    target.uploadEl.replaceChild(target.uploadMaskEl, target.uploadFormEl);
};

YabiFileSelector.prototype.uploadResponse = function(o) {
    var json = o.responseText;
    
    target = o.argument[0];
    target.uploadFormEl.reset();
    
    target.uploadEl.replaceChild(target.uploadFormEl, target.uploadMaskEl);
    
    target.updateBrowser(new YabiSimpleFileValue([], 'workspace'));
};

YabiFileSelector.prototype.hydrateResponse = function(o) {
    var json = o.responseText;
   
    try {
        target = o.argument[0];
        
        target.hydrateProcess(YAHOO.lang.JSON.parse(json));
    } catch (e) {
        YAHOO.ccgyabi.YabiMessage.yabiMessageFail('Error loading file listing');
    }
};
