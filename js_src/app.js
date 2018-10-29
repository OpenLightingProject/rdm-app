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

goog.provide('app.setup');

goog.require('app.displayCommand');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.Component');
goog.require('goog.ui.TableSorter');


// These are populated in the page
app.SOFTWARE_VERSIONS = [];
app.OPEN_FIXTURE_LIBRARY_MODEL_URL = null;

/**
 * Sort hex values
 * @param {*} a First sort value.
 * @param {*} b Second sort value.
 * @return {number} Negative if a < b, 0 if a = b, and positive if a > b.
 */
app.hexSort = function(a, b) {
  return parseInt(a, 16) - parseInt(b, 16);
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
 * @param {!Element} node The HTML element to hide.
 */
app.hideNode = function(node) {
  node.style.display = 'none';
};

/**
 * Show a block node
 * @param {!Element} node The HTML element to show as a block.
 */
app.showBlock = function(node) {
  node.style.display = 'block';
};

/**
 * Show a inline node
 * @param {!Element} node The HTML element to show inline.
 */
app.showInline = function(node) {
  node.style.display = 'inline';
};

/**
 * Show a table row
 * @param {!Element} row The HTML element to show as a table row.
 */
app.showRow = function(row) {
  row.style.display = 'table-row';
};


/**
 * Create a TD node and set the innerHTML property
 * @param {!string} text Inner HTML for the new table cell.
 * @return {!Element} The created TD element.
 */
app.newTD = function(text) {
  var td = goog.dom.createDom('td');
  td.innerHTML = text;
  return td;
};


/**
 * Make the model table sortable
 * @param {!string} table_id
 */
app.makeModelTable = function(table_id) {
  var table = new goog.ui.TableSorter();
  table.decorate(goog.dom.getElement(table_id));

  table.setSortFunction(0, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(1, app.hexSort);
  table.setSortFunction(2, goog.ui.TableSorter.alphaSort);
};
goog.exportSymbol('app.makeModelTable', app.makeModelTable);


/**
 * Set the software versions
 * @param {!Array.<Object>} version_info The software versions.
 */
app.setSoftwareVersions = function(version_info) {
  app.SOFTWARE_VERSIONS = version_info;
};
goog.exportSymbol('app.setSoftwareVersions', app.setSoftwareVersions);


/**
 * Set the URL of the RDM lookup page in the Open Fixture library with the RDM IDs
 * of this model so we can use it to link every personality.
 * @param {!string} url The URL with query parameters for RDM manufacturer ID and RDM model ID.
 */
app.setOpenFixtureLibraryModelUrl = function(url) {
  app.OPEN_FIXTURE_LIBRARY_MODEL_URL = url;
};
goog.exportSymbol('app.setOpenFixtureLibraryModelUrl', app.setOpenFixtureLibraryModelUrl);


/**
 * Display info for the currently selected software version
 * @param {?Element=} element
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
  var personality_fieldset = goog.dom.getElement('model_personality_fieldset');
  if (personality_fieldset) {
    if (personalities && personalities.length) {
      var tbody = goog.dom.getElement('model_personality_tbody');
      goog.dom.removeChildren(tbody);
      for (var i = 0; i < personalities.length; ++i) {
        var personality = personalities[i];
        var oflLink = app.OPEN_FIXTURE_LIBRARY_MODEL_URL + '&amp;personalityIndex=' + personality['index'];

        var tr = goog.dom.createDom('tr');
        // add the cells
        goog.dom.appendChild(tr, app.newTD(personality['index']));
        if ('slot_count' in personality) {
          goog.dom.appendChild(tr, app.newTD(personality['slot_count']));
        } else {
          goog.dom.appendChild(tr, app.newTD('Unknown'));
        }
        goog.dom.appendChild(tr, app.newTD(personality['description']));
        goog.dom.appendChild(tr, app.newTD('<a href="' + oflLink + '">View in Open Fixture Library</a>'));
        goog.dom.appendChild(tbody, tr);
      }
      app.showBlock(personality_fieldset);
    } else {
      app.hideNode(personality_fieldset);
    }
  }

  // Sensors
  var sensors = software_version['sensors'];
  var sensor_fieldset = goog.dom.getElement('model_sensor_fieldset');
  if (sensor_fieldset) {
    if (sensors && sensors.length) {
      var tbody = goog.dom.getElement('model_sensor_tbody');
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
          sensor_type = app.toHex(sensor['type'], 2);
        }
        goog.dom.appendChild(tr, app.newTD(sensor_type));
        goog.dom.appendChild(tr, app.newTD(sensor['supports_recording']));
        goog.dom.appendChild(tr, app.newTD(sensor['supports_min_max']));
        goog.dom.appendChild(tbody, tr);
      }
      app.showBlock(sensor_fieldset);
    } else {
      app.hideNode(sensor_fieldset);
    }
  }

  // supported params
  var supported_params = software_version['supported_parameters'];
  var supported_params_fieldset = goog.dom.getElement('model_params_fieldset');
  if (supported_params_fieldset) {
    if (supported_params && supported_params.length) {
      var supported_params_list = goog.dom.getElement('model_params_list');
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
          goog.dom.appendChild(li, a);
        } else {
          li.innerHTML = '0x' + app.toHex(param['id'], 4);
        }
        goog.dom.appendChild(supported_params_list, li);
      }
      app.showBlock(supported_params_fieldset);
    } else {
      app.hideNode(supported_params_fieldset);
    }
  }
};
goog.exportSymbol('app.changeSoftwareVersion', app.changeSoftwareVersion);


/**
 * Display the latest version for the element.
 * @param {!Element} element
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
};
goog.exportSymbol('app.setLatestVersion', app.setLatestVersion);


/**
 * Make the pid table sortable
 * @param {!string} table_id
 */
app.makePIDTable = function(table_id) {
  var table = new goog.ui.TableSorter();
  table.decorate(goog.dom.getElement(table_id));

  table.setSortFunction(0, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(1, app.hexSort);
  table.setSortFunction(2, app.hexSort);
  table.setSortFunction(3, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(4, goog.ui.TableSorter.alphaSort);
  table.setSortFunction(5, goog.ui.TableSorter.alphaSort);
};
goog.exportSymbol('app.makePIDTable', app.makePIDTable);
