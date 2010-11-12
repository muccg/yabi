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

    YAHOO.ccgyabi.widget.Loading.superclass.constructor.call(this, this.element);
};

YAHOO.lang.extend(YAHOO.ccgyabi.widget.Loading, YAHOO.util.Element, {
    destroy: function() {
        this.container.removeChild(this.element);
    },
    hide: function() {
        this.setStyle("display", "none");
    },
    show: function() {
        this.setStyle("display", "block");
    }
});
