YUI().use(
    'node', 'event', 'dd-drag', 'dd-proxy', 'dd-drop', 'io', 'json', 'anim', 'cookie',
    function(Y) {
      isFinishedStatus = _.partial(_.include, ['complete', 'aborted', 'error']);

      didWorkflowFinish = function(wfl_status, jobs) {
        return isFinishedStatus(wfl_status) && _.all(_.pluck(jobs, 'status'), isFinishedStatus);
      };

      /**
       * YabiWorkflow
       * create a new workflow, which handles overall validation status as well
       * as ordering/sequencing and ensuring that file inputs are
       * managed in a sequential, logical manner
       */
      YabiWorkflow = function(editable, reusing) {
        this.editable = editable ? true : false;
        this.reusing = reusing ? true : false;
        this.workflowLoaded = false;
        this.draftLoaded = true;
        this.payload = {};
        this.isPropagating = false; //recursion protection
        this.tags = [];
        this.jobs = [];
        this.attachedProxies = [];
        this.setupJobsList = [];
        this.status = 'Design';
        this.selectedJob = null;


        this.container = Y.Node.create('<div class="workflowContainer"/>');

        // construct the main dom, including title, submit (if editable) and
        // bookends
        this.mainEl = document.createElement('div');

        if (this.editable) {
          this.submitEl = document.createElement('button');
          this.submitEl.appendChild(document.createTextNode('run'));
          this.submitEl.id = 'submitButton';
          this.submitEl.className = 'fakeButton largeButton';
          this.mainEl.appendChild(this.submitEl);

          this.nameEl = document.createElement('input');
          this.nameEl.className = 'workflowName';
          this.nameEl.id = 'titleDiv';

          Y.one(this.nameEl).on('blur', this.nameBlurCallback, null, this);
          Y.one(this.nameEl).on('keyup', this.nameChangeCallback, null, this);
          Y.one(this.nameEl).on('change', this.nameChangeCallback, null, this);
          Y.one(this.nameEl).on('click', this.nameFocusCallback, null, this);
        } else {
          this.nameEl = document.createElement('div');
          this.nameEl.className = 'workflowName';
          this.nameEl.id = 'titleDiv';
        }

        if (editable) {
          this.setInitialName("unnamed");
        }

        this.mainEl.appendChild(this.nameEl);

        //tag el
        this.tagEl = document.createElement('div');
        this.tagEl.className = 'tagListContainer';
        this.tagEl.appendChild(document.createTextNode('Tags: '));

        this.tagListEl = document.createElement('span');
        this.tagListEl.className = 'tagList';
        this.tagEl.appendChild(this.tagListEl);

        this.tagInputEl = document.createElement('input');
        this.tagInputEl.className = 'displayNone';
        this.tagEl.appendChild(this.tagInputEl);

        this.tagAddLink = document.createElement('div');
        this.tagAddLink.className = 'tagAddLink';
        Y.one(this.tagAddLink).on('click', this.addTagCallback, null, this);
        this.tagEl.appendChild(this.tagAddLink);

        this.tagHintDiv = document.createElement('div');
        this.tagHintDiv.className = 'displayNone';

        this.tagCancelEl = document.createElement('span');
        this.tagCancelEl.className = 'fakeButton';
        this.tagCancelEl.appendChild(document.createTextNode('cancel'));
        Y.one(this.tagCancelEl).on('click', this.cancelTagsCallback,
            null, this);

        this.tagSaveEl = document.createElement('span');
        this.tagSaveEl.className = 'fakeButton';
        this.tagSaveEl.appendChild(document.createTextNode('save'));
        Y.one(this.tagSaveEl).on('click', this.saveTagsCallback, null, this);

        this.tagHintDiv.appendChild(this.tagCancelEl);
        this.tagHintDiv.appendChild(this.tagSaveEl);
        this.tagEl.appendChild(this.tagHintDiv);

        //tag help bubble
        this.tagHelpEl = document.createElement('div');
        this.tagHelpEl.className = 'tagHelp';
        var helpImg = new Image();
        helpImg.src = appURL + 'static/images/tagHelp.png';
        this.tagHelpEl.appendChild(helpImg);
        this.tagEl.appendChild(this.tagHelpEl);
        Y.one(this.tagHelpEl).on('click', function(e, obj) {
          var myAnim = new Y.Anim({
            node: Y.one(obj.tagHelpEl),
            to: { opacity: 0 },
            easing: 'easeOut',
            duration: 0.5
          });
          myAnim.on('end', function() {
            obj.tagHelpEl.style.display = 'none';
          }, this);
          myAnim.run();
        }, null, this);


        this.mainEl.appendChild(this.tagEl);

        //actions toolbar
        var toolbar = Y.Node.create('<div class="workflowToolbar" />').appendTo(this.mainEl);
        this.toolbar = toolbar;

        if (!this.editable) {
          Yabi.util.fakeButton('re-use')
            .appendTo(toolbar)
            .on('click', this.reuseCallback, null, this);
        } else {
          var clear = Yabi.util.fakeButton("clear").appendTo(toolbar);
          var yes = Yabi.util.fakeButton("Yes"), no = Yabi.util.fakeButton("No");
          var dlg = Y.Node.create('<div class="workflowSaveAsDlg" />')
            .append(Y.Node.create('<label>Clear workflow?</label').append(yes).append(no))
            .appendTo(this.mainEl)
            .hide();

          var self = this;
          var reset = function() {
            toolbar.show();
            dlg.hide();
          };

          clear.on('click', function() {
            dlg.show();
            toolbar.hide();
          });
          yes.on('click', function() {
            self.clear();
            reset();
          });
          no.on('click', function() {
            reset();
          });
        }

        Yabi.util.fakeButton(this.editable ? 'save' : 'save as')
          .appendTo(toolbar)
          .on('click', this.saveAsCallback, null, this);

        this.startEl = document.createElement('div');
        this.startEl.appendChild(document.createTextNode('start'));
        this.startEl.className = 'workflowStartBookend';

        this.mainEl.appendChild(this.startEl);

        //add empty workflow marker
        this.hintNode = Y.Node.create('<div class="workflowHint" />')
          .appendTo(this.mainEl).toggleView(this.editable);
        if (this.editable) {
          this.hintNode.append('<div>drag tools here to begin<br />' +
              '(or use the <span>add</span> buttons)</div>');
        }

        this.container.appendTo(this.mainEl);

        this.endEl = document.createElement('div');
        this.endEl.appendChild(document.createTextNode('end'));
        this.endEl.className = 'workflowEndBookend';

        this.mainEl.appendChild(this.endEl);

        if (this.editable) {
          this.dd = new Y.DD.Drop({
            node: this.container
          });
          this.dd.on('drop:over', this.onDragOverJobCallback);

          // TODO - see other registerDDTarget for TODO expl.
          YabiToolCollection.registerDDTarget(this.container);
        }

        this.optionsEl = document.createElement('div');
        this.optionsEl.className = 'jobOptionsContainer';

        this.statusEl = document.createElement('div');
        this.statusEl.className = 'jobStatusContainer';

        if (!editable) {
          var header;
          this.fileOutputsEl = document.createElement('div');
          this.fileOutputsEl.className = 'fileOutputs';
          header = document.createElement('h1');
          header.appendChild(document.createTextNode('File outputs'));
          this.fileOutputsEl.appendChild(header);

          // not editable, create a file selector to point at the
          // stageout directory if it exists
          this.fileOutputsSelector = new YabiFileSelector(
              null, true, null, true);
          this.fileOutputsSelector.homeEl.style.display = 'none';
          this.fileOutputsEl.appendChild(this.fileOutputsSelector.containerEl);
          this.fileOutputsEl.style.display = 'none';
          this.fileOutputsSelector.containerEl.style.marginLeft = '4px';
        }

        //add an enter key listener for the tags field
        Y.one(this.tagInputEl).on('keypress', function(e) {
          if (e.keyCode !== 13) {
            return;
          }
          this.saveTags();
        }, this);

        if (!reusing) {
          this.loadDraft();
        }
      };

      YabiWorkflow.prototype.setStatus = function(obj) {
        var statusText = obj.status;
        var is_retrying = obj.is_retrying;
        this.status = statusText.toLowerCase();

        //update proxies
        var proxy;
        for (index in this.attachedProxies) {
          proxy = this.attachedProxies[index];
          proxy.payload.status = this.status;
          proxy.payload.is_retrying = is_retrying;
          proxy.renderStatus();
        }

        if (this.editable) {
          return;
        }

        var loadImg;
        if (!didWorkflowFinish(obj.status, obj.json.jobs)) {
          if (this.toolbar.all('button.abortWorkflow').isEmpty()) {
            Yabi.util.fakeButton('abort', 'abortWorkflow')
              .appendTo(this.toolbar)
              .on('click', this.abortCallback, null, this);
          }
          if (!Y.Lang.isValue(this.loadingEl)) {
            this.loadingEl = document.createElement('div');
            this.loadingEl.className = 'workflowLoading';
            loadImg = new Image();
            loadImg.src = appURL + 'static/images/processing.gif';
            this.loadingEl.appendChild(loadImg);

            this.loadingTextEl = document.createElement('span');
          }

          this.loadingTextEl.innerHTML = 'workflow running, ' +
              'waiting for completion...';
          this.loadingEl.appendChild(this.loadingTextEl);

          this.mainEl.appendChild(this.loadingEl);
        } else {
          if (Y.Lang.isValue(this.loadingEl)) {
              this.mainEl.removeChild(this.loadingEl);
              this.loadingEl = null;
          }
          var abortBtn = this.toolbar.one('button.abortWorkflow');
          if (abortBtn !== null) {
            abortBtn.remove(true);
          }
          if (this.toolbar.all('button.deleteWorkflow').isEmpty()) {
            Yabi.util.fakeButton('delete', 'deleteWorkflow')
              .appendTo(this.toolbar)
              .on('click', this.deleteCallback, null, this);
          }
        }
      };

      /* sets a name for the workflow, using the date to uniquify it */
      YabiWorkflow.prototype.setInitialName = function(base) {
        //util fn
        var dblzeropad = function(number) {
          if (number < 10) {
            number = '0' + number;
          }
          return number;
        };
        var date = new Date();
        this.name = base + ' (' +
          date.getFullYear() + '-' + dblzeropad(date.getMonth() + 1) + '-' +
          dblzeropad(date.getDate()) + ' ' +
          dblzeropad(date.getHours()) + ':' +
          dblzeropad(date.getMinutes()) + ')';
        this.prefillName = this.name;

        this.nameEl.value = this.name;
      };

      /* returns true iff the user hasn't edited the name */
      YabiWorkflow.prototype.nameIsUnchanged = function() {
        return this.name === this.prefillName;
      };

      /* returns true iff the workflow has no jobs */
      YabiWorkflow.prototype.isEmpty = function() {
        return this.jobs.length === 0;
      };


      /**
       * addJob
       *
       * adds a job to the end of the workflow
       */
      YabiWorkflow.prototype.addJob = function(toolName, toolId, preloadValues,
          shouldFadeIn) {

        if (this.processing) {
          return;
        }
        this.processing = true;

        this.hintNode.hide();

        var job = new YabiJob(toolName, toolId, this.jobs.length + 1, preloadValues);
        job.editable = this.editable;
        if (!this.editable) {
          job.inputsNode.hide();
          job.outputsNode.hide();
        }
        job.workflow = this;
        this.jobs.push(job);

        job.hydrate();

        job.container.on('click', function(e, job) {
          e.halt(true);
          this.selectJob(job);
        }, this, job);

        if (!this.editable) {
          //don't select any job (ie select null)
          this.selectJob(null);
        } else {
          //decorate the job with a 'destroy' link
          Y.Node.create('<div class="destroyDiv"/>')
            .append(Y.Node.create('<img title="delete tool" alt="delete tool"/>')
                    .set("src", appURL + 'static/images/delnode.png'))
            .appendTo(job.jobNode)
            .on('click', function(e, job) {
              //prevent propagation of the event to select/deselecting the job
              e.halt(true);
              this.deleteJob(job);
            }, this, job);

          //drag drop
          job.dd = new Y.DD.Drag({
            node: job.container,
            target: {}
          }).plug(Y.Plugin.DDProxy, {
            moveOnEnd: false
          });

          // TODO
          // We are registering this as DD.Drops in the YUI instance of the tool
          // collection, otherwise the tools can't be dropped on top of the job
          // elements. There has to be a better way to do this!
          YabiToolCollection.registerDDTarget(job.container);

          job.dd.on('drag:start', this.startDragJobCallback);
          job.dd.on('drag:end', this.endDragJobCallback);
          job.dd.on('drag:drag', this.onDragJobCallback);
          job.dd.on('drag:over', this.onDragOverJobCallback);

          //select the new item but only if we are editable
          this.selectJob(job);
        }

        if (Y.Lang.isUndefined(shouldFadeIn)) {
          shouldFadeIn = true;
        }

        if (shouldFadeIn) {
          //start off the opacity at 0.0
          job.container.setStyle("opacity", 0.0);
        }

        //add into the DOM
        this.container.append(job.container);
        job.optionsNode.appendTo(this.optionsEl);
        job.statusNode.appendTo(this.statusEl);

        if (shouldFadeIn) {
          new Y.Anim({
            node: job.container,
            to: { opacity: 1.0 },
            duration: 1.0
          }).run();
        }

        this.processing = false;

        this.onJobChanged(job);

        return job;
      };


      /**
       * deleteJob
       *
       * this uses simple locking to prevent multiple deletes happening
       * concurrently, which causes validation errors
       */
      YabiWorkflow.prototype.deleteJob = function(job) {
        if (this.deleting) {
          return;
        }

        this.deleting = true;
        var counter = 1;
        var delIndex = -1;

        if (job == this.selectedJob) {
          this.selectedJob = null;

          this.afterSelectJob(null);
        }

        //iterate jobs array, leaving out this item
        //reassigning jobId
        for (var index in this.jobs) {
          if (this.jobs[index] == job) {
            delIndex = index;
            continue;
          }

          this.jobs[index].jobId = counter++;
          this.jobs[index].updateTitle();
        }

        this.jobs.splice(delIndex, 1);

        this.removeJobNode(job);

        this.hintNode.toggleView(this.jobs.length === 0);

        //force propagate
        this.propagateFiles();

        this.saveDraft();

        this.deleting = false;
      };

      YabiWorkflow.prototype.removeJobNode = function(job) {
        job.destroy();

        job.container.remove();
        job.optionsNode.remove();
        job.statusNode.remove();

        job.container.detachAll();
      };

      /* resets workflow to initial state */
      YabiWorkflow.prototype.clear = function() {
        _.forEach(this.jobs, this.removeJobNode, this);
        this.tags = [];
        this.jobs = [];
        this.setInitialName("unnamed");

        this.refreshTagList();

        this.selectedJob = null;
        this.afterSelectJob(null);

        this.hintNode.show();

        this.deleteDraft();
      };


      /**
       * attachProxy
       *
       * attaches a workflowProxy to this workflow, so that changes in this
       * workflow are propagated back to the proxy
       */
      YabiWorkflow.prototype.attachProxy = function(proxy) {
        this.attachedProxies.push(proxy);
      };


      /**
       * propagateFiles
       *
       * iterates over the jobs, querying the jobs for their emittedOutputs,
       * using those outputs to prefill following jobs the optional 'sender'
       * param is to specify which node to start propagating from, to prevent
       * trying to cause that and previous jobs from consuming their own values
       * into oblivion
       */
      YabiWorkflow.prototype.propagateFiles = function(sender) {
        //recursion protection
        if (this.isPropagating) {
          return;
        }

        var subEmitted;

        this.isPropagating = true;
        var emittedFiles = [];
        var emittedKeys = []; //used for duplicate protection
        var foundSender = false;
        //if we have no sender, then we are propagating the whole workflow
        if (Y.Lang.isUndefined(sender)) {
          foundSender = true;
        }

        // iterate
        for (var index in this.jobs) {
          // do not allow the sender or above to consume
          if (foundSender) {
            this.jobs[index].optionallyConsumeFiles(emittedFiles, false);
          }
          // flag that the sender is found, after the optional consume, so the
          //  sender doesn't consume
          if (this.jobs[index] == sender) {
            foundSender = true;
          }

          subEmitted = this.jobs[index].emittedFiles().slice();
          if (subEmitted.length > 0) {
            for (var subindex in subEmitted) {
              // duplicates have a value
              if (!emittedKeys.hasOwnProperty(subEmitted[subindex])) {
                emittedFiles.push(subEmitted[subindex]);
                emittedKeys[subEmitted[subindex]] = 1;
              }
            }
          }
        }
        this.isPropagating = false;

        //afterPropagate call for other objects to hook in to
        if (!Y.Lang.isUndefined(this.afterPropagate) &&
            !Y.Lang.isUndefined(sender)) {
          this.afterPropagate(sender);
        }
      };


      /**
       * selectJob
       *
       * tells a job to render as selected, and tells all other jobs to render
       * deselected
       */
      YabiWorkflow.prototype.selectJob = function(object) {
        if (!this.editable) {
          this.fileOutputsEl.style.display = 'none';
        }

        //iterate
        var selectedIndex = null;
        for (var index in this.jobs) {
          if (this.jobs[index] == object) {
            if (object == this.selectedJob) {
              this.jobs[index].deselectJob();
              this.selectedJob = null;

              // callback hook to allow other elements to hook in when jobs are
              // selected/deselected
              if (!Y.Lang.isUndefined(this.afterSelectJob) && object.loaded) {
                this.afterSelectJob(null);
              }
            } else {
              selectedIndex = index;
            }
          } else {
            this.jobs[index].deselectJob();
          }
        }

        /* Firing selectJob() used to occur within the for loop, but it's more
         * logically sensible (and makes it easier to write code handling
         * deselection and selection) to make all the deselectJob() calls above
         * and then fire selectJob() last.
         */
        if (selectedIndex !== null) {
          this.jobs[selectedIndex].selectJob();
          this.selectedJob = object;

          if (!this.editable) {
              var dirToDisplay = [];
              var loadContents = false;
              var selectedJob = this.payload.jobs[selectedIndex];
              if (!Y.Lang.isUndefined(selectedJob.stageout)) {
                  dirToDisplay = selectedJob.stageout;
              }
              if (selectedJob.status === 'complete') {
                loadContents = true;
              }
              this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue(
                          dirToDisplay, ''), loadContents);
          }

          // callback hook to allow other elements to hook in when jobs are
          // selected/deselected
          if (!Y.Lang.isUndefined(this.afterSelectJob) && object.loaded) {
            this.afterSelectJob(object);
          }
        }
      };


      /**
       * delayedSelectJob
       *
       * exists for the purpose of allowing an afterSelectJob callback after a
       * tool has loaded
       */
      YabiWorkflow.prototype.delayedSelectJob = function(job) {
        this.afterSelectJob(job);
      };


      YabiWorkflow.prototype.onJobLoaded = function(job) {
        if (!this.workflowLoaded && _.every(this.jobs, "loaded")) {
          this.onWorkflowLoaded();
        }
      };

      YabiWorkflow.prototype.onWorkflowLoaded = function(value) {
        this.workflowLoaded = true;
        if (this.reusing) {
          this.setupJobParams(this.jobs);
        } else if (this.setupJobsList.length > 0) {
          this.setupJobParams(this.setupJobsList);
          this.setupJobsList = [];
        }
      };

      /**
       * updateName
       *
       * updates the workflow name and rendering
       */
      YabiWorkflow.prototype.updateName = function(value) {
        this.name = value;

        if (this.editable) {
          this.nameEl.value = value;
        } else {
          while (this.nameEl.firstChild) {
            this.nameEl.removeChild(this.nameEl.firstChild);
          }

          this.nameEl.appendChild(document.createTextNode(value));
        }
      };


      /**
       * getName
       *
       */
      YabiWorkflow.prototype.getName = function() {
        if (this.editable) {
          return this.nameEl.value;
        } else {
          return this.name;
        }
      };


      /**
       * getDisplayNameForJobId
       */
      YabiWorkflow.prototype.getDisplayNameForJobId = function(jobId) {
        var num = parseInt(jobId, 10);
        num = num - 1;

        if (num < this.jobs.length) {
          return this.jobs[num].toString();
        } else {
          return 'unknown';
        }
      };


      /**
       * isJobIdLoaded
       */
      YabiWorkflow.prototype.isJobIdLoaded = function(jobId) {
        var num = parseInt(jobId, 10);
        num = num - 1;

        if (num < this.jobs.length) {
          return this.jobs[num].loaded;
        } else {
          //no such jobId, so, uh, yes it is
          return true;
        }
      };


      /**
       * getJobForId
       */
      YabiWorkflow.prototype.getJobForId = function(jobId) {
        var num = parseInt(jobId, 10);
        num = num - 1;

        if (num < this.jobs.length) {
          return this.jobs[num];
        } else {
          //no such jobId, so, uh, oops
          return null;
        }
      };


      /**
       * isValid
       *
       * verify validity of all jobs before proceeding
       */
      YabiWorkflow.prototype.isValid = function() {
        var nameValid = this.getName() !== '' && this.getName().indexOf('?') === -1;

        this.nameEl.className = nameValid ? 'workflowName' : 'invalidWorkflowName';

        return this.jobs.length > 0 &&
          nameValid && _.every(this.jobs, "valid");
      };


      /**
       * toJSON
       *
       * produces a json string for this workflow
       */
      YabiWorkflow.prototype.toJSON = function() {
        return Y.JSON.stringify({
          name: this.name,
          tags: this.tags,
          jobs: _.map(this.jobs, function(job) { return job.toJSON(); })
        });
      };

      /**
       * hydrate
       *
       * fetch workflow definition from the server
       */
      YabiWorkflow.prototype.hydrate = function(workflowId) {
        var loadImg;

        if (Y.Lang.isUndefined(this.workflowId)) {
          this.hydrateDiv = document.createElement('div');
          this.hydrateDiv.className = 'workflowHydrating';
          loadImg = new Image();
          loadImg.src = appURL + 'static/images/largeLoading.gif';
          this.hydrateDiv.appendChild(loadImg);
          document.body.appendChild(this.hydrateDiv);
        }

        this.workflowId = workflowId;
        var baseURL = appURL + 'ws/workflows/get/' + workflowId;

        //load json
        var jsUrl, jsCallback, jsTransaction;
        jsUrl = baseURL;
        jsCallback = {
          success: this.hydrateCallback,
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
        this.jsTransaction = Y.io(jsUrl, cfg);

      };

      YabiWorkflow.prototype.fadeHydratingDiv = function() {
        //fade out and remove the loading element
        if (!Y.one(document.body).contains(this.hydrateDiv)) {
          return;
        }
        var anim = new Y.Anim({
          node: Y.one(this.hydrateDiv),
          to: { opacity: 0 },
          duration: 0.3
        });
        anim.on('end', function() {
          document.body.removeChild(this.hydrateDiv);
        }, this);
        anim.run();
      };


      /**
       * reuse
       *
       * reload the whole page with a reuse URL
       */
      YabiWorkflow.prototype.reuse = function() {
        var baseURL = appURL + 'design/reuse/' + this.workflowId;

        window.location = baseURL;
      };

      /**
       * save as
       *
       * submits the workflow to server
       */
      YabiWorkflow.prototype.saveAs = function(name) {
        if (this.isValid() || true) {
          var oldName = this.name;
          var name = name || oldName;
          this.name = name;

          Y.io(appURL + "ws/workflows/save/", {
            method: 'POST',
            on: {
              success: function(transId, obj, args) {
                YAHOO.ccgyabi.widget.YabiMessage.success("Saved workflow " + name);
              },
              failure: function(transId, obj) {
                YAHOO.ccgyabi.widget.YabiMessage.fail("Failed to save :-(");
              }
            },
            data: { workflowjson: this.toJSON() }
          });

          this.name = oldName;
        } else {
          var msg = "Workflow isn't valid. Please correct errors before saving.";
          YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
        }
      };

      YabiWorkflow.prototype.deleteWorkflow = function() {
        Y.io(appURL + "ws/workflows/delete/", {
          method: 'POST',
          on: {
            success: function(transId, obj, args) {
              resp = Y.JSON.parse(obj.responseText);
              if (resp.status === 'error') {
                var msg = "Failed to delete";
                if (typeof(resp.message !== 'undefined')) {
                  msg += ": " + resp.message;
                }
                YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
                return;
              }
              YAHOO.ccgyabi.widget.YabiMessage.success("Deleted workflow");
              // TODO don't reload page, just reload workflow listing
              // it requires more work than expected
              window.location = appURL + "jobs";
            },
            failure: function(transId, obj) {
              YAHOO.ccgyabi.widget.YabiMessage.fail("Failed to delete");
            }
          },
          data: { id: this.workflowId }
        });
      };

      YabiWorkflow.prototype.abortWorkflow = function() {
        Y.io(appURL + "ws/workflows/abort/", {
          method: 'POST',
          on: {
            success: function(transId, obj, args) {
              resp = Y.JSON.parse(obj.responseText);
              if (resp.status === 'error') {
                var msg = "Failed to abort";
                if (typeof(resp.message !== 'undefined')) {
                  msg += ": " + resp.message;
                }
                YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
                return;
              }
              YAHOO.ccgyabi.widget.YabiMessage.success("Abort of workflow requested");
            },
            failure: function(transId, obj) {
              YAHOO.ccgyabi.widget.YabiMessage.fail("Failed to abort");
            }
          },
          data: { id: this.workflowId }
        });
      };

      YabiWorkflow.prototype.onJobChanged = function(job) {
        this.saveDraft();
      };

      YabiWorkflow.prototype.saveDraft = function() {
        if (this.editable && this.draftLoaded) {
          Y.Cookie.set("workflow", this.toJSON());
        }
      };

      YabiWorkflow.prototype.deleteDraft = function(preventSaves) {
        if (preventSaves) {
          // Sometimes you want to delete the draft and prevent
          // callback functions, etc from saving it again.
          this.draftLoaded = false;
        }
        Y.Cookie.remove("workflow");
      };

      YabiWorkflow.prototype.loadDraft = function() {
        var loadMigrateWorkflow = function(json) {
          var ob;
          if (json) {
            ob = Y.JSON.parse(json);
            if (!(ob && ob.jobs && _.all(ob.jobs, "toolId"))) {
              // discard drafts from older versions which don't have toolId
              ob = null;
            }
          }
          return ob;
        };

        if (this.editable) {
          this.draftLoaded = false;
          var ob = loadMigrateWorkflow(Y.Cookie.get("workflow"));
          if (ob) {
            this.solidify(ob);
            this.setTags(ob.tags);
            this.setupJobsList = this.jobs;
            this.prefillName = ob.name;
          }
          this.draftLoaded = true;
        }
      };

      /**
       * Job parameters can't be set until the tool definitions are
       * loaded.
       *
       * This method is called after all tools are loaded, when there
       * are params which need to be set.
       *
       * Params need to be set when reusing workflows, importing saved
       * workflows, or loading a saved draft workflow.
       */
      YabiWorkflow.prototype.setupJobParams = function(jobs) {
        function collectAllInputFileParams(jobs) {
          return jobs.map(function(job) {
            return _.filter(job.params, "isInputFile");
          }).flatten(true);
        }

        function paramOrder(param) {
          // Currently we just make sure fileselector params come before
          // other params. Should be enough.
          return param.renderMode === 'fileselector' ? 0 : 1;
        }

        function setPreviousDropDownValues(param) {
          var value, jobId, fileName;
          if (param.value.length === 0) return;

          value = param.value[0];

          if (value['type'] === 'jobfile') {
            jobId = value.jobId;
            fileName = value.filename;

            consumableFile = null;
            for (var i = 0; i < param.consumableFiles.length; i++) {
              if (param.consumableFiles[i].hasOwnProperty('job') &&
                       param.consumableFiles[i].job.jobId === jobId &&
                       param.consumableFiles[i].filename === fileName) {
                consumableFile = param.consumableFiles[i];
                break;
              }
            }

            if (consumableFile !== null) {
              param.inputEl.selectedIndex = i;
              param.userValidate();
            }
          }
        }

        function unselectFileIfInvalid(param, fileObj) {
          var lsURL = appURL + 'ws/fs/ls?uri=' + encodeURIComponent(fileObj.toString());

          function onSuccess(transId, response) {
            var json = null;
            var fileIdx;
            try {
              json = Y.JSON.parse(response.responseText);
            } catch (e) {}

            if (json == null || Y.JSON.stringify(json) === '{}') {
              fileIdx = param.fileSelector.indexOfFile(fileObj);
              if (fileIdx >= 0) {
                param.fileSelector.deleteFileAtIndex(fileIdx);
              }
            }
          }

          var cfg = {
            on: {
              success: onSuccess
            }
          };
          Y.io(lsURL, cfg);
        }

        function setPreviousFileSelectorValues(param) {
          _(param.value).filter("filename").forEach(function(value) {
            var fileObj = new YabiSimpleFileValue(value.pathComponents, value.filename);
            param.fileSelector.selectFile(fileObj);
            unselectFileIfInvalid(param, fileObj);
          });
        }

        function setPreviousValues(param) {
          if (param.renderMode === 'fileselector') {
            setPreviousFileSelectorValues(param);
          }
          if (param.renderMode === 'select') {
            setPreviousDropDownValues(param);
          }
        }

        collectAllInputFileParams(_(jobs))
          .sortBy(paramOrder)
          .forEach(setPreviousValues);
      };


      /**
       * saveTags
       *
       * save tags
       */
      YabiWorkflow.prototype.saveTags = function(postRelocate) {
        this.tagInputEl.blur();

        if (Y.Lang.isUndefined(this.workflowId)) {
          this.tagsFinishedSaving();
          return;
        }

        var baseURL = appURL + 'ws/workflows/' + this.workflowId + '/tags';

        //load json
        var jsUrl, jsCallback, jsTransaction;
        jsUrl = baseURL;
        jsCallback = {
          success: this.saveTagsResponseCallback,
          failure: function(transId, o) {
            YAHOO.ccgyabi.widget.YabiMessage.fail(
                'Error saving tags'); }
        };
        var cfg = {
          method: 'POST',
          data: 'taglist=' + encodeURIComponent(this.tagInputEl.value),
          on: jsCallback,
          'arguments': {
            target: this,
            callback: postRelocate
          }
        };
        Y.io(jsUrl, cfg);
      };


      /**
       * solidify
       *
       * handle json response, populating object and rendering as required
       */
      YabiWorkflow.prototype.solidify = function(obj) {
        var oldJobsData = this.payload.jobs;
        this.payload = obj;
        var updateMode = false;

        var jobEl, jobData, index, oldJobStatus;

        this.updateName(obj.name);

        if (this.jobs.length > 0) {
          updateMode = true;
        }

        this.refreshTagList();

        for (index in obj.jobs) {
          jobData = obj.jobs[index];
          if (updateMode) {
            jobEl = this.jobs[index];
          } else {
            jobEl = this.addJob(jobData.toolName,
                                jobData.toolId,
                                jobData.parameterList.parameter,
                                false);
          }
          if (!this.editable) {
            oldJobStatus = '';
            if (oldJobsData && oldJobsData[index]) {
                oldJobStatus = oldJobsData[index].status || '';
            }

            jobEl.renderProgress(jobData.status, jobData.is_retrying,
                jobData.tasksComplete, jobData.tasksTotal);

            if (this.selectedJob == jobEl &&
                    oldJobStatus != jobData.status &&
                    jobData.status === 'complete') {
              this.fileOutputsSelector.updateBrowser(new YabiSimpleFileValue(
                  [jobData.stageout], ''));
            }
          }
        }
      };


      /**
       * fetchProgress
       *
       * one-time fetch current workflow status
       */
      YabiWorkflow.prototype.fetchProgress = function(callback) {
        if (!didWorkflowFinish(this.status, this.jobs)) {
          this.hydrate(this.workflowId);
        }

        if (callback !== null) {
          callback(this.status);
        }
      };


      /**
       * setTags
       *
       * update tags array and input field simultaneously
       */
      YabiWorkflow.prototype.setTags = function(tagArray) {
        if (this.tagInputEl.style.display != 'inline') {
          this.tags = tagArray;
          this.tagInputEl.value = tagArray;
          this.refreshTagList();
        } //dont set the tags if they are being edited
      };


      /**
       * cancelTagEditing
       *
       * reset tag input to the same as the tags array, hide editing fields
       */
      YabiWorkflow.prototype.cancelTagEditing = function() {
        this.tagInputEl.value = this.tags;
        this.tagHintDiv.className = 'displayNone';
        this.tagInputEl.style.display = 'none';
        this.tagListEl.style.display = 'inline';
        this.tagAddLink.style.display = 'block';
        var anim = new Y.Anim({
          node: Y.one(this.tagHelpEl),
          to: { opacity: 0 },
          easing: 'easeOut',
          duration: 0.5
        });
        anim.on('end', function() {
          this.tagHelpEl.style.display = 'none';
        }, this);
        anim.run();
      };


      /**
       * tagsFinishedSaving
       *
       * hide editing fields, solidify tags editing field into an array
       */
      YabiWorkflow.prototype.tagsFinishedSaving = function(postRelocate) {
        this.tags = this.tagInputEl.value.split(',');
        this.refreshTagList();

        //notify attached proxies
        for (var index in this.attachedProxies) {
          this.attachedProxies[index].setTags(this.tags);
        }

        this.tagHintDiv.className = 'displayNone';
        this.tagInputEl.style.display = 'none';
        this.tagListEl.style.display = 'inline';
        this.tagAddLink.style.display = 'block';
        var anim = new Y.Anim({
          node: Y.one(this.tagHelpEl),
          to: { opacity: 0 },
          easing: 'easeOut',
          duration: 0.5
        });
        anim.on('end', function() {
          this.tagHelpEl.style.display = 'none';
        }, this);
        anim.run();

        //if postRelocate != undefined then redirect user to the jobs tab
        if (!Y.Lang.isUndefined(postRelocate)) {
          postRelocate(this.workflowId);
        }
        this.saveDraft();
      };

      YabiWorkflow.prototype.refreshTagList = function() {
        while (this.tagListEl.firstChild) {
          this.tagListEl.removeChild(this.tagListEl.firstChild);
        }
        this.tagListEl.appendChild(document.createTextNode('' + this.tags));
        this.tagInputEl.value = this.tags;
      };

      /**
       * destroy
       *
       * delete any internal variables and dom handlers
       */
      YabiWorkflow.prototype.destroy = function() {
        if (!Y.Lang.isUndefined(this.jsTransaction) &&
            this.jsTransaction.isInProgress()) {
          this.jsTransaction.abort();
        }

        var job;

        for (var index in this.jobs) {
          job = this.jobs[index];

          job.destroy();

          job.container.remove();
          job.optionsNode.remove();
          job.statusNode.remove();

          job.container.detachAll();
        }

        //purge all listeners on nameEl
        Y.one(this.nameEl).detachAll();

        //remove the workflow from its container
        this.mainEl.parentNode.removeChild(this.mainEl);

        if (!Y.Lang.isUndefined(this.fileOutputsEl)) {
          this.fileOutputsEl.parentNode.removeChild(this.fileOutputsEl);
        }

        if (!Y.Lang.isUndefined(this.hydrateDiv)) {
          try {
            document.body.removeChild(this.hydrateDiv);
            this.hydrateDiv = null;
          } catch (e) {}
        }
      };

      //---- CALLBACKS ----
      YabiWorkflow.prototype.hydrateCallback = function(transId, o, args) {
        var json = o.responseText;
        var i;
        var obj;

        args.target.fadeHydratingDiv();

        target = args.target;

        obj = Y.JSON.parse(json);

        //preprocess wrapper meta data
        target.setTags(obj.tags);

        target.setStatus(obj);

        target.solidify(obj.json);
      };

      YabiWorkflow.prototype.startDragJobCallback = function(e) {
        var dragNode = e.target.get('dragNode');
        var node = e.target.get('node');

        node.setStyle('visibility', 'hidden');
        dragNode.set('innerHTML', node.get('innerHTML'));
        dragNode.setStyles({
          border: 'none',
          textAlign: 'left'
        });

        this.dragType = 'job';
        this.lastY = dragNode.getY();
      };

      YabiWorkflow.prototype.endDragJobCallback = function(e) {
        var anim;
        var drag = e.target.get('node');

        if (this.dragType == 'job') {
          drag.setStyle('visibility', '');
        } else {
          this.optionsNode.show();
          this.jobNodes.show()
            .each(function(node) {
              (new Y.Anim({
                node: node,
                to: { opacity: 1.0 },
                duration: 0.3
              })).run();
            });
        }

        // replace jobs array with newly re-ordered items based on
        // current div locations
        var updateJob = (function() {
          var jobNodes = workflow.container.get("childNodes");
          return function(job) {
            job.jobId = jobNodes.indexOf(job.container) + 1;
            job.updateTitle();
          };
        })();
        workflow.jobs = _(workflow.jobs).forEach(updateJob).sortBy("jobId").value();

        //re-propagate files
        workflow.propagateFiles();

        workflow.saveDraft();
      };

      YabiWorkflow.prototype.onDragJobCallback = function(e) {
        // Keep track of the direction of the drag for use during onDragOver
        var y = e.target.get('dragNode').getY();

        if (y < this.lastY) {
          this.goingUp = true;
        } else if (y > this.lastY) {
          this.goingUp = false;
        }
        this.lastY = y;
      };


      YabiWorkflow.prototype.onDragOverJobCallback = function(e) {
        e.halt(true);
        var drag = e.drag.get('node'),
            drop = e.drop.get('node');

        if (this.dragType !== 'job') {
          drag = this.jobNodes;
        }

        if (drop.hasClass('jobSuperContainer')) {
          //Are we not going up?
          if (!this.goingUp) {
            drop = drop.get('nextSibling');
          }
          //Add the nodes to this list
          try {
            e.drop.get('node').get('parentNode').insertBefore(drag, drop);
          } catch (e) {
            // ignore dom heirachy exceptions
          }

          //Resize this nodes shim, so we can drop on it later.
          e.drop.sizeShim();
        }
      };

      YabiWorkflow.prototype.nameChangeCallback = function(e, obj) {
        obj.name = obj.nameEl.value;
      };

      YabiWorkflow.prototype.nameBlurCallback = function(e, obj) {
        if (obj.nameEl.value === '') {
          obj.nameEl.value = obj.prefillName;
        }
        obj.name = obj.nameEl.value;
      };

      YabiWorkflow.prototype.nameFocusCallback = function(e, obj) {
        if (obj.nameEl.value == obj.prefillName) {
          obj.nameEl.value = '';
        }

        return true;
      };

      YabiWorkflow.prototype.addTagCallback = function(e, obj) {
        obj.tagAddLink.style.display = 'none';
        obj.tagListEl.style.display = 'none';
        obj.tagInputEl.style.display = 'inline';
        obj.tagHintDiv.className = 'tagHint';
        obj.tagHelpEl.style.display = 'block';
        var anim = new Y.Anim({
          node: Y.one(obj.tagHelpEl),
          to: { opacity: 1 },
          easing: 'easeOut',
          duration: 0.5
        });
        anim.run();
        obj.tagInputEl.focus();
      };

      YabiWorkflow.prototype.cancelTagsCallback = function(e, obj) {
        obj.cancelTagEditing();
      };

      YabiWorkflow.prototype.saveTagsCallback = function(e, obj) {
        obj.saveTags();
      };

      YabiWorkflow.prototype.reuseCallback = function(e, obj) {
        obj.reuse();
      };

      YabiWorkflow.prototype.deleteCallback = function(e, self) {
        var node = this;
        e.halt(true);

        var container = node.get("parentNode");

        var btn = Y.Node.create('<span class="fakeButton"/>').set("text", "Delete Workflow");
        var cancel = Y.Node.create('<span class="fakeButton"/>').set("text", "Cancel");
        var dlg = Y.Node.create('<div class="workflowSaveAsDlg" />')
          .append(Y.Node.create('<label>Are you sure? </label'))
          .append(btn).append(cancel);

        var reset = function() {
          container.show();
          dlg.remove();
        };

        btn.on('click', function() {
          self.deleteWorkflow();
          reset();
        });
        cancel.on('click', function() {
          reset();
        });

        container.hide().get("parentNode").insert(dlg, container);
      };

      YabiWorkflow.prototype.abortCallback = function(e, self) {
        var node = this;
        e.halt(true);

        var container = node.get("parentNode");

        var btn = Y.Node.create('<span class="fakeButton"/>').set("text", "Abort Workflow");
        var cancel = Y.Node.create('<span class="fakeButton"/>').set("text", "Cancel");
        var dlg = Y.Node.create('<div class="workflowSaveAsDlg" />')
          .append(Y.Node.create('<label>Are you sure? </label'))
          .append(btn).append(cancel);

        var reset = function() {
          container.show();
          dlg.remove();
        };

        btn.on('click', function() {
          self.abortWorkflow();
          reset();
        });
        cancel.on('click', function() {
          reset();
        });

        container.hide().get("parentNode").insert(dlg, container);
      };

      YabiWorkflow.prototype.saveAsCallback = function(e, self) {
        var node = this;
        e.halt(true);

        var container = node.get("parentNode");

        var btn = Y.Node.create('<span class="fakeButton"/>').set("text", "save");
        var cancel = Y.Node.create('<span class="fakeButton"/>').set("text", "cancel");
        var name = Y.Node.create('<input type="text" />').set("value", self.name);
        var dlg = Y.Node.create('<div class="workflowSaveAsDlg" />')
          .append(Y.Node.create('<label>Save as: </label').append(name))
          .append(btn).append(cancel);

        var reset = function() {
          container.show();
          dlg.remove();
        };

        btn.on('click', function() {
          if (name.get("value").length > 0) {
            self.saveAs(name.get("value"));
          }
          reset();
        });
        cancel.on('click', function() {
          reset();
        });

        container.hide().get("parentNode").insert(dlg, container);
        name.select();
        name.focus();
      };

      YabiWorkflow.prototype.saveTagsResponseCallback = function(
          transId, o, args) {
        YAHOO.ccgyabi.widget.YabiMessage.success('tags saved');
        var obj;

        try {
          obj = args.target;
          obj.tagsFinishedSaving(args.callback);
        } catch (e) {
          //do nothing
        }
      };

      YabiWorkflow.prototype.submitSuccessCallback = function(
          o, postRelocateCallback, target) {
        var json = o.responseText;
        var i;
        var obj;
        var msg = 'Workflow submission error';

        try {
          obj = Y.JSON.parse(json);
          resp_status = obj.status;
        } catch (e) {
          YAHOO.ccgyabi.widget.YabiMessage.fail(
            'Submission error. Invalid response');

          return;
        }
        if (obj.status !== 'success') {
          if (Y.Lang.isString(obj.message) && Y.Lang.trim(obj.message) != '') {
            msg = obj.message;
          }

          YAHOO.ccgyabi.widget.YabiMessage.fail(msg);
          return;
        }

        target.workflowId = obj.data.workflow_id;
        target.saveTags(postRelocateCallback);
     };

    }); // end of YUI().use(...
