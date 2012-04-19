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
