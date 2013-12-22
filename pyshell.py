#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, vte, pango, os
import xml.etree.ElementTree as ET

class PyShell:

    def delete_event(self, widget, data):
        print "Exiting..."
        gtk.main_quit()
        return False

    def get_file(obj, widget):
        list_file = obj.server_list_file.get_filename()
        obj.server_list_file.destroy()
        return list_file
        
    def open_file(self, widget, data):
        self.server_list_file = gtk.FileSelection("Choose a server list file")
        self.server_list_file.ok_button.connect("clicked", self.get_file)
        self.server_list_file.cancel_button.connect("clicked", lambda w: self.server_list_file.destroy())

        self.server_list_file.show()

    def print_hello(self, w, data):
        print "Hello, World!"

    def main_menu(self, window):
        accel_group = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)
        item_factory.create_items(self.menu_items)
        self.window.add_accel_group(accel_group)

        self.item_factory = item_factory
        return item_factory.get_widget("<main>")

    def __init__(self):

        self.menu_items = (
                  ( "/_File",         None,         None, 0, "<Branch>" ),
                  ( "/File/_New",     "<control>N", self.print_hello, 0, None ),
                  ( "/File/_Open",    "<control>O", self.open_file, 0, None ),
                  ( "/File/_Save",    "<control>S", self.print_hello, 0, None ),
                  ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, None ),
                  )

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("PyShell")
        self.window.set_border_width(2)
        self.window.set_resizable(True)
        self.window.set_default_size(1280, 1024)

        self.window.connect("delete_event", self.delete_event)

        self.vbox = gtk.VBox(False, False)
        self.window.add(self.vbox)
        self.vbox.show()
        
        self.menubar = self.main_menu(self.window)
        self.vbox.pack_start(self.menubar, False, False)
        self.menubar.show()

        self.hpaned = gtk.HPaned()
        self.hpaned.set_position(1024)
        self.vbox.pack_start(self.hpaned)
        self.hpaned.show()

        self.scroller = gtk.ScrolledWindow()
        self.hpaned.add1(self.scroller)

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

        self.scroller.add(self.term)
        self.term.show()
        self.scroller.show()
        
        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)
        
        
        tree = ET.parse("serverlist.xml")
        root = tree.getroot()

        for i in root:
            self.mydir = i.attrib['name']
            piter = self.treestore.append(None, [self.mydir])
            for j in i:
                self.myserver = j.attrib['name']
                self.treestore.append(piter, [self.myserver])
        
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Server List')

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()

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

        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    pyshell = PyShell()
    pyshell.main()

