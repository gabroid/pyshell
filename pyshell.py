#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk, vte
from xml.dom import minidom

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
        self.window.set_default_size(800, -1)

        self.window.connect("delete_event", self.delete_event)

        #self.boxContainer = gtk.HBox(False, 15)
        #self.window.add(self.boxContainer)
        #self.boxContainer.show()
        
        self.hpaned = gtk.HPaned()
        self.window.add(self.hpaned)
        self.hpaned.show()

        self.term = vte.Terminal()
        self.pid = self.term.fork_command('bash')
        self.term.set_emulation('xterm')
        self.hpaned.add1(self.term)
        self.term.show()
        
        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)
        
        
        xmldoc = minidom.parse('serverlist.xml')
        
        self.dirlist =  xmldoc.getElementsByTagName('dir') 
        
        for i in self.dirlist:
            self.serverlist = xmldoc.getElementsByTagName('item')
            self.mydir = i.attributes['name'].value
            piter = self.treestore.append(None, ['%s' % self.mydir])
            for j in self.serverlist:
                self.server = j.attributes['name'].value
                self.treestore.append(piter, ['%s' % self.server])
    
        # we'll add some data now - 4 rows with 3 child rows each
        #for parent in range(4):
        #    piter = self.treestore.append(None, ['parent %i' % parent])
        #    for child in range(3):
        #        self.treestore.append(piter, ['child %i of parent %i' %
        #                (child, parent)])

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

