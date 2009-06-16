// $Id: fileDetails.js 2816 2008-06-04 07:38:55Z andrew $

/**
 * Utility
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.FileDetails = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

	var workUnitManager;
	
    var sUrl;

    var renameUrl;
    
    var addDirUrl;
    

	/**
	 * detailsCallback
	 */    
	detailsCallback = function(o) {
	    var detailsDiv = YAHOO.util.Dom.get('fileDetails');
	    detailsDiv.innerHTML = o.responseText;
	};
	
	
	/**
	 * detailsFailedCallback
	 *
	 * If the ajax call fails its most likely due to a session timeout, so reload the page to reauthenticate
	 *
	 */    
	detailsFailedCallback = function(o) {
	    window.location.reload(true);
	};	


	/**
	 * renameCallback
	 */    
	renameCallback = function(o) {
	    //var detailsDiv = YAHOO.util.Dom.get('fileDetails');
	    //detailsDiv.innerHTML = o.responseText;
	    
	    //alert('Success');
	    window.location.reload(true);
	};
	
	
	/**
	 * renameFailedCallback
	 *
	 * If the ajax call fails its most likely due to a session timeout, so reload the page to reauthenticate
	 *
	 */    
	renameFailedCallback = function(o) {
	
	    //alert('Failed');	

	};	


	/**
	 * addDirCallback
	 */    
	addDirCallback = function(o) {
	    //var detailsDiv = YAHOO.util.Dom.get('fileDetails');
	    //detailsDiv.innerHTML = o.responseText;
	    
	    //alert('Success');
	    window.location.reload(true);
	};
	
	
	/**
	 * addDirFailedCallback
	 *
	 * If the ajax call fails its most likely due to a session timeout, so reload the page to reauthenticate
	 *
	 */    
	addDirFailedCallback = function(o) {
	
	    //alert('Failed');	

	};

    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////
    
   
    return {    


        /**
         * setUrl
         */
        setUrl:
        function(url) { 
            sUrl = url;
        },
        
        /**
         * setRenameUrl
         */
        setRenameUrl:
        function(rurl) { 
            renameUrl = rurl;
        },        
        

        /**
         * setAddDirUrl
         */
        setAddDirUrl:
        function(rurl) { 
            addDirUrl = rurl;
        }, 
        
        /**
         * renameFile
         */
        renameFile:
        function(path, currentFileName) { 
        
        	
        	var newFileName = prompt('New File Name:', currentFileName);

        	if (newFileName === null){
	        	return;
        	}

        	
        	var fUrl = renameUrl +'index?path=' + path + '&filename=' + newFileName ;
        	
        	YAHOO.ccgyabi.YabiMessage.yabiMessageWarn('Renaming File. Please Wait for the page to reload.');
        	
			var rCallback = {
		        success: renameCallback,
		        failure: renameFailedCallback,
		        argument: [] };
		    var transaction = YAHOO.util.Connect.asyncRequest('GET', fUrl, rCallback, null);
		                	

        	
        },


        /**
         * addDir
         */
        addDir:
        function(path) { 
        
        	var newFileName = prompt('New Directory Name (will be created in workspace):', '');

        	if (newFileName === null || newFileName === ''){
                // no directory name supplied, so do nothing
	        	return;
        	}

        	var fUrl = addDirUrl +'index?path=' + path + '&dirname=' + newFileName ;
        	
        	YAHOO.ccgyabi.YabiMessage.yabiMessageWarn('Creating Directory. Please Wait for the page to reload.');
        	
			var addCallback = {
		        success: addDirCallback,
		        failure: addDirFailedCallback,
		        argument: [] };
		    var transaction = YAHOO.util.Connect.asyncRequest('GET', fUrl, addCallback, null);
        },


        /**
         * fetchDetails
         */
        fetchDetails:
        function(path) {  
			
		    var detailsDiv = YAHOO.util.Dom.get('fileDetails');
		    detailsDiv.innerHTML = '<h1>Loading...</h1>';
		
		    //ajax request the details section of the page
		    var fUrl = sUrl +'index?path=' + path;
		    
		    var callback = {
		        success: detailsCallback,
		        failure: detailsFailedCallback,
		        argument: [] };
		    var transaction = YAHOO.util.Connect.asyncRequest('GET', fUrl, callback, null);
		        
		    //to be nice, set a session cookie to allow the tree to expand the last opened file again when inited
		    createCookie('yabiFileBrowseLast', path);
   
		}
    };
}();
