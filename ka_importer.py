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
import os
import sys
import traceback

import ka_debug
import ka_extensionpoint

_marker = 'v' + str(ka_extensionpoint.revision_number)
_populated = False
_themes = []
_rgb_image_list = []
_alpha_image_list = []
_svg_image_list = []

def _populate_theme_list(import_path):
    """
    pre: import_path.startswith('/')
    """
    for theme in os.listdir(import_path):
        abs_name = os.path.join(import_path, theme)
        if os.path.isdir(abs_name):
            _themes.append(theme)
            _populate_imports(abs_name, theme)
    _populate_imports(import_path, '')

def _populate_imports(import_path, theme):
    """
    pre: import_path.startswith('/')
    """
    for element in os.listdir(import_path):
        abs_name = os.path.join(import_path, element)
        if os.path.isfile(abs_name):
            if element.lower().endswith('.png'):
                if element.find('.alpha.') == -1:
                    _rgb_image_list.append( (theme, abs_name) )
                else:
                    _alpha_image_list.append( (theme, abs_name) )
            elif element.lower().endswith('.svg'):
                _svg_image_list.append( (theme, abs_name) )

def _populate():
    global _populated
    if _populated:
        return
    _populated = True
    _populate_theme_list(get_import_path())

def get_data_path():
    """
    post: os.path.exists(__return__)
    """
    data_path = ka_debug.DEBUG_PROFILE_PATH # default path for debugging
    if 'SUGAR_BUNDLE_PATH' in os.environ:
        import sugar.env
        ka_debug.info('profile_path    ' + sugar.env.get_profile_path())
        data_path = sugar.env.get_profile_path()
    data_path = os.path.join(data_path, 'net.sourceforge.kandid/data/')
    return data_path

def get_import_path():
    """
    post: os.path.exists(__return__)
    """
    import_path = os.path.join(get_data_path(), 'collection')
    if not os.path.exists(import_path):
        try:
            os.makedirs(import_path)
        except:
#            print 'failed writing [%s] [%s] [%s]' % \
#                       (import_path, sys.exc_info()[0], sys.exc_info()[1])
#            traceback.print_exc(file=sys.__stderr__)
            ka_debug.err('failed writing [%s] [%s] [%s]' % \
                       (import_path, sys.exc_info()[0], sys.exc_info()[1]))
    ka_debug.info('import_path     ' + import_path)
    return import_path

def get_tmp_path():
    """
    post: os.path.exists(__return__)
    """
    tmp_path = ka_debug.DEBUG_PROFILE_PATH # default path for debugging
    if 'SUGAR_BUNDLE_PATH' in os.environ:
        import sugar.env
        ka_debug.info('profile_path    ' + sugar.env.get_profile_path())
        tmp_path = sugar.env.get_profile_path()
    tmp_path = os.path.join(tmp_path, 'net.sourceforge.kandid/tmp')
    ka_debug.info('import_path     ' + tmp_path)
    return tmp_path

def get_theme_list():
    _populate()
    return _themes

def get_rgb_image_list(theme):
    _populate()
    return [x[1] for x in _rgb_image_list if x[0] == theme]

def get_alpha_image_list(theme):
    """
    post: forall(__return__, lambda x: x.lower().endswith('.alpha.png'))
    """
    _populate()
    return [x[1] for x in _alpha_image_list if x[0] == theme]

def get_svg_image_list(theme):
    """
    post: forall(__return__, lambda x: x.lower().endswith('.svg'))
    """
    _populate()
    return [x[1] for x in _svg_image_list if x[0] == theme]

def _make_path(target_path, theme):
    """Create output folder
    pre: os.path.exists(target_path)
    post: os.path.exists(__return__)
    """
    ip = os.path.join(target_path, theme) if len(theme) else target_path
    if not os.path.exists(ip):
        os.makedirs(ip)
    return ip

