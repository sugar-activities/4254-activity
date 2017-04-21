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

from gettext import gettext as _

import cairo
import gtk

import ka_debug
import ka_task
import ka_controller

class ZoomController(object):
    """
    inv: self._widget_list is not None
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        self._controller = controller
        self._widget_list = widget_list
        self._surface = None
        self._protozoon = None
        self.position = 100

    def close(self):
        """Clean up"""
        pass

    def create_gui(self):
        """ """
        page = gtk.HBox()
        self._widget_list.remember('zoomPage', page)
        aspectframe = gtk.AspectFrame()
        drawingarea = gtk.DrawingArea()
        self._widget_list.remember('zoomarea', drawingarea)
        aspectframe.add(drawingarea)
        page.pack_start(aspectframe, expand=True, fill=True)
        return page, gtk.Label(_('Zoom'))

    def autoconnect_events(self):
        """Auto connect zoom view."""
        drawing_area = self._widget_list.get_widget('zoomarea')
        drawing_area.connect('expose-event', self.on_zoomarea_expose)
        drawing_area.connect('size-allocate', self.on_zoomarea_size_allocate)
        
    def localize(self):
        """A dummy"""
        pass

    def activate_gui(self):
        """Hide zoom view initially."""
        drawing_page = self._widget_list.get_widget('zoomPage')
        drawing_page.hide()

    def on_zoomarea_expose(self, widget, event):
        """ Repaint image of a single protozoon inside zoom view.
        pre: widget is not None
        """
#        ka_debug.info('on_zoomarea_expose: ' + widget.name + ' ' 
#                      + str(widget.allocation.width) 
#                      + 'x' + str(widget.allocation.height))
        # draw precalculated protozoon stored in the surface cache. 
        self._draw_from_cache(widget)

    def on_zoomarea_size_allocate(self, widget, event):
        """New size for zoom drawing area available.
        pre: widget is not None
        """
#        ka_debug.info('on_zoomarea_size_allocate: ' + widget.name + ' ' 
#                      + str(widget.allocation.width) 
#                      + 'x' + str(widget.allocation.height))
        self.start_calculation(self._protozoon)

    def on_zoom_completed(self, *args):
        """Rendering protozoon is completed."""
#        ka_debug.info('on_zoom_completed: ' + str(args[0]))
        self._controller.switch_page('ZoomController')
        self._draw_from_cache(self._widget_list.get_widget('zoomarea'))

    def task_render(self, task, *args, **kwargs):
        """Render zoom view of protozoon.
        pre: len(args) == 4
        """
        protozoon, dummy, width, height = \
                                             args[0], args[1], args[2], args[3]
#        ka_debug.info('task_render entry: ')
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(self._surface)
        protozoon.render(task, ctx, width, height)
#        ka_debug.info('task_render exit: ')

    def start_calculation(self, zoom_protozoon):
        """Start rendering of protozoon."""
        self._protozoon = zoom_protozoon
        if self._protozoon is not None:
            widget = self._widget_list.get_widget('zoomarea')
            task = ka_task.GeneratorTask(self.task_render,
                                         self.on_zoom_completed,
                                         'zoomarea')
            task.start(self._protozoon, -1,
                       widget.allocation.width, widget.allocation.height)
#            ka_debug.info('start_calculation %ux%u for %s' % 
#              (widget.allocation.width, widget.allocation.height, widget.name))

    def _draw_from_cache(self, widget):
        """Paint to drawing area.
        pre: widget is not None
        """
        if self._surface is not None:
            ctx = ka_controller.create_context(widget)
#            ctx.set_operator(cairo.OPERATOR_CLEAR)
#            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_SOURCE)
#            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.set_source_surface(self._surface)
            ctx.paint()
