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
 * The Device Model Search Frame.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.AutoComplete.Basic');
goog.require('goog.ui.Component');
goog.require('goog.ui.CustomButton');
goog.require('goog.ui.MenuItem');
goog.require('goog.ui.Select');
goog.require('goog.ui.Tooltip');

goog.require('app.BaseFrame');
goog.require('app.History');
goog.require('app.ModelTable');
goog.require('app.Server');

goog.provide('app.ModelSearchFrame');


/**
 * Create a new device model search frame.
 * @constructor
 */
app.ModelSearchFrame = function(element) {
  app.BaseFrame.call(this, element);
  this._index_to_product_categories = new Array();
  this._index_to_tags = new Array();

  var t = this;
  // setup the search-by-manufacturer
  this.manufacturer_search_input =
    goog.dom.$('model_manufacturer_input');
  goog.events.listen(
    goog.dom.$('model_form'),
    goog.events.EventType.SUBMIT,
    function(e) {
      e.stopPropagation();
      e.preventDefault();
      t.searchByManufacturer();
      return false;
    },
    false, this);
  var search_button = goog.dom.$('model_manufacturer_button');
  goog.ui.decorate(search_button);
  goog.events.listen(
      search_button,
      goog.events.EventType.CLICK,
      this.searchByManufacturer,
      false,
      this);

  // setup the search-by-product-category
  this._product_category_select =
    goog.ui.decorate(goog.dom.getElement('model_category_select'));
  this._product_category_select.setScrollOnOverflow(true);
  var category_search_button = goog.dom.$('model_category_button');
  goog.ui.decorate(category_search_button);
  goog.events.listen(
      category_search_button,
      goog.events.EventType.CLICK,
      this.searchByCategory,
      false,
      this);

  var category_tt = new goog.ui.Tooltip(
    category_search_button,
    "Search by RDM (E1.20) Product Category");

  // setup the search by tag
  this._tag_select =
    goog.ui.decorate(goog.dom.getElement('model_tag_select'));
  var tag_search_button = goog.dom.$('model_tag_button');
  goog.ui.decorate(tag_search_button);
  goog.events.listen(
      tag_search_button,
      goog.events.EventType.CLICK,
      this.searchByTag,
      false,
      this);
  var tag_tt = new goog.ui.Tooltip(
    tag_search_button,
    "Search by Custom Tags");

  // fire off a request to get the list of manufacturers
  app.Server.getInstance().modelCategoriesAndTags(function(results) {
      t.newCategoriesAndTags(results);
  });

  this.model_table = new app.ModelTable('model_table');
};
goog.inherits(app.ModelSearchFrame, app.BaseFrame);


/**
 * Setup an auto-complete based on the list of manufacturers.
 */
app.ModelSearchFrame.prototype.newManufacturers = function(results) {
  if (results == undefined) {
    return;
  }

  var manufacturers = new Array();
  for (var i = 0; i < results.length; ++i) {
    result = results[i];
    manufacturers.push(
      result['name'] + ' [' + app.toHex(result['id'], 4) + ']');
  }
  var ac1 = new goog.ui.AutoComplete.Basic(
        manufacturers, this.manufacturer_search_input, false);
};


/**
 * Store the list of product categories.
 */
app.ModelSearchFrame.prototype.newCategoriesAndTags = function(results) {
  if (results == undefined) {
    return;
  }

  for (var i = 0; i < results['categories'].length; ++i) {
    category = results['categories'][i];
    var label = category['name'] + ' (' + category['count'] + ')';
    this._product_category_select.addItem(new goog.ui.MenuItem(label));
    this._index_to_product_categories.push(category['id']);
  }

  // add tags
  for (var i = 0; i < results['tags'].length; ++i) {
    tag = results['tags'][i];
    var label = tag['tag'] + ' (' + tag['count'] + ')';
    this._tag_select.addItem(new goog.ui.MenuItem(label));
    this._index_to_tags.push(tag['tag']);
  }
};


/**
 * Called when the product search button is clicked.
 */
app.ModelSearchFrame.prototype.searchByManufacturer = function() {
  var value = this.manufacturer_search_input.value;
  app.history.setToken(app.History.MODEL_MANUFACTURER_SEARCH + ',' + value);
};


/**
 * Called when the product category search button is clicked.
 */
app.ModelSearchFrame.prototype.searchByCategory = function() {
  var value = this._product_category_select.getSelectedIndex();
  var category = this._index_to_product_categories[value];
 app.history.setToken(app.History.MODEL_CATEGORY_SEARCH + ',' + category);
};


/**
 * Called when the tag search button is clicked.
 */
app.ModelSearchFrame.prototype.searchByTag = function() {
 var value = this._tag_select.getSelectedIndex();
 var tag = this._index_to_tags[value];
 app.history.setToken(app.History.MODEL_TAG_SEARCH + ',' + tag);
};


/**
 * Update the pid table with the new list of pids.
 */
app.ModelSearchFrame.prototype.update = function(models) {
  this.model_table.update(models);
};
