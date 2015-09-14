#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from subprocess import check_output
import csv
import os.path

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS
import simplestyle

class CsvToVinyl(InkscapeEffect):
    def __init__(self, names):
        InkscapeEffect.__init__(self)
        self.OptionParser.add_option('-f', '--csv_file', action = 'store',
            type=str, dest = 'csv_file', default = '/home',
            help = 'CSV file to read names from')
        self.OptionParser.add_option('-n', '--csv_field_num', action = 'store',
            type=int, dest = 'csv_field_num', default = 0,
            help = 'Number of the field number that contains strings we want to vectorize, starts at 0')
        self.names = names
        self.filename = sys.argv[-1]

    def effect(self):
        self.root = self.document.getroot()
        self.csv_file = self.options.csv_file
        self.csv_field_num = self.options.csv_field_num

        self.names = self.load_csv_file(self.csv_file, self.csv_field_num)

        if len(self.selected) == 1:
            # extract style and attributes from selection
            selected = self.selected.popitem()[1]
            self.text_style = selected.attrib["style"]
            self.line_spacing, self.delta_y = self.get_linespacing(selected)

            assert self.text_style != None

            for name in self.names:
                self.add_name(name)

    def add_name(self, name):
        parent = self.current_layer

        text_attribs = {
            'style' : self.text_style,
            'x' : str(0),
            'y' : str(0),
            addNS('linespacing','sodipodi') : str(self.line_spacing),
        }

        line1_attribs = {
            'x' : str(0),
            'y' : str(0),
            addNS('role','sodipodi') : 'line',
        }

        line2_attribs = dict(line1_attribs)
        line2_attribs['y'] = str(self.delta_y)

        # make all-caps and turn whitespace into linebreak
        name = name.upper()
        firstname = name.split()[0]
        lastname = name.split()[1]
        
        # add nodes to doucument tree
        text = etree.SubElement(parent, addNS('text','svg'), attrib=text_attribs)
        first_line = etree.SubElement(text, addNS('tspan','svg'), attrib=line1_attribs)
        first_line.text = firstname
        second_line = etree.SubElement(text, addNS('tspan','svg'), attrib=line2_attribs)
        second_line.text = lastname

    @staticmethod
    def load_csv_file(filename, field_num=0):
        """
        Load CSV file and return field with index 'field_num' of each row as a list.
        Fields are indexed from 0.
        """

        with open(filename, 'r') as csv_file:
            lines = []

            csvreader = csv.reader(csv_file)
            for row in csvreader:
                lines.append(row[field_num])

            return lines

    @staticmethod
    def get_linespacing(text):
        """
        Examines two line 'text' and returns a tuple of the sodipodi linespacing and
        delta of their y coordinates, ie. delta_y = y2 - y1.
        Returns (linespacing, delta_y)
        """

        y1 = float(text[0].attrib["y"])
        y2 = float(text[1].attrib["y"])

        delta_y = y2 - y1
        line_spacing = text.attrib[addNS('linespacing','sodipodi')]

        return line_spacing, delta_y

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
