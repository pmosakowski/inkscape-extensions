#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS

from copy import deepcopy

from simpletransform import computeBBox, applyTransformToNode
from simplepath import parsePath, translatePath, formatPath

class FillRow(InkscapeEffect):
    def __init__(self):
        InkscapeEffect.__init__(self)
        self.filename = sys.argv[-1]

    def effect(self):
        if len(self.selected) > 0:
            # bboxes = self.calculate_bboxes(self.selected)
            self.total_height = 0
            for id, node in self.selected.items():
                self.fill_row(node)

    def fill_row(self, node):
        max_line_width = self.unittouu('450mm')

        x_gap = y_gap = self.unittouu('10mm')
        x_start = self.unittouu('3mm')
        y_start = self.unittouu('1600mm') - self.unittouu('3mm')

        total_width = 0
        total_height = self.total_height

        group = etree.SubElement(self.current_layer, addNS('g','svg'))

        bbox = computeBBox([node])
        x, _, y, _ = bbox
        node_width = x_gap + self.width(bbox)

        while total_width + node_width < max_line_width:
            node_copy = deepcopy(node)
            group.append(node_copy)

            x_dest = x_start + total_width
            y_dest = y_start - (total_height + self.height(bbox))

            # translation logic
            if node_copy.tag == addNS('path','svg'):
                x_delta = x_dest - x
                y_delta = y_dest - y

                path = parsePath(node_copy.attrib['d'])
                translatePath(path, x_delta, y_delta)
                node_copy.attrib['d'] = formatPath(path)
            elif node_copy.tag == addNS('g','svg'):
                x_delta = x_dest - x
                y_delta = y_dest - y

                translation_matrix = [[1.0, 0.0, x_delta], [0.0, 1.0, y_delta]]
                applyTransformToNode(translation_matrix, node_copy)

            else:
                node_copy.attrib['x'] = str(x_dest)
                node_copy.attrib['y'] = str(y_dest)

            total_width += node_width

        self.total_height += self.height(computeBBox(group)) + y_gap

    def width(self,bbox):
        (x1, x2, y1, y2) = bbox
        width = x2 - x1

        return width

    def height(self,bbox):
        (x1, x2, y1, y2) = bbox
        height = y2 - y1

        return height


effect = FillRow()
effect.affect()
