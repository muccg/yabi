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

        /* Helper function to turn a HTTP response code into a YabiMessage
         * error level. */
        var guessErrorLevel = function(status) {
            // IE handles 204 No Content as status code 1223. Yes, really.
            if ((status >= 200 && status <= 299) || status == 1223) {
                return "success";
            }

            /* There's no point trying to distinguish warnings and errors: if
             * we're at this point, they're all errors. */
            return "fail";
        };

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
            handleResponse: function(response) {
                var message, level = guessErrorLevel(response.status);

                try {
                    // Handle a valid JSON structure.
                    var data = YAHOO.lang.JSON.parse(response.responseText);

                    if ("message" in data) {
                        message = data.message;
                    }

                    if ("level" in data) {
                        level = data.level;
                    }
                }
                catch (e) {
                    /* No valid JSON returned, so we'll check the error level
                     * based on the status code: if it appears to be a failure,
                     * then we'll display a generic error message. */
                    if (level == "fail") {
                        message = "An error occurred within YABI. No further information is available.";
                    }
                }

                if (message) {
                    show(level, message);
                }
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
