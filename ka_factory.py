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
import ka_extensionpoint

class LayerFactory(object):
    """
    inv: self.factory_keys is not None
    """
    def __init__(self, category):
        """ LayerFactory is a singleton. 
        Please call ka_factory.get_factory(category) to retrieve the instance.
        """
        self.category = category
        self.factory_keys = ka_extensionpoint.list_extensions(self.category)
        self.factory_keys = map(lambda x: x.replace(self.category + '_', ''), \
                                self.factory_keys)

    def count(self):
        """
        post: __return__ > 0
        """
        return len(self.factory_keys)

    def keys(self):
        """
        """
        return self.factory_keys

    def create(self, factory_key, *params):
        """
        pre: factory_key in self.factory_keys
        post: __return__ is not None
        """
        return ka_extensionpoint.create(self.category + '_' + factory_key,
                                        *params)

    def create_random(self, key_filter, *params):
        """
        pre: key_filter is not None
        pre: len(key_filter) > 0
        post: __return__ is not None
        """
        permitted = [x for x in self.factory_keys if x in key_filter]
        return self.create(random.choice(permitted), *params)

FACTORY_DICT = {}

def get_factory(category):
    """
    pre: category is not None
    post: __return__ is not None
    """
    if not FACTORY_DICT.has_key(category):
        FACTORY_DICT[category] = LayerFactory(category)
    return FACTORY_DICT[category]
