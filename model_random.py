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
import math

import ka_debug
import model_locus

crossing_probability = 0.75
swapping_probability = 0.10
mutating_probability = 0.25

_flurry = 0.5

def set_flurry(flurry_rate):
    """Set amount of turbulence while breeding a new chromosome.
    pre: 0 <= flurry_rate <= 9
    post: 0.0 <= _flurry <= 1.0
    """
    global _flurry
    _flurry = flurry_rate / 10.0

def get_flurry():
    """Returns amount of turbulence while breeding a new chromosome.
    post: 0 <= __return__ <= 9
    """
    return _flurry * 10.0

def binomial(n, probability):
    """ Generates a binomial distributed random value.
    Returns a random number between 0 (inclusive) and n (inclusive).
    Code is from http://geovistastudio.sourceforge.net/
    pre: n >= 0
    pre: 0.0 <= probability <= 1.0
    post: 0 <= __return__ <= n 
    """
    result = 0
    for dummy in range(n):
        if random.random() < probability:
            result += 1
    return result

def jitter(sigma):
    """Returns a gaussian jitter. Scaled by flurry rate.
    """
    return 0.03 * _flurry * random.gauss(0.0, sigma)

def jitter_constrained(value, constraint):
    """Returns a gaussian jitter. Scaled by constraint and flurry rate.
    pre: len(constraint) == 2
    pre: constraint[0] <= constraint[1]
    """
    sigma = 0.03 * _flurry * (constraint[1] - constraint[0])
    value += random.gauss(0.0, sigma)
    if value < constraint[0]:
        return constraint[0]
    if value > constraint[1]:
        return constraint[1]
    return value

def jitter_discret_constrained(value, constraint):
    """Returns a binomial distributed number.
    Scaled by constraint and flurry rate.
    pre: len(constraint) == 2
    pre: constraint[0] <= constraint[1]
    post: constraint[0] <= __return__ <= constraint[1]
    """
    interval = constraint[1] - constraint[0]
    delta = binomial(interval, _flurry * 0.25) * random.choice([-1, 1])
    return limit_range(value+delta, constraint[0], constraint[1])

def randint_constrained(constraint):
    """Return a random integer N such that constraint[0] <= N <= constraint[1].
    pre: len(constraint) == 2
    pre: constraint[0] <= constraint[1]
    post: constraint[0] <= __return__ <= constraint[1]
    """
    return random.randint(constraint[0], constraint[1])

def uniform_constrained(constraint):
    """Return a random floating point number N
    such that constraint[0] <= N <= constraint[1].
    pre: len(constraint) == 2
    pre: constraint[0] <= constraint[1]
    post: constraint[0] <= __return__ <= constraint[1]
    """
    return random.uniform(constraint[0], constraint[1])

def is_swapping():
    """Test whether to shuffle data or leave them unmodified."""
    return random.random() < swapping_probability * _flurry

def is_mutating():
    """Test whether to mutate data or leave them unmodified."""
    return random.random() < mutating_probability * _flurry

def is_crossing():
    """Test whether to mix data or leave them unmodified."""
    return random.random() < crossing_probability * _flurry

def crossing_sequence(size):
    """Produces a sequence filled with True or False elements.
    With a low crossing_probability there will be lesser change overs from
    True series to False series.
    pre: size >= 1
    post: len(__return__) == size
    post: forall(__return__, lambda x: x is True or x is False)
    """
    sample = [random.choice([False, True])]
    for dummy in range(size-1):
        if is_crossing():
            sample.append(not sample[-1])
        else:
            sample.append(sample[-1])
    return sample

def crossingover_elem(this_element, other_element):
    """
    pre: this_element is not None
    pre: other_element is not None
    post: (not this_element.__class__ == other_element.__class__) \
        or model_locus.unique_check(__return__, this_element, other_element) == ''
    """
    if this_element.__class__ == other_element.__class__:
        return this_element.crossingover(other_element)
    else:
        return other_element.copy() if is_crossing() else this_element.copy()
        
def crossingover_list(this_list, other_list):
    """Crossing over operator for two lists.
    pre: this_list is not None
    pre: other_list is not None
    post: min([len(this_list), len(other_list)]) <= len(__return__) <= max([len(this_list), len(other_list)])
    post: forall(__return__, lambda x: not ka_debug.contains_by_id(this_list, x))
    post: forall(__return__, lambda x: not ka_debug.contains_by_id(other_list, x))
    """
    # crossing over common part of this list and other list
    len_this, len_other = len(this_list), len(other_list)
    min_elements = min([len_this, len_other])
    max_elements = max([len_this, len_other])
    new_list = []
    if max_elements > 0:
        cross_sequence = crossing_sequence(min_elements)
        for index in range(min_elements):
            this_element, other_element = this_list[index], other_list[index]
            if this_element.__class__ == other_element.__class__ \
               and 'crossingover' in dir(this_element):
                # delegate crossing over to the elements components
                new_list.append(this_element.crossingover(other_element))
            else:
                # crossing over whole elements
                if cross_sequence[index]:
                    new_list.append(this_element.copy())
                else:
                    new_list.append(other_element.copy())
    
        # appending elements from protozoon of greater size
        if len_this > len_other:
            for index in range(min_elements, max_elements):
                new_list.append(this_list[index].copy())
        if len_this < len_other:
            for index in range(min_elements, max_elements):
                new_list.append(other_list[index].copy())
    return  new_list

