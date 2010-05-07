// $Id: YabiFileSelector.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiFileSelector
 * create a new file selector object, to allow selection of files from yabi, or via upload
 */
function YabiFileSelector(param, isBrowseMode, filePath) {
    this.selectedFiles = [];
    this.pathComponents = [];
    this.browseListing = [];
    this.param = param;
    this.isBrowseMode = isBrowseMode;
    this.jsTransaction = null;
    
    this.containerEl = document.createElement("div");
    this.containerEl.className = "fileSelector";
    
    // the selected files element
    this.selectedFilesEl = document.createElement("div");
    this.selectedFilesEl.className = "validInput";
    this.containerEl.appendChild(this.selectedFilesEl);
    
    // the yabi browser
    this.browseEl = document.createElement("div");
    this.browseEl.className = "fileSelectorBrowse";
    
    //toplevel
    this.toplevelEl = document.createElement("div");
    this.toplevelEl.className = "fileSelectorBreadcrumb";
    this.browseEl.appendChild(this.toplevelEl);

    //home el
    this.homeEl = document.createElement("span");
    var homeImg = new Image();
    homeImg.alt = 'filesystem root';
    homeImg.title = homeImg.alt;
    homeImg.src = appURL + "static/images/home.png";
    this.homeEl.appendChild(homeImg);
    YAHOO.util.Event.addListener(this.homeEl, "click", this.goToRoot, this);
    this.toplevelEl.appendChild(this.homeEl);
    this.browseEl.appendChild(this.toplevelEl);

    //rootEl
    this.rootEl = document.createElement("span");
    this.toplevelEl.appendChild(this.rootEl);
    
    // the breadcrumb div
    this.breadcrumbContainerEl = document.createElement("div");
    this.breadcrumbContainerEl.className = "fileSelectorBreadcrumb";
    this.browseEl.appendChild(this.breadcrumbContainerEl);

    //the file list div
    this.fileListEl = document.createElement("div");
    this.fileListEl.className = "fileSelectorListing";
    this.browseEl.appendChild(this.fileListEl);
    
    this.loadingEl = document.createElement("div");
    this.loadingEl.className = "listingLoading";
    var loadImg = new Image();
    loadImg.src = appURL + "static/images/largeLoading.gif";
    this.loadingEl.appendChild( loadImg );

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
    this.formFileEl.setAttribute("name", "file1");
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
    
    this.ddTarget = new YAHOO.util.DDTarget(this.fileListEl, 'files', {});

    // update the browser
    if (YAHOO.lang.isUndefined(filePath) || filePath === null) {
        filePath = new YabiSimpleFileValue([], '');
    }
    this.updateBrowser(filePath);
}

/**
 * updateBrowser
 *
 * fetches updated file listing based on a new browse location
 */
YabiFileSelector.prototype.updateBrowser = function(location) {
    //console.log(location);
    this.pathComponents = location.pathComponents.slice();
    if (location.filename !== '') {
        this.pathComponents.push(location.filename);
    }
    
    //clear existing files
    while (this.fileListEl.firstChild) {
        YAHOO.util.Event.purgeElement(this.fileListEl.firstChild);
        this.fileListEl.removeChild(this.fileListEl.firstChild);
    }

    //add loading el
    this.fileListEl.appendChild(this.loadingEl);
    
    //disable drop target if location is empty (ie. the root)
    //disable uploader as well
    if (location.toString() === "") {
        this.ddTarget.lock();
        this.uploadEl.style.visibility = "hidden";
    } else {
        this.ddTarget.unlock();
        this.uploadEl.style.visibility = "visible";
    }

    this.ddTarget.invoker = {'object':new YabiSimpleFileValue(this.pathComponents, ''), 'target':this};
    this.hydrate(location.toString());
    
    this.updateBreadcrumbs();
};

/**
 * currentPath
 *
 * return current path as a YabiSimpleFileValue
 */
YabiFileSelector.prototype.currentPath = function() {
    return new YabiSimpleFileValue(this.pathComponents, '');
};

/**
 * hydrateProcess
 *
 * processes the results of a file listing json response
 */
