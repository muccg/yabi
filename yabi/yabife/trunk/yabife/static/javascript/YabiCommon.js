YabiGlobalEventHandler = {
    failure: function(eventType, args) {
        if (args[0].status == 401) { 
            document.location.href = appURL + 'login';
        }
    }
};
YAHOO.util.Connect.failureEvent.subscribe(YabiGlobalEventHandler.failure, YabiGlobalEventHandler);


var getElementOffset = function(element) {
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

var getViewportHeight = function() {
    var height;

    if (typeof window.innerHeight != "undefined") {
        height = window.innerHeight;
    }
    else if (typeof document.documentElement != "undefined") {
        height = document.documentElement.clientHeight;
    }

    return height;
};
