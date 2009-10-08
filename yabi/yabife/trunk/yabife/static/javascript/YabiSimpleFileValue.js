// $Id: YabiSimpleFileValue.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiSimpleFileValue
 * create a new file value which represents the path and relevant filename
 */
function YabiSimpleFileValue(path, filename) {
    if (!YAHOO.lang.isArray(path)) {
        path = [path];
    }
    this.pathComponents = path.slice();

    this.path = path.slice();
    this.root = this.path.shift();
    this.filename = filename;
    this.type = "file";
}

YabiSimpleFileValue.prototype.toString = function() {
    if (YAHOO.lang.isUndefined(this.root)) {
        return this.filename;
    }

    if (this.filename === '') {
        return this.root + this.path.join("/");
    }

    if (this.path.length === 0) {
        return this.root + this.filename;
    }

    return this.root + this.path.join("/") + "/" + this.filename;
};

YabiSimpleFileValue.prototype.isEqual = function(b) {
    //console.log(this + " isEqual? " + b);
    //we don't allow files that have the same filename to be selected, even if they come from different paths
    return (this.root == b.root && this.pathComponents == b.pathComponents && this.filename == b.filename);
};
