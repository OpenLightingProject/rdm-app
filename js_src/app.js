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
goog.require('goog.ui.Component');
goog.require('goog.ui.TabPane');
goog.require('goog.ui.Tooltip');

goog.require('app.Server');
goog.require('app.PidSearchFrame');
goog.require('app.PidDisplayFrame');
goog.require('app.ModelSearchFrame');

goog.provide('app.setup');

var app = app || {}


/**
 * Top level class to manage PID searching.
 * @constructor
 */
app.PidSearcher = function(state_manager) {
  this.pid_search_frame = new app.PidSearchFrame('pid_search',
                                                 state_manager);
  this.pid_display_frame = new app.PidDisplayFrame('pid_display',
                                                   state_manager);
  this.pid_search_frame.show();
  this.pid_display_frame.hide();
};


/**
 * Show the PID Search Frame.
 */
app.PidSearcher.prototype.showSearchFrame = function() {
  this.pid_search_frame.show();
  this.pid_display_frame.hide();
};


/**
 * Show the PID display frame.
 */
app.PidSearcher.prototype.showDisplayFrame = function() {
  this.pid_search_frame.hide();
  this.pid_display_frame.show();
};


/**
 * Display PID search results.
 */
app.PidSearcher.prototype.displaySearchResults = function(search_results) {
  if (search_results == undefined) {
    return;
  }
  this.pid_search_frame.show();
  this.pid_display_frame.hide();
  this.pid_search_frame.newPids(search_results['pids']);
};


/**
 * Show the details for a particular PID.
 */
app.PidSearcher.prototype.displayPid = function(pid_data) {
  if (pid_data == undefined) {
    return;
  }
  this.pid_search_frame.hide();
  this.pid_display_frame.show();
  this.pid_display_frame.displayPid(response);
};




/**
 * The top level class for handling device model searches.
 * @constructor
 */
app.ModelSearcher = function(state_manager) {
  this.model_search_frame = new app.ModelSearchFrame(state_manager);
};


/**
 * Display device model search results.
 */
app.ModelSearcher.prototype.displaySearchResults = function(search_results) {
  if (search_results == undefined) {
    return;
  }
  this.model_search_frame.newModels(search_results['models']);
};




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

  goog.events.listen(app.history,
                     goog.History.EventType.NAVIGATE,
                     this.navChanged,
                     false,
                     this);
};

app.StateManager.prototype.enable = function() {
  app.history.setEnabled(true);
};

app.StateManager.prototype.setPidSearcher = function(pid_searcher) {
  this.pid_searcher = pid_searcher;
};

app.StateManager.prototype.setModelSearcher = function(model_searcher) {
  this.model_searcher = model_searcher;
};


app.StateManager.prototype.displayPid = function(manufacturer_id, pid) {
  this.pid_searcher.showDisplayFrame();
  app.history.setToken('pid,' + manufacturer_id + ',' + pid);
};


app.StateManager.prototype.navChanged = function(e) {
  if (e.token == null) {
    return;
  }
  params = e.token.split(',');
  var t = this;

  switch (params[0]) {
    case 'm':
      app.Server.getInstance().manufacturerSearch(
        params[1],
        function(response) { t.pid_searcher.displaySearchResults(response); });
      break;
    case 'p':
      app.Server.getInstance().pidSearch(
        params[1],
        function(response) { t.pid_searcher.displaySearchResults(response); });
      break;
      break;
    case 'pn':
      app.Server.getInstance().pidNameSearch(
        params[1],
        function(response) { t.pid_searcher.displaySearchResults(response); });
      break;
    case 'pid':
      app.Server.getInstance().getPid(
        params[1],
        params[2],
        function(response) { t.pid_searcher.displayPid(response); });
      break;
    case 'ps':
      this.tab_pane.setSelectedPage(this.model_search_page);
      app.Server.getInstance().modelSearch(
        params[1],
        function(response) { t.model_searcher.displaySearchResults(response); });
      break;
    default:
      this.pid_searcher.showSearchFrame();
  }
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
 * Update the last updated time.
 */
app.updateTimestamp = function(response) {
  var update_time = new Date(response['timestamp'] * 1000);
  var div = goog.dom.$('update_time');
  div.innerHTML = 'Last Updated: ' + update_time;
  div.style.display = 'block';
};


/**
 * The main setup function
 */
app.setup = function() {
  var state_manager = new app.StateManager();
  var pid_searcher = new app.PidSearcher(state_manager);
  var model_searcher = new app.ModelSearcher(state_manager);

  state_manager.setPidSearcher(pid_searcher);
  state_manager.setModelSearcher(model_searcher);
  state_manager.enable();

  // get the last updated time
  var server = app.Server.getInstance();
  server.getUpdateTime(app.updateTimestamp);
};
goog.exportSymbol('app.setup', app.setup);
