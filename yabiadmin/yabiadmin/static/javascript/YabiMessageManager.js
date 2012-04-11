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
    this.addDiv(el); //animate in
    this.messages[key] = el;
};

YabiMessageManager.prototype.removeMessage = function (key) {
    try {
        this.removeDiv(this.messages[key]); //animate out
        delete this.messages[key];
    } catch (e) {
        //console.log("argh "+e);
    }
};

YabiMessageManager.prototype.addDiv = function(div) {
    var anim = new YAHOO.util.Anim(div, { opacity: { to: 1.0 } }, 0.3, YAHOO.util.Easing.Linear);
    anim.animate();
};

YabiMessageManager.prototype.removeDiv = function(div) {
    var anim = new YAHOO.util.Anim(div, { opacity: { to: 0.0 } }, 0.3, YAHOO.util.Easing.Linear);
    anim.onComplete.subscribe(function() { this.getEl().parentNode.removeChild(this.getEl()); });
    anim.animate();
};
