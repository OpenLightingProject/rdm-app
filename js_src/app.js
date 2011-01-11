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
goog.require('goog.ui.Tooltip');

goog.require('app.Server');
goog.require('app.BaseFrame');
goog.require('app.PidTable');
goog.require('app.PidSearchFrame');
goog.require('app.PidDisplayFrame');

goog.provide('app.setup');

var app = app || {}


/**
 * This manages all the state transitions.
 * @constructor
 */
app.StateManager = function() {
  this.pid_display_frame = undefined;
  this.pid_search_frame = undefined;
  goog.events.listen(app.history,
                     goog.History.EventType.NAVIGATE,
                     this.navChanged,
                     false,
                     this);
};

app.StateManager.prototype.enable = function() {
  app.history.setEnabled(true);
};

app.StateManager.prototype.setSearchFrame = function(pid_search_frame) {
  this.pid_search_frame = pid_search_frame;
};


app.StateManager.prototype.setDisplayFrame = function(pid_display_frame) {
  this.pid_display_frame = pid_display_frame;
};

app.StateManager.prototype.displayPid = function(manufacturer_id, pid) {
  this.pid_search_frame.show();
  this.pid_display_frame.hide();
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
        function(response) { t.newPids(response); });
      break;
    case 'p':
      app.Server.getInstance().pidSearch(
        params[1],
        function(response) { t.newPids(response); });
      break;
    case 'pn':
      app.Server.getInstance().pidNameSearch(
        params[1],
        function(response) { t.newPids(response); });
      break;
    case 'pid':
      app.Server.getInstance().getPid(
        params[1],
        params[2],
        function(response) { t.renderPid(response); });
      break;
    default:
      this.pid_search_frame.show();
      this.pid_display_frame.hide();
  }
};


/**
 * Called when we receive a new list of pids from a search
 */
app.StateManager.prototype.newPids = function(response) {
  if (response == undefined) {
    return;
  }
  this.pid_search_frame.show();
  this.pid_display_frame.hide();
  this.pid_search_frame.newPids(response['pids']);
};


app.StateManager.prototype.renderPid = function(response) {
  if (response == undefined) {
    return;
  }
  this.pid_search_frame.hide();
  this.pid_display_frame.show();
  this.pid_display_frame.displayPid(response);
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


app.initHistory = function() {
  goog.require('goog.History');
  app.history = new goog.History();
};
goog.exportSymbol('app.initHistory', app.initHistory);


app.setup = function() {
  var state_manager = new app.StateManager();
  var pid_search_frame = new app.PidSearchFrame('pid_search',
                                                state_manager);
  var pid_display_frame = new app.PidDisplayFrame('pid_display',
                                                  state_manager);
  pid_display_frame.hide();

  state_manager.setSearchFrame(pid_search_frame);
  state_manager.setDisplayFrame(pid_display_frame);
  state_manager.enable();
};
goog.exportSymbol('app.setup', app.setup);
