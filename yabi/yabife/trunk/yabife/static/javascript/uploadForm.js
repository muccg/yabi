// $Id: uploadForm.js 3537 2008-09-23 09:03:20Z ntakayama $

/**
 * UploadForm
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.UploadForm = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    /**
     * uploadDataFileResponse
     *
     */
    var uploadDataFileResponse = function(o){ 
		    YAHOO.ccgyabi.UploadForm.hideUploadForm();
		    YAHOO.ccgyabi.UploadForm.reloadPage();        
    };
		

    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {    

        /**
         * showUploadForm
         */
    showUploadForm:
        function() {
            document.getElementById('uploadFormDiv').style.visibility = 'visible';
            document.getElementById('uploadFormDiv').style.display = 'block';
		},
	

        /**
         * hideUploadForm
         */
    hideUploadForm:
        function() {	
            document.getElementById('uploadFormDiv').style.visibility = 'hidden';
            document.getElementById('uploadFormDiv').style.display = 'none';
		},


        /**
         * reloadPage
         */	
    reloadPage:
        function() {
            window.location.reload();
		},


        /**
         * updateStatus
         *
         * Fetches status from server and updates appropriate div
         */
    uploadTheDataFile:
        function(fileUploadUrl) {	

		    var formObject = YAHOO.util.Dom.get('uploadForm');
		
		    YAHOO.util.Connect.setForm(formObject, true); //must be true for file to upload
		
		    var callback = {
		        upload: uploadDataFileResponse, 
		        timeout: 120000,
		        argument: [] };
		
		    var transaction = YAHOO.util.Connect.asyncRequest('POST', fileUploadUrl, callback);
	    }

    };
}();
