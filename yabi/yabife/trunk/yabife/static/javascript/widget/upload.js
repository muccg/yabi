YAHOO.namespace("ccgyabi.widget");


/**
 * An upload widget designed for use with YabiFileSelector objects.
 *
 * This widget implements the {@link EventEmitter} interface, and emits two
 * events: "fail", which will include a human-readable message to be displayed
 * to the user when an upload fails, and "upload", which is emitted when an
 * upload succeeds and includes no arguments.
 *
 * @constructor
 * @param {HTMLElement} container A container to render the widget into.
 */
YAHOO.ccgyabi.widget.Upload = function (container) {
    /* Requiring the container at construct-time isn't ideal, from a coupling
     * point of view, but the Flash implementation needs to be able to add
     * elements to the DOM and have them rendered so it can size the Flash
     * object accordingly. */
    this.container = container;
    this.uri = null;

    this.createElements();

    /* Most of the magic of the widget is actually handled within an object
     * contained within the widget; the two options at the time of writing at
     * Flash and HTML uploaders, but there's no technical reason more options
     * couldn't be added later, so long as they implement the same interface.
     * One obvious candidate is XMLHttpRequest 2 and the File API, which
     * Firefox 4 and recent Chrome versions support.
     *
     * Note that implementations do not take a reference to the upload widget,
     * but instead signal back via events. These include the "fail" and
     * "upload" events documented in the object docblock above, which simply
     * get passed onto this object's listener(s), and also an "uploadRequested"
     * event which will cause the upload process to begin.
     *
     * We use Mark Pilgrim's Flash Blocker Detector to detect whether Flash is
     * actually usable. If the user has a Flash blocker installed but disables
     * it for YABI, then they get the Flash uploader, just as a user with Flash
     * and no blocker would. Users with a Flash blocker enabled get the HTML
     * uploader at present.
     */
    this.impl = new YAHOO.ccgyabi.widget.Upload.supportedImplementation(this.element);

    this.addEventListeners();
    EventEmitter.call(this);
};

YAHOO.ccgyabi.widget.Upload.prototype = new EventEmitter();

/**
 * Attaches the event listeners for the elements created by the
 * {@link #createElements} method.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.prototype.addEventListeners = function () {
    var self = this;

    // Start the upload process when the Upload button is clicked.
    YAHOO.util.Event.addListener(this.uploadButton, "click", function (e) {
        YAHOO.util.Event.stopEvent(e);
        self.upload();
    });

    // Handle events emitted from the specific implementation.
    this.impl.addEventListener("fail", function (e, message) {
        self.sendEvent("fail", message);
    });

    this.impl.addEventListener("remove", function (e, file) {
        self.remove(file);
    });

    this.impl.addEventListener("upload", function (e) {
        self.sendEvent("upload");
    });

    this.impl.addEventListener("uploadRequested", function (e) {
        self.upload();
    });
};

/**
 * Creates the base elements required for the upload widget.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.prototype.createElements = function () {
    /* Everything bar the containing div and Upload button are left for the
     * implementation to construct. */
    this.element = document.createElement("div");
    this.element.className = "fileSelectorUpload";

    this.uploadButton = document.createElement("span");
    this.uploadButton.className = "fakeButton fakeUploadButton";
    this.uploadButton.appendChild(document.createTextNode("Upload"));

    this.element.appendChild(this.uploadButton);

    this.container.appendChild(this.element);
};

/**
 * Destroys the upload widget and removes its HTML elements from the DOM.
 */
YAHOO.ccgyabi.widget.Upload.prototype.destroy = function () {
    this.impl.destroy();

    this.container.removeChild(this.element);
    this.element = null;
};

/**
 * Removes the given file from the current destination directory.
 *
 * @param {String} file The name of the file to delete.
 */
YAHOO.ccgyabi.widget.Upload.prototype.remove = function (file) {
    var self = this;

    if (this.uri) {
        var callbacks = {
            success: function (o) {
                self.sendEvent("remove", file);
            },
            failure: function (o) {
                self.sendEvent("removeFail", file);
            }
        };

        var uri = appURL + "ws/fs/rm?uri=" + escape(this.uri + "/" + file);
        YAHOO.util.Connect.asyncRequest("GET", uri, callbacks);
    }
};

/**
 * Sets the URI parameter to add as the destination when uploading.
 *
 * @param {String} uri The new URI.
 */
YAHOO.ccgyabi.widget.Upload.prototype.setURI = function (uri) {
    this.uri = uri;
};

