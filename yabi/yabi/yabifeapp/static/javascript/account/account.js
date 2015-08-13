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

function YabiAccount(username, showUserOptions, showCredentials) {
  this.showUserOptions = showUserOptions;
  this.showCredentials = showCredentials;
  this.username = username;

  this.paneContainer = document.querySelector('.yabiLeftColumn');
  this.loading = new YAHOO.ccgyabi.widget.Loading(this.paneContainer);

  this.hydrate();
}

YabiAccount.prototype.hydrate = function() {
  var old = this.paneContainer.querySelectorAll('li');
  for (var i = 0; i < old.length; i++) {
    this.paneContainer.removeChild(old[i]);
  }

  this.loading.show();

  this.solidify();
};

YabiAccount.prototype.solidify = function() {
  this.list = new RadioList(this.paneContainer);

  if (this.showUserOptions) {
    this.options = new YabiAccountOptions(this);
  }

  if (this.showCredentials) {
    this.credentials = new YabiAccountCredentials(this);
  }

  this.loading.hide();
  this.list.selectItem(this.list.items[0]);
};

YabiAccount.prototype.destroyRightColumn = function() {
  var column = document.querySelector('.yabiRightColumn');
  var elements = column.childNodes;
  var toRemove = [];

  for (var i = 0; i < elements.length; i++) {
    if (!('className' in elements[i]) ||
        elements[i].className.indexOf('template') == -1) {
      toRemove.push(elements[i]);
    }
  }

  for (i = 0; i < toRemove.length; i++) {
    column.removeChild(toRemove[i]);
  }

};
