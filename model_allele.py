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

import model_locus

class Allele(model_locus.Locus):
    
    def __init__(self, root):
        super(Allele, self).__init__(root)

    def __eq__(self, other):
        raise TypeError("Use only __eq__ from derived subclasses.")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        raise TypeError("Genome objects are unhashable")
