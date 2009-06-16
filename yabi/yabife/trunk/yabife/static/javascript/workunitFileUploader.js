// $Id: workunitFileUploader.js 3537 2008-09-23 09:03:20Z ntakayama $

/**
 * workunitFileUploader
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.workunitFileUploader = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

	var sUrl = '';
	var id = '';
		
    /**
     * uploadFileResponse
     */
    var uploadFileResponse = function(o) {
		
        var response = o.responseText;
        var uploadedFiles;
        var splitValues = response.split(":");
        var i;
        var filesInput;

        if (splitValues[0] == "success"){
            //successfull upload
            filenameList = splitValues[1];
            
            filenames = filenameList.split(",");
		
            YAHOO.ccgyabi.workunitFileUploader.resetFileFields();
		
            YAHOO.ccgyabi.workunitFileUploader.uploadSuccessFeedback(splitValues[2]);
            
			for (i = 0;i< filenames.length; i++)
			{
			
			    document.getElementById('uploadedFiles').innerHTML =  document.getElementById('uploadedFiles').innerHTML + filenames[i]+'<br/>';
			    
	            filesInput = YAHOO.util.Dom.get(id+':input:files');
	            if (filesInput.value === "" || filesInput.value === null) {
	                filesInput.value = filenames[i];
	            } else {
	                filesInput.value = filesInput.value + "," + filenames[i];
	            }		
	            
	            listSelector.setKeyValue( o.argument[0], 'file' , filenames[i] );
	            listSelector.addOutputFiletype(o.argument[0], filenames[i]);	            
	            
			}            

            YAHOO.ccgyabi.workunitFileUploader.resetFileFields();

        } else if (splitValues[0] == "warn")  {
        	//semi successfull upload
            filenameList = splitValues[1];
            
            filenames = filenameList.split(",");
		
            YAHOO.ccgyabi.workunitFileUploader.resetFileFields();
		
            YAHOO.ccgyabi.workunitFileUploader.uploadWarningFeedback(splitValues[2]);
            
			for (i = 0;i< filenames.length; i++)
			{
			
			    document.getElementById('uploadedFiles').innerHTML =  document.getElementById('uploadedFiles').innerHTML + filenames[i]+'<br/>';
			    
	            filesInput = YAHOO.util.Dom.get(id+':input:files');
	            if (filesInput.value === "" || fileInput.value === null) {
	                filesInput.value = filenames[i];
	            } else {
	                filesInput.value = filesInput.value + "," + filenames[i];
	            }	
	            //listSelector.setKeyValue( o.argument[0], 'file' , filenames[i] );
	            //listSelector.addOutputFiletype(o.argument[0], filenames[i]);          
	            	
			}            

            YAHOO.ccgyabi.workunitFileUploader.resetFileFields();

        
        } else {
        
            //upload failed
            //TODO write an error message to the browser
            var message = splitValues[2];
            if (message == null || message == '') {
                message = "upload did not complete. File may be too large?";
            }
            
            YAHOO.ccgyabi.workunitFileUploader.uploadFailFeedback('Error: '+ message);	
        }
    };


    /**
     * detailsCallback
     */
    var detailsCallback = function(o) {        
        var detailsDiv = YAHOO.util.Dom.get('fileDetails');
        detailsDiv.innerHTML = o.responseText;
    };


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {    

		/**
		 * uploadFile
		 */
		uploadFile:
        function(url, pid) {
				
			sUrl = url;
		    id = pid;  
		
		    //ajax request the Options section of the page
			
		    var formObject = YAHOO.util.Dom.get(id+'_uploadForm');
		
		    YAHOO.util.Connect.setForm(formObject, true); //must be true for file to upload
		
		    var callback = {
		        upload: uploadFileResponse, 
		        timeout: 120000,
		        argument: [id] };
		
		    var transaction = YAHOO.util.Connect.asyncRequest('POST', sUrl, callback);
		},


		/**
		 * resetFileFields
		 */
		resetFileFields:
		function() {        
		    document.getElementById(id+'_uploadFields').innerHTML = 'Upload file:<br/><input type=\"file\" name=\"'+id+'_file1\" id=\"'+id+'_file1\" value=\"\" /><a href=\"#\" onClick=\"toggleVisibility(\''+id+':extraFiles\');\" class=\"toolFolder\">more files</a><br /><div id=\"'+id+':extraFiles\" style=\"display:none;\"><input type=\"file\" name=\"'+id+'_file2\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file3\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file4\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file5\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file6\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file7\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file8\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file9\" id=\"'+id+'_file\" value=\"\" /> <br /><br /><input type=\"file\" name=\"'+id+'_file10\" id=\"'+id+'_file\" value=\"\" /> <br /></div>';
		},	


		/**
		 * uploadFailFeedback
		 */
		uploadFailFeedback:
        function(feedback) {
		    //var feedbackDiv = YAHOO.util.Dom.get(id+'_uploadFeedback');
		    // use the new message thingo instead.
		    YAHOO.ccgyabi.YabiMessage.yabiMessageFail(feedback);

		},
	
	
		/**
		 * uploadWarningFeedback
		 */
		uploadWarningFeedback:
        function(feedback) {
		    //var feedbackDiv = YAHOO.util.Dom.get(id+'_uploadFeedback');
		    // use the new message thingo instead.
		    YAHOO.ccgyabi.YabiMessage.yabiMessageWarn(feedback);

		},	
		
		/**
		 * uploadSuccessFeedback
		 */
		uploadSuccessFeedback:
        function(feedback) {
		    //var feedbackDiv = YAHOO.util.Dom.get(id+'_uploadFeedback');
		    // use the new message thingo instead.
		    YAHOO.ccgyabi.YabiMessage.yabiMessageSuccess(feedback);

		}		
		
		
    };
}();
































