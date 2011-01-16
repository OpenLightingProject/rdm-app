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

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.Component');
goog.require('goog.ui.Tooltip');


goog.provide('app.PidDisplayFrame');


/**
 * A message field, this represents a field within a RDM message.
 * @constructor
 */
app.MessageField = function(field_info, opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
  this._field_info = field_info;
};
goog.inherits(app.MessageField, goog.ui.Component);


/**
 * Return the underlying field info
 */
app.MessageField.prototype.pid = function() { return this._pid; };


/**
 * This component can't be used to decorate
 */
app.MessageField.prototype.canDecorate = function() { return false; };


/**
 * Create the dom for this component
 */
app.MessageField.prototype.createDom = function() {
  var class_names = this._field_info['type'] + '_field message_field';
  var field_name = this._field_info['name'];
  if (this._field_info['type'] == 'string' &&
      this._field_info['max_size'] != undefined) {
    field_name += ' ( <=' + this._field_info['max_size'] + ' bytes)'; 
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

  var tt = (
    'Type: ' + this._field_info['type'] + '<br>' +
    'Name: ' + this._field_info['name'] + '<br>');

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

  if (this._field_info['size'] != undefined) {
    tt += 'Size: ' + this._field_info['size'];
  }
  this.tt = new goog.ui.Tooltip(this.getElement());
  this.tt.setHtml(tt);
};


/**
 * Remove the tooltip
 */
app.MessageField.prototype.exitDocument = function() {
  app.MessageField.superClass_.exitDocument.call(this);
  this.tt.detach(this.getElement());
};


/**
 * Call when the user clicks on this field to rename it.
 */
app.MessageField.prototype._fieldClicked = function() {
};


/**
 * Create a RDM message structure object.
 * @constructor
 */
app.MessageStructure = function(opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(app.MessageStructure, goog.ui.Component);


/**
 * Create the dom for the TableContainer
 */
app.MessageStructure.prototype.createDom = function(container) {
  this.decorateInternal(this.dom_.createElement('div'));
};


/**
 * Decorate an existing element
 */
app.MessageStructure.prototype.decorateInternal = function(element) {
  app.MessageStructure.superClass_.decorateInternal.call(this, element);
};


/**
 * Check if we can decorate an element.
 * @param {Element} element the dom element to check.
 */
app.MessageStructure.prototype.canDecorate = function(element) {
  return element.tagName == 'DIV';
};


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
 * @constructor
 */
app.MessageGroup = function(opt_domHelper) {
  goog.ui.Component.call(this, opt_domHelper);
  this.tt = null;
};
goog.inherits(app.MessageGroup, app.MessageStructure);


/**
 * Attach the tooltip for this group
 */
app.MessageGroup.prototype.attachTooltip = function(field) {
  this.tt = new goog.ui.Tooltip(this.getElement());
  var tt = 'A repeated group of fields. ';
  var min = field['min_size'];
  var max = field['max_size'];

  if (min != undefined && max != undefined) {
    tt += 'This group repeats ' + min + ' to ' + max + ' times.';
  } else if (min != undefined) {
    tt += 'This group repeats at least ' + min + ' times.';
  } else if (max != undefined) {
    tt += 'This group repeats at most ' + max + ' times.';
  }
  this.tt.setHtml(tt);
};


/**
 * Decorate an existing element
 */
app.MessageGroup.prototype.decorateInternal = function(element) {
  app.MessageStructure.superClass_.decorateInternal.call(this, element);
  element.className = 'message_group';
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
 * Create a new pid display frame.
 * @constructor
 */
app.PidDisplayFrame = function(element, state_manager){
  app.BaseFrame.call(this, element);
  this._state_manager = state_manager;
  this._get_request = new app.MessageStructure();
  this._get_request.decorate(goog.dom.$('get_request'));
  this._get_response = new app.MessageStructure();
  this._get_response.decorate(goog.dom.$('get_response'));

  this._set_request = new app.MessageStructure();
  this._set_request.decorate(goog.dom.$('set_request'));
  this._set_response = new app.MessageStructure();
  this._set_response.decorate(goog.dom.$('set_response'));

  var subdevice_help_nodes = goog.dom.getElementsByTagNameAndClass(
    'img', 'subdevice_range_help');
  this._attachToolTipForNodes(
    subdevice_help_nodes,
    "The allowed values for the sub device field. Options are: <ul>" +
    "<li>Root device only (0x0)</li>" +
    "<li>Root or all sub-devices (0x0 - 0x200, 0xffff)</li>" +
    "<li>Root or sub devices (0x0 - 0x200)</li>" +
    "<li>Only sub-devices (0x1 - 0x200)</li>" +
    "</ul>"
    );

  var repeated_help_nodes = goog.dom.getElementsByTagNameAndClass(
    'img', 'repeat_help');
  this._attachToolTipForNodes(
    repeated_help_nodes,
    "Specifies if the displayed block of fields is allowed to be repeated");

  var max_repeated_help_nodes = goog.dom.getElementsByTagNameAndClass(
    'img', 'max_repeat_help');
  this._attachToolTipForNodes(
    max_repeated_help_nodes,
    "The maximum number of times the block of fields can be repeated");

};
goog.inherits(app.PidDisplayFrame, app.BaseFrame);



/**
 * Attach a tooltip for each node in a list.
 */
app.PidDisplayFrame.prototype._attachToolTipForNodes = function(nodes, msg) {
  for (var i = 0; i < nodes.length; ++i) {
    this._attachToolTip(nodes[i], msg);
  }
}


/**
 * Attach a tooltip to a node, this also adds an on click handler.
 */
app.PidDisplayFrame.prototype._attachToolTip = function(node, msg) {
  var tt = new goog.ui.Tooltip(node);
  tt.setHtml(msg);

  goog.events.listen(
      node,
      goog.events.EventType.CLICK,
      function() { tt.showForElement(node); });
};


/**
 * Display the structure of a PID
 */
app.PidDisplayFrame.prototype.displayPid = function(pid_info) {
  goog.dom.$('pid_manufacturer').innerHTML = pid_info['manufacturer'];
  goog.dom.$('pid_name').innerHTML = pid_info['name'];
  goog.dom.$('pid_value').innerHTML = '0x' + app.toHex(pid_info['value'], 4);
  goog.dom.$('pid_link').innerHTML = pid_info['link'];
  goog.dom.$('pid_link').href = pid_info['link'];
  goog.dom.$('pid_notes').innerHTML = pid_info['notes'];

  this._updateCommand(pid_info, 'get');
  this._updateCommand(pid_info, 'set');
};


app.PidDisplayFrame.prototype._hideNode = function(node) {
  node.style.display = 'none';
}


app.PidDisplayFrame.prototype._showNode = function(node) {
  node.style.display = 'block';
}

app.PidDisplayFrame.prototype._updateCommand = function(pid_info, mode) {
  var unsupported_node = goog.dom.$(mode + '_command_unsupported');
  var info_node = goog.dom.$(mode + '_command_description');

  var request_key = mode + '_request';
  var response_key = mode + '_response';

  if (pid_info[request_key] == null) {
    this._showNode(unsupported_node);
    this._hideNode(info_node);
  } else {
    this._hideNode(unsupported_node);
    this._showNode(info_node);
    goog.dom.$(mode + '_subdevice_range').innerHTML = (
      pid_info[mode + '_subdevice_range']);

    var request = pid_info[request_key];
    var response = pid_info[response_key];

    this._setupRepeatInformation(request, request_key);
    this._setupRepeatInformation(response, response_key);

    if (mode == 'get') {
      this._get_request.update(request['items']);
      this._get_response.update(response['items']);
    } else {
      this._set_request.update(request['items']);
      this._set_response.update(response['items']);
    }
  }
};


/**
 * Populate the repeat section of the pid info display
 */
app.PidDisplayFrame.prototype._setupRepeatInformation = function(message,
                                                                 prefix) {
  goog.dom.$(prefix + '_repeated').innerHTML = (
    message['is_repeated'] ? 'True' : 'False');

  var repeat_div = goog.dom.$(prefix + '_repeat_div');
  if (!message['is_repeated'] || message['max_repeats'] == null) {
    this._hideNode(repeat_div);
  } else {
    this._showNode(repeat_div);
    goog.dom.$(prefix + '_max_repeats').innerHTML = message['max_repeats'];
  }
};
