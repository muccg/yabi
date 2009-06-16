/**
 * toggleVisibility
 */
function toggleVisibility(div) {    
	
    element = document.getElementById(div);
    if(element === null) {
        return;
    }
		
    // toggle display
    if(element.style.display == 'block') {
        element.style.display = 'none';
    } else {
        element.style.display = 'block';
    }

    return false;
}



/**
 * radioCheck
 */
function radioCheck(me,group) { 

    var checked = me.checked;
    var i;
    var ck;

    if (checked) {
        for (i = 1; i < arguments.length; i++) {
            ck = document.getElementById(arguments[i]);
            if (ck) {
                ck.checked = false;
            }
        }
    }
    me.checked = checked; // checkbox action
}

