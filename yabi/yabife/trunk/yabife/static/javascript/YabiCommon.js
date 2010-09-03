YabiGlobalEventHandler = {
    failure: function(eventType, args) {
        if (args[0].status == 401) { 
            document.location.href = appURL + 'login';
        }
    }
};
YAHOO.util.Connect.failureEvent.subscribe(YabiGlobalEventHandler.failure, YabiGlobalEventHandler);

