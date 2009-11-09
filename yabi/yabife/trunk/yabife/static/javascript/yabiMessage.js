// $Id: yabiMessage.js 1809 2007-12-04 02:29:50Z ntakayama $

/**
 * YabiMessage
 *
 * Uses a YUI singleton pattern
 */
YAHOO.ccgyabi.YabiMessage = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////


    /**
     * showMessage
     */
    var showMessage = function(o) {        
		var yabiMessageDiv = YAHOO.util.Dom.get('yabi-message-ajax');
		yabiMessageDiv.style.display = 'inline';
		yabiMessageDiv.style.visibility = 'visible';
        yabiMessageDiv.style.opacity = 1.0;
        yabiMessageDiv.style.filter = 'alpha(opacity=1.0)';
    };	


    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {

        /**
         * fade
         * 
         * Is called from _header.php when the message divs are used to close message div after 8 secs
         */
        fade:
        function () {
            setTimeout("YAHOO.ccgyabi.YabiMessage.close('" + this.id + "');", 8000);
        },


        /**
         * close
         *
         * Animated close of selected element
         */
        close:
        function (div) {

            //animate fade out
            var myAnim = new YAHOO.util.Anim(div, { opacity: { to: 0 } }, 0.25, YAHOO.util.Easing.easeOut);
            myAnim.animate();

        },
        
        /**
         * Methods for setting the yabi message via javascript 
         * eg. for use when the page is not refreshed
         *
         */
        yabiMessageSuccess:
        function(message) {

		    var yabiMessage = YAHOO.util.Dom.get('yabi-message-ajax');
            yabiMessage.style.backgroundColor = '#00da00';
            var closeLink = '&nbsp;&nbsp;&nbsp;&nbsp;<a class="delLink" href="#" onClick="YAHOO.ccgyabi.YabiMessage.close(\'yabi-message-ajax\');">[x]</a>';
            var newMessage = message + closeLink;
            yabiMessage.innerHTML = newMessage;
            showMessage('yabi-message-ajax');
            setTimeout(function () {YAHOO.ccgyabi.YabiMessage.close('yabi-message-ajax');}, 5000);
        },

        yabiMessageWarn:
        function(message) {
	        var yabiMessage = YAHOO.util.Dom.get('yabi-message-ajax');
            yabiMessage.style.backgroundColor = '#FF6600';
            var closeLink = '&nbsp;&nbsp;&nbsp;&nbsp;<a class="delLink" href="#" onClick="YAHOO.ccgyabi.YabiMessage.close(\'yabi-message-ajax\');">[x]</a>';
            var newMessage = message + closeLink;
            yabiMessage.innerHTML = newMessage;
            showMessage('yabi-message-ajax');
            setTimeout(function () {YAHOO.ccgyabi.YabiMessage.close('yabi-message-ajax');}, 8000);
        },
        
        yabiMessageFail:
        function(message) {
		    var yabiMessage = YAHOO.util.Dom.get('yabi-message-ajax');
            yabiMessage.style.backgroundColor = '#f30124';
            var closeLink = '&nbsp;&nbsp;&nbsp;&nbsp;<a class="delLink" href="#" onClick="YAHOO.ccgyabi.YabiMessage.close(\'yabi-message-ajax\');">[x]</a>';
            var newMessage = message + closeLink;
            yabiMessage.innerHTML = newMessage;
            showMessage('yabi-message-ajax');
            setTimeout(function () {YAHOO.ccgyabi.YabiMessage.close('yabi-message-ajax');}, 8000);
        }          
       
    };
}();


