// $Id: YabiSimpleFileValue.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiSimpleFileValue
 * create a new file value which represents the path and relevant filename
 */
function YabiSimpleFileValue(path, filename) {
    this.path = path;
    this.filename = filename;
    this.type = "file";
}

YabiSimpleFileValue.prototype.toString = function() {
    if (this.path.length === 0) {
        return this.filename;
    }

    if (this.filename === '') {
        return this.path.join("/");
    }

    return this.path.join("/") + "/" + this.filename;
};

YabiSimpleFileValue.prototype.isEqual = function(b) {
    //console.log(this + " isEqual? " + b);
    //we don't allow files that have the same filename to be selected, even if they come from different paths
    return (this.filename == b.filename);
};
