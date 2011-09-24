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
 * The PID Search Results table.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.Component');
goog.require('goog.ui.TableSorter');


goog.provide('app.PidTable');


/**
 * Sort hex values
 * @param {*} a First sort value.
 * @param {*} b Second sort value.
 * @return {number} Negative if a < b, 0 if a = b, and positive if a > b.
 */
app.hexSort = function(a, b) {
  return parseInt(a) - parseInt(b);
};

/**
 * Convert a number to the hex representation
 * @param {number} n the number to convert.
 * @param {number} padding the length to pad to
 * @return {string} the hex representation of the number.
 */
app.toHex = function(n, padding) {
  if (n < 0) {
    n = 0xffffffff + n + 1;
  }
  var s = n.toString(16);
  while (s.length < padding) {
    s = '0' + s;
  }
  return s;
};



/**
 * Create a new pid table object.
 * @constructor
 */
app.PidTable = function(element, state_manager) {
  var table = new goog.ui.TableSorter();
  table.decorate(goog.dom.$(element));
  table.setSortFunction(0, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(1, app.hexSort);
  table.setSortFunction(2, app.hexSort);
  table.setSortFunction(3, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(4, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(5, goog.ui.TableSorter.alphaSort);

  this.result_rows = new app.ResultsRows(state_manager);

  var table = goog.dom.$(element);
  var tbody = table.getElementsByTagName(goog.dom.TagName.TBODY)[0];
  this.result_rows.decorate(tbody);
};


/**
 * Update the PID table with new data.
 */
app.PidTable.prototype.update = function(new_pids) {
  this.result_rows.update(new_pids);
};


/**
 * A row in the results table.
 * @constructor
 */
app.PidRow = function(pid, state_manager, opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
  this._pid = pid;
  this._state_manager = state_manager;
};
goog.inherits(app.PidRow, goog.ui.Component);


/**
 * Return the underlying pid
 */
app.PidRow.prototype.pid = function() { return this._pid; };


/**
 * This component can't be used to decorate
 */
app.PidRow.prototype.canDecorate = function() { return false; };


/**
 * Create the dom for this component
 */
app.PidRow.prototype.createDom = function() {
  var tr = this.dom_.createDom(
      'tr', {},
      goog.dom.createDom('td', {}, this._pid['manufacturer']),
      goog.dom.createDom('td',
                         {},
                         '0x' + app.toHex(this._pid['manufacturer_id'], 4)),
      goog.dom.createDom('td', {}, '0x' + app.toHex(this._pid['pid'], 4)),
      goog.dom.createDom('td',
                         {},
                         this._pid['get_valid'] ? this.tickNode() : ''),
      goog.dom.createDom('td',
                         {},
                         this._pid['set_valid'] ? this.tickNode() : ''),
      goog.dom.createDom('td', {}, this._pid['name']));
  this.setElementInternal(tr);
};


app.PidRow.prototype.tickNode = function() {
  return goog.dom.createDom(
      'img',
      {'src': '/images/tick.png'});
};


/**
 * Attach the event handler
 */
app.PidRow.prototype.enterDocument = function() {
  app.PidRow.superClass_.enterDocument.call(this);
  goog.events.listen(
    this.getElement(),
    goog.events.EventType.CLICK,
    this._rowClicked,
    false,
    this);
};


/**
 * Remove the event hanler
 */
app.PidRow.prototype.exitDocument = function() {
  app.PidRow.superClass_.exitDocument.call(this);
  goog.events.unlisten(
    this.getElement(),
    goog.events.EventType.CLICK,
    this._rowClicked,
    false,
    this);
};


/**
 * Call when the user clicks on this row
 */
app.PidRow.prototype._rowClicked = function() {
  this._state_manager.displayPid(this._pid['manufacturer_id'],
                                this._pid['pid']);
};


/**
 * Create a new result rows object.
 * @constructor
 */
app.ResultsRows = function(state_manager, opt_domHelper) {
  this._state_manager = state_manager;
  goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(app.ResultsRows, goog.ui.Component);


/**
 * Create the dom for the TableContainer
 */
app.ResultsRows.prototype.createDom = function(container) {
  this.decorateInternal(this.dom_.createElement('tbody'));
};


/**
 * Decorate an existing element
 */
app.ResultsRows.prototype.decorateInternal = function(element) {
  app.ResultsRows.superClass_.decorateInternal.call(this, element);
};


/**
 * Check if we can decorate an element.
 * @param {Element} element the dom element to check.
 */
app.ResultsRows.prototype.canDecorate = function(element) {
  return element.tagName == 'TBODY';
};


app.ResultsRows.prototype.update = function(results) {
  this.removeChildren(true);

  for (var i = 0; i < results.length; ++i) {
    var pid = results[i];
    var new_row = new app.PidRow(pid, this._state_manager);
    this.addChild(new_row, true);
  }
};
