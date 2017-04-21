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

import ka_extensionpoint
import ka_debug

class KandidController(object):
    """
    inv: self._widget_list is not None
    inv: self._activity_root is not None
    """

    def __init__(self, widget, activity_root, started_anew):
        """
        pre: widget is not None
        """
        self._widget = widget
        self._widget_list = widget.widget_list
        self._activity_root = activity_root        
        self._started_anew = started_anew

        self._pages = []
        

    @staticmethod
    def numeric_compare(page1, page2):
        """
        pre: page1 is not None
        pre: page2 is not None
        """
        return page1.position - page2.position

    def create_pages(self):
        """
        Add optional pages to kandid notebook
        """
        page_names = ka_extensionpoint.list_extensions('page')
        for name in page_names:
            page_controller = ka_extensionpoint.create(name, self,
                                                       self._widget_list,
                                                       self._activity_root,
                                                       self._started_anew)
            self._pages.append(page_controller)
        self._pages.sort(cmp=KandidController.numeric_compare)
        for page_controller in self._pages:
            self._widget._notebook.append_page(*page_controller.create_gui())
            page_controller.autoconnect_events()
            page_controller.localize()
            page_controller.activate_gui()

    def find_page(self, page_name):
        """
        pre: page_name is not None and len(page_name) > 1
        """
        for page_controller in self._pages:
            pattern1 = "<class 'ep_page_"
            pattern2 = "." + page_name + "'>"
            type_str = str(type(page_controller))
            if type_str.startswith(pattern1) and type_str.endswith(pattern2):
                return page_controller
        ka_debug.err('Missing ' + page_name)
        return None
    
    def find_page_number(self, page_name):
        """
        pre: page_name is not None and len(page_name) > 1
        """
        for page_number, page_controller in enumerate(self._pages):
            pattern1 = "<class 'ep_page_"
            pattern2 = "." + page_name + "'>"
            type_str = str(type(page_controller))
            if type_str.startswith(pattern1) and type_str.endswith(pattern2):
                return page_number
        return -1
        
    
    def switch_page(self, page_name):
        """
        pre: page_name is not None and len(page_name) > 1
        pre: self.find_page(page_name) is not None
        """
        for page_number, page_controller in enumerate(self._pages):
            pattern1 = "<class 'ep_page_"
            pattern2 = "." + page_name + "'>"
            type_str = str(type(page_controller))
            if type_str.startswith(pattern1) and type_str.endswith(pattern2):
                self._widget_list.get_widget('kandidNotebook'). \
                                                   set_current_page(page_number)
                return
    
    def close(self):
        """Clean up on close"""
        for page in self._pages:
            page.close()

def name_to_index(name):
    """Extract index from last part of a name.
    Parts are separated by _.
    pre: name[-1].isdigit()
    post: __return__ >= 0
    """
    return int(name.rsplit('_')[-1])

def create_context(widget):
    """ Create cairo context for widget.
    pre: widget is not None
    pre: widget.window is not None
    """
    ctx = widget.window.cairo_create()
    ctx.rectangle(0, 0, \
                  widget.allocation.width, widget.allocation.height)
    ctx.clip()
    return ctx
