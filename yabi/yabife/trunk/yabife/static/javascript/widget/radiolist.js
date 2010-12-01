YAHOO.namespace("ccgyabi.widget");


/**
 * A very, very basic object allowing simple events to be sent and handled by
 * arbitrary objects extending from this one.
 *
 * @constructor
 */
var EventEmitter = function () {
    this.events = {};
};

/**
 * Adds an event listener.
 *
 * @param {String} type The event type (defined by the object extending from
 *                      EventEmitter).
 * @param {Function} callback The function called when the event occurs. This
 *                            function will receive at least one parameter
 *                            (a simple event object supporting a
 *                            stopPropagation method).
 */
EventEmitter.prototype.addEventListener = function (type, callback) {
    if (type in this.events) {
        this.events[type].push(callback);
    }
    else {
        this.events[type] = [callback];
    }
};

/**
 * Sends an event to any registered callbacks. Generally, this would only be
 * called from within the object extending EventEmitter, although there's
 * nothing stopping this method being called from external contexts.
 *
 * @param {String} type The event type.
 * @param ... Additional arguments will be sent to the callback functions as
 *            additional arguments.
 */
EventEmitter.prototype.sendEvent = function (type) {
    var event = {
        stop: false,
        stopPropagation: function () { event.stop = true; }
    };

    var args = [event];

    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args.push(arguments[i]);
        }
    }

    if (type in this.events) {
        for (var i = 0; (i < this.events[type].length) && !event.stop; i++) {
            this.events[type][i].apply(this, args);
        }
    }
};


/**
 * A basic radio list element: this constructs an unordered list with the
 * appropriate event handlers to ensure that only one list item is selected at
 * a time.
 *
 * No styling is performed within this object. The top-level ul element will
 * have a "radio-list" class attached, and the selected list item will have a
 * "selected" class (guaranteed to be only one element at most).
 *
 * @constructor
 * @extends EventEmitter
 * @param {Element} container The containing element.
 */
var RadioList = function (container) {
    this.container = container;
    this.items = [];

    this.list = document.createElement("ul");
    this.list.className = "radio-list";
    this.container.appendChild(this.list);

    EventEmitter.call(this);
};

RadioList.prototype = new EventEmitter();

/**
 * Creates an item within the radio list.
 *
 * @param label Either a string or an element to use as the label.
 * @type RadioListItem
 */
RadioList.prototype.createItem = function (label) {
    var self = this;
    var item = new RadioListItem(this, label);

    this.items.push(item);
    this.list.appendChild(item.element);

    YAHOO.util.Event.addListener(item.element, "click", function () {
        if (item.selected) {
            item.deselect();
        }
        else {
            self.selectItem(item);
        }
    });

    return item;
};

/**
 * Destroys the radio list and removes it from the DOM.
 */
RadioList.prototype.destroy = function () {
    try {
        this.container.removeChild(this.list);
    }
    catch (e) {}

    this.events = {};
    this.items = [];
    this.list = null;
};

/**
 * Selects the given item. Note that the "change" event is only sent if the
 * item given isn't already selected.
 *
 * @param {RadioListItem} The item to select.
 */
RadioList.prototype.selectItem = function (item) {
    // Deselect anything that's already selected.
    for (var i = 0; i < this.items.length; i++) {
        if (this.items[i].selected) {
            // No need to reselect an already selected item.
            if (this.items[i] == item) {
                return;
            }

            this.items[i].deselect();
        }
    }

    // Select the actual item.
    item.select();

    // Send the event.
    this.sendEvent("change", item);
};


/**
 * An item within a {@see RadioList} object.
 *
 * @constructor
 * @extends EventEmitter
 * @param {RadioList} The list to attach the item to.
 * @param label Either a string or Element to use as the label.
 */
var RadioListItem = function (list, label) {
    this.list = list;
    this.label = label;
    this.selected = false;

    this.element = document.createElement("li");
    if (typeof label == "string") {
        this.element.appendChild(document.createTextNode(label));
    }
    else {
        this.element.appendChild(label);
    }

    EventEmitter.call(this);
};

RadioListItem.prototype = new EventEmitter();

/**
 * Deselects the item and sends a "deselect" event.
 */
RadioListItem.prototype.deselect = function () {
    this.element.className = this.element.className.replace(/\bselected\b/, " ");
    this.selected = false;
    this.sendEvent("deselect");
};

/**
 * Selects the item and sends a "select" event.
 */
RadioListItem.prototype.select = function () {
    this.element.className = this.element.className.replace(/\s*$/, " selected");
    this.selected = true;
    this.sendEvent("select");
};
