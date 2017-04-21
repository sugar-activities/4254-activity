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

"""Extension point for buzzword lists."""

import model_locus

class SugarBuzzwordConstraint(model_locus.Locus):
    """List of buzzwords related to Sugar."""

    def __init__(self, trunk):
        """Buzzword constraint constructor"""
        super(SugarBuzzwordConstraint, self).__init__(trunk)
        
    def get_wordlist(self):
        """Returns a list of predefined words."""
        return (u'Sugar Labs',
                u'Sugar on a Stick',
                u'learning platform',
                u'activity',
                u'education',
                u'open source',
                u'collaboration',
                u'participation',
                u'independence',
               )