/**
 * Initiates the upload process. If the URI hasn't been set by a call to the
 * {@link #setURI} method, then this will do nothing, silently. Otherwise, this
 * should result in an "upload" or "fail" event being emitted by the upload
 * widget at some point.
 */
YAHOO.ccgyabi.widget.Upload.prototype.upload = function () {
    if (this.uri) {
        this.impl.upload(this.uri);
    }
};


/**
 * An implementation object for the upload widget that provides a Flash
 * uploader using the SWFUpload library. This object shouldn't be instantiated
 * directly from outside {@link YAHOO.ccgyabi.widget.Upload} objects.
 *
 * @constructor
 * @param {HTMLElement} container The containing element.
 */
YAHOO.ccgyabi.widget.Upload.Flash = function (container) {
    // Contains the file ID as returned from the Flash object.
    this.selectedFile = null;

    /* Because the Flash object can't access the cookies set within the
     * browser, we have to extract the Django session ID so it can be sent as
     * part of the upload URL. */
    this.session = /sessionid=([0-9a-f]{32})/.exec(document.cookie)[1];

    this.createElements(container);
    this.addEventListeners();

    EventEmitter.call(this);
};

YAHOO.ccgyabi.widget.Upload.Flash.prototype = new EventEmitter();

/**
 * Attaches the event listeners for the elements created by the
 * {@link #createElements} method.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.addEventListeners = function () {
    var self = this;

    /* Event listeners for the SWFUpload object are attached in
     * createElements(), since they can only be attached when the object is
     * constructed. */

    YAHOO.util.Event.addListener(this.cancel, "click", function (e) {
        self.uploader.cancelUpload(self.selectedFile.id, true);
        self.sendEvent("remove", self.selectedFile.name);
    });
};

/**
 * Creates the elements required for the Flash uploader.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.createElements = function (container) {
    var self = this;
    var swfUploadBase = appURL + "static/javascript/swfupload-2.5.0b3/";

    this.container = document.createElement("div");

    this.select = document.createElement("div");
    this.select.className = "fakeButton selectButton";
    this.select.appendChild(document.createTextNode("Select File"));

    this.placeholder = document.createElement("div");
    this.placeholder.className = "placeholder";

    this.progress = document.createElement("div");
    this.progress.className = "uploadProgress";
    this.progress.style.display = "none";

    this.cancel = document.createElement("div");
    this.cancel.className = "fakeButton fakeUploadButton";
    this.cancel.appendChild(document.createTextNode("Cancel"));

    this.progressText = document.createElement("span");

    container.appendChild(this.container);

    this.container.appendChild(this.select);
    this.container.appendChild(this.placeholder);
    this.container.appendChild(this.progress);

    this.progress.appendChild(this.cancel);
    this.progress.appendChild(this.progressText);

    /* This has to be constructed after the elements have been appended, since
     * it depends on the select button's dimensions. */
    this.file = document.createElement("div");
    this.file.style.position = "absolute";
    this.file.style.left = new Number(this.select.scrollWidth + 8).toString() + "px";
    this.file.style.top = "0.3em";

    this.container.appendChild(this.file);

    /* Construct the actual SWFUpload object and attach the event handlers we
     * need to give feedback to the user and send the appropriate events. */
    this.uploader = new SWFUpload({
        button_placeholder: this.placeholder,
        flash_url: swfUploadBase + "swfupload.swf",
        flash9_url: swfUploadBase + "swfupload_fp9.swf",
        file_post_name: "file1",
        button_action: SWFUpload.BUTTON_ACTION.SELECT_FILES,
        button_window_mode: SWFUpload.WINDOW_MODE.TRANSPARENT,
        button_width: this.select.scrollWidth,
        button_height: this.select.scrollHeight,
        file_queued_handler: function (file) {
            self.setFileName(file.name);
            self.selectedFile = file;
        },
        upload_start_handler: function (file) {
            self.showProgress(file.name, 0);
        },
        upload_progress_handler: function (file, bytes, total) {
            self.showProgress(file.name, bytes / total);
        },
        upload_error_handler: function (file, code, message) {
            self.hideProgress();
            self.reset();
            self.sendEvent("fail", message);
        },
        upload_success_handler: function (file, data, response) {
            self.hideProgress();
            self.reset();
            self.sendEvent("upload");
        }
    });
};

