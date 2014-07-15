ToolCollectionYUI = YUI().use(
    'node', 'event', 'dd-drag', 'dd-proxy', 'dd-drop', 'io', 'json-parse',
    function(Y) {

      /**
       * YabiToolCollection
       * fetch and render listing/grouping/smart filtering of tools
       */
      YabiToolCollection = function() {
        var self = this;
        this.tools = [];
        this.autofilter = true;

        this.containerNode = Y.Node.create('<div class="toolCollection"/>');
        var filterEl = Y.Node.create('<div class="filterPanel"/>');

        this.searchLabelEl = Y.Node.create("<label>Find tool: </label>");
        filterEl.append(this.searchLabelEl);

        this.searchNode = Y.Node.create('<input type="search" class="toolSearchField">');

        //attach key events for changes/keypresses
        this.searchNode.on('blur', this.filterCallback, null, this);
        this.searchNode.on('keyup', this.filterCallback, null, this);
        this.searchNode.on('change', this.filterCallback, null, this);
        this.searchNode.on('search', this.filterCallback, null, this);

        filterEl.append(this.searchNode);

        this.clearFilterNode = Y.Node.create('<span class="fakeButton">show all</span>');
        this.clearFilterNode.hide();
        this.clearFilterNode.on('click', this.clearFilterCallback, null, this);

        filterEl.append(this.clearFilterNode);

        //autofilter
        this.autofilterContainer = document.createElement('div');
        this.autofilterContainer.className = 'autofilterContainer';
        this.autofilterContainer.appendChild(document.createTextNode(
            'Use selection to auto-filter?'));

        this.autofilterEl = document.createElement('span');
        this.autofilterEl.className = 'virtualCheckboxOn';
        this.autofilterEl.appendChild(document.createTextNode('on'));

        Y.one(self.autofilterEl).on('click', self.autofilterCallback,
            null, self);
        this.autofilterContainer.appendChild(this.autofilterEl);

        filterEl.append(this.autofilterContainer);

        this.containerNode.append(filterEl);

        //no results div
        this.noResultsDiv = Y.Node.create('<div class="wfNoResultsDiv">no matching tools</div>');
        this.containerNode.append(this.noResultsDiv);

        this.listingNode = Y.Node.create('<div class="toolListing"/>');

        this.loading = new YAHOO.ccgyabi.widget.Loading(this.listingNode.getDOMNode());
        this.loading.show();

        this.containerNode.append(this.listingNode);

        this.searchNode.set("value", "select");
        this.filter();

        this.hydrate();
      };

      YabiToolCollection.registerDDTarget = function(node) {
        new Y.DD.Drop({ node: node });
      };

      YabiToolCollection.prototype.solidify = function(obj) {
        var self = this;

        this.payload = obj;

        this.loading.hide();

        var fixupTool = function(tooldef) {
          if (!Y.Lang.isArray(tooldef.inputExtensions)) {
            tooldef.inputExtensions = [tooldef.inputExtensions];
          }

          if (Y.Lang.isUndefined(tooldef.outputExtensions)) {
            tooldef.outputExtensions = [];
          } else if (!Y.Lang.isArray(tooldef.outputExtensions)) {
            tooldef.outputExtensions = [tooldef.outputExtensions];
          }
          return tooldef;
        };

        _.forEach(obj.menu.toolsets, function(toolset) {
          _.forEach(toolset.toolgroups, function(toolgroup) {
            var groupNode = Y.Node.create('<div class="toolGroup"/>');
            groupNode.set("text", toolgroup.name);
            self.listingNode.append(groupNode);

            _(toolgroup.tools).map(fixupTool).forEach(function(tooldef) {
              var tool = new YabiTool(tooldef, self, groupNode);

              self.listingNode.append(tool.node);

              //drag drop
              var dd = new Y.DD.Drag({
                node: tool.node,
                data: {
                  tool: tool
                }
                //startCentered: true,
              }).plug(Y.Plugin.DDProxy, {
                moveOnEnd: false
              });

              dd.on('drag:start', self.startDragToolCallback);
              dd.on('drag:end', workflow.endDragJobCallback);
              dd.on('drag:drag', workflow.onDragJobCallback);
              dd.on('drag:over', workflow.onDragOverJobCallback);

              self.tools.push(tool);
            });

          });
        });

        this.filter();
      };


      /**
       * hydrate
       *
       * performs an AJAX json fetch of all the tool details and data
       *
       */
      YabiToolCollection.prototype.hydrate = function() {
        var self = this;
        var url = appURL + 'ws/menu/';

        var cfg = {
          on: { complete: self.hydrateResponse },
          'arguments': self
        };

        Y.io(url, cfg);

      };

      YabiToolCollection.prototype.toString = function() {
        return 'tool collection';
      };


      /**
       * filter
       *
       * use the search field to limit visible tools
       */
      YabiToolCollection.prototype.filter = function() {
        var filterVal = this.searchNode.get("value");
        var visibleCount = 0;

        this.clearFilterNode.toggleView(filterVal !== '');

        Y.all(".toolGroup").hide();

        _.forEach(this.tools, function(tool) {
          if (tool.matchesFilter(filterVal)) {
            tool.node.show();
            tool.groupNode.show();
            visibleCount++;
          } else {
            tool.node.hide();
          }
        });

        this.noResultsDiv.toggleView(visibleCount === 0 && this.tools.length !== 0);
      };


      /**
       * clearFilter
       */
      YabiToolCollection.prototype.clearFilter = function() {
        this.searchNode.set("value", "");
        this.filter();
      };


      /**
       * autofilterToggle
       */
      YabiToolCollection.prototype.autofilterToggle = function() {
        this.autofilter = !this.autofilter;

        if (this.autofilter) {
          this.autofilterEl.className = 'virtualCheckboxOn';
          this.autofilterEl.innerHTML = 'on';
        } else {
          this.autofilterEl.className = 'virtualCheckbox';
          this.autofilterEl.innerHTML = 'off';
        }
      };

      // ----- callback methods, these require a target via their inputs -----


      /**
       * filterCallback
       *
       */
      YabiToolCollection.prototype.filterCallback = function(e, target) {
        target.filter();
      };


      /**
       * clearFilterCallback
       *
       */
      YabiToolCollection.prototype.clearFilterCallback = function(e, target) {
        target.clearFilter();
      };


      /**
       * autofilterCallback
       *
       * toggle autofiltering
       */
      YabiToolCollection.prototype.autofilterCallback = function(e, target) {
        target.autofilterToggle();
      };


      /**
       * addCallback
       *
       * local callback for adding a tool
       */
      YabiToolCollection.prototype.addCallback = function(e, obj) {
        workflow.addJob(obj);
      };


      /**
       * hydrateResponse
       *
       * handle the response
       * parse json, store internally
       */
      YabiToolCollection.prototype.hydrateResponse = function(
          transId, o, target) {
        var i, json;

        try {
          json = o.responseText;

          target.solidify(Y.JSON.parse(json));
        } catch (e) {
          YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
          target.solidify({'menu': {'toolsets': []}});
        }
      };

      YabiToolCollection.prototype.startDragToolCallback = function(e) {
        // work out which tool it is
        var tool = e.target.get('data').tool;

        if (Y.Lang.isUndefined(tool)) {
          YAHOO.ccgyabi.widget.YabiMessage.fail('Failed to find tool');
          return false;
        }

        var job = workflow.addJob(tool.toString(), undefined, false);
        job.container.setStyle("opacity", '0.1');
        job.optionsNode.hide();

        this.jobNode = job.container;
        this.optionsNode = job.optionsNode;

        var dragNode = e.target.get('dragNode');
        dragNode.set('innerHTML', e.target.get('node').get('innerHTML'));
        dragNode.setStyles({
          border: 'none',
          textAlign: 'left'
        });
        // remove the 'add' image from the dragged item
        dragNode.one(".addLink").remove();

        this.dragType = 'tool';
        this.lastY = dragNode.getY();
      };


    }); // end of YUI().use(
