/*
 * Yabi - a sophisticated online research environment for Grid, High Performance
 * and Cloud computing.
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
 * YabiJobFileValue
 * create a new job file value which represents the job and relevant filename
 */
function YabiJobFileValue(job, filename) {
  this.job = job;
  this.filename = filename;
}

YabiJobFileValue.prototype.toString = function() {
  return this.filename + ' (' + this.job + ')';
};

YabiJobFileValue.prototype.isEqual = function(b) {
  //console.log(this + " isEqual? " + b);
  return (this.job == b.job && this.filename == b.filename);
};
