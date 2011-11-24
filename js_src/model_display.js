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

goog.provide('app.ModelDisplayFrame');


/**
 * Create a new model display frame.
 * @constructor
 */
app.ModelDisplayFrame = function(element){
  app.BaseFrame.call(this, element);
};
goog.inherits(app.ModelDisplayFrame, app.BaseFrame);


/**
 * Hide a table row
 */
app.ModelDisplayFrame.prototype.hideNode = function(node) {
  node.style.display = 'none';
}


/**
 * Show a table row
 */
app.ModelDisplayFrame.prototype.showRow = function(row) {
  row.style.display = 'table-row';
}

/**
 * Show a inline node
 */
app.ModelDisplayFrame.prototype.showInline = function(node) {
  node.style.display = 'block';
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
    // TODO(simon): switch to using a container
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
};
