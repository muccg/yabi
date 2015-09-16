/*
 * Yabi - a sophisticated online research environment for Grid, High Performance
 * and Cloud computing.
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
      accepted.append(span).append(document.createTextNode(" "));
    });

    return node;
  };

  var descNode = Y.Node.create('<div class="toolDescription"/>').hide();

  this.setupDescNode(descNode);

  if (tooldef.inputExtensions) {
    descNode.append(filetypesNode("accepts", tooldef.inputExtensions));
  }
  if (tooldef.outputExtensions) {
    descNode.append(filetypesNode("outputs", tooldef.outputExtensions));
  }

  var addLink = Y.Node.create('<div class="addLink"/>');
  addLink.on('click', function() { collection.addToolToWorkflow(this); }, this);

  this.setupFootNode().appendTo(descNode);

  Y.Node.create('<div class="tool"/>')
    .set("text", this.payload.displayName || this.payload.defDisplayName)
    .append(Y.Node.create('<span class="backend"/>')
            .set("text", this.payload.backend)
            .toggleView(this.payload.manyBackends && !this.payload.displayName))
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

YabiTool.prototype.getTitle = function() {
  return this.payload.displayName;
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
    descNode.setHTML(this.payload.description);
  }
};

YabiTool.prototype.setupFootNode = function() {
  var node = Y.Node.create('<div class="toolFooter"/>');

  if (this.isSavedWorkflow()) {
    var creator = this.payload.creator;
    var created = this.payload.created_on;
    var del = Yabi.util.fakeButton("delete").addClass("delButton").appendTo(node);
    var yes = Yabi.util.fakeButton("Yes"), no = Yabi.util.fakeButton("No");
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

    var self = this;
    var removeFromCollection = function() {
      self.node.hide();
      _.pull(self.collection.tools, self);
    };

    del.on("click", ask);
    no.on("click", ask);
    yes.on("click", function(e) {
      ask(e);

      Yabi.util.setCSRFHeader(Y.io);
      Y.io(appURL + "ws/workflows/delete_saved/", {
        method: 'POST',
        on: {
          success: function(transId, obj, args) {
            removeFromCollection();
            YAHOO.ccgyabi.widget.YabiMessage.success("Deleted");
          },
          failure: function(transId, obj) {
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

  var cacheKey = function(id) {
    return id;
  };

  var toolUrl = function(id) {
    return appURL + 'ws/tool/' + id;
  };

  return {
    get: function(id, success, failure) {
      var key = cacheKey(id);
      if (_.has(tools, key)) {
        window.setTimeout(function() { success(tools[key]); }, 0);
      } else {
        Y.io(toolUrl(id), {
          on: {
            success: function(transId, o) {
              tools[key] = o;
              success(o);
            },
            failure: function(transId, o) {
              failure(o);
            }
          }
        });
      }
    }
  };
})();