/**
 * Destroys the Flash uploader. This doesn't do anything in particular,
 * although we could abort an in progress upload, I guess.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.destroy = function () {};

/**
 * Hides the upload progress overlay.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.hideProgress = function () {
    this.progress.style.display = "none";
};

/**
 * Resets the upload control by removing any currently selected file.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.reset = function () {
    this.selectedFile = null;
    this.setFileName("");
};

/**
 * Sets the file name displayed in the upload label.
 *
 * @private
 * @param {String} name The name to set.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.setFileName = function (name) {
    while (this.file.childNodes.length) {
        this.file.removeChild(this.file.firstChild);
    }

    this.file.appendChild(document.createTextNode(name));
};

/**
 * Shows the upload progress overlay.
 *
 * @param {String} name The name of the file being uploaded.
 * @param {Number} progress The current progress of the upload, from 0.0 to
 *                          1.0.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.showProgress = function (name, progress) {
    while (this.progressText.childNodes.length) {
        this.progressText.removeChild(this.progressText.firstChild);
    }

    var text = "Uploading " + name + ": " +
               (100 * progress).toFixed().toString() + "%";

    this.progressText.appendChild(document.createTextNode(text));
    this.progress.style.display = "block";
};

/**
 * Starts the upload process. Emits a "fail" event if no file is selected.
 *
 * @param {String} uri The destination URI.
 */
YAHOO.ccgyabi.widget.Upload.Flash.prototype.upload = function (uri) {
    if (this.selectedFile) {
        var target = appURL + "ws/fs/put/" + this.session + "?uri=" + 
                     encodeURIComponent(uri).replace(/%20/g, "+");

        this.uploader.setUploadURL(target);
        this.uploader.startUpload(this.selectedFile.id);
    }
    else {
        this.sendEvent("fail", "No file has been selected to upload");
    }
};


/**
 * An implementation object for a traditional HTML uploader.
 *
 * @constructor
 * @param {HTMLElement} container The containing element.
 */
YAHOO.ccgyabi.widget.Upload.HTML = function (container) {
    this.createElements(container);
    this.addEventListeners();

    EventEmitter.call(this);
};

YAHOO.ccgyabi.widget.Upload.HTML.prototype = new EventEmitter();

/**
 * Attaches the event listeners for the elements created by the
 * {@link #createElements} method.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.HTML.prototype.addEventListeners = function () {
    var self = this;

    /* Some browsers can emit a form submit event by hitting ENTER while the
     * file selector is highlighted (since they use a text box and button to
     * represent the control), so we need to capture it and dispatch the
     * appropriate event to avoid the form submission working in the normal
     * way. */
    YAHOO.util.Event.addListener(this.form, "submit", function (e) {
        YAHOO.util.Event.stopEvent(e);
        self.sendEvent("uploadRequested");
    });
};

/**
 * Creates the elements required for the HTML uploader.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.HTML.prototype.createElements = function (container) {
    this.form = document.createElement("form");
    this.form.setAttribute("enctype", "multipart/form-data");
    this.form.setAttribute("method", "POST");

    this.file = document.createElement("input");
    this.file.setAttribute("type", "file");
    this.file.setAttribute("name", "file1");

    this.progress = document.createElement("span");

    container.appendChild(this.form);
    this.form.appendChild(this.file);
    this.form.appendChild(this.progress);
};

/**
 * Destroys the HTML uploader. This doesn't do anything.
 */
YAHOO.ccgyabi.widget.Upload.HTML.prototype.destroy = function () {};

/**
 * Starts the upload process.
 *
 * @param {String} uri The destination URI.
 */
YAHOO.ccgyabi.widget.Upload.HTML.prototype.upload = function (uri) {
    var self = this;
    var target = appURL + "ws/fs/put?uri=" + escape(uri);

    var callbacks = {
        upload: function (o) {
            self.uploadResponse(o);
        }
    };

    this.file.style.display = "none";
    this.progress.appendChild(document.createTextNode("Uploading file..."));

    YAHOO.util.Connect.setForm(this.form, true);
    YAHOO.util.Connect.asyncRequest("POST", target, callbacks);
};

/**
 * Response handler for the YAHOO.util.Connect upload implementation.
 *
 * @private
 * @param {Object} o The event object.
 */
YAHOO.ccgyabi.widget.Upload.HTML.prototype.uploadResponse = function (o) {
    this.form.reset();

    while (this.progress.childNodes.length) {
        this.progress.removeChild(this.progress.firstChild);
    }
    this.file.style.display = "inline";

    /* YUI will call this callback even when the upload has failed (lovely
     * piece of design, that). Since we don't have the status code (or any
     * other headers) available, we'll have to try to decode the JSON that was
     * (hopefully) received and go from there. */
    try {
        var json = YAHOO.lang.JSON.parse(o.responseText)

        if (json.level != "success") {
            /* It's not a real response object, it's simply something
             * masquerading as such. As a result, we'll just call the error
             * display function directly. */
            this.sendEvent("fail", json.message);
            return;
        }
    }
    catch (e) {
        // Bad JSON. Firstly, we'll check for a 413 from nginx.
        try {
            var titles = o.responseXML.getElementsByTagName("title");

            if (titles.length) {
                var title = titles[0].innerText || titles[0].textContent;
                if (title.indexOf("413 ") != -1) {
                    this.sendEvent("fail", "File too large to be uploaded");
                    return;
                }
            }
        }
        catch (e) {}

        this.sendEvent("fail", "Error uploading file");
        return;
    }

    this.sendEvent("upload");
};


