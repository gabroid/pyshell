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

    def __init__(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("PyShell")
        self.window.set_border_width(5)
        self.window.set_resizable(True)
        self.window.set_default_size(1280, 1024)

        self.window.connect("delete_event", self.delete_event)
        
        self.hpaned = gtk.HPaned()
        self.hpaned.set_position(1024)
        self.window.add(self.hpaned)
        self.hpaned.show()

        self.term = vte.Terminal()
        self.term.connect("child-exited", lambda w: gtk.main_quit())
        self.pid = self.term.fork_command('/bin/bash')
        self.term.set_emulation('xterm')
        #self.term.feed_child("cd $HOME\n")
        
        font = pango.FontDescription()
        font.set_size(11 * pango.SCALE)
        font.set_weight(pango.WEIGHT_NORMAL)
        font.set_stretch(pango.STRETCH_NORMAL)
        self.term.set_font_full(font, True)

        self.hpaned.add1(self.term)
        self.term.show()
        
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

