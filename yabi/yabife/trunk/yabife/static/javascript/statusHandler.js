// $id: statusHandler.js 763 2007-06-26 06:46:58Z andrew $

/**
 * StatusHandler
 *
 * Uses a YUI singleton pattern to keep all the variables etc within name space and
 * provide a single object. The parentheses at the end make the object execute immediately
 * returning the object to the namespace. Functions above the return are private and are 
 * retained as they are referenced from the public functions, so they are a closure
 */
YAHOO.ccgyabi.StatusHandler = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    /**
     * responseSuccess
     *
     * Called to update status div
     * private
     */
    var responseSuccess = function(o){ 
        var statusHTML = o.responseText;
        document.getElementById('status').innerHTML = statusHTML;
    };


    /**
     * responseFailure
     *
     * Leave status div alone if we can't get a new status
     * private
     */
    var responseFailure = function(o){};


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {

        /**
         * updateStatus
         *
         * Fetches status from server and updates appropriate div
         */
    updateStatus:
        function(url) {

            var stCallback = { success: responseSuccess, failure: responseFailure };
            var transaction = YAHOO.util.Connect.asyncRequest('GET', url, stCallback, null); 
    
            // reload workflow panel every 30 seconds
            // relies on statusHandler being set in _status.php
            setTimeout("YAHOO.ccgyabi.StatusHandler.updateStatus('" + url + "');",30000);
        }
    };
}();


