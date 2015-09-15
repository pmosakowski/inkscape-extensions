#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS

from simpletransform import computeBBox, applyTransformToNode
from simplestyle import formatStyle
from simplepath import parsePath, translatePath, formatPath

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
            x, _, y, _ = bbox

            x_dest = x_start + x_gap + total_width
            y_dest = y_start - (y_gap + total_height + self.height(bbox))

            node_width = x_gap + self.width(bbox)
            if total_width + node_width < max_line_width:
                if node.tag == addNS('path','svg'):
                    x_delta = x_dest - x
                    y_delta = y_dest - y

                    path = parsePath(node.attrib['d'])
                    translatePath(path, x_delta, y_delta)
                    node.attrib['d'] = formatPath(path)
                elif node.tag == addNS('g','svg'):
                    x_delta = x_dest - x
                    y_delta = y_dest - y

                    translation_matrix = [[1.0, 0.0, x_delta], [0.0, 1.0, y_delta]]
                    applyTransformToNode(translation_matrix, node)

                else:
                    node.attrib['x'] = str(x_dest)
                    node.attrib['y'] = str(y_dest)

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
