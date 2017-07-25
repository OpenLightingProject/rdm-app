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
goog.require('goog.ui.Component');
goog.require('goog.ui.TableSorter');
goog.require('app.MessageStructure');

goog.provide('app.setup');

var app = app || {}

// Empty list, this is populated in the page
app.SOFTWARE_VERSIONS = []

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
 * Hide a node.
 */
app.hideNode = function(node) {
  node.style.display = 'none';
}

/**
 * Show a block node
 */
app.showBlock = function(node) {
  node.style.display = 'block';
}

/**
 * Show a inline node
 */
app.showInline = function(node) {
  node.style.display = 'inline';
}

/**
 * Show a table row
 */
app.showRow = function(row) {
  row.style.display = 'table-row';
}


/**
 * Create a TD node and set the innerHTML property
 */
app.newTD = function(text) {
  var td = goog.dom.createDom('td');
  td.innerHTML = text;
  return td;
}


/**
 * Make the model table sortable
 */
app.makeModelTable = function(table_id) {
  var table = new goog.ui.TableSorter();
  table.decorate(goog.dom.$(table_id));

  table.setSortFunction(0, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(1, app.hexSort);
  table.setSortFunction(2, goog.ui.TableSorter.alphaSort);
};
goog.exportSymbol('app.makeModelTable', app.makeModelTable);


/**
 * Set the software versions
 */
app.setSoftwareVersions = function(version_info) {
  app.SOFTWARE_VERSIONS = version_info;
};
goog.exportSymbol('app.setSoftwareVersions', app.setSoftwareVersions);


/**
 * Display info for the currently selected software version
 */
app.changeSoftwareVersion = function(element) {
  // default to displaying the first version
  var index = 0;
  if (element) {
    index = element.selectedIndex;
  }
  if (index >= app.SOFTWARE_VERSIONS.length) {
    return;
  }
  var software_version = app.SOFTWARE_VERSIONS[index];

  // DMX Personalities
  var personalities = software_version['personalities'];
  var personality_fieldset = goog.dom.$('model_personality_fieldset');
  if (personalities && personalities.length) {
    var tbody = goog.dom.$('model_personality_tbody');
    goog.dom.removeChildren(tbody);
    for (var i = 0; i < personalities.length; ++i) {
      var personality = personalities[i];
      var tr = goog.dom.createDom('tr');
      // add the cells
      goog.dom.appendChild(tr, app.newTD(personality['index']));
      if ('slot_count' in personality) {
        goog.dom.appendChild(tr, app.newTD(personality['slot_count']));
      } else {
        goog.dom.appendChild(tr, app.newTD('Unknown'));
      }
      goog.dom.appendChild(tr, app.newTD(personality['description']));
      goog.dom.appendChild(tbody, tr);
    }
    app.showBlock(personality_fieldset);
  } else {
    app.hideNode(personality_fieldset);
  }

  // Sensors
  var sensors = software_version['sensors'];
  var sensor_fieldset = goog.dom.$('model_sensor_fieldset');
  if (sensors && sensors.length) {
    var tbody = goog.dom.$('model_sensor_tbody');
    goog.dom.removeChildren(tbody);
    for (var i = 0; i < sensors.length; ++i) {
      var sensor = sensors[i];
      var tr = goog.dom.createDom('tr');
      // add the cells
      goog.dom.appendChild(tr, app.newTD(sensor['index']));
      goog.dom.appendChild(tr, app.newTD(sensor['description']));
      var type_str = sensor['type_str'];
      var sensor_type = '';
      if (type_str) {
        sensor_type = type_str + ' (0x' + app.toHex(sensor['type'], 2) + ')';
      } else  {
        sensor_type = app.toHex(sensor['type'], 2)
      }

      var sensor_range_min_max = '';
	  var sensor_range_min = typeof sensor['range_min'] !== 'number' ? "" : sensor['range_min'];
	  var sensor_range_max = typeof sensor['range_max'] !== 'number' ? "" : sensor['range_max'];
	  sensor_range_min_max = sensor_range_min + " / " + sensor_range_max;

      var sensor_normal_min_max = '';
	  var sensor_normal_min = typeof sensor['normal_min'] !== 'number' ? "" : sensor['normal_min'];
	  var sensor_normal_max = typeof sensor['normal_max'] !== 'number' ? "" : sensor['normal_max'];
	  sensor_normal_min_max = sensor_normal_min + " / " + sensor_normal_max;

      var unit_str = sensor['unit_str'];
      var sensor_unit = '';
      if (unit_str) {
        sensor_unit = unit_str + ' (0x' + app.toHex(sensor['unit'], 2) + ')';
      } else  {
		if (unit_str==null){
		  sensor_unit = ""
		} else {
		  sensor_unit = app.toHex(sensor['unit'], 2)
		}
      }
      goog.dom.appendChild(tr, app.newTD(sensor_type));
      goog.dom.appendChild(tr, app.newTD(sensor['supports_recording']));
      goog.dom.appendChild(tr, app.newTD(sensor['supports_min_max']));
      goog.dom.appendChild(tr, app.newTD(sensor_range_min_max));
      goog.dom.appendChild(tr, app.newTD(sensor_normal_min_max));
      goog.dom.appendChild(tr, app.newTD(sensor_unit));
      goog.dom.appendChild(tbody, tr);
    }
    app.showBlock(sensor_fieldset);
  } else {
    app.hideNode(sensor_fieldset);
  }

  // supported params
  var supported_params = software_version['supported_parameters'];
  var supported_params_fieldset = goog.dom.$('model_params_fieldset');
  if (supported_params && supported_params.length) {
    var supported_params_list = goog.dom.$('model_params_list');
    goog.dom.removeChildren(supported_params_list);
    for (var i = 0; i < supported_params.length; ++i) {
      var param = supported_params[i];
      var param_name = param['name'];
      var li = goog.dom.createDom('li');
      if (param_name) {
        var a = goog.dom.createDom('a');
        a.innerHTML = param_name + ' (0x' + app.toHex(param['id'], 4) + ')';
        a.href = ('/pid/display?manufacturer=' + param['manufacturer_id'] +
          '&pid=' + param['id']);
        goog.dom.appendChild(li, a)
      } else {
        li.innerHTML = '0x' + app.toHex(param['id'], 4);
      }
      goog.dom.appendChild(supported_params_list, li);
    }
    app.showBlock(supported_params_fieldset);
  } else {
    app.hideNode(supported_params_fieldset);
  }
};
goog.exportSymbol('app.changeSoftwareVersion', app.changeSoftwareVersion);


/**
 * Display the latest version for the element.
 */
app.setLatestVersion = function(element) {
  var index = 0;
  var version = 0;
  for (var i = 0; i < app.SOFTWARE_VERSIONS.length; ++i) {
    var version_id = app.SOFTWARE_VERSIONS[i]['version_id'];
    if (version_id > version) {
      version = version_id;
      index = i;
    }
  }
  element.selectedIndex = index;
  app.changeSoftwareVersion(element);
}
goog.exportSymbol('app.setLatestVersion', app.setLatestVersion);


/**
 * Make the pid table sortable
 */
app.makePIDTable = function(table_id) {
  var table = new goog.ui.TableSorter();
  table.decorate(goog.dom.$(table_id));

  table.setSortFunction(0, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(1, app.hexSort);
  table.setSortFunction(2, app.hexSort);
  table.setSortFunction(3, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(4, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(5, goog.ui.TableSorter.alphaSort);
};
goog.exportSymbol('app.makePIDTable', app.makePIDTable);


/**
 * Display a pid command
 */
app.displayCommand = function(json, element_id) {
  var msg_structure = new app.MessageStructure();
  msg_structure.decorate(goog.dom.$(element_id));
  msg_structure.update(json['items']);
};
goog.exportSymbol('app.displayCommand', app.displayCommand);
