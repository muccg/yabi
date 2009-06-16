// $Id: workflow.js 2602 2008-05-14 07:39:48Z ntakayama $

/**
 * Workflow
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.Workflow = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    var workflowSaveUrl = null;


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {

        /**
         * validateJobName
         */
        validateJobName:
        function () {

            var jobName = document.getElementById('jobNameField');
            if (jobName) {
                if (jobName.value.replace(/\s/,'') === '') {
                    jobName.value = document.getElementById('defaultJobName').innerHTML;
                }
            }
        },


        /**
         * focusJobName
         */
        focusJobName:
        function () {

            var jobName = document.getElementById('jobNameField');
            if (jobName) {
                if (jobName.value == document.getElementById('defaultJobName').innerHTML) {
                    jobName.select();
                }
            }
        },


        /**
         * filterInputText
         */
        filterInputText:
        function (event) {

            //ie keycodes
            if (event.which === null){
                if (event.keyCode == 32) { return true; }// space
                if (event.keyCode == 40) { return true; } // (
                if (event.keyCode == 41) { return true; } // )
                if (event.keyCode == 45) { return true; } // -
                if (event.keyCode == 91) { return true; } // [
                if (event.keyCode == 93) { return true; } // ]
                if (event.keyCode == 95) { return true; } // _

                //UPPERCASE Charaters
                if (event.keyCode >= 65  && event.keyCode <= 90) { return true; } // A to Z

                //lowercase Charaters
                if (event.keyCode >= 97  && event.keyCode <= 122) { return true; } // a to z

                // numbers
                if (event.keyCode  >= 48  && event.keyCode <= 57) { return true; }  
            }
    

            //firefox
            if (event &&  event.which == 32) { return true; } // space
            if (event &&  event.which == 40) { return true; } // (
            if (event &&  event.which == 41) { return true; } // )
            if (event &&  event.which == 45) { return true; } // -
            if (event &&  event.which == 91) { return true; } // [
            if (event &&  event.which == 93) { return true; } // ] 
            if (event &&  event.which == 95) { return true; }
    
            //UPPERCASE Charaters
            if (event &&  event.which >= 65  && event.which <= 90) { return true; } // A to Z

            //lowercase Charaters
            if (event &&  event.which >= 97  && event.which <= 122) { return true; } // a to z

            // numbers
            if (event &&  event.which >= 48  && event.which <= 57) { return true; } // 0 to 9
            if (event.keyCode == 9) { return true; }     //tab 
            if (event.keyCode == 16) { return true; }     //shift
            if (event.keyCode == 20) { return true; }     //caps lock
            if (event.keyCode == 35) { return true; }     //end
            if (event.keyCode == 36) { return true; }     //home
            if (event.keyCode == 37) { return true; }     //left arrow
            if (event.keyCode == 39) { return true; }     //right arrow
            if (event.keyCode == 38) { return true; }     //up arrow
            if (event.keyCode == 40) { return true; }     //down arrow
            if (event.keyCode == 45) { return true; }     //insert
            if (event.keyCode == 46) { return true; }     //delete
            if (event &&  event.which == 13) { return true; }     //enter        
            if (event &&  event.which == 8) { return true; }     //backspace        
            if (event &&  event.which == 127) { return true; }     //delete        
            return false;
        },


        /**
         * saveWorkflow
         */
        saveWorkflow:
        function () {
            //ajax request the Options section of the page
        
            var formObject = YAHOO.util.Dom.get('designForm');
            YAHOO.util.Connect.setForm(formObject, false);

            var callback = {
                success: saveWorkflowResponse,
                failure: saveWorkflowResponse,
                argument: [] };

            var transaction = YAHOO.util.Connect.asyncRequest('GET', workflowSaveUrl, callback);

            //if necessary create overlay
            var overlay, saving;
            if (! YAHOO.util.Dom.get('yabi-overlay') ) {
                overlay = document.createElement('div');
                overlay.id='yabi-overlay';
                document.getElementsByTagName('body')[0].appendChild(overlay);    
                saving = document.createElement('div');
                saving.innerHTML = 'Saving...';
                saving.id = 'yabi-saving';
                document.getElementsByTagName('body')[0].appendChild(saving);
            }
	
            //show overlay and 'saving' text
            YAHOO.util.Dom.get('yabi-overlay').style.display = 'block';
            YAHOO.util.Dom.get('yabi-saving').style.display = 'block';
            overlay.style.width = (YAHOO.util.Dom.getViewportWidth() - 2) +'px';
            overlay.style.height = (YAHOO.util.Dom.getViewportHeight() - 80) +'px';
        },


        /**
         * saveWorkflowResponse
         */
        saveWorkflowResponse:
        function (o) {
            //change saving text to saved
            var saving = YAHOO.util.Dom.get('yabi-saving');
            saving.innerHTML = 'Design saved';
            saving.style.borderColor = '#529847';
            saving.style.color = '#529847';
    
            //animate fade out - this may be broken, saving not enabled to test at the moment - ABM
            YAHOO.util.Anim('yabi-overlay', { opacity: { to: 0 } }, 1, YAHOO.util.Easing.easeOut).animate();
            var myAnim = new YAHOO.util.Anim('yabi-saving', { opacity: { to: 0 } }, 1, YAHOO.util.Easing.easeOut);
            myAnim.onComplete.subscribe(hideOverlaySaving);
            myAnim.animate();
        },


        /**
         * hideOverlaySaving
         */
        hideOverlaySaving:
        function () {
            var overlay = YAHOO.util.Dom.get('yabi-overlay');
            overlay.style.display = 'none';
            var saving = YAHOO.util.Dom.get('yabi-saving');
            saving.style.display = 'none';

            document.getElementsByTagName('body')[0].removeChild(overlay);
            document.getElementsByTagName('body')[0].removeChild(saving);
        },



        /**
         * hideOverlaySaving
         */
        submitJobNameCheck:
        function () {
            //first, validate
            listSelector.update(null, false);

            if (listSelector.containsValidationErrors === true) {
                YAHOO.ccgyabi.YabiMessage.yabiMessageFail("Validation error. Please check the red highlighted work units.");
                return false;
            }
            
            var jobName = document.getElementById('jobNameField');
            var reply = null;
            if (jobName) {
                if (jobName.value == document.getElementById('defaultJobName').innerHTML) {
                    reply = prompt("Enter a new Workflow Name or use default value", jobName.value);
                    
                    if (reply !== null && reply !== ''){
	                    jobName.value = reply;
						document.getElementById('defaultJobName').innerHTML = reply;
					} else {
                        return false;
                    }
                }
            }
        },



        /**
         * setWorkflowSaveUrl
         */
        setWorkflowSaveUrl:
	    function (url){
            workflowSaveUrl = url;
	    }
        
    };
}();

























