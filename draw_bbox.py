#!/usr/bin/env python2

import sys
sys.path.append('/usr/share/inkscape/extensions')

from collections import defaultdict

from inkex import Effect as InkscapeEffect
from inkex import etree, addNS

from simpletransform import computeBBox, applyTransformToNode
from simplestyle import formatStyle
from simplepath import parsePath, translatePath, formatPath

class DrawBBoxes(InkscapeEffect):
    def __init__(self):
        InkscapeEffect.__init__(self)
        self.filename = sys.argv[-1]

    def effect(self):
        if len(self.selected) > 0:
            bboxes = self.calculate_bboxes(self.selected)
            for id, node, bbox in bboxes:
                self.draw_bbox(bbox)

    def calculate_bboxes(self, nodes):
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

effect = DrawBBoxes()
effect.affect()
