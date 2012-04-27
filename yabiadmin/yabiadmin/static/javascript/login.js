YAHOO.util.Event.onDOMReady(function () {
    /* We may want to perform some more feature tests in here at some point: a
     * warning for users with neither Flash nor File API support might be
     * handy, for instance. For the time being, though, let's just detect the
     * absolute baseline, which is the Selectors API at present. */

    if ("querySelector" in document) {
        document.querySelector("form").style.display = "block";
    }
    else {
        /* Browser sniffing isn't foolproof, of course, but in this case we're
         * not allowing or denying access based on it, but only using it to
         * provide an appropriate upgrade message. If this fails, it's not that
         * big a deal, really. */

        var search = [
            ["Opera", "requirements-failed-opera"],
            ["Chrom", "requirements-failed-chrome"],
            ["Safari", "requirements-failed-safari"],
            ["Firefox", "requirements-failed-firefox"],
            ["MSIE", "requirements-failed-ie"],
            ["*", "requirements-failed-generic"]
        ];

        for (var i = 0; i < search.length; i++) {
            var term = search[i][0];
            var id = search[i][1];

            if (term == "*" || navigator.userAgent.indexOf(term) != -1) {
                document.getElementById(id).style.display = "inline";
                break;
            }
        }

        document.getElementById("requirements-failed").style.display = "block";
    }
});
