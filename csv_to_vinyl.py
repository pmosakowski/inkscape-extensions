#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from subprocess import check_output
import csv
import os.path
import argparse

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS
import simplestyle

def str_to_bool(v):
      return v.lower() in ("yes", "true", "t", "1")

class CsvToVinyl(InkscapeEffect):
    def __init__(self):
        InkscapeEffect.__init__(self)
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("--id", action='append', type=str, dest='ids', default=[],
            help='id attribute of object to manipulate')
        self.parser.add_argument('filename',
            help='temporary file on which extension will operate')
        self.parser.add_argument('-f', '--csv_file', type=str, default = '/home',
            help = 'CSV file to read names from')
        self.parser.add_argument('-n', '--csv_field_num', type=int, default = 1,
            help = 'Number of the field number that contains strings we want to vectorize, starts at 1')
        self.parser.add_argument('-l', '--separate_sizes', type=str_to_bool, default = False,
            help = 'Separate names for different sized graments onto different layers')
        self.parser.add_argument('-s', '--size_field_num', type=int, default = 1,
            help = 'Field number containing size for a given name')
        self.filename = sys.argv[-1]

    def getoptions(self,args=sys.argv[1:]):
        self.options = self.parser.parse_args()

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
                self.__add_name(name)

    def __add_name(self, name):
        parent = self.current_layer

        text_attribs = {
            'style' : self.text_style,
            'x' : str(0),
            'y' : str(0),
            addNS('linespacing','sodipodi') : str(self.line_spacing),
        }

        line_attribs = {
            'x' : str(0),
            'y' : str(0),
            addNS('role','sodipodi') : 'line',
        }

        # make all-caps and turn whitespace into linebreak
        lines = name.upper().split()

        # add nodes to doucument tree
        text = etree.SubElement(parent, addNS('text','svg'), attrib=text_attribs)
        for line in lines:
            text_line = etree.SubElement(text, addNS('tspan','svg'), attrib=line_attribs)
            text_line.text = line

            # set coordinates for next line
            y = float(line_attribs['y'])
            line_attribs['y'] = str(y + self.delta_y)

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

effect = CsvToVinyl()
effect.affect()
