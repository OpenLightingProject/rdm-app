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
 * The API to communicate with the web server.
 * Copyright (C) 2011 Simon Newton
 */


goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.net.XhrIoPool');
goog.require('goog.net.EventType');


goog.provide('app.Server');


/**
 * A pending server request.
 * @constructor
 */
app.Request = function(url, callback, opt_method, opt_content) {
  this.url = url;
  this.callback = callback;
  this.opt_method = opt_method;
  this.opt_content = opt_content;
};


/**
 * Create a new Server object, this is used to communicate with the web server.
 * @constructor
 */
app.Server = function() {
  this.pool = new goog.net.XhrIoPool({}, 5);
  this.request_queue = new Array();
};

goog.addSingletonGetter(app.Server);

// The max number of requests to have in the queue before displaying a warning
app.Server.REQUEST_QUEUE_LIMIT = 10;
app.Server.MANUFACTURERS_URL = 'manufacturers';
app.Server.PRODUCT_CATEGORY_URL = 'product_categories';
app.Server.SEARCH_URL = 'pid_search';
app.Server.PID_URL = 'pid';
app.Server.MODEL_SEARCH_URL = 'model_search';
app.Server.INFO_URL = 'index_info';


/**
 * Initiate a JSON request
 * @param url the url to fetch.
 * @param callback the callback to invoke when the request completes.
 * @param opt_method {string=} 'GET' or 'POST'.
 * @param opt_content {string=} The post form data.
 * @private
 */
app.Server.prototype._initiateRequest = function(url,
                                                 callback,
                                                 opt_method,
                                                 opt_content) {
  if (this.request_queue.length >= app.Server.REQUEST_QUEUE_LIMIT) {
    alert('The request pool was empty, the server is probably down.');
    return;
  }

  var request = new app.Request(url, callback, opt_method, opt_content);
  this.request_queue.push(request);

  var t = this;
  this.pool.getObject(
    function(xhr) {
      if (!t.request_queue.length)
        return;
      var r = t.request_queue.shift();
      if (r.callback)
        goog.events.listen(xhr, goog.net.EventType.COMPLETE, r.callback, false, t);
      goog.events.listen(xhr, goog.net.EventType.READY, t._cleanupRequest, false, t);
      xhr.send(r.url, r.opt_method, r.opt_content);
    },
    1);
};

/**
 * Clean up from a request, this removes the listener and returns the channel
 * to the pool.
 * @private
 */
app.Server.prototype._cleanupRequest = function(e) {
  var xhr = e.target;
  goog.events.removeAll(xhr);
  this.pool.releaseObject(xhr);
};


/**
 * Check if a request completed properly and if not, show a dialog.
 * This checks both the HTTP code, and the existance of the 'error' property in
 * the response.
 * @return {object} The JSON output, or undefined if an error occured.
 */
app.Server.prototype.checkForErrorDialog = function(e) {
  if (e.target.getStatus() == 200) {
    var response = e.target.getResponseJson();
    if (response['error']) {
      this._showErrorDialog(response['error']);
      return undefined;
    }
    return response;
  } else {
    this._showErrorDialog(e.target.getLastUri() + ' : ' +
                          e.target.getLastError());
    return undefined;
  }
};


/**
 * Show the error dialog
 */
app.Server.prototype._showErrorDialog = function(message) {
  alert(message);
  /*
  var dialog = app.Dialog.getInstance();
  dialog.setButtonSet(goog.ui.Dialog.ButtonSet.OK);
  dialog.setTitle('Request Failed');
  dialog.setContent(message);
  dialog.setVisible(true);
  */
};



/**
 * Fetch a list of manufacturers
 */
app.Server.prototype.manufacturers = function(callback) {
  var s = this;
  this._initiateRequest(
    app.Server.MANUFACTURERS_URL,
    function(e) {
      response = s.checkForErrorDialog(e);
      callback(response);
    });
};


/**
 * Fetch a list of product categories
 */
app.Server.prototype.productCategories = function(callback) {
  var s = this;
  this._initiateRequest(
    app.Server.PRODUCT_CATEGORY_URL,
    function(e) {
      response = s.checkForErrorDialog(e);
      callback(response);
    });
};


/**
 * Search for manufacturer pids.
 */
app.Server.prototype.manufacturerSearch = function(manufacturer_id, callback) {
  var s = this;
  this._initiateRequest(
    app.Server.SEARCH_URL + '?manufacturer=' + manufacturer_id,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Search for a specific PID
 */
app.Server.prototype.pidSearch = function(pid, callback) {
  var s = this;
  this._initiateRequest(
    app.Server.SEARCH_URL + '?pid=' + pid,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Search for a specific PID name
 */
app.Server.prototype.pidNameSearch = function(name, callback) {
  var s = this;
  this._initiateRequest(
    app.Server.SEARCH_URL + '?pid_name=' + name,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Search for a specific PID
 */
app.Server.prototype.getPid = function(manufacturer_id, pid, callback) {
  var s = this;
  this._initiateRequest(
    app.Server.PID_URL + '?manufacturer=' + manufacturer_id + '&pid=' + pid,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Get device model details for a particular manufacturer.
 */
app.Server.prototype.modelSearchByManufacturer = function(manufacturer_id,
                                                          callback) {
  var s = this;
  this._initiateRequest(
    app.Server.MODEL_SEARCH_URL + '?manufacturer=' + manufacturer_id,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Get device models matching a particular category
 */
app.Server.prototype.modelSearchByCategory = function(category_id, callback) {
  var s = this;
  this._initiateRequest(
    app.Server.MODEL_SEARCH_URL + '?category=' + category_id,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};


/**
 * Get the stats for the data store.
 */
app.Server.prototype.getIndexInfo = function(callback) {
  var s = this;
  this._initiateRequest(
    app.Server.INFO_URL,
    function(e) {
      response = s.checkForErrorDialog(e);
      if (response != undefined) {
        callback(response);
      }
    });
};
