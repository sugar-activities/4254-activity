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

import copy
import ka_utils
import model_random
import model_locus
import model_allele
import model_constraintpool
from gettext import gettext as _
import random
import math

NUM_TRANSFORMATION_CONSTRAINT = 'numtransformationconstraint'
SYMMETRY_CONSTRAINT = 'symmetryconstraint'
DN_CONSTRAINT = 'dnconstraint'
ORBIT_CONSTRAINT = 'orbitconstraint'
X_STAMP_SIZE_CONSTRAINT = 'xstampsizeconstraint'
Y_STAMP_SIZE_CONSTRAINT = 'ystampsizeconstraint'


MAX_TRANSFORMATIONS = 8
MAX_MATCHER = 128



class AffineIfsSampler(model_allele.Allele):
    """AffineIfsSampler: Affine iterated function system.
    inv: self.symmetry >= 0
    inv: self.num_transformations <= MAX_TRANSFORMATIONS
    inv: len(self.mta) == MAX_TRANSFORMATIONS
    inv: len(self.mta) == len(self.mtf)
    """

    cdef = [{'bind'  : NUM_TRANSFORMATION_CONSTRAINT,
             'name'  : 'Number of transformations use in this iterated function system',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 8},
            {'bind'  : SYMMETRY_CONSTRAINT,
             'name'  : 'Symmetry',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0, 'max': 12},
             {'bind'  : DN_CONSTRAINT,
             'name'  : 'Dn',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0, 'max': 1},
             {'bind'  : ORBIT_CONSTRAINT,
             'name'  : 'Number of iterations',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 150},
             {'bind'  : X_STAMP_SIZE_CONSTRAINT,
             'name'  : 'Number of rectilinear tiles in x direction',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.25},
             {'bind'  : Y_STAMP_SIZE_CONSTRAINT,
             'name'  : 'Number of rectilinear tiles in y direction',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.25},
           ]

    def __init__(self, trunk):
        """Constructor for Affine iterated function system."""
        super(AffineIfsSampler, self).__init__(trunk)
        self.x_point, self.y_point = 0.0, 0.0
        self.xmin, self.ymin, self.xmax, self.ymax = -1.0, -1.0, 1.0, 1.0
        self.matcher = [0] * MAX_MATCHER
        
        self.random_seed = 1512
        self.orbits = 10
        self.num_transformations = 1
        self._fill_pol_transf()
        self.mta = [0.0] * MAX_TRANSFORMATIONS
        self.mtb = [0.0] * MAX_TRANSFORMATIONS
        self.mtc = [0.0] * MAX_TRANSFORMATIONS
        self.mtd = [0.0] * MAX_TRANSFORMATIONS
        self.mte = [0.0] * MAX_TRANSFORMATIONS
        self.mtf = [0.0] * MAX_TRANSFORMATIONS

        self.Dn = 0
        self.symmetry = 0
        self.tr_rand = random.Random(self.random_seed)

        self.x_stamp_size = 1
        self.y_stamp_size = 1

    def __deepcopy__ ( self,  memo ):
        """Don't store transient members."""
