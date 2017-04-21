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

import gtk
import os

import ka_debug
import ka_extensionpoint

class WidgetList():
    """ """
    def __init__(self):
        self._list = {}

    def remember(self, widget_name, widget):
        """
        pre: widget_name is not None
        pre: widget is not None
        pre: widget_name not in self._list
        """
        widget.set_name(widget_name)
        self._list[widget_name] = widget

    def get_widget(self, widget_name):
        """
        pre: widget_name in self._list
        post: __return__ is not None
        """
        if widget_name in self._list:
            return self._list[widget_name]
        ka_debug.err('missing: ' + widget_name)
        return None


class KandidWidget(object):
    """ """

    def __init__(self):
        self.widget_list = WidgetList()
        self._notebook = None

    def get_widget_tree(self):
        """
        post: __return__ is not None
        """
        if self._notebook is None:
            # Create GUI
            self._notebook = gtk.Notebook()
            self.widget_list.remember('kandidNotebook', self._notebook)
            self._notebook.set_tab_pos(gtk.POS_TOP)
        return self._notebook

    def get_widget(self, widget_name):
        return self.widget_list.get_widget(widget_name)
             
    @staticmethod
    def get_localization():
        """ returns localization and territory
        post: len(__return__[0]) >= 2
        """
        languages = []
        territory, locale= '', ''
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                for lang in languages:
                    pos = lang.find('.')
                    if pos >= 0:
                        lang = lang[:pos]
                    pos = lang.find('_')
                    if pos >= 0:
                        locale = lang[:pos]
                        territory = lang[pos+1:]
                    else:
                        locale = lang
                break
        ka_debug.info('languages: %s "%s" "%s"' % (languages, locale, territory)) 
        return locale, territory

    @staticmethod
    def get_localized_path():
        """Try to find the LOCALE folder. Default folder is locale/en/"""
        locale, territory = KandidWidget.get_localization()
        bundle_path = ka_extensionpoint.get_bundle_path()
        path_to_file = os.path.join(bundle_path,
                                 'locale',
                                 locale + '_' + territory,
                                 '')
        if not os.path.isfile(path_to_file):
            path_to_file = os.path.join(bundle_path,
                                     'locale',
                                     locale,
                                     '')
        if not os.path.isfile(path_to_file):
            path_to_file = os.path.join(bundle_path,
                                     'locale',
                                     'en',
                                     '')
        return path_to_file

    @staticmethod
    def get_introimage_path():
        """Try to locate the intro folder"""
        bundle_path = ka_extensionpoint.get_bundle_path()
        path_to_file = os.path.join(bundle_path,
                                 'intro',
                                 '')
        return path_to_file
