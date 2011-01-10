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
 * The RDM PID Store app.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.AutoComplete.Basic');
goog.require('goog.ui.Component');
goog.require('goog.ui.CustomButton');
goog.require('goog.ui.Tooltip');

goog.require('app.Server');
goog.require('app.BaseFrame');
goog.require('app.PidTable');

goog.provide('app.PidSearchFrame');


/**
 * Create a new pid search frame.
 * @constructor
 */
app.PidSearchFrame = function(element, state_manager) {
  app.BaseFrame.call(this, element);
  this._state_manager = state_manager;

  this.manufacturer_search_input = goog.dom.$('manufacturer_input');
  var tt = new goog.ui.Tooltip(
      this.manufacturer_search_input,
      'Enter a manufacturer name or hex id, e.g. 7a70')

  goog.events.listen(
    goog.dom.$('manufacturer_form'),
    goog.events.EventType.SUBMIT,
    function(e) {
      e.stopPropagation();
      e.preventDefault();
      this.searchByManufacturer();
      return false;
    },
    false, this);

  var manufacturer_search_button = goog.dom.$('esta_search_button');
  goog.ui.decorate(manufacturer_search_button);

  goog.events.listen(
      manufacturer_search_button,
      goog.events.EventType.CLICK,
      this.searchByManufacturer,
      false,
      this);

  this.pid_search_input = goog.dom.$('pid_input');
  tt = new goog.ui.Tooltip(
      this.pid_search_input,
      'Enter parameter id in hex (0x8000) or decimal (32768)')

  goog.events.listen(
    goog.dom.$('pid_form'),
    goog.events.EventType.SUBMIT,
    function(e) {
      e.stopPropagation();
      e.preventDefault();
      this.searchByPid();
      return false;
    },
    false, this);

  var pid_search_button = goog.dom.$('pid_search_button');
  goog.ui.decorate(pid_search_button);

  goog.events.listen(
      pid_search_button,
      goog.events.EventType.CLICK,
      this.searchByPid,
      false,
      this);

  // fire off a request to get the list of manufacturers
  var server = app.Server.getInstance();
  server.manufacturers(this.newManufacturerList);

  this.pid_table = new app.PidTable('pid_table', state_manager);
};
goog.inherits(app.PidSearchFrame, app.BaseFrame);


/**
 * Setup an auto-complete based on the list of manufacturers.
 */
app.PidSearchFrame.prototype.newManufacturerList = function(results) {
  if (results == undefined) {
    return;
  }

  var manufacturers = new Array();
  for (var i = 0; i < results['manufacturers'].length; ++i) {
    result = results['manufacturers'][i];
    manufacturers.push(
      result['name'] + ' [' + app.toHex(result['id'], 4) + ']');
  }
  var ac1 = new goog.ui.AutoComplete.Basic(
        manufacturers, goog.dom.$('manufacturer_input'), false);
};


/**
 * Called when the manufacturer search button is clicked.
 */
app.PidSearchFrame.prototype.searchByManufacturer = function() {
  var value = this.manufacturer_search_input.value;
  app.history.setToken('m,' + value);
};


/**
 * Called when the pid search button is clicked.
 */
app.PidSearchFrame.prototype.searchByPid = function() {
  var value = this.pid_search_input.value;
  app.history.setToken('p,' + value);
};


/**
 * Update the pid table with the new list of pids.
 */
app.PidSearchFrame.prototype.newPids = function(pids) {
  this.pid_table.update(pids);
};
