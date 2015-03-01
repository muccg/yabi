YabiGlobalEventHandler = {
  failure: function(transId, response) {
    if (response.status == 401) {
      document.location.href = appURL + 'login?error=' +
          'Could+not+connect+to+yabiadmin+server:+401+Unauthorised+returned';
    }
  }
};
Y.use('*', function(Y) {
  Y.on('io:failure', YabiGlobalEventHandler.failure, Y);
});

// Utility function namespaces.
Yabi = {
  util: {}
};


/**
 * Returns the offset from the top-left of the viewport for the given element.
 *
 * @return {Object} An object with "left" and "top" elements, each a number
           representing the offset from the viewport origin in pixels.
 * @type {Object}
 */
Yabi.util.getElementOffset = function(el) {
  var left = el.offsetLeft;
  var top = el.offsetTop;

  for (var parent = el.offsetParent; parent; parent = parent.offsetParent) {
    left += parent.offsetLeft;
    top += parent.offsetTop;
  }

  return {
    left: left,
    top: top
  };
};


/**
 * Returns the height of the viewport in a cross browser way.
 *
 * @return {Number} The viewport height in pixels.
 */
Yabi.util.getViewportHeight = function() {
  var height;

  if (typeof window.innerHeight != 'undefined') {
    height = window.innerHeight;
  }
  else if (typeof document.documentElement != 'undefined') {
    height = document.documentElement.clientHeight;
  }

  return height;
};

Yabi.util.doesGlobMatch = function(name, glob) {
  var matcher = globToRegexp(glob, {extended: true});
  return matcher.test(name);
};

Yabi.util.Status = {};
Yabi.util.Status.getStatusImage = function(status) {
  if (status === 'complete') return 'ok.png';
  if (status === 'error') return 'error.png';
  if (status === 'aborted') return 'aborted.png';
  if (status === 'retrying') return 'blocked.png';
  return 'pending.png';
};

Yabi.util.Status.getStatusDescription = function(status) {
  if (status === 'complete') return 'completed';
  if (status === 'error') return 'errored';
  if (status === 'retrying') return 'errored, Yabi is retrying to run it';
  return status;
};

/* Creates a real fake button Y.Node */
Yabi.util.fakeButton = function(text, cls) {
  clses = 'fakeButton';
  if (typeof(cls) !== 'undefined') {
    clses += ' ' + cls;
  }
  return Y.Node.create('<button type="button" class="' + clses + '" />')
    .set("text", text);
};

Yabi.util.humaniseBytes = function(bytes) {
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