YabiFileSelector.prototype.hydrateProcess = function(jsonObj) {
    this.browseListing = jsonObj;
    var fileEl, invoker, selectEl, downloadEl, downloadImg, sizeEl, fileSize, index;
    var handleDrop = function(srcDD, destid) {
        var target = YAHOO.util.DragDropMgr.getDDById(destid);
        var src, dest;
        src = srcDD.invoker.object;
        dest = target.invoker.object;

        srcDD.invoker.target.handleDrop(src, dest, srcDD.invoker.target, target.invoker.target);
    };
    
    //clear existing files
    while (this.fileListEl.firstChild) {
        YAHOO.util.Event.purgeElement(this.fileListEl.firstChild);
        this.fileListEl.removeChild(this.fileListEl.firstChild);
    }

    // new style 20090921 has the path as the key for the top level, then files as an array and directories as an array
    // each file and directory is an array of [fname, size in bytes, date]
    for (var toplevelindex in this.browseListing) {
        for (index in this.browseListing[toplevelindex].directories) {
            fileEl = document.createElement("div");
            fileEl.className = "dirItem";
            fileEl.appendChild(document.createTextNode(this.browseListing[toplevelindex].directories[index][0]));
            this.fileListEl.appendChild(fileEl);
            
            invoker = {"target":this, "object":new YabiSimpleFileValue(this.pathComponents, this.browseListing[toplevelindex].directories[index][0], "directory")};
            
            YAHOO.util.Event.addListener(fileEl, "click", this.expandCallback, invoker);

            if (!this.isBrowseMode && this.pathComponents.length > 0) {
                selectEl = document.createElement("a");
                selectEl.appendChild(document.createTextNode('(select)'));
                fileEl.appendChild(selectEl);
                YAHOO.util.Event.addListener(selectEl, "click", this.selectFileCallback, invoker);
            } else if (this.isBrowseMode) {
                if (this.pathComponents.length > 0) {
		    deleteEl = document.createElement("div");
		    deleteEl.className = "deleteFile";
		    deleteImg = new Image();
                    deleteImg.alt = 'delete';
                    deleteImg.title = deleteImg.alt;
		    deleteImg.src = appURL + "static/images/delete.png";
		    deleteEl.appendChild( deleteImg );
		    fileEl.appendChild( deleteEl );
		    YAHOO.util.Event.addListener(deleteEl, "click", this.deleteRemoteFileCallback, invoker);
                }
                
                tempDD = new YAHOO.util.DDProxy(fileEl, 'files', {isTarget:true});
                tempDD.overCount = 0;
                tempDD.endDrag = this.movelessDrop;
                tempDD.onDragDrop = function(e, id) { if (this.overCount === 1) { handleDrop(this, id); } this.overCount -= 1; document.getElementById(id).style.borderColor = "white"; }; //TODO make this function determine where it was dropped and issue an ajax call to move the file, then refresh the browsers that are affected
                tempDD.onDragEnter = function(e, id) { this.overCount += 1; document.getElementById(id).style.borderColor = "#3879e6"; } ;
                tempDD.onDragOut = function(e, id) { this.overCount -= 1; document.getElementById(id).style.borderColor = "white"; } ;
                tempDD.invoker = invoker;
            }
        }
        for (index in this.browseListing[toplevelindex].files) {
            fileEl = document.createElement("div");
            fileEl.className = "fileItem";
            fileEl.appendChild(document.createTextNode(this.browseListing[toplevelindex].files[index][0]));
            this.fileListEl.appendChild(fileEl);
            
            //file size
            fileSize = this.browseListing[toplevelindex].files[index][1];
            //convert from bytes to kB or MB or GB
            fileSize = this.humanReadableSizeFromBytes(fileSize);
            
            sizeEl = document.createElement("div");
            sizeEl.className = "fileSize";
            sizeEl.appendChild( document.createTextNode( fileSize ) );
            fileEl.appendChild( sizeEl );
            
            invoker = {"target":this, "object":new YabiSimpleFileValue(this.pathComponents, this.browseListing[toplevelindex].files[index][0])};
            
            if (!this.isBrowseMode) {
                YAHOO.util.Event.addListener(fileEl, "click", this.selectFileCallback, invoker);
            } else {
                deleteEl = document.createElement("div");
                deleteEl.className = "deleteFile";
                deleteImg = new Image(); 
                deleteImg.alt = 'delete';
                deleteImg.title = deleteImg.alt;
                deleteImg.src = appURL + "static/images/delete.png";
                deleteEl.appendChild( deleteImg );
                fileEl.appendChild( deleteEl );
                YAHOO.util.Event.addListener(deleteEl, "click", this.deleteRemoteFileCallback, invoker);
                
                downloadEl = document.createElement("div");
                downloadEl.className = "download";
                downloadImg = new Image();
                downloadImg.alt = 'download';
                downloadImg.title = 'download';
                downloadImg.src = appURL + "static/images/download.png";
                downloadEl.appendChild( downloadImg );
                fileEl.appendChild( downloadEl );
                YAHOO.util.Event.addListener(downloadEl, "click", this.downloadFileCallback, invoker);
                
                tempDD = new YAHOO.util.DDProxy(fileEl, 'files', {isTarget:false});
                tempDD.overCount = 0;
                tempDD.endDrag = this.movelessDrop;
                tempDD.onDragDrop = function(e, id) { try { if (this.overCount === 1) { handleDrop(this, id); } this.overCount -= 1; document.getElementById(id).style.borderColor = "white"; } catch (e) { } }; 
                tempDD.onDragEnter = function(e, id) { this.overCount += 1; document.getElementById(id).style.borderColor = "#3879e6"; } ;
                tempDD.onDragOut = function(e, id) { this.overCount -= 1; document.getElementById(id).style.borderColor = "white"; } ;
                tempDD.invoker = invoker;
            }
        }
    }

};

