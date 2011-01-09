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
 * The parent frame class.
 * Copyright (C) 2011 Simon Newton
 */

goog.require('goog.dom');

goog.provide('app.BaseFrame');


/**
 * The base frame class
 * @param {string} element the id of the div to use.
 * @constructor
 */
app.BaseFrame = function(element_id) {
  this.element = goog.dom.$(element_id);
};


/**
 * Check if this frame is visible.
 * @return {boolean} true if visible, false otherwise.
 */
app.BaseFrame.prototype.isVisible = function() {
  return this.element.style.display == 'block';
};


/**
 * Show this frame
 */
app.BaseFrame.prototype.show = function() {
  this.element.style.display = 'block';
};


/**
 * Hide this frame
 */
app.BaseFrame.prototype.hide = function() {
  this.element.style.display = 'none';
};
