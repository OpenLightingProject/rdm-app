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
 * The code to display model information.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('app.BaseFrame');
goog.require('goog.events');
goog.require('goog.ui.Component.EventType');
goog.require('goog.ui.MenuItem');
goog.require('goog.ui.Select');

goog.provide('app.ModelDisplayFrame');


/**
 * Create a new model display frame.
 * @constructor
 */
app.ModelDisplayFrame = function(element){
  app.BaseFrame.call(this, element);
  this._software_versions = new Array();

  this._software_select =
    goog.ui.decorate(goog.dom.getElement('software_select'));
  goog.events.listen(
      this._software_select,
      goog.ui.Component.EventType.ACTION,
      this.displaySoftwareVersion,
      false,
      this);
};
goog.inherits(app.ModelDisplayFrame, app.BaseFrame);

/**
 * Hide a table row
 */
app.ModelDisplayFrame.prototype.hideNode = function(node) {
  node.style.display = 'none';
}

/**
 * Show a block node
 */
app.ModelDisplayFrame.prototype.showBlock = function(node) {
  node.style.display = 'block';
}

/**
 * Show a inline node
 */
app.ModelDisplayFrame.prototype.showInline = function(node) {
  node.style.display = 'inline';
}

/**
 * Show a table row
 */
app.ModelDisplayFrame.prototype.showRow = function(row) {
  row.style.display = 'table-row';
}


/**
 * Create a TD node and set the innerHTML property
 */
app.ModelDisplayFrame.prototype.newTD = function(text) {
  var td = goog.dom.createDom('td');
  td.innerHTML = text;
  return td;
}


/**
 * Display the information for a model.
 */
app.ModelDisplayFrame.prototype.update = function(model_info) {
  goog.dom.$('model_manufacturer').innerHTML = model_info['manufacturer'];
  goog.dom.$('model_name').innerHTML = model_info['description'];
  goog.dom.$('model_id').innerHTML = '0x' + app.toHex(model_info['model_id'], 4);

  // link
  var link = model_info['link'];
  var link_row = goog.dom.$('model_link_row');
  if (!link || link.size == 0) {
    this.hideNode(link_row);
  } else {
    var href_element = goog.dom.$('model_link');
    href_element.innerHTML = link;
    href_element.href = link;
    this.showRow(link_row);
  }

  // product category
  var product_category = model_info['product_category'];
  var category_row = goog.dom.$('model_category_row');
  if (!product_category || product_category.size == 0) {
    this.hideNode(category_row);
  } else {
    var element = goog.dom.$('model_category');
    element.innerHTML = product_category;
    this.showRow(category_row);
  }

  // image
  var image_url = model_info['image_key'];
  var image = goog.dom.$('model_image');
  if (image_url) {
    image.src = image_url;
    this.showInline(image);
  } else {
    this.hideNode(image);
    image.src = '';
  }

  // tags
  var tags = model_info['tags']
  var tag_row = goog.dom.$('model_tags_row');
  if (tags) {
    this.showRow(tag_row);
    var tags_div = goog.dom.$('model_tags');
    goog.dom.removeChildren(tags_div);
    for (var i = 0; i < tags.length; ++i) {
      var div = goog.dom.createDom('div');
      div.className = 'model_tag';
      div.innerHTML = tags[i];
      goog.dom.appendChild(tags_div, div);
    }
  } else {
    this.hideNode(tag_row);
  }

  // software versions
  var versions = model_info['software_versions'];
  var software_fieldset = goog.dom.$('software_fieldset');
  if (versions && versions.length) {
    this._software_versions = versions;
    this.showBlock(software_fieldset);
    while (this._software_select.getItemCount() > 0) {
      this._software_select.removeItemAt(0);
    }
    for (var i = 0; i < versions.length; ++i) {
      var version = versions[i];
      var version_str = version['label'] + ' (' + version['version_id'] + ')';
      this._software_select.addItem(new goog.ui.MenuItem(version_str));
    }
    this._software_select.setSelectedIndex(0);
    // for some reason the call above doesn't trigger the event;
    this.displaySoftwareVersion();
  } else {
    this.hideNode(software_fieldset);
  }
};


/**
 * Display info for the currently selected software version
 */
app.ModelDisplayFrame.prototype.displaySoftwareVersion = function() {
  var index = this._software_select.getSelectedIndex();
  var software_version = this._software_versions[index];

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
      goog.dom.appendChild(tr, this.newTD(personality['index']));
      goog.dom.appendChild(tr, this.newTD(personality['slot_count']));
      goog.dom.appendChild(tr, this.newTD(personality['description']));
      goog.dom.appendChild(tbody, tr);
    }
    this.showBlock(personality_fieldset);
  } else {
    this.hideNode(personality_fieldset);
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
      goog.dom.appendChild(tr, this.newTD(sensor['index']));
      goog.dom.appendChild(tr, this.newTD(sensor['description']));
      var type_str = sensor['type_str'];
      var sensor_type = '';
      if (type_str) {
        sensor_type = type_str + ' (0x' + app.toHex(sensor['type'], 2) + ')';
      } else  {
        sensor_type = app.toHex(sensor['type'], 2)
      }
      goog.dom.appendChild(tr, this.newTD(sensor_type));
      goog.dom.appendChild(tr, this.newTD(sensor['supports_recording']));
      goog.dom.appendChild(tbody, tr);
    }
    this.showBlock(sensor_fieldset);
  } else {
    this.hideNode(sensor_fieldset);
  }

  // supported params
  var supported_params = software_version['supported_parameters'];
  var supported_params_fieldset = goog.dom.$('model_params_fieldset');
  if (supported_params && supported_params.length) {
    var supported_params_list = goog.dom.$('model_params_list');
    goog.dom.removeChildren(supported_params_list);
    for (var i = 0; i < supported_params.length; ++i) {
      var li = goog.dom.createDom('li');
      li.innerHTML = supported_params[i];
      goog.dom.appendChild(supported_params_list, li);
    }
    this.showBlock(supported_params_fieldset);
  } else {
    this.hideNode(supported_params_fieldset);
  }
};
