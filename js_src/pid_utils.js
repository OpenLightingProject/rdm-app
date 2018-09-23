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

goog.provide('app.displayCommand');

goog.require('app.MessageStructure');

/**
 * Display a pid command
 * @param {!Object} json
 * @param {!string} element_id
 */
app.displayCommand = function(json, element_id) {
  var msg_structure = new app.MessageStructure();
  msg_structure.decorate(goog.dom.getElement(element_id));
  msg_structure.update(json['items']);
};
goog.exportSymbol('app.displayCommand', app.displayCommand);
