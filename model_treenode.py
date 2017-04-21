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

import sys
import traceback
import cairo
import random

import ka_debug
import ka_factory
import model_random
import model_constraintpool
import model_locus
import model_allele
import exon_color

LAYERTYPE_CONSTRAINT = 'layertypeconstraint'
NUMBER_OF_LAYERS_CONSTRAINT = 'layernumberofconstraint'
MERGERTYPE_CONSTRAINT = 'mergertypeconstraint'
MODIFIERTYPE_CONSTRAINT = 'modifiertypeconstraint'

class TreeNode(model_allele.Allele):
    """
    inv: (self.left_treenode is None) or isinstance(self.left_treenode, TreeNode)
    inv: (self.right_treenode is None) or isinstance(self.right_treenode, TreeNode)
    inv: self.layer is not None
    inv: self.merger is not None
    inv: self.modifier is not None
    """

    cdef = [{'bind'  : LAYERTYPE_CONSTRAINT,
             'name'  : 'Permitted layer types',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('layer').keys()
            },
            {'bind'  : NUMBER_OF_LAYERS_CONSTRAINT,
             'name'  : 'Number of layers',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 4,
            },
            {'bind'  : MERGERTYPE_CONSTRAINT,
             'name'  : 'Permitted merging strategies for layers',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('merger').keys()
            },
            {'bind'  : MODIFIERTYPE_CONSTRAINT,
             'name'  : 'Permitted merging strategies for layers',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('modifier').keys()
            },
           ]
    
    def __init__(self, trunk):
        super(TreeNode, self).__init__(trunk)
        self.left_treenode = None
        self.right_treenode = None
        self.left_background = exon_color.Color(self.path, 0, 0, 0, 1)
        self.right_background = exon_color.Color(self.path, 0, 0, 0, 1)
        layer_factory = ka_factory.get_factory('layer')
        self.layer = layer_factory.create(layer_factory.keys()[0], self.path)
        merger_factory = ka_factory.get_factory('merger')
        self.merger = merger_factory.create(merger_factory.keys()[0], self.path)
        modifier_factory = ka_factory.get_factory('modifier')
        self.modifier = modifier_factory.create(modifier_factory.keys()[0], self.path)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.left_treenode, self.right_treenode, 
                    self.layer, self.merger, self.modifier,
                    self.left_background, self.right_background]:
            if ref is not None:
                result += ka_debug.dot_ref(anchor, ref)
        return result

    @staticmethod
    def _paint_checker_board(ctx):
        """Paint a checker board background"""
        steps = 16
        delta = (1.0) / (1.0 * steps)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        for row in range(steps):
            for col in range(steps):
                ctx.rectangle(col * delta - 0.5, row * delta - 0.5,
                              delta, delta)
                if (col + row) % 2 == 0:
                    ctx.set_source_rgb(0.4, 0.4, 0.4)
                else:
                    ctx.set_source_rgb(0.6, 0.6, 0.6)
                ctx.fill()

    def __eq__(self, other):
        """Equality based on layers quantity and content."""
        equal = isinstance(other, TreeNode) \
                 and self.left_treenode == other.left_treenode \
                 and self.right_treenode == other.right_treenode \
                 and self.left_background == other.left_background \
                 and self.right_background == other.right_background \
                 and self.layer == other.layer \
                 and self.merger == other.merger \
                 and self.modifier == other.modifier