/**
 * An implementation object for a XMLHttpRequest 2 and File API based uploader.
 * (The HTML5 bit in the name is technically a misnomer, but it's snappier than
 * something based on the aforementioned standards.)
 *
 * @constructor
 * @param {HTMLElement} container The containing element.
 */
YAHOO.ccgyabi.widget.Upload.HTML5 = function (container) {
    this.file = null;

    this.createElements(container);
    this.addEventListeners();

    EventEmitter.call(this);
};

YAHOO.ccgyabi.widget.Upload.HTML5.prototype = new EventEmitter();

/**
 * Attaches the event listeners for the elements created by the
 * {@link #createElements} method.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.addEventListeners = function () {
    var self = this;

    YAHOO.util.Event.addListener(this.cancel, "click", function (e) {
        YAHOO.util.Event.stopEvent(e);
        if (self.xhr) {
            self.xhr.abort();
        }
    });

    YAHOO.util.Event.addListener(this.select, "click", function (e) {
        YAHOO.util.Event.stopEvent(e);
        self.input.click();
    });

    YAHOO.util.Event.addListener(this.input, "change", function (e) {
        self.setFile(this.files[0]);
    });

    YAHOO.util.Event.addListener(this.form, "submit", function (e) {
        YAHOO.util.Event.stopEvent(e);
        self.sendEvent("uploadRequested");
    });
};

/**
 * Creates the elements required for the HTML uploader.
 *
 * @private
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.createElements = function (container) {
    this.form = document.createElement("form");
    this.form.setAttribute("enctype", "multipart/form-data");
    this.form.setAttribute("method", "POST");

    this.input = document.createElement("input");
    this.input.setAttribute("type", "file");
    this.input.setAttribute("name", "file1");

    /* The input has to be visible for Chrome to allow the click() method to be
     * called, but we really, really want to hide it. Width: 0 and inline-block
     * does that in Chrome, but Firefox on some platforms also needs opacity:
     * 0 to hide it. */
    this.input.style.display = "inline-block";
    this.input.style.opacity = 0;
    this.input.style.overflow = "hidden";
    this.input.style.width = "0";

    this.select = document.createElement("span");
    this.select.className = "fakeButton selectButton";
    this.select.style.position = "static";
    this.select.appendChild(document.createTextNode("Select File"));

    this.name = document.createElement("span");

    this.progress = document.createElement("div");
    this.progress.className = "uploadProgress";
    this.progress.style.display = "none";

    this.cancel = document.createElement("div");
    this.cancel.className = "fakeButton fakeUploadButton";
    this.cancel.appendChild(document.createTextNode("Cancel"));

    this.progressText = document.createElement("span");

    container.appendChild(this.form);
    this.form.appendChild(this.input);
    this.form.appendChild(this.select);
    this.form.appendChild(this.name);
    this.form.appendChild(this.progress);

    this.progress.appendChild(this.cancel);
    this.progress.appendChild(this.progressText);
};

