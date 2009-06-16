// $Id: workUnitManager.js 4169 2009-02-20 04:09:13Z ntakayama $

/**
 * WorkUnitManager
 *
 * TODO: the code for selecting a unit is somehow called for each unit present
 * i.e. three units, three calls.
 * We should also look at using code similar to the update method currently in 
 * ListSelector used by the design screen
 */
YAHOO.ccgyabi.WorkUnitManager = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    var elements = null;
    var basePath = null;
    

    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {

        /**
         * init
         */
        init:
        function () {

            elements = YAHOO.util.Dom.getElementsByClassName('workunit');
            var elem;
            for (var i=0; i< elements.length; i++) {
                elem = null;
                elem = elements[i];
                YAHOO.util.Event.on(elem, 'click', YAHOO.ccgyabi.WorkUnitManager.select);
            }
        },


        /**
         * select
         */
        select:
        function (e) {
            var optionsResultsDiv;
            var targ;
            if (!e) { 
                e = window.event; 
            }
            if (e.target) { 
                targ = e.target; 
            } else if (e.srcElement) {
                targ = e.srcElement;
            }
            if (targ.nodeType == 3) { // defeat Safari bug
                targ = targ.parentNode;
            }

            this.selectedElId = targ.id;

            if (!this.selectedElId) {
                return;
            }

            var el = YAHOO.util.Dom.get(this.selectedElId);

            // stop event going further
            YAHOO.util.Event.stopEvent(e);

            var i, flowtriangle, workUnitId, workUnitName, workUnitParameters, optionsResultFilesDiv, paramHeader;
            if (el.parentNode.id == 'yabi-design') {

                // deselect units
                for (i=0;i< elements.length;i++) {
                    flowtriangle = null;
                    flowtriangle = YAHOO.util.Dom.get(elements[i].id + 'flow');
                    if (flowtriangle) {
                        flowtriangle.style.backgroundImage = 'url(../images/yabi-flow-triangle.gif)';
                    } 
                    if (elements[i].style !== null) {
                        elements[i].style.background = 'none';
                        elements[i].style.backgroundColor = '#fff';
                    }
                }

                // select element
                if (el) {
                
                    //change the background image of the selected item's flow triangle
                    flowtriangle = null;
                    flowtriangle = YAHOO.util.Dom.get(el.id + 'flow');
                    if (flowtriangle) {
                        flowtriangle.style.backgroundImage = 'url(../images/yabi-flow-triangle-selected.gif)';
                    }
                
                    el.style.backgroundColor = '#FFEBF0';
                    el.style.background = 'url(../images/node-selected-gradient.png)';

                }

                workUnitId = null;
                workUnitId = YAHOO.util.Dom.get(el.id + 'id');

                YAHOO.ccgyabi.JobFilter.fetchJobUnitFiles(workUnitId.innerHTML);

                workUnitName = null;
                workUnitName = YAHOO.util.Dom.get(el.id + 'name');

                workUnitParameters = null;
                workUnitParameters = YAHOO.util.Dom.get(el.id + 'params');

                optionsResultFilesDiv = null;
                optionsResultFilesDiv = YAHOO.util.Dom.get('optionsResultFilesDiv');

                paramHeader = YAHOO.util.Dom.get('paramHeader');
                paramHeader.style.display = 'none';

                optionsResultsDiv = null;
                optionsResultsDiv = YAHOO.util.Dom.get('optionsResultsDiv');
                optionsResultsDiv.innerHTML = workUnitParameters.innerHTML;

            }
        },


        /**
         * workUnitSelectProxy
         */
        workUnitSelectProxy:
        function () {
            var el = YAHOO.util.Dom.get(this.id);
            YAHOO.ccgyabi.WorkUnitManager.select(el);
        },
        
        
        /**
         * setBasePath
         */
        setBasePath:
        function (path) {
	        basePath = path;
        }
    };
}();