#        if not equal and isinstance(other, TreeNode):
#            print self.__class__
#            print self.left_treenode == other.left_treenode
#            print self.right_treenode == other.right_treenode
#            print self.left_background == other.left_background
#            print self.right_background == other.right_background
#            print self.layer == other.layer
#            print self.merger == other.merger
#            print self.modifier == other.modifier
#            print equal
        return equal

    def randomize(self):
        """Randomize the tree nodes components.
        post: self.layer is not None
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()

        self.left_background.randomize()
        self.right_background.randomize()
        
        # create layer
        layer_factory = ka_factory.get_factory('layer')
        layertype_constraint = cpool.get(self, LAYERTYPE_CONSTRAINT)
        self.layer = layer_factory.create_random(layertype_constraint,
                                                       self.path)
        self.layer.randomize()

        # create strategy for merging 'left' and 'right' layer
        merger_factory = ka_factory.get_factory('merger')
        mergertype_constraint = cpool.get(self, MERGERTYPE_CONSTRAINT)
        self.merger = merger_factory.create_random(mergertype_constraint,
                                                       self.path)
        self.merger.randomize()

        # create strategy for modifying stacked layers
        modifier_factory = ka_factory.get_factory('modifier')
        modifiertype_constraint = cpool.get(self, MODIFIERTYPE_CONSTRAINT)
        self.modifier = modifier_factory.create_random(modifiertype_constraint,
                                                       self.path)
        self.modifier.randomize()

        number_of_constraint = cpool.get(self, NUMBER_OF_LAYERS_CONSTRAINT)
        depth = _count_slash(self.path)
        if (depth <= number_of_constraint[0] or \
           (depth > number_of_constraint[0] and random.choice([False, True]))) \
           and  depth <= number_of_constraint[1]:
            self.left_treenode = TreeNode(self.path)
            self.left_treenode.path += 'Left'
            self.left_treenode.randomize()
        if (depth <= number_of_constraint[0] or \
           (depth > number_of_constraint[0] and random.choice([False, True]))) \
           and  depth <= number_of_constraint[1]:
            self.right_treenode = TreeNode(self.path)
            self.right_treenode.path += 'Right'
            self.right_treenode.randomize()


    def mutate(self):
        """Make random changes to the tree node.
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()

        # delegate mutating to the nodes child components
        if self.left_treenode is not None:
            self.left_treenode.mutate()
        if self.right_treenode is not None:
            self.right_treenode.mutate()
        # mutating my details
        self.left_background.mutate()
        self.right_background.mutate()
        if model_random.is_mutating():
            self.layer.mutate()
        if model_random.is_mutating():
            if model_random.is_mutating():
                merger_factory = ka_factory.get_factory('merger')
                mergertype_constraint = cpool.get(self, MERGERTYPE_CONSTRAINT)
                self.merger = merger_factory.create_random(mergertype_constraint,
                                                               self.path)
            self.merger.randomize()
        if model_random.is_mutating():
            if model_random.is_mutating():
                modifier_factory = ka_factory.get_factory('modifier')
                modifiertype_constraint = cpool.get(self, MODIFIERTYPE_CONSTRAINT)
                self.modifier = modifier_factory.create_random(modifiertype_constraint,
                                                               self.path)
            self.modifier.randomize()

    def swap_places(self):
        """Swap 'left' and 'right' tree node delegate swapping to the nodes components."""
        # shuffle tree node
        self.left_treenode, self.right_treenode = \
                          model_random.swap_parameters(self.left_treenode,
                                                       self.right_treenode)
        self.left_background, self.right_background = \
                          model_random.swap_parameters(self.left_background,
                                                       self.right_background)
        # delegate swapping to the nodes child components
        if self.left_treenode is not None:
            self.left_treenode.swap_places()
        if self.right_treenode is not None:
            self.right_treenode.swap_places()
        self.layer.swap_places()
        self.merger.swap_places()
        self.modifier.swap_places()

    def crossingover(self, other):
        """Returns a deep copy mixed from my tree node and the other tree node.
        pre: isinstance(other, TreeNode)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        post: __return__.layer is not None
        """
        # deep copy
        new_one = TreeNode(self.get_trunk())
        # crossing over the layers
        new_one.left_treenode = other.left_treenode \
                                    if model_random.is_crossing() \
                                    else self.left_treenode
        if new_one.left_treenode is not None:
            new_one.left_treenode = new_one.left_treenode.copy()
        new_one.right_treenode = other.right_treenode \
                                    if model_random.is_crossing() \
                                    else self.right_treenode
        if new_one.right_treenode is not None:
            new_one.right_treenode = new_one.right_treenode.copy()
        new_one.left_background = self.left_background.crossingover(other.left_background)
        new_one.right_background = self.right_background.crossingover(other.right_background)
        new_one.layer = other.layer.copy() \
                                    if model_random.is_crossing() \
                                    else self.layer.copy()
        new_one.merger = other.merger.copy() \
                                    if model_random.is_crossing() \
                                    else self.merger.copy()
        new_one.modifier = other.modifier.copy() \
                                    if model_random.is_crossing() \
                                    else self.modifier.copy()
        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        if task.quit:
#            ka_debug.info('quitting task: [%s], %s' % \
#                   (task.work_for, self.path))
            return
#!!        time.sleep(0.001)
        try:
            ctx.save()
