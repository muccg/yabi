// $Id: YabiSimpleFileValue.js 4322 2009-03-17 06:18:36Z ntakayama $

/**
 * YabiMessageManager
 * handles a lookup array of objects and message divs
 * so, for example, a single XHR can update its own div with messages
 */
function YabiMessageManager(container) {
    this.containerEl = YAHOO.util.Dom.get(container);
    this.messages = [];
}

YabiMessageManager.prototype.addMessage = function (key, value, styleName) {
    var el = document.createElement('div');
    el.className = styleName;
    el.appendChild(document.createTextNode(value));
    this.containerEl.appendChild(el);
    this.messages[key] = el;
};

YabiMessageManager.prototype.removeMessage = function (key) {
    try {
        this.containerEl.removeChild(this.messages[key]);
        delete this.messages[key];
    } catch (e) {
        console.log("argh "+e);
    }
};