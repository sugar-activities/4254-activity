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

import ka_debug
import ka_widget
import ka_html_page


class IntroController(ka_html_page.HtmlPage):
    """
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: widget_list is not None
        """
        file_uri = 'file://' \
                   + ka_widget.KandidWidget.get_localized_path() \
                   + 'intro.html'
        super(IntroController, self).__init__(controller,
                                              file_uri,
                                              'intro_scrolledwindow',
                                              widget_list)
        self.position = 500

    def close(self):
        """Clean up"""
        pass

    def create_gui(self):
        """ """
        page = gtk.HBox()
        self._widget_list.remember('introPage', page)
        scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self._widget_list.remember('intro_scrolledwindow', scrolled_window)
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        page.pack_start(scrolled_window, expand=True, fill=True)
        return page, gtk.Label(_('Introduction'))
