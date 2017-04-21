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

import traceback
import sys
import os
from ConfigParser import ConfigParser

import ka_debug

_PREFIX = 'ep_'
_PYEXT = '.py'
_SEP = '_'

_extension_types = []
_extensions = []
revision_number = 0

def list_extensions(extension_type):
    """
    pre: extension_type in _extension_types
    """
    e_list = []
    for extension_class in _extensions:
        if extension_class.startswith(extension_type + _SEP):
            e_list.append(extension_class)
    e_list.sort()
    return e_list

def list_extension_types():
    return _extension_types

def create(extension_key, *params):
    """
    pre: extension_key in _extensions
    post: __return__ is not None
    """
    a_module = __import__('ep_' + extension_key)
    for key, value in a_module.__dict__.iteritems():
#        print '-- ', str(type(value)), key
        if str(type(value)) == "<type 'type'>":
            a_class = getattr(a_module, key)
            return a_class(*params)

def _add(extension_type, extension_class):
    if extension_type not in _extension_types:
        _extension_types.append(extension_type)
    e_key = extension_type + _SEP + extension_class
    if e_key not in _extensions:
        _extensions.append(e_key)

def get_bundle_path():
    bundle_path = ka_debug.DEBUG_ACTIVITY_PATH
    if 'SUGAR_BUNDLE_PATH' in os.environ:
        from sugar.activity import activity
        bundle_path = activity.get_bundle_path()
    return bundle_path

def  _get_manifest_version(bundle_path):
    revision = 0
    try:
        cp = ConfigParser()
        cp.readfp(open(os.path.join(bundle_path, 'activity/activity.info'), 'rb'))
        if cp.has_option('Activity', 'activity_version'):
            version = cp.get('Activity', 'activity_version')
            revision = int(version)
    except:
        ka_debug.err('reading manifest version failed [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)
    return revision

def scann():
    global revision_number
    bundle_path = get_bundle_path()
    revision_number = _get_manifest_version(bundle_path)
    ka_debug.info('This is Kandid, release v' + str(revision_number))
    ka_debug.info('Searching for extensions in ' + bundle_path)
    for element in os.listdir(bundle_path):
        if element.startswith(_PREFIX) and element.endswith(_PYEXT) \
           and os.path.isfile(os.path.join(bundle_path, element)):
            name_parts = element.split(_SEP)
            if len(name_parts) == 3:
                _add(name_parts[1], name_parts[2].replace(_PYEXT, ''))
    _extension_types.sort()
    _extensions.sort()

scann()