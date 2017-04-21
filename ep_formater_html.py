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
import ka_utils

"""Generate HTML describing the genome."""

import os
import sys
import traceback

import ka_debug
import exon_color
import exon_position
import exon_direction

class HtmlFormater(object):
    """Html formater
    inv: self._indent >= 0
    """

    generator = u'Minimal Kandid'

    def __init__(self, base_name, unique_id, base_folder):
        """Constructor for HTML formater."""
        self._base_name = base_name.replace(' ', '_')
        self.unique_id = unique_id
        self._base_folder = base_folder.replace(' ', '_')
        self._indent = 0
        self._page = u''
        self.produced_files_list = []
        self.id_count = 0
        self._header_occured = False # debugging only
        self._footer_occured = False # debugging only
        file_path = os.path.join(base_folder, unique_id)
        if not os.path.exists(file_path):
            try:
                os.mkdir(file_path)
            except:
                ka_debug.err('creating directory [%s] [%s] [%s]' % \
                          (file_path, sys.exc_info()[0], sys.exc_info()[1]))
                traceback.print_exc(file=sys.__stderr__)
           

    def _escape(self, text):
        """Quote special characters '<' and '&'.
        This must be done to produce correct HTML.
        pre: text is not None
        """
        utext = unicode(text)
        quoted = u''
        for uchar in utext:
            if uchar in [u'<']:
                quoted += u'&lt;'
            elif uchar in [u'&']:
                quoted += u'&amp;'
            else:
                quoted += uchar
        return quoted

    def _append(self, lines):
        """Append lines to HTML page.
        pre: lines is not None
        """
        indenting = u' '*(2*self._indent)
        for line in lines:
            self._page += indenting + line + u'\n'

    def _append_escaped(self, text):
        """Append text to HTML page.
        pre: text is not None
        """
        self._page += self._escape(text)

    def _get_id(self):
        """Returns a unique id.
        All elements generated are decorated with an id.
        We need this to use the HTML page like a tree widget.
        """
        self.id_count += 1
        return u'id_' + unicode(self.id_count)

    def get_absolutename(self, extension, postfix=None):
        """Returns absolute path appended by filename
         of the generated HTML page."""
        return os.path.join(self.get_pathname(),
                            self.get_filename(extension, postfix))
        
    def get_pathname(self):
        """Returns absolute path."""
        return os.path.join(self._base_folder, 
                            self.unique_id)
        
    def get_filename(self, extension, postfix=None):
        """Returns the filename only of the generated HTML page."""
        postfix = '' if postfix is None else '_' + postfix
        return self._base_name + postfix + '.' + extension
        
    def header(self, title):
        """Generate starting sequence to the HTML page.
        pre: not self._header_occured
        pre: not self._footer_occured
        """
        self._append( (
        u'<?xml version="1.0" encoding="UTF-8"?>',
        u'<?xml-stylesheet href="../treestyles.css" type="text/css"?>',
        u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"',
        u'  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
        u'',
        u'<html xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">',
        u'<head>',
        u'  <meta name="generator" content="' + HtmlFormater.generator +'" />',
        u'',
        u'  <title>' + title + u'</title>',
        u'  <link rel="stylesheet" href="../treestyles.css" type="text/css" />',
        u'  <script type="text/javascript" src="../marktree.js">',
        u'//<![CDATA[',
        u'',
        u'  //]]>',
        u'  </script>',
        u'</head>',
        u'',
        u'<body>',
        u'  <div class="basetop">',
        u'    <a href="#" onclick="expandAll(document.getElementById(\'base\'))">Expand</a> -',
        u'    <a href="#" onclick="collapseAll(document.getElementById(\'base\'))">Collapse</a>',
        u'  </div>',
        u'',
        u'  <div id="base" class="basetext">',
        u'',
        u'    <ul>',
                    ) )
        self._header_occured = True

    def footer(self):
        """Generate finishing sequence to the HTML page.
        pre: self._indent == 0
        pre: self._header_occured
        pre: not self._footer_occured
        """
        self._append( (
        u'    </ul>',
        u'  </div>',
        u'</body>',
        u'</html>',
                    ) )
        self._footer_occured = True

    def _begin_list_item(self, identification):
        """Start a list item.
        pre: self._header_occured
        pre: not self._footer_occured
        """
        self._append( (
        u'          <li class="basic" id="id_' + identification + u'" >',
        u'            <span>',
                    ) )

    def _end_list_item(self):
        """Close a list item.
        pre: self._header_occured
        pre: not self._footer_occured
        """
        self._append( (
        u'            </span>',
        u'          </li>',
                    ) )
        
    def _image_item(self, filename, width, height, description, newline=True):
        """Append an image tag to the page.
        pre: filename is not None
        pre: width is not None
        pre: height is not None
        pre: description is not None
        """
        if newline:
            self._append( (
            u'              <br />',
                        ) )
        self._append( (
        u'              <img style="background-color:#000000" src="' + filename + u'"' \
                         + u' width="' + unicode(width) + u'"' \
                         + u' height="' + unicode(height) + u'"' \
                         + u' alt="' + description + u'"'
                         + u' title="' + description + u'" border="1" />',
                    ) )

    def begin_list(self, text):
        """Start a list.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: text is not None
        """
        self._indent += 1
        self._append( (
        u'      <li class="col" id="' + self._get_id() + u'">',
        self._escape(text),
        u'          <ul class="subexp">',
                             ) )

    def end_list(self):
        """Close a list.
        pre: self._header_occured
        pre: not self._footer_occured
        """
        self._append( (
        u'        </ul>',
        u'    </li>',
                    ) )
        self._indent -= 1
        
    def text_item(self, text):
        """Generate an item for using in text lists.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: text is not None
        """
        self._begin_list_item(self._get_id())
        self._append_escaped(text)
        self._end_list_item()

    def text_list(self, title, text_list):
        """Generate a text list.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: text_list is not None
        """
        self._begin_list_item(self._get_id())
        self._append_escaped(title)
        for text in text_list:
            self._append_escaped(text + u', ')
        self._end_list_item()

    def color_item(self, color, text, alpha=True):
        """Generate a preview icon showing colors.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: color is not None
        pre: text is not None
        """
        identification = self._get_id()
        pathname = self.get_absolutename('png', postfix=identification)
        filename = self.get_filename('png', postfix=identification)
        surface = exon_color.Color.make_icon(color.rgba, alpha,
                                 ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT)
        surface.write_to_png(pathname)
        self.produced_files_list.append(pathname)

        description = color.explain(alpha)
        self._begin_list_item(identification)
        self._append_escaped(text)
        self._image_item(filename, ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT,
                         description)
        self._end_list_item()

    def alpha_item(self, alpha, text):
        """Generate a preview icon showing transparency.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: alpha is not None
        pre: text is not None
        """
        identification = self._get_id()
        pathname = self.get_absolutename('png', postfix=identification)
        filename = self.get_filename('png', postfix=identification)
        surface = exon_color.Color.make_icon((1.0, 1.0, 1.0, alpha), True,
                                     ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT)
        surface.write_to_png(pathname)
        self.produced_files_list.append(pathname)

        description = '%d%% opaque' % (100*alpha)
        self._begin_list_item(self._get_id())
        self._append_escaped(text)
        self._image_item(filename, ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT,
                         description)
        self._end_list_item()

    def color_array(self, color_list, text, alpha=True):
        """Generate some preview icons showing colors.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: color_list is not None
        pre: text is not None
        """
        self._begin_list_item(self._get_id())
        self._append_escaped(text)
        self._append( (u'              <br />',) )
        for color in color_list:
            identification = self._get_id()
            pathname = self.get_absolutename('png', postfix=identification)
            filename = self.get_filename('png', postfix=identification)
            surface = color.make_icon(color.rgba, alpha,
                                      ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT)
            surface.write_to_png(pathname)
            self.produced_files_list.append(pathname)
            description = color.explain(alpha)
            self._image_item(filename,
                             ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT,
                             description, newline=False)
        self._end_list_item()

    def position_item(self, position, text):
        """Generate a preview icon showing a position.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: position is not None
        pre: text is not None
        """
        self.position_array([position], text)

    def position_array(self, position_list, text):
        """Generate some preview icons showing positions.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: position_list is not None
        pre: text is not None
        """
        description = u'['
        for position in position_list:
            description += position.explain() + u'; '
        description += u']'
        
        self._begin_list_item(self._get_id())
        self._append_escaped(text + u' ' + description)
        identification = self._get_id()
        pathname = self.get_absolutename('png', postfix=identification)
        filename = self.get_filename('png', postfix=identification)
        surface = exon_position.Position.make_icon(position_list,
                                    ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT)
        surface.write_to_png(pathname)
        self.produced_files_list.append(pathname)
        self._image_item(filename, ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT,
                         description)
        self._end_list_item()

    def direction_item(self, direction, text):
        """Generate a preview icon showing one direction vectors.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: direction is not None
        pre: text is not None
        """
        self.direction_array([direction], text)

    def direction_array(self, direction_list, text):
        """Generate some preview icons showing direction vectors.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: direction_list is not None
        pre: text is not None
        """
        description = u'['
        for direction in direction_list:
            description += direction.explain() + u'; '
        description += u']'

        self._begin_list_item(self._get_id())
        self._append_escaped(text + u' ' + description)
        identification = self._get_id()
        pathname = self.get_absolutename('png', postfix=identification)
        filename = self.get_filename('png', postfix=identification)
        surface = exon_direction.Direction.make_icon(direction_list,
                                     ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT)
        surface.write_to_png(pathname)
        self.produced_files_list.append(pathname)
        self._image_item(filename, ka_utils.ICON_WIDTH, ka_utils.ICON_HEIGHT,
                         description)
        self._end_list_item()

    def surface_item(self, surface, text, description):
        """Generate a preview icon of the layers surface.
        pre: self._header_occured
        pre: not self._footer_occured
        pre: surface is not None
        pre: text is not None
        pre: description is not None
        """
        identification = self._get_id()
        pathname = self.get_absolutename('png', postfix=identification)
        filename = self.get_filename('png', postfix=identification)
        surface.write_to_png(pathname)
        self.produced_files_list.append(pathname)
        width  = surface.get_width()
        height = surface.get_height()

        self._begin_list_item(self._get_id())
        self._append_escaped(text)
        self._image_item(filename, width, height, description)
        self._end_list_item()

    def write_html_file(self, file_path):
        """Write HTML to the file system.
        pre: self._header_occured
        pre: self._footer_occured
        pre: self._indent == 0
        pre: file_path is not None
        """
        out_file = None
        try:
            out_file = open(file_path, 'w')
            out_file.write(self._page.encode('utf-8'))
            self.produced_files_list.append(file_path)
        except:
            ka_debug.err('failed writing [%s] [%s] [%s]' % \
                       (file_path, sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        finally:
            if out_file:
                out_file.close()
