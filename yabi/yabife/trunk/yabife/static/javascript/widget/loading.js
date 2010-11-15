YAHOO.namespace("ccgyabi.widget");

YAHOO.ccgyabi.widget.Loading = function(container) {
    this.container = container;

    this.element = document.createElement("div");
    this.element.className = "listingLoading";

    this.image = document.createElement("img");
    this.image.src = appURL + "static/images/largeLoading.gif";

    this.hide();

    this.element.appendChild(this.image);
    this.container.appendChild(this.element);
};

YAHOO.ccgyabi.widget.Loading.prototype.destroy = function () {
    this.container.removeChild(this.element);
};

YAHOO.ccgyabi.widget.Loading.prototype.hide = function () {
    this.element.style.display = "none";
};

YAHOO.ccgyabi.widget.Loading.prototype.show = function () {
    this.element.style.display = "block";
};
