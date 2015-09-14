#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from subprocess import check_output
import csv

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS
import simplestyle

class CsvToVinyl(InkscapeEffect):
    def __init__(self, names):
        InkscapeEffect.__init__(self)
        self.OptionParser.add_option('-f', '--csv_file', action = 'store',
            type=str, dest = 'csv_file', default = '/home',
            help = 'CSV file to read names from')
        self.names = names
        self.filename = sys.argv[-1]

    def effect(self):
        self.root = self.document.getroot()
        self.csv_file = self.options.csv_file

        if len(self.selected) == 1:
            # extract style from selection
            self.text_style = self.selected.popitem()[1].attrib["style"]
            assert self.text_style != None
            for name in self.names:
                self.add_name(name)

    def add_name(self, name):
        parent = self.current_layer

        text_attribs = {
            'style' : self.text_style,
            'x' : str(0),
            'y' : str(0),
            addNS('linespacing','sodipodi') : '100%',
        }

        line_attribs = {
            'x' : str(0),
            'y' : str(0),
            addNS('role','sodipodi') : 'line',
        }

        # make all-caps and turn whitespace into linebreak
        name = name.upper()
        firstname = name.split()[0]
        lastname = name.split()[1]
        
        # add nodes to doucument tree
        text = etree.SubElement(parent, addNS('text','svg'), attrib=text_attribs)
        first_line = etree.SubElement(text, addNS('tspan','svg'), line_attribs)
        first_line.text = firstname
        second_line = etree.SubElement(text, addNS('tspan','svg'), line_attribs)
        second_line.text = lastname

    def resize_page(self):
        csv = check_output(["inkscape", "--without-gui", "--query-all", self.filename])
        print(csv)
        svg = self.document.getroot()
        width = self.unittouu(svg.get("width"))
        height = self.unittouu(svg.get("height"))
        print(width)
        print(svg.get("width"))
        print(height)
        print(svg.get("height"))
        #print("Height " + svg.get("height"))
        #print(self.filename)

names = [
    'John Does',
    'Albus Dumbledore',
    'GI Joe',
    'Jet Jaguar',
    'John McClaine',
    'Robert Maguire',
    'Magnus Mangusson',
    'Lucy Jones',
    'Jan Kowalski',
    'Frodo Baggins',
    'Phileas Fogg',
    'Katherine Romanoff',
    'Kim Jong-Illest',
]

effect = CsvToVinyl(names)
effect.affect()
