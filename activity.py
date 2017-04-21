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

import gtk
gtk.gdk.threads_init()
import sys
import traceback
import telepathy

from sugar.activity import activity
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

import ka_debug
import ka_controller
import ka_widget
import ka_status
import kandidtube


class KandidActivity(activity.Activity):
    """Kandid is a system to evolve graphics. It uses an interactive genetic
    approach to find interesting visual patterns. This idea comes
    originally from Karls Sims. Some years ago I published a Java
    application based on this idea. http://kandid.sourceforge.net/
    Here is a similar program for Sugar and OLPC. This version
    of Kandid will use Sugar's collaborative capabilities. Instead of an
    direct port some parts of Kandid are rewritten in a way more suitable
    for children and taking in account the limited hardware resources of
    the OLPC XO.
    """

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self._name = handle
        self.metadata['mime_type'] = 'application/x-kandid-activity'
        self._print_greetings(handle)
        self._status = ka_status.Status.instance()
        self._joined_buddies =  set([])
        self._new_tubes =  []
        # Set title for our Activity
        self.set_title('Kandid')
        
        # Attach sugar toolbox (Share, ...)
        try:
            # try sugar 0.86
            ka_debug.info('searching sugar 0.86, sugar.graphics.toolbarbox')
            import sugar.graphics.toolbarbox
            toolbar_box = sugar.graphics.toolbarbox.ToolbarBox()
            self._add_toolbar_buttons(toolbar_box)
            self.set_toolbar_box(toolbar_box)
        except:
            ka_debug.err('failed sugar 0.86 toolbarbox [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
            # try sugar 0.82
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)

        # Create the main container
        main_view = gtk.HBox()
        self._widget = ka_widget.KandidWidget()
        main_view.pack_start(self._widget.get_widget_tree())
        # Create a controller to connect view and model
        self._controller = ka_controller.KandidController( \
                                                      self._widget,
                                                      self.get_activity_root(),
                                                      handle.object_id is None)
        self._controller.create_pages()
        self.set_canvas(main_view)
 
        self.kandidtube = None  # Shared session
        self.initiating = False
        self.telepathy_conn = None
        self.tubes_chan = None
        self.text_chan = None

        # get the Presence Service
        self.pservice = presenceservice.get_instance()
        self._start_collaboration()

        self.show_all()
        if handle.object_id is None:
            self._controller.switch_page('GettingstartedController')

    def _print_greetings(self, handle):
        if handle.object_id is None:
            ka_debug.info('Activity is started anew (from the home view).')
        else:
            ka_debug.info('Activity is started from the journal and the object id is %s'
                           % handle.object_id)

    def _start_collaboration(self):
        # Buddy object for you
        found_buddies = set([])
        try:
            self.connect('shared', self._on_shared)
            self.connect('joined', self._on_joined)
