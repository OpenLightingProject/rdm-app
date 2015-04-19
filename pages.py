# This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# page.py
# Copyright (C) 2011 Simon Newton
# Handlers for simple static pages

from google.appengine.ext import webapp

import common


class AboutPageHandler(common.BasePageHandler):
    """Display the about page."""
    TEMPLATE = 'templates/about.tmpl'


class DisclaimerPageHandler(common.BasePageHandler):
    """Display the disclaimer page."""
    TEMPLATE = 'templates/disclaimer.tmpl'


class ToolsPageHandler(common.BasePageHandler):
    """Display the tools page."""
    TEMPLATE = 'templates/tools.tmpl'


app = webapp.WSGIApplication(
    [
        ('/about', AboutPageHandler),
        ('/contact', AboutPageHandler),
        ('/disclaimer', DisclaimerPageHandler),
        ('/tools', ToolsPageHandler)
    ],
    debug=True)
