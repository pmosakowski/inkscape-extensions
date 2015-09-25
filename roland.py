#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from collections import defaultdict

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS

from simpletransform import computeBBox as _computeBBox
from simpletransform import applyTransformToNode
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

    def calculate_bboxes(self, nodes):
        bboxes = [(id, node, self.computeBBox(node))
                for id, node in nodes.items()]

        nodes = defaultdict(list)
        for id, node, bbox in bboxes:
            nodes[self.height(bbox)].append((id,node,bbox))

        ordered_bboxes = []
        for height in sorted(nodes.keys(), reverse=True):
            ordered_bboxes.extend(nodes[height])

        return ordered_bboxes
    
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
        x_start = self.unittouu('3mm')
        y_start = self.unittouu('1600mm') - self.unittouu('3mm')

        total_width = 0
        total_height = 0

        line_nodes = []

        group = etree.SubElement(self.current_layer, addNS('g','svg'))

        for id, node, bbox in nodes:
            x, _, y, _ = bbox

            node_width = x_gap + self.width(bbox)
            # reached end of line, reset, move higher, start new group
            if total_width + node_width > max_line_width:
                group = etree.SubElement(self.current_layer, addNS('g','svg'))
                total_width = 0
                total_height += self.height(self.computeBBox(line_nodes)) + y_gap
                line_nodes = []

            group.append(node)

            x_dest = x_start + total_width
            y_dest = y_start - (total_height + self.height(bbox))

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
            line_nodes.append(node)

    def computeBBox(self, node):
        # turn 'node' into 1-element list if necessary
        if type(node) == list:
            return _computeBBox(node)
        else:
            return _computeBBox([node])

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
