# coding: UTF-8
# Copyright 2009, 2010 Thomas Jourdan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os.path
import base64
import sys

import cairo
from sugar.datastore import datastore

import ka_debug
import ka_task

_THUMB_SIZE = 100

class PngExporter(object):
    """
    """
    def __init__(self, protozoon, init_activity_root):
        """
        inv: self._protozoon is not None
        inv: self._activity_root is not None
        """
        self._protozoon = protozoon
        self._activity_root = init_activity_root        
        self._export_surface = None
        self._thumb_surface = None

    def export(self, width, height):
        """
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        task = ka_task.GeneratorTask(self.task_render, 
                                     self.on_render_completed,
                                     'export_png'+self._protozoon.get_unique_id())
        task.start(self._protozoon, -1, width, height)
        ka_debug.info('export: start_calculation %ux%u for %s' %  
                            (width, height, self._protozoon.get_unique_id()))

    def task_render(self, task, *args, **kwargs):
        """Render bitmap for exporting protozoon.
        pre: len(args) == 4
        """
        protozoon, dummy, width, height = \
                                             args[0], args[1], args[2], args[3]
        ka_debug.info('export: task_render entry: ')
        self._export_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(self._export_surface)
        protozoon.render(task, ctx, width, height)

        self._thumb_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                 _THUMB_SIZE, _THUMB_SIZE)
        ctx = cairo.Context(self._thumb_surface)
        protozoon.render(task, ctx, _THUMB_SIZE, _THUMB_SIZE)
        ka_debug.info('export: task_render exit: ')

    def on_render_completed(self, *args):
        """Rendering protozoon is completed.
        pre: self._export_surface is not None
        pre: self._thumb_surface is not None
        """
        ka_debug.info('export: on_render_completed: ' + str(args[0]))
        unique_id = 'kandidimage' + self._protozoon.get_unique_id()
        export_filename = unique_id + '.png'
        export_path = os.path.join(self._activity_root, 'instance', export_filename)
        
        # Create a datastore object
        file_dsobject = datastore.create()

        # Write any metadata (here we specifically set the title of the file
        # and specify that this is a portable network graphics file). 
        file_dsobject.metadata['title'] = 'Kandid Image ' + \
                                            self._protozoon.get_unique_id()[1:]
        file_dsobject.metadata['mime_type'] = 'image/png'

        #Write the actual file to the data directory of this activity's root. 
        try:
            self._export_surface.write_to_png(export_path)
        except:
            ka_debug.err('export: failed exporting to [%s] [%s] [%s]' % \
                   (export_path, sys.exc_info()[0], sys.exc_info()[1]))

        #insert thumbnail image into metadata
        thumb_filename = unique_id + '.thumb.png'
        thumb_path = os.path.join(self._activity_root, 'instance', thumb_filename)
        try:
            self._thumb_surface.write_to_png(thumb_path)
            thumb_in = open(thumb_path, 'rb')
            file_dsobject.metadata['preview'] = \
                                             base64.b64encode(thumb_in.read())
            thumb_in.close()
            os.unlink(thumb_path)
        except:
            ka_debug.err('export: failed creating preview image [%s] [%s] [%s]' % \
                   (thumb_path, sys.exc_info()[0], sys.exc_info()[1]))

        #Set the file_path in the datastore.
        file_dsobject.set_file_path(export_path)
        datastore.write(file_dsobject)
        file_dsobject.destroy()
