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

import traceback
import sys
import gtk

import ka_debug
import ka_widget

class GettingstartedController(object):
    """
    inv: self._widget_list is not None
    inv: self._controller is not None
    """
    
    _getting_started_text = """Getting started with Kandid:

Kandid is a system to evolve graphical forms and color combinations. In subsequent generations Kandid creates random images. These images are proposals. You must rank these automatically generated images.

Kandid uses a simulated evolution without a fitness function. A cybernetic system has no aesthetic feeling. You select favorite images to give them a higher chance to reproduce. Over some generation you can find 'cool' looking images.
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        self._controller = controller
        self._widget_list = widget_list
        self.position = 400

    def close(self):
        """Clean up"""
        pass

    def create_gui(self):
        """ """
        inner_border = 10
        page = gtk.HBox()
        page.set_border_width(30)
        self._widget_list.remember('startHpaned', page)
        teaserBox = gtk.VBox()
        teaserBox.set_border_width(inner_border)
        
        try:        
            image_file = ka_widget.KandidWidget.get_introimage_path() \
                         + 'kandid-teaser.jpg'
            image = gtk.Image()
            image.set_from_file(image_file)
            teaserBox.pack_start(image, expand=False, fill=False)
        except:
            ka_debug.err('locating intro image failed [%s] [%s]' % \
                       (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        page.pack_start(teaserBox, expand=False, fill=False)

        controlBox = gtk.VBox()
        controlBox.set_border_width(inner_border)
        controlBox.pack_start(gtk.Label(''), expand=True, fill=True)
        readintroLinkbutton = gtk.Button('')
        readintroLinkbutton.set_label(_('Read the Introduction'))
        self._widget_list.remember('readintroLinkbutton', readintroLinkbutton)
        controlBox.pack_start(readintroLinkbutton, expand=False, fill=False)
        
        controlBox.pack_start(gtk.Label(''), expand=True, fill=True)
        startnewLinkbutton = gtk.Button('')
        startnewLinkbutton.set_label(_('Show image population'))
        self._widget_list.remember('startnewLinkbutton', startnewLinkbutton)
        controlBox.pack_start(startnewLinkbutton, expand=False, fill=False)
        teaserBox.pack_start(controlBox, expand=False, fill=False)
        
        textBox = gtk.VBox()
        textBox.set_border_width(inner_border)
        scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self._widget_list.remember('start_scrolledwindow', scrolled_window)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        self._widget_list.remember('gettingstarted_textview', textview)
        textview.set_wrap_mode(gtk.WRAP_WORD)
        textview.set_editable(False)
        textview.set_left_margin(10)
        textview.set_right_margin(10)
        textview.set_border_width(3)
        textview.set_sensitive(False)
        scrolled_window.add(textview)
        textBox.pack_start(scrolled_window, expand=True, fill=True)
        page.pack_start(textBox, expand=True, fill=True)
        
        return page, gtk.Label(_('Getting started'))

    def autoconnect_events(self):
        """Auto connect status view."""
        self._widget_list.get_widget('readintroLinkbutton') \
                                 .connect('clicked', self.on_readintro)
        self._widget_list.get_widget('startnewLinkbutton') \
                                 .connect('clicked', self.on_startnew)

    def localize(self):
        try:
            textview = self._widget_list.get_widget('gettingstarted_textview')
            buf = textview.get_buffer()
            translated = _('getting_started')
            translated = translated if not translated == 'getting_started' \
                            else GettingstartedController._getting_started_text
            buf.delete(buf.get_start_iter(), buf.get_end_iter())
#!!            buf.insert(buf.get_end_iter(), '\n')
#!!            buf.insert(buf.get_end_iter(), '\n')
            buf.insert(buf.get_end_iter(), translated)
        except:
            ka_debug.err('localizing page "getting started" failed [%s] [%s]' % \
                       (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)

    def activate_gui(self):
        """A dummy"""
        pass

    def on_readintro(self, args):
        """Show introduction page.
        """
#        ka_debug.info('on_readintro')
        self._controller.switch_page('IntroController')

    def on_startnew(self, args):
        """Show population page.
        """
#        ka_debug.info('on_startnew')
        self._controller.switch_page('PopulationController')
