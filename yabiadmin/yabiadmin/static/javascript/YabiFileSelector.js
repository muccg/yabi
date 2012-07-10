YUI().use('dd-constrain', 'dd-proxy', 'dd-drop', 'io', 'json-parse',
    function(Y) {

      /**
       * YabiFileSelector
       * create a new file selector object, to allow selection of files
       * from yabi, or via upload
       */
      YabiFileSelector = function(param, isBrowseMode, filePath, readOnly) {
        var self = this;
        this.selectedFiles = [];
        this.pathComponents = [];
        this.browseListing = [];
        this.param = param;
        this.isBrowseMode = isBrowseMode;
        this.jsTransaction = null;
        this.readOnly = !!readOnly;

        this.containerEl = document.createElement('div');
        this.containerEl.className = 'fileSelector';

        // the selected files element
        this.selectedFilesEl = document.createElement('div');
        this.selectedFilesEl.className = 'validInput';
        this.containerEl.appendChild(this.selectedFilesEl);

        // the yabi browser
        this.browseEl = document.createElement('div');
        this.browseEl.className = 'fileSelectorBrowse';

        //toplevel
        this.toplevelEl = document.createElement('div');
        this.toplevelEl.className = 'fileSelectorBreadcrumb fileSelectorRoot';
        this.browseEl.appendChild(this.toplevelEl);

        //home el
        this.homeEl = document.createElement('span');
        var homeImg = new Image();
        homeImg.alt = 'filesystem root';
        homeImg.title = homeImg.alt;
        homeImg.src = appURL + 'static/images/home.png';
        this.homeEl.appendChild(homeImg);
        Y.one(self.homeEl).on('click', self.goToRoot, null, self);
        this.toplevelEl.appendChild(this.homeEl);
        this.browseEl.appendChild(this.toplevelEl);

        //rootEl
        this.rootEl = document.createElement('span');
        this.toplevelEl.appendChild(this.rootEl);

        // the breadcrumb div
        this.breadcrumbContainerEl = document.createElement('div');
        this.breadcrumbContainerEl.className =
            'fileSelectorBreadcrumb fileSelectorPath';
        this.browseEl.appendChild(this.breadcrumbContainerEl);

        //the file list div
        this.fileListEl = document.createElement('div');
        this.fileListEl.className = 'fileSelectorListing';
        this.browseEl.appendChild(this.fileListEl);

        this.containerEl.appendChild(this.browseEl);

        this.upload = null;

        this.ddTarget = new Y.DD.Drop({
          node: this.fileListEl
        });

        this.setUpDragAndDrop();

        // update the browser
        if (Y.Lang.isUndefined(filePath) || filePath === null) {
          filePath = new YabiSimpleFileValue([], '');
        }
        this.updateBrowser(filePath);
      }


      /**
       * updateBrowser
       *
       * fetches updated file listing based on a new browse
       * location
       */
      YabiFileSelector.prototype.updateBrowser = function(loc) {
        //console.log(location);
        this.pathComponents = loc.pathComponents.slice();
        if (loc.filename !== '') {
          this.pathComponents.push(loc.filename);
        }

        //clear existing files
        while (this.fileListEl.firstChild) {
          Y.one(this.fileListEl.firstChild).detachAll();
          this.fileListEl.removeChild(this.fileListEl.firstChild);
        }

        //add loading el
        this.loading = new YAHOO.ccgyabi.widget.Loading(this.fileListEl);
        this.loading.show();
        this.fileListEl.scrollTop = 0;

        this.ddTarget.invoker = {
          'object': new YabiSimpleFileValue(this.pathComponents, ''),
          'target': this
        };

        //disable drop target if location is empty (ie. the root)
        //disable uploader as well
        if (loc.toString() === '') {
          this.ddTarget.lock = true;
          this.disableUpload();
        } else {
          this.ddTarget.lock = false;
          this.enableUpload();
        }

        this.hydrate(loc.toString());

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

        this.upload.addEventListener('fail', function(e, message) {
          YAHOO.ccgyabi.widget.YabiMessage.fail(message);
        });

        this.upload.addEventListener('remove', function(e, file) {
          self.updateBrowser(self.currentPath());
        });

        this.upload.addEventListener('upload', function(e) {
          YAHOO.ccgyabi.widget.YabiMessage.success(
              'File uploaded successfully');
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
        var fileEl, invoker, selectEl, downloadEl, downloadImg;
        var sizeEl, fileSize, index;
        var fileName;

        //clear existing files
        while (this.fileListEl.firstChild) {
          Y.one(this.fileListEl.firstChild).detachAll();
          this.fileListEl.removeChild(this.fileListEl.firstChild);
        }

        // new style 20090921 has the path as the key for the top level, then
        // files as an array and directories as an array
        // each file and directory is an array of [fname, size in bytes, date]
        for (var toplevelindex in this.browseListing) {
          for (index in this.browseListing[toplevelindex].directories) {
            fileEl = document.createElement('div');
            fileEl.className = 'dirItem';
            fileName = this.browseListing[toplevelindex].directories[index][0];
            if (this.browseListing[toplevelindex].directories[index][3]) {
              // this is a symlink, so change the icon image
              fileEl.className += ' dirLink';
            }

            var fileNameSpan = document.createElement('span');
            fileNameSpan.appendChild(document.createTextNode(fileName));
            fileNameSpan.className = 'fileName';
            fileEl.appendChild(fileNameSpan);

            this.fileListEl.appendChild(fileEl);

            invoker = {
              'target': this,
              'object': new YabiSimpleFileValue(this.pathComponents,
                  fileName, 'directory')
            };

            Y.one(fileEl).on('click', this.expandCallback, null, invoker);

            if (!this.isBrowseMode && this.pathComponents.length > 0) {
              selectEl = document.createElement('a');
              selectEl.appendChild(document.createTextNode('(select)'));
              fileEl.appendChild(selectEl);
              Y.one(selectEl).on('click', this.selectFileCallback,
                  null, invoker);
            } else if (this.isBrowseMode) {
              if (this.pathComponents.length > 0) { // not top-level
                deleteEl = document.createElement('div');
                deleteEl.className = 'deleteFile';
                deleteImg = new Image();
                deleteImg.alt = 'delete';
                deleteImg.title = deleteImg.alt;
                deleteImg.src = appURL + 'static/images/delete.png';
                deleteEl.appendChild(deleteImg);
                fileEl.appendChild(deleteEl);
                Y.one(deleteEl).on('click', this.deleteRemoteFileCallback,
                    null, invoker);

                var dd = new Y.DD.Drag({
                  node: fileEl,
                  target: {},
                  startCentered: true,
                  data: {
                    filename: fileName,
                    invoker: invoker
                  }
                }).plug(Y.Plugin.DDProxy, {
                  moveOnEnd: false
                });
              }
            }
          }
          for (index in this.browseListing[toplevelindex].files) {
            fileEl = document.createElement('div');
            fileEl.className = 'fileItem';
            if (this.browseListing[toplevelindex].files[index][3]) {
              // this is a symlink, so change the icon image
              fileEl.className += ' fileLink';
            }
            var fileNameSpan = document.createElement('span');
            fileNameSpan.appendChild(document.createTextNode(
                this.browseListing[toplevelindex].files[index][0]));
            fileNameSpan.className = 'fileName';
            fileEl.appendChild(fileNameSpan);

            this.fileListEl.appendChild(fileEl);

            //file size
            fileSize = this.browseListing[toplevelindex].files[index][1];
            //convert from bytes to kB or MB or GB
            fileSize = this.humanReadableSizeFromBytes(fileSize);

            sizeEl = document.createElement('div');
            sizeEl.className = 'fileSize';
            sizeEl.appendChild(document.createTextNode(fileSize));
            fileEl.appendChild(sizeEl);

            invoker = {
              target: this,
              object: new YabiSimpleFileValue(this.pathComponents,
                  this.browseListing[toplevelindex].files[index][0]),
              topLevelIndex: toplevelindex
            };

            fileEl.href = appURL + 'preview?uri=' +
                escape(invoker.object.toString());

            /* Both browse and non-browse mode use the preview button, but they
             * need to add them at different points in the tree, so we'll build
             * them here but not append them to the document or hook up the
             * event handler. */
            previewEl = document.createElement('div');
            previewEl.className = 'preview';
            previewImg = new Image();
            previewImg.alt = 'preview';
            previewImg.title = 'preview';
            previewImg.src = appURL + 'static/images/preview.png';
            previewEl.appendChild(previewImg);

            if (!this.isBrowseMode) {
              Y.one(fileEl).on('click', this.selectFileCallback, null, invoker);

              fileEl.appendChild(previewEl);
              Y.one(previewEl).on('click', this.previewFileCallback,
                  null, invoker);
            } else {
              Y.one(fileEl).on('click', this.previewFileCallback,
                  null, invoker);

              deleteEl = document.createElement('div');
              deleteEl.className = 'deleteFile';
              deleteImg = new Image();
              deleteImg.alt = 'delete';
              deleteImg.title = deleteImg.alt;
              deleteImg.src = appURL + 'static/images/delete.png';
              deleteEl.appendChild(deleteImg);
              fileEl.appendChild(deleteEl);
              Y.one(deleteEl).on('click', this.deleteRemoteFileCallback,
                  null, invoker);

              fileEl.appendChild(previewEl);
              Y.one(previewEl).on('click', this.previewFileCallback,
                  null, invoker);

              downloadEl = document.createElement('div');
              downloadEl.className = 'download';
              downloadImg = new Image();
              downloadImg.alt = 'download';
              downloadImg.title = 'download';
              downloadImg.src = appURL + 'static/images/download.png';
              downloadEl.appendChild(downloadImg);
              fileEl.appendChild(downloadEl);
              Y.one(downloadEl).on('click', this.downloadFileCallback,
                  null, invoker);

              var dd = new Y.DD.Drag({
                node: fileEl,
                startCentered: true,
                data: {
                  filename: this.browseListing[toplevelindex].files[index][0],
                  invoker: invoker
                }
              }).plug(Y.Plugin.DDProxy, {
                moveOnEnd: false
              });
            }
          }
        }

      };


      YabiFileSelector.prototype.setUpDragAndDrop = function() {
        var self = this;

        function droppedOnPane(e) {
          var drop = e.drop.get('node');
          return (drop.get('className').indexOf('fileSelectorListing') != -1);
        };

        Y.DD.DDM.on('drag:drophit', function(e) {
          e.halt(true);
          var drop = e.drop;
          var dropNode = e.drop.get('node');
          var targetInvoker;
          var src, dst;

          if (droppedOnPane(e)) {
            // TODO
            // Setting drop.lock to true when the file panel is the root panel
            // doesn't seem to prevent droping on the file panel, so we just
            // short-cut the metod here for now
            if (drop.lock) {
              return;
            }
            targetInvoker = drop.invoker;
          } else {
            targetInvoker = dropNode.dd.get('data').invoker;

            var fileName = dropNode.getElementsByTagName('span');
            fileName.removeClass('dropTarget');
          }

          src = e.target.get('data').invoker.object;
          dst = targetInvoker.object;
          self.handleDrop(src, dst, targetInvoker.target);
        });

        Y.DD.DDM.on('drag:start', function(e) {
          var sourceNode = e.target.get('node');
          var fileNameNode = sourceNode.getElementsByTagName('span');

          var dragNode = e.target.get('dragNode');

          fileNameNode.addClass('dragSource');

          dragNode.set('innerHTML', e.target.get('data').filename);
          dragNode.setStyles({
            'opacity': '.5',
            'borderColor': '#FFFFFF',
            'backgroundColor': '#FFFFFF',
            'width': ''
          });
        });

        Y.DD.DDM.on('drag:end', function(e) {
          var sourceNode = e.target.get('node');
          var fileNameNode = sourceNode.getElementsByTagName('span');
          fileNameNode.removeClass('dragSource');
        });

        Y.DD.DDM.on('drop:enter', function(e) {
          var drop = e.target.get('node');
          if (droppedOnPane(e)) {
            return;
          }
          var fileName = drop.getElementsByTagName('span');
          fileName.addClass('dropTarget');
        });

        Y.DD.DDM.on('drop:exit', function(e) {
          var drop = e.target.get('node');
          if (droppedOnPane(e)) {
            return;
          }
          var fileName = drop.getElementsByTagName('span');
          fileName.removeClass('dropTarget');
        });
      };

      YabiFileSelector.prototype.srcSameAsDest = function(src, dest) {
        var sep = '/';
        var srcBasePath = src.pathComponents.join(sep);
        var destBasePath = dest.pathComponents.join(sep);
        if (srcBasePath !== destBasePath) {
          return false;
        }
        if (src.filename === dest.filename || dest.filename === '') {
          return true;
        }
        return false;
      }

      /**
       * handleDrop
       */
      YabiFileSelector.prototype.handleDrop = function(src, dest, target) {
        if (this.srcSameAsDest(src, dest)) {
          return;
        }
        // default is normal copy
        var baseURL = appURL + 'ws/fs/copy';

        // is source path a directory
        if (src.type == 'directory')
        {
          // we want to use rcopy webservice
          baseURL = appURL + 'ws/fs/rcopy';
        }

        YAHOO.ccgyabi.widget.YabiMessage.success(
            'Copying ' + src + ' to ' + dest);

        var jsUrl, jsCallback, jsTransaction;
        jsUrl = baseURL + '?src=' + escape(src) + '&dst=' + escape(dest);
        jsCallback = {
          success: this.copyResponse,
          failure: function(transId, o) {
            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
          }
        };

        var cfg = {
          on: jsCallback,
          'arguments': {
            target: target
          }
        };
        Y.io(jsUrl, cfg);
      };


      /**
       * updateBreadcrumbs
       *
       * updates the rendered breadcrumb elements for navigating the file
       * hierarchy
       */
      YabiFileSelector.prototype.updateBreadcrumbs = function() {
        var spanEl, invoker;

        while (this.breadcrumbContainerEl.firstChild) {
          this.breadcrumbContainerEl.removeChild(
              this.breadcrumbContainerEl.firstChild);
        }

        if (this.rootEl.firstChild) {
          Y.one(this.rootEl).detachAll();
          this.rootEl.removeChild(this.rootEl.firstChild);
        }

        // a single space acts as a spacer node to prevent the container
        // collapsing around the breadcrumbs
        this.breadcrumbContainerEl.appendChild(document.createTextNode(' '));

        var prevpath = [];
        for (var index in this.pathComponents) {
          if (prevpath.length === 0) {
            spanEl = this.rootEl;
          } else {
            spanEl = document.createElement('span');
          }

          spanEl.appendChild(document.createTextNode(
              this.pathComponents[index]));

          if (prevpath.length === 0) {
          } else {
            this.breadcrumbContainerEl.appendChild(spanEl);
          }

          invoker = {
            'target': this,
            'object': new YabiSimpleFileValue(prevpath.slice(),
                this.pathComponents[index])};

          Y.one(spanEl).on('click', this.expandCallback, null, invoker);

          prevpath.push(this.pathComponents[index]);
        }
      };


      /**
       * getFileIndex
       *
       * Returns the index of the given file in the files array. If it doesn't
       * exist, returns null.
       */
      YabiFileSelector.prototype.getFileIndex = function(
          filename, topLevelIndex) {
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
       * returns YabiJobFileValue objects, unless useInternal is true,
       * when it returns YabiSimpleFileValue objects
       */
      YabiFileSelector.prototype.getValues = function(useInternal) {
        if (useInternal === null) {
          useInternal = false;
        }

        var yjfv;

        if (useInternal) {
          return this.selectedFiles.slice();
        }

        var sanitizedValues = []; //  will be a new array of YabiJobFileValues

        for (var index in this.selectedFiles) {
          yjfv = new YabiJobFileValue(this.param.job,
              this.selectedFiles[index].filename);
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
        var previews = this.browseEl.querySelectorAll('.fileSelectorPreview');
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

        this.selectedFilesEl.className = 'invalidAcceptedExtensionList';
        var nofilesEl = document.createElement('span');
        nofilesEl.className = 'acceptedExtension';

        nofilesEl.appendChild(document.createTextNode('no files selected'));

        this.selectedFilesEl.appendChild(nofilesEl);
      };


      /**
       * renderValid
       *
       * changes display classes to indicate valid selections
       */
      YabiFileSelector.prototype.renderValid = function() {
        this.selectedFilesEl.className = 'validInput';
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
        window.location = appURL + 'ws/fs/get?uri=' + escape(file.toString());
      };


      /**
       * deleteRemoteFile
       */
      YabiFileSelector.prototype.deleteRemoteFile = function(file) {
        var baseURL = appURL + 'ws/fs/rm';

        //load json
        var jsUrl, jsCallback, jsTransaction;
        jsUrl = baseURL + '?uri=' + escape(file.toString());
        jsCallback = {
          success: this.deleteRemoteResponse,
          failure: function(transId, o) {
            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
          }
        };
        var cfg = {
          on: jsCallback,
          'arguments': {
            target: this
          }
        };
        Y.io(jsUrl, cfg);
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
          wrapperEl = document.createElement('div');
          wrapperEl.className = 'filePadding';

          fileEl = document.createElement('span');
          fileEl.className = 'selectedFile';
          fileEl.appendChild(document.createTextNode(
              this.selectedFiles[index].filename));
          fileEl.title = this.selectedFiles[index].filename;

          delEl = document.createElement('div');
          delEl.className = 'destroyDiv';
          fileEl.appendChild(delEl);

          invoker = {'target': this, 'object': index};
          Y.one(delEl).on('click', this.unselectFileCallback, null, invoker);

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
        var baseURL = appURL + 'ws/fs/ls';

        // cancel previous transaction if it exists
        if (this.jsTransaction !== null && this.jsTransaction.isInProgress()) {
          this.jsTransaction.abort();
        }

        //load json
        var jsUrl, jsCallback;
        if (path.length && path.charAt(path.length - 1) != '/')
        {
          path += '/';
        }
        jsUrl = baseURL + '?uri=' + escape(path);
        jsCallback = {
          success: this.hydrateResponse,
          failure: function(transId, o, args) {
            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
            args.target.loading.hide();
          }
        };
        var cfg = {
          on: jsCallback,
          'arguments': {
            target: this
          }
        };
        this.jsTransaction = Y.io(jsUrl, cfg);
      };


      /**
       * humanReadableSizeFromBytes
       */
      YabiFileSelector.prototype.humanReadableSizeFromBytes = function(bytes) {
        if (!Y.Lang.isNumber(bytes)) {
          return bytes;
        }

        var humanSize;

        if (bytes > (300 * 1024 * 1024)) { //GB
          humanSize = bytes / (1024 * 1024 * 1024);
          humanSize = humanSize.toFixed(2);
          humanSize += ' GB';
          return humanSize;
        }

        if (bytes > (300 * 1024)) { //MB
          humanSize = bytes / (1024 * 1024);
          humanSize = humanSize.toFixed(2);
          humanSize += ' MB';
          return humanSize;
        }

        //kB
        humanSize = bytes / (1024);
        humanSize = humanSize.toFixed(1);
        if (humanSize == 0.0 && bytes > 0) {
          humanSize = 0.1;
        }
        humanSize += ' kB';
        return humanSize;
      };


      // ==== CALLBACKS ====
      /**
       * goToRoot
       *
       * load the root element to get a list of fs backends
       */
      YabiFileSelector.prototype.goToRoot = function(e, target) {
        target.updateBrowser(new YabiSimpleFileValue([], ''));
      };

      YabiFileSelector.prototype.selectFileCallback = function(e, invoker) {
        e.halt(true);
        var target = invoker.target;
        target.selectFile(invoker.object);
      };

      YabiFileSelector.prototype.downloadFileCallback = function(e, invoker) {
        e.halt(true);
        var target = invoker.target;
        target.downloadFile(invoker.object);
      };

      YabiFileSelector.prototype.deleteRemoteFileCallback = function(
          e, invoker) {
        e.halt(true);
        var target = invoker.target;

        //file deletion
        target.deleteRemoteFile(invoker.object);
      };

      YabiFileSelector.prototype.unselectFileCallback = function(e, invoker) {
        var target = invoker.target;
        target.deleteFileAtIndex(invoker.object);
      };

      YabiFileSelector.prototype.expandCallback = function(e, invoker) {
        e.halt(true);
        var target = invoker.target;
        target.updateBrowser(invoker.object);
      };

      YabiFileSelector.prototype.previewFileCallback = function(e, invoker) {
        e.halt(true);
        var target = invoker.target;
        target.previewFile(invoker.object, invoker.topLevelIndex);
      };

      YabiFileSelector.prototype.deleteRemoteResponse = function(
          transId, o, args) {
        var json = o.responseText;

        var target = args.target;

        target.updateBrowser(
            new YabiSimpleFileValue(target.pathComponents, ''));
      };

      YabiFileSelector.prototype.hydrateResponse = function(transId, o, args) {
        var json = o.responseText;

        try {
          var target = args.target;

          target.hydrateProcess(Y.JSON.parse(json));
        } catch (e) {
          YAHOO.ccgyabi.widget.YabiMessage.fail('Error loading file listing');

          target.loading.hide();
        } finally {
          this.jsTransaction = null;
        }
      };

      YabiFileSelector.prototype.copyResponse = function(transId, o, args) {
        YAHOO.ccgyabi.widget.YabiMessage.success('Copying finished');

        var json = o.responseText;

        //invoke refresh on component
        var target = args.target;
        target.updateBrowser(
            new YabiSimpleFileValue(target.pathComponents, ''));
      };

      /**
       * YabiFileCopyStatusPane
       *
       * Overlays a large spinner on the window
       */
      var YabiFileCopyStatusPane = function(fs) {
        this.fs = fs;

        this.spinnerEl = document.createElement('div');
        this.spinnerEl.className = 'fileCopyStatusPane';

        this.fs.browseEl.appendChild(this.spinnerEl);
      };


      /**
       * YabiFileSelectorPreview
       *
       * An object that provides an overlay over a given YabiFileSelector that
       * securely previews the given file.
       */
      var YabiFileSelectorPreview = function(fs, file, topLevelIndex) {
        this.fs = fs;
        this.file = file;
        this.loadCallbackFired = false;
        this.topLevelIndex = topLevelIndex;
        this.uri = appURL + 'preview?uri=' + escape(file.toString());

        this.previous = this.getPrevious();
        this.next = this.getNext();

        // THERE CAN BE ONLY ONE.
        this.fs.purgePreviewElements();

        this.previewEl = document.createElement('div');
        this.previewEl.className = 'fileSelectorPreview';

        this.createControls();
        this.createIFrame();

        this.fs.browseEl.appendChild(this.previewEl);
      };


      /**
       * createControlButton
       *
       * Internal method to create a fake button in the preview control bar.
       */
      YabiFileSelectorPreview.prototype.createControlButton = function(
          className, onClick, title) {
        var button = document.createElement('div');
        button.className = 'controlButton ' + className;

        if (onClick) {
          button.className += ' enabled';

          Y.one(button).on('click', onClick);
        }
        else {
          button.className += ' disabled';
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
      YabiFileSelectorPreview.prototype.createControls = function() {
        var self = this;

        var controls = document.createElement('div');
        controls.className = 'fileSelectorPreviewControls';

        this.title = document.createElement('h3');
        this.title.className = 'fileSelectorPreviewTitle';
        this.title.appendChild(document.createTextNode(this.file.filename));

        controls.appendChild(this.title);

        // Add buttons.
        controls.appendChild(this.createControlButton(
            'fileSelectorPreviewClose',
            function(e) {
              self.closeCallback();
            }, 'close preview'));

        controls.appendChild(this.createControlButton(
            'fileSelectorPreviewDownload',
            function(e) {
              self.fs.downloadFile(self.file);
            }, 'download file'));

        var previousCallback = null;
        var title = null;
        if (this.previous) {
          previousCallback = function(e) {
            self.fs.previewFile(self.previous, self.topLevelIndex);
          };

          title = this.previous.filename;
        }
        controls.appendChild(this.createControlButton(
            'fileSelectorPreviewPrevious', previousCallback, title));

        var nextCallback = null;
        title = null;
        if (this.next) {
          nextCallback = function(e) {
            self.fs.previewFile(self.next, self.topLevelIndex);
          };

          title = this.next.filename;
        }
        controls.appendChild(this.createControlButton('fileSelectorPreviewNext',
            nextCallback, title));

        this.previewEl.appendChild(controls);
      };


      /**
       * createIFrame
       *
       * Internal method to create the iframe for the previewed file.
       */
      YabiFileSelectorPreview.prototype.createIFrame = function() {
        var self = this;

        var container = document.createElement('div');
        container.className = 'fileSelectorPreviewFrameContainer';

        this.iframeEl = document.createElement('iframe');
        this.iframeEl.className = 'loading';
        this.iframeEl.frameBorder = 0;
        this.iframeEl.src = this.uri;

        Y.one(this.iframeEl).on('load', function(e) {
          self.loadCallback();
        }, self);
        container.appendChild(this.iframeEl);
        this.previewEl.appendChild(container);
      };


      /**
       * closeCallback
       *
       * Handler for clicks on the close button.
       */
      YabiFileSelectorPreview.prototype.closeCallback = function() {
        this.fs.purgePreviewElements();
      };


      /**
       * loadCallback
       *
       * Handler called when the iframe has loaded.
       */
      YabiFileSelectorPreview.prototype.loadCallback = function() {
        var self = this;

        if (this.loadCallbackFired) {
          return;
        }
        this.loadCallbackFired = true;

        this.iframeEl.className = '';

        var callbacks = {
          success: function(transId, o) {
            self.metadataCallback(o);
          },
          failure: function(transId, o) {
            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
          }
        };

        var url = appURL + 'preview/metadata?uri=' +
            escape(this.file.toString());
        Y.io(url, { on: callbacks });
      };


      /**
       * metadataCallback
       *
       * Handler called when preview metadata is available.
       */
      YabiFileSelectorPreview.prototype.metadataCallback = function(o) {
        var metadata = Y.JSON.parse(o.responseText);

        var span = document.createElement('span');
        span.className = 'fileSelectorPreviewMetadata';

        var size = document.createElement('span');
        size.className = 'fileSelectorPreviewSize';
        size.appendChild(document.createTextNode(
            this.fs.humanReadableSizeFromBytes(metadata.size)));
        span.appendChild(size);

        if (metadata.truncated) {
          var truncatedLength = this.fs.humanReadableSizeFromBytes(
              metadata.truncated);

          // Oh, English.
          var verb = 'are';
          if (truncatedLength.slice(0, 4) == '1.00') {
            verb = 'is';
          }

          var truncated = document.createElement('span');
          truncated.className = 'fileSelectorPreviewTruncated';
          truncated.title = 'This file is too long to be previewed in full. ' +
              'The first ' + truncatedLength + ' ' + verb + ' shown below. ' +
              'To view the complete file, please download it.';
          truncated.appendChild(document.createTextNode('truncated'));

          /* This would be better done in CSS with a generated content block,
           * but the border style can't be overridden in a :before style,
           * which is ugly.
           */
          span.appendChild(document.createTextNode('; '));

          span.appendChild(truncated);
        }

        this.title.appendChild(span);
      };


      /**
       * getPrevious
       *
       * Returns the previous file in the file selector's file array or null
       * if the file is the first one.
       */
      YabiFileSelectorPreview.prototype.getPrevious = function() {
        var files = this.fs.browseListing[this.topLevelIndex].files;
        var index = this.fs.getFileIndex(
            this.file.filename, this.topLevelIndex);

        if (index !== null && index > 0) {
          if (--index in files) {
            return new YabiSimpleFileValue(
                this.fs.pathComponents, files[index][0]);
          }
        }

        return null;
      };


      /**
       * getNext
       *
       * Returns the next file in the file selector's file array or null if
       * the file is the last one.
       */
      YabiFileSelectorPreview.prototype.getNext = function() {
        var files = this.fs.browseListing[this.topLevelIndex].files;
        var index = this.fs.getFileIndex(this.file.filename,
            this.topLevelIndex);

        if (index !== null) {
          if (++index in files) {
            return new YabiSimpleFileValue(this.fs.pathComponents,
                files[index][0]);
          }
        }

        return null;
      };


    }); // end of YUI().use()
