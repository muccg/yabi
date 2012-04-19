var YabiAccountOptions = function (account) {
    var self = this;

    this.account = account;
    this.item = this.account.list.createItem("user options");
    this.list = null;

    this.item.addEventListener("deselect", function () {
        self.account.destroyRightColumn();
        self.destroyList();
    });

    this.item.addEventListener("select", function () {
        self.createList();
    });
};

YabiAccountOptions.prototype.createList = function () {
    this.destroyList();

    this.list = new RadioList(document.querySelector(".yabiMiddleColumn"));
    this.password = new YabiAccountPassword(this);

    this.list.selectItem(this.list.items[0]);
};

YabiAccountOptions.prototype.destroyList = function () {
    if (this.list) {
        this.list.destroy();
        this.list = null;
    }
};


var YabiAccountPassword = function (options) {
    var self = this;

    this.options = options;
    this.container = null;
    this.item = this.options.list.createItem("change password");
    this.template = document.getElementById("optionsPassword");

    this.item.addEventListener("deselect", function () {
        if (self.container) {
            document.querySelector(".yabiRightColumn").removeChild(self.container);
            self.container = null;
            self.form = null;
        }
    });

    this.item.addEventListener("select", function () {
        if (self.container) {
            document.querySelector(".yabiRightColumn").removeChild(self.container);
        }

        self.container = self.template.cloneNode(true);
        self.container.className = null;
        self.container.id = null;
        self.form = self.container.querySelector("form");

        document.querySelector(".yabiRightColumn").appendChild(self.container);

        YAHOO.util.Event.addListener(self.container, "submit", function (e) {
            YAHOO.util.Event.stopEvent(e);

            var currentPassword = self.container.querySelector("input[name='currentPassword']").value;
            var newPassword = self.container.querySelector("input[name='newPassword']").value;
            var confirmPassword = self.container.querySelector("input[name='confirmPassword']").value;

            if (newPassword == confirmPassword) {
                if (newPassword.length >= 6) {
                    var callback = {
                        success: function(o) {
                            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);

                            self.enableForm();
                            self.form.reset();
                        },
                        failure: function(o) {
                            YAHOO.ccgyabi.widget.YabiMessage.handleResponse(o);
                            self.enableForm();
                        }
                    };

                    YAHOO.util.Connect.setForm(self.container.querySelector("form"));
                    YAHOO.util.Connect.asyncRequest("POST", appURL + "account/password", callback);

                    self.disableForm();
                }
                else {
                    YAHOO.ccgyabi.widget.YabiMessage.fail("The new password must be at least 6 characters in length");
                }
            }
            else {
                YAHOO.ccgyabi.widget.YabiMessage.fail("The new passwords must match");
            }
        }, false);
    });
};

YabiAccountPassword.prototype.disableForm = function () {
    var elements = this.form.querySelectorAll("input, select, textarea");

    for (var i = 0; i < elements.length; i++) {
        elements[i].enabled = false;
    }
};

YabiAccountPassword.prototype.enableForm = function () {
    var elements = this.form.querySelectorAll("input, select, textarea");

    for (var i = 0; i < elements.length; i++) {
        elements[i].enabled = true;
    }
};
