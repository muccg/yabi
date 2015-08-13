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
 * Parses a string in ISO 8601 date/time format.
 *
 * @param {String} s The string to parse.
 * @throws String
 * @type {Date}
 */
var parseISODate = function(s) {
  var re = new RegExp('^([0-9]{2}|[0-9]{4})-([0-9]{2})-([0-9]{2})\s+' +
                      '([0-9]{2}):([0-9]{2}):([0-9]{2})');
  var matches = s.match(re);

  if (!matches) {
    throw 'Invalid date string';
  }

  return new Date(matches[1], matches[2] - 1, matches[3], matches[4],
                  matches[5], matches[6]);
};


/**
 * Converts a given interval in seconds to an approximate, human friendly
 * English representation of that interval.
 *
 * @param {Number} seconds The interval in seconds. This must be a non-negative
 *                         number.
 * @type {String}
 */
YAHOO.ccgyabi.widget.EnglishTime = function(seconds) {
  var units = [
    {
      divisor: 365 * 86400,
      singular: 'year',
      plural: 'years'
    },
    {
      divisor: 30 * 86400,
      singular: 'month',
      plural: 'months'
    },
    {
      divisor: 7 * 86400,
      singular: 'week',
      plural: 'weeks'
    },
    {
      divisor: 86400,
      singular: 'day',
      plural: 'days'
    },
    {
      divisor: 3600,
      singular: 'hour',
      plural: 'hours'
    },
    {
      divisor: 60,
      singular: 'minute',
      plural: 'minutes'
    },
    {
      divisor: 1,
      singular: 'second',
      plural: 'seconds'
    },
    {
      divisor: 0.001,
      singular: 'millisecond',
      plural: 'milliseconds'
    },
    {
      divisor: 0.00000001,
      singular: 'shake',
      plural: 'shakes'
    }
  ];
  if (seconds == 0) {
    return 'now';
  }

  for (var i = 0; i < units.length; i++) {
    if (seconds >= units[i].divisor) {
      var unit = units[i];
      var amount = Math.round(seconds / unit.divisor);
      if (amount != 1) {
        return 'in ' + amount + ' ' + unit.plural;
      }
      return 'in ' + amount + ' ' + unit.singular;
    }
  }

  return 'now';
};
