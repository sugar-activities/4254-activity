# coding: UTF-8
# Copyright 2009, 2010 Thomas Jourdan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import cairo

import ka_debug

ICON_WIDTH = ICON_HEIGHT = 48

def explain_points(head, points):
    """
    pre: points is not None
    post: __return__ is not None
    """
    description = '['
    for point in points:
        description += '%4.3f, %4.3f; ' % (point[0], point[1])
    description += ']'
    text = head + ' ' + description if head is not None and len(head) \
                                    else description

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ICON_WIDTH, ICON_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(ICON_WIDTH, ICON_HEIGHT)
#    ka_debug.matrix(ctx.get_matrix())
    # paint background
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.paint()
    radius = 0.1
    ctx.set_line_width(0.02)
    for point in points:
        # paint a cross for each position
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.move_to(0.5+point[0]-radius, 0.5+point[1]-radius)
        ctx.line_to(0.5+point[0]+radius, 0.5+point[1]+radius)
        ctx.move_to(0.5+point[0]+radius, 0.5+point[1]-radius)
        ctx.line_to(0.5+point[0]-radius, 0.5+point[1]+radius)
        ctx.stroke()
    return text, surface, head
