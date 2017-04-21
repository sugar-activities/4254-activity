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
import math
import gtk

import model_history

_SCALE = math.sqrt(2.0)

class AncestorsController(object):
    """
    inv: self._controller is not None
    inv: self._widget_list is not None
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        self._controller = controller
        self._widget_list = widget_list
        self._history = model_history.KandidHistory.instance()
        self._protozoon_id = None
        self.position = 700

    def close(self):
        """Only a dummy."""
        pass

    def create_gui(self):
        """ """
        page = gtk.HBox()
        self._widget_list.remember('ancestorsPage', page)
        scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        scrolled_window.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        drawingarea = gtk.DrawingArea()
        self._widget_list.remember('ancestors_drawingarea', drawingarea)
        scrolled_window.add_with_viewport(drawingarea)
        page.pack_start(scrolled_window, expand=True, fill=True)
        return page, gtk.Label(_('Ancestors'))

    def autoconnect_events(self):
        """Auto connect ancestors view."""
        drawing_area = self._widget_list.get_widget('ancestors_drawingarea')
        drawing_area.connect('expose-event', self.on_ancestorsarea_expose)
        
    def localize(self):
        """A dummy"""
        pass

    def activate_gui(self):
        """A dummy"""

    def start_calculation(self, protozoon):
        """Start explaining of a protozoon.
        pre: protozoon is not None
        """
#        ka_debug.info('AncestorsController.start_calculation %s' % 
#                                                   (protozoon.get_unique_id()))
        self._protozoon_id = protozoon.get_unique_id()
        self._controller.switch_page('AncestorsController')

    def on_ancestorsarea_expose(self, widget, event):
        """ Repaint image of a single protozoon inside ancestors view.
        pre: widget is not None
        """
        # draw precalculated protozoon stored in the surface cache. 
#        ka_debug.info('on_ancestrosarea_expose: ' + widget.name + ' ' 
#                      + str(widget.allocation.width) 
#                      + 'x' + str(widget.allocation.height))
        ctx = widget.window.cairo_create()
        # Restrict Cairo to the exposed area; avoid extra work
        ctx.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        ctx.clip()
        ctx.set_operator(cairo.OPERATOR_SOURCE)

        # Fill the background with white
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        ctx.fill()

        self._paint_next(ctx, event.area.width/2, 3, self._protozoon_id)

    def _paint_connector(self, ctx, mx, my, x0, y0, my_parent):
        if my_parent is not None:
            ctx.set_line_width(2)
            ctx.set_source_rgb(0.2, 0.2, 0.2)
            ctx.move_to(mx, my)
            ctx.line_to(x0, y0)
            ctx.stroke()

    def _collision(self, my_id):
        if my_id is not None and self._history.contains(my_id):
            p01, p10 = None, None
            my_parents = self._history.get_parents(my_id)
            if my_parents[0] is not None and self._history.contains(my_parents[0]):
                p0 = self._history.get_parents(my_parents[0])
                if p0[1] is not None and self._history.contains(p0[1]):
                    p01 = self._history.get_parents(p0[1])
            if my_parents[1] is not None and self._history.contains(my_parents[1]):
                p1 = self._history.get_parents(my_parents[1])
                if p1[0] is not None and self._history.contains(p1[0]):
                    p10 = self._history.get_parents(p1[0])
            distance = 1.0 if p01 is None or p10 is None else _SCALE
            return 0.5 * distance * \
                (self._collision(my_parents[0]) + self._collision(my_parents[1]))
        else:
            return 0.5
            
    def _paint_next(self, ctx, xpos, ypos, my_id):
        if my_id is not None and self._history.contains(my_id):
#            ka_debug.info('my_id: ' + my_id) 
            surface = self._history.get_surface(my_id)
            width = surface.get_width() if surface is not None else 200
            height = surface.get_height() if surface is not None else 200

            if self._history.contains(my_id):
                mx, my = xpos, ypos+height
                x0, y0 = xpos-(self._collision(my_id)*width+23), ypos+height+23
                x1, y1 = xpos+(self._collision(my_id)*width+23), ypos+height+23
                my_parents = self._history.get_parents(my_id)
                self._paint_connector(ctx, mx, my, x0, y0, my_parents[0])
                self._paint_connector(ctx, mx, my, x1, y1, my_parents[1])

                ctx.save()
#                ka_debug.matrix_s(ctx.get_matrix())
                ctx.scale(1.0/_SCALE, 1.0/_SCALE)
#                ka_debug.matrix(ctx.get_matrix())
                self._paint_next(ctx, _SCALE*x0, _SCALE*y0, my_parents[0])
                self._paint_next(ctx, _SCALE*x1, _SCALE*y1, my_parents[1])
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()

            if surface is not None:
#                ka_debug.info('(xpos, ypos): %d, %d' % (xpos, ypos)) 
                ctx.save()
#                ka_debug.matrix_s(ctx.get_matrix())
                ctx.set_operator(cairo.OPERATOR_SOURCE)
                ctx.rectangle(xpos-width/2, ypos, width, height)
                ctx.clip()
                ctx.set_source_surface(surface, xpos-width/2, ypos)
                ctx.paint()
#                ctx.reset_clip() #TODO Required argument 'cr' not found
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()
