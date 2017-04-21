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

import cairo
import gtk
import gobject

import ka_debug
import ka_task
import ka_controller
import ka_extensionpoint
import model_population
import model_random
import model_history
import kandidtube
import ka_status
import ka_incoming
import ka_preference

POPULATION_CAPACITY = 12

class PopulationController(object):
    """
    inv: self._widget_list is not None
    """

    def __init__(self, controller, widget_list, activity_root, started_anew):
        """
        pre: controller is not None
        pre: widget_list is not None
        """
        self._controller = controller
        self._widget_list = widget_list
        self._activity_root = activity_root
        self._anew = started_anew
        self._tube = None
        self.surface_cache = {}
        self._status = ka_status.Status.instance()
        self._gencount = 0
        self._task_lock = -1
        self.model = None
        self.incoming = ka_incoming.KandidIncoming(self, widget_list)
        self.position = 100

    def close(self):
        """Clean up"""
        pass

    def _create_box_toolbar(self):
        """ """
        toolbarButtonbox = gtk.VButtonBox()
        breedGenerationButton = gtk.Button(_('Breed'))
        toolbarButtonbox.pack_start(breedGenerationButton, expand=True, fill=True)
        self._widget_list.remember('breedGenerationButton', breedGenerationButton)

        flurryLabel = gtk.Label(_('Flurry rate:'))
        toolbarButtonbox.pack_start(flurryLabel, expand=True, fill=True)
        
        adjustmentSpinButton = gtk.Adjustment(value=0, lower=0, upper=9,
                                          step_incr=1, page_incr=3, page_size=0)
        flurrySpinButton = gtk.SpinButton(adjustment=adjustmentSpinButton)
        toolbarButtonbox.pack_start(flurrySpinButton, expand=True, fill=True)
        self._widget_list.remember('flurrySpinButton', flurrySpinButton)
        
        hseparator1 = gtk.HSeparator()
        toolbarButtonbox.pack_start(hseparator1, expand=True, fill=True)
        
        randomGenerationButton = gtk.Button(_('Random'))
        toolbarButtonbox.pack_start(randomGenerationButton, expand=True, fill=True)
        self._widget_list.remember('randomGenerationButton', randomGenerationButton)
        return toolbarButtonbox

    def _create_box_cell(self, index):
        """ """
        self._create_menue_protozoon(index)
        cellBox = gtk.VBox()
        cellBox.set_border_width(3)
        self._widget_list.remember('vbox_' + str(index), cellBox)
        hBox = gtk.HBox()
        openPopupButton = gtk.Button()
        self._widget_list.remember('open_popup_' + str(index), openPopupButton)
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
        openPopupButton.add(arrow)
        hBox.pack_start(openPopupButton, expand=False, fill=False)
        fitnessScale = gtk.HScale()
        self._widget_list.remember('fitness_' + str(index), fitnessScale)
        fitnessScale.set_value_pos(gtk.POS_RIGHT)
        fitnessScale.set_digits(0)
        fitnessScale.set_adjustment(gtk.Adjustment(value=1.0, lower=0.0, upper=10.0, 
                                  step_incr=1.0, page_incr=1.0, page_size=1.0))
        hBox.pack_start(fitnessScale, expand=True, fill=True)
        cellBox.pack_start(hBox, expand=False, fill=True)
        
        aspectframe = gtk.AspectFrame()
        drawingarea = gtk.DrawingArea()
        self._widget_list.remember('drawingarea_' + str(index), drawingarea)
        aspectframe.add(drawingarea)
        cellBox.pack_start(aspectframe, expand=True, fill=True)
        return cellBox

    def _create_table_population(self, rows, cols):
        """ """
        populationTable = gtk.Table(cols, rows, homogeneous=False)
