/*
 * Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
 * Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
 *  
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the 
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  */

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
 * @param {String} uri The uri of the directory we will upload to.
 */
YAHOO.ccgyabi.widget.Upload = function(container, uri) {
  this.container = container;
  this.uri = uri;

  this.createElements();

  this.selectedFiles = [];

  this.addEventListeners();
  EventEmitter.call(this);
};


var upload = YAHOO.ccgyabi.widget.Upload;


upload.prototype = new EventEmitter();


/**
 * Attaches the event listeners for the elements created by the
 * {@link #createElements} method.
 */
upload.prototype.addEventListeners = function() {
  var self = this;

  // Start the upload process when the Upload button is clicked.
  Y.use('*', function(Y) {
    if (self.uploadButton) {
        Y.one(self.uploadButton).on('click', function(e) {
          e.halt(true);
          Yabi.util.setCSRFHeader(Y.io);
          self.upload();
        });
    }
  });

};


/**
 * Creates the base elements required for the upload widget.
 */
upload.prototype.createElements = function() {
  var self = this;
  this.element = document.createElement('div');
  this.element.className = 'fileSelectorUpload';

  if (Y.Uploader.TYPE == "none" || Y.UA.ios) {
      this.element.textContent = "Sorry, but your browser doesn't support uploading files.";
      this.container.appendChild(this.element);
      return;
  }

  // TODO clean up, move stuff to CSS, use YUI DOM API?

  var uploadButtonContainer = document.createElement('span');
  uploadButtonContainer.className = 'uploadButtonContainer';
  uploadButtonContainer.className = 'uploadButtonContainer';

  this.uploadButton = document.createElement('button');
  this.uploadButton.className = 'yui3-button fakeButton fakeUploadButton';
  this.uploadButton.style.width = '90px';
  this.uploadButton.style.height = '23px';
  this.uploadButton.setAttribute('aria-label', 'Upload');
  this.uploadButton.setAttribute('role', 'button');
  this.uploadButton.setAttribute('type', 'button');
  this.uploadButton.textContent = 'Upload';

  uploadButtonContainer.appendChild(this.uploadButton);

  this.selectContainer = document.createElement('span');
  this.selectContainer.className = 'selectButtonContainer';
  this.selectContainer.style.display = 'inline-block';

  this.infoBar = document.createElement('span');
  this.infoBar.textContent = 'No files selected.';
  this.infoBar.style.marginLeft = '10px';

  this.element.appendChild(this.selectContainer);
  this.element.appendChild(this.infoBar);
  this.element.appendChild(uploadButtonContainer);
  this.container.appendChild(this.element);

  this.uploader = new Y.Uploader({
     width: '90px',
     height: '23px',
     multipleFiles: true,
     swfURL: appURL + 'static/flashuploader.swf?t=' + Math.random(),
     uploadURL: appURL + 'ws/fs/put?uri=' + escape(this.uri),
     simLimit: 2,
     withCredentials: false
  });
  this.uploader.render(this.selectContainer);

  this.uploader.after("fileselect", function (event) {
    function ensureFileListIsUnique() {
      var fileList = self.uploader.get('fileList');
      var newFileNames = _.map(event.fileList, function(f) { return f.get('name'); });
      fileList = _.reject(fileList, function(file) { 
        return _.contains(newFileNames, file.get('name'));
      });
      self.uploader.set('fileList', fileList);
    };

    Y.use('*', function(Y) {
      ensureFileListIsUnique();

      var fileList = self.uploader.get('fileList');

      var allFiles = fileList.concat(event.fileList);
      var size = _.reduce(allFiles, function(sum, f2) {
        return sum + f2.get('size');
      }, 0);

      var infoMsg = allFiles.length + ' files (' +
                    Yabi.util.humaniseBytes(size) +
                    ') selected.';
      self.setInfoBarMsg(infoMsg);
    });

  });

  this.uploader.on("uploaderror", function (event) {
    self.sendEvent('fail', 'Error uploading file');
  });

  this.uploader.on("alluploadscomplete", function (event) {
    self.sendEvent('upload');
    // self.uploader.set("enabled", true);
  });

  this.uploader.on("uploadstart", function (event) {
    // self.uploader.set("enabled", false);
    self.setInfoBarMsg('Starting upload...');
  });

  this.uploader.on("totaluploadprogress", function (event) {
    var h = Yabi.util.humaniseBytes;
    var infoMsg = Math.floor(event.percentLoaded) + "% uploaded";
    var remaining = event.bytesTotal - event.bytesLoaded;
    // library bug? It ends up loading more than the total each time.
    if (remaining < 0) {
      remaining = 'a few bytes';
      infoMsg = '99% uploaded';
    } else {
      remaining = h(remaining);
    }
    infoMsg += ' (' + remaining + ' of ' + h(event.bytesTotal) + ' remaining).';

    self.setInfoBarMsg(infoMsg);
  });
 
};

upload.prototype.setInfoBarMsg = function(msg) {
  var infoBar = Y.one(this.infoBar);
  infoBar.setHTML(msg);
}

/**
 * Destroys the upload widget and removes its HTML elements from the DOM.
 */
upload.prototype.destroy = function() {
  this.container.removeChild(this.element);
  this.element = null;
};


/**
 * Initiates the upload process. If the URI hasn't been set by a call to the
 * {@link #setURI} method, then this will do nothing, silently. Otherwise, this
 * should result in an "upload" or "fail" event being emitted by the upload
 * widget at some point.
 */
upload.prototype.upload = function() {
  if (this.uri && this.uploader.get("fileList").length > 0) {
    this.uploader.uploadAll();
  }
};


YUI().use("uploader", function(Y) {
   if (Y.Uploader.TYPE != "none" && !Y.UA.ios) {
       upload.uploader = new Y.Uploader;
   }
});
