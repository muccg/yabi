YAHOO.namespace("ccgyabi.widget");

/**
 * Constructs a new loading widget. This widget provides a simple overlay that
 * can be attached to a containing element to imply that something is loading
 * in the background. The detail of actually loading something is left as an
 * exercise for the caller, of course.
 *
 * This function won't actually show the loading widget; call {@see #show}
 * after instantiating the object to do so.
 *
 * @constructor
 * @param {Element} container The container to attach the loading overlay to.
 */
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

/**
 * Destroys the loading widget by removing it entirely from the DOM.
 *
 * @warning Don't call the {@link #hide} or {@link #show} methods after calling
 *          this method unless you like code blowing up.
 */
YAHOO.ccgyabi.widget.Loading.prototype.destroy = function () {
    this.container.removeChild(this.element);
};

/**
 * Hides the loading widget.
 */
YAHOO.ccgyabi.widget.Loading.prototype.hide = function () {
    this.element.style.display = "none";
};

/**
 * Shows the loading widget.
 */
YAHOO.ccgyabi.widget.Loading.prototype.show = function () {
    this.element.style.display = "block";
};
