// $Id: fileSelector.js 4207 2009-02-25 07:57:28Z ntakayama $

/**
 * FileSelector
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.FileSelector = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

	var id = '';
	var sUrl = '';		
	var path = '';	
	var detailsDiv  ='';


    /**
     * fileSelectorDetailsCallback
     */
    var fileSelectorDetailsCallback = function (o) {
        detailsDiv.innerHTML = o.responseText;
    };


    /**
     * fileSelectorFailedCallback
     */
    var fileSelectorFailedCallback = function (o) {
        detailsDiv.innerHTML = 'Error: Could not load File Details.';
    };


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {    


        /**
         * setDetailsDiv
         */
        setDetailsDiv:
        function (id) {
            detailsDiv = YAHOO.util.Dom.get(id+'_fileSelectorDetails');
        },  		


        /**
         * setPath
         */
        setPath:
        function (inputPath) {
            path = inputPath;
	    }, 


        /**
         * setUrl
         */
	    setUrl:
        function (url) {
	        sUrl = url;
	    },


        /**
         * selectFile
         */
        selectFile:
        function(pid, filename){

        	id = pid;
	        var selectedFilesDiv = YAHOO.util.Dom.get(id+'_selectedFiles');
	        selectedFiles = selectedFilesDiv.innerHTML ;
	        
	        // New no working stuff
	        selectedFilesDiv.innerHTML = selectedFiles + filename + ' [<a style="color:#f60;" href="#" onClick="return YAHOO.ccgyabi.FileSelector.deselectFile(\''+id+'\',\''+filename+'\');" >x</a>] <br/>';
			
			//old working stuff
			//selectedFilesDiv.innerHTML =  selectedFiles +filename+'<br/>';

            var filesInput = YAHOO.util.Dom.get(id+':input:files');
            if (filesInput.value === "") {
                filesInput.value = filename;
            } else {
                filesInput.value = filesInput.value + "," + filename;
            }
            //	        listSelector.setKeyValue(id, 'file', id );
	        listSelector.setKeyValue(id, 'file', filename );
            listSelector.addOutputFiletype(id, filename); 
	    },


        /**
         * deselectFile
         */
        deselectFile:
        function(pid, filename){

        	id = pid;
	        var selectedFilesDiv = YAHOO.util.Dom.get(id+'_selectedFiles');

	        var filesInput = YAHOO.util.Dom.get(id+':input:files');
	        fileList = filesInput.value;
	        
	        fileList = fileList.replace(filename, "");
			fileList = fileList.replace(/,,/, ","); // remove double commas
			fileList = fileList.replace(/^,/, ""); // remove leading comma
			fileList = fileList.replace(/,$/, ""); // remove trailing comma
	        filesInput.value = fileList;
	        
	        fileHtml = filesInput.value;
	        fileArray = fileList.split(',');
	        
	        selectedFilesDiv.innerHTML = "";
	        
	        listSelector.removeKeyValue(id, 'file', filename );
	        listSelector.removeOutputFiletypes(id);

	        for (i=0;i< fileArray.length;i++) {
	        	
	        	if (fileArray[i].length > 0 ){

	        		linkHtml = ' [<a style="color:#f60;" href="#" onClick="YAHOO.ccgyabi.FileSelector.deselectFile(\''+id+'\',\''+fileArray[i]+'\')" >x</a>] <br/>';
          	    	selectedFilesDiv.innerHTML = selectedFilesDiv.innerHTML + fileArray[i] +linkHtml;
          	    	
          	    	//re add the stuff
			        listSelector.setKeyValue(id, 'file',fileArray[i]);
		            listSelector.addOutputFiletype(id, fileArray[i]);           	    	
          	    	
          	    }

	        }

            return false;
	    },


        /**
         * getFileDetails
         */    
        getFileDetails:
        function(id, path){    
		    var fUrl =  sUrl +'index?path='+path+'&type=selector&id='+id+'&filetype=all';
		    detailsDiv = YAHOO.util.Dom.get(id+'_fileSelectorDetails');
		    var fileSelectorCallback = {
		        success: fileSelectorDetailsCallback,
		        failure: fileSelectorFailedCallback,
		        argument: [id] };
		    var transaction = YAHOO.util.Connect.asyncRequest('GET', fUrl, fileSelectorCallback, null);
	    },


        /**
         * getDirectoryDetails
         */    
        getDirectoryDetails:
        function(id, path){    
		    var fUrl =  sUrl +'index?path='+path+'&type=selector&id='+id+'&filetype=directory';
		    detailsDiv = YAHOO.util.Dom.get(id+'_fileSelectorDetails');
		    var fileSelectorCallback = {
		        success: fileSelectorDetailsCallback,
		        failure: fileSelectorFailedCallback,
		        argument: [id] };
		    var transaction = YAHOO.util.Connect.asyncRequest('GET', fUrl, fileSelectorCallback, null);
	    }
    };
}();