def _write_file(target_path, theme, file_name, content):
    """Write textual content to the file system.
    """
    out_file = None
    fn = ''
    try:
        fn = os.path.join(_make_path(target_path, theme), file_name)
        if not os.path.exists(fn):
            out_file = open(fn, 'w')
            out_file.write(content)
    except:
        ka_debug.err('failed writing [%s] [%s] [%s]' % \
                   (fn, sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)
    finally:
        if out_file:
            out_file.close()

def _write_surface_file(target_path, theme, file_name, surface):
    """Write graphical content to the file system.
    """
    fn = ''
    try:
        fn = os.path.join(_make_path(target_path, theme), file_name)
        if not os.path.exists(fn):
            surface.write_to_png(fn)
    except:
        ka_debug.err('failed writing [%s] [%s] [%s]' % \
                   (fn, sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)

def _create_icon(is_plus_sign):
    width, height = 16, 16  
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.scale(float(width), float(height))
#    ka_debug.matrix(ctx.get_matrix())
    # paint background
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.paint()
    ctx.set_line_width(0.1)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.move_to(0.0, 0.0)
    ctx.line_to(1.0, 0.0)
    ctx.line_to(1.0, 1.0)
    ctx.line_to(0.0, 1.0)
    ctx.line_to(0.0, 0.0)
    ctx.stroke()
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.move_to(0.2, 0.5)
    ctx.line_to(0.8, 0.5)
    if is_plus_sign:
        ctx.move_to(0.5, 0.2)
        ctx.line_to(0.5, 0.8)
    ctx.stroke()
    return surface

def _post_install():
    """
    pre: len(_marker) >= 2 and int(_marker[1]) > 2
    """
    try:
        tmp_path = get_tmp_path()
        import_path = get_import_path()
        install_marker = os.path.join(import_path, 'install.inf')
        reinstall = not os.path.exists(install_marker)
        if not reinstall:
            in_file = None
            try:
                in_file = open(install_marker, 'r')
                marker = in_file.read()
                reinstall = not marker == _marker
            except:
                reinstall = True
                ka_debug.err('failed reading [%s] [%s] [%s]' % \
                        (install_marker, sys.exc_info()[0], sys.exc_info()[1]))
                traceback.print_exc(file=sys.__stderr__)
            finally:
                if in_file:
                    in_file.close()
        if not reinstall:
            return

        ka_debug.info('running post installation [%s]' % import_path)
        _write_file(import_path, 'segment_of_a_circle', 'stamp_circle.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <circle cx ="50" cy ="50" r ="50" style="fill:#000000"/>

</svg>
''' 
        )
        _write_file(import_path, 'segment_of_a_circle', 'stamp_halfcircle_bottom.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <path
       d="M 0,100 A 50 50 180 0 1 100,100"
       style="fill:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'segment_of_a_circle', 'stamp_halfcircle_left.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <path
       d="M 50,100 A 50 50 180 0 1 50,0"
       style="fill:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'segment_of_a_circle', 'stamp_halfcircle_right.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <path
       d="M 50,100 A 50 50 180 0 0 50,0"
       style="fill:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'segment_of_a_circle', 'stamp_halfcircle_top.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <path
       d="M 0,0 A 50 50 180 0 0 100,0"
       style="fill:#000000;"/>

</svg>
''' 
        )

#---- cybernetic_serendipity
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_ascending_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <line x1="16.666666667" y1="83.333333333320" x2="83.333333333320" y2="16.666666667"
          style="fill:none; stroke-width:3%; stroke:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_circle_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <circle cx ="50" cy ="50" r ="33.333333333"
            style="fill:none; stroke-width:3%; stroke:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_descending_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <line x1="16.666666667" y1="16.666666667" x2="83.333333333320" y2="83.333333333320"
          style="fill:none; stroke-width:3%; stroke:#000000;"/>

</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_horizontal_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <line x1="20" y1="55" x2="80" y2="55"
          style="fill:none; stroke-dasharray:19.166666667,3.3333333333; stroke-width:3%; stroke:#000000;"/>
</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_sawtooth_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <polyline points="20 50, 30 40, 40 50, 50 40, 60 50, 70 40, 80 50"
          style="fill:none; stroke-width:3%; stroke:#000000;"/>
</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_square_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <rect x="26.42977396" y="26.42977396"
          width="47.140452079" height="47.140452079"
          style="fill:none; stroke-width:3%; stroke:#000000;"/>
</svg>
''' 
        )
        _write_file(import_path, 'cybernetic_serendipity', 'stamp_vertical_path.svg',
'''<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100" >

    <line x1="50" y1="16.666666667" x2="50" y2="83.333333333320"
          style="fill:none; stroke-width:3%; stroke:#000000;"/>

</svg>
''' 
        )
        
#---- marktree
        _write_file(tmp_path, '', 'marktree.js',
'''
/* MarkTree JavaScript code
 * 
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 * 
 * Miika Nurminen, 12.7.2004.
 */

/* cross-browser (tested with ie5, mozilla 1 and opera 5) keypress detection */
function get_keycode(evt) {
  // IE
    code = document.layers ? evt.which
           : document.all ? event.keyCode // event.keyCode!=evt.keyCode!
           : evt.keyCode;

  if (code==0) 
    code=evt.which; // for NS
  return code;
}

var lastnode=null;
var listnodes = null;
var list_index=1;
var lastnodetype=''; // determines if node is a link, input or text;

// up, left, down, right, keypress codes
//ijkl
//var keys = new Array(105,106,107,108);
//num arrows
//var keys = new Array(56,52,50,54);
//wasd
// var press2 = new Array(119,97,115,100);
 var press = new Array(47,45,42,43);

// keydown codes
  //  var keys2=new Array(87,65,83,68);
  var keys= new Array(38,37,40,39);

  // keyset 1 = keydown, otherwise press
function checkup(keyset,n) {
  if (keyset==1) return (n==keys[0]);
  return ((n==press[0]) /*|| (n==press2[0])*/)
}

function checkdn(keyset,n) {
  if (keyset==1) return (n==keys[2]);
  return ((n==press[2]) /*|| (n==press2[2])*/)
}

function checkl(keyset,n) {
  if (keyset==1) return (n==keys[1]);
  return ((n==press[1]) /*|| (n==press2[1])*/)
}

function checkr(keyset,n) {
  if (keyset==1) return (n==keys[3]);
  return ((n==press[3]) /*|| (n==press2[3])*/)
}





function is_exp(n) {
  if (n==null) return false;
  return ((n.className=='exp') || (n.className=='exp_active'));
}

function is_col(n) {
  if (n==null) return false;
  return ((n.className=='col') || (n.className=='col_active'));
}

function is_basic(n) {
  if (n==null) return false;
  return ((n.className=='basic') || (n.className=='basic_active'));
}



/* returns i>=0 if true */
function is_active(node) {
  if (node.className==null) return false
  return node.className.indexOf('_active');
}

function toggle_class(node) {
  if ((node==null) || (node.className==null)) return;
  str=node.className;
  result="";
  i = str.indexOf('_active');
  if (i>0)
    result= str.substr(0,i);
  else
    result= str+"_active";
  node.className=result; 
  return node;
}

function activate(node) {
  node.style.backgroundColor='#eeeeff';
}

function deactivate(node) {
   node.style.backgroundColor='#ffffff';
}

function is_list_node(n) {
  if (n==null) return false;
  if (n.className==null) return false;
  if ( (is_exp(n)) || 
       (is_col(n)) ||
       (is_basic(n)) )
   return true; else return false;
}


function get_href(n) {
  alist=n.attributes;
  if (alist!=null) {
    hr = alist.getNamedItem('href');
    if (hr!=null) return hr.nodeValue;
  }
  if (n.childNodes.length==0) return '';
  for (var i=0; i<n.childNodes.length; i++) {
    s = get_href(n.childNodes[i]);
    if (s!='') return s;
  }
  return '';
}

function get_link(n) {
  if (n==null) return null;
  if (n.style==null) return null;

 // disabling uncontrolled recursion to prevent error messages on IE
 // when trying to focus to invisible links (readonly mode)
//    alert(n.nodeName+' '+n.className);
  if ((n.nodeName=='UL') && (n.className=='sub')) return null;

  if (n.nodeName=='A') return n;
  if (n.childNodes.length==0) return null;
  for (var i=0; i<n.childNodes.length; i++) {
    s = get_link(n.childNodes[i]);
    if (s!=null) return s;
  }
  return null;
}

function set_lastnode(n) {
/*var d = new Date();
var t_mil = d.getMilliseconds();*/
// testattu nopeuksia explorerilla, ei merkittäviä eroja
  if (lastnode==n) return; 
/*  deactivate(lastnode)
  lastnode=n;
  activate(lastnode);*/

  if (is_active(lastnode)>=0)
    toggle_class(lastnode);
  lastnode=n;
  if (!(is_active(lastnode)>=0))
    toggle_class(lastnode);


/*var d2 = new Date();
var t_mil2 = d2.getMilliseconds();
  window.alert(t_mil2-t_mil);*/
}

function next_list_node() {
  tempIndex = list_index;
  while (tempIndex<listnodes.length-1) {
    tempIndex++;
    var x = listnodes[tempIndex];
    if (is_list_node(x)) {
      list_index=tempIndex;
      return;
    }
  }
}

function prev_list_node() {
  tempIndex = list_index;
  while (tempIndex>0) {
    tempIndex--;
    var x = listnodes[tempIndex];
    if (is_list_node(x)) {
      list_index=tempIndex;
      return;
    }
  }
}



function getsub (li) {
  if (li.childNodes.length==0) return null;
  for (var c = 0; c < li.childNodes.length; c++)
    if ( (li.childNodes[c].className == 'sub') || (li.childNodes[c].className == 'subexp') ) 
      return li.childNodes[c];
}

function find_listnode_recursive (li) {
  if (is_list_node(li)) return li; 
  if (li.childNodes.length==0) return null;
  result=null;
  for (var c = 0; c < li.childNodes.length; c++) {
    result=find_listnode_recursive(li.childNodes[c]);
    if (result!=null) return result;
  }
  return null;
}

function next_child_listnode(li) {
  var result=null;
  for (var i=0; i<li.childNodes.length; i++) {
    result=find_listnode_recursive(li.childNodes[i]);
    if (result!=null) return result;
  }
  return null;  
}

function next_actual_sibling_listnode(li) {
  if (li==null) return null;
  var temp=li;
  while (1) { 
    var n = temp.nextSibling;
    if (n==null) {
      n=parent_listnode(temp);
      return next_actual_sibling_listnode(n);
    }
    if (is_list_node(n)) return n;
    temp=n;
  }
}

function next_sibling_listnode(li) {
if (li==null) return null; 
 var result=null;
  var temp=li;
  if (is_col(temp)) return next_child_listnode(temp);
  while (1) { 
    var n = temp.nextSibling;
    if (n==null) {
      n=parent_listnode(temp);
      return next_actual_sibling_listnode(n);
    }
    if (is_list_node(n)) return n;
    temp=n;
  }
}

function last_sibling_listnode(li) {
  if (li==null) return null;
  var temp=li;
  var last=null;
  while(1) {
    var n = temp.nextSibling;
    if (is_list_node(temp)) 
      last = temp;
    if (n==null) {
      if (is_col(last)) return last_sibling_listnode(next_child_listnode(last));
      else return last;
    }
    temp = n;
  }
}

function prev_sibling_listnode(li) { 
  if (li==null) return null;
  var temp=li;
  var n = null;
  while (1) { 
    n = temp.previousSibling;
    if (n==null) {
      return parent_listnode(li);
    }
    if (is_list_node(n)) {
      if (is_col(n)) { 
        return last_sibling_listnode(next_child_listnode(n));
      }
      else {
        return n;
      }
    }
    temp=n;
  }
}


function parent_listnode(li) {
  // added 12.7.2004 to prevent IE error when readonly mode==true
  if (li==null) return null;
  n=li;
  while (1) {
    n=n.parentNode;
    if (n==null) return null;
    if (is_list_node(n)) return n;
  }
}

function getVisibleParents(id) {
  var n = document.getElementById(id);
  while(1) {
    expand(n);
    n = parent_listnode(n);
    if (n==null) return;
  }
}

function onClickHandler (evt) {
if (lastnode==null) 
{
listnodes = document.getElementsByTagName('li');
lastnode=listnodes[1];
temp=listnodes[1];
}


  var target = evt ? evt.target : event.srcElement;
  if (!is_list_node(target)) return;
  toggle(target);
  set_lastnode(target);
}


function expand(node) {
    if (!is_exp(node)) return;
    if (node.className=='exp_active') 
      node.className='col_active';
    else 
        node.className='col';
    setSubClass(node,'subexp');
    //    getsub(node).className='subexp';
}

function collapse(node) {
  if (!is_col(node)) return;
  
if (node.className=='col_active')
    node.className='exp_active'
  else 
    node.className='exp';

 setSubClass(node,'sub');
//  getsub(node).className='sub';

}

function setSubClass(node,name) {
  sub = getsub(node);
  if (sub==null) return;
  sub.className=name;  
}

function toggle(target) {
  if (!is_list_node(target)) return;
    if (is_col(target)) {
      target.className='exp';
      setSubClass(target,'sub');
      //      getsub(target).className='sub';
    }
    else if (is_exp(target)) {
      target.className='col';
      setSubClass(target,'subexp');
      //      getsub(target).className='subexp';
    }
 
}

function expandAll(node) {
    if (node.className=='exp') {
        node.className='col';
        setSubClass(node,'subexp');
//        getsub(node).className='subexp';
    }
    var i;
    if (node.childNodes!=null) 
//    if (node.hasChildNodes()) 
        for ( i = 0; i<node.childNodes.length; i++)
            expandAll(node.childNodes[i]);
}

function collapseAll(node) {
    if  (node.className=='col') {
        node.className='exp';
        setSubClass(node,'sub');
//        getsub(node).className='sub';
    }
    var i;        
    if (node.childNodes!=null) 
// for opera   if (node.hasChildNodes()) 
        for ( i = 0; i<node.childNodes.length; i++)
            collapseAll(node.childNodes[i]);
}



function unFocus(node) {
     // unfocuses potential link that is to be hidden (if a==null there is no link so it should not be blurred).
     // tested with mozilla 1.7, 12.7.2004. /mn (
      intemp=parent_listnode(node);  
      a = get_link(intemp);     // added 6.4. to get keyboard working with
      // moved before collapse to prevent an error message with IE when readonly==true      
      if (a!=null) a.blur(); // netscape after collapsing a focused node
      return intemp;
}

// mode: 0==keypress, 1==keyup
function keyfunc(evt,mode) {
 var c = get_keycode(evt);
 var temp = null;
 var a = null;

  if (lastnode==null) {
    listnodes = document.getElementsByTagName('li');
    lastnode=listnodes[1];
    temp=listnodes[1];
  }

  //window.alert(c);
  if (checkup(mode,c)) { // i 
   temp=prev_sibling_listnode(lastnode);
  }
  else if (checkdn(mode,c)) { // k
    temp=next_sibling_listnode(lastnode);
  }
  else if (checkr(mode,c)) { // l
    expand(lastnode);
    //  temp=next_child_listnode(lastnode);
    // if (temp==null) {
      a = get_link(lastnode);
        if (a!=null) a.focus(); else self.focus(); 
      //}
  }
  else if (checkl(mode,c)) { // j
    if (is_col(lastnode)) {
      unFocus(lastnode);
      collapse(lastnode);
    }
    else {
      temp=unFocus(lastnode);
      collapse(temp);
    }
   //    if (temp==null) lastnode.focus(); // forces focus to correct div (try mozilla typesearch) (doesn't seem to work -mn/6.4.2004)
  }
  else return;
  if (temp!=null) set_lastnode(temp);

  // alert('pressed ' + String.fromCharCode(c) + '(' + c + ')');
  return true;
}


function keytest (evt) {
  return keyfunc(evt,1);
};


function presstest (evt) {
  return keyfunc(evt,0);
};


  document.onclick = onClickHandler;
  document.onkeypress = presstest;
  document.onkeyup = keytest;
'''
        )
        
        _write_file(tmp_path, '', 'treestyles.css',
'''
body {
    background-color: #eeeeee;
      color: #000000;
    font-family : 'DejaVu Sans', 'Sans Serif', sans-serif;
}

:link { color: #0000ff; text-decoration:none;}
:visited { color: #6666ff; text-decoration:none; }
a:active { color: #0000ff; text-decoration:none;}
a:hover {color: #0000ff; text-decoration:underline; }

div.basetext {
    background-color:#ffffff;
        margin-top:11px;
        margin-bottom:11px;
    margin-left:1%;
    margin-right:1%;
    padding-top:11px;
    padding-left:11px;
    padding-right:11px;
    padding-bottom:11px;
    text-align:left;
    font-weight:normal;
  border-width:thin;
  border-style:solid;
  border-color:#dddddd;
}

div.basetop {
  position: fixed;
  width:auto;
  height:auto;
  right:0em;
  top:0em;
  left:auto; 
  top:0;
    background-color:#ffffff;
        margin-top:0;
        margin-bottom:0;
    margin-left:1%;
    margin-right:1%;
    padding-top:2px;
    padding-left:11px;
    padding-right:11px;
    padding-bottom:2px;
    text-align:left;
    font-weight:normal;
text-align:right;
  border-width:thin;
  border-style:solid;
  border-color:#dddddd;
}

h1 {
    text-align:center;
}

span.h2 {
    font-family : 'DejaVu Sans', 'Sans Serif', sans-serif;
    font-weight:bold;
}

div.year {
    margin-right:2%;
    background-color:#eeeeee;
}

div.form {
}

span.cpt {
    color:#005500;
    font-weight:bold;
}

span.cm {
    color:#666666;
}

.fl {
    color:#0000FF;    
    font-style:italic;
}

ul {
    margin-top:1px;
        margin-bottom:1px;
    margin-left:0px;
    padding-left:3%;
}

li {
    list-style:outside;
  margin-top:10px;   
  margin-bottom:10px;
}

ul li {
    list-style:square;
    font-family : 'DejaVu Sans', 'Sans Serif', sans-serif;
    font-weight:normal;
}

li.basic {
    list-style:square;
    list-style-image:none;
  margin-top:2px;
  margin-bottom:2px;
}

span.links {
}




.sub { display: none; }
.subexp {display: block; }
.sub { display: none; } 

.subexp {display: block; } 

li.exp {
  list-style-image:url("plus.png");
  margin-top:10px;
  margin-bottom:10px;
  cursor:pointer;
}

li.col {
  list-style-image:url("minus.png");
  margin-top:10px;
  margin-bottom:10px;
  cursor:pointer;
}

li.exp_active {
  list-style-image:url("plus.png");
  margin-top:10px;  
  margin-bottom:10px;
  background-color:#eeeeff;
  cursor:pointer;
}

li.col_active {
  list-style-image:url("minus.png");
  margin-top:10px;
  margin-bottom:10px;
  background-color:#eeeeff;
  cursor:pointer; /* if not included, bullets are not shown right in moz*/
}


li.basic_active {
  list-style:square;
  list-style-image:none;
  background-color:#eeeeff;
  margin-top:2px;
  margin-bottom:2px;
}
'''
        )
        
#---- icons used by marktree
        #Calculate an '+' and a '-' icon.
        _write_surface_file(tmp_path, '', 'minus.png', _create_icon(False))
        _write_surface_file(tmp_path, '', 'plus.png', _create_icon(True))

#---- write version marker
        _write_file(import_path, '', 'install.inf', _marker)
    except:
#        print 'post install failed [%s] [%s]' % \
#                   (sys.exc_info()[0], sys.exc_info()[1])
#        traceback.print_exc(file=sys.__stderr__)
        ka_debug.err('post install failed [%s] [%s]' % \
                     (sys.exc_info()[0], sys.exc_info()[1]))

_post_install()