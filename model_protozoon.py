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

import ka_debug
import model_locus
import model_allele
import model_treenode
import exon_color

TRUNK = '/'

class Protozoon(model_allele.Allele):
    """
    inv: self.treenode is not None
    #CLEAR inv: isinstance(self.background, exon_color.Color)
    """

    def __init__(self):
        super(Protozoon, self).__init__(TRUNK)
        self.treenode = model_treenode.TreeNode(TRUNK)
        self.background = exon_color.Color(self.path, 0, 0, 0, 1)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.treenode, self.background]:
            result += ka_debug.dot_ref(anchor, ref)
        return result

    def __eq__(self, other):
        """Equality based on layers quantity and content."""
        equal = isinstance(other, Protozoon) \
                 and self.treenode == other.treenode \
                 and self.background == other.background
        return equal

    def randomize(self):
        """Randomize the protozoons components.
        """
        self.treenode.randomize()
        self.background.randomize()

    def mutate(self):
        """Make random changes to the protozoon.
        """
        self.treenode.mutate()
        # mutate background color
        self.background.mutate()

    def swap_places(self):
        """Delegate swapping to the protozoons components."""
        self.treenode.swap_places()

    def crossingover(self, other):
        """Returns a deep copy mixed from my protozoon and the other protozoon.
        pre: isinstance(other, Protozoon)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        # deep copy
        new_one = Protozoon()
        # crossing over the layers
        new_one.treenode = self.treenode.crossingover(other.treenode).copy()
        # crossing over the background color
        new_one.background = self.background.crossingover(other.background)
        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        ctx.scale(float(width), float(height))
#        ka_debug.matrix(ctx.get_matrix())
        ctx.translate(0.5, 0.5)
#        ka_debug.matrix(ctx.get_matrix())
        
        # paint background
#        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        rgb = self.background.rgba
        ctx.set_source_rgba(rgb[0], rgb[1], rgb[2], 1.0)
        ctx.paint()

        self.treenode.render(task, ctx, width, height)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain(self, task, formater):
        """Explain all layers and mergers."""
        # begin with header
        titel = _('protozoon ') + self.get_unique_id()
        formater.header(titel)

        # display combined layers
        width = height = 256
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        self.render(task, ctx, width, height)
        formater.surface_item(surface, _('Final image, all layers are combined'), titel)
        #explain background color
        formater.color_item(self.background, _('background color:'), alpha=False)

        # explain all layers from top to bottom
        self.treenode.explain(task, formater)

        # stop with footer
        formater.footer()

    def copy(self):
        """ The protozoons copy constructor.
        """
        new_one = Protozoon()
        new_one.treenode = self.treenode.copy()
        new_one.background = self.background.copy()
        return new_one
