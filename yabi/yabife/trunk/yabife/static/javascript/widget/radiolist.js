YAHOO.namespace("ccgyabi.widget");

var EventEmitter = function () {
    this.events = {};
};

EventEmitter.prototype.addEventListener = function (type, callback) {
    if (type in this.events) {
        this.events[type].push(callback);
    }
    else {
        this.events[type] = [callback];
    }
};

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



var RadioList = function (container) {
    this.container = container;
    this.items = [];

    this.list = document.createElement("ul");
    this.list.className = "radio-list";
    this.container.appendChild(this.list);

    EventEmitter.call(this);
};

RadioList.prototype = new EventEmitter();

RadioList.prototype.createItem = function (label) {
    var self = this;
    var item = new RadioListItem(this, label);

    this.items.push(item);
    this.list.appendChild(item.element);

    item.element.addEventListener("click", function () {
        if (item.selected) {
            item.deselect();
        }
        else {
            self.selectItem(item);
        }
    }, false);

    return item;
};

RadioList.prototype.destroy = function () {
    try {
        this.container.removeChild(this.list);
    }
    catch (e) {}

    this.events = {};
    this.items = [];
    this.list = null;
};

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

RadioListItem.prototype.deselect = function () {
    this.element.className = this.element.className.replace(/\bselected\b/, " ");
    this.selected = false;
    this.sendEvent("deselect");
};

RadioListItem.prototype.select = function () {
    this.element.className = this.element.className.replace(/\s*$/, " selected");
    this.selected = true;
    this.sendEvent("select");
};
