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