/**
 * Destroys the HTML5 uploader. This doesn't do anything.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.destroy = function () {};

/**
 * Hides the upload progress overlay.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.hideProgress = function () {
    this.progress.style.display = "none";
};

/**
 * Sets the currently selected file.
 *
 * @param {File} file The File object (from the File API) to select.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.setFile = function (file) {
    this.file = file;

    while (this.name.childNodes.length) {
        this.name.removeChild(this.name.firstChild);
    }

    if (file) {
        this.name.appendChild(document.createTextNode(file.name));
    }
};

/**
 * Shows the upload progress overlay.
 *
 * @param {String} name The name of the file being uploaded.
 * @param {Number} progress The current progress of the upload, from 0.0 to
 *                          1.0.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.showProgress = function (name, progress) {
    while (this.progressText.childNodes.length) {
        this.progressText.removeChild(this.progressText.firstChild);
    }

    var text = "Uploading " + name;
    
    if (typeof progress == "number") {
        text += ": " + (100 * progress).toFixed().toString() + "%";
    }
    else if (typeof progress == "string") {
        text += ": " + progress;
    }
    else {
        text += "...";
    }

    this.progressText.appendChild(document.createTextNode(text));
    this.progress.style.display = "block";
};

/**
 * Starts the upload process.
 *
 * @param {String} uri The destination URI.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.upload = function (uri) {
    var self = this;

    if (!this.file) {
        return;
    }

    this.xhr = new XMLHttpRequest();

    /* We need to send the file as a normal form to avoid needing to change the
     * way the put views and upload streaming work, so we'll use FormData to
     * fake it. */
    var formData = new FormData();
    formData.append("file1", this.file);

    var target = appURL + "ws/fs/put?uri=" + escape(uri);
    this.xhr.open("POST", target, true);

    /* Set up the event handlers for the request object. We need to attach the
     * events to the XHR object and not the upload object for anything other
     * than "progress", because the terminating events (most notably "load")
     * are fired on the upload object _after_ the XHR object is GCed in WebKit,
     * which isn't very helpful. */

    this.xhr.addEventListener("abort", function (e) {
        // User aborts don't need to output a message.
        self.sendEvent("remove", self.file.name);
        self.hideProgress();
        self.form.reset();
        self.setFile(null);
        self.xhr = null;
    }, false);

    this.xhr.addEventListener("error", function (e) {
        self.uploadResponse(e);
    }, false);

    this.xhr.addEventListener("load", function (e) {
        self.uploadResponse(e);
    }, false);

    this.xhr.addEventListener("loadstart", function (e) {
        self.uploadProgress(e);
    }, false);

    this.xhr.upload.addEventListener("progress", function (e) {
        self.uploadProgress(e);
    }, false);

    this.xhr.send(formData);
};

/**
 * Progress event handler.
 *
 * @private
 * @param {ProgressEvent} e The progress event.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.uploadProgress = function (e) {
    if (e.lengthComputable) {
        this.showProgress(this.file.name, e.loaded / e.total);
    }
    else {
        this.showProgress(this.file.name);
    }
};

/**
 * Response handler once the upload is complete.
 *
 * @private
 * @param {ProgressEvent} e The progress event.
 */
YAHOO.ccgyabi.widget.Upload.HTML5.prototype.uploadResponse = function (e) {
    this.hideProgress();
    this.form.reset();
    this.setFile(null);

    if ((this.xhr.status >= 200 && this.xhr.status <= 299) || this.xhr.status == 1223) {
        this.sendEvent("upload");
    }
    else if (this.xhr.status == 413) {
        this.sendEvent("fail", "File too large to be uploaded");
    }
    else {
        try {
            var json = YAHOO.lang.JSON.parse(o.responseText)
            this.sendEvent("fail", json.message);
        }
        catch (e) {
            this.sendEvent("fail", "Error uploading file");
        }
    }

    this.xhr = null;
};


/* Detect what we can use in terms of uploading technology. The preference list
 * goes HTML5 > Flash > traditional HTML. */
YAHOO.util.Event.onDOMReady(function () {
    if (("upload" in new XMLHttpRequest) &&
        !!window.FormData &&
        (typeof FileReader != "undefined")) {
        YAHOO.ccgyabi.widget.Upload.supportedImplementation = YAHOO.ccgyabi.widget.Upload.HTML5;
        return;
    }

    var useFlash = false;

    if(!useFlash) {
        YAHOO.ccgyabi.widget.Upload.supportedImplementation = YAHOO.ccgyabi.widget.Upload.HTML;
    } else {

    var testFlash = function () {
        YAHOO.ccgyabi.widget.Upload.supportedImplementation = YAHOO.ccgyabi.widget.Upload.Flash;

        FBD.initialize(function (blocked) {
            if (blocked) {
                YAHOO.ccgyabi.widget.Upload.supportedImplementation = YAHOO.ccgyabi.widget.Upload.HTML;
            }
        });
    };

    YAHOO.ccgyabi.widget.Upload.supportedImplementation = YAHOO.ccgyabi.widget.Upload.HTML;

    if (navigator.plugins && navigator.plugins["Shockwave Flash"]) {
        testFlash();
    }
    else if (navigator.mimeTypes && navigator.mimeTypes["application/x-shockwave-flash"]) {
        var flash = navigator.mimeTypes["application/x-shockwave-flash"];
        if (flash && flash.enabledPlugin) {
            testFlash();
        }
    }
    else {
        // IE. We'll only look for Flash 9 or later.
        try {
            console.log("IE test");
            new ActiveXObject("ShockwaveFlash.ShockwaveFlash.9");
            testFlash();
        }
        catch (e) {}
    }
    }
});
