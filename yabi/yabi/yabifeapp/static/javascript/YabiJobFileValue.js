

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
