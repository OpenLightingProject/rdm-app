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

goog.require('goog.History');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.TabPane');

goog.require('app.History');
goog.require('app.ModelDisplayFrame');
goog.require('app.ModelSearchFrame');
goog.require('app.PidDisplayFrame');
goog.require('app.PidSearchFrame');
goog.require('app.SearchDisplayPane');
goog.require('app.Server');
goog.require('app.StatusBar');

goog.provide('app.setup');

var app = app || {}

/**
 * This manages all the state transitions.
 * @constructor
 */
app.StateManager = function() {
  this.pid_searcher = undefined;
  this.model_searcher = undefined;

  // setup the tab pane
  this.tab_pane = new goog.ui.TabPane(goog.dom.$('tab_pane'));
  this.pid_search_page = new goog.ui.TabPane.TabPage(
    goog.dom.$('tab_page_1'), "Parameter IDs");
  this.model_search_page = new goog.ui.TabPane.TabPage(
    goog.dom.$('tab_page_2'), 'Device Models');
  this.tab_pane.addPage(this.pid_search_page);
  this.tab_pane.addPage(this.model_search_page);

  this.pid_searcher = new app.ManufacturerSearchDisplayPane(
      new app.PidSearchFrame('pid_search'),
      new app.PidDisplayFrame('pid_display'));

  this.model_searcher = new app.ManufacturerSearchDisplayPane(
    new app.ModelSearchFrame('device_search'),
    new app.ModelDisplayFrame('device_display'));
  this.status_bar = new app.StatusBar('status_bar');

  var server = app.Server.getInstance();
  // fire off a request to get the list of manufacturers
  var server = app.Server.getInstance();
  var t = this;
  server.manufacturers(function(results) {t.newManufacturers(results); });

  goog.events.listen(app.history,
                     goog.History.EventType.NAVIGATE,
                     this.navChanged,
                     false,
                     this);

  app.history.setEnabled(true);
};


/**
 * This is called when the url changes and triggers a state change.
 */
app.StateManager.prototype.navChanged = function(e) {
  if (e.token == null) {
    return;
  }
  params = e.token.split(',');
  var t = this;

  switch (params[0]) {
    case app.History.PID_MANUFACTURER_SEARCH:
      this.status_bar.setSearching();
      app.Server.getInstance().manufacturerSearch(
        params[1],
        function(response) { t.newPidResults(response); });
      break;
    case app.History.PID_ID_SEARCH:
      this.status_bar.setSearching();
      app.Server.getInstance().pidSearch(
        params[1],
        function(response) { t.newPidResults(response); });
      break;
      break;
    case app.History.PID_NAME_SEARCH:
      this.status_bar.setSearching();
      app.Server.getInstance().pidNameSearch(
        params[1],
        function(response) { t.newPidResults(response); });
      break;
    case app.History.PID_DISPLAY:
      this.status_bar.setLoading();
      app.Server.getInstance().getPid(
        params[1],
        params[2],
        function(response) { t.newPidInfo(response); });
      break;
    case app.History.MODEL_MANUFACTURER_SEARCH:
      this.status_bar.setSearching();
      this.tab_pane.setSelectedPage(this.model_search_page);
      app.Server.getInstance().modelSearchByManufacturer(
        params[1],
        function(response) { t.newDeviceModelResults(response); });
      break;
    case app.History.MODEL_CATEGORY_SEARCH:
      this.status_bar.setSearching();
      this.tab_pane.setSelectedPage(this.model_search_page);
      app.Server.getInstance().modelSearchByCategory(
        params[1],
        function(response) { t.newDeviceModelResults(response); });
      break;
    case app.History.MODEL_DISPLAY:
      this.status_bar.setLoading();
      app.Server.getInstance().getModel(
        params[1],
        params[2],
        function(response) { t.newModel(response); });
      break;
    default:
      this.pid_searcher.showSearchFrame();
  }
};


/**
 * Called when a new manufacturer list arrives.
 */
app.StateManager.prototype.newManufacturers = function(response) {
  this.pid_searcher.newManufacturers(response['manufacturers']);
  this.model_searcher.newManufacturers(response['manufacturers']);
};


/**
 * Called when new pid results arrive
 */
app.StateManager.prototype.newPidResults = function(response) {
  this.status_bar.hide();
  this.pid_searcher.displaySearchResults(response['pids']);
};


/**
 * Called when new pid info is available.
 */
app.StateManager.prototype.newPidInfo = function(response) {
  this.status_bar.hide();
  this.pid_searcher.displayEntity(response);
};

/**
 * Called when new device model results arrive
 */
app.StateManager.prototype.newDeviceModelResults = function(response) {
  this.status_bar.hide();
  this.model_searcher.displaySearchResults(response['models']);
};


/**
 * Called when new model data is available
 */
app.StateManager.prototype.newModel = function(response) {
  this.status_bar.hide();
  this.model_searcher.displayEntity(response);
};


/**
 * Navigate back to the previous state, or go to the main search page if there
 * is no history remaining.
 */
app.backToSearchResults = function() {
  if (history.previous == undefined) {
    app.history.setToken('');
  } else {
    history.back();
  }
};
goog.exportSymbol('app.backToSearchResults', app.backToSearchResults);


/**
 * Init the history tracking object
 */
app.initHistory = function() {
  goog.require('goog.History');
  app.history = new goog.History();
};
goog.exportSymbol('app.initHistory', app.initHistory);


/**
 * Update the last updated time, and the pid / model counts.
 */
app.updateIndexInfo = function(response) {
  var update_time = new Date(response['timestamp'] * 1000);
  var div = goog.dom.$('update_time');
  div.innerHTML = (
      'Last Updated: ' + update_time + '<br>' +
      response['manufacturer_pid_count'] +  ' Manufacturer PIDs, ' +
      response['device_model_count'] + ' Device Models.');
  div.style.display = 'block';
};


/**
 * The main setup function
 */
app.setup = function() {
  var state_manager = new app.StateManager();

  // get the last updated time
  var server = app.Server.getInstance();
  server.getIndexInfo(app.updateIndexInfo);
};
goog.exportSymbol('app.setup', app.setup);
