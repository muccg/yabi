

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

  var descNode = Y.Node.create('<div class="toolDescription"/>')
    .set("text", this.payload.description)
    .append(filetypesNode("accepts", tooldef.inputExtensions))
    .append(filetypesNode("outputs", tooldef.outputExtensions))
    .hide();

  var addLink = Y.Node.create('<div class="addLink"/>');
  addLink.on('click', collection.addCallback, null, this.payload.name);

  Y.Node.create('<div class="tool"/>')
    .set("text", this.payload.displayName)
    .append(addLink)
    .append(descNode)
    .appendTo(this.node)
    .on('click', function() { descNode.toggleView(); });
}

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
        success(tools[name]);
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
