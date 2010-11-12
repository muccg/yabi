YAHOO.namespace("ccgyabi.widget");

YAHOO.util.Event.onDOMReady(function() {
    /**
     * Faux-singleton to implement simple message display.
     */
    YAHOO.ccgyabi.widget.YabiMessage = (function() {
        // Grab the containing element.
        var el = document.getElementById("yabi-message");

        // Construct the internal elements needed for display.
        var text = document.createElement("span");
        el.appendChild(text);

        var close = document.createElement("a");
        close.appendChild(document.createTextNode("[x]"));
        close.href = "#";
        el.appendChild(close);

        // Internal function to actually show a message with a given CSS class.
        var show = function(cls, message) {
            el.className = cls;

            while (text.childNodes.length > 0) {
                text.removeChild(text.firstChild);
            }
            text.appendChild(document.createTextNode(message));

            /* Get a YUI wrapped Element object so we can use setStyle() to
             * handle cross-browser differences in the opacity style. */
            var yuiEl = new YAHOO.util.Element(el);

            yuiEl.setStyle("display", "inline");
            yuiEl.setStyle("visibility", "visible");
            yuiEl.setStyle("opacity", "1.0");

            window.setTimeout(function() { publicMethods.close(); }, 8000);
        };

        // The object containing the available methods to be returned.
        var publicMethods = {
            close: function() {
                var anim = new YAHOO.util.Anim(el, { opacity: { to: 0 } }, 0.25, YAHOO.util.Easing.easeOut);
                anim.animate();
            },
            fail: function(message) { show("fail", message); },
            success: function(message) { show("success", message); },
            warn: function(message) { show("warn", message); }
        };

        // Set up listeners.
        YAHOO.util.Event.addListener(close, "click", function(e) {
            publicMethods.close();
            YAHOO.util.Event.stopEvent(e);
        });

        return publicMethods;
    })();
});
