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

import random
import cairo
import model_random
import model_allele
from gettext import gettext as _

## Cairo's compositing operators 
##    OPERATOR_ADD = 12
##    OPERATOR_ATOP = 5
##    OPERATOR_CLEAR = 0
##    OPERATOR_DEST = 6
##    OPERATOR_DEST_ATOP = 10
##    OPERATOR_DEST_IN = 8
##    OPERATOR_DEST_OUT = 9
##    OPERATOR_DEST_OVER = 7
##    OPERATOR_IN = 3
##    OPERATOR_OUT = 4
##    OPERATOR_OVER = 2
##    OPERATOR_SATURATE = 13
##    OPERATOR_SOURCE = 1
##    OPERATOR_XOR = 11
#
#OPERATOR_CONSTRAINT = 'operatorconstraint'

class Layer(model_allele.Allele):
    """Layer
    """

    base_cdef = [{}]

    def __init__(self, trunk):
        """Layer constructor"""
        super(Layer, self).__init__(trunk)
        self.random_seed = 1512

    def __eq__(self, other):
        """Equality based on the cells color components."""
        equal = isinstance(other, Layer) \
                and self.random_seed == other.random_seed
        return equal

    def randomize(self):
        """Randomize the layers components."""
        self.random_seed = random.randint(1, 65535)

    def mutate(self):
        """Make small random changes to the layers components."""
        pass

    def swap_places(self):
        """Layer is an abstract class. Call swap_places() on sub classes only.
        """
        raise TypeError("Layer is an abstract class. " \
                        "Call swap_places() on sub classes only.")

    def crossingover(self, other):
        """Layer is an abstract class. Call crossingover() on sub classes only.
        """
        raise TypeError("Layer is an abstract class. " \
                        "Call crossingover() on sub classes only.")

    def crossingover_base(self, new_one, other, cross_lenght):
        """
        pre: isinstance(new_one, Layer)
        pre: isinstance(other, Layer)
        pre: cross_lenght >= 0
        """
        cross_sequence = model_random.crossing_sequence(cross_lenght + 1)
        new_one.random_seed = self.random_seed \
                         if cross_sequence[cross_lenght] else other.random_seed
        return cross_sequence

    def render(self, task, ctx, width, height):
        """Layer is an abstract class. Call render() on sub classes only."""
        raise TypeError("Layer is an abstract class. " \
                        "Call render() on sub classes only.")

    def begin_render(self, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        ctx.set_operator(cairo.OPERATOR_SOURCE)

    def explain(self, formater):
        formater.text_item(_('Painters algorithm: ') + self.__class__.__name__)
        formater.text_item(_('Seed value for random generator: ') \
                           + str(self.random_seed))

    def copy(self):
        """Layer is an abstract class. "Call copy() on sub classes only."""
        raise TypeError("Layer is an abstract class. " \
                        "Call copy() on sub classes only.")
    
    def copy_base(self, new_one):
        """The layers copy constructor
        pre: isinstance(new_one, Layer)
        """
        new_one.random_seed = self.random_seed