# pservice.get_buddies() is deprecated
#            ka_debug.info('searching buddies')
#            buddies = self.pservice.get_buddies()
#            for buddy in buddies:
#                ka_debug.info('  buddy nick: %s' % buddy.get_property('nick'))
#                ka_debug.info('  activity: %s'
#                              % buddy.get_property('current-activity'))
#                ka_debug.info('  owner: %s' % buddy.get_property('owner'))
#                found_buddies |= set([buddy.get_property('nick')])
        except:
            ka_debug.err('start collaboration failed [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        self._status.set(ka_status.TOPIC_COLLABORATION,
                        ka_status.SUB_BUDDIES_FOUND, found_buddies)
        self._status.set(ka_status.TOPIC_COLLABORATION,
                        ka_status.SUB_SHARE, '')

    def _add_toolbar_buttons(self, toolbar_box):
        import sugar.activity.widgets
        activity_button = sugar.activity.widgets.ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = sugar.activity.widgets.StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

    def read_file(self, file_path):
        """Implement reading from journal
        
        This is called within sugar.activity.Activity code
        which provides file_path.
        """
        ka_debug.info('read_file [%s] [%s]' % \
                    (self.metadata['mime_type'], file_path))
        population_controller = self._controller.find_page('PopulationController')
        if population_controller is not None:
            population_controller.read_file(file_path)
            population_controller.start_all_calculations()

    
    def write_file(self, file_path):
        """Implement writing to the journal

        This is called within sugar.activity.Activity code
        which provides the file_path.
        """
        ka_debug.info('write_file [%s]' % file_path)
        population_controller = self._controller.find_page('PopulationController')
        if population_controller is not None:
            population_controller.write_file(file_path)

    def can_close(self):
        """Activity will be closed."""
        self._controller.close()
        return True
    
    def _on_shared(self, shared_activity):
        ka_debug.info('shared activity [%s]' % shared_activity)
        self.initiating = True
        if self._sharing_setup():
            self._status.set(ka_status.TOPIC_COLLABORATION,
                             ka_status.SUB_SHARE, _('Activity is shared.'))

        ka_debug.info('making a tube...')
        chan_id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            kandidtube.SERVICE, {})
        ka_debug.info('tube %u' % chan_id)
        my_nick, my_csh = self._get_my_id()
        self._status.set(ka_status.TOPIC_COLLABORATION,
                         ka_status.SUB_ID,
                         _("I am '%s', my handle in that group is %u.") % (my_nick, my_csh))
 

    def _sharing_setup(self):
        if self._shared_activity is None:
            ka_debug.info('Failed to share or join activity')
            return False

        self.telepathy_conn = self._shared_activity.telepathy_conn
        self.tubes_chan = self._shared_activity.telepathy_tubes_chan
        self.text_chan = self._shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self._on_new_tube)

        self._shared_activity.connect('buddy-joined', self._on_buddy_joined)
        self._shared_activity.connect('buddy-left', self._on_buddy_left)

        # Find out who's already in the shared activity:
        for buddy in self._shared_activity.get_joined_buddies():
            ka_debug.info('Buddy [%s] is already in the activity' % \
                        buddy.props.nick)
            self._joined_buddies |= set([buddy.props.nick])
        self._status.set(ka_status.TOPIC_COLLABORATION,
                        ka_status.SUB_BUDDIES_JOINED, self._joined_buddies)
        return True

    def _on_list_tubes_reply(self, tubes):
        for tube_info in tubes:
            self._on_new_tube(*tube_info)

    def _on_list_tubes_error(self, error):
        ka_debug.info('ListTubes() failed: [%s]' % error)

    def _on_joined(self, joined_activity):
        if not self._shared_activity:
            return

        ka_debug.info('Joined an existing shared activity [%s]' % \
                   joined_activity)
        self.initiating = False
        if self._sharing_setup():
            self._status.set(ka_status.TOPIC_COLLABORATION,
                            ka_status.SUB_SHARE, _('Joined an existing shared activity.'))
        my_nick, my_csh = self._get_my_id()
        self._status.set(ka_status.TOPIC_COLLABORATION,
                         ka_status.SUB_ID,
                         _("I am '%s', my handle in that group is %u.") % (my_nick, my_csh))

        #TODO If a tube already exist, use it.
        ka_debug.info('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._on_list_tubes_reply,
            error_handler=self._on_list_tubes_error)

    def _on_new_tube(self, tube_id, initiator, tube_type, service, params, state):
        details = 'ID=%d initiator=%d type=%d service=[%s] params=%r state=%d' % \
                     (tube_id, initiator, tube_type, service, params, state)
        ka_debug.info('New tube ' + details)
        self._new_tubes.append(details)
        self._status.set(ka_status.TOPIC_COLLABORATION,
                         ka_status.SUB_TUBES, self._new_tubes)
        if (tube_type == telepathy.TUBE_TYPE_DBUS and service == kandidtube.SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(tube_id)
            tube_conn = TubeConnection(self.telepathy_conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                tube_id,
                group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
            population_controller = self._controller.find_page('PopulationController')
            if population_controller is not None:
                self.kandidtube = population_controller.on_new_tube(
                                                           self.telepathy_conn,
                                                           tube_conn,
                                                           self._get_my_id(),
                                                           self.initiating,
                                                           self.get_buddy_by_handle)

    def _on_buddy_joined (self, joined_activity, buddy):
        """Called when a buddy joins the shared activity.
        """
        ka_debug.info('Buddy [%s] joined' % buddy.props.nick)
        self._joined_buddies |= set([buddy.props.nick])
        self._status.set(ka_status.TOPIC_COLLABORATION,
                        ka_status.SUB_BUDDIES_JOINED, self._joined_buddies)
 
    def _on_buddy_left (self, left_activity, buddy):
        """Called when a buddy leaves the shared activity.
        """
        ka_debug.info('Buddy [%s] left' % buddy.props.nick)
        self._joined_buddies -= set([buddy.props.nick])
        self._status.set(ka_status.TOPIC_COLLABORATION,
                        ka_status.SUB_BUDDIES_JOINED, self._joined_buddies)

    def _get_my_id(self):
        """Get my channel ID and nick."""
        group = self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP]
        my_csh = group.GetSelfHandle()
        my_buddy = self.get_buddy_by_handle(my_csh)
        my_nick = my_buddy.props.nick if my_buddy is not None else '?'
        ka_debug.info('I am %s, my handle in that group is %u' % \
                                                           (my_nick, my_csh))
        return my_nick, my_csh

    def get_buddy_by_handle(self, cs_handle):
        """Get a Buddy from a channel specific handle."""
        try:
            ka_debug.info('Trying to find owner of handle %u...' % cs_handle)
            group = self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP]
            my_csh = group.GetSelfHandle()
            ka_debug.info('My handle in that group is %u' % my_csh)
            if my_csh == cs_handle:
                handle = self.telepathy_conn.GetSelfHandle()
                ka_debug.info('CS handle %u belongs to me, %u' % \
                            (cs_handle, handle))
            elif group.GetGroupFlags() & telepathy.CHANNEL_GROUP_FLAG_CHANNEL_SPECIFIC_HANDLES:
                handle = group.GetHandleOwners([cs_handle])[0]
                ka_debug.info('CS handle %u belongs to %u' % \
                           (cs_handle, handle))
            else:
                handle = cs_handle
                ka_debug.info('non-CS handle %u belongs to itself' % handle)
                #TODO: deal with failure to get the handle owner
    
            return self.pservice.get_buddy_by_telepathy_handle(
                self.telepathy_conn.service_name,
                self.telepathy_conn.object_path, handle)
        except:
            ka_debug.err('buddy added failed [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        return None


