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

import gtk
import gtk.gdk
import gobject

import ka_debug
import ka_status
import ka_preference

class StatusController(object):
    """
    inv: self._widget_list is not None
    inv: self._status is not None
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        self._widget_list = widget_list
        self._visible = False
        self._status = ka_status.Status.instance()
        self.position = 900

    def close(self):
        """Clean up"""
        pass

    def create_gui(self):
        """ """
        page = gtk.VBox()

        param_panel = gtk.HBox()
        param_panel.set_border_width(10)
        label1 = gtk.Label(_('Size of the exported image in pixels: '))
        param_panel.pack_start(label1, expand=False, fill=False)
        cb = gtk.combo_box_new_text()
        cb.connect("changed", self.on_changed)
        cb.append_text('200 * 200')
        cb.append_text('400 * 400')
        cb.append_text('600 * 600')
        cb.append_text('1000 * 1000')
        preference = ka_preference.Preference.instance()
        export_size = preference.get(ka_preference.EXPORT_SIZE)
        if export_size[0] == 400:
            cb.set_active(1)
        elif export_size[0] == 600:
            cb.set_active(2)
        elif export_size[0] == 1000:
            cb.set_active(3)
        else:
            cb.set_active(0)
        param_panel.pack_start(cb, expand=False, fill=False)
        page.pack_start(param_panel, expand=False, fill=True)
        
        self._widget_list.remember('statusPage', page)
        scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        textview = gtk.TextView()
        self._widget_list.remember('statusTextview', textview)
        textview.set_editable(False)
        scrolled_window.add(textview)
        page.pack_start(scrolled_window, expand=True, fill=True)

        return page, gtk.Label(_('Status'))

    def autoconnect_events(self):
        """Auto connect status view."""
        self._widget_list.get_widget('kandidNotebook') \
                           .connect('switch-page', self.on_notebook_switch_page)
        statusview = self._widget_list.get_widget('statusTextview')
        statusview.connect('visibility-notify-event',
                           self.on_statuspage_visibility_notify_event)
        gobject.timeout_add(1000, self.on_timer)
        
    def localize(self):
        """A dummy"""
        pass

    def activate_gui(self):
        """A dummy"""
        pass

    def refresh(self):
        """Replace status text completely."""
        self._status.scan_os_status()
        statusview = self._widget_list.get_widget('statusTextview')
        buf = statusview.get_buffer()
        buf.delete(buf.get_start_iter(), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), self._status.recall())

    def on_timer(self, *args):
        """Process next update cycle."""
        if self._visible:
            self.refresh()
        gobject.timeout_add(1000, self.on_timer)

    def on_statuspage_visibility_notify_event(self, *args):
        """
        pre: len(args) >= 2
        pre: isinstance(args[1], gtk.gdk.Event)
        """
        self._visible = not args[1].state == gtk.gdk.VISIBILITY_FULLY_OBSCURED
#        ka_debug.info('on_statuspage_visibility_notify_event %s %s' % (self._visible, args[1].state))
        return False

    def on_notebook_switch_page(self, *args):
        """Test if status page will be displayed.
        pre: len(args) >= 3
        """
        self._visible = False
#        ka_debug.info('on_notebook_switch_page %s %s' % (self._visible, args[2]))

    def on_changed(self, widget):
        index = widget.get_active()
        ka_debug.info('on_changed %d' % (index))
        preference = ka_preference.Preference.instance()
        if index == 0:
            preference.set(ka_preference.EXPORT_SIZE, (200, 200))
        elif index == 1:
            preference.set(ka_preference.EXPORT_SIZE, (400, 400))
        elif index == 2:
            preference.set(ka_preference.EXPORT_SIZE, (600, 600))
        elif index == 3:
            preference.set(ka_preference.EXPORT_SIZE, (1000, 1000))
        preference.store()
        
