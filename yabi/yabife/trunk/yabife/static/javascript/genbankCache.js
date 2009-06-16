// $Id: genbankCache.js 1072 2007-07-26 08:23:05Z andrew $

/**
 * GenbankCache
 *
 * Uses a YUI singleton pattern.
 */
YAHOO.ccgyabi.GenbankCache = function () {

    ////////////////////////////////////////////////////////////////////////////////
    // PRIVATE
    ////////////////////////////////////////////////////////////////////////////////



    ////////////////////////////////////////////////////////////////////////////////
    // PUBLIC
    ////////////////////////////////////////////////////////////////////////////////

    return {    

        /**
         * updateUrl
         */
        updateUrl:
        function (id) {
            var url = YAHOO.util.Dom.get(id + ":input:url");
            var type = YAHOO.util.Dom.get(id + ":temp:type");
            var value = YAHOO.util.Dom.get(id + ":temp:value");
            url.value = type.value + value.value;

            var output = YAHOO.util.Dom.get(id + ":input:-o");
            output.value = value.value + ".fa";
        }
    };
}();
