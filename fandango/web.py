#!/usr/bin/env python

#############################################################################
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################

"""

Some extensions to python dictionary
ThreadDict: Thread safe dictionary with redefinable read/write methods and a backgroud thread for hardware update.
defaultdict_fromkey: Creates a dictionary with a default_factory function that creates new elements using key as argument.
CaselessDict: caseless dictionary
CaselessDefaultDict: a join venture between caseless and default dict

@deprecated
@note see in tau.core.utils.containers

by Sergi Rubio, 
srubio@cells.es, 
2010 
"""


import sys,time,traceback
import fandango
from fandango.functional import time2str,isString,isSequence,toList
import pickle
import PyQt4
from PyQt4 import Qt
from PyQt4.Qt import QColor
#import fandango.qt

#import guiqwt
#import guidata
#from guiqwt.plot import CurveDialog
#from guiqwt.builder import make
#from guiqwt.styles import COLORS

###############################################################################

page = lambda s: '<html>%s</html>'%s
body = lambda s: '<body>%s</body>'%s
paragraph = lambda s: '<p>%s</p>'%s
code = lambda s: '<pre>%s</pre>'%str(s)
raw = code
linebreak = '<br>'
separator = '<hr>'

ulist = lambda s: '<ul>%s</ul>'%s
item = lambda s: '<li>%s</li>'%s

bold = lambda s: '<b>%s</b>'%s
em = lambda s: '<em>'+str(s)+'</em>'
under = lambda s: '<u>\n'+str(s)+'\n</u>'
camel = lambda s: ''.join(r[0].upper()+(r[1:] or '').lower() for r in s.split())
color = lambda s,color: '<font color="%s">%s</font>'%(camel(color),s)
colors = "black white yellow blue green red gray fuchsia lime maroon aqua navy olive purple silver teal".split()
size = lambda s,size: '<font size="%s">%s</font>'%(size,s)

link = lambda s,url: '<a href="%s">%s</a>' % (url,s)
iname = lambda s: s.replace(' ','').lower()
iurl = lambda url: '#'+iname(url)
ilink = lambda s,url: '<a name="%s">%s</a>' % (iname(s),s)
title = lambda s,n=1: '<a name="%s"><h%d>%s</h%d></a>' % (iname(s),n,s,n) #<a> allows to make titles linkable
title1 = lambda s: '<h1>%s</h1>'%s

row,cell = (lambda s: '<tr>%s</tr>'%s) , (lambda s: '<td>%s</td>'%s)
table = lambda s: '<table border=1>\n'+'\n'.join([row(''.join([
                            (cell('%s'%c) if (len(s)==1 or j or (len(toList(r))<3 and i)) else cell(bold('%s'%c)))
                                for j,c in enumerate(toList(r))])) 
                            for i,r in enumerate(s)]
                   )+'\n</table>'

def list_to_ulist(l):
    return ulist('\n'.join(item(str(s)) for s in l))

def dicts2table(dcts,keys=None,formatter=None):
    """
    :param dcts:  a list of dictionaries
    :param keys: an alternative list of keys
    """
    if not keys: keys = sorted(set(k for dct in dcts for k in dct.keys()))
    if not formatter: formatter = lambda s:s
    lines = [keys,]
    for dct in dcts:
        lines.append([formatter(dct.get(k,'')) for k in keys])
    return table(lines)
    
def dict2dict2table(seq,keys=None,formatter=None):
    """
    :param seq: a nested dictionary {:{}}
    :param keys:  a list of header names
    """
    if not keys: keys = [""]+sorted(set(k for v in seq.values() for k in v.keys()))
    if not formatter: formatter = lambda s:s
    lines = [keys,]
    for k,v in sorted(seq.items()):
        line = [k]
        for k in keys[1:]:
            line.append(formatter(v.get(k,'')))
        lines.append(line)
    return table(lines)
    

###############################################################################

