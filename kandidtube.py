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

import hashlib 
import base64

from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

import ka_debug
import ka_status

SERVICE = 'net.sourceforge.kandid'
IFACE = SERVICE
PATH = '/net/sourceforge/kandid/minimal'

SEND_POPULATION = 'P'
SEND_PROTOZOON = 'I'

class KandidTube(ExportedGObject):
    """The bit that talks over the tubes"""

    def __init__(self, controller, telepathy_conn, tube, my_id,
                 is_initiator, get_buddy):
        super(KandidTube, self).__init__(tube, PATH)
        self._controller = controller
        self._telepathy_conn = telepathy_conn
        self._tube = tube
        self._my_id = my_id
        self._is_initiator = is_initiator
        self.get_buddy_by_handle = get_buddy  # Converts handle to Buddy object
        self._entered = False  # Have we set up the tube?
        self._participating_buddies = set([])
        self._status = ka_status.Status.instance()
        self._tube.watch_participants(self.on_participant_change)

    def on_participant_change(self, added, removed):
        if added:
            ka_debug.info('Tube: Added participants: %r' % added)
        if removed:
            ka_debug.info('Tube: Removed participants: %r' % removed)
        for handle, bus_name in added:
            ka_debug.info('participant add: [%s] [%s] ' % (handle, bus_name))
            buddy = self.get_buddy_by_handle(handle)
            if buddy is not None:
                ka_debug.info('Tube: Handle %u (Buddy [%s]) was added' % \
                                   (handle, buddy.props.nick))
                self._participating_buddies |= set([buddy.props.nick])
        for handle in removed:
            buddy = self.get_buddy_by_handle(handle)
            if buddy is not None:
                nickname = buddy.props.nick
                ka_debug.info('Buddy [%s] was removed' % nickname)
                self._participating_buddies -= set([nickname])
        self._status.set(ka_status.TOPIC_COLLABORATION,
                         ka_status.SUB_BUDDIES_PARTICIPATING,
                         self._participating_buddies)
        if not self._entered:
            if self._is_initiator:
                ka_debug.info("I'm initiating the tube, will watch for hellos.")
                self.add_hello_handler()
                self.add_publish_handler()
            else:
                ka_debug.info('Hello, everyone! What did I miss?')
                self.Hello()
                self.add_publish_handler()
        self._entered = True

    def add_hello_handler(self):
        ka_debug.info('I am initiating. Adding hello handler.')
        self._tube.add_signal_receiver(self.on_hello, 'Hello',
                                IFACE, path=PATH, sender_keyword='sender')

    def add_publish_handler(self):
        ka_debug.info('I am entered. Adding input handler.')
        self._tube.add_signal_receiver(self.on_publish_protozoon, 'PublishProtozoon',
                                IFACE, path=PATH, sender_keyword='sender')

    @signal(dbus_interface=IFACE, signature='')
    def Hello(self):
        """Say Hello to whoever else is in the tube."""
        ka_debug.info('I said Hello.')

    def on_hello(self, sender=None):
        """Somebody helloed me. Send them my population."""
        if sender == self._tube.get_unique_name():
            # sender is my bus name, so ignore my own signal
            return
        ka_debug.info('on_hello: Newcomer [%s] has joined. World them.' % sender)
        self.send_population(self._controller.serialize_model(), sender)

    def publish_protozoon(self, code_element):
        code_element_base64 = base64.b64encode(code_element)
        code_md5 = hashlib.md5(code_element).hexdigest() 
        ka_debug.info('publish_protozoon: Sent %u bytes, type: [%s] md5: [%s]' % \
                   (len(code_element), SEND_PROTOZOON, code_md5))
        self.PublishProtozoon(SEND_PROTOZOON, code_element_base64, code_md5)

    @signal(dbus_interface=IFACE, signature='sss')
    def PublishProtozoon(self, code_type, code_element, code_md5):
        """Send protozoon."""
        ka_debug.info('PublishProtozoon: I published %u bytes, type: [%s] md5: [%s]' \
                   % (len(code_element), code_type, code_md5))

    def on_publish_protozoon(self, code_type, code_element_base64, code_md5,
                             sender=None):
        """Somebody published. Process received parameters."""
        if sender == self._tube.get_unique_name():
            # sender is my bus name, so ignore my own signal
            return
        code_element = base64.b64decode(code_element_base64)
        ka_debug.info('on_publish_protozoon: I got %u bytes, type: [%s] md5: [%s]' \
                   % (len(code_element), code_type, code_md5))
        if hashlib.md5(code_element).hexdigest() == code_md5:
            nick = self._map_to_nick(sender)
            self._controller.on_received(code_type, code_element, nick)
        else:
            ka_debug.err('Somebody called me with a corrupt data model.')

    def send_population(self, code_element, sender=None):
        code_element_base64 = base64.b64encode(code_element)
        code_md5 = hashlib.md5(code_element).hexdigest() 
        ka_debug.info('send_population: Sent %u bytes, type: [%s] md5: [%s]' % \
                   (len(code_element), SEND_POPULATION, code_md5))
        self._tube.get_object(sender, PATH).SendPopulation(SEND_POPULATION,
                                                           code_element_base64,
                                                           code_md5)

    @method(dbus_interface=IFACE, in_signature='sss', out_signature='',
            sender_keyword='sender')
    def SendPopulation(self, code_type, code_element_base64, code_md5, sender=None):
        """Send to all participants."""
        code_element = base64.b64decode(code_element_base64)
        ka_debug.info('SendPopulation: Received %u bytes, type: [%s] md5: [%s]' \
                   % (len(code_element), code_type, code_md5))
        if hashlib.md5(code_element).hexdigest() == code_md5:
            nick = self._map_to_nick(sender)
            self._controller.on_received(code_type, code_element, nick)
        else:
            ka_debug.err('Somebody called me with a corrupt data model.')

    #TODO How to map from sender to buddy / nick?
    def _map_to_nick(self, sender):
        nick = '?'
#        nick = self._telepathy_conn[
#                telepathy.CONN_INTERFACE_ALIASING].RequestAliases([sender])[0]
#        try:
#            # One to one XMPP chat
#            nick = self._telepathy_conn[
#                telepathy.CONN_INTERFACE_ALIASING].RequestAliases([sender])[0]
#        except:
#            # Normal sugar MUC chat
#            nick = self._get_buddy(sender).get_property('nick')
#        part = ''
#        try:
#            part = sender.split('.')[0]
#            part = part[1:]
#            buddy = self._get_buddy(int(part))
#            ka_debug.info('Mapping: [%s] to [%s]' % \
#                                         (sender, buddy.get_property('nick')))
#        except:
#            ka_debug.err('map_to_buddy failed [%s] [%s] [%s] [%s]' % \
#                         (sys.exc_info()[0], sys.exc_info()[1], sender, part))
#            traceback.print_exc(file=sys.__stderr__)
#        ka_debug.info('Mapping: [%s] to [%s]' % (sender, nick))
        return nick
