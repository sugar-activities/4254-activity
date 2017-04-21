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

import os.path
import gtk

import ka_debug
import ka_extensionpoint
import ka_task
import ka_html_page

class DetailsController(ka_html_page.HtmlPage):
    """
    inv: self._produced_files_list is not None
    inv: self._activity_root is not None
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        super(DetailsController, self).__init__(controller,
                                                None,
                                                'details_scrolledwindow',
                                                widget_list)
        self._controller = controller
        self._produced_files_list = []
        self._activity_root = controller._activity_root
        self.position = 600

    def create_gui(self):
        """ """
        page = gtk.HBox()
        self._widget_list.remember('detailsPage', page)
        scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self._widget_list.remember('details_scrolledwindow', scrolled_window)
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        page.pack_start(scrolled_window, expand=True, fill=True)
        return page, gtk.Label(_('Details'))

    def close(self):
        """Clean up"""
        files = [fp for fp in self._produced_files_list if os.path.isfile(fp)]
        for file_path in files:
#            print 'unlink', file_path
            os.unlink(file_path)
        folders = [fp for fp in self._produced_files_list if os.path.isdir(fp)]
        for file_path in folders:
#            print 'rmdir', file_path
            os.rmdir(file_path)

    def on_switch_page(self):
        """Only a dummy."""
        pass

    def task_explain(self, task, *args, **kwargs):
        """Render zoom view of protozoon.
        pre: len(args) >= 1
        """
        protozoon = args[0]
#        ka_debug.info('task_explain entry: ')
        folder = os.path.join(self._activity_root, 'tmp')
        ep_key = 'html'
        formater = ka_extensionpoint.create('formater_'+ep_key,
                                            'index',
                                            protozoon.get_unique_id(),
                                            folder)
        protozoon.explain(task, formater)
        file_path = formater.get_absolutename(ep_key)
        formater.write_html_file(file_path)
        self._produced_files_list.extend(formater.produced_files_list)
        self._produced_files_list.append(formater.get_pathname())
        self.set_uri('file://' + file_path)
#        ka_debug.info('task_explain exit:  %s' % (self._uri))

    def start_calculation(self, protozoon):
        """Start explaining of a protozoon.
        pre: protozoon is not None
        """
#        ka_debug.info('DetailsController.start_calculation %s' % 
#                                                   (protozoon.get_unique_id()))
        task = ka_task.GeneratorTask(self.task_explain,
                                     self.on_explain_completed,
                                     'explain')
        task.start(protozoon)

    def on_explain_completed(self, *args):
        """HTML file and PNGs are created. Time to switch to a browser widget.
        """
#        ka_debug.info('on_explain_completed %s' % (self._uri))
        self._controller.switch_page('DetailsController')
