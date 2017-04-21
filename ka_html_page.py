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

import os
import sys
import traceback
import webbrowser

import ka_debug

try:
    from sugar import env
    # HACK: Needed by http://dev.sugarlabs.org/ticket/456
    import gnome
    gnome.init('Hulahop', '1.0')
    
    import hulahop
    hulahop.set_app_version(os.environ['SUGAR_BUNDLE_VERSION'])
    hulahop.startup(os.path.join(env.get_profile_path(), 'gecko'))
    from hulahop.webview import WebView
except:
    ka_debug.err('failed importing hulahop [%s] [%s]' % \
           (sys.exc_info()[0], sys.exc_info()[1]))
    traceback.print_exc(file=sys.__stderr__)

class HtmlPage(object):
    """
    inv: self._widget_list is not None
    inv: self._widget_list is not None
    """

    def __init__(self, controller, uri, parent_widget, widget_list):
        """
        pre: parent_widget is not None
        pre: widget_list is not None
        """
        self._controller = controller
        self._widget_list = widget_list
        self._parent_widget = parent_widget
        self._htmlview = None
        self._uri = '' if uri is None else uri 
        try:
            # The XOCom object helps us communicate with the browser
            # This uses web/index.html as the default page to load
#!!            from XOCom import XOCom
#!!            self.xocom = XOCom(self.control_sending_text) #REMEMBER THAT I HAVE STILL TO SEND THE ARGUMENT IN THE XOCOM CLASS
#!!            self._htmlview = self.xocom.create_webview()
            self._htmlview = WebView()
        except:
            ka_debug.err('failed creating hulahop [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)

    def autoconnect_events(self):
        """Auto connect introduction view."""
        self._widget_list.get_widget('kandidNotebook') \
                          .connect('switch-page', self.on_notebook_switch_page)
        
    def localize(self):
        """A dummy"""
        pass

    def activate_gui(self):
        """Insert HTML view."""
        if self._htmlview is not None:
            intro_scrolled = self._widget_list.get_widget(self._parent_widget)
            intro_scrolled.add_with_viewport(self._htmlview)

    def set_uri(self, uri):
        """ """
        self._uri = '' if uri is None else uri 

    def on_notebook_switch_page(self, *args):
        """Test if introduction page will be displayed.
        Lazy evaluation to fill the page with text.
        pre: len(args) >= 3
        """
        visible = args[2] == self._controller.find_page_number(self.__class__.__name__)
#        ka_debug.info('on_notebook_switch_page %s %s' % (visible, args[2]))
        if visible and len(self._uri) > 0: 
            if ka_debug.locale_testrun:
                # Only for testing on my computer
                result = webbrowser.open(self._uri)
                ka_debug.info('webbrowser.open: [%s] %s' % 
                                                 (self._uri, str(result)))
            if self._htmlview is not None:
                self._htmlview.load_uri(self._uri)
