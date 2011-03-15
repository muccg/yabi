// $Id: YabiFileSelector.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiFileSelector
 * create a new file selector object, to allow selection of files from yabi, or via upload
 */
function YabiFileSelector(param, isBrowseMode, filePath, readOnly) {
    this.selectedFiles = [];
    this.pathComponents = [];
    this.browseListing = [];
    this.param = param;
    this.isBrowseMode = isBrowseMode;
    this.jsTransaction = null;
    this.readOnly = !!readOnly;
    
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
    this.toplevelEl.className = "fileSelectorBreadcrumb fileSelectorRoot";
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
    this.breadcrumbContainerEl.className = "fileSelectorBreadcrumb fileSelectorPath";
    this.browseEl.appendChild(this.breadcrumbContainerEl);

    //the file list div
    this.fileListEl = document.createElement("div");
    this.fileListEl.className = "fileSelectorListing";
    this.browseEl.appendChild(this.fileListEl);
    
    this.containerEl.appendChild(this.browseEl);

    this.upload = null;
    
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
    this.loading = new YAHOO.ccgyabi.widget.Loading(this.fileListEl);
    this.loading.show();
    this.fileListEl.scrollTop = 0;
    
    //disable drop target if location is empty (ie. the root)
    //disable uploader as well
    if (location.toString() === "") {
        this.ddTarget.lock();
        this.disableUpload();
    } else {
        this.ddTarget.unlock();
        this.enableUpload();
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
 * disableUpload
 *
 * Disables the upload form.
 */
YabiFileSelector.prototype.disableUpload = function() {
    if (this.upload) {
        this.upload.destroy();
        this.upload = null;
    }
};

/**
 * enableUpload
 *
 * Disables the upload form.
 */
YabiFileSelector.prototype.enableUpload = function() {
    var self = this;

    this.disableUpload();

    if (this.readOnly) {
        // No need for uploads in browse mode.
        return;
    }

    this.upload = new YAHOO.ccgyabi.widget.Upload(this.browseEl);
    this.upload.setURI(this.currentPath());

    this.upload.addEventListener("fail", function(e, message) {
        YAHOO.ccgyabi.widget.YabiMessage.fail(message);
    });

    this.upload.addEventListener("remove", function(e, file) {
        self.updateBrowser(self.currentPath());
    });

    this.upload.addEventListener("upload", function(e) {
        YAHOO.ccgyabi.widget.YabiMessage.success("File uploaded successfully");
        self.updateBrowser(self.currentPath());
    });
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
            if (this.browseListing[toplevelindex].directories[index][3]) {
                fileEl.className += " dirLink"                                      // this is a symlink, so change the icon image
            }
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
            fileEl = document.createElement("a");
            fileEl.className = "fileItem";
            if (this.browseListing[toplevelindex].files[index][3]) {
                fileEl.className += " fileLink"                                      // this is a symlink, so change the icon image
            }
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

            invoker = {
                target: this,
                object: new YabiSimpleFileValue(this.pathComponents, this.browseListing[toplevelindex].files[index][0]),
                topLevelIndex: toplevelindex
            };
            
            fileEl.href = appURL + "preview?uri=" + escape(invoker.object.toString());

            /* Both browse and non-browse mode use the preview button, but they
             * need to add them at different points in the tree, so we'll build
             * them here but not append them to the document or hook up the
             * event handler. */
            previewEl = document.createElement("div");
            previewEl.className = "preview";
            previewImg = new Image();
            previewImg.alt = 'preview';
            previewImg.title = 'preview';
            previewImg.src = appURL + "static/images/preview.png";
            previewEl.appendChild( previewImg );
            
            if (!this.isBrowseMode) {
                YAHOO.util.Event.addListener(fileEl, "click", this.selectFileCallback, invoker);

                fileEl.appendChild( previewEl );
                YAHOO.util.Event.addListener(previewEl, "click", this.previewFileCallback, invoker);
            } else {
                YAHOO.util.Event.addListener(fileEl, "click", this.previewFileCallback, invoker);

                deleteEl = document.createElement("div");
                deleteEl.className = "deleteFile";
                deleteImg = new Image(); 
                deleteImg.alt = 'delete';
                deleteImg.title = deleteImg.alt;
                deleteImg.src = appURL + "static/images/delete.png";
                deleteEl.appendChild( deleteImg );
                fileEl.appendChild( deleteEl );
                YAHOO.util.Event.addListener(deleteEl, "click", this.deleteRemoteFileCallback, invoker);
                
                fileEl.appendChild( previewEl );
                YAHOO.util.Event.addListener(previewEl, "click", this.previewFileCallback, invoker);
                
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
                tempDD.clickValidator = function (e) { return true; };
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
            failure: function (o) {
                YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);

                if (!YAHOO.lang.isUndefined(messageManager)) {
                    messageManager.removeMessage(o);
                }
            },
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
 * getFileIndex
 *
 * Returns the index of the given file in the files array. If it doesn't exist,
 * returns null.
 */
YabiFileSelector.prototype.getFileIndex = function(filename, topLevelIndex) {
    var files = this.browseListing[topLevelIndex].files;
    var index = null;

    for (var i in files) {
        if (files.hasOwnProperty(i) && files[i][0] == filename) {
            index = i;
            break;
        }
    }

    return index;
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
 * purgePreviewElements
 *
 * Removes all preview elements from the selector.
 */
YabiFileSelector.prototype.purgePreviewElements = function() {
    var previews = this.browseEl.querySelectorAll(".fileSelectorPreview");
    for (var i = 0; i < previews.length; i++) {
        var previewParent = previews[i].parentNode;
        previewParent.removeChild(previews[i]);
    }
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
    failure: YAHOO.ccgyabi.widget.YabiMessage.handleResponse,
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
 * previewFile
 *
 * Previews the selected file, if possible.
 */
YabiFileSelector.prototype.previewFile = function(file, topLevelIndex) {
    this.preview = new YabiFileSelectorPreview(this, file, topLevelIndex);
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
        fileEl.title = this.selectedFiles[index].filename;
        
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
            failure: function (o) {
                YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
                o.argument[0].loading.hide();
            },
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

YabiFileSelector.prototype.previewFileCallback = function(e, invoker) {
    var target = invoker.target;
    target.previewFile(invoker.object, invoker.topLevelIndex);

    YAHOO.util.Event.stopEvent(e);
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
        YAHOO.ccgyabi.widget.YabiMessage.fail('Error loading file listing');
        
        target.loading.hide();
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


/**
 * YabiFileSelectorPreview
 *
 * An object that provides an overlay over a given YabiFileSelector that
 * securely previews the given file.
 */
var YabiFileSelectorPreview = function (fs, file, topLevelIndex) {
    this.fs = fs;
    this.file = file;
    this.loadCallbackFired = false;
    this.topLevelIndex = topLevelIndex;
    this.uri = appURL + "preview?uri=" + escape(file.toString());

    this.previous = this.getPrevious();
    this.next = this.getNext();

    // THERE CAN BE ONLY ONE.
    this.fs.purgePreviewElements();

    this.previewEl = document.createElement("div");
    this.previewEl.className = "fileSelectorPreview";

    this.createControls();
    this.createIFrame();

    this.fs.browseEl.appendChild(this.previewEl);
};

/**
 * createControlButton
 *
 * Internal method to create a fake button in the preview control bar.
 */
YabiFileSelectorPreview.prototype.createControlButton = function (className, onClick, title) {
    var button = document.createElement("div");
    button.className = "controlButton " + className;

    if (onClick) {
        button.className += " enabled";
        
        YAHOO.util.Event.addListener(button, "click", onClick);
    }
    else {
        button.className += " disabled";
    }

    if (title) {
        button.title = title;
    }

    return button;
};

/**
 * createControls
 *
 * Internal method to create the various controls we want for the file.
 */
YabiFileSelectorPreview.prototype.createControls = function () {
    var self = this;

    var controls = document.createElement("div");
    controls.className = "fileSelectorPreviewControls";

    this.title = document.createElement("h3");
    this.title.className = "fileSelectorPreviewTitle";
    this.title.appendChild(document.createTextNode(this.file.filename));

    controls.appendChild(this.title);

    // Add buttons.
    controls.appendChild(this.createControlButton("fileSelectorPreviewClose", function (e) {
        self.closeCallback();
    }, "close preview"));

    controls.appendChild(this.createControlButton("fileSelectorPreviewDownload", function (e) {
        self.fs.downloadFile(self.file);
    }, "download file"));

    var previousCallback = null;
    var title = null;
    if (this.previous) {
        previousCallback = function (e) {
            self.fs.previewFile(self.previous, self.topLevelIndex);
        };

        title = this.previous.filename;
    }
    controls.appendChild(this.createControlButton("fileSelectorPreviewPrevious", previousCallback, title));

    var nextCallback = null;
    title = null;
    if (this.next) {
        nextCallback = function (e) {
            self.fs.previewFile(self.next, self.topLevelIndex);
        };

        title = this.next.filename;
    }
    controls.appendChild(this.createControlButton("fileSelectorPreviewNext", nextCallback, title));

    this.previewEl.appendChild(controls);
};

/**
 * createIFrame
 *
 * Internal method to create the iframe for the previewed file.
 */
YabiFileSelectorPreview.prototype.createIFrame = function () {
    var self = this;

    var container = document.createElement("div");
    container.className = "fileSelectorPreviewFrameContainer";

    this.iframeEl = document.createElement("iframe");
    this.iframeEl.className = "loading";
    this.iframeEl.frameBorder = 0;
    this.iframeEl.src = this.uri;

    YAHOO.util.Event.addListener(this.iframeEl, "load", function (e) {
        self.loadCallback();
    });

    container.appendChild(this.iframeEl);
    this.previewEl.appendChild(container);
};

/**
 * closeCallback
 *
 * Handler for clicks on the close button.
 */
YabiFileSelectorPreview.prototype.closeCallback = function () {
    this.fs.purgePreviewElements();
};


/**
 * loadCallback
 *
 * Handler called when the iframe has loaded.
 */
YabiFileSelectorPreview.prototype.loadCallback = function () {
    var self = this;

    if (this.loadCallbackFired) {
        return;
    }
    this.loadCallbackFired = true;

    this.iframeEl.className = "";

    var callbacks = {
        success: function (o) {
            self.metadataCallback(o);
        },
        failure: YAHOO.ccgyabi.widget.YabiMessage.handleResponse
    };

    var url = appURL + "preview/metadata?uri=" + escape(this.file.toString());
    YAHOO.util.Connect.asyncRequest("GET", url, callbacks);
};

/**
 * metadataCallback
 *
 * Handler called when preview metadata is available.
 */
YabiFileSelectorPreview.prototype.metadataCallback = function (o) {
    var metadata = YAHOO.lang.JSON.parse(o.responseText);

    var span = document.createElement("span");
    span.className = "fileSelectorPreviewMetadata";

    var size = document.createElement("span");
    size.className = "fileSelectorPreviewSize";
    size.appendChild(document.createTextNode(this.fs.humanReadableSizeFromBytes(metadata.size)));
    span.appendChild(size);

    if (metadata.truncated) {
        var truncatedLength = this.fs.humanReadableSizeFromBytes(metadata.truncated);

        // Oh, English.
        var verb = "are";
        if (truncatedLength.slice(0, 4) == "1.00") {
            verb = "is";
        }

        var truncated = document.createElement("span");
        truncated.className = "fileSelectorPreviewTruncated";
        truncated.title = "This file is too long to be previewed in full. " +
                          "The first " + truncatedLength + " " + verb + " shown below. " +
                          "To view the complete file, please download it.";
        truncated.appendChild(document.createTextNode("truncated"));

        /* This would be better done in CSS with a generated content block, but
         * the border style can't be overridden in a :before style, which is
         * ugly. */
        span.appendChild(document.createTextNode("; "));

        span.appendChild(truncated);
    }

    this.title.appendChild(span);
};


/**
 * getPrevious
 *
 * Returns the previous file in the file selector's file array or null if the
 * file is the first one.
 */
YabiFileSelectorPreview.prototype.getPrevious = function () {
    var files = this.fs.browseListing[this.topLevelIndex].files;
    var index = this.fs.getFileIndex(this.file.filename, this.topLevelIndex);

    if (index !== null && index > 0) {
        if (--index in files) {
            return new YabiSimpleFileValue(this.fs.pathComponents, files[index][0]);
        }
    }

    return null;
};

/**
 * getNext
 *
 * Returns the next file in the file selector's file array or null if the file
 * is the last one.
 */
YabiFileSelectorPreview.prototype.getNext = function () {
    var files = this.fs.browseListing[this.topLevelIndex].files;
    var index = this.fs.getFileIndex(this.file.filename, this.topLevelIndex);

    if (index !== null) {
        if (++index in files) {
            return new YabiSimpleFileValue(this.fs.pathComponents, files[index][0]);
        }
    }

    return null;
};