/**
 * handleDrop
 */
YabiFileSelector.prototype.handleDrop = function(src, dest, srcFileSelector, destFileselector) {
    //send copy command
    var baseURL = appURL + "ws/fs/copy";

    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL + "?src=" + escape(src) + "&dst=" + escape(dest);
    jsCallback = {
            success: this.copyResponse,
            failure: this.copyResponse,
            argument: [destFileselector] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);

    if (!YAHOO.lang.isUndefined(messageManager)) {
        messageManager.addMessage(jsTransaction, 'Copying '+src+' to '+dest, 'fileOperationMessage');
    }
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
    
    if (this.rootEl.firstChild) {
        YAHOO.util.Event.purgeElement(this.rootEl);
        this.rootEl.removeChild(this.rootEl.firstChild);
    }
    
    //a single space acts as a spacer node to prevent the container collapsing around the breadcrumbs
    this.breadcrumbContainerEl.appendChild(document.createTextNode(" "));
    
    var prevpath = [];
    for (var index in this.pathComponents) {
        if (prevpath.length === 0) {
            spanEl = this.rootEl;
        } else {
            spanEl = document.createElement("span");
        }

        spanEl.appendChild(document.createTextNode(this.pathComponents[index]));
        
        if (prevpath.length === 0) {
        } else {
            this.breadcrumbContainerEl.appendChild(spanEl);
        }
        
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
 * downloadFile
 *
 * download file via web service call
 */
YabiFileSelector.prototype.downloadFile = function(file) {
    window.location = appURL + "ws/fs/get?uri=" + escape(file.toString());
};

/**
 * deleteRemoteFile
 */
YabiFileSelector.prototype.deleteRemoteFile = function(file) {
    var baseURL = appURL + "ws/fs/rm";
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL + "?uri=" + escape(file.toString());
    jsCallback = {
    success: this.deleteRemoteResponse,
    failure: this.deleteRemoteResponse,
        argument: [this] };
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
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
        YAHOO.util.Event.addListener(delEl, "click", this.unselectFileCallback, invoker);
    
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
    var baseURL = appURL + "ws/fs/ls";
    
    // cancel previous transaction if it exists
    if (this.jsTransaction !== null && YAHOO.util.Connect.isCallInProgress( this.jsTransaction ) ) {
        YAHOO.util.Connect.abort( this.jsTransaction, null, false );
    }
    
    //load json
    var jsUrl, jsCallback;
    jsUrl =  baseURL + "?uri=" + escape(path);
    jsCallback = {
            success: this.hydrateResponse,
            failure: this.hydrateResponse,
            argument: [this] };
    this.jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback, null);
};

/**
 * humanReadableSizeFromBytes
 */
YabiFileSelector.prototype.humanReadableSizeFromBytes = function(bytes) {
    if (!YAHOO.lang.isNumber(bytes)) {
        return bytes;
    }
    
    var humanSize;
    
    if (bytes > (300 * 1024 * 1024)) { //GB
        humanSize = bytes / (1024 * 1024 * 1024);
        humanSize = humanSize.toFixed(2);
        humanSize += " GB";
        return humanSize;
    }
    
    if (bytes > (300 * 1024)) { //MB
        humanSize = bytes / (1024 * 1024);
        humanSize = humanSize.toFixed(2);
        humanSize += " MB";
        return humanSize;
    }
    
    //kB
    humanSize = bytes / (1024);
    humanSize = humanSize.toFixed(1);
    if (humanSize == 0.0 && bytes > 0) {
        humanSize = 0.1;
    }
    humanSize += " kB";
    return humanSize;
};

// ==== CALLBACKS ====
/**
 * goToRoot
 *
 * load the root element to get a list of fs backends
 */
YabiFileSelector.prototype.goToRoot = function(e, target) {
    target.updateBrowser(new YabiSimpleFileValue([], ""));
};

YabiFileSelector.prototype.selectFileCallback = function(e, invoker) {
    var target = invoker.target;
    target.selectFile(invoker.object);

    //prevent propagation from passing on to expand
    YAHOO.util.Event.stopEvent(e);
};

YabiFileSelector.prototype.downloadFileCallback = function(e, invoker) {
    var target = invoker.target;
    target.downloadFile(invoker.object);
    
    //prevent propagation from passing on to expand
    YAHOO.util.Event.stopEvent(e);
};

YabiFileSelector.prototype.deleteRemoteFileCallback = function(e, invoker) {
    var target = invoker.target;
    
    //file deletion
    target.deleteRemoteFile(invoker.object);

    //prevent propagation from passing on to expand
    YAHOO.util.Event.stopEvent(e);
};

YabiFileSelector.prototype.unselectFileCallback = function(e, invoker) {
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
    YAHOO.util.Event.stopEvent(e);
    
    /*var baseURL = appURL + "ws/fs/put";
    var uri = target.currentPath().toString();
    baseURL = baseURL + "?uri=" + escape(uri);
    */
    
    var baseURL = appURL + "ws/fs/getuploadurl";
    var uri = target.currentPath().toString();
    baseURL = baseURL + "?uri=" + escape(uri);
    
    //load json
    var jsUrl, jsCallback, jsTransaction;
    jsUrl =  baseURL;
    jsCallback = {
            success: target.uploadUrlResponse,
            failure: target.uploadResponse,
            argument: [target] };
//     YAHOO.util.Connect.setForm(target.uploadFormEl, true);
    jsTransaction = YAHOO.util.Connect.asyncRequest('GET', jsUrl, jsCallback);
    
    target.uploadEl.replaceChild(target.uploadMaskEl, target.uploadFormEl);
};

YabiFileSelector.prototype.uploadUrlResponse = function(o) {
    var jsUrl = YAHOO.lang.JSON.parse(o.responseText);
    
    alert("Got back: "+jsUrl);
    
    //load json
    var jsCallback, jsTransaction;
    jsCallback = {
            upload: target.uploadResponse,
            failure: target.uploadResponse,
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
    
    target.updateBrowser(new YabiSimpleFileValue(target.pathComponents, ''));
};

YabiFileSelector.prototype.deleteRemoteResponse = function(o) {
    var json = o.responseText;
    
    target = o.argument[0];

    target.updateBrowser(new YabiSimpleFileValue(target.pathComponents, ''));
};

YabiFileSelector.prototype.hydrateResponse = function(o) {
    var json = o.responseText;
   
    try {
        target = o.argument[0];
        
        target.hydrateProcess(YAHOO.lang.JSON.parse(json));
    } catch (e) {
        YAHOO.ccgyabi.YabiMessage.yabiMessageFail('Error loading file listing');
        
        target.fileListEl.removeChild( target.loadingEl );
    } finally {
        this.jsTransaction = null;
    }
};

YabiFileSelector.prototype.copyResponse = function(o) {
    var json = o.responseText;
    
    var target = o.argument[0];

    //invoke refresh on component
    target.updateBrowser(new YabiSimpleFileValue(target.pathComponents, ''));

    if (!YAHOO.lang.isUndefined(messageManager)) {
        messageManager.removeMessage(o);
    }
};

// drag n drop
YabiFileSelector.prototype.movelessDrop = function(e) {
    var DOM = YAHOO.util.Dom;
    var lel = this.getEl();
    var del = this.getDragEl();
    
    // Show the drag frame briefly so we can get its position
    // del.style.visibility = "";
    DOM.setStyle(del, "visibility", "");
    
    // Hide the linked element before the move to get around a Safari 
    // rendering bug.
    //lel.style.visibility = "hidden";
    DOM.setStyle(lel, "visibility", "hidden");
    //disable the move-to-el
    //YAHOO.util.DDM.moveToEl(lel, del);
    //del.style.visibility = "hidden";
    DOM.setStyle(del, "visibility", "hidden");
    //lel.style.visibility = "";
    DOM.setStyle(lel, "visibility", "");
};
