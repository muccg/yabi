ToolCollectionYUI = YUI().use('node', 'event', 'dd-drag', 'dd-proxy', 'dd-drop', 'io', 'json-parse', function(Y) {

/**
 * YabiToolCollection
 * fetch and render listing/grouping/smart filtering of tools
 */
YabiToolCollection = function() {
  var self = this;
  this.tools = [];
  this.groupEls = [];
  this.autofilter = true;

  this.containerEl = document.createElement('div');
  this.containerEl.className = 'toolCollection';

  this.filterEl = document.createElement('div');
  this.filterEl.className = 'filterPanel';

  this.searchLabelEl = document.createElement('label');
  this.searchLabelEl.appendChild(document.createTextNode('Find tool: '));
  this.filterEl.appendChild(this.searchLabelEl);

  this.searchEl = document.createElement('input');
  this.searchEl.setAttribute('type', 'search');
  this.searchEl.className = 'toolSearchField';

  //attach key events for changes/keypresses
  Y.one(self.searchEl).on('blur', self.filterCallback, null, self);
  Y.one(self.searchEl).on('keyup', self.filterCallback, null, self);
  Y.one(self.searchEl).on('change', self.filterCallback, null, self);
  Y.one(self.searchEl).on('search', self.filterCallback, null, self);


  this.filterEl.appendChild(this.searchEl);

  this.clearFilterEl = document.createElement('span');
  this.clearFilterEl.className = 'fakeButton';
  this.clearFilterEl.appendChild(document.createTextNode('show all'));
  this.clearFilterEl.style.visibility = 'hidden';
  Y.one(self.clearFilterEl).on('click', self.clearFilterCallback, null, self);

  this.filterEl.appendChild(this.clearFilterEl);

  //autofilter
  this.autofilterContainer = document.createElement('div');
  this.autofilterContainer.className = 'autofilterContainer';
  this.autofilterContainer.appendChild(document.createTextNode(
      'Use selection to auto-filter?'));

  this.autofilterEl = document.createElement('span');
  this.autofilterEl.className = 'virtualCheckboxOn';
  this.autofilterEl.appendChild(document.createTextNode('on'));

  Y.one(self.autofilterEl).on('click', self.autofilterCallback, null, self);
  this.autofilterContainer.appendChild(this.autofilterEl);

  this.filterEl.appendChild(this.autofilterContainer);

  this.containerEl.appendChild(this.filterEl);

  //no results div
  this.noResultsDiv = document.createElement('div');
  this.noResultsDiv.className = 'wfNoResultsDiv';
  this.noResultsDiv.appendChild(document.createTextNode('no matching tools'));
  this.containerEl.appendChild(this.noResultsDiv);

  this.listingEl = document.createElement('div');
  this.listingEl.className = 'toolListing';

  this.loading = new YAHOO.ccgyabi.widget.Loading(this.listingEl);
  this.loading.show();

  this.containerEl.appendChild(this.listingEl);

  this.searchEl.value = 'select';
  this.filter();

  this.hydrate();
}

YabiToolCollection.registerDDTarget = function(el) {
  new Y.DD.Drop({ 
    node: Y.one(el)
  });
};

YabiToolCollection.prototype.solidify = function(obj) {
  var tempTool;
  var toolgroup;

  this.payload = obj;

  this.loading.hide();

  for (var toolsetindex in obj.menu.toolsets) {

    for (var index in obj.menu.toolsets[toolsetindex].toolgroups) {

      toolgroup = obj.menu.toolsets[toolsetindex].toolgroups[index];

      tempGroupEl = document.createElement('div');
      tempGroupEl.className = 'toolGroup';
      tempGroupEl.appendChild(document.createTextNode(toolgroup.name));
      this.listingEl.appendChild(tempGroupEl);

      this.groupEls.push(tempGroupEl);

      for (var subindex in toolgroup.tools) {
        tempTool = new YabiTool(toolgroup.tools[subindex], this, tempGroupEl);

        this.listingEl.appendChild(tempTool.el);

        //drag drop
        var dd = new Y.DD.Drag({
            node: tempTool.el,
            data: {
                tool: tempTool
            }
            //startCentered: true,
        }).plug(Y.Plugin.DDProxy, {
            moveOnEnd: false
        });

        dd.on('drag:start', this.startDragToolCallback);
        dd.on('drag:end', workflow.endDragJobCallback);
        dd.on('drag:drag', workflow.onDragJobCallback);
        dd.on('drag:over', workflow.onDragOverJobCallback);

        this.tools.push(tempTool);

      }
    }
  }

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
    "arguments": self
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
  var filterVal = this.searchEl.value;
  var visibleCount = 0;

  if (filterVal === '') {
    this.clearFilterEl.style.visibility = 'hidden';
  } else {
    this.clearFilterEl.style.visibility = 'visible';
  }

  for (var gindex in this.groupEls) {
    this.groupEls[gindex].style.display = 'none';
  }

  for (var index in this.tools) {
    if (this.tools[index].matchesFilter(filterVal)) {
      this.tools[index].el.style.display = 'block';
      this.tools[index].groupEl.style.display = 'block';
      visibleCount++;
    } else {
      this.tools[index].el.style.display = 'none';
    }
  }

  if (visibleCount === 0) {
    if (this.tools.length !== 0) {
      this.noResultsDiv.style.display = 'block';
    }
  } else {
    this.noResultsDiv.style.display = 'none';
  }
};


/**
 * clearFilter
 */
YabiToolCollection.prototype.clearFilter = function() {
  this.searchEl.value = '';
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

// --------- callback methods, these require a target via their inputs --------


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
YabiToolCollection.prototype.hydrateResponse = function(transId, o, target) {
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
  var tool;

  //work out which tool it is
  tool = e.target.get('data').tool;

  if (Y.Lang.isUndefined(tool)) {
    YAHOO.ccgyabi.widget.YabiMessage.fail('Failed to find tool');
    return false;
  }

  var job = workflow.addJob(tool.toString(), undefined, false);
  job.containerEl.style.opacity = '0.1';
  job.optionsEl.style.display = 'none';

  this.jobEl = job.containerEl;
  this.optionsEl = job.optionsEl;

  var dragNode = e.target.get('dragNode');
  dragNode.set('innerHTML', e.target.get('node').get('innerHTML'));
  dragNode.setStyles({
    border: 'none',
    textAlign: 'left'
  });
  // remove the 'add' image from the dragged item
  dragNode.removeChild(dragNode.get('children').slice(-1).item(0));

  this.dragType = 'tool';
  this.lastY = dragNode.getY();
};


}); // end of YUI().use(
