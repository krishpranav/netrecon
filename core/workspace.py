#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import os
import signal
import datetime
import gi
import copy

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from core.extensions import karmaEngine
from core.widgets import *

import core.file_filters as file_filters
import core.icons as iconslib

class Logger():
	def __init__(self, database):
		""" log box """
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/logger.glade")

		self.database = database

		# log list
		self.notebook = builder.get_object("log-notebook")
		self.log_box = builder.get_object("log-box")
		self.scrolled = builder.get_object("scrolled")

		self.log_liststore = Gtk.ListStore(int, int, str, str, int, str, str, int, str, int)
		self.log_tree = Gtk.TreeView(model=self.log_liststore)
		self.id = 0

		self.extensions  = karmaEngine()

		for i, column_title in enumerate(["#","Status","Start time", "End time", "Pid", "Target", "Task"]):
			if i == 1:

				renderer = Gtk.CellRendererProgress()

				column = Gtk.TreeViewColumn(column_title, renderer, value=1 )
				column.set_min_width(100)
				column.add_attribute(renderer, "pulse", 7)				#renderer.text = " "
			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)
		
			self.log_tree.append_column(column)

		# get logs from the database
		self.refresh(self.database)
		self.log_tree.show()

		# pulse progress bar every second
		GObject.timeout_add(100, self._pulse_progressbars)

		# connect events
		self.log_tree.connect("button_press_event", self.mouse_click)
		self.log_tree.connect("row-activated", self.on_row_activated)
		self.log_tree.connect('size-allocate', self._scroll)

		# multi selection 
		selection = self.log_tree.get_selection()
		selection.set_mode(Gtk.SelectionMode.MULTIPLE)

		self.log_box.add(self.log_tree)

	def _scroll(self, widget, event, data=None):
		# auto scroll
		adj = self.log_box.get_vadjustment()
		adj.set_value( adj.get_upper() - adj.get_page_size() )


	def refresh(self, db):
		# refresh the log tree with the new database
		self.log_liststore.clear()
	
		self.database = db
		logs = self.database.get_logs()
		i = 0
	
		for log in logs:
			
			self.log_liststore.append([log.id, 0, log.start_time, log.end_time, log.pid, log.target, log.title, GObject.G_MAXINT, log.extension, i])
			i += 1
	
		self.log_tree.show()
	
		return True

	def delete_log(self, widget, logs_selected):
		""" delete a log from the database """

		# ask for confirmation with a dialog
		dialog = Gtk.MessageDialog(Gtk.Window(), 0, Gtk.MessageType.WARNING,
			Gtk.ButtonsType.OK_CANCEL, "Delete log(s)?")
		dialog.format_secondary_text(
			"This operation will be irreversible.")
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			dialog.close()

			for log_id in logs_selected:

				self.database.remove_log(log_id)

				model = self.log_tree.get_model()

				for row in model:
					if row[0] == log_id:
						self.log_liststore.remove(row.iter)


		elif response == Gtk.ResponseType.CANCEL:
			dialog.close()

	def add_log(self, pid, title, target, extension, id):
		""" add a task log """
		self.id -= 1	

		self.log_liststore.append([-int(id), 0, str(datetime.datetime.now()).split(".")[0], " ", pid, target, title, 1, extension, len(self.log_liststore)])
		
		return self.id

	def complete_log(self, id_task, output):
		""" set at 100% the progressbar """

		id_task = -int(id_task)

		model = self.log_tree.get_model()

		for t in model:
			
			if t[0] == id_task:
				row = t

				id_r      = row[0]
				start_dat = row[2]
				end_dat   = str(datetime.datetime.now()).split(".")[0]
				pid       = row[4]
				target    = row[5]
				title     = row[6]
				extension = row[8]
				path      = row[9]

				iter = model.get_iter(Gtk.TreePath.new_from_string(str(path)))

				progress_bar = 0

				id = self.database.add_log(pid, start_dat, end_dat, title, target, output, extension)
				self.log_liststore.set_value(iter, 0, id)
				self.log_liststore.set_value(iter, 7, GObject.G_MAXINT)
				self.log_liststore.set_value(iter, 3, end_dat)


	def _pulse_progressbars(self):
		# progress bars task running animation

		model = self.log_tree.get_model()

		for a in range(0,len(model)):
			if len(self.log_liststore[model.get_iter(Gtk.TreePath.new_from_string(str(a)))][3]) < 3:

				self.log_liststore[model.get_iter(Gtk.TreePath.new_from_string(str(a)))][-3] += 1

		return True

	def on_row_activated(self, listbox, cell, listboxrow):

		(model, pathlist) = self.log_tree.get_selection().get_selected_rows()
		for path in pathlist :

			tree_iter = model.get_iter(path)
			log_id   = model.get_value(tree_iter,0)

			self.open_log(log_id)		

	
	def open_log(self, log_id):

		try:

			log = self.database.get_logs(str(log_id))

			scrolledwindow = self.extensions.get_log(log.extension, log.output)

			# generate and fill the toolbox
			builder	 = Gtk.Builder()
			builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/logger.glade")

			toolbox        = builder.get_object("showlog-box")
			lbl_start_time = builder.get_object("start-time-label")
			lbl_end_time   = builder.get_object("end-time-label")
			lbl_pid        = builder.get_object("pid-label") 
			lbl_name       = builder.get_object("extension-name-label")
			lbl_target     = builder.get_object("extension-target-label")
			export_button  = builder.get_object("export-button")
			delete_button  = builder.get_object("delete-button")

			lbl_start_time.set_text(log.start_time)
			lbl_end_time.set_text(log.end_time)
			lbl_pid.set_text(str(log.pid))
			lbl_name.set_text(log.extension)
			lbl_target.set_text(log.target)

			export_button.connect("clicked", self.export_log, log.id)
			delete_button.connect("clicked", self.delete_log, log.id)
		
			box = Gtk.Box()
			box.pack_start(scrolledwindow, True, True, 0)

			# box label + close button for extension
			box_label = Gtk.Box(spacing=6)
			box_label.add( Gtk.Label("%s %s" % (log.title, log.target)) )
			close_image = Gtk.Image.new_from_icon_name( "gtk-delete", Gtk.IconSize.MENU )
			close_button = Gtk.Button()
			close_button.set_relief(Gtk.ReliefStyle.NONE)
			close_button.add(close_image)
			box_label.add( close_button )

			toolbox.add(box)

			# close task window option
			close_button.connect("clicked", self.close_log_tab, toolbox)

			self.notebook.append_page(toolbox, box_label)
			self.notebook.set_current_page(-1)

			box.show()
			toolbox.show_all()
			box_label.show_all()
				
			scrolledwindow.show()

		except: pass

	def close_log_tab(self, btn, widget):
		""" close a log notebook tab button's event """
		current_tab = self.notebook.page_num(widget)
		self.notebook.remove_page(current_tab)

	def mouse_click(self, tv, event):
		# right click on a log
		
		try:
			if event.button == 3:

				try:
					self.rightclickmenu.destroy()
				except: pass

				# get selected port
				self.rightclickmenu = Gtk.Menu()

				logs_selected = []

				(model, pathlist) = self.log_tree.get_selection().get_selected_rows()
				for path in pathlist :

					tree_iter = model.get_iter(path)

					end_time = model.get_value(tree_iter,3) # selected port
					pid = model.get_value(tree_iter,4) # selected service
					log_id = model.get_value(tree_iter,0)

					logs_selected.append(log_id)

				if len(end_time) < 3:
					
					i1 = Gtk.MenuItem("kill")
					self.rightclickmenu.append(i1)
					i1.connect("activate", self.kill_task, pid)

				else:
					i1 = Gtk.MenuItem("export to file")
					self.rightclickmenu.append(i1)
					i1.connect("activate", self.export_log, log_id)

					i2 = Gtk.MenuItem("delete")
					self.rightclickmenu.append(i2)
					i2.connect("activate", self.delete_log, logs_selected)
			
				# show all
				self.rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
				self.rightclickmenu.show_all()

		except: pass


	def kill_task(self, widget, pid):
		# kill a task
		os.killpg(os.getpgid(pid), signal.SIGKILL)


	def export_log(self, widget, log_id):
		# export a log in a txt file
		log = self.database.get_logs(log_id)
		text = log.output

		dialog = Gtk.FileChooserDialog("Please choose a filename", None,
			Gtk.FileChooserAction.SAVE,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))


		dialog.set_filename("export output")
		file_filters.add_filter_txt(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()

			try:
				file = open(file_selected,"w") 
 
				for line in text:
					file.write(line)
				 
				file.close() 
			except: pass
			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()



class Serviceslist():
	def __init__(self, database):
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/hostlist.glade")

		self.database = database

		self.services_search = builder.get_object("hosts_search")
		self.services_list	 = builder.get_object("hostlist")
		self.services_box    = builder.get_object("host-box")

		self.services_search.connect("search-changed", self._search_service)

		self.services_liststore = Gtk.ListStore(str)

		#creating the treeview, making it use the filter as a model, and adding the columns
		self.servicestree = Gtk.TreeView(model=self.services_liststore) #.new_with_model(self.language_filter)
		for i, column_title in enumerate(["service"]):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			
		self.servicestree.append_column(column)


		self.services_list.add(self.servicestree)
		
		#self.servicestree.show()
		self.services_box.show()
		self.out_of_scope = True

		self.servicestree.props.activate_on_single_click = True

		self.refresh(self.database)


	def refresh(self, db):
		# refresh the log tree with the new database

		self.database = db
		ports = self.database.get_services_uniq(scope=self.out_of_scope)
		self.services_liststore.clear()

		for port in ports:
			self.services_liststore.append([port[0]])

		self.servicestree.show()

		return True

	def toggle_scope(self):
		# switch scope 
		self.out_of_scope = not self.out_of_scope
		self.refresh(self.database)


	def _search_service(self, widget):
		# search an host in hostlist and hint it

		# get the search value
		keyword = self.services_search.get_text()
		result  = ""

		row = 0
		for service in self.servicestree.get_model():
			if keyword in service[0]:
				break

			row += 1

		# hint the result row
		self.servicestree.row_activated(Gtk.TreePath.new_from_string(str(row)), Gtk.TreeViewColumn(None))
		self.servicestree.set_cursor(Gtk.TreePath.new_from_string(str(row)))



class Hostlist():
	def __init__(self, database):
		""" left-side Hostlist """
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/hostlist.glade")

		self.database = database

		self.host_search  = builder.get_object("hosts_search")
		self.hostlist	  = builder.get_object("hostlist")
		self.host_box     = builder.get_object("host-box")

		self.host_search.connect("search-changed", self._search_host)
		self.host_liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, str, str, int)

		#creating the treeview, making it use the filter as a model, and adding the columns
		self.hosttree = Gtk.TreeView(model=self.host_liststore) #.new_with_model(self.language_filter)
		

		for i, column_title in enumerate(["#", "address", "hostname", "status", "scope"]):
			if i == 0:

				renderer = Gtk.CellRendererPixbuf()
				column = Gtk.TreeViewColumn(column_title, renderer, pixbuf=0)
			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			
			self.hosttree.append_column(column)

		#self.hosttree.connect("button_press_event", self.mouse_click)
		self.hostlist.add(self.hosttree)

		# multi selection
		selection = self.hosttree.get_selection()
		selection.set_mode(Gtk.SelectionMode.MULTIPLE)

		self.hosttree.show()
		self.host_box.show()

		self.hosttree.props.activate_on_single_click = True

		self.out_of_scope = True

		self.refresh(self.database)

	def refresh(self, db):
		# refresh the log tree with the new database

		self.database = db
		hosts = self.database.get_hosts()

		self.host_liststore.clear()

		for host in hosts:
			#if not host in self.old_hosts:

			status = host.status

			try: # add icon fot the os found
				icon = iconslib.get_icon(host.os_match)
			except:
				icon = iconslib.icon("unknown")

			if not self.out_of_scope:
				if host.scope:
					try:
						self.host_liststore.append([icon, host.address, host.hostname.split(" ")[0], status, str(host.scope),  host.id])
					except:
						self.host_liststore.append([icon, host.address, "", status, str(host.scope), host.id])

			else:
				try:
					self.host_liststore.append([icon, host.address, host.hostname.split(" ")[0], status, str(host.scope),  host.id])
				except:
					self.host_liststore.append([icon, host.address, "", status, str(host.scope), host.id])


		self.hosttree.show()

		return True

	def toggle_scope(self):
		# switch scope 
		self.out_of_scope = not self.out_of_scope
		self.refresh(self.database)

	def _search_host(self, widget):
		# search an host in hostlist and hint it

		# get the search value
		keyword = self.host_search.get_text()
		result  = ""

		row = 0
		for host in self.hosttree.get_model():
			if keyword in host[1]:
				break

			row += 1

		# hint the result row
		self.hosttree.row_activated(Gtk.TreePath.new_from_string(str(row)), Gtk.TreeViewColumn(None))
		self.hosttree.set_cursor(Gtk.TreePath.new_from_string(str(row)))



