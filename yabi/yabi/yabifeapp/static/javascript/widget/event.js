/*
 * Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
 * Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
 *  
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the 
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  */



/**
 * A very, very basic object allowing simple events to be sent and handled by
 * arbitrary objects extending from this one.
 *
 * @constructor
 */
var EventEmitter = function() {
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
EventEmitter.prototype.addEventListener = function(type, callback) {
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
 * Additional arguments will be sent to the callback functions as additional
 * arguments.
 */
EventEmitter.prototype.sendEvent = function(type) {
  var event = {
    stop: false,
    stopPropagation: function() { event.stop = true; }
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
