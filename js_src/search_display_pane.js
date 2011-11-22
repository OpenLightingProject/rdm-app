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
 * Provides the search / display logic.
 * Copyright (C) 2011 Simon Newton
 */

goog.provide('app.SearchDisplayPane');
goog.provide('app.ManufacturerSearchDisplayPane');

/**
 * A Pane that has two frames, one that provides the search UI and another that
 * provides the display UI.
 * @constructor
 */
app.SearchDisplayPane = function(search_frame, display_frame) {
  this._search_frame = search_frame;
  this._display_frame = display_frame;
  this._search_frame.show();
  this._display_frame.hide();
};


/**
 * Show the Search Frame.
 */
app.SearchDisplayPane.prototype.showSearchFrame = function() {
  this._search_frame.show();
  this._display_frame.hide();
};


/**
 * Show the display frame.
 */
app.SearchDisplayPane.prototype.showDisplayFrame = function() {
  this._search_frame.hide();
  this._display_frame.show();
};


/**
 * Display search results, this passes the results through to the
 * display_frame.
 */
app.SearchDisplayPane.prototype.displaySearchResults = function(search_results) {
  if (search_results == undefined) {
    return;
  }
  this._search_frame.show();
  this._display_frame.hide();
  this._search_frame.update(search_results);
};


/**
 * Update and show the display frame
 */
app.SearchDisplayPane.prototype.displayEntity = function(data) {
  if (data == undefined) {
    return;
  }
  this._search_frame.hide();
  this._display_frame.update(data);
  this._display_frame.show();
};


/**
 * A subclass of the SearchDisplayPane which uses a list of manufacturers.
 */
app.ManufacturerSearchDisplayPane = function(search_frame, display_frame) {
  app.SearchDisplayPane.call(this, search_frame, display_frame);
};
goog.inherits(app.ManufacturerSearchDisplayPane, app.SearchDisplayPane);


/**
 * Handle notification of a new manufacturer list.
 */
app.ManufacturerSearchDisplayPane.prototype.newManufacturers = function(
    manufacturers) {
  this._search_frame.newManufacturers(manufacturers);
};