#            ka_debug.matrix_s(ctx.get_matrix())
            if (self.left_treenode is None) and (self.right_treenode is None):
                # I am a leaf, use my own layer painting strategy
                self.layer.render(task, ctx, width, height)
            elif (self.left_treenode is not None) and (self.right_treenode is not None):
                # merge 'left' and 'right' tree node
                left_surface, left_ctx = self._prepare_surface(ctx, width, height, \
                                                               self.left_background)
                self.left_treenode.render(task, left_ctx, width, height)
    #            left_surface.write_to_png('/dev/shm/left_' + self.left_treenode.get_unique_id() + '.png')
                right_surface, right_ctx = self._prepare_surface(ctx, width, height, \
                                                                 self.right_background)
                right_ctx.set_operator(cairo.OPERATOR_SOURCE)
                self.right_treenode.render(task, right_ctx, width, height)
    #            right_surface.write_to_png('/dev/shm/right_' + self.right_treenode.get_unique_id() + '.png')
    
                if not task.quit:
                    self.merger.merge_layers(left_surface, right_surface, \
                                             ctx, width, height)
            elif (self.left_treenode is not None) and (self.right_treenode is None):
                self.modifier.render_single_layer(task, self.layer, self.left_treenode,
                                                  ctx, width, height)
            elif (self.left_treenode is None) and (self.right_treenode is not None):
                self.modifier.render_single_layer(task, self.layer, self.right_treenode, 
                                                  ctx, width, height)
#            ka_debug.matrix_r(ctx.get_matrix())
            ctx.restore()
        except:
            ka_debug.err('failed calculating [%s] [%s] [%s]' % \
                   (self.get_unique_id(), sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
#            ka_debug.matrix(ctx.get_matrix())

    def _prepare_surface(self, ctx, width, height, background):
        new_surface = ctx.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA, 
                                                      width, height)
        new_ctx = cairo.Context(new_surface)
        new_ctx.scale(float(width), float(height))
#        ka_debug.matrix(new_ctx.get_matrix())
        new_ctx.translate(0.5, 0.5)
#        ka_debug.matrix(new_ctx.get_matrix())
        new_ctx.set_operator(cairo.OPERATOR_SOURCE)
        rgba = background.rgba
        new_ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        new_ctx.paint()
        return new_surface, new_ctx

    def explain(self, task, formater):
        """Explain all layers, modifier and mergers."""

        width = height = 256

        # explain layers for current node and its child nodes
        leaf = (self.left_treenode is None) and (self.right_treenode is None)
        # preview
#ex        title = 'Leaf ' if leaf  else 'Combined layers of subtree'
#ex        formater.begin_list(title)
        # preview this node
        self._preview(task, self, formater, width, height)

        # explain details
        if leaf:
            # explain the leafs layer
            self.layer.explain(formater)
        elif (self.left_treenode is not None) and (self.right_treenode is not None):
            formater.begin_list(_('Details for merging node ') + self.path)
            # explain how layers are combined
            formater.color_item(self.left_background,
                                _('left background color:'),
                                alpha=True)
            self.merger.explain_left(formater)
            self.left_treenode.explain(task, formater)
            formater.color_item(self.right_background,
                                _('right background color:'),
                                alpha=True)
            self.merger.explain_right(formater)
            self.right_treenode.explain(task, formater)
            formater.end_list()
        else:
            formater.begin_list(_('Details for modifying node ') + self.path)
            # preview this node
            self._preview(task, self.layer, formater, width, height)
            if self.left_treenode is not None:
                self.modifier.explain(task, formater,
                                      self.layer, self.left_treenode)
            if self.right_treenode is not None:
                self.modifier.explain(task, formater,
                                      self.layer, self.right_treenode)
            formater.end_list()
        
#ex        formater.end_list()
        
    def _preview(self, task, source, formater, width, height):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.scale(float(width), float(height))
#        ka_debug.matrix(ctx.get_matrix())
        ctx.translate(0.5, 0.5)
#        ka_debug.matrix(ctx.get_matrix())
        TreeNode._paint_checker_board(ctx)
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        source.render(task, ctx, width, height)
        formater.surface_item(surface, 'Tree node ' + self.path, self.path)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def copy(self):
        """ The tree nodes copy constructor.
        post: __return__.layer is not None
        """
        new_one = TreeNode(self.get_trunk())
        new_one.path = self.path[:]
        new_one.left_treenode = self.left_treenode.copy() \
                                if self.left_treenode is not None \
                                else None
        new_one.right_treenode = self.right_treenode.copy() \
                                 if self.right_treenode is not None \
                                 else None
        new_one.layer = self.layer.copy()
        new_one.merger = self.merger.copy()
        new_one.modifier = self.modifier.copy()
        new_one.left_background = self.left_background.copy()
        new_one.right_background = self.right_background.copy()
        return new_one


def _count_slash(path):
    return len([char for char in path if char == '/'])
