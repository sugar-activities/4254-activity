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

import sys
import traceback
import threading
import gobject

import ka_debug
import ka_status

class GeneratorTask(object):
    """Decoupling rendering and GUI.
    inv: GeneratorTask._internal_task_count >= 0
    """
    _internal_task_list_lock = threading.Lock()
    _internal_serialize_lock = threading.Lock()
    _internal_leave_condition = threading.Condition()
    _internal_task_count = 0
    _internal_task_list = {}
    
    @staticmethod
    def _enter(task):
        """Used for counting of running tasks.
        pre: GeneratorTask._internal_task_count >= 0
        #pre: not GeneratorTask._internal_task_list.has_key(task.work_for)
        post: GeneratorTask. _internal_task_count >= 1
        #post: __old__.GeneratorTask._internal_task_count-1 == GeneratorTask._internal_task_count
        """
        GeneratorTask._internal_task_list_lock.acquire()
#        GeneratorTask._wait(task.work_for)

        GeneratorTask._internal_task_count += 1
        GeneratorTask._internal_task_list[task.work_for] = task
#        ka_debug.info('enter task: [%s], count aprox.= %u' % \
#               (task.work_for, GeneratorTask._internal_task_count))
        GeneratorTask._internal_task_list_lock.release()
        ka_status.Status.instance(). \
                       set(ka_status.TOPIC_TASK, ka_status.SUB_UNFINISHED,
                           str(GeneratorTask._internal_task_count))
    
    @staticmethod
    def _leave(work_for):
        """Used for counting of running tasks.
        pre: GeneratorTask._internal_task_count >= 1
        #pre: GeneratorTask._internal_task_list.has_key(work_for)
        post: GeneratorTask._internal_task_count >= 0
        #post: __old__.GeneratorTask._internal_task_count+1 == GeneratorTask._internal_task_count
        """
        GeneratorTask._internal_task_list_lock.acquire()
        GeneratorTask._internal_task_count -= 1

        GeneratorTask._internal_leave_condition.acquire()
        if GeneratorTask._internal_task_list.has_key(work_for):
            del GeneratorTask._internal_task_list[work_for]
        GeneratorTask._internal_leave_condition.notifyAll()
        GeneratorTask._internal_leave_condition.release()

#        ka_debug.info('leave task: [%s], count aprox.= %u' % \
#               (work_for, GeneratorTask._internal_task_count))
        GeneratorTask._internal_task_list_lock.release()
        ka_status.Status.instance(). \
                       set(ka_status.TOPIC_TASK, ka_status.SUB_UNFINISHED,
                           str(GeneratorTask._internal_task_count))
    
    @staticmethod
    def _wait(work_for):
        GeneratorTask._internal_task_list_lock.acquire()
        if GeneratorTask._internal_task_list.has_key(work_for):
            GeneratorTask._internal_task_list[work_for].quit = True
            ka_debug.info('set quit task: [%s], count aprox.= %u' % \
                   (work_for, GeneratorTask._internal_task_count))
            ka_debug.print_call_stack()
        GeneratorTask._internal_task_list_lock.release()

        GeneratorTask._internal_leave_condition.acquire()
        while GeneratorTask._internal_task_list.has_key(work_for):
#            ka_debug.info('wait task: [%s], count aprox.= %u' % \
#                   (work_for, GeneratorTask._internal_task_count))
            GeneratorTask._internal_leave_condition.wait()
        GeneratorTask._internal_leave_condition.release()
            
    @staticmethod
    def is_completed():
        """Check that all tasks are terminated.
        pre: GeneratorTask._internal_task_count >= 0
        """
        return GeneratorTask._internal_task_count < 1
    
    def __init__(self, task_function, on_task_completed, work_for):
        """
        pre: task_function is not None and callable(task_function)
        pre: on_task_completed is not None and callable(on_task_completed)
        """
        self.quit = False
        self._on_task_completed = on_task_completed
        self._task_function = task_function
        self.work_for = work_for

    def _start(self, *args, **dummy):
        try:
            GeneratorTask._internal_serialize_lock.acquire()
            GeneratorTask._wait(self.work_for)
            GeneratorTask._enter(self)
            GeneratorTask._internal_serialize_lock.release()

            result = self._task_function(self, *args)
            if not self.quit:
                # GTK will start this 'completed task' whenever there are no higher
                # priority events pending to the default main loop.
                gobject.idle_add(self._on_task_completed, result)
            else:
                ka_debug.info('quitting task: [%s], count aprox.= %u' % \
                       (self.work_for, GeneratorTask._internal_task_count))                
        except:
            ka_debug.err('failed calculating [%s] [%s] [%s]' % \
                   (self._task_function, sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        finally:
            GeneratorTask._leave(self.work_for)

    def start(self, *args, **kwargs):
        threading.Thread(target=self._start, args=args, kwargs=kwargs).start()
