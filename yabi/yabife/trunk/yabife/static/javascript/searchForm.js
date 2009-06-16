// $Id: searchForm.js 995 2007-07-23 04:15:33Z andrew $

/**
 * SearchForm
 *
 * Uses a YUI singleton pattern to keep all the variables etc within name space and
 * provide a single object. The parentheses at the end make the object execute immediately
 * returning the object to the namespace. Functions above the return are private and are 
 * retained as they are referenced from the public functions, so they are a closure
 */
YAHOO.ccgyabi.SearchForm = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    /**
     * uploadDataFileResponse
     *
     */
    var uploadDataFileResponse = function(o){ 
		    YAHOO.ccgyabi.SearchForm.hideSearchForm();
		    YAHOO.ccgyabi.SearchForm.reloadPage();        
    };
		


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {    


	    showSearchForm: function() {
		        document.getElementById('searchFormDiv').style.visibility = 'visible';
		        document.getElementById('searchFormDiv').style.display = 'block';
		},
	
	    hideSearchForm: function() {	
		        document.getElementById('searchFormDiv').style.visibility = 'hidden';
		        document.getElementById('searchFormDiv').style.display = 'none';
		},
	
	    reloadPage: function() {	
		        window.location.reload();
		},
	
        /**
         * updateStatus
         *
         * Fetches status from server and updates appropriate div
         */
        uploadTheDataFile: function(fileUploadUrl) {	

		    var formObject = YAHOO.util.Dom.get('searchForm');
		
		    YAHOO.util.Connect.setForm(formObject, true); //must be true for file to upload
		
		    var callback = {
		        upload: uploadDataFileResponse, 
		        timeout: 10000,
		        argument: [] };
		
		    var transaction = YAHOO.util.Connect.asyncRequest('POST', fileUploadUrl, callback);
	    }
	    
    };
}();
