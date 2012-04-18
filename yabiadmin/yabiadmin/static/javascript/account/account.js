function YabiAccount(username, showUserOptions, showCredentials) {
    this.showUserOptions = showUserOptions;
    this.showCredentials = showCredentials;
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

    this.solidify();
};

YabiAccount.prototype.solidify = function() {
    this.list = new RadioList(this.paneContainer);

    if (this.showUserOptions) {
        this.options = new YabiAccountOptions(this);
    }

    if (this.showCredentials) {
        this.credentials = new YabiAccountCredentials(this);
    }

    this.loading.hide();
    this.list.selectItem(this.list.items[0]);
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