MULTIPLIER = 10
OFFSETS = [-15,-30,-45,-60,-75,-90,-105,-120]
COLORS = {
 'red': (255, 0, 0, 255),  
 'blue': (0, 0, 255, 255),
 'darkgreen': (0, 100, 0, 255),
 'grey': (128, 128, 128, 255),
 'lightblue': (173, 216, 230, 255),
 'lightgreen': (144, 238, 144, 255),
 'magenta': (255, 0, 255, 255),
 'orange': (255, 165, 0, 255),
 'violet': (238, 130, 238, 255)
 }
HEXs = {
 'red': '#ff0000',
 'blue': '#0000ff',
 'darkgreen': '#006400',
 'grey': '#808080',
 'lightblue': '#add8e6',
 'lightgreen': '#90ee90',
 'magenta': '#ff00ff',
 'orange': '#ffa500',
 'violet': '#ee82ee'
 }

all_colors = COLORS.values()


#ats = [CURRENT]+FRONTENDS
#all_colors = [fg]+FECOLORS
#t = [time.time()-DAYS*24*3600,time.time()]

###############################################################################
#import PyTangoArchiving
#from PyTangoArchiving.utils import decimate_array
###############################################################################

def jqplot(title,ats):
    #USING jqPlot instead of Qt
    js = 'http://www.cells.es/static/Files/Computing/Controls/Reports/js'
    includes = """
        <script language="javascript" type="text/javascript" src="$JS/jquery.min.js"></script>
        <script language="javascript" type="text/javascript" src="$JS/jquery.jqplot.min.js"></script>
        <script type="text/javascript" src="$JS/plugins/jqplot.canvasAxisTickRenderer.min.js"></script>
        <script type="text/javascript" src="$JS/plugins/jqplot.dateAxisRenderer.min.js"></script>
        <link rel="stylesheet" type="text/css" href="$JS/jquery.jqplot.css" />
        """.replace('$JS',js)
    jqp_template = """
        <div id="chartdiv" style="height:100%;width:100%; "></div>
        <script class="code" type="text/javascript">
        //var line1=[['2008-08-12 4:00',4], ['2008-09-12 4:00',6.5], ['2008-10-12 4:00',5.7], ['2008-11-12 4:00',9], ['2008-12-12 4:00',8.2]];
        //var line1 = [['2012-09-17 16:44', -0.24086535644531001], ['2012-09-17 16:44', -0.166169769287108], ['2012-09-17 16:45', -0.097435409545898494]];
        //var line1 = [['2012-09-17 16:41:25', -0.0238617248535157], ['2012-09-17 16:45:34', 0.058192413330078102], ['2012-09-17 16:49:34', 0.19318386840820501], ['2012-09-17 16:49:45', 0.61706387329101398], ['2012-09-17 16:49:55', 1.0387241058349601], ['2012-09-17 16:50:15', 1.54242512512208], ['2012-09-17 16:50:35', 2.4866759948730399], ['2012-09-17 16:51:34', 4.2881499938964902], ['2012-09-17 17:39:05', 2.0870143585204999], ['2012-09-17 17:39:15', -0.115877944946289], ['2012-09-17 17:43:55', -0.216508895874022], ['2012-09-17 17:50:45', -0.12760966491699099], ['2012-09-17 17:51:05', 0.00132557678222655], ['2012-09-17 17:51:14', 0.093648117065429706], ['2012-09-17 17:51:25', 0.17557904052734499], ['2012-09-17 17:51:35', 0.27481381225586199], ['2012-09-17 17:51:45', 0.45713497924804802], ['2012-09-17 17:52:05', 0.70768925476073896], ['2012-09-17 17:52:24', 1.0928863220214899], ['2012-09-17 17:52:55', 1.6552524261474699], ['2012-09-17 17:54:24', 2.6534446411132699], ['2012-09-17 17:57:35', 4.5955463104248198], ['2012-09-17 18:00:45', 7.7440131835937498], ['2012-09-17 19:02:15', 12.3284885101318], ['2012-09-17 19:15:35', 7.1876571350097702], ['2012-09-17 19:15:45', 0.51328236389160098], ['2012-09-17 19:16:35', 0.82798764038085604], ['2012-09-17 19:18:05', 1.2241496734619199], ['2012-09-17 19:18:25', 1.97309834289551], ['2012-09-17 19:18:45', 3.0986022644042799], ['2012-09-17 19:19:25', 4.5590980224609501], ['2012-09-17 19:19:55', 6.3049014739990499], ['2012-09-17 19:21:15', 10.757810562133701], ['2012-09-17 19:22:15', -0.19701274108886499], ['2012-09-17 19:22:25', 0.40055233764648701], ['2012-09-17 19:22:35', 1.10074002075196], ['2012-09-17 19:22:45', 1.6407546691894599], ['2012-09-17 19:23:15', 3.0096213989257699], ['2012-09-17 19:23:45', 4.4580032043457098], ['2012-09-17 19:24:25', 6.4163531951904602], ['2012-09-17 19:25:55', 10.671424835205], ['2012-09-17 19:27:35', 16.0758376770019], ['2012-09-17 19:36:35', -0.088338500976562498], ['2012-09-17 19:37:25', -0.0030716247558593901], ['2012-09-17 19:38:05', 0.081846588134765599], ['2012-09-17 19:38:45', 0.18200032043457201], ['2012-09-17 19:39:25', 0.24985005187988499]];
        line1 = $DATA;
        //var ticks = [[1,'Dec 10'], [2,'Jan 11'], [3,'Feb 11'], [4,'Mar 11'], [5,'Apr 11'], [6,'May 11'], [7,'Jun 11'], [8,'Jul 11'], [9,'Aug 11'], [10,'Sep 11'], [11,'Oct 11'], [12,'Nov 11'], [13,'Dec 11']]; 
        $(document).ready(function(){
            var plot1 = $.jqplot('chartdiv',  line1,
            { title:'$TITLE',
                //axes:{yaxis:{min:-10, max:240}},
                axes:{
                    xaxis:{
                        //ticks: ticks,
                        renderer:$.jqplot.DateAxisRenderer,
                        //min: "09-01-2008 16:00",
                        //max: "06-22-2009 16:00",
                        //rendererOptions:{
                        //        tickInset: 0,
                        //        tickRenderer:$.jqplot.CanvasAxisTickRenderer
                        //    },                        
                        tickOptions:{
                            formatString:'%b %e',
                            angle: -40
                            },
                                // For date axes, we can specify ticks options as human
                                // readable dates.  You should be as specific as possible,
                                // however, and include a date and time since some
                                // browser treat dates without a time as UTC and some
                                // treat dates without time as local time.
                                // Generally, if  a time is specified without a time zone,
                                // the browser assumes the time zone of the client.
                        //tickInterval: "2 weeks",
                        //tickRenderer: $.jqplot.CanvasAxisTickRenderer,
    
                        label:'Time(s)',
                        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                        },
                    yaxis:{
                        label:'Am',
                        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                        }
                    },
                $SERIES,
                legend:{
                    show:true,
                    placement: 'outsideGrid',
                    //location: 'e',
                    }
            });
        });
        </script>
        """
    serie = """
            {
                label:'$ATTR',
                lineWidth: 3,
                //color:'#5FAB78',
                color: "$COLOR",
                showMarker:false,
                //fill:true,
                //fillAndStroke:true,
            }
        """#.replace('$ATTR',CURRENT).replace('$COLOR','rgba(255, 0, 0, 0.5)')
    series = 'series:[\n%s\n]'%',\n'.join([
        serie.replace('$ATTR',a).replace('$COLOR','rgba(%d,%d,%d,1)'%all_colors[i][:3])
        for i,a in enumerate(ats)
        ])
    #data = """[[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]]"""
    data = str([
        list([fandango.time2str(t[0]),t[1]] for t in vals[k]) for k in ats]
        )
    return jqp_template.replace('$DATA',data).replace('$SERIES',series).replace('$TITLE',title)

from . import doc
__doc__ = doc.get_fn_autodoc(__name__,vars())

