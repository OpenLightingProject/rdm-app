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
 * The code to display pid information.
 * Copyright (C) 2011 Simon Newton
 */

goog.provide('app.MessageStructure');

goog.require('goog.dom');
goog.require('goog.html.sanitizer.HtmlSanitizer');
goog.require('goog.ui.Component');
goog.require('goog.ui.Tooltip');


/**
 * A message field, this represents a field within a RDM message.
 * @param {Object} field_info
 * @param {?goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends goog.ui.Component
 */
app.MessageField = function(field_info, opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
  this._field_info = field_info;
};
goog.inherits(app.MessageField, goog.ui.Component);


/**
 * Return the underlying field info
 * @return {Object}
 */
app.MessageField.prototype.pid = function() { return this._pid; };


/**
 * This component can't be used to decorate
 * @return {!boolean}
 */
app.MessageField.prototype.canDecorate = function() { return false; };


/**
 * Create the dom for this component
 */
app.MessageField.prototype.createDom = function() {
  var class_names = this._field_info['type'] + '_field message_field';
  var field_name = this._field_info['name'];
  if (this._field_info['type'] == 'string') {
    var max = this._field_info['max_size'];
    var min = this._field_info['min_size'];

    if (max != undefined && min != undefined) {
      if (max == min) {
        field_name += ' (' + max + ' bytes )';
      } else {
        field_name += ' ( ≥ ' + min + ', ≤ ' + max + ' bytes )';
      }
    } else if (max != undefined) {
      field_name += ' ( ≤ ' + max + ' bytes )';
    } else if (min != undefined) {
      field_name += ' ( ≥ ' + min + ' bytes )';
    }
  }
  var div = this.dom_.createDom(
      'div',
      {'class': class_names},
      field_name);
  this.setElementInternal(div);
};


/**
 * Attach the event handler
 */
app.MessageField.prototype.enterDocument = function() {
  app.MessageField.superClass_.enterDocument.call(this);

  var tt = 'Type: ' + this._field_info['type'] + '<br>';
  tt += 'Name: ' + this._field_info['name'] + '<br>';

  if (this._field_info['multiplier'] != undefined) {
    tt += 'Multipler: 10<sup>' + this._field_info['multiplier'] + '</sup><br>';
  }

  if (this._field_info['size'] != undefined) {
    tt += 'Size: ' + this._field_info['size'];
  }

  if (this._field_info['ranges']) {
    tt += 'Allowed Values: <ul>';
    var ranges = this._field_info['ranges'];
    for (var i = 0; i < ranges.length; ++i) {
      tt += '<li>[' + ranges[i]['min'] + ', ' + ranges[i]['max'] + ']</li>';
    }
    tt += '</ul>';
  }

  if (this._field_info['enums']) {
    tt += 'Labeled Values: <ul>';
    var enums = this._field_info['enums'];
    for (var i = 0; i < enums.length; ++i) {
      tt += '<li>' + enums[i]['value'] + ': ' + enums[i]['label'] + '</li/>';
    }
    tt += '</ul>';
  }

  var sanitizer = new goog.html.sanitizer.HtmlSanitizer.Builder().build();

  this.tt = new goog.ui.Tooltip(this.getElement());
  this.tt.setSafeHtml(sanitizer.sanitize(tt));
};


/**
 * Remove the tooltip
 */
app.MessageField.prototype.exitDocument = function() {
  app.MessageField.superClass_.exitDocument.call(this);
  if (this.tt) {
    this.tt.detach(this.getElement());
  }
};


/**
 * Create a RDM message structure object.
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends goog.ui.Component
 */
app.MessageStructure = function(opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(app.MessageStructure, goog.ui.Component);


/**
 * Create the dom for the TableContainer
 */
app.MessageStructure.prototype.createDom = function() {
  this.decorateInternal(this.dom_.createElement('div'));
};


/**
 * Decorate an existing element
 * @param {Element} element
 */
app.MessageStructure.prototype.decorateInternal = function(element) {
  app.MessageStructure.superClass_.decorateInternal.call(this, element);
};


/**
 * Check if we can decorate an element.
 * @param {Element} element The DOM element to check.
 * @return {!boolean} True if we can decorate the element.
 */
app.MessageStructure.prototype.canDecorate = function(element) {
  return element.tagName == 'DIV';
};


/**
 * @param {!Array.<app.MessageField>} fields
 */
app.MessageStructure.prototype.update = function(fields) {
  this.removeChildren(true);

  for (var i = 0; i < fields.length; ++i) {
    var field = fields[i];

    var new_div = null;
    if (field['type'] == 'group') {
      new_div = new app.MessageGroup();
      new_div.update(field['items']);
      this.addChild(new_div, true);
      new_div.attachTooltip(field);
    } else {
      new_div = new app.MessageField(field);
      this.addChild(new_div, true);
    }
  }
};


/**
 * A message group, this represents a repeated group of fields within an RDM
 * message.
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends goog.ui.Component
 */
app.MessageGroup = function(opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
  this.tt = null;
};
goog.inherits(app.MessageGroup, app.MessageStructure);


/**
 * Attach the tooltip for this group
 * @param {!app.MessageField} field
 */
app.MessageGroup.prototype.attachTooltip = function(field) {
  this.tt = new goog.ui.Tooltip(this.getElement());
  var tt = 'A repeated group of fields. ';
  var min = field['min_size'];
  var max = field['max_size'];

  if (min != undefined && max != undefined) {
    if (min == max) {
      tt += 'This group repeats ' + min + ' times.';
    } else {
      tt += 'This group repeats ' + min + ' to ' + max + ' times.';
    }
  } else if (min != undefined) {
    tt += 'This group repeats at least ' + min + ' times.';
  } else if (max != undefined) {
    tt += 'This group repeats at most ' + max + ' times.';
  }
  this.tt.setText(tt);
};


/**
 * Decorate an existing element
 * @param {Element} element
 */
app.MessageGroup.prototype.decorateInternal = function(element) {
  app.MessageStructure.superClass_.decorateInternal.call(this, element);
  element.className = 'message_group';
};
