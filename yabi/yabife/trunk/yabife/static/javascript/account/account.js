function YabiAccount(username) {
    this.username = username;

    this.paneContainer = document.querySelector(".yabiLeftColumn");
    this.loading = new YAHOO.ccgyabi.widget.Loading(this.paneContainer);

    this.hydrate();
};

YabiAccount.prototype.hydrate = function() {
    var old = this.paneContainer.querySelectorAll("li");
    for (var i = 0; i < old.length; i++) {
        this.paneContainer.removeChild(old[i]);
    }

    this.loading.show();

    // TODO: AJAX call to determine if the credentials button should be shown.

    this.solidify({
        showCredentials: true
    });
};

YabiAccount.prototype.solidify = function(obj) {
    this.list = new RadioList(this.paneContainer);

    this.options = new YabiAccountOptions(this);

    if (obj.showCredentials) {
        this.credentials = new YabiAccountCredentials(this);
    }

    this.loading.hide();
};

YabiAccount.prototype.destroyRightColumn = function () {
    var column = document.querySelector(".yabiRightColumn");
    var elements = column.childNodes;

    for (var i = 0; i < elements.length; i++) {
        if (!("className" in elements[i]) || elements[i].className.indexOf("template") == -1) {
            column.removeChild(elements[i]);
        }
    }
};
