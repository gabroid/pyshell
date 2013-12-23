#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, vte, pango, os, getpass, pynotify, gobject
import xml.etree.ElementTree as ET

pynotify.init('pyConnection Manager!')

class PyShell:

    def delete_event(self, widget, data):
        """Simple function to quit program"""
        print "Exiting..."
        gtk.main_quit()
        return False

    def load_file(self, window):
        """Retrive and load server list file"""
        self.list_file = self.server_list_file.get_filename()
        self.server_list_file.destroy()

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)

        try:
            self.tree = ET.parse(self.list_file)
        except:
            print "ERROR"
            return False

        self.root = self.tree.getroot()

        for i in self.root:
            self.mydir = i.attrib['name']
            self.piter = self.treestore.append(None, [self.mydir])
            for j in i:
                self.myserver = j.attrib['name']
                self.treestore.append(self.piter, [self.myserver])
        
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Server List')

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        #self.cell.set_property('editable', True)
        
        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        self.hpaned.add2(self.treeview)
        self.treeview.show()

        # Signal for tree view goes here
        self.treeview.connect("row-activated", self.dynamic_connection)
        
    def open_file(self, widget, data):
        """Open server list file"""
        self.server_list_file = gtk.FileSelection("Choose a server list file")
        self.server_list_file.ok_button.connect("clicked", self.load_file)
        self.server_list_file.cancel_button.connect("clicked", lambda w: self.server_list_file.destroy())
        self.server_list_file.show()

    def open_preferences(self, widget, data):
        """Open preferences"""
        self.window_preferences = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window_preferences.set_title("PyCM - Preferences")
        self.window_preferences.set_border_width(5)
        self.window_preferences.set_resizable(True)
        self.window_preferences.set_default_size(640, 480)

        self.window_preferences.show()

    def remove_tab(self, current_tab):
        """Remove vte tab when user enter exit in shell"""
        self.current_tab = self.notebook.get_current_page()
        self.notebook.remove_page(self.current_tab)
    
    def create_vte(self, user=None, host=None):
        """Function to create vte.Terminal"""
        if user is None or user == "Username":
            self.command = "ssh %s\n" % host
        else:
            self.command = "ssh %s@%s\n" % (user, host)

        self.new_term = vte.Terminal()
        self.new_term.connect("child-exited", self.remove_tab)
        self.pid = self.new_term.fork_command()
        self.new_term.set_emulation('xterm')
        
        self.font = pango.FontDescription()
        self.font.set_size(11 * pango.SCALE)
        self.font.set_weight(pango.WEIGHT_NORMAL)
        self.font.set_stretch(pango.STRETCH_NORMAL)
        self.new_term.set_font_full(self.font, True)

        self.label = gtk.Label(user + "@" + host)
        self.notebook.append_page(self.new_term, self.label)
        self.new_term.feed_child(self.command)
        self.new_term.show()
        self.notebook.next_page()
        self.new_term.grab_focus()

    def new_local_tab(self, widget):
        """Open a new vte tab on localhost"""
        self.new_term = vte.Terminal()
        self.pid = self.new_term.fork_command()
        self.new_term.set_emulation('xterm')
        
        self.hostname = os.uname()[1]
        self.username = getpass.getuser()
        self.label = gtk.Label(self.username + "@" + self.hostname)

        self.notebook.append_page(self.new_term, self.label)
        
        self.new_term.connect("child-exited", self.remove_tab)

        self.font = pango.FontDescription()
        self.font.set_size(11 * pango.SCALE)
        self.font.set_weight(pango.WEIGHT_NORMAL)
        self.font.set_stretch(pango.STRETCH_NORMAL)
        self.new_term.set_font_full(self.font, True)

        self.new_term.show()
        self.notebook.next_page()
        self.new_term.grab_focus()

    def static_connection(self, widget):
        """Function to create new remote vte tab"""
        self.host = self.entry_host.get_text()
        self.user = self.entry_user.get_text()
        self.label = gtk.Label(self.user + "@" + self.host)

        self.create_vte(self.user, self.host)

    def dynamic_connection(self, window, item, obj):
        self.treeselection = self.treeview.get_selection()
        (self.model, self.pathlist) = self.treeselection.get_selected_rows()
        for path in self.pathlist :
            self.tree_iter = self.model.get_iter(path)
            self.host = self.model.get_value(self.tree_iter,0)
            
        self.create_vte("maurelio", self.host)

        

    def main_menu(self, window):
        """Menu toolbar"""
        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        self.window.add_accel_group(accel_group)

        self.item_factory = item_factory
        return item_factory.get_widget("<main>")

    def __init__(self):

        self.menu_items = (
                  ( "/_File",         None,         None, 0, "<Branch>" ),
                  ( "/File/_New",     "<control>N", self.open_file, 0, None ),
                  ( "/File/_Open",    "<control>O", self.open_file, 0, None ),
                  ( "/File/_Save",    "<control>S", self.open_file, 0, None ),
                  ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, None ),
                  ( "/_Edit",         None,         None, 0,  "<Branch>"),
                  ( "/Edit/_Prefernces","<control>P", self.open_preferences, 0, None)
                  )

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("PyConnection Manager")
        self.window.set_border_width(5)
        self.window.set_resizable(True)
        self.window.set_default_size(1280, 1024)

        self.window.connect("delete_event", self.delete_event)

        self.vbox = gtk.VBox(False, False)
        self.window.add(self.vbox)
        self.vbox.show()
        
        self.menubar = self.main_menu(self.window)
        self.vbox.pack_start(self.menubar, False, False)
        self.menubar.show()

        self.table = gtk.Table(1, 5, True)
        self.vbox.pack_start(self.table, False, False)
        self.table.show()

        self.entry_host = gtk.Entry()
        self.entry_host.set_text("Hostname")
        self.table.attach(self.entry_host, 0, 1, 0, 1)
        self.entry_host.show()

        self.entry_user = gtk.Entry()
        self.entry_user.set_text("Username")
        self.table.attach(self.entry_user, 1, 2, 0, 1)
        self.entry_user.show()

        self.entry_pwd = gtk.Entry()
        self.entry_pwd.set_text("Password")
        self.entry_pwd.set_visibility(False)
        self.table.attach(self.entry_pwd, 2, 3, 0, 1)
        self.entry_pwd.show()

        self.connect_button = gtk.Button("Connect")
        self.table.attach(self.connect_button, 3, 4, 0, 1)
        self.connect_button.show()

        self.new_tab_button = gtk.Button("New tab")
        self.table.attach(self.new_tab_button, 4, 5, 0, 1)
        self.new_tab_button.show()

        self.hpaned = gtk.HPaned()
        self.hpaned.set_position(1024)
        self.vbox.pack_start(self.hpaned)
        self.hpaned.show()

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.hpaned.add1(self.notebook)

        self.term = vte.Terminal()
        self.term.connect("child-exited", lambda w: gtk.main_quit())
        self.pid = self.term.fork_command()
        self.term.set_emulation('xterm')
        #self.term.feed_child("cd $HOME\n")
        
        font = pango.FontDescription()
        font.set_size(11 * pango.SCALE)
        font.set_weight(pango.WEIGHT_NORMAL)
        font.set_stretch(pango.STRETCH_NORMAL)
        self.term.set_font_full(font, True)

        self.hostname = os.uname()[1]
        self.username = getpass.getuser()

        self.label = gtk.Label(self.username + "@" + self.hostname)
        self.notebook.append_page(self.term, self.label)
        self.term.show()
        self.notebook.show()
        self.term.grab_focus()
        


        self.window.show()


        # Here i will define all handlers and connect for obj in __init__
        self.connect_button.connect("clicked", self.static_connection)
        self.new_tab_button.connect("clicked", self.new_local_tab)


    def main(self):
        gtk.main()

if __name__ == "__main__":
    pyshell = PyShell()
    pyshell.main()

