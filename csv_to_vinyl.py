#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from collections import namedtuple
from subprocess import check_output
import csv
import os.path
import argparse
import re

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS
import simplestyle

Name = namedtuple('Name', ['name','size'])

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
        self.separate_sizes = self.options.separate_sizes
        self.size_field_num = self.options.size_field_num

        self.names = self.load_csv_file(self.csv_file, self.csv_field_num, self.size_field_num)

        if len(self.selected) == 1:
            # extract style and attributes from selection
            selected = self.selected.popitem()[1]
            self.text_style = selected.attrib["style"]
            self.text_transform = selected.get('transform','')
            self.line_spacing, self.delta_y = self.get_linespacing(selected)

            assert self.text_style != None

            for name in self.names:
                self.__add_name(name.name, name.size)

    def __add_name(self, name, layer):
        if self.separate_sizes:
            parent = self.__get_layer(layer)
        else:
            parent = self.current_layer

        text_attribs = {
            'style' : self.text_style,
            'transform' : self.text_transform,
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

        # skip empty strings
        if len(lines) > 0:
            # add nodes to doucument tree
            text = etree.SubElement(parent, addNS('text','svg'), attrib=text_attribs)
            for line in lines:
                text_line = etree.SubElement(text, addNS('tspan','svg'), attrib=line_attribs)
                text_line.text = line

                # set coordinates for next line
                y = float(line_attribs['y'])
                line_attribs['y'] = str(y + self.delta_y)

            if self.separate_sizes:
                self.__sort_layers()

    def __get_layer(self, label):
        root = self.document.getroot()
        # tidy up the label
        label = label.strip().upper()
        label = re.sub(' +', ' ', label)

        # return layer if already exists
        for layer in root:
            if layer.get(addNS('label','inkscape'), default=None) == str(label):
                return layer
        # otherwise create new one
        layer_attrib = {
                addNS('groupmode','inkscape') : 'layer',
                addNS('label','inkscape') : str(label),
        }

        layer = etree.SubElement(root, addNS('g','svg'), attrib=layer_attrib)
        return layer

    def __sort_layers(self):
        root = self.document.getroot()
        layers = {}
        for node in root:
            if node.tag == addNS('g','svg'):
                label = node.get(addNS('label','inkscape'), default='')
                layers[label] = node

        for key in sorted(layers.keys(), reverse=True):
            layer = layers[key]
            root.append(layer)

    def load_csv_file(self, filename, field_num=1, size_field_num=None):
        """
        Load CSV file and return field with index 'field_num' of each row as a list.
        Fields are indexed from 1.
        """
        field_num -= 1
        if size_field_num:
            size_field_num -= 1

        with open(filename, 'r') as csv_file:
            lines = []

            csvreader = csv.reader(csv_file)
            for row in csvreader:
                if self.separate_sizes:
                    name = Name(name=row[field_num],size=row[size_field_num])
                else:
                    name = Name(name=row[field_num],size='')
                lines.append(name)

            return lines

    def get_linespacing(self, text):
        """
        Examines two line 'text' and returns a tuple of the sodipodi linespacing and
        delta of their y coordinates, ie. delta_y = y2 - y1.
        Returns (linespacing, delta_y)
        """
        if len(text) > 1:
            y1 = float(text[0].attrib["y"])
            y2 = float(text[1].attrib["y"])

            delta_y = y2 - y1
        else:
            delta_y = self.unittouu("10mm")

        line_spacing = text.attrib[addNS('linespacing','sodipodi')]

        return line_spacing, delta_y

effect = CsvToVinyl()
effect.affect()
