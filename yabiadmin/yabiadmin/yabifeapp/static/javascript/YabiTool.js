

/**
 * YabiTool
 * render a single yabi tool
 */
function YabiTool(tooldef, collection, groupNode) {
  this.payload = tooldef;
  this.collection = collection;
  this.groupNode = groupNode;

  this.node = Y.Node.create("<div/>").setStyle("position", "relative");

  var filetypesNode = function(title, exts) {
    var node = Y.Node.create('<div class="toolHelp"/>').set("text", title + ': ');
    var accepted = Y.Node.create('<span class="acceptedExtensionList"/>').appendTo(node);

    _.forEach(exts, function(ext) {
      var span = Y.Node.create('<span class="acceptedExtension"/>').set("text", ext);
      accepted.append(span).append(" ");
    });

    return node;
  };

  var descNode = Y.Node.create('<div class="toolDescription"/>').hide();

  this.setupDescNode(descNode);

  descNode.append(filetypesNode("accepts", tooldef.inputExtensions))
    .append(filetypesNode("outputs", tooldef.outputExtensions));

  var addLink = Y.Node.create('<div class="addLink"/>');
  addLink.on('click', function() { collection.addToolToWorkflow(this); }, this);

  this.setupFootNode().appendTo(descNode);

  Y.Node.create('<div class="tool"/>')
    .set("text", this.payload.displayName)
    .append(addLink)
    .append(descNode)
    .appendTo(this.node)
    .on('click', function() { descNode.toggleView(); });
}

YabiTool.prototype.isSavedWorkflow = function() {
  return this.payload.json ? true : false;
};

YabiTool.prototype.getWorkflowJobs = function() {
  return this.payload.json.jobs;
};

YabiTool.prototype.setupDescNode = function(descNode) {
  if (this.isSavedWorkflow()) {
    var list = Y.Node.create("<ul/>").appendTo(descNode);
    _.forEach(this.getWorkflowJobs(), function(job) {
      Y.Node.create("<li/>")
        .set("text", job.jobId + ". " + job.displayName)
        .appendTo(list);
    });
  } else {
    descNode.set("text", this.payload.description);
  }
};

YabiTool.prototype.setupFootNode = function() {
  var node = Y.Node.create('<div class="toolFooter"/>');

  var btn = function(text) {
    return Y.Node.create('<button type="button" class="fakeButton" />').set("text", text);
  };

  if (this.isSavedWorkflow()) {
    var creator = this.payload.creator;
    var created = this.payload.created_on;
    var del = btn("delete").addClass("delButton").appendTo(node);
    var yes = btn("Yes"), no = btn("No");
    var confirm = Y.Node.create('<span class="confirm">Sure?</span>')
        .append(yes).append(no).appendTo(node).hide();
    Y.Node.create("<span>creator: " + creator + "<br/>" +
                  "last modified: " + created + "</span>").appendTo(node);

    del.toggleView(creator === YAHOO.ccgyabi.username);

    var ask = function(e) {
      e.halt();
      del.toggleView();
      confirm.toggleView();
    };

    del.on("click", ask);
    no.on("click", ask);
    yes.on("click", function(e) {
      var node = this.node;
      ask(e);

      Y.io(appURL + "ws/workflows/delete_saved/", {
        method: 'POST',
        on: {
          success: function (transId, obj, args) {
            node.hide();
            YAHOO.ccgyabi.widget.YabiMessage.success("Deleted");
          },
          failure: function (transId, obj) {
            YAHOO.ccgyabi.widget.YabiMessage.fail("Failed to delete");
          }
        },
        data: { id: this.payload.savedWorkflowId }
      });

    }, this);
  }

  return node.toggleView(this.isSavedWorkflow());
};

YabiTool.prototype.toString = function() {
  return this.payload.name;
};


/**
 * matchesFilter
 *
 * returns true/false if it matches text
 */
YabiTool.prototype.matchesFilter = function(needle) {
  var index, bindex, subneedle;
  var needles = [];
  var haystack = this.payload.displayName.toLowerCase();
  needle = needle.toLowerCase();

  if (haystack.indexOf(needle) != -1) {
    return true;
  }

  if (needle.indexOf('*.') === 0) {
    needle = needle.substring(2);

    for (index in this.payload.inputExtensions) {
      if (this.payload.inputExtensions[index] == needle) {
        return true;
      }
    }

    for (index in this.payload.outputExtensions) {
      if (this.payload.outputExtensions[index] == needle) {
        return true;
      }
    }
  }

  if (needle.indexOf('in:') === 0) {
    needle = needle.substring(3);

    needles = needle.split(',');

    for (bindex in needles) {
      subneedle = needles[bindex];

      if (subneedle === '*') {
        return true;
      }

      for (index in this.payload.inputExtensions) {
        if (this.payload.inputExtensions[index] == subneedle) {
          return true;
        }
      }
    }
  }

  return false;
};


/**
 * A singleton object that exposes a get() method that implements asynchronous
 * loading of tool information, including client side caching.
 */
var YabiToolCache = (function() {
  var tools = {};

  return {
    get: function(name, success, failure) {
      if (name in tools) {
        window.setTimeout(function() { success(tools[name]); }, 0);
      } else {
        var url = appURL + 'ws/tool/' + escape(name);
        var callbacks = {
          success: function(transId, o) {
            tools[name] = o;
            success(o);
          },
          failure: function(transId, o) {
            failure(o);
          }
        };

        Y.io(url, {on: callbacks});
      }
    }
  };
})();
