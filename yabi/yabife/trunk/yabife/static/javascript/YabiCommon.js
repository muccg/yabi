YabiGlobalEventHandler = {
    failure: function(eventType, args) {
        if (args[0].status == 401) { 
            document.location.href = appURL + 'login';
        }
    }
};
YAHOO.util.Connect.failureEvent.subscribe(YabiGlobalEventHandler.failure, YabiGlobalEventHandler);


// Utility function namespaces.
Yabi = {
    util: {}
};

/**
 * Removes all children from the given element. Normally you'd use a library
 * that does this for you, but sadly, we're not blessed with such a beast in
 * YUI 2.
 *
 * @param {DOMElement} e The element to purge children from.
 * @return {DOMElement}
 */
Yabi.util.empty = function(e) {
    while (e.childNodes.length) {
        e.removeChild(e.firstChild);
    }

    return e;
};

/**
 * Returns the offset from the top-left of the viewport for the given element.
 *
 * @return An object with "left" and "top" elements, each a number representing
 *         the offset from the viewport origin in pixels.
 * @type Object
 */
Yabi.util.getElementOffset = function(element) {
    var left = element.offsetLeft;
    var top = element.offsetTop;
    
    for (var parent = element.offsetParent; parent; parent = parent.offsetParent) {
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
 * @return The viewport height in pixels.
 * @type Number
 */
Yabi.util.getViewportHeight = function() {
    var height;

    if (typeof window.innerHeight != "undefined") {
        height = window.innerHeight;
    }
    else if (typeof document.documentElement != "undefined") {
        height = document.documentElement.clientHeight;
    }

    return height;
};

/**
 * Replaces all child elements in the given element with the new element(s).
 *
 * @param {DOMElement} e
 * @param {DOMElement} ...
 * @return {DOMElement}
 */
Yabi.util.replace = function(e) {
    Yabi.util.empty(e);

    for (var i = 1; i < arguments.length; i++) {
        e.appendChild(arguments[i]);
    }

    return e;
};

/**
 * Updates the given element to contain only the given text.
 *
 * @param {DOMElement} e
 * @param {String} text
 * @return {DOMElement}
 */
Yabi.util.text = function(e, text) {
    return Yabi.util.replace(e, document.createTextNode(text));
};
