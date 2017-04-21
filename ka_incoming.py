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
import ka_controller
import ka_task


INCOMMING_CAPACITY = 3

class KandidIncoming(object):
    """
    inv: 0 <= len(self.incoming_protozoans) <= self._capacity
    inv: 0 <= len(self.incoming_surface_cache) <= self._capacity
    inv: 0 <= len(self.incoming_surface_cache) <= len(self.incoming_protozoans)
    inv: self._capacity > 0
    """
    
    ids = 0

    def __init__(self, parent, widget_list):
        """
        pre: widget_list is not None
        """
        self._capacity = INCOMMING_CAPACITY
        self._widget_list = widget_list
        self._parent = parent
        self.incoming_id = []
        self.incoming_protozoans = {}
        self.incoming_surface_cache = {}
 
    def create_gui(self):
        """ """
        incomingBox = gtk.VBox()
        self._widget_list.remember('incomingBox', incomingBox)
        for index in xrange(INCOMMING_CAPACITY):
            incomingBox.pack_start(self._create_box_incomming(index), 
                                   expand=True, fill=True)
        return incomingBox

    def _create_box_incomming(self, index):
        """ """
        self._create_menue_incomming(index)
        cellBox = gtk.VBox()
        hBox = gtk.HBox()
        openPopupButton = gtk.Button()
        self._widget_list.remember('incomingbutton_' + str(index), openPopupButton)
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
        openPopupButton.add(arrow)
        hBox.pack_start(openPopupButton, expand=False, fill=False)
        cellBox.pack_start(hBox, expand=False, fill=True)
        
        aspectframe = gtk.AspectFrame()
        drawingarea = gtk.DrawingArea()
        self._widget_list.remember('incomingarea_' + str(index), drawingarea)
        aspectframe.add(drawingarea)
        cellBox.pack_start(aspectframe, expand=True, fill=True)
        return cellBox

    def _create_menue_incomming(self, index):
        """ """
        menu = gtk.Menu()
        self._widget_list.remember('incoming_menu_' + str(index), menu)

        menuitem = gtk.MenuItem(_('Zoom'))
        self._widget_list.remember('zoom_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_('Accept protozoon'))
        self._widget_list.remember('accept_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_('Decline protozoon'))
        self._widget_list.remember('decline_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        menu.show_all()
        return menu
    
    def autoconnect_events(self):
        """Create a dictionary to connect events."""
        for cell_index in xrange(self._capacity):
            six = str(cell_index)
            self._widget_list.get_widget('incomingarea_' + six) \
                        .connect('expose-event', self.on_incomingarea_expose)
            menu = self._widget_list.get_widget('incoming_menu_' + six)
            self._widget_list.get_widget('incomingbutton_' + six) \
                        .connect_object('button-press-event', self.on_incoming_popup, menu)
            self._widget_list.get_widget('zoom_menuitem_' + six) \
                                 .connect('activate', self.on_zoom_incoming)
            self._widget_list.get_widget('accept_menuitem_' + six) \
                                 .connect('activate', self.on_accept_incoming)
            self._widget_list.get_widget('decline_menuitem_' + six) \
                                 .connect('activate', self.on_decline_incoming)

    def at_index(self, index):
        iid = self.incoming_id[index] if index < len(self.incoming_id) \
                                      else -1
        protozoon = self.incoming_protozoans[iid] \
                      if self.incoming_protozoans.has_key(iid) \
                      else None
        return protozoon, iid

    def append_protozoon(self, incoming_protozoon):
        """ Append incoming protozoon and manage capacity.
        pre: incoming_protozoon is not None
        """
#        ka_debug.info('incoming: append protozoon')
        while len(self.incoming_protozoans) >= self._capacity:
            iid = self.incoming_id[0]
            del self.incoming_id[0]
            del self.incoming_protozoans[iid]
            if self.incoming_surface_cache.has_key(iid):
                del self.incoming_surface_cache[iid]
        KandidIncoming.ids += 1
        self.incoming_id.append(KandidIncoming.ids)
        self.incoming_protozoans[KandidIncoming.ids] = incoming_protozoon
        index = len(self.incoming_id) - 1
        widget_name = 'incomingarea_' + str(index)
        widget = self._widget_list.get_widget(widget_name)
        task = ka_task.GeneratorTask(self.task_render,
                                     self.on_image_completed,
                                     widget_name)
        task.start(incoming_protozoon, KandidIncoming.ids,
                   widget.allocation.width, widget.allocation.height)
#        ka_debug.info('incoming: start_calculation %ux%u, iid %u for %s' % 
#          (widget.allocation.width, widget.allocation.height,
#           KandidIncoming.ids, widget.name))

    def accept_protozoon(self, index):
        """ Move protozoon from incoming list to image population.
        pre: 0 <= index < self._capacity
        """
        protozoon, iid = self.at_index(index)
        if protozoon is not None:
#            ka_debug.info('incoming: accept incoming protozoon %u' % iid)
            del self.incoming_id[index]
            del self.incoming_protozoans[iid]
            if self.incoming_surface_cache.has_key(iid):
                del self.incoming_surface_cache[iid]
            self.update_incomming_gui()
        return protozoon

    def decline_protozoon(self, index):
        """ Remove protozoon from incoming list
        pre: 0 <= index < self._capacity
        """
        if index < len(self.incoming_protozoans):
#            ka_debug.info('incoming: decline incoming protozoon %u' % index)
            iid = self.incoming_id[index]
            del self.incoming_id[index]
            del self.incoming_protozoans[iid]
            if self.incoming_surface_cache.has_key(iid):
                del self.incoming_surface_cache[iid]
            self.update_incomming_gui()

    def task_render(self, task, *args, **kwargs):
        """Draw protozoon to surface cache.
        pre: len(args) == 4
        """
        protozoon, iid, width, height = \
                                             args[0], args[1], args[2], args[3]
#        ka_debug.info('incoming: task_render entry: ' + str(iid))
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        protozoon.render(task, ctx, width, height)
        if self.incoming_protozoans.has_key(iid):
            self.incoming_surface_cache[iid] = surface
#        ka_debug.info('incoming: task_render exit: ' + str(iid))
        return iid

    def on_image_completed(self, *args):
        """Rendering task has finished"""
#        ka_debug.info('incoming: on_image_completed: ' + str(args[0]))
        self.update_incomming_gui()

    def on_incomingarea_expose(self, widget, dummy):
        """ Repaint image of a single protozoon inside incoming area.
        pre: widget is not None
        """
#        ka_debug.info('incoming: on_incomingarea_expose: ' + widget.name)
        self.draw(ka_controller.name_to_index(widget.name), \
                           ka_controller.create_context(widget), \
                           widget.allocation.width, widget.allocation.height)

    def draw(self, index, ctx, width, height):
        """ Repaint one protozoon image inside incoming area.
        pre: 0 <= index < self._capacity
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        """
        iid = -1
        if index < len(self.incoming_id):
            iid = self.incoming_id[index]
        if self.incoming_surface_cache.has_key(iid):
            # draw protozoon to screen
            ctx.set_operator(cairo.OPERATOR_SOURCE)
            ctx.set_source_surface(self.incoming_surface_cache[iid])
            ctx.paint()
        else:
            ctx.set_source_rgba(0.65, 0.65, 0.65, 0.0)
            ctx.rectangle(0.0, 0.0, width, height)
            ctx.fill()

    def update_incomming_gui(self):
        for index in range(self._capacity):
            six = str(index)
            self._widget_list.get_widget('incomingbutton_' + six). \
                  set_sensitive(len(self.incoming_id) > index)
            self._widget_list.get_widget('incomingarea_' + six).queue_draw()

# Event handling for incoming protozoans
    def on_incoming_popup(self, widget, event):
        ka_debug.info('on_incoming_popup: ' + widget.name)
        index = ka_controller.name_to_index(widget.name)
        self._show_popup(widget, event, 'incoming_menu_'+ str(index))

    def _show_popup(self, widget, event, menu):
        ka_debug.info('%s [%s]' % (menu, widget.name))
        popup_menu = self._widget_list.get_widget(menu)
        popup_menu.popup(None, None, None, event.button, event.time)

    def on_zoom_incoming(self, menu_item):
#        ka_debug.info('on_zoom_incoming [%s]' % menu_item.parent.name)
        zoom_controller = self._parent._controller.find_page('ZoomController')
        if zoom_controller is not None:
            index = ka_controller.name_to_index(menu_item.parent.name)
            protozoon, dummy = self.at_index(index)
            zoom_controller.start_calculation(protozoon)

    def on_accept_incoming(self, menu_item):
        ka_debug.info('on_accept_incoming [%s]' % menu_item.parent.name)
        protozoon = self.accept_protozoon(
                                       ka_controller.name_to_index(menu_item.parent.name))
        if protozoon is not None:
            new_at = self._parent.model.replace(protozoon.copy())
            self._parent.start_calculation([new_at])

    def on_decline_incoming(self, menu_item):
        ka_debug.info('on_decline_incoming [%s]' % menu_item.parent.name)
        self.decline_protozoon(ka_controller.name_to_index(menu_item.parent.name))

