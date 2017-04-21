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

class KandidHistory(object):
    """
    """
    _history = None
    _icon_width = 48
    _newest = 1

    class Item(object):
        def __init__(self, init_parent1_id, init_parent2_id):
            self.ref_count = 0
            self.surface = None
            self.parent1_id = init_parent1_id
            self.parent2_id = init_parent2_id
            self.old = 0

        def __str__(self):
            return '(' \
                + str(self.ref_count) + ', ' \
                + (self.parent1_id if self.parent1_id is not None else 'None') \
                + ', ' \
                + (self.parent2_id if self.parent2_id is not None else 'None') \
                + ', ' \
                + (str(self.surface) if self.surface is not None else 'None') \
                + ')'

    def __init__(self):
        """
        inv: self.parents is not None
        """
        self.parents = {}
        self.assumed_icon_width = KandidHistory._icon_width
        self.surfaces_referenced = 0
 
    @staticmethod
    def instance():
        if KandidHistory._history is None:
            KandidHistory._history = KandidHistory()
        return KandidHistory._history
    
    def clear(self):
        self.parents = {}
        self.surfaces_referenced = 0

    def rember_parents(self, my_id, parent1_id, parent2_id):
        """Remember the ids of my parents.
        pre: my_id is not None and my_id.startswith('_')
        pre: parent1_id is not None and parent1_id.startswith('_')
        pre: parent2_id is not None and parent2_id.startswith('_')
        pre: not my_id == parent1_id
        pre: not my_id == parent2_id
        """
        if my_id not in self.parents:
            self.parents[my_id] = KandidHistory.Item(parent1_id, parent2_id)
        else:
            self.parents[my_id].parent1_id = parent1_id
            self.parents[my_id].parent2_id = parent2_id
        if parent1_id in self.parents:
            self.parents[parent1_id].ref_count += 1
        if parent2_id in self.parents:
            self.parents[parent2_id].ref_count += 1

    def link_surface(self, my_id, my_surface):
        """Link an id with an surface
        pre: my_id is not None and my_id.startswith('_')
        pre: my_surface is not None
        """
        if my_id not in self.parents:
            self.parents[my_id] = KandidHistory.Item(None, None)
#!!            self.parents[my_id].ref_count += -1
        if self.parents[my_id].surface is None:
            self.surfaces_referenced += 1
        self.parents[my_id].surface = my_surface
        self.parents[my_id].old = KandidHistory._newest
        KandidHistory._newest += 1
        self._limit_memory_usage()
        
    def _limit_memory_usage(self):
        """
        limit memory usage, forget old surfaces
        """
        while self.surfaces_referenced > 25:
            min_id, min_old = None, 2**31
            for key, parent in self.parents.iteritems():
                if parent.surface is not None and parent.old < min_old:
                    min_id, min_old  = key, parent.old
            if min_id is not None:
                self.parents[min_id].surface = None
                self.surfaces_referenced -= 1
                          
    def unlink(self, my_id):
        """Forget an id and free the linked surface.
        pre: my_id is not None and my_id.startswith('_')
        """
        if my_id in self.parents:
            self.parents[my_id].ref_count -= 1
            if self.parents[my_id].ref_count < 0:
                my_parents = self.get_parents(my_id)
                parent1_id, parent2_id = my_parents[0], my_parents[1]
                if parent1_id in self.parents:
                    self.unlink(parent1_id)
                if parent2_id in self.parents:
                    self.unlink(parent2_id)
                if self.parents[my_id].surface is not None:
                    self.surfaces_referenced -= 1
                del self.parents[my_id]

    def contains(self, my_id):
        """Returns True if my_id can be found.
        pre: my_id is not None and my_id.startswith('_')
        """
        return my_id in self.parents

    def get_parents(self, my_id):
        """Return ids of both parents
        pre: my_id is not None and my_id.startswith('_')
        pre: self.parents.has_key(my_id)
        post: len(__return__) == 2
        """
        my_parents = self.parents[my_id]
        return ( my_parents.parent1_id, my_parents.parent2_id )

    def get_surface(self, my_id):
        """
        pre: my_id is not None and my_id.startswith('_')
        """
        return self.parents[my_id].surface if my_id in self.parents else None

#    def get_pixbuf(self, my_id):
#        """
#        pre: my_id is not None and my_id.startswith('_')
#        """
#        pixbuf, surface = None, self.get_surface(my_id)
#        if surface is not None:
#            width, height = surface.get_width(), surface.get_height()
#            pixmap = gtk.gdk.Pixmap (None, width, height, 24)
#            cr = pixmap.cairo_create()
#            cr.set_source_surface(surface, 0, 0)
#            cr.paint()
#            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
#            pixbuf = pixbuf.get_from_drawable(pixmap, gtk.gdk.colormap_get_system(), 0, 0, 0, 0, width, height)
#        return pixbuf

#    def get_pixbuf(self, my_id):
#        """
#        pre: my_id is not None and my_id.startswith('_')
#        """
#        pixbuf, surface = None, self.get_surface(my_id)
#        if surface is not None:
#            filename = '/dev/shm/' + my_id + '.png'
#            surface.write_to_png(filename)
#            pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
#        return pixbuf

#    def get_treestore(self, my_id):
#        """
#        pre: my_id is not None and my_id.startswith('_')
#        """
#        treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str)
#        self.assumed_icon_width, icon = self._draw_icon(my_id)
#        it = treestore.append(None, [icon, my_id])
#        self._get_treestore0(my_id, treestore, it)
#        return treestore
#
#    def _get_treestore0(self, my_id, treestore, it):
#        """
#        pre: my_id is not None and my_id.startswith('_')
#        pre: treestore is not None
#        pre: it is not None
#        """
#        if my_id is not None and self.contains(my_id): 
#            my_parents = self.get_parents(my_id)
#            parent1_id, parent2_id = my_parents[0], my_parents[1]
#            self._append_node(my_id, parent1_id, treestore, it)
#            self._append_node(my_id, parent2_id, treestore, it)
#
#    def _append_node(self, my_id, parent_id, treestore, it):
#        if parent_id is not None:
#            title = parent_id if self.parents[my_id].surface is not None \
#                        else parent_id + _('Sorry, can not remember the image')
#            child_it = treestore.append(it, [self._draw_icon(parent_id)[1],
#                                             title])
#            self._get_treestore0(parent_id, treestore, child_it)
#
#    def _draw_icon(self, my_id):
#        """
#        post: len(__return__) == 2
#        post: __return__[0] >= 0
#        """
#        pixbuf = None
#        width = KandidHistory._icon_width
#        if my_id in self.parents:
#            surface = self.parents[my_id].surface
#            if surface is not None:
#                width, h = surface.get_width(), surface.get_height()
#                pixmap = gtk.gdk.Pixmap (None, width, h, 24)
#                cr = pixmap.cairo_create()
#                cr.set_source_surface(surface, 0, 0)
#                cr.paint()
#                pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, h)
#                pixbuf = pixbuf.get_from_drawable(pixmap, gtk.gdk.colormap_get_system(), 0, 0, 0, 0, width, h)
#        if pixbuf is None:
#            theme = gtk.icon_theme_get_default()
#            pixbuf = theme.load_icon(gtk.STOCK_DELETE, KandidHistory._icon_width, 0)
#        return width, pixbuf
