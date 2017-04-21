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

import logging
import os
import time
import math

#Add support for design by contract to all classes except blacklist.

# default path for testing on local machine
DEBUG_ACTIVITY_PATH = '/home/strom/minimal/activities/Kandid.activity'
DEBUG_PROFILE_PATH = '/home/strom/.sugar/1/'
DBC_BLACK_LIST = ['activity', 'ka_debug', 'kandidtube', 'setup', ]
_logger = None
_start_time = time.time()
_last_clock = 0.0
_try_once, locale_testrun = False, False
if os.path.exists(DEBUG_ACTIVITY_PATH):
    locale_testrun = True
    _try_once = True

is_DbC_activated = False

def _avtivate_logger():
    """Activate logger."""
    global _logger
    if not _logger:
        _logger = logging.getLogger('Kandid')
        _logger.setLevel(logging.DEBUG)

def info(msg):
    """Log an info message."""
    global _last_clock, locale_testrun
    clock_now = time.clock()
    if locale_testrun:
        print 'debug', int((time.time()-_start_time)*1000), \
                       int((clock_now-_last_clock)*1000), ':', msg
    _last_clock = clock_now
    _avtivate_logger()
    _logger.debug(msg)
#    _logger.debug(caller())

def _matrix(mtrx, context):
    """Log an info message."""
    xx, yx, xy, yy, x0, y0 = mtrx
    det = xx * yy + yx * xy
    if math.fabs(det) < (0.004 ** 2):
        global _last_clock, locale_testrun
        clock_now = time.clock()
        if locale_testrun:
            print 'matrix', int((time.time()-_start_time)*1000), \
                int((clock_now-_last_clock)*1000), ':', context, mtrx, ', det=', det
        _last_clock = clock_now
        _avtivate_logger()
        _logger.debug(mtrx)
#        raise ValueError('det=' + str(det) + ', ' + str(mtrx))

def matrix(mtrx):
    """Log an info message."""
    _matrix(mtrx, '')

def matrix_s(mtrx):
    """Log matrix after save."""
    _matrix(mtrx, 'save')

def matrix_r(mtrx):
    """Log matrix before restore."""
    _matrix(mtrx, 'restore')

def err(msg):
    """Log an error message."""
    global _last_clock, locale_testrun
    clock_now = time.clock()
    if locale_testrun:
        print 'error', int((time.time()-_start_time)*1000), \
                       int((clock_now-_last_clock)*1000), ':', msg
        _last_clock = clock_now
    _avtivate_logger()
    _logger.error(msg)

_ref_list = []
def dot_start():
    global _ref_list
    _ref_list = []

def dot_id(obj):
    result = '"' + str(type(obj)) + ' ' + str(id(obj)) + '"'
    return result.replace("'>", '').replace("<class '", '').replace("<type '", '')

def dot_ref(anchor, ref):
    result = '\n' + anchor + dot_id(ref)
    for referenced in _ref_list:
        if id(ref) == referenced:
            result += ' [color=red ]'
            break
    _ref_list.append(id(ref))
    result += ' ;'
    try:
        result += '\n' + ref.dot()
    finally:
        return result
    
def print_call_stack():
#    import traceback
#    try:
#        raise TypeError("")
#    except TypeError:
#        traceback.print_stack()
    pass

def contains_by_id(this_list, this_element):
    """Returns True if element in list. Comparison is done using id().
    Only for use in design by contact statements."""
    for elem in this_list:
        if id(elem) == id(this_element):
            return True
    return False

if _try_once:
    try:
        _try_once = False
        import contract, doctest
        def enable_contact(module_name):
            """Enables design by contact for a module."""
            if module_name not in DBC_BLACK_LIST \
               and not module_name.startswith('test_'):
                a_modul = __import__(module_name)
                contract.checkmod(module_name)
                doctest.testmod(a_modul)
                print module_name, 
            
        bundle_path = DEBUG_ACTIVITY_PATH
        if 'SUGAR_BUNDLE_PATH' in os.environ:
            from sugar.activity import activity
            bundle_path = activity.get_bundle_path()
        print 'enable_contact',
        for element in os.listdir(bundle_path):
            if element.endswith('.py') \
               and os.path.isfile(os.path.join(bundle_path, element)):
                name_parts = element.split('.')
                if len(name_parts) == 2:
                    enable_contact(name_parts[0])
        is_DbC_activated = True
    except ImportError:
        is_DbC_activated = False
        print "unsupported design by contract"
