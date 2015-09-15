#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS

from simpletransform import computeBBox
from simplestyle import formatStyle

class Roland(InkscapeEffect):
    def __init__(self):
        InkscapeEffect.__init__(self)
        self.filename = sys.argv[-1]

    def effect(self):
        if len(self.selected) > 0:
            svg = self.document.getroot()
            bboxes = self.calculate_bboxes(self.selected)
            #for id, node, bbox in bboxes:
            #    self.draw_bbox(bbox)
            self.place(bboxes)

    @staticmethod
    def calculate_bboxes(nodes):
        bboxes = [(id, node, computeBBox([node]))
                for id, node in nodes.items()]
        return bboxes
    
    def draw_bbox(self, bbox):
        (x1, x2, y1, y2) = bbox
        width = x2 - x1
        height = y2 - y1
        self.draw_rect(x1, y1, width, height)

    #SVG element generation routine
    def draw_rect(self, x, y, width, height):
        layer = self.current_layer

        style = {   'stroke'        : '#ff0000',
                    'stroke-width'  : '1',
                    'fill'          : 'none',
        }
                    
        attribs = {
            'style'     : formatStyle(style),
            'x'         : str(x),
            'y'         : str(y),
            'width'     : str(width),
            'height'    : str(height),
        }

        rect = etree.SubElement(layer, addNS('rect','svg'), attribs )

    def place(self, nodes):
        max_line_width = self.unittouu('450mm')

        x_gap = y_gap = self.unittouu('10mm')
        x_start = self.unittouu('0mm')
        y_start = self.unittouu('1600mm')

        total_width = 0
        total_height = 0

        for id, node, bbox in nodes:
            node_width = x_gap + self.width(bbox)
            if total_width + node_width < max_line_width:
                node.attrib['x'] = str(x_start + x_gap + total_width)
                node.attrib['y'] = str(y_start - (y_gap + total_height + self.height(bbox)))
                total_width += node_width

    def width(self,bbox):
        (x1, x2, y1, y2) = bbox
        width = x2 - x1

        return width

    def height(self,bbox):
        (x1, x2, y1, y2) = bbox
        height = y2 - y1

        return height


effect = Roland()
effect.affect()