#        x = AffineIfsSampler(self.get_trunk())
        x = self.__class__(self.get_trunk())
        memo[id(self)] = x
        # deep copy members
        for n, v in self.__dict__.iteritems():
            # do not copy transient members
            if n not in ['x_point', 'y_point', 'xmin', 'ymin', 'xmax', 'ymax', \
                         'tr_rand', 'matcher', \
                         'mta', 'mtb', 'mtc', 'mtd', 'mte', 'mtf', ]:
                setattr(x, n, copy.deepcopy(v, memo))
        return x

    def __eq__(self, other):
        """Equality based persistent."""
        equal = isinstance(other, AffineIfsSampler) \
                and self.num_transformations == other.num_transformations \
                and self.random_seed == other.random_seed \
                and self.orbits == other.orbits \
                and self.symmetry == other.symmetry \
                and self.Dn == other.Dn \
                and self.x_stamp_size == other.x_stamp_size \
                and self.y_stamp_size == other.y_stamp_size
        if equal:
            for row, transf in enumerate(self.pol_transf):
                for col, value in enumerate(transf):
                    equal = equal \
                            and math.fabs(value-other.pol_transf[row][col]) < 0.0001                
        return equal


    def _fill_pol_transf(self):
        self.pol_transf = [
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                           [0.0, 0.0, 0.0, 0.0, 0.5, 0.5],
                          ]

    def randomize(self):
        """Randomize tranformations.
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()
        symmetry_constraint = cpool.get(self, SYMMETRY_CONSTRAINT)
        #TODO symmetry 0, 25 Binominal
        self.symmetry = model_random.randint_constrained(symmetry_constraint)

        Dn_constraint = cpool.get(self, DN_CONSTRAINT)
        self.Dn = model_random.randint_constrained(Dn_constraint)
        
        orbit_constraint = cpool.get(self, ORBIT_CONSTRAINT)
        self.orbits = model_random.randint_constrained(orbit_constraint)

        self.random_seed = random.randint(1, 65535)

        num_transformations_constraint = cpool.get(self, NUM_TRANSFORMATION_CONSTRAINT)
        self.num_transformations = model_random.randint_constrained(num_transformations_constraint)
        self._fill_pol_transf()
        for tix in range(self.num_transformations):
            #translation -2.0, 2.0
            self.pol_transf[tix][0] = model_random.uniform_constrained([-2.0, 2.0])
            self.pol_transf[tix][1] = model_random.uniform_constrained([-2.0, 2.0])
            #rotation  -math.pi, math.pi
            self.pol_transf[tix][2] = model_random.uniform_constrained([-math.pi, math.pi])
            self.pol_transf[tix][3] = model_random.uniform_constrained([-math.pi, math.pi])
            #scaling 0.0, 1.0
            self.pol_transf[tix][4] = model_random.uniform_constrained([-1.0, 1.0])
            self.pol_transf[tix][5] = model_random.uniform_constrained([-1.0, 1.0])
#        self._prepare_transient_members()
        x_stamp_size_constraint = cpool.get(self, X_STAMP_SIZE_CONSTRAINT)
        self.x_stamp_size = model_random.uniform_constrained(x_stamp_size_constraint)
        y_stamp_size_constraint = cpool.get(self, Y_STAMP_SIZE_CONSTRAINT)
        self.y_stamp_size = model_random.uniform_constrained(y_stamp_size_constraint)


    def mutate(self):
        """Mutate transformations."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        #TODO self.pol_transf polar coordinaten mutieren
        if model_random.is_mutating():
            symmetry_constraint = cpool.get(self, SYMMETRY_CONSTRAINT)
            self.symmetry = model_random.jitter_discret_constrained(self.symmetry,
                                                            symmetry_constraint)
        if model_random.is_mutating():
            Dn_constraint = cpool.get(self, DN_CONSTRAINT)
            self.Dn = model_random.jitter_discret_constrained(self.Dn,
                                                              Dn_constraint)
        
        if model_random.is_mutating():
            orbit_constraint = cpool.get(self, ORBIT_CONSTRAINT)
            self.orbits = model_random.jitter_discret_constrained(self.Dn,
                                                              orbit_constraint)
        self.random_seed = random.randint(1, 65535)
        for tix in range(self.num_transformations):
            #translation -2.0, 2.0
            self.pol_transf[tix][0] = model_random.jitter_constrained(self.pol_transf[tix][0], [-2.0, 2.0])
            self.pol_transf[tix][1] = model_random.jitter_constrained(self.pol_transf[tix][1], [-2.0, 2.0])
            #rotation  -math.pi, math.pi
            radian = self.pol_transf[tix][2] + model_random.jitter(0.1)
            self.pol_transf[tix][2] = model_random.radian_limit(radian)
            radian = self.pol_transf[tix][3] + model_random.jitter(0.1)
            self.pol_transf[tix][3] = model_random.radian_limit(radian)
            #scaling 0.0, 1.0
            self.pol_transf[tix][4] = model_random.jitter_constrained(self.pol_transf[tix][4], [-1.0, 1.0])
            self.pol_transf[tix][5] = model_random.jitter_constrained(self.pol_transf[tix][5], [-1.0, 1.0])
