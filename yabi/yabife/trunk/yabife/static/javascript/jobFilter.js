// $Id: jobFilter.js 4169 2009-02-20 04:09:13Z ntakayama $

/**
 * JobFilter
 */
YAHOO.ccgyabi.JobFilter = function() {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    /** watchDelay*/
    var watchDelay = 1000;
    
    var currentFilter = 'none';
    
    var currentNode = 0;

    var basePath = '';

    var jobWatcher;

    var watchJobname = 'none';

    var fetchJobsUrl = '';

    var showJobUrl = '';

    var fetchJobUnitOptionsUrl = '';

    var fetchJobUnitFilesUrl = '';

    var reloadJobUrl = '';

    var jobStatusUrl = '';
    
    var milisec=0 ;
	var seconds= 2 ; 
	var xmlMd5   = 'dummymd5';
	
	var endSec;
	var timeLimit;
	
    /**
     * fetchJobs
     */
    var fetchJobs = function(filter) {
        var contentDiv = YAHOO.util.Dom.get(filter + '_content');
        contentDiv.innerHTML = '<div id=\'temploading_'+filter+'\'>Loading...</div>';

        //ajax request the details section of the page
        currentFilter = filter;

        var sUrl = fetchJobsUrl+ filter;

        //nicely resize to show the loading text
        var temploading = YAHOO.util.Dom.get('temploading_'+filter);
        contentDiv.style.height = temploading.offsetHeight + 'px';

        var fetchJobsCallback = {
            success: jobListCallback,
            failure: jobListCallback,
            argument: [filter]
        };
        
        var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, fetchJobsCallback, null);
    };


    /**
     * jobListCallback
     *
     * This is used to animated the slide down for the joblist for running, recently completed
     */    
    var jobListCallback = function(o) {

        var filter= o.argument[0];
        var contentDiv = YAHOO.util.Dom.get(o.argument[0] + '_content');

        contentDiv.innerHTML = o.responseText;

        var joblist = YAHOO.util.Dom.get('jobList_'+filter);
        var anim = new YAHOO.util.Anim(contentDiv.id, { height: {to: joblist.offsetHeight} }, 0.2, YAHOO.util.Easing.easeIn);
        anim.animate();
    };


    /**
     * jobUnitCallback
     */
    var jobUnitCallback = function(o) {
        var optionsResultsDiv = YAHOO.util.Dom.get('optionsResultsDiv');
        optionsResultsDiv.innerHTML = o.responseText;
    };


    /**
     * jobUnitFilesCallback
     */
    var jobUnitFilesCallback = function(o) {
        var optionsResultFilesDiv = YAHOO.util.Dom.get('optionsResultFilesDiv');
        var fileDetails = YAHOO.util.Dom.get('fileDetails'); // remove any viewed files if we are changing units
        fileDetails.innerHTML = '';

        var paramHeader = YAHOO.util.Dom.get("paramHeader");
        paramHeader.style.display = "block";

        optionsResultFilesDiv.innerHTML = o.responseText;
    };


    /**
     * fetchJobUnitOptions
     */
    var fetchJobUnitOptions = function(workUnitName,workUnitParameters) {

        var optionsResultsDiv = YAHOO.util.Dom.get('optionsResultsDiv');
        var item = workUnitName;

        optionsResultsDiv.innerHTML = '<h1>Loading Options...</h1>';
    
        //ajax request the details section of the page

        var sUrl = fetchJobUnitOptionsUrl + item;
                      
        var fjuoCallback = {
            success: jobUnitCallback,
            failure: jobUnitCallback,
            argument: [item] };
        var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, fjuoCallback, null);
    };


    /**
     * jobStatusCallback
     */
    var jobStatusCallback = function(o) {
        var jobStatus =  o.responseText;
        var jobName = o.argument;

        if (jobName != YAHOO.ccgyabi.JobFilter.watchJobname) {
            //this callback has returned after we have clicked on a different job altogether, so we should abort rather than confuse things
            document.getElementById("refreshrate").innerHTML = jobName + ' is not ' + YAHOO.ccgyabi.JobFilter.watchJobname;
            return;
        }

        if  (jobStatus == 'complete'){
            YAHOO.ccgyabi.JobFilter.watchJob('stop', jobName);
            reloadJob(jobName);
            fetchJobs('running');
            fetchJobs('completed');
            document.getElementById("refreshrate").innerHTML = '<a class="refresh">Completed</a>';
            return;
        } 

        if  (jobStatus == 'error'){
            YAHOO.ccgyabi.JobFilter.watchJob('stop', jobName);
            reloadJob(jobName);
            fetchJobs('running');
            fetchJobs('completed');
            return;
        } 
        
        // back off delay
	    if(watchDelay < 34000) {
	        watchDelay = watchDelay * 2;
	    } else {
	        watchDelay = 60000;
	    }
	    
		timeLimit = watchDelay/1000;
		if (timeLimit > 60){
			timeLimit = 60;
			watchDelay = 60000;
		}	   

		
		var today=new Date();
		var nowSec=today.getSeconds();
		
		nowSec = nowSec + 1000;
		
		endSec = nowSec +timeLimit;
		
		YAHOO.ccgyabi.JobFilter.countdown();

        checkReloadJob(jobName);
        


    };


    /**
     * jobStatusCallbackError
     */
    var jobStatusCallbackError = function(o) {
        return;
    };


    /**
     * checkReloadJob
     */
    var checkReloadJob = function(jobName) {
        //ajax request the details section of the page
        
        document.getElementById("refreshrate").innerHTML = '<a class="refresh">Updating workflow....</a>';
        
        if (xmlMd5 === ''){
        	xmlMd5 = 'dummymd5';
        
        }
        
        var sUrl = reloadJobUrl + jobName + '&reload=' + xmlMd5 ;
        
        
        var checkRjCallback = {
            success: checkReloadJobCallback,
            failure: checkReloadJobCallback,
            argument: jobName };
        var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, checkRjCallback, null);
    };



    /**
     * reloadJob
     */
    var reloadJob = function(jobName) {
        //ajax request the details section of the page
        
        var sUrl = reloadJobUrl + jobName;
        
        var rjCallback = {
            success: reloadJobCallback,
            failure: reloadJobCallback,
            argument: [] };
        var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, rjCallback, null);
    };



    /**
     * checkReloadJobCallback
     */
    var checkReloadJobCallback = function(o) {
        var jobName = o.argument;

        if (o.responseText != 'false'){
	        document.getElementById("refreshrate").innerHTML = '<a class="refresh">Reloading workflow....</a>';
        	xmlMd5 = o.responseText;
	        reloadJob(jobName);
        }
        //YAHOO.ccgyabi.JobFilter.countdown();
        //kill all other timeouts
        if (jobWatcher != null) {
            clearInterval(jobWatcher);
        }
        jobWatcher = setTimeout(function () {YAHOO.ccgyabi.JobFilter.watchJob('watch', jobName);}, watchDelay);	          
        
        
    };




    /**
     * reloadJobCallback
     */
    var reloadJobCallback = function(o) {

        var workflowDiv = YAHOO.util.Dom.get('workflowDiv');
        workflowDiv.innerHTML = o.responseText;
        
		watchDelay = 1000;
		timeLimit = watchDelay/1000;
		if (timeLimit > 60){
			timeLimit = 60;
			watchDelay = 60000;
		}		
		
		var today=new Date();
		var nowSec=today.getSeconds();
		nowSec = nowSec + 1000;
		endSec = nowSec +timeLimit;		

        YAHOO.util.Event.onAvailable('yabi-design', YAHOO.ccgyabi.WorkUnitManager.init, null);
    };


    /**
     * workflowCallback
     */
    var workflowCallback = function(o) {

        var workflowDiv = YAHOO.util.Dom.get('workflowDiv');
        var jobName = o.argument;

        workflowDiv.innerHTML = o.responseText;

        //hide param header
        var paramHeader = YAHOO.util.Dom.get("paramHeader");
        paramHeader.style.display = "none";
        

        // empty out the details div
        var details = YAHOO.util.Dom.get('optionsResultsDiv');
        details.innerHTML = '';

        // and the options div
        details = null;
        details = YAHOO.util.Dom.get('optionsResultFilesDiv');
        details.innerHTML = '';

        // and the file details div
        details = null;
        details = YAHOO.util.Dom.get('fileDetails');
        details.innerHTML = '';

        YAHOO.util.Event.onAvailable('yabi-design', YAHOO.ccgyabi.WorkUnitManager.init, null);
        YAHOO.ccgyabi.JobFilter.watchJob('start', jobName);
    };
    


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {



        setBasePath: function(path) {
            basePath = path;
	    
	    },
	
	    setFetchJobsUrl: function (path){
            fetchJobsUrl = path;	    
	    
	    },
	
	    setShowJobUrl: function (path){
            showJobUrl = path;
	    },
	
	    setFetchJobUnitOptionsUrl: function (path){
            fetchJobUnitOptionsUrl = path;
	    },
	
	    setFetchJobUnitFilesUrl: function (path){
            fetchJobUnitFilesUrl = path;
	    },
	
	    setReloadJobUrl: function (path){
            reloadJobUrl = path;
	    },
	
	    setJobStatusUrl: function (path){
            jobStatusUrl = path;
	    },



        /**
         * toggleFilter
         */
        toggleFilter:
        function (e) {

            var elem = YAHOO.util.Dom.get(this.id + '_content');
            var height = elem.style.height;
            var anim;

            height = height.replace('px','');

            if (height > 0) {
                anim = new YAHOO.util.Anim(elem.id, { height: {to: 0} }, 0.2, YAHOO.util.Easing.easeIn);
                anim.animate();
            } else {
                fetchJobs(this.id);
            }

            YAHOO.util.Event.stopEvent(e); //prevent hash link from working as this will cause page reload
        },


        /**
         * fetchJobUnitFiles
         */
        fetchJobUnitFiles:
        function (workUnitId) {

            var path = YAHOO.util.Dom.get('path').innerHTML;
            var optionsResultFilesDiv = YAHOO.util.Dom.get('optionsResultFilesDiv');
            optionsResultFilesDiv.innerHTML = '<h1>Loading File Details...</h1>';
    
            //ajax request the files details section of the page
            var sUrl = fetchJobUnitFilesUrl + 'path=' + path + '&unitid=' + workUnitId;
                      
            var filesCallback = {
                success: jobUnitFilesCallback,
                failure: jobUnitFilesCallback,
                argument: [workUnitId] };
            var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, filesCallback, null);
        },


        /**
         * filterInit
         */
        filterInit:
        function () {

            elements = YAHOO.util.Dom.getElementsByClassName('jobFilterTitle');
            var i, elem;
            for (i=0; i< elements.length; i++) {
                elem = null;
                elem = elements[i];
                YAHOO.util.Event.on(elem, 'click', YAHOO.ccgyabi.JobFilter.toggleFilter);
            }
        },


        /**
         * getJobStatus
         */
        getJobStatus:
        function () {
            var jobName = YAHOO.ccgyabi.JobFilter.watchJobname;

            //early abort if the jobName div contains the text 'complete'
            //otherwise we end up performing lots of unnecessary AJAX calls
            var el = YAHOO.util.Dom.get('jobName');
            if (el.innerHTML.match('complete') !== null) {
                return;
            }

            // abort if jobName not supplied
            if(jobName === undefined) {
                return;
            }

            //ajax request the details section of the page
            var sUrl = jobStatusUrl + jobName;

            var jsCallback = {
                success: jobStatusCallback,
                failure: jobStatusCallbackError,
                argument: jobName
            };

            //if we dont have a jobname, there is no workflow loaded, so dont do this.
            var transaction = null;
            if (jobName !== ''){
	            transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, jsCallback, null);
	        }
        },


        /**
         * showJob
         */
        showJob:
        function (jobName) {
            //ajax request the details section of the page

            var sUrl = showJobUrl + jobName; 

            var showJobCallback = {
                success: workflowCallback,
                failure: workflowCallback,
                argument: jobName };
            var transaction = YAHOO.util.Connect.asyncRequest('GET', sUrl, showJobCallback, null);
        },


        /**
         * watchJob
         */
        watchJob:
        function (jobStatus, jobName){

            if (jobStatus == 'stop'){
                return;
            }

            if (jobStatus == 'start') {
                YAHOO.ccgyabi.JobFilter.watchJobname = jobName;
            }

            if (jobName != 'none'){
                this.getJobStatus();
            }
        },
        
        
      countdown:
        function(){ 
	    
			var today=new Date();
			var nowSec=today.getSeconds();
			
			newNowSec = nowSec + 1000;
			dsec = endSec - newNowSec; 
			
			if (dsec > 60 ){
                newNowSec = newNowSec + 60;
                dsec = endSec - newNowSec;
			}			
			
			if(dsec <= 1){
			    document.getElementById("refreshrate").innerHTML = '<a class="refresh">Updating workflow in 1 second</a>';
			    
//				timeLimit = watchDelay/1000;
//				if (timeLimit > 60){
//					timeLimit = 60;
//					watchDelay = 60000;
//				}
//				var today=new Date();
//				var nowSec=today.getSeconds();
//				nowSec = nowSec + 1000;
//				endSec = nowSec +timeLimit;

			    //setTimeout(function () {YAHOO.ccgyabi.JobFilter.countdown();},800);				
			    return;
			    
			} else {
			  document.getElementById("refreshrate").innerHTML = '<a class="refresh">Updating workflow in '+dsec+' seconds</a>';
			  setTimeout(function () {YAHOO.ccgyabi.JobFilter.countdown();},800);
			}
		 
		}    
		
		
		
		  
        
                
        

    };
}();
