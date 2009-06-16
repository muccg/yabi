// $Id: fileTree.js 3951 2008-12-08 06:32:31Z ntakayama $

/**
 * FileTree
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.FileTree = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////

    var tree;
    var nodes = [];
    var nodeIndex;	
    var treeUrl;
    var oTrashTextNode;    // Kept in storage so that when we delete items, we can move them into it
    var oTextNodeMap = {}; // Map of TextNode instances in the TreeView instance
		

    /**
     * uploadDataFileResponse
     */
    var uploadDataFileResponse = function(o){ 
        YAHOO.ccgyabi.UploadForm.hideUploadForm();
        YAHOO.ccgyabi.UploadForm.reloadPage();        
    };
    
    /*
     * getTextNodeLabel
     */
     var getTextNodeLabel = function(oTextNode) {
		// The label is sometimes an anchor tag, so to get the text in-between
		// the html tags, use some regEx magic
		var sLabel = oTextNode.label;
		var sLabelText = sLabel;
		var regEx = /^<a.*?>(.*)<\/a>$/i;
		var results = sLabel.match(regEx);
		if (results) {
			sLabelText = results[1];
        }
		return sLabelText;
     };
		

    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {

		/**
		* getTrashTextNode
		*/
	getTrashTextNode:
		function() {
			return oTrashTextNode;
		},

		/**
		* getTextNodePath
		*/
	getTextNodePath:
		function(oTextNode) {
			// The label is sometimes an anchor tag, so to get the text in-between
			// the html tags, use some regEx magic
			var sLabel = oTextNode.label;
			var sLabelText = sLabel;
			var regEx = /^<a.*?>(.*)<\/a>$/i;
			var results = sLabel.match(regEx);
			if (results){
				sLabelText = results[1];
			}
			if (oTextNode.parent.isRoot()) {
				return ("/" + sLabelText);
			} else {
				return (this.getTextNodePath(oTextNode.parent) + "/" + sLabelText);
			}
		},

		/**
		* getTextNodeMap
		*/
	getTextNodeMap:
		function() {
			return oTextNodeMap;
		},

		/**
		* moveTextNode
		*
		*/
	moveTextNode:
		function(oSrcTextNode, oDestTextNode) {
            var oSrcTextNodesParent = oSrcTextNode.parent;

            tree.removeChildren(oSrcTextNode.parent);
            tree.removeChildren(oDestTextNode);

            oSrcTextNodesParent.expand();
            oDestTextNode.expand();
		},

    copyTextNode:
        function(oSrcTextNode, oDestTextNode) {
            var oSrcTextNodesParent = oSrcTextNode.parent;

            tree.removeChildren(oSrcTextNode.parent);
            tree.removeChildren(oDestTextNode);

            oSrcTextNodesParent.expand();
            oDestTextNode.expand();
        },


        /**
         * treeInit
         */
    treeInit:
        function() {    
            YAHOO.ccgyabi.FileTree.buildTreeFromStarterTree();
            
            tree.subscribe("labelClick", function(node) {
				YAHOO.ccgyabi.FileDetails.fetchDetails(node.labelElId);
			});

        },
        
        /**
         * setUrl
         */
    setUrl:
        function(url) {
            treeUrl = url;
        },
        
        /**
         * loadNodeData
         */
    loadNodeData:
        function(node, fnLoadComplete) {    
            var nodeLabel = encodeURI(node.labelElId);
            
            //prepare URL for XHR request:
            var sUrl = treeUrl + "?id=" + nodeLabel;
            
            //prepare our callback object
            var callback = {
                
                //if our XHR call is successful, we want to make use
                //of the returned data and create child nodes.
            success: function(oResponse) {
                YAHOO.log("XHR transaction was successful.", "info", "example");
                var oResults = YAHOO.lang.JSON.parse( oResponse.responseText );
                if((oResults.ResultSet.Result) && (oResults.ResultSet.Result.length)) {
                    //Result is an array if more than one result, string otherwise
                    if(YAHOO.lang.isArray(oResults.ResultSet.Result)) {
                        for (i=0, j=oResults.ResultSet.Result.length; i<j; i++) {
                            tempNode = new YAHOO.widget.TextNode(oResults.ResultSet.Result[i].name, node, false);
                            tempNode.labelElId = oResults.ResultSet.Result[i].encodedPath;
                            if (oResults.ResultSet.Result[i].hasChildren == "false") {
                                tempNode.iconMode = 1;
                                tempNode.children = {};
                                tempNode.dynamicLoadComplete = true;
                                tempNode.expanded = true;
                            }
                            oTextNodeMap[tempNode.labelElId] = tempNode;
                        }
                    } else {
                        //there is only one result; comes as string:
                        tempNode = new YAHOO.widget.TextNode(oResults.ResultSet.Result, node, false);
                        tempNode.labelElId = oResults.ResultSet.Result.encodedPath;
                        if (oResults.ResultSet.Result.hasChildren == "false") {
                            tempNode.iconMode = 1;
                            tempNode.children = {};
                            tempNode.dynamicLoadComplete = true;
                            tempNode.expanded = true;
                        }
                        oTextNodeMap[tempNode.labelElId] = tempNode;
                    }
                }
                
                //When we're done creating child nodes, we execute the node's
                //loadComplete callback method which comes in via the argument
                //in the response object (we could also access it at node.loadComplete,
                //if necessary):
                oResponse.argument.fnLoadComplete();
            },
                
                //if our XHR call is not successful, we want to
                //fire the TreeView callback and let the Tree
                //proceed with its business.
            failure: function(oResponse) {
                YAHOO.log("Failed to process XHR transaction.", "info", "example");
                oResponse.argument.fnLoadComplete();
            },
                
                //our handlers for the XHR response will need the same
                //argument information we got to loadNodeData, so
                //we'll pass those along:
            argument: {
                "node": node,
                "fnLoadComplete": fnLoadComplete
            },
                
                //timeout -- if more than 7 seconds go by, we'll abort
                //the transaction and assume there are no children:
            timeout: 7000
            };
            
            //With our callback object ready, it's now time to 
            //make our XHR call using Connection Manager's
            //asyncRequest method:
            YAHOO.util.Connect.asyncRequest('GET', sUrl, callback);
        },
    

        /**
         * buildTreeFromStarterTree
         */    
    buildTreeFromStarterTree:
        function() { 
	           
	        tree = new YAHOO.widget.TreeView('treeDiv');
            
            //turn dynamic loading on for entire tree: 
            tree.setDynamicLoad(this.loadNodeData, 0); 
            
	        var parent = [];
	        parent[0] = tree.getRoot();
	        var depth = 0;
	        var lastNode = parent[0];
	
	        //grab handle on starterTree and iterate its nodes
	        var starterTree = YAHOO.util.Dom.get('starterTree');
            var nodeName, tmpNode;
            var i, j;
	        for (i = 0; i < starterTree.childNodes.length; i++) {
                nodeName = null;
	            nodeName = starterTree.childNodes[i].innerHTML;
	            
	            if (nodeName == '+1') {
	                //increment depth, set new parent
	                depth++;
	                parent[depth] = lastNode;
	                continue;
	            }
	            if (nodeName == '-1') {
	                //decrement depth, continue
	                depth--;
	                continue;
	            }
	            if (nodeName == '-2') {
	                //decrement depth, continue
	                depth -= 2;
	                continue;
	            }
	            if (nodeName == '-3') { depth -= 3; continue; }
	            if (nodeName == '-4') { depth -= 4; continue; }
                if (nodeName == '-5') { depth -= 5; continue; }
	
                tmpNode = null;
	            tmpNode = new YAHOO.widget.TextNode(nodeName, parent[depth], false);
	            tmpNode.labelElId = starterTree.childNodes[i].id;
                tmpNode.iconMode = 1;
                oTextNodeMap[tmpNode.labelElId] = tmpNode;
                if (tmpNode.label && (getTextNodeLabel(tmpNode) == "Trash")) {
                	oTrashTextNode = tmpNode;
                }
                if (starterTree.childNodes[i].className == "file") {
                    tmpNode.expand();
                }
	            lastNode = tmpNode;
	            
	            //if we have a cookied path then pre-expand to that path
	            if (readCookie('yabiFileBrowseLast') !== null && 
	                tmpNode.labelElId !== null) {
	                if (tmpNode.labelElId == readCookie('yabiFileBrowseLast') ) {
                        tmpNode.dataLoader = null;
                        tmpNode.dynamicLoadComplete = true;
                        tmpNode.expand();
                        
	                    for (j=1; j<= depth;j++) {
	                        parent[j].dataLoader = null;
                            parent[j].dynamicLoadComplete = true;
                            parent[j].expand();
	                    }
                        
	                    //and also fetch details for that path
	                    YAHOO.ccgyabi.FileDetails.fetchDetails(tmpNode.labelElId);
	                }
	            }
	        }
	
	        tree.draw();
	    }
    };
}();
