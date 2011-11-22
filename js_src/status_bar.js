/**
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 * Provides the simple status bar at the top of the page.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('goog.ui.RoundedPanel');

goog.provide('app.StatusBar');


/**
 * The small status bar the appears at the top of the screen to provide
 * feedback to users.
 * @constructor
 */
app.StatusBar = function(element_id) {
  var element = goog.dom.$(element_id)
  this.panel = goog.ui.RoundedPanel.create(3,
                                           3,
                                           '#bbccff',
                                           '#bbccff',
                                           goog.ui.RoundedPanel.Corner.ALL);
  this.panel.decorate(element);
};


app.StatusBar.prototype.setText = function(text) {
  this.panel.getContentElement().innerHTML = text;
  this.panel.getElement().style.display = 'block';
};


app.StatusBar.prototype.setSearching = function() {
  this.setText('Searching ...');
};

app.StatusBar.prototype.setLoading = function() {
  this.setText('Loading ...');
};

app.StatusBar.prototype.hide = function() {
  this.panel.getElement().style.display = 'none';
};
