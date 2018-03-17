#  This program is free software; you can redistribute it and/or modify
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
# image_fetcher.py
# Copyright (C) 2011 Simon Newton
# Handles fetching images from remote sites.

from __future__ import with_statement
import logging
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import urlfetch


class ImageFetcher(object):
  """Return the image for a model.

  TODO(simon): this is fine for now but we should switch to using task queues
  or map reduce so the fetches aren't in the serving path.
  """
  # width to resize images to
  RESIZE_WIDTH = 200

  def __init__(self):
    pass

  def FetchAndSaveImage(self, url):
    """
    Args:
      url: The url to fetch.

    Returns:
      The new blob key, or None if the fetch failed.
    """
    logging.info('fetching %s' % url)
    try:
      image_response = urlfetch.fetch(url)
    except urlfetch.Error:
      return None

    if image_response.status_code != 200:
      logging.info('image fetch failed. %s -> %d' %
                   (url, image_response.status_code))
      return None

    img = images.Image(image_response.content)
    # shrink things if needed
    if img.width > self.RESIZE_WIDTH:
      img.resize(width=self.RESIZE_WIDTH)
    # we need at least one transform, so use I'm feeling lucky :)
    img.im_feeling_lucky()
    try:
      thumbnail = img.execute_transforms(output_encoding=images.PNG)
    except SystemError, e:
      # this fires on the dev server if it can't load the PIL module
      logging.info(e)
      return None

    file_name = files.blobstore.create(mime_type='image/png')
    with files.open(file_name, 'a') as f:
      f.write(thumbnail)
    files.finalize(file_name)

    return files.blobstore.get_blob_key(file_name)