#        self._prepare_transient_members()
        if model_random.is_mutating():
            x_stamp_size_constraint = cpool.get(self, X_STAMP_SIZE_CONSTRAINT)
            self.x_stamp_size = model_random.jitter_constrained(self.x_stamp_size,
                                                            x_stamp_size_constraint)
        if model_random.is_mutating():
            y_stamp_size_constraint = cpool.get(self, Y_STAMP_SIZE_CONSTRAINT)
            self.y_stamp_size = model_random.jitter_constrained(self.y_stamp_size,
                                                            y_stamp_size_constraint)

    def swap_places(self):
        """Exchange x- and y-stamp_size."""
        self.x_stamp_size, self.y_stamp_size = model_random.swap_parameters(self.x_stamp_size,
                                                             self.y_stamp_size)

    def crossingover(self, other):
        """
        pre: isinstance(other, AffineIfsSampler)
        pre: isinstance(self, AffineIfsSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = AffineIfsSampler(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(7+MAX_TRANSFORMATIONS)
        new_one.symmetry = self.symmetry if cross_sequence[0] else other.symmetry
        new_one.Dn = self.Dn if cross_sequence[1] else other.Dn
        new_one.random_seed = self.random_seed if cross_sequence[2] else other.random_seed
        new_one.orbits = self.orbits if cross_sequence[3] else other.orbits

        new_one.x_stamp_size = self.x_stamp_size if cross_sequence[4] else other.x_stamp_size
        new_one.y_stamp_size = self.y_stamp_size if cross_sequence[5] else other.y_stamp_size

        new_one.num_transformations = self.num_transformations \
                             if cross_sequence[6] else other.num_transformations
        new_one._fill_pol_transf()
        len_self = self.num_transformations
        len_other = other.num_transformations
        min_rows = min([len_self, len_other])
        longest = self.pol_transf if len_self >= len_other else other.pol_transf
        for row in range(new_one.num_transformations):
            if row < min_rows:
                if cross_sequence[7+row]:
                    for col in range(len(other.pol_transf[row])):
                        new_one.pol_transf[row][col] = other.pol_transf[row][col]
                else:
                    for col in range(len(self.pol_transf[row])):
                        new_one.pol_transf[row][col] = self.pol_transf[row][col]
            else:
                for col in range(len(longest[row])):
                    new_one.pol_transf[row][col] = longest[row][col]

#        new_one._prepare_transient_members()
        return new_one


    @staticmethod
    def _polar2matrix(polar):
        """Converts from polar to matrix.
        pre: len(polar) == 6
        """
        grad2rad = math.pi / 180.0
        # returns a, b,  c, d, e, f
        return \
            polar[4] * math.cos(grad2rad * polar[2]), \
           -polar[5] * math.sin(grad2rad * polar[3]), \
            polar[4] * math.sin(grad2rad * polar[2]), \
            polar[5] * math.cos(grad2rad * polar[3]), \
            polar[0], \
            polar[1]
  
    def _prepare_transient_members(self):
        self.x_point, self.y_point = 0.5, 0.5
        self.tr_rand = random.Random(self.random_seed)
        self.mta = [0.0] * MAX_TRANSFORMATIONS
        self.mtb = [0.0] * MAX_TRANSFORMATIONS
        self.mtc = [0.0] * MAX_TRANSFORMATIONS
        self.mtd = [0.0] * MAX_TRANSFORMATIONS
        self.mte = [0.0] * MAX_TRANSFORMATIONS
        self.mtf = [0.0] * MAX_TRANSFORMATIONS
        self.xmin, self.ymin, self.xmax, self.ymax = -1.0, -1.0, 1.0, 1.0
        self.matcher = [0] * MAX_MATCHER
        
        for tix in range(self.num_transformations):
            matrix = AffineIfsSampler._polar2matrix(self.pol_transf[tix])
            self.mta[tix] = matrix[0]
            self.mtb[tix] = matrix[1]
            self.mtc[tix] = matrix[2]
            self.mtd[tix] = matrix[3]
            self.mte[tix] = matrix[4]
            self.mtf[tix] = matrix[5]
#        tnumber = 0
#        matrix = AffineIfsSampler._polar2matrix(0.0, 0.0, 0.0, 0.0, 0.0, 0.16)
#        self.mta[tnumber] = matrix[0]
#        self.mtb[tnumber] = matrix[1]
#        self.mtc[tnumber] = matrix[2]
#        self.mtd[tnumber] = matrix[3]
#        self.mte[tnumber] = matrix[4]
#        self.mtf[tnumber] = matrix[5]
#        tnumber += 1
#        matrix = AffineIfsSampler._polar2matrix(0.0, 1.6, -2.5, -2.5, 0.85, 0.85)
#        self.mta[tnumber] = matrix[0]
#        self.mtb[tnumber] = matrix[1]
#        self.mtc[tnumber] = matrix[2]
#        self.mtd[tnumber] = matrix[3]
#        self.mte[tnumber] = matrix[4]
#        self.mtf[tnumber] = matrix[5]
#        tnumber += 1
#        matrix = AffineIfsSampler._polar2matrix(0.0, 1.6, 49.0, 49.0, 0.3, 0.3)
#        self.mta[tnumber] = matrix[0]
#        self.mtb[tnumber] = matrix[1]
#        self.mtc[tnumber] = matrix[2]
#        self.mtd[tnumber] = matrix[3]
#        self.mte[tnumber] = matrix[4]
#        self.mtf[tnumber] = matrix[5]
#        tnumber += 1
#        matrix = AffineIfsSampler._polar2matrix(0.0, 0.44, 120.0, -50.0, 0.3, 0.37)
#        self.mta[tnumber] = matrix[0]
#        self.mtb[tnumber] = matrix[1]
#        self.mtc[tnumber] = matrix[2]
#        self.mtd[tnumber] = matrix[3]
#        self.mte[tnumber] = matrix[4]
#        self.mtf[tnumber] = matrix[5]
#        tnumber += 1
#        self.num_transformations = tnumber
        self._prepare_matcher()
        

    def _prepare_matcher(self):
        """Calculate the probability a specific transformation is selected. 
        pre: self.num_transformations > 0
        """
        #calculate probability for each transformation
        probability = [0.0] * MAX_TRANSFORMATIONS
        for tnumber in xrange(self.num_transformations):
            probability[tnumber] =  \
                             math.fabs(self.mta[tnumber] * self.mtd[tnumber] \
                                       - self.mtb[tnumber] * self.mtc[tnumber])
            if probability[tnumber] < 0.01:
                probability[tnumber] = 0.01

        #array of probabilities summing to 1
        probability_sum = sum(probability)
        probability[0] /= probability_sum
        probability[1] /= probability_sum
        probability[2] /= probability_sum
        probability[3] /= probability_sum
        probability[4] /= probability_sum
        probability[5] /= probability_sum
        probability[6] /= probability_sum
        probability[7] /= probability_sum

        trigger = 0.0
        mix = 0
        while mix < MAX_MATCHER:
            if trigger < probability[0]:
                self.matcher[mix] = 0
            elif trigger < probability[0] + probability[1]:
                self.matcher[mix] = 1
            elif trigger < probability[0] + probability[1] + probability[2]:
                self.matcher[mix] = 2
            elif trigger < probability[0] + probability[1] + probability[2] + probability[3]:
                self.matcher[mix] = 3
            elif trigger < probability[0] + probability[1] + probability[2] + probability[3] + probability[4]:
                self.matcher[mix] = 4
            elif trigger < probability[0] + probability[1] + probability[2] + probability[3] + probability[4] + probability[5]:
                self.matcher[mix] = 5
            elif trigger < probability[0] + probability[1] + probability[2] + probability[3] + probability[4] + probability[5] + probability[6]:
                self.matcher[mix] = 6
            else:
                self.matcher[mix] = 7
            trigger += 1.0 / MAX_MATCHER
            mix += 1

    def _iterate(self):
        """Calculate one iteration."""
        tnumber = self.matcher[self.tr_rand.randrange(0, MAX_MATCHER)] \
                                        if self.num_transformations > 1 else 0
        tnumber = tnumber % self.num_transformations
        x_tmp = self.x_point * self.mta[tnumber] \
                + self.y_point * self.mtb[tnumber] + self.mte[tnumber]
        y_tmp = self.x_point * self.mtc[tnumber] \
                + self.y_point * self.mtd[tnumber] + self.mtf[tnumber]
        self.x_point, self.y_point = x_tmp, y_tmp
        if self.symmetry > 0:
            angel  = 2.0 * math.pi * self.tr_rand.randint(0, self.symmetry-1) \
                     / float(self.symmetry)
            cosinus = math.cos(angel)
            sinus   = math.sin(angel)
            x_tmp = cosinus * self.x_point - sinus * self.y_point
            y_tmp = sinus * self.x_point + cosinus * self.y_point
            self.x_point = x_tmp
            self.y_point = -y_tmp if self.Dn > 0 and self.tr_rand.randrange(0, 2) == 0 \
                                  else y_tmp
        return tnumber

    def _skip(self):
        """The first values from this iteration are not valid."""
        loop = 0
        while loop < 25:
            self._iterate()
            loop += 1

    def _maxima(self):
        """Iterate and calculate maxima"""
        self._iterate()
        self.xmin = self.x_point
        self.ymin = self.y_point
        self.xmax = self.x_point
        self.ymax = self.y_point
        loop = 0
        while loop < 199:
            self._iterate()
            if self.x_point < self.xmin:
                self.xmin = self.x_point
            if self.y_point < self.ymin:
                self.ymin = self.y_point
            if self.x_point > self.xmax:
                self.xmax = self.x_point
            if self.y_point > self.ymax:
                self.ymax = self.y_point
            loop += 1

    def _enumerate_points(self):
        """Iterate and collect sample points"""
        x_delta, y_delta = self.xmax - self.xmin, self.ymax - self.ymin
        sample_points = []
        if x_delta > 0.001 and y_delta > 0.001:
            loop = 0
            while loop < self.orbits:
                tnumber = self._iterate()
                x_rel = (self.x_point - self.xmin) / x_delta
                y_rel = (self.y_point - self.ymin) / y_delta
#TODO dritter parameter            sample_points.append( (x_rel-0.5, y_rel-0.5, tnumber) )
                sample_points.append( (x_rel-0.5, y_rel-0.5) )
                loop += 1
        return sample_points

    def get_sample_points(self):
        """ Produces a list of sampling points.
        """
#        self.tr_rand = random.Random(self.random_seed)
#        self.x_point, self.y_point = 0.5, 0.5
        #transient members
        self._prepare_transient_members()
        self._skip()
        self._maxima()
        return self._enumerate_points()

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        return self.x_stamp_size, self.y_stamp_size

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Affine iterated function system sampler')
        details = _('iterations=%d, transformations=%d symmetry=%d, Dn=%d: ')
        details = details % (self.orbits, self.num_transformations,
                             self.symmetry, self.Dn)
        return ka_utils.explain_points(head + ' ' + details + ': ',
                                       self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, AffineIfsSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = AffineIfsSampler(self.get_trunk())
        #persistent members
        new_one.random_seed = self.random_seed
        new_one.orbits = self.orbits
        new_one.num_transformations = self.num_transformations
        new_one._fill_pol_transf()
        for pix in range(self.num_transformations):
            new_one.pol_transf[pix] = self.pol_transf[pix][:]
        new_one.symmetry = self.symmetry
        new_one.Dn = self.Dn

        new_one.x_stamp_size = self.x_stamp_size
        new_one.y_stamp_size = self.y_stamp_size
        #transient members
#        new_one._prepare_transient_members()        
        return new_one
