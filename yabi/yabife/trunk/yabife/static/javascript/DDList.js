/**
 * @version    SVN: $Id: DDList.js 4232 2009-03-04 04:25:25Z ntakayama $
 * @package yabi
 * @copyright CCG, Murdoch University, 2007
 */

/* Copyright (c) 2006 Yahoo! Inc. All rights reserved. */
/**
 * @class a YAHOO.util.DDProxy implementation. During the drag over event, the
 * dragged element is inserted before the dragged-over element.
 *
 * @extends YAHOO.util.DDProxy
 * @constructor
 * @param {String} id the id of the linked element
 * @param {String} sGroup the group of related DragDrop objects
 */


/**
 * DDList
 */
YAHOO.example.DDList = function(id, sGroup, config) {



    if (id) {
        this.init(id, sGroup, config);
        this.initFrame();
        this.logger = this.logger || YAHOO;
    }

    var s = this.getDragEl().style;
    s.border = "2px solid #ff6600";
    s.backgroundColor = "#ffffff";
    s.opacity = 0.86;
    s.filter = "alpha(opacity=76)";
};

// YAHOO.example.DDList.prototype = new YAHOO.util.DDProxy();
YAHOO.extend(YAHOO.example.DDList, YAHOO.util.DDProxy);


/**
 * startDrag
 */
YAHOO.example.DDList.prototype.startDrag = function(x, y) {
    this.logger.log(this.id + " startDrag");

    var dragEl = this.getDragEl();
    var clickEl = this.getEl();

    dragEl.innerHTML = clickEl.innerHTML;
    dragEl.className = "yabi-tool";
    dragEl.style.height = "20px";
};


/**
 * endDrag
 */
YAHOO.example.DDList.prototype.endDrag = function(e) {

    // if tempEl is not null we are dragging from the tools menu,
    // other wise we are dragging within the workflow
    var delLink, flowDiv;

    if (this.tempEl !== null && this.tempEl !== undefined) {

        //add garnish to the element
        delLink = document.createElement('a');
        delLink.setAttribute('href', '#');
        var tmpId = this.tempEl.id;
        delLink.onclick = function() { return listSelector.destruct(tmpId); };
        delLink.className = 'delLink';
        delLink.innerHTML = '&nbsp;&nbsp;&nbsp;';
        this.tempEl.appendChild(delLink);
        
        //flow triangle garnish
        flowDiv = document.createElement('div');
        flowDiv.className = 'flowTriangle';
        flowDiv.id = this.tempEl.id + 'flow';
        this.tempEl.appendChild(flowDiv);
        listSelector.update(this.tempEl, false);
    } else {
        listSelector.update(this.getEl(), true);
    }
    
    //forget about the new element
    this.tempEl = null;
};


/**
 * onDrag
 */
YAHOO.example.DDList.prototype.onDrag = function(e, id) {
};


/**
 * onDragOver
 */
YAHOO.example.DDList.prototype.onDragOver = function(e, id) {
    // this.logger.log(this.id.toString() + " onDragOver " + id);

    //uncomment the following line to make drag events more 'accurate' but slows things down badly and causes 'jumping' of options
    //this.onDragEnter(e, id);
};


/**
 * onDragEnter
 */
YAHOO.example.DDList.prototype.onDragEnter = function(e, id) {
    // this.logger.log(this.id.toString() + " onDragEnter " + id);
    // this.getDragEl().style.border = "1px solid #449629";

    var el, mid, el2, p, validDrop, toolName, dragit;

    if (this.tempEl === null || this.tempEl === undefined) {

        if ("string" == typeof id) {
            el = YAHOO.util.DDM.getElement(id);
        } else { 
            el = YAHOO.util.DDM.getBestMatch(id).getEl();
        }
        
        if (el !== null && el !== undefined) {
            mid = YAHOO.util.DDM.getPosY(el) + ( Math.floor(el.offsetTop / 2));
            this.logger.log("mid: " + mid);
        
            if ( YAHOO.util.Event.getPageY(e) < mid ||
                el.id == 'startMarker' ||
                el.id == 'yabi-workflow-drop' ||
                el.id == 'endMarker' ||
                el.id == 'cleanup') {
                el2 = this.getEl();
                p = el.parentNode;
                validDrop = true;
                
                //on drag from left to right, clone
                if (this.getEl().parentNode.className == 'DDSourceList' &&
                    p.className != 'DDSourceList') {
                    el2 = el2.cloneNode(true);
                    el2.id = "clone_" + listSelector.getCloneCounter();
                    
                    toolName = YAHOO.util.Dom.getElementsByClassName('toolName', null, el2 )[0].innerHTML;
                    el2.name = toolName;
                                        
                    //make new element draggable
                    dragit = new YAHOO.example.DDList(el2.id);
                    this.tempEl = el2;
                }
                //on drag to left, ignore
                if (p.className == 'DDSourceList') {
                    validDrop = false;
                } 
                
                //only drop if valid drop
                if (validDrop) {
                    listSelector.swallowHint();				

                    if (el.id == 'yabi-workflow-drop' || el.id == 'endMarker' || el.id == 'startMarker' || el.id == "cleanup") {
                        p = YAHOO.util.DDM.getElement('yabi-design-dropzone');
                        el = YAHOO.util.DDM.getElement('cleanup');
                    }
                    
                    p.insertBefore(el2, el);
                    
                    //set selected highlight
                    listSelector.update(el2, true);
                }
                
            }
        }
    }
};

