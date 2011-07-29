window.onload = function () {
    var appliance = document.getElementById("id_appliance");
    var tos = document.getElementById("tos");

    var setToS = function (text) {
        while (tos.childNodes.length) {
            tos.removeChild(tos.firstChild);
        }

        tos.appendChild(document.createTextNode(text));
    };

    var updateToS = function () {
        if (appliance.value && appliance.value in applianceTerms) {
            setToS(applianceTerms[appliance.value]);
        }
        else {
            setToS("");
        }

        return true;
    };

    appliance.onchange = updateToS;
    updateToS();
};
