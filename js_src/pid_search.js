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

  var t = this;
  // manufacturer search
  this.manufacturer_search_input = goog.dom.$('manufacturer_input');
  this._attachFormHandler('manufacturer_form',
                          function() {t.searchByManufacturer(); });
  this._attachButtonHandlers('manufacturer_search_button',
                             this.searchByManufacturer);

  // pid name search
  this.pid_name_search_input = goog.dom.$('pid_name_input');
  this._attachFormHandler('pid_name_form', function() {t.searchByPidName(); });
  this._attachButtonHandlers('pid_name_search_button', this.searchByPidName);

  // pid id search
  this.pid_search_input = goog.dom.$('pid_input');
  this._attachFormHandler('pid_form', function() {t.searchByPid(); });
  this._attachButtonHandlers('pid_search_button', this.searchByPid);

  this.pid_table = new app.PidTable('pid_table', state_manager);
};
goog.inherits(app.PidSearchFrame, app.BaseFrame);


/**
 * Setup an auto-complete based on the list of manufacturers.
 */
app.PidSearchFrame.prototype.newManufacturers = function(results) {
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
 * Called when the pid name search button is clicked.
 */
app.PidSearchFrame.prototype.searchByPidName = function() {
  var value = this.pid_name_search_input.value;
  app.history.setToken('pn,' + value);
};


/**
 * Update the pid table with the new list of pids.
 */
app.PidSearchFrame.prototype.update = function(pids) {
  this.pid_table.update(pids);
};


/**
 * Attach a handler for this button
 */
app.PidSearchFrame.prototype._attachButtonHandlers = function(button_name,
                                                              handler) {
  var button = goog.dom.$(button_name);
  goog.ui.decorate(button);
  goog.events.listen(
      button,
      goog.events.EventType.CLICK,
      handler,
      false,
      this);
};


/**
 * Attach a handler for this form
 */
app.PidSearchFrame.prototype._attachFormHandler = function(form_name, handler) {
  goog.events.listen(
    goog.dom.$(form_name),
    goog.events.EventType.SUBMIT,
    function(e) {
      e.stopPropagation();
      e.preventDefault();
      handler();
      return false;
    },
    false, this);
};