/**
 * addToEnd
 */
YAHOO.example.DDList.prototype.addToEnd = function(e, id) {
    var el2 = this.getEl();
    var toolName, dragit, el;

    //on drag from left to right, clone
    if (this.getEl().parentNode.className == 'DDSourceList') {
        el2 = el2.cloneNode(true);
        el2.id = "clone_" + listSelector.getCloneCounter();
        
        // get name
        toolName = YAHOO.util.Dom.getElementsByClassName('toolName', null, el2 )[0].innerHTML;
        el2.name = toolName;
                   
        // get path
        path = YAHOO.util.Dom.getElementsByClassName('toolPath', null, el2 )[0].innerHTML;
        el2.path = path;

         
        //make new element draggable
        dragit = new YAHOO.example.DDList(el2.id);
        this.tempEl = el2;
    }
    
    listSelector.swallowHint();             
    p = YAHOO.util.DDM.getElement('yabi-design-dropzone');
    el = YAHOO.util.DDM.getElement('cleanup');
    
    p.insertBefore(el2, el);
    
    //add garnish to the element
    delLink = document.createElement('a');
    delLink.setAttribute('href', '#');
    var tmpId = this.tempEl.id;
    delLink.onclick = function() { return listSelector.destruct(tmpId); };
    delLink.className = 'delLink';
    delLink.innerHTML = '&nbsp;&nbsp;&nbsp;';
    this.tempEl.appendChild(delLink);

    //flow triangle garnish
    flowDiv = document.createElement('div');
    flowDiv.className = 'flowTriangle';
    flowDiv.id = this.tempEl.id + 'flow';
    this.tempEl.appendChild(flowDiv);
    listSelector.update(this.tempEl, false);

    //set selected highlight 
    listSelector.update(el2, true);

};


YAHOO.example.DDList.prototype.addToEndForLoadWorkflow = function(e, id) {
    var el2 = this.getEl();
    var toolName, dragit, el;

    //on drag from left to right, clone
    if (this.getEl().parentNode.className == 'DDSourceList') {
        el2 = el2.cloneNode(true);
        el2.id = "clone_" + listSelector.getCloneCounter();
        
        toolName = YAHOO.util.Dom.getElementsByClassName('toolName', null, el2 )[0].innerHTML;
        el2.name = toolName;
                            
        //make new element draggable
        dragit = new YAHOO.example.DDList(el2.id);
        this.tempEl = el2;
    }
    
    listSelector.swallowHint();             
    p = YAHOO.util.DDM.getElement('yabi-design-dropzone');
    el = YAHOO.util.DDM.getElement('cleanup');
    
    p.insertBefore(el2, el);
    
    //add garnish to the element
    delLink = document.createElement('a');
    delLink.setAttribute('href', '#');
    var tmpId = this.tempEl.id;
    delLink.onclick = function() { return listSelector.destruct(tmpId); };
    delLink.className = 'delLink';
    delLink.innerHTML = '&nbsp;&nbsp;&nbsp;';
    this.tempEl.appendChild(delLink);

    //flow triangle garnish
    flowDiv = document.createElement('div');
    flowDiv.className = 'flowTriangle';
    flowDiv.id = this.tempEl.id + 'flow';
    this.tempEl.appendChild(flowDiv);
    listSelector.update(this.tempEl, false);
};




/**
 * onMouseDown
 */
YAHOO.example.DDList.prototype.onMouseDown = function(e, id) {
    listSelector.update(this.getEl(), false);
};


/**
 * onDragOut
 */
YAHOO.example.DDList.prototype.onDragOut = function(e, id) {
    // I need to know when we are over nothing
    // this.getDragEl().style.border = "1px solid #964428";
    if (this.tempEl !== null && this.tempEl !== undefined) {
        this.tempEl.parentNode.removeChild(this.tempEl);
        this.tempEl = null;
    }
    
    var workflow = YAHOO.util.DDM.getElement('yabi-design-dropzone');
    if (workflow.childNodes.length <= 3) {
            listSelector.spitHint();
    }
};


/**
 * toString
 */
YAHOO.example.DDList.prototype.toString = function() {
    return "DDList " + this.id;
};



/////////////////////////////////////////////////////////////////////////////
// DDListBoundary
/////////////////////////////////////////////////////////////////////////////

/**
 * DDListBoundary
 */
YAHOO.example.DDListBoundary = function(id, sGroup, config) {
    if (id) {
        this.init(id, sGroup, config);
        this.logger = this.logger || YAHOO;
        this.isBoundary = true;
    }
};

// YAHOO.example.DDListBoundary.prototype = new YAHOO.util.DDTarget();
YAHOO.extend(YAHOO.example.DDListBoundary, YAHOO.util.DDTarget);

YAHOO.example.DDListBoundary.prototype.toString = function() {
    return "DDListBoundary " + this.id;
};