#        self._widget_list.remember('populationTable', populationTable)
        index = 0
        for row in xrange(rows):
            for col in xrange(cols):
                populationTable.attach(self._create_box_cell(index),
                                       0+col, 1+col,
                                       0+row, 1+row,
                                       xoptions=gtk.EXPAND|gtk.FILL,
                                       yoptions=gtk.EXPAND|gtk.FILL, )
                index += 1
        return populationTable

    def create_gui(self):
        """ """
        
        page = gtk.HBox()
        self._widget_list.remember('populationPage', page)
        controlBox = gtk.VBox()
        controlBox.set_border_width(3)
        controlBox.pack_start(self._create_box_toolbar(), expand=False, fill=False)
        controlBox.pack_start(gtk.Alignment(xalign=0.0, yalign=0.5, xscale=0.0, yscale=1.0))
        controlBox.pack_end(self.incoming.create_gui(), expand=True, fill=True)
        page.pack_start(controlBox, expand=False, fill=True)
        page.pack_start(self._create_table_population(3, 4), expand=True, fill=True)
        return page, gtk.Label(_('Population'))

    def _create_menue_protozoon(self, index):
        """ """
        menu = gtk.Menu()
        self._widget_list.remember('protozoon_menu_' + str(index), menu)

        menuitem = gtk.MenuItem(_('My favorite'))
        self._widget_list.remember('favorite_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_('Awful bore'))
        self._widget_list.remember('awfull_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_('Zoom'))
        self._widget_list.remember('zoomprotozoon_menuitem_' + str(index), menuitem)
        menu.append(menuitem)

        submenu = gtk.Menu()
        sub1 = gtk.MenuItem(_('Publish to my friends'))
        self._widget_list.remember('publishprotozoon_menuitem_' + str(index), sub1)
        submenu.append(sub1)
        sub2 = gtk.MenuItem(_('Send image to journal'))
        self._widget_list.remember('exportpng_menuitem_' + str(index), sub2)
        submenu.append(sub2)
        menuitem = gtk.MenuItem(_('Send'))
        menuitem.set_submenu(submenu)
        menu.append(menuitem)

        submenu = gtk.Menu()
        sub1 = gtk.MenuItem(_('Explain details'))
        self._widget_list.remember('explain_menuitem_' + str(index), sub1)
        submenu.append(sub1)
        sub2 = gtk.MenuItem(_('Show ancestors'))
        self._widget_list.remember('ancestors_menuitem_' + str(index), sub2)
        submenu.append(sub2)
        menuitem = gtk.MenuItem(_('Explain'))
        menuitem.set_submenu(submenu)
        menu.append(menuitem)

        menu.show_all()
        return menu
    
    def autoconnect_events(self):
        """Auto connect zoom view."""
        self._widget_list.get_widget('kandidNotebook') \
                           .connect('switch-page', self.on_notebook_switch_page)
        self._widget_list.get_widget('breedGenerationButton') \
                                 .connect('clicked', self.on_breed_generation)
        self._widget_list.get_widget('randomGenerationButton') \
                                 .connect('clicked', self.on_random_generation)
        self._widget_list.get_widget('flurrySpinButton') \
                                 .connect('value-changed', self.on_flurry_value_changed)
        for cell_index in xrange(POPULATION_CAPACITY):
            six = str(cell_index)
            self._widget_list.get_widget('drawingarea_' + six) \
                        .connect('expose-event', self.on_drawingarea_expose)
            self._widget_list.get_widget('drawingarea_' + six) \
                        .connect('size-allocate', self.on_drawingarea_size_allocate)
            self._widget_list.get_widget('fitness_' + six) \
                        .connect('value-changed', self.on_fitness_value_changed)
            menu = self._widget_list.get_widget('protozoon_menu_' + six)
            self._widget_list.get_widget('open_popup_' + six) \
                        .connect_object('button-press-event', self.on_protozoon_popup, menu)
            self._widget_list.get_widget('favorite_menuitem_' + six) \
                        .connect('activate', self.on_favorite_activate)
            self._widget_list.get_widget('awfull_menuitem_' + six) \
                        .connect('activate', self.on_awfull_activate)
            self._widget_list.get_widget('zoomprotozoon_menuitem_' + six) \
                        .connect('activate', self.on_zoomprotozoon_activate)
            self._widget_list.get_widget('publishprotozoon_menuitem_' + six) \
                        .connect('activate', self.on_publishprotozoon_activate)
            self._widget_list.get_widget('exportpng_menuitem_' + six) \
                        .connect('activate', self.on_exportpng_activate)
            self._widget_list.get_widget('explain_menuitem_' + six) \
                        .connect('activate', self.on_explain_activate)
            self._widget_list.get_widget('ancestors_menuitem_' + six) \
                        .connect('activate', self.on_ancestors_activate)

        self.incoming.autoconnect_events()
        gobject.timeout_add(1000, self.on_timer)
        
    def localize(self):
        """A dummy"""
        pass

    def activate_gui(self):
        """ """
        self.incoming.update_incomming_gui()

    def _update_model(self, in_model):
        if in_model:
#            ka_debug.info('update model')
            self.model = in_model
#            self.model._state = model_population.STATE_EVOLVED
            self.surface_cache = {}
        self._update_population_gui()

    def _update_population_gui(self):
        """
        pre: self.model is not None
        """
        # update fitness
        for cell_index in range(self.model.size):
            strix = str(cell_index)
            key = 'fitness_#'.replace('#', strix)
            self._widget_list.get_widget(key). \
                set_value(self.model.fitness[cell_index])
        # update flurry
        self._widget_list.get_widget('flurrySpinButton'). \
                                          set_value(self.model.flurry_rate)
        self._update_generate_buttons()

    def _update_generate_buttons(self):
        """
        update buttons
        """
        is_sensitive = ka_task.GeneratorTask.is_completed()
        if is_sensitive and self.model is not None:
            dummy, moderate, poor = self.model.classify()
            is_sensitive = len(poor) > 0 and len(moderate) > 0
#        ka_debug.info('_update_generate_buttons %s' % is_sensitive)
        self._widget_list.get_widget('breedGenerationButton'). \
                                                  set_sensitive(is_sensitive)
        self._widget_list.get_widget('randomGenerationButton'). \
                                                  set_sensitive(is_sensitive)

    def _draw_from_cache(self, widget, cell_index):
        if self.surface_cache.has_key(cell_index):
#            ka_debug.info('_draw_from_cache: ' + widget.name + ' '
#                          + str(cell_index))
            ctx = ka_controller.create_context(widget)
            ctx.set_operator(cairo.OPERATOR_SOURCE)
            ctx.set_source_surface(self.surface_cache[cell_index])
            ctx.paint()

    def on_notebook_switch_page(self, *args):
        """Test if status page will be displayed.
        pre: len(args) >= 3
        """
        if self._anew:
            visible = args[2] == self._controller.find_page_number('PopulationController')
#            ka_debug.info('on_notebook_switch_page %s %s %s' % (self.__class__, visible, args[2]))
            if visible and self.model is None:
                self._anew = False
                self.model = model_population.KandidModel(POPULATION_CAPACITY)
                self.model.randomize()
                self.start_all_calculations()

    def on_drawingarea_expose(self, widget, event):
        """ Repaint image of a single protozoon inside population area.
        pre: widget is not None
        """
        # draw precalculated protozoon stored in the surface cache. 
#        ka_debug.info('on_drawingarea_expose: ' + widget.name + ' ' 
#                      + str(widget.allocation.width) 
#                      + 'x' + str(widget.allocation.height))
        self._draw_from_cache(widget, ka_controller.name_to_index(widget.name))

    def on_drawingarea_size_allocate(self, widget, event):
        """ New size for drawing area available.
        pre: widget is not None
        """
#        ka_debug.info('on_drawingarea_size_allocate: ' + widget.name + ' ' 
#                      + str(widget.allocation.width) 
#                      + 'x' + str(widget.allocation.height))
        if self.model is not None:
            self.start_calculation([ka_controller.name_to_index(widget.name)])

    def on_fitness_value_changed(self, *args):
        """
        pre: len(args) >= 1
        """
#        ka_debug.info('on_fitness_value_changed %f [%s]' % 
#                   (args[0].get_value(), args[0].get_name()))
        self.model.fitness[ka_controller.name_to_index(args[0].get_name())] \
            = args[0].get_value()
        self._update_population_gui()

    def on_breed_generation(self, *args):
        if ka_task.GeneratorTask.is_completed():
#            ka_debug.info('on_breed_generation entry')
            self._gencount += 1
            ka_task.GeneratorTask(self.task_breed_generation, 
                                  self.on_model_completed,
                                  'breed_'+str(self._gencount)).start()
#            ka_debug.info('on_breed_generation exit')
        else:
            ka_debug.info('on_breed_generation ignored')
    
    def on_random_generation(self, *args):
        if ka_task.GeneratorTask.is_completed():
#            ka_debug.info('on_random_generation entry')
            self._gencount += 1
            ka_task.GeneratorTask(self.task_random_generation, 
                                  self.on_model_completed,
                                  'random_'+str(self._gencount)).start()
#            ka_debug.info('on_random_generation exit')
        else:
            ka_debug.info('on_random_generation ignored')
    
    def on_model_completed(self, *args):
        """
        pre: len(args) == 1
        """
#        ka_debug.info('on_model_completed entry')
        for cell_index in args[0]:
            self._widget_list.get_widget('vbox_' + str(cell_index)). \
                                                          set_sensitive(False)
        self.start_calculation(args[0])
#        ka_debug.info('on_model_completed exit')

    def on_timer(self, *args):
        compl = ka_task.GeneratorTask.is_completed()
        if self._task_lock == -1:
#            ka_debug.info('on_timer %s %u' % (compl, self._task_lock))
            self._update_generate_buttons()
            self._task_lock = 0 if compl else 1 
        elif self._task_lock == 1:
#            ka_debug.info('on_timer %s %u' % (compl, self._task_lock))
            self._update_generate_buttons()
            self._task_lock = 0 if compl else 1 
        elif self._task_lock == 0: # and not compl:
#            ka_debug.info('on_timer %s %u' % (compl, self._task_lock))
            self._update_generate_buttons()
            self._task_lock = 1
        return True

    def activate_page(self):
        """
        Page will be displayed. Prepare page.
        """
        if self.model is None:
            self.model = model_population.KandidModel(POPULATION_CAPACITY)
            self.model.randomize()
            self.start_all_calculations()

    def start_all_calculations(self):
        """
        pre: self.model is not None
        """
#        ka_debug.print_call_stack()
#        if self.model is None:
#            self.model = model_population.KandidModel(POPULATION_CAPACITY)
#            ka_debug.info('randomize model %u' % (self.model.size))
#            self.model.randomize()
#        ka_debug.info('start_all_calculations %u' % (self.model.size))
        self.start_calculation([i for i in range(self.model.size)])

    def start_calculation(self, concerned):
        """
        pre: len(concerned) > 0
        pre: forall(concerned, lambda x: 0 <= x <= self.model.size)
        """
        for cell_index in concerned:
            widget_name = 'drawingarea_' + str(cell_index)
            widget = self._widget_list.get_widget(widget_name)
            task = ka_task.GeneratorTask(self.task_render,
                                         self.on_image_completed,
                                         widget_name)
            task.start(self.model.protozoans[cell_index], cell_index,
                       widget.allocation.width, widget.allocation.height)
#            ka_debug.info('start_calculation %ux%u for %s' % 
#              (widget.allocation.width, widget.allocation.height, widget.name))

    def task_breed_generation(self, task, *args, **kwargs):
        """
        pre: len(args) == 0
        """
#        ka_debug.info('task_breed_generation entry')
        new_indices = self.model.breed_generation()
#        ka_debug.info('task_breed_generation exit')
        return new_indices

    def task_breed_single(self, task, *args, **kwargs):
        """
        pre: len(args) == 1
        """
#        ka_debug.info('task_breed_single entry')
        new_indices = self.model.breed_single(args[0])
#        ka_debug.info('task_breed_single exit')
        return new_indices

    def task_random_generation(self, task, *args, **kwargs):
        """
        pre: len(args) == 0
        """
#        ka_debug.info('task_random_generation entry')
        new_indices = self.model.random()
#        ka_debug.info('task_random_generation exit')
        return new_indices

    def task_render(self, task, *args, **kwargs):
        """
        pre: len(args) == 4
        """
        protozoon, cell_index, width, height = \
                                             args[0], args[1], args[2], args[3]
#        ka_debug.info('task_render entry: ' + str(cell_index))
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        protozoon.render(task, ctx, width, height)
        self.surface_cache[cell_index] = surface
        history = model_history.KandidHistory.instance()
        history.link_surface(protozoon.get_unique_id(), surface)
#        ka_debug.info('task_render exit: ' + str(cell_index))
        return cell_index

    def on_image_completed(self, *args):
#        ka_debug.info('on_image_completed: ' + str(args[0]))
        cell_index = args[0]
        widget = self._widget_list.get_widget('drawingarea_'
                                                    + str(cell_index))
        self._draw_from_cache(widget, cell_index)
        self._widget_list.get_widget('vbox_' + str(cell_index)). \
                                                            set_sensitive(True)
        self._widget_list.get_widget('fitness_' + str(cell_index)). \
                                      set_value(self.model.fitness[cell_index]) 

    def on_flurry_value_changed(self, *args):
        """
        pre: len(args) >= 1
        pre: 0 <= args[0].get_value() <= 9
        """
#        ka_debug.info('on_flurry_value_changed [%s]' % args[0].get_value())
        model_random.set_flurry(args[0].get_value())

    def on_protozoon_popup(self, widget, event):
#        ka_debug.info('on_protozoon_popup: ' + widget.name)
        self._show_popup(widget, event, \
                         'protozoon_menu_%u' % ka_controller.name_to_index(widget.name))

    def _show_popup(self, widget, event, menu):
#        ka_debug.info('%s [%s]' % (menu, widget.name))
        index = ka_controller.name_to_index(menu)
        self._widget_list.get_widget('favorite_menuitem_' + str(index)). \
                            set_sensitive(self.model.fitness[index] < 9.0)
        dummy, moderate, dummy = self.model.classify()
        is_sensitive = len(moderate) > 0
        self._widget_list.get_widget('awfull_menuitem_' + str(index)). \
                            set_sensitive(is_sensitive)
        popup_menu = self._widget_list.get_widget(menu)
        popup_menu.popup(None, None, None, event.button, event.time)

    def on_publishprotozoon_activate(self, *args):
        """Publish single protozoon to all other buddies.
        pre: len(args) >= 1
        """
        ka_debug.info('on_publishprotozoon_activate [%s]' % args[0].get_name())
        if self._tube:
            proto = self.model.protozoans[ka_controller.name_to_index(args[0].get_name())]
            self._tube.publish_protozoon(model_population.to_buffer(proto))

    def on_exportpng_activate(self, *args):
        """Publish single protozoon to all other buddies.
        pre: len(args) >= 1
        """
        ka_debug.info('on_exportpng_activate [%s]' % args[0].get_name())
        pix = ka_controller.name_to_index(args[0].get_name())
        exporter = ka_extensionpoint.create('exporter_png',
                                            self.model.protozoans[pix],
                                            self._activity_root)
        preference = ka_preference.Preference.instance()
        export_size = preference.get(ka_preference.EXPORT_SIZE)
        exporter.export(*export_size)

    def on_zoomprotozoon_activate(self, *args):
        """Publish single protozoon to all other buddies.
        pre: len(args) >= 1
        """
        ka_debug.info('on_zoomprotozoon_activate [%s]' % args[0].get_name())
        zoom_controller = self._controller.find_page('ZoomController')
        if zoom_controller is not None:
            pix = ka_controller.name_to_index(args[0].get_name())
            zoom_controller.start_calculation(self.model.protozoans[pix].copy())

    def on_explain_activate(self, *args):
        """Publish single protozoon to all other buddies.
        pre: len(args) >= 1
        """
        ka_debug.info('on_explain_activate [%s]' % args[0].get_name())
        details_controller = self._controller.find_page('DetailsController')
        if details_controller is not None:
            pix = ka_controller.name_to_index(args[0].get_name())
            details_controller.start_calculation(self.model.protozoans[pix])

    def on_ancestors_activate(self, *args):
        """Publish single protozoon to all other buddies.
        pre: len(args) >= 1
        """
        ka_debug.info('on_ancestors_activate [%s]' % args[0].get_name())
        ancestors_controller = self._controller.find_page('AncestorsController')
        if ancestors_controller is not None:
            pix = ka_controller.name_to_index(args[0].get_name())
            ancestors_controller.start_calculation(self.model.protozoans[pix])

    def on_favorite_activate(self, *args):
        """Set best ranking for this protozoon.
        pre: len(args) >= 1
        """
#        ka_debug.info('on_favorite_activate [%s]' % args[0].get_name())
        self.model.raise_fitness(ka_controller.name_to_index(args[0].get_name()))
        self._update_population_gui()

    def on_awfull_activate(self, *args):
        """Set last ranking for this protozoon.
        pre: len(args) >= 1
        """
#        ka_debug.info('on_awfull_activate [%s]' % args[0].get_name())
        index = ka_controller.name_to_index(args[0].get_name())
        self.model.reduce_fitness(index)
        self._update_population_gui()
        ka_task.GeneratorTask(self.task_breed_single, 
                              self.on_model_completed,
                              args[0].get_name()).start(index)

    def on_received(self, code_type, code_element, nick):
        """Update population or protozoon preview when received from others."""
        ka_debug.info('on_received: Received %u bytes, type: [%s], from: [%s]' % \
                   (len(code_element), code_type, nick))
        if code_type == kandidtube.SEND_POPULATION:
            self._status.set(ka_status.TOPIC_COLLABORATION,
                             ka_status.SUB_RECEIVED,
                             'Population from ' + nick)
            if self.is_overwrite_allowed():
                self._update_model(model_population.from_buffer(code_element))
                self.start_all_calculations()
            else:
                in_model = model_population.from_buffer(code_element)
                max_fit, best_ix, second_ix = -1, -1, -1
                for index, fit in enumerate(in_model.fitness):
                    if fit > max_fit:
                        second_ix = best_ix
                        best_ix, max_fit = index, fit
                if best_ix >= 0:
                    self.incoming.append_protozoon(in_model.protozoans[best_ix])
                if second_ix >= 0:
                    self.incoming.append_protozoon(in_model.protozoans[second_ix])
                if best_ix >= 0 or second_ix >= 0:
                    ka_debug.info("I've already an evolved population, proposing protozoon %d, %d." % (best_ix, second_ix))
                else:
                    ka_debug.info("I've already an evolved population, ignore incoming protozoon.")
        elif code_type == kandidtube.SEND_PROTOZOON:
            ka_debug.info('Proposing protozoon.')
            self._status.set(ka_status.TOPIC_COLLABORATION,
                             ka_status.SUB_RECEIVED,
                             'Protozoon from ' + nick)
            self.incoming.append_protozoon(model_population.from_buffer(code_element))
        else:
            ka_debug.err('Somebody called me using an illegal type [%s]'
                          % code_type)

    def on_new_tube(self, telepathy_conn, tube, my_id, is_initiator, get_buddy):
        """Creates communication object and sends population
        pre: tube > 0
        pre: get_buddy is not None
        """
        self._tube = kandidtube.KandidTube(self, telepathy_conn, tube, my_id,
                                           is_initiator, get_buddy)

# data model and persistence
    def is_overwrite_allowed(self):
        """Preserve an already evolved population from over writing."""
        return self.model.is_overwrite_allowed()

    def serialize_model(self):
        """Serialize population to a string buffer."""
        return model_population.to_buffer(self.model)

    def read_file(self, file_path):
        """Delegate reading from journal to data model
        pre: (file_path is not None) and (len(file_path) >= 1)
        """
        model = model_population.read_file(file_path)
        if model is not None:
            self._update_model(model)
            self._controller.switch_page('PopulationController')
            self.start_all_calculations()
        else:
            self._controller.switch_page('GettingstartedController')

    def write_file(self, file_path):
        """Delegate writing data model to journal
        pre: (file_path is not None) and (len(file_path) >= 1)
        """
        model_population.write_file(file_path, self.model)