class Serviceview():
	def __init__(self, service, database, view_out_scope=True):
		""" servicesview workspace tab """
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/servicesview.glade")	

		self.database = database
		self.service  = service

		self.notebook = builder.get_object("notebook1")
		self.portlistframe = builder.get_object("portlistframe")

		# creating the treeview, making it use the filter as a model, and adding the columns
		self.treeview = ServicesTree(self.database, self.service)

		scrolled = Gtk.ScrolledWindow()
		viewport = Gtk.Viewport()

		scrolled.add(viewport)
		viewport.add(self.treeview)
		scrolled.show_all()

		self.portlistframe.add(scrolled)

		self.refresh(self.database, view_out_scope=view_out_scope)


	def refresh(self, db, view_out_scope = True):

		self.database = db
		self.treeview.refresh( self.database, self.service, scope=view_out_scope )


class Hostview():
	def __init__(self, host, database):
		""" hostview workspace tab """
		# initialization
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/hostview.glade")

		self.database = database
		self.host = host

		self.notebook = builder.get_object("notebook1")
		self.portlistframe = builder.get_object("portlistframe")

		# tab title
		self.dash_title = builder.get_object("dash-title")
		self.dash_title.set_text("Target: %s" % self.host.address)

		# responsive widgets rows
		self.w_row_1 = builder.get_object("row1")
		self.w_row_2 = builder.get_object("row2")
		self.w_row_3 = builder.get_object("row3")

		# info-tab
		self.info_loc = builder.get_object("tab-info-location")
		self.info_tab = host_informations(self.database, self.host)

		self.info_loc.add(self.info_tab)

		# notes
		self.notes_place = builder.get_object("notes-place")
		self.notes_view = Notesview(database, host)
		self.notes_place.add(self.notes_view)

		# history tab
		self.history_box = builder.get_object("history-box")

		self.history_view = Historyview(self.database, self.host)

		scrolled_history = Gtk.ScrolledWindow()
		viewport = Gtk.Viewport()

		scrolled_history.add(viewport)
		scrolled_history.set_property("height-request", 400)
		viewport.add(self.history_view)

		self.history_box.add(scrolled_history)
		self.history_box.show_all()

		# Geolocation tab
		self.geoloc_box = builder.get_object("geoloc-box")
		self.geolocation_map = OSM(self.database, self.host)
		self.geoloc_box.add(self.geolocation_map)

		# title
		self.info_target    = builder.get_object("target-label")
		self.info_os_short  = builder.get_object("info-os-short")
		self.info_image     = builder.get_object("target-image")

		self.info_target.set_text(self.host.address)

		# services
		self.treeview = PortsTree(self.database, self.host) #Gtk.TreeView(model=self.port_liststore)

		scrolled = Gtk.ScrolledWindow()
		viewport = Gtk.Viewport()

		scrolled.add(viewport)
		scrolled.set_property("height-request", 400)
		viewport.add(self.treeview)
		scrolled.show_all()

		self.portlistframe.add(scrolled)

		# expand buttons
		tab_info_button          = builder.get_object("tab-info-button")
		image2                   = builder.get_object("image2")
		tab_services_button      = builder.get_object("tab-services-button")
		image6                   = builder.get_object("image6")
		tab_geoloc_button        = builder.get_object("tab-geoloc-button")
		image3                   = builder.get_object("image3")
		tab_notes_button         = builder.get_object("tab-notes-button")
		image7                   = builder.get_object("image7")
		tab_history_button       = builder.get_object("tab-history-button")
		image5                   = builder.get_object("image5")

		tab_services_button.connect("clicked", self.tab_clicked_max, "Services", scrolled, self.portlistframe, image6)
		tab_geoloc_button.connect("clicked", self.tab_clicked_max, "Geolocation", self.geolocation_map, self.geoloc_box, image3)
		tab_info_button.connect("clicked", self.tab_clicked_max, "Informations", self.info_tab, self.info_loc, image2)
		tab_notes_button.connect("clicked", self.tab_clicked_max, "Notes", self.notes_view, self.notes_place,image7)
		tab_history_button.connect("clicked", self.tab_clicked_max, "Task's history", scrolled_history, self.history_box, image5)

		self.fullscreen = []
		
		try:
			self.info_os_short.set_text(str(self.host.os_match).split("\n")[0])
			self.info_image.set_from_pixbuf(iconslib.get_icon(self.host.os_match,lg=True))
		except: pass

		# responsive stuff

		self.w_row_1.connect('size-allocate', self._size_changed)
		self.w_row_2.connect('size-allocate', self._size_changed)
		self.w_row_3.connect('size-allocate', self._size_changed)

	def _size_changed(self, widget, rectangle):
		""" host view scrolled size changed, 
		this make the widget's "grid" responsive """

		orient = widget.get_orientation()
		
		if rectangle.width < 680:
			if orient == Gtk.Orientation.HORIZONTAL:
				# convert hbox to vbox
				widget.set_orientation(Gtk.Orientation.VERTICAL)
		else:
			if orient == Gtk.Orientation.VERTICAL:
				# convert vbox to hbox
				widget.set_orientation(Gtk.Orientation.HORIZONTAL)


	def refresh(self, db, history = False):

		# refresh history
		self.database = db

		if history:
			# refresh ONLY history
			self.history_view.refresh(self.database,self.host)

			return True

		self.history_view.refresh(self.database, self.host)
		self.treeview.refresh(self.database, self.host)
		self.geolocation_map.refresh(self.database, self.host)
		self.info_tab.refresh(self.database, self.host)

		try:
			self.info_os_short.set_text(str(self.host.os_match).split("\n")[0])
			self.info_image.set_from_pixbuf(iconslib.get_icon(self.host.os_match,lg=True))
		except: pass

		# responsive stuff
		if self.w_row_1.get_allocation().width < 680:
			self.w_row_1.set_orientation(Gtk.Orientation.VERTICAL)
			self.w_row_2.set_orientation(Gtk.Orientation.VERTICAL)
			self.w_row_3.set_orientation(Gtk.Orientation.VERTICAL)
		else: 
			self.w_row_1.set_orientation(Gtk.Orientation.HORIZONTAL)
			self.w_row_2.set_orientation(Gtk.Orientation.HORIZONTAL)
			self.w_row_3.set_orientation(Gtk.Orientation.HORIZONTAL)			

	def tab_clicked_max(self, button, name, oldobj, oldparent, image):
		""" Fullscreen option """
		if not oldobj in self.fullscreen:
			oldparent.remove(oldobj)
			self.notebook.append_page(oldobj,Gtk.Label(name))

			self.notebook.set_current_page(-1)
			self.fullscreen.append(oldobj)

			image =iconslib.gtk_exit_fullscreen(image)
		else:
			page_id = self.notebook.page_num(oldobj)
			self.notebook.remove_page(page_id)
			image =iconslib.gtk_fullscreen(image)

			self.fullscreen.remove(oldobj)
			oldparent.add(oldobj)