def crossingover_str_list(first, second):
    """Crossing over the str elements of the two input lists.
    Returns a new list.
    pre: len(first) >= 0
    pre: len(second) >= 0
    post: min([len(first), len(second)]) <= len(__return__) <= max([len(first), len(second)])
    post: forall(__return__, lambda x: x in first or x in second)
    """
    seq = []
    len_first, len_second = len(first), len(second)
    len_max = max([len_first, len_second])
    if len_max > 0:
        randseq = crossing_sequence(len_max)
        for index in range(len_max):
            if randseq[index]:
                if index < len_first:
                    seq.append(first[index][:])
            else:
                if index < len_second:
                    seq.append(second[index][:])
    return seq

def crossingover_nativeelement_list(first, second):
    """Crossing over the native elements of the two input lists.
    Returns a new list. This is not a deep copy of the elements.
    pre: len(first) >= 0
    pre: len(second) >= 0
    post: min([len(first), len(second)]) <= len(__return__) <= max([len(first), len(second)])
    post: forall(__return__, lambda x: x in first or x in second)
    """
    seq = []
    len_first, len_second = len(first), len(second)
    len_max = max([len_first, len_second])
    if len_max > 0:
        randseq = crossing_sequence(len_max)
        for index in range(len_max):
            if randseq[index]:
                if index < len_first:
                    seq.append(first[index])
            else:
                if index < len_second:
                    seq.append(second[index])
    return seq

def swap_places(this_list):
    """Select two elements from the list by random. 
    Exchange these randomly selected elements."""
    if len(this_list) >= 2 and is_swapping():
        max_index = len(this_list) - 1
        ix1, ix2 = random.randint(0, max_index), random.randint(0, max_index)
        temp1, temp2 = this_list[ix1], this_list[ix2]
        this_list[ix1], this_list[ix2] = temp2, temp1

def swap_parameters(param1, param2):
    """Returns the tuple (p1, p2) 
    or the tuple (p2, p1) with reordered elements."""
    if is_swapping():
        return param2, param1
    else:
        return param1, param2

def mutate_list(this_list, number_of_constraint, new_element):
    """Mutate a list containing alleles / elements
    and delegate mutating to all elements in the lists.
    pre: number_of_constraint[0] <= number_of_constraint[1]
    pre: new_element is not None
    """
    # maybe remove one element
    len_this = len(this_list)
    if len_this > number_of_constraint[0] and is_mutating():
        del this_list[random.randint(0, len_this-1)]
        len_this -= 1
    # maybe duplicate one of the elements
    if len_this < number_of_constraint[1] and is_mutating():
        random_element = this_list[random.randint(0, len_this-1)]
        dupli_element = random_element.copy()
        this_list.insert(random.randint(0, len_this-1), dupli_element)
        len_this += 1
    # maybe insert a new element
    if len_this < number_of_constraint[1] and is_mutating():
        new_element.randomize()
        this_list.insert(random.randint(0, len_this-1), new_element)
        len_this += 1

    # delegate mutation to the elements child components
    for single_element in this_list:
        single_element.mutate()

def limit(value):
    """Limit value to range 0.0, 1.0
    post: 0.0 <= __return__ <= 1.0
    """
    if value < 0.0:
        value = 0.0
    elif value > 1.0:
        value = 1.0
    return value

def cyclic_limit(value):
    """Limit value to range 0.0, 1.0
    Overflow is handled in a cyclic manner.
    post: 0.0 <= __return__ <= 1.0
    """
    return _cyclic_limit(value, 0.0, 1.0)

def radian_limit(value):
    """Limit value to range -Pi, +Pi
    Overflow is handled in a cyclic manner.
    post: (-1.0*math.pi) <= __return__ <= math.pi
    """
    return _cyclic_limit(value, -1.0*math.pi, math.pi)

def _cyclic_limit(value, lower_bound, upper_bound):
    """Limit value to range lower_bound, upper_bound.
    Overflow is handled in a cyclic manner.
    post: lower_bound <= __return__ <= upper_bound
    """
    while value < lower_bound:
        value += upper_bound-lower_bound
    while value > upper_bound:
        value -= upper_bound-lower_bound
    return value

def limit_range(value, min_value, max_value):
    """Limit value to range min_value, max_value
    pre: min_value <= max_value
    post: min_value <= __return__ <= max_value
    """
    if value < min_value:
        value = min_value
    elif value > max_value:
        value = max_value
    return value

def copy_list(other_list):
    """Make a deep copy of a list and its elements.
    pre: other_list is not None
    post: __return__ is not other_list
    post: len(__return__) == len(other_list)
    post: forall([other_list[i] is not __return__[i] for i in range(len(other_list))])
    post: forall([other_list[i] == __return__[i] for i in range(len(other_list))])
    """
    new_list = []
    for element in other_list:
        new_list.append(element.copy())
    return new_list 

#def copy_tuple_list(other_list):
#    """Make a deep copy of a list and its tuple elements.
#    Assumes every tuple has two cells
#    pre: other_list is not None
#    pre: len(other_list) == 0 or forall([len(e) == 2 for e in other_list])
#    post: __return__ is not other_list
#    post: len(__return__) == len(other_list)
#    post: forall([other_list[i][0] is not __return__[i][0] for i in range(len(other_list))])
#    post: forall([other_list[i][0] == __return__[i][0] for i in range(len(other_list))])
#    post: forall([other_list[i][1] is not __return__[i][1] for i in range(len(other_list))])
#    post: forall([other_list[i][1] == __return__[i][1] for i in range(len(other_list))])
#    """
#    new_list = []
#    for element in other_list:
#        new_list.append( (element[0].copy(), element[1].copy()) ) 
#    return new_list 