class Main():
	def __init__(self):
		""" main windows """

		# initialization
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/main.glade")

		# window
		self.headerbar = builder.get_object("headerbar")
		self.window = builder.get_object("window")
		self.window.set_title("BadKarma")
		self.window.set_titlebar(self.headerbar)

		self.main_paned    = builder.get_object("main-paned")
		self.main_notebook = builder.get_object("main-notebook")

		# main menu
		self.preferences_popover = builder.get_object("preferences-popover")
		self.file_addtarget      = builder.get_object("file_addtarget")
		self.file_quit	         = builder.get_object("file_quit")
		self.file_import         = builder.get_object("file_import")
		self.file_open           = builder.get_object("file_open")
		self.file_save_as        = builder.get_object("file_save_as")
		self.file_about          = builder.get_object("file_about")
		
		self.portlist_empty = True

		# preferences 
		self.popovermenu2    = builder.get_object("popovermenu2")
		self.auto_exec       = builder.get_object("auto-execute-ext")
		self.use_proxychains = builder.get_object("use-proxychains")
		self.view_logs       = builder.get_object("view-logs")
		self.out_of_scope    = builder.get_object("view-out-of-scope")

		# about window
		self.about_window    = builder.get_object("about-window")
		self.donate_button   = builder.get_object("donate-button")

		# workspace & hostlist
		self.controller_notebook = builder.get_object("controller-notebook")
		self.hostlist_box        = builder.get_object("host-box")
		self.services_box        = builder.get_object("services-box")
		self.workspace           = builder.get_object("workspace-work")

		self.welcome_note        = builder.get_object("welcome-note")

		# connect donate button
		self.donate_button.connect('clicked', self._donate_url)

		# connect preferences menu for quit
		self.use_proxychains.connect('toggled', self._quit_menu)
		self.auto_exec.connect('toggled', self._quit_menu)
		self.view_logs.connect('toggled', self._quit_menu)
		self.out_of_scope.connect('toggled', self._quit_menu)

		# connect main menu for quit
		self.file_addtarget.connect('clicked', self._quit_menu)
		self.file_quit.connect('clicked', self._quit_menu)
		self.file_open.connect('clicked', self._quit_menu)
		self.file_import.connect('clicked', self._quit_menu)
		self.file_save_as.connect('clicked', self._quit_menu)
		self.file_about.connect('clicked', self._quit_menu)

		# show about window
		self.file_about.connect('clicked', self.show_about)
		self.about_window.connect('response', self.close_about)


	def _donate_url(self,widget):
		url = "\"https://www.paypal.com/donate/?token=OblZPt9m--dJC0S-6QISb8J5ae_24cklvOOu5crnd1CFRyhQTADa_ZRFKbbUh93U56qeAW&country.x=US&locale.x=en_XC\""
		os.system('xdg-open %s' % url)

	def _quit_menu(self,widget):

		self.preferences_popover.hide()
		self.popovermenu2.hide()

	def close_about(self,widget,event):

		self.window.set_sensitive(True)
		self.about_window.hide()

	def show_about(self,widget):

		self.window.set_sensitive(False)
		self.about_window.show()
