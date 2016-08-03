#!/usr/bin/env python

#############################################################################
##
## file :       db.py
##
## description : This module simplifies database access.
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2014 $
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

import Queue,traceback,time,sys,os
from functools import partial
import fandango
from fandango.functional import isString,isSequence,isDictionary,isCallable
from fandango.log import Logger,shortstr
from fandango.dicts import SortedDict
from fandango.objects import Singleton,Decorated,Decorator,ClassDecorator,BoundDecorator

def getQt(full=False):
    """
    Choosing between PyQt and Taurus Qt distributions
    """
    try:
        import taurus
        taurus.setLogLevel(taurus.Warning)
        from taurus.external.qt import Qt,QtCore,QtGui
    except:
        from PyQt4 import Qt,QtCore,QtGui
    if full:
        return Qt,QtCore,QtGui
    else:
        return Qt

Qt,QtCore,QtGui = getQt(True)

###############################################################################

def getStateLed(model):
    from taurus.qt.qtgui.display import TaurusStateLed
    led = TaurusStateLed()
    led.setModel(model)
    print 'In TaurusStateLed.setModel(%s)'%model
    return led

def checkApplication(args=None):
    try:
      assert Qt.QApplication.instance(),'QApplication not running!'
      return True
    except:
      return False

def getApplication(args=None):
    app = Qt.QApplication.instance()
    return app or Qt.QApplication(args or [])

def execApplication():
    getApplication().exec_()
   
def getQwtTimeScaleDraw():
    from PyQt4 import Qt,Qwt5
    from PyQt4.Qwt5 import qplt,QwtScaleDraw,QwtText
    class QwtTimeScale(QwtScaleDraw):
        def label(self,v):
            return QwtText('\n'.join(fandango.time2str(v).split()))
    return QwtTimeScale()
    
def getRandomColor(i=None):
    import random
    ranges = 50,230
    if i is not None:
        ranges = map(int,(170,256/(i+.01),256%(i+0.01),256-256/(i+0.01)) if i<256 else (170,i/256.,i%256))
        ranges = min(ranges),max(ranges)
        print ranges
    return Qt.QColor(
        int(random.randint(*ranges)),
        int(random.randint(*ranges)),
        int(random.randint(*ranges)))

def getQwtPlot(series,xIsTime=False):
    """ Series would be a {Label:[(time,value)]} dictionary """
    app = getApplication()
    from PyQt4 import Qt,Qwt5
    from PyQt4.Qwt5 import qplt,QwtScaleDraw
    qpt = qplt.Plot(*[qplt.Curve(
            [x[0] for x in t[1]],
            [y[1] for y in t[1]],t[0],
            qplt.Pen(getRandomColor(i=None),2)) 
        for i,t in enumerate(series.items())])
    if xIsTime: qpt.setAxisScaleDraw(qpt.xBottom,getQwtTimeScaleDraw())
    return qpt

class QDialogWidget(Qt.QDialog):
    """
    It converts any Widget into a Dialog
    
    setAccept method allows to easily connect the accepted() signal to a callable
    """
    def __init__(self,parent=None,flags=None,buttons=None):
        if flags is not None: Qt.QDialog.__init__(self,parent,flags)
        else: Qt.QDialog.__init__(self,parent)
        self.buttons = buttons
        self.setLayout(Qt.QVBoxLayout())
        if self.buttons:
            self.buttons = Qt.QDialogButtonBox(Qt.QDialogButtonBox.Ok|Qt.QDialogButtonBox.Cancel)
            self.connect(self.buttons,Qt.SIGNAL('accepted()'),self.accept)
            self.connect(self.buttons,Qt.SIGNAL('rejected()'),self.reject)
            self.layout().addWidget(self.buttons)
    def widget(self):
        self._widget = getattr(self,'_widget',None)
        return self._widget
    def setWidget(self,widget,accept_signal=None,reject_signal=None):
        widget.setParent(self)
        self.layout().insertWidget(0,widget)
        self.setSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding)
        self._widget = widget
        if accept_signal:self.connect(widget,Qt.SIGNAL(accept_signal),self.accept)
        if reject_signal:self.connect(widget,Qt.SIGNAL(reject_signal),self.reject)
        self.updateGeometry()
        return self
    def sizeHint(self):
        return Qt.QDialog.sizeHint(self)
    def setAccept(self,f):
        """connect the accepted() signal to a callable"""
        self.connect(self.buttons or self,Qt.SIGNAL('accepted()'),f)
        
class QOptionDialog(QDialogWidget):
    """
    This class provides a fast way to update a dictionary from a Qt dialog
    
    s = fandango.Struct(name='test',value=7.8)
    qo = QOptionDialog(model=s,cast=s.cast,title='Options')
    qo.show()
    #Edit and save the values
    s.value : 5.0
    
    Using plain dicts:
    d = {'name':'A','value':4}
    qo = QOptionDialog(model=d,cast=fandango.str2type,title='Options')
    qo.exec()
    """
  
    def __init__(self,parent=None,model={},title='',cast=None):
      QDialogWidget.__init__(self,parent,buttons=True)
      self.accepted = False
      self.cast = cast
      if model: self.setModel(model)
      if title: self.setWindowTitle(title)
      self.connect(self,Qt.SIGNAL('accepted'),self.close)
      
    def setModel(self,model):
      self._model = model
      self._widget = Qt.QWidget()
      self._widget.setLayout(Qt.QGridLayout())
      self._edits = {}
      for i,t in enumerate(self._model.items()):
        k,w = str(t[0]),Qt.QLineEdit(str(t[1]))
        self._widget.layout().addWidget(Qt.QLabel(k),i,0,1,1)
        self._edits[k] = w
        self._widget.layout().addWidget(w,i,1,1,1)
      self.setWidget(self._widget)
        
    def accept(self):
      self.accepted = True
      for k,w in self._edits.items():
        v = str(w.text())
        self._model[k] = (self.cast or str)(v)
      QDialogWidget.accept(self)
        
    def getModel(self):
      return self._model
        
class QExceptionMessage(object):
    def __init__(self,*args):
        import traceback
        self.message = '\n'.join(map(str,args)) or ''
        if not self.message or len(args)<2:
            self.message+=traceback.format_exc()
        self.qmb = Qt.QMessageBox(Qt.QMessageBox.Warning,"Exception","The following exception occurred:\n\n%s"%self.message,Qt.QMessageBox.Ok)
        print 'fandango.qt.QExceptionMessage(%s)'%self.message
        self.qmb.exec_()

class QColorDictionary(SortedDict,Singleton):
    """
    Returns a {name:QColor} dictionary; 
    if sorted tries to sort by color difference
    """
    def __init__(self,sort = False):
        SortedDict.__init__(self)
        colors = {}
        last = SortedDict()
        for n in Qt.QColor.colorNames():
            c = Qt.QColor(n)
            rgb = c.getRgb()[:3]
            if not sum(rgb): last['black'] = c
            elif sum(rgb)==255*3: last['white'] = c
            elif not any(v.getRgb()[:3]==c.getRgb()[:3] for v in colors.values()):
                colors[n] = c
            else: last[n] = c
        if sorted:
            self.distances = {}
            dark = [(n,colors.pop(n)) for n in colors.keys() if max(colors[n].getRgb()[:3])<.25*(255*3)]
            light = [(n,colors.pop(n)) for n in colors.keys() if min(colors[n].getRgb()[:3])>.75*(255*3)]
            self.update(
                sorted(
                    ((n,colors.pop(n)) for n in colors.keys() if all(c in (0,255) for c in colors[n].getRgb()[:3])),
                    key=(lambda t:sum(t[1].getRgb()[:3]))
                    )
                )
            #self.update([(n,colors.pop(n)) for n in colors.keys() if all(c in colors[n].getRgb()[:3] for c in (0,255))])
            #for inc in range(0,255/2):
                #self.update([(n,colors.pop(n)) for n in colors.keys() if any(c in colors[n].getRgb() for c in (0+inc,255-inc))])
                #if not colors: break
            #for n,color in sorted(colors,key=lambda t: -self.get_diff_code(t[1])): self[n] = color
            x = len(colors)
            for i in range(x):
                n = sorted(colors.items(),key=lambda t: -self.get_diff_code(*t))[0][0]
                self[n] = colors.pop(n)
            self.update(light)
            self.update(dark)
            self.update(last)
        else:
            self.update(sorted(colors.items()))
            self.update(last)
    def show(self):
        getApplication()
        self.widget = Qt.QScrollArea()
        w = Qt.QWidget()
        w.setLayout(Qt.QVBoxLayout())
        for n,c in self.items():
            l = Qt.QLabel('%s: %s, %s'%(n,str(c.getRgb()[:3]),self.distances.get(n,None)))
            l.setStyleSheet('QLabel { background-color: rgba(%s) }'%(','.join(str(x) for x in c.getRgb())))
            w.layout().addWidget(l)
        self.widget.setWidget(w)
        self.widget.show()
    def get_rgb_normalized(self,color):
        rgb = color.getRgb()[:3]
        average = fandango.avg(rgb)
        return tuple((c-average) for c in rgb)
    def get_diff_code(self,name,color):
        #get_avg_diff = lambda seq: (abs(seq[0]-seq[1])+abs(seq[1]-seq[2])+abs(seq[2]-seq[0]))/3.
        #return get_avg_diff(color.getRgb())
        NValues = 15
        MinDiff = 50
        self.distances[name] = [sum((abs(x-y) if abs(x-y)>MinDiff else 0) 
            #for x,y in zip(self.get_rgb_normalized(color),self.get_rgb_normalized(k)))
            for x,y in zip(color.getRgb()[:3],k.getRgb()[:3]))  
                for k in self.values()[-NValues:]]
        return sum(self.distances[name]) if not any(d<MinDiff*1.5 for d in self.distances[name]) else 0
        

class QCustomPushButton(Qt.QPushButton):
    def __init__(self,label,widget=None,parent=None):
        Qt.QPushButton.__init__(self,parent)
        self._widget = widget
        self.label = Qt.QLabel(label)
        self.setLayout(Qt.QVBoxLayout())
        if widget: self.layout().addWidget(self._widget)
        self.layout().setAlignment(Qt.Qt.AlignCenter)
        self.layout().addWidget(self.label)
        self.connect(self,Qt.SIGNAL("pressed()"),lambda:self.setBold(True))
        self.connect(self,Qt.SIGNAL("released()"),lambda:self.setBold(False))
    def setLabel(self,label):
        self.label.setText(label)
    def setBold(self,bold):
        if bold:
            text = str(self.label.text()).replace('<b>','').replace('</b>','')
            self.label.setText('<b>%s</b>'%text)
        else:
            self.label.setText(str(self.label.text()).replace('<b>','').replace('</b>',''))
    def setWidget(self,widget):
        if self.widget: self.layout().removeWidget(self.widget)
        self._widget = widget
        self.layout().addWidget(self._widget)
    def getText(self):
        return self.label.text()
    pass

class QCustomTabWidget(Qt.QWidget):
    """
    A reimplementation of QTabWidget but using custom buttons to manage tabs
    """
    __pyqtSignals__ = ("currentChanged(int)",)
    def __init__(self,parent=None,icon_builder=None):
        Qt.QWidget.__init__(self,parent)
        self.setLayout(Qt.QVBoxLayout())
        self.buttonGroup = Qt.QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonFrame = Qt.QFrame(self)
        self.buttonFrame.setLayout(Qt.QHBoxLayout())
        self.buttonFrame.layout().setContentsMargins(0,0,0,0)
        self.buttonFrame.layout().setSpacing(1)
        self.stackWidget = Qt.QStackedWidget(self)
        self.layout().addWidget(self.buttonFrame)
        self.layout().addWidget(self.stackWidget)
        self.icon_builder = icon_builder
        self.widgets = {}
        self.buttons = {}
        self.rcount = 0
        self.connect(self.stackWidget,Qt.SIGNAL("currentChanged(int)"),self.emitCurrentChanged)

    def emitCurrentChanged(self):
        self.emit(Qt.SIGNAL("currentChanged(int)"),self.stackWidget.currentIndex())

    def addTab(self,widget,label,icon=None,width=50,height=60):
        print '-'*80
        print 'Adding %s tab to QCustomTabWidget(%d)'%(label,self.count())
        if label in self.buttons: 
            print ('======> Button(%s) already exists!,\n\t %s rejected!!'%(label,widget))
        else:
            if icon is None and self.icon_builder is not None: 
                try: icon = self.icon_builder(label)
                except: 
                    print 'Unable to get icon widget'
                    print traceback.format_exc()
            button = QCustomPushButton(label,icon,parent=self.buttonFrame)
            button.setCheckable(True)
            self.buttons[label] = button
            self.widgets[label] = widget
            if width and height: button.setMinimumSize(width,height)
            self.buttonGroup.addButton(button)
            self.buttonFrame.layout().addWidget(button)
            self.stackWidget.addWidget(widget)
            self.connect(button,Qt.SIGNAL("pressed()"),lambda w=widget,l=label:self.setCurrentWidget(w,l))
        
    def insertTab(self,index,page,label): return self.addTab(page,label)
    def insertTab(self,index,page,icon,label): return self.addTab(page,label,icon)
    def removeTab(self,index): 
        w = self.widget(index)
        label = self.labelOf(w)
        self.stackWidget.removeWidget(w)
        self.widgets.pop(label)
        button = self.buttons.pop(label)
        self.buttonGroup.removeButton(button)
        self.buttonFrame.layout().removeWidget(button)
        return label
    def clear(self): 
        while self.widgets():
            self.removeTab(0)
        
    def setCurrentIndex(self,index): 
        print 'In QCustomTabWidget.setCurrentIndex(%s)'%index
        button = self.buttonGroup.buttons()[index]
        if not button.check(): button.setChecked(True)
        return self.stackWidget.setCurrentIndex()
    
    def count(self): return self.stackWidget.count()
    def widget(self,index): 
        if isString(index): return self.widgets[index]
        else: return self.stackWidget.widget(index)
    def labelIndex(self,label):
        w = self.widget(label)
        return self.indexOf(w)
    def indexOf(self,widget): 
        if isString(widget): return self.labelIndex(widget)
        else: return self.stackWidget.indexOf(widget)
    def labelOf(self,widget):
        return (k for k,v in self.widgets.items() if v is widget).next()
    def currentIndex(self): return self.stackWidget.currentIndex()
    def setCurrentWidget(self,widget,label=''): 
        self.stackWidget.setCurrentWidget(widget)
        if (not label or label not in self.buttons):
            for l,w in self.widgets.items():
                if w==widget:
                    label = l
                    break
        if label: 
            self.buttons[label].setBold(True)
            self.buttons[label].setDown(True)
            for l,b in self.buttons.items():
                if l!=label:
                    #print 'In QCustomTabWidget.setCurrentWidget(%s): push down %s(%s)'%(label,b,l)
                    (b.setDown(False),b.setBold(False))
                else: (b.setDown(True),b.setBold(True))
    def currentWidget(self): return self.stackWidget.currentWidget()
    def tabBar(self): return self.buttonFrame
    def isTabEnabled(self,index): 
        print 'QCustomTabWidget.TabEnabled: Not implemented!'
        return True
    def setTabEnabled(self,index,enable): 
        print 'QCustomTabWidget.TabEnabled: Not implemented!'
        return
    def setTabShape(self,shape): 
        print 'QCustomTabWidget.TabShape: Not implemented!'
        return
    def tabShape(self):
        print 'QCustomTabWidget.TabShape: Not implemented!'
        return Qt.QTabWidget.Rounded
    def setTabPosition(self,position):
        print 'QCustomTabWidget.TabPosition: Not implemented!'
        return
    def tabPosition(self):
        print 'QCustomTabWidget.TabPosition: Not implemented!'
        return Qt.QTabWidget.North
    def setElideMode(self,elide):
        print 'QCustomTabWidget.ElideMode: Not implemented!'
        return
    def elideMode(self):
        print 'QCustomTabWidget.ElideMode: Not implemented!'
        return Qt.Qt.ElideNone
    def setUsesScrollButtons(self,uses):
        print 'QCustomTabWidget.UsesScrollButtons: Not implemented!'
        return
    def usesScrollButtons(self):
        print 'QCustomTabWidget.UsesScrollButtons: Not implemented!'
        return True
    def tabText(self,index): 
        print 'QCustomTabWidget.TabText: Not implemented!'
        return ''
    def tabToolTip(self,index): 
        print 'QCustomTabWidget.TabToolTip: Not implemented!'
        return ''
    def setTabToolTip(self,index,tip): 
        print 'QCustomTabWidget.TabToolTip: Not implemented!'
        return
        
#from taurus.qt.qtgui.display import TaurusStateLed
#qapp = Qt.QApplication([])
#qf = Qt.QFrame()
#qf.setLayout(Qt.QHBoxLayout())
#qbp = Qt.QButtonGroup()
#for i in range(16):
    #qpb = Qt.QPushButton()
    #qpb.setLayout(Qt.QVBoxLayout())
    #qbp.addButton(qpb)
    #tsl = TaurusStateLed()
    #tsl.setModel('sr%02d/vc/eps-plc-01/state'%(i+1))
    #qpb.layout().addWidget(tsl)
    #qpb.layout().addWidget(Qt.QLabel('SR%02d'%(i+1)))
    #qf.layout().addWidget(qpb)

#qbp.setExclusive(True)
#[qpb.setCheckable(True) for qpb in qbp.buttons()]
#l = qf.layout()
#l.setContentsMargins(0,0,0,0)
#l.setSpacing(1)
#[qpb.setMinimumSize(50,60) for qpb in qbp.buttons()]

#buttons = [b for b in qf.children() if is instance(b,Qt.QPushButton())

#-------------------------------------------------------------------------------

class TauFakeEventReceiver():
    def event_received(self,source,type_,value):
        print '%s: Event from %s: %s(%s)'% (time.ctime(),source,type_,shortstr(getattr(value,'value',value)))
        
class TaurusImportException(Exception):
    pass
        
try:
    import taurus.core,taurus.qt
    import taurus.qt.qtgui.util.tauruscolor as colors
    import taurus.qt.qtgui.base as taurusbase
    from taurus.qt.qtgui.base import TaurusBaseComponent
    from taurus.core import TaurusEventType,TaurusAttribute
    from taurus.qt.qtgui.graphic import TaurusGraphicsItem
    from taurus.qt.qtgui.container.tauruswidget import TaurusWidget
except:
    print 'Unable to import Taurus!'
    taurus,colors,taurusbase,tie = None,None,None,TaurusImportException
    TaurusBaseComponent,TaurusEventType,TaurusAttribute,TaurusGraphicsItem,TaurusWidget = tie,tie,tie,tie,tie

def getColorsForValue(value,palette = getattr(colors,'QT_DEVICE_STATE_PALETTE',None)):
    """ 
    Get QColor equivalent for a given Tango attribute value 
    It returns a Background,Foreground tuple
    """
    print 'In getColorsForValue(%s)'%value
    if value is None:
        return Qt.QColor(Qt.Qt.gray),Qt.QColor(Qt.Qt.black)
    elif hasattr(value,'value'): #isinstance(value,PyTango.DeviceAttribute):
        if value.type == PyTango.ArgType.DevState:
            bg_brush, fg_brush = colors.QT_DEVICE_STATE_PALETTE.qbrush(value.value)
        elif value.type == PyTango.ArgType.DevBoolean:
            bg_brush, fg_brush = colors.QT_DEVICE_STATE_PALETTE.qbrush((PyTango.DevState.FAULT,PyTango.DevState.ON)[value.value])
        else:
            bg_brush, fg_brush = colors.QT_ATTRIBUTE_QUALITY_PALETTE.qbrush(value.quality)
    else:
        bg_brush, fg_brush = palette.qbrush(int(value))
        
    return bg_brush.color(),fg_brush.color()

class TauColorComponent(TaurusBaseComponent):
    """
    Abstract class for Tau color-based items.
    
    :param: defaults will be a tuple with the default foreground,background colors (appliable if value not readable)
            It may allow to differentiate not-read from UNKNOWN
            
    The TauColorComponent contains a QObject to emit Qt.SIGNALs if needed:
        self.emitter.connect(self.emitter,Qt.SIGNAL("setColors"),self.parent.tabBar().setTabTextColor)
        self.emitter.emit(Qt.SIGNAL("setColors"),self.getIndex(),color)
    """
    
    def __init__(self, name = None, parent = None, defaults = None):
        self.__name = name
        self.call__init__(taurusbase.TaurusBaseComponent, name, parent)
        self.__value = None
        self._defBgColor = defaults and defaults[0] or Qt.QColor(Qt.Qt.gray)
        self._defFgColor = defaults and defaults[-1] or Qt.QColor(Qt.Qt.black)
        self._currBgColor,self._currFgColor = self._defBgColor,self._defFgColor
        self.emitter = Qt.QObject(parent)
        
    def setColors(self,background,foreground):
        raise Exception('Method should be overriden in %s subclass!'%type(self))
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory methods to be implemented in any subclass of TauComponent
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def setModel(self,model):
        print '#'*80
        self.info('In %s.setModel(%s)'%(type(self).__name__,model))
        model = str(model)
        self.__name = model
        #If the model is a device the color will depend of its State
        if model.count('/')==2: model += '/state'
        #We don't want the ._name to be overriden by ._name+/state            
        taurusbase.TaurusBaseComponent.setModel(self,model) 

    def getParentTauComponent(self):
        """ Returns a parent Tau component or None if no parent TaurusBaseComponent 
            is found."""
        p = self.parentItem()
        while p and not isinstance(p, TauGraphicsItem):
            p = self.parentItem()
        return p

    #def fireEvent(self, evt_src = None, evt_type = None, evt_value = None):
    def handleEvent(self, evt_src = None, evt_type = None, evt_value = None):
        """fires a value changed event to all listeners"""
        self.info('In TauColorComponent(%s).handleEvent(%s,%s)'%(self.__name,evt_src,evt_type))
        if evt_type!=TaurusEventType.Config: 
            #@todo ; added to bypass a problem with getModelValueObj()
            self.__value = evt_value if evt_type!=TaurusEventType.Error else None
            self.updateStyle()

    def updateStyle(self):
        """ Method called when the component detects an event that triggers a change
            in the style.
            If the value is not parseable the default colors will be set.
        """
        try:
            self._currBgColor,self._currFgColor = self._defBgColor,self._defFgColor
            #@todo ; added to bypass a problem with getModelValueObj()
            value = self.__value #self.getModelValueObj()
            if value is not None:
                value = value.value
                self.info('In TauColorComponent(%s).updateStyle(%s)'%(self.__name,value))
                self._currBgColor,self._currFgColor = getColorsForValue(value)
            else:
                self.info('In TauColorComponent(%s).updateStyle(%s), using defaults'%(self.__name,value))
        except: 
                self.info('TauColorComponent(%s).updateStyle(): Unable to getColorsForValue(%s):\n%s'%(self.__name,value,traceback.format_exc()))
        self.setColors(self._currBgColor,self._currFgColor)
        return

    def isReadOnly(self):
        return True

    def __str__(self):
        return self.log_name + "(" + self.modelName + ")"

    def getModelClass(self):
        return TaurusAttribute

class QSignalHook(Qt.QObject):
    """
    Class initialized with a transformation function.
    For every setModel(model) it will emit a modelChanged(function(model))
    """
    __pyqtSignals__ = ("modelChanged",)
    def __init__(self,function):
        Qt.QObject.__init__(self)
        self._model = None
        self._new_model = None
        self.function = function
        
    def setModel(self,model):
        self._model = model
        self._new_model = self.function(model) if self.function is not None else model
        self.emit(Qt.SIGNAL("modelChanged"), self._new_model)

class NullWidget(TaurusWidget):
    def __init__(self,*args):
        TaurusWidget.__init__(self,*args)
        self.setVisible(False)

    def show(self):
        self.hide()

    def Input(self,value):
        print 'In NullWidget.setInput(%s)'%value
        self.emit(Qt.SIGNAL('Output'), value or 'sys/database/2')

import threading

class ModelRefresher(threading.Thread,fandango.objects.SingletonMap):

  def __init__(self,period=30):
    threading.Thread.__init__(self)
    self.period = period
    self.targets = []
    self.stop_event = threading.Event()
    print('ModelRefresher.init()')
    
  def run(self):
    while not self.stop_event.isSet():
      self.targets = self.get_targets()
      for t in self.targets:
        self.fire_targets([t])
        self.stop_event.wait(float(self.period)/len(self.targets))
        if self.stop_event.isSet(): break
    print('Model Refresh finished')
    
  def stop(self):
    self.stop_event.set()
    self.join()
    
  def get_targets(self,widgets=[]):
    print('ModelRefresher.getTargets()')
    widgets = widgets or getApplication().allWidgets()
    targets = []
    for w in widgets:
      try:
        if hasattr(w,'getModelObj') and w.getModelObj():
            targets.append(w)
      except:
        pass
      try:
        if hasattr(w,'getCurveNames'):
          for ts in w.getCurveNames():
            ts = w.getCurve(ts)
            if ts.getModelObj():
              targets.append(ts)
        if hasattr(w,'getTrendSetNames'):
          for ts in w.getTrendSetNames():
            ts = w.getTrendSet(ts)
            if ts.getModelObj():
              targets.append(ts)
      except:
        print w,w.getModel()
        traceback.print_exc()
    self.targets = targets
    return targets
    
  def fire_targets(self,targets=[]):
    targets = targets or self.targets
    for ts in targets:
      try:
        ts.fireEvent(ts,taurus.core.TaurusEventType.Change,ts.getModelValueObj(cache=False))
      except:
        print ts
        traceback.print_exc()
    return

#############################################################################################
## DO NOT EDIT THIS CLASS HERE, THE ORIGINAL ONE IS IN taurus utils emitter!!!
#############################################################################################

def modelSetter(obj,model):
    if hasattr(obj,'setModel') and model:
        obj.setModel(model)
    return
        
class QWorker(Qt.QThread):
    """
    IF YOU USE TAURUS, GO THERE INSTEAD: taurus.qt.qtcore.util.emitter.SingletonWorker ; it is more optimized and maintained
    
    This object get items from a python Queue and performs a thread safe operation on them.
    It is useful to delay signals in a background thread.
    :param parent: a Qt/Tau object
    :param name: identifies object logs
    :param queue: if None parent.getQueue() is used, if not then the queue passed as argument is used
    :param method: the method to be executed using each queue item as argument
    :param cursor: if True or QCursor a custom cursor is set while the Queue is not empty
    
    USAGE
    -----
    
    Delaying model subscription using TauEmitterThread[edit]::
    
        <pre>
        #Applying TauEmitterThread to an existing class:
        import Queue
        from functools import partial
        
        def modelSetter(args):
            obj,model = args[0],args[1]
            obj.setModel(model)
        
        klass TauGrid(Qt.QFrame, TaurusBaseWidget):
            ...
            def __init__(self, parent = None, designMode = False):
                ...
                self.modelsQueue = Queue.Queue()
                self.modelsThread = TauEmitterThread(parent=self,queue=self.modelsQueue,method=modelSetter )
                ...
            def build_widgets(...):
                ...
                            previous,synoptic_value = synoptic_value,TauValue(cell_frame)
                            #synoptic_value.setModel(model)
                            self.modelsQueue.put((synoptic_value,model))
                ...
            def setModel(self,model):
                ...
                if hasattr(self,'modelsThread') and not self.modelsThread.isRunning(): 
                    self.modelsThread.start()
                elif self.modelsQueue.qsize():
                    self.modelsThread.next()
                ...    
        </pre>
    """
    def __init__(self, parent=None,name='',queue=None,method=None,cursor=None,sleep=5000):
        """
        Parent most not be None and must be a TauGraphicsScene!
        """
        Qt.QThread.__init__(self, parent)
        self.name = name
        self.log = Logger('TauEmitterThread(%s)'%self.name)
        self.log.setLogLevel(self.log.Info)
        self.queue = queue or Queue.Queue()
        self.todo = Queue.Queue()
        self.method = method
        self.cursor = Qt.QCursor(Qt.Qt.WaitCursor) if cursor is True else cursor
        self._cursor = False
        self.sleep = sleep
        
        self.emitter = Qt.QObject()
        self.emitter.moveToThread(Qt.QApplication.instance().thread())
        self.emitter.setParent(Qt.QApplication.instance()) #Mandatory!!! if parent is set before changing thread it could lead to segFaults!
        self._done = 0
        #Moved to the end to prevent segfaults ...
        Qt.QObject.connect(self.emitter, Qt.SIGNAL("doSomething"), self._doSomething)
        Qt.QObject.connect(self.emitter, Qt.SIGNAL("somethingDone"), self.next)
        
    def getQueue(self):
        if self.queue: return self.queue
        elif hasattr(self.parent(),'getQueue'): self.parent().getQueue()
        else: return None

    def getDone(self):
        """ Returns % of done tasks in 0-1 range """
        return float(self._done)/(self._done+self.getQueue().qsize()) if self._done else 0.

    def _doSomething(self,args):
        self.log.debug('At TauEmitterThread._doSomething(%s)'%str(args))
        if not self.method: 
            if isSequence(args): method,args = args[0],args[1:]
            else: method,args = args,[]
        else: 
            method = self.method
        if method:
            try:
                method(*args)
            except:
                self.log.error('At TauEmitterThread._doSomething(): %s' % traceback.format_exc())
        self.emitter.emit(Qt.SIGNAL("somethingDone"))
        self._done += 1
        return
    
    def put(self,*args):
        """
        QWorker.put(callable,arg0,arg1,arg2,...)
        """
        if len(args)==1 and isSequence(args[0]): args = args[0]
        self.getQueue().put(args)
                
    def next(self):
        queue = self.getQueue()
        (queue.empty() and self.log.info or self.log.debug)('At TauEmitterThread.next(), %d items remaining.' % queue.qsize())
        try:
            if not queue.empty():
                if not self._cursor and self.cursor is not None: 
                    Qt.QApplication.instance().setOverrideCursor(Qt.QCursor(self.cursor))
                    self._cursor=True                
                item = queue.get(False) #A blocking get here would hang the GUIs!!!
                self.todo.put(item)
                self.log.debug('Item added to todo queue: %s' % str(item))
            else:
                self._done = 0.
                if self._cursor: 
                    Qt.QApplication.instance().restoreOverrideCursor()
                    self._cursor = False        
                
        except Queue.Empty,e:
            self.log.warning(traceback.format_exc())
            pass
        except: 
            self.log.warning(traceback.format_exc())
        return
        
    def run(self):
        Qt.QApplication.instance().thread().wait(self.sleep)
        print '#'*80
        self.log.info('At TauEmitterThread.run()')
        self.next()
        while True:
            item = self.todo.get(True)
            if isString(item):
                if item == "exit":
                    break
                else:
                    continue
            self.log.debug('Emitting doSomething signal ...')
            self.emitter.emit(Qt.SIGNAL("doSomething"), item)
            #End of while
        self.log.info('#'*80+'\nOut of TauEmitterThread.run()'+'\n'+'#'*80)
        #End of Thread 
        
TauEmitterThread = QWorker #For backwards compatibility
            
###############################################################################

###############################################################################
# QT Helping Classes
TEXT_MIME_TYPE = 'text/plain'
try:
  import taurus, taurus.qt, taurus.qt.qtcore
  from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, TAURUS_MODEL_LIST_MIME_TYPE
except: 
  print('WARNING: fandango.qt: Importing taurus.qt.qtcore.mimetypes failed!')
  TAURUS_ATTR_MIME_TYPE = TAURUS_DEV_MIME_TYPE = TAURUS_MODEL_MIME_TYPE = TAURUS_MODEL_LIST_MIME_TYPE = TEXT_MIME_TYPE

@ClassDecorator
def Dropable(QtKlass):
    """ 
    This decorator enables any Qt class to accept drops
    """    
    class DropableQtKlass(QtKlass): #,Decorated):
    
        def checkDropSupport(self): 
            ''' Initializes DropEvent support '''
            try: 
                self.setAcceptDrops(True)
                if not hasattr(self,'TAURUS_DEV_MIME_TYPE'):
                    self.TAURUS_DEV_MIME_TYPE = TAURUS_DEV_MIME_TYPE
                    self.TAURUS_ATTR_MIME_TYPE = TAURUS_ATTR_MIME_TYPE
                    self.TAURUS_MODEL_MIME_TYPE = TAURUS_MODEL_MIME_TYPE
                    self.TAURUS_MODEL_LIST_MIME_TYPE = TAURUS_MODEL_LIST_MIME_TYPE
            except: traceback.print_exc()
            self.TEXT_MIME_TYPE = 'text/plain'
            return True

        def getSupportedMimeTypes(self): 
            '''
            :param mimetypes: (list<str>) list (ordered by priority) of MIME type names or a {mimeType: callback} dictionary (w/out priority if not using SortedDict)
            '''
            self.checkDropSupport()
            if not getattr(self,'_supportedMimeTypes',[]):
                try: 
                    self.setSupportedMimeTypes([self.TAURUS_DEV_MIME_TYPE, self.TAURUS_ATTR_MIME_TYPE,self.TAURUS_MODEL_MIME_TYPE, self.TAURUS_MODEL_LIST_MIME_TYPE, self.TEXT_MIME_TYPE])
                except:
                    print 'Unable to import TAURUS MIME TYPES: %s'%traceback.format_exc()
                    self.setSupportedMimeTypes([self.TEXT_MIME_TYPE])
            return self._supportedMimeTypes
        
        def setSupportedMimeTypes(self, mimetypes):
            ''' sets the mimeTypes that this widget support 
            :param mimetypes: (list<str>) list (ordered by priority) of MIME type names or a {mimeType: callback} dictionary (w/out priority if not using SortedDict)
            '''
            print 'In setSupportedMimeTypes()'
            self.checkDropSupport()
            self._supportedMimeTypes = mimetypes

        def setDropEventCallback(self,callback):
            ''' Assings default DropEventCallback '''
            self._dropeventcallback = callback
            
        def getDropEventCallback(self,mimetype = None):
            try:
                mimes = self.getSupportedMimeTypes()
                if mimetype and fandango.isMapping(mimes):
                    return mimes.get(mimetype)
            except: traceback.print_exc()
            return getattr(self,'_dropeventcallback',None) or getattr(self,'setText',None)
        
        # ENABLING DROP OF DEVICE NAMES :
        def checkSupportedMimeType(self,event,accept=False): 
            for t in self.getSupportedMimeTypes():
                if t in event.mimeData().formats():
                    if accept: event.acceptProposedAction()
                    return self.getDropEventCallback(t) or True
            return False
        
        def dragEnterEvent(self,event): self.checkSupportedMimeType(event,accept=True)
        def dragMoveEvent(self,event): event.acceptProposedAction()
                
        def dropEvent(self, event):
            '''reimplemented to support drag&drop of models. See :class:`QWidget`'''
            print('dropEvent(%s): %s,%s'%(event,event.mimeData(),event.mimeData().formats()))
            if event.source() is self:
                print('Internal drag/drop not allowed')
            mtype = self.handleMimeData(event.mimeData())
            event.acceptProposedAction()
            
        def handleMimeData(self, mimeData, method=None):
            '''Selects the most appropriate data from the given mimeData object (in the order returned by :meth:`getSupportedMimeTypes`) and passes it to the given method.
            :param mimeData: (QMimeData) the MIME data object from which the model is to be extracted
            :param method: (callable<str>) a method that accepts a string as argument. This method will be called with the data from the mimeData object
            :return: (str or None) returns the MimeType used if the model was successfully set, or None if the model could not be set
            '''
            for mtype in self.getSupportedMimeTypes():
                try:
                    data = str(mimeData.data(mtype) or '')
                    try:
                        if data.strip():
                            try:
                                (method or self.getDropEventCallback(mtype))(data)
                                return mtype
                            except:
                                print('Invalid data (%s,%s) for MIMETYPE=%s'%(repr(mimeData),repr(data), repr(mtype)))
                                traceback.print_exc()
                                return None
                    except: self.info(traceback.warning_exc())
                except: self.debug('\tNot dropable data (%s)'%(data))
    return DropableQtKlass

QDropable = Dropable(object)

@ClassDecorator
def DoubleClickable(QtKlass):
    """ 
    This decorator enables a Qt class to execute a 'hook' method every time is double-clicked
    """    
    class DoubleClickableQtKlass(QtKlass): #,Decorated):
        __doc__ = DoubleClickable.__doc__
        def __init__(self,*args):
            self.my_hook = None
            QtKlass.__init__(self,*args)
        def setClickHook(self,hook):
            """ the hook must be a function or callable """
            self._doubleclickhook = hook #self.onEdit
        def mouseDoubleClickEvent(self,event):
            if getattr(self,'_doubleclickhook',None) is not None:
                self._doubleclickhook()
            else:
                try: QtKlass.mouseDoubleClickEvent(self)
                except: pass
    return DoubleClickableQtKlass

QDoubleClickable = DoubleClickable(object)

@ClassDecorator
def Draggable(QtKlass):
    """
    This ClassDecorator enables Drag on widgets that does not support it.
    BUT!, it will fail on those that already implement it (e.g. QTextEdit)
    """
    
    class DraggableQtKlass(QtKlass): #,Decorated):
        __doc__ = Draggable.__doc__
        
        def setDragEventCallback(self,hook,Mimetype=None):
            self._drageventcallback = hook
            self.Mimetype = Mimetype 

        def getDragEventCallback(self):
            if not getattr(self,'_drageventcallback',None):
                self.setDragEventCallback(lambda s=self:str(s.text() if hasattr(s,'text') else ''))
            return self._drageventcallback
        
        def mousePressEvent(self, event):
            '''reimplemented to provide drag events'''
            #QtKlass.mousePressEvent(self, event)
            QtKlass.mousePressEvent(self,event)
            print 'In Draggable(%s).mousePressEvent'%type(self)
            if event.button() == Qt.Qt.LeftButton: self.dragStartPosition = event.pos()
                
        def mouseMoveEvent(self, event):
            '''reimplemented to provide drag events'''
            QtKlass.mouseMoveEvent(self,event)
            if not event.buttons() & Qt.Qt.LeftButton:
                return
            call_back = self.getDragEventCallback()
            mimeData = call_back()
            if not isinstance(mimeData,Qt.QMimeData):
                txt = str(mimeData)
                mimeData = Qt.QMimeData()
                if getattr(self,'Mimetype',None):
                    mimeData.setData(self.Mimetype, txt)
                mimeData.setText(txt) #Order is not trivial, preferred must go first
            drag = Qt.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(event.pos() - self.rect().topLeft())
            dropAction = drag.start(Qt.Qt.CopyAction)
    return DraggableQtKlass

QDraggable = Draggable(object)
QDraggableLabel = Draggable(Qt.QLabel)

@ClassDecorator
def MenuContexted(QtKlass):
    """ 
    This class decorator provides a simple hook to add context menu options/callables 
    
    Example:
      label = MenuContexted(Qt.QLabel)('a/device/name')
      label.setContextCallbacks({'Test Device',lambda:show_device_panel('a/device/name')})
      
    """
    class MenuContextedQtKlass(QtKlass):
        __doc__ = MenuContexted.__doc__
        
        def setContextCallbacks(self,hook_dict):
            self._actions = hook_dict
        
        def mousePressEvent(self, event):
            point = event.pos()
            widget = Qt.QApplication.instance().widgetAt(self.mapToGlobal(point))
            # If the widget is a container:
            if hasattr(widget,'_actions'):
                #print('onMouseEvent(%s)'%(getattr(widget,'text',lambda:widget)()))
                self._current_item = widget
                if event.button()==Qt.Qt.RightButton:
                    self.onContextMenu(point)
            elif hasattr(self,'_actions'):
                self.onContextMenu()
            getattr(super(type(self),self),'mousePressEvent',lambda e:None)(event)
            
        def getContextItem(self):
            return getattr(self,'_current_item',None)
            
        def onContextMenu(self, point=None):
            try:
                self._contextmenu = Qt.QMenu()
                for k,v in self._actions.items():
                  self._contextmenu.addAction(Qt.QIcon(),k,v)
                if point:
                    self._contextmenu.exec_(self.mapToGlobal(point))
                else:
                   self._contextmenu.exec_()
            except:
                traceback.print_exc()

    return MenuContextedQtKlass

#class QDraggableLabel(!Draggable,Qt.QLabel):
    #def __init__(self,parent=None,text=''):
        #Qt.QLabel.__init__(self,text)
        #Draggable.__init__(self)
                
class QOptionChooser(Qt.QDialog):
    """ 
    Dialog used to trigger several options from a bash launch script
    """
    def __init__(self,title,text,command,args,parent=None):
        Qt.QDialog.__init__(self,parent)
        self.command = command
        self.args = args
        self.combo = Qt.QComboBox()
        self.combo.addItems(self.args)
        self.buttons = Qt.QDialogButtonBox(Qt.QDialogButtonBox.Ok|Qt.QDialogButtonBox.Cancel)
        self.connect(self.buttons,Qt.SIGNAL('accepted()'),self.launch)
        self.connect(self.buttons,Qt.SIGNAL('rejected()'),self.close)
    
        self.setLayout(Qt.QHBoxLayout())
        self.setWindowTitle(title)
        self.layout().addWidget(Qt.QLabel(text))
        self.layout().addWidget(self.combo)
        self.layout().addWidget(self.buttons)

    def launch(self):
        cmd = ' '.join(map(str,[self.command[0],self.combo.currentText()]+self.command[1:]))+' &'
        print cmd
        import os
        os.system(cmd)

class TangoHostChooser(Qt.QDialog):
    """
    Allows to choose a tango_host from a list
    """
    def __init__(self,hosts):
        self.hosts = sorted(hosts)
        Qt.QDialog.__init__(self,None)
        self.setLayout(Qt.QVBoxLayout())
        self.layout().addWidget(Qt.QLabel('Choose your TangoHost:'))
        self.chooser = Qt.QComboBox()
        self.chooser.addItems(self.hosts)
        self.layout().addWidget(self.chooser)
        self.button = Qt.QPushButton('Done')
        self.layout().addWidget(self.button)
        self.button.connect(self.button,Qt.SIGNAL('pressed()'),self.done)
        self.button.connect(self.button,Qt.SIGNAL('pressed()'),self.close)
    def done(self,*args):
        import os
        os.environ['TANGO_HOST']=str(self.chooser.currentText())
        new_value = os.getenv('TANGO_HOST')
        self.close()
        self.hide()
        
    @staticmethod
    def main(args=[]):
        app = getApplication()
        thc = TangoHostChooser(args or sys.argv[1:])
        thc.show()
        app.exec_()
        v = str(thc.chooser.currentText())
        print(v)
        return v
    
###############################################################################

class DialogCloser(object):
    """
    This decorator triggers dialog closure at the end of the decorated method
    e.g.
    dialog = QTextBuffer()
    widget = TaurusTrend()
    
    TaurusTrend.closeEvent = DialogCloser(d)
    """
    def __init__(self,dialog):
        self.dialog = dialog
    def __call__(self,f):
        def wrapped_closeEvent(*args):
            f(*args)
            try: self.dialog.close()
            except:pass
        return wrapped_closeEvent

def setDialogCloser(dialog,widget):
    """
    set dialog to be closed on widget.closeEvent()
    """
    widget.closeEvent = DialogCloser(dialog)(widget.closeEvent)
    widget.hideEvent = DialogCloser(dialog)(widget.hideEvent)
    
    
def QConfirmAction(action,parent=None,title='WARNING',message='Are you sure?',options=Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel):
    """
    This method will just execute action but preceeded by a confirmation dialog.
    To pass arguments to your action just use partial(action,*args,**kwargs) when declaring it
    e.g:
        self._clearbutton.connect(self._clearbutton,Qt.SIGNAL('clicked()'),fandango.partial(fandango.qt.QConfirmAction,self.clearBuffers)
    """
    if Qt.QMessageBox.Ok == QtGui.QMessageBox.warning(parent,title,message,QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel):
        action()

class QTextBuffer(Qt.QDialog):
    """
    This dialog provides a Text dialog where logs can be inserted from your application in a round buffer.
    It also provides a button to save the logs into a file if needed.
    """
    def __init__(self,title='TextBuffer',maxlen=1000,parent=None):
        Qt.QDialog.__init__(self,parent) #,*args)
        self.setWindowTitle(title)
        lwidget,lcheck = Qt.QVBoxLayout(),Qt.QHBoxLayout()
        self.setLayout(lwidget)
        self._maxlen = maxlen
        self._buffer = [] #collections.deque could be used instead
        self._count = Qt.QLabel('0/%d'%maxlen)
        lwidget.addWidget(self._count)
        self._browser = Qt.QTextBrowser()
        lwidget.addWidget(self._browser)
        self._cb = Qt.QCheckBox('Dont popup logs anymore')
        self._checked = False
        #self._label = Qt.QLabel('Dont popup logs anymore')
        #self._label.setAlignment(Qt.Qt.AlignLeft)
        map(lcheck.addWidget,(self._cb,)) #self._label))
        lwidget.addLayout(lcheck)
        self.connect(self._cb,Qt.SIGNAL('toggled(bool)'),self.toggle)
        self._savebutton = Qt.QPushButton('Save Logs to File')
        self._savebutton.connect(self._savebutton,Qt.SIGNAL('clicked()'),self.saveLogs)
        self.layout().addWidget(self._savebutton)
        
    def append(self,text):
        if self._buffer and text==self._buffer[-1]: test = '+1'
        self._buffer.append(text)
        if len(self._buffer)>=1.2*self._maxlen:
            self._buffer = self._buffer[-self._maxlen:]
            self._browser.setText('\n'.join(self._buffer))
        else:
            self._browser.append(text)
        self._count.setText('%d/%d'%(min((self._maxlen,len(self._buffer))),self._maxlen))
        if not self._checked:
            self.show()
    def text(self):
        return self._browser.toPlainText()
    def setText(self,text):
        self._buffer = text.split('\n')
        self._browser.setText(text)
    def clear(self):
        self._browser.clear()
        self._buffer = []
    def toggle(self,arg=None):
        if arg is None:
            self._checked = self._cb.isChecked()
        elif arg:
            self._cb.setChecked(True)
            self._checked = True
        else:
            self._cb.setChecked(False)
            self._checked = False
        #print 'toggled(%s): %s'%(arg,self._checked)
        #sys.stdout.flush()
    def saveLogs(self):
        fname = str(Qt.QFileDialog.getSaveFileName(None,'Choose a file to save'))
        #self.info('Saving logs to %s'%fname)
        if fname: open(fname,'w').write(str(self.text()))
    

class QDropTextEdit(Qt.QTextEdit):
    """
    This method provides a widget that allows drops of text from other widgets.
    As a bonus, it provides a simple hook for DoubleClick events
    But!, QTextEdit already supported drag/drop, so it is just an exercise of how to do these things.
    """
    def __init__(self,*args):#,**kwargs):
        self.double_click_hook = None
        QtGui.QTextEdit.__init__(self,*args)#,**kwargs)
        self.mimeTypes() #Default mimeTypes loaded
    
    def setClickHook(self,hook):
        """ the hook must be a function or callable """
        self.double_click_hook = hook #self.onEdit
    
    def mouseDoubleClickEvent(self,event):
        if self.double_click_hook is not None:
            self.double_click_hook()
        else:
            try: Qt.QTextEdit.mouseDoubleClickEvent(self)
            except: pass

    def setSupportedMimeTypes(self, mimetypes):
        '''
        sets the mimeTypes that this widget support 
        
        :param mimetypes: (list<str>) list (ordered by priority) of MIME type names
        '''
        self._supportedMimeTypes = mimetypes
        
    def mimeTypes(self):
        try: 
            import taurus
            import taurus.qt
            import taurus.qt.qtcore
            from taurus.qt.qtcore.mimetypes import TAURUS_ATTR_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_MODEL_MIME_TYPE, TAURUS_MODEL_LIST_MIME_TYPE
            self.setSupportedMimeTypes([
                TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_DEV_MIME_TYPE, TAURUS_ATTR_MIME_TYPE,
                TAURUS_MODEL_MIME_TYPE, 'text/plain'])
        except:
            import traceback
            print traceback.format_exc()
            print 'Unable to import TAURUS MIME TYPES'
        return self.getSupportedMimeTypes()
        
    def getSupportedMimeTypes(self): 
        return self._supportedMimeTypes

    def addModels(self,models):
        self.setText(str(self.toPlainText())+'\n'+str(models))

    #In this method is where dropped data is checked
    def dropEvent(self, event):
        '''reimplemented to support dropping of modelnames in forms'''
        print('dropEvent(%s): %s,%s'%(event,event.mimeData(),event.mimeData().formats()))
        if event.source() is self:
            print('Internal drag/drop not allowed')
            return
        if any(s in event.mimeData().formats() for s in self.mimeTypes()):
            mtype = self.handleMimeData(event.mimeData(),self.addModels)#lambda m:self.addModels('^%s$'%m))
            event.acceptProposedAction()
        else:
            print('Invalid model in dropped data')

    def handleMimeData(self, mimeData, method):
        '''Selects the most appropriate data from the given mimeData object
        (in the order returned by :meth:`getSupportedMimeTypes`) and passes 
        it to the given method.
        
        :param mimeData: (QMimeData) the MIME data object from which the model
                         is to be extracted
        :param method: (callable<str>) a method that accepts a string as argument. 
                       This method will be called with the data from the mimeData object
        
        :return: (str or None) returns the MimeType used if the model was
                 successfully set, or None if the model could not be set
        '''
        print('QDropTextEdit.handleMimeData(%s,%s)'%(mimeData,method))
        supported = self.mimeTypes()
        print map(str,supported)
        formats = mimeData.formats()
        print map(str,formats)
        for mtype in supported:
            if mtype in formats:
                d = str(mimeData.data(mtype))
                if d is None: 
                    return None
                try:
                    method(d)
                    return mtype
                except:
                    print('Invalid data (%s) for MIMETYPE=%s'%(repr(d), repr(mtype)))
                    #self.traceback(taurus.Debug)
                    return None


class QGridTable(Qt.QFrame):#Qt.QFrame):
    """
    This class is a frame with a QGridLayout that emulates some methods of QTableWidget
    """
    def __init__(self,parent=None):
        Qt.QFrame.__init__(self,parent)
        self.setLayout(Qt.QGridLayout())
        self._widgets = []
    def setHorizontalHeaderLabels(self,labels):
        print 'QGridTable.setHorizontalHeaderLabels(%s)'%labels
        for i,l in enumerate(labels):
            ql = Qt.QLabel(l)
            f = ql.font()
            f.setBold(True)
            ql.setFont(f)
            ql.setAlignment(Qt.Qt.AlignCenter)
            self.setCellWidget(0,i,ql)
            if ql not in self._widgets: self._widgets.append(ql)
    def setVerticalHeaderLabels(self,labels):
        print 'QGridTable.setVerticalHeaderLabels(%s)'%labels
        for i,l in enumerate(labels):
            ql = Qt.QLabel(l)
            f = ql.font()
            f.setBold(True)
            ql.setFont(f)
            ql.setAlignment(Qt.Qt.AlignCenter)
            self.setCellWidget(i,0,ql)
            if ql not in self._widgets: self._widgets.append(ql)
    def rowCount(self):
        return self.layout().rowCount()
    def setRowCount(self,count):
        return None
    def columnCount(self):
        return self.layout().columnCount()
    def setColumnCount(self,count):
        None
    def itemAt(self,x,y):
        return self.layout().itemAtPosition(x,y)
    def setItem(self,x,y,item,spanx=1,spany=1):
        #print 'QGridTable.setItem(%s,%s,%s)'%(x,y,item)
        self.layout().addWidget(item,x,y,spanx,spany)
        if item not in self._widgets: self._widgets.append(item)
    def setCellWidget(self,*args):
        self.setItem(*args)
    def resizeColumnsToContents(self): 
        return None
    def resizeRowsToContents(self): 
        return None
    def setRowHeight(self,row,height):
        self.layout().setRowMinimumHeight(row,height)
    def setColumnWidth(self,col,width):
        self.layout().setColumnMinimumWidth(col,width)
    def clear(self):
        def deleteItems(layout):
          if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    deleteItems(item.layout())
        deleteItems(self.layout())
        #l = self.layout()
        #l.deleteLater()
        #self.setLayout(Qt.QGridLayout())
        self._widgets = []
    def removeWidget(self,widget):
        self.layout().removeWidget(widget)
        if widget in self._widgets: self._widgets.remove(widget)
        
###############################################################################

class QDictToolBar(Qt.QToolBar):
    """
    Just a customizable toolbar that can be setup using a dictionary:
        toolbar = QDictToolBar(tmw)
        toolbar.set_toolbar([('Archiving Viewer','Mambo-icon.ico', lambda:launch('mambo')),])
    """
    def __init__(self,parent=None):
        Qt.QToolBar.__init__(self,parent)
        self.setup_ui()
    def setup_ui(self):
        self.setWindowModality(Qt.Qt.NonModal)
        sizePolicy = Qt.QSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())        
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(Qt.QSize(0,0))     
        font = Qt.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.setFont(font)
        self.setMouseTracking(False)
        self.setContextMenuPolicy(Qt.Qt.ActionsContextMenu)
        self.setAutoFillBackground(True)
        self.setMovable(False)
        self.setAllowedAreas(Qt.Qt.AllToolBarAreas)
        self.setIconSize(Qt.QSize(40,30))
        self.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)
        #self.setPalette(get_halfWhite_palette())
    def build_action(self,name,icon,action):
        qaction = Qt.QAction(self)
        if name: qaction.setText(name) 
        if icon: 
            qpixmap = Qt.QPixmap(icon).scaled(35,30)
            qaction.setIcon(Qt.QIcon(qpixmap))
        #qaction.setShortcut(QtGui.QApplication.translate("SynopticTree", "Ctrl+J", None, QtGui.QApplication.UnicodeUTF8))                    
        #qaction.setMenuRole(QtGui.QAction.TextHeuristicRole)
        if action: Qt.QObject.connect(qaction,Qt.SIGNAL("triggered()"),action)
        return qaction
    def set_toolbar(self,toolbar):
        """ The toolbar argument must be dictionary {name:(icon,action)} or a list of ('Name','icon.jpg',action) tuples.
        """        
        if hasattr(toolbar,'items'): toolbar = [(k,v[0],v[1]) for k,v in toolbar.items()]
        for name,icon,action in toolbar:
            print 'Adding action to toolbar: %s,%s,%s'%(name,icon,action)
            if isSequence(action):
                #Building a sub menu
                print '\tAdding SubMenu: %s'%action
                qaction = Qt.QPushButton(name)
                qaction.setLayout(Qt.QVBoxLayout())
                if icon: 
                    pixmap = Qt.QPixmap(icon).scaled(40,30)
                    qaction.setIcon(Qt.QIcon(pixmap))
                    qaction.setIconSize(Qt.QSize(40,30))
                menu = Qt.QMenu()
                [menu.addAction(self.build_action(n,i,a)) for n,i,a in action]
                qaction.setMenu(menu)
                self.addWidget(qaction)
            elif (name or icon or action):
                self.addAction(self.build_action(name,icon,action))
            else:
                self.addSeparator()
        self.setObjectName("ToolBar")
        print 'Out of set_toolbar()'
        return self
    def add_to_main_window(self,MainWindow,where=Qt.Qt.TopToolBarArea):
        try: MainWindow.addToolBar(where,self)
        except: 
            print('Unable to add toolbar to MainWindow(%s)'%MainWindow)
            print traceback.format_exc()
            
class QDictTextBrowser(Qt.QWidget):

    """
    Easy widget, it just shows a dictionary in a text shape
    """
    
    def __init__(self,parent=None):
        Qt.QWidget.__init__(self,parent)
        self.model = {}
        self.setupUi()
        
    def setupUi(self):
        self.top = Qt.QListWidget()
        try:
          self.top.itemClicked.connect(self.updateText)
        except:
          self.top.connect(self.top,Qt.SIGNAL('itemClicked(item)'),self.updateText)
        self.bottom = Qt.QTextBrowser()
        self.setLayout(Qt.QVBoxLayout())
        map(self.layout().addWidget,(self.top,self.bottom))
        
    def setModel(self,model):
        self.model = model
        self.top.clear()
        for k in sorted(self.model.keys()):
            self.top.addItem(k)
        self.top.setMinimumHeight(125)
        self.top.setMaximumHeight(max((125,len(self.model)*25)))
    
    def updateText(self,item):
        txt = self.model.get(str(item.text()))
        txt = str(txt).replace('\t','    ')
        self.emit(Qt.SIGNAL('textChanged'),txt)
        self.bottom.setHtml('<pre>%s</pre>'%txt)
    
    @staticmethod
    def test():
        app = getApplication()
        w = QDictTextBrowser()
        w.setModel({'1':'na\na'*100,'2':'no\nsi'})
        w.show()
        app.exec_()
    
def GetFramedTaurusValue(model=None,label=True,hook=None):

    from taurus.qt.qtgui.panel import TaurusValue
    frame = QtGui.QFrame()
    frame.setLayout(QtGui.QGridLayout())
    frame.layout().setContentsMargins(2,2,2,2)
    frame.layout().setSpacing(0)
    frame.layout().setSpacing(0)
    frame.taurusvalue = TaurusValue(frame)
    if hook:
        frame.taurusvalue.connect(frame.taurusvalue, QtCore.SIGNAL("itemClicked(QString)"), hook)
    if label:
        frame.taurusvalue.setLabelConfig('label') ## DO NOT DELETE THIS LINE!!!
    else:
        frame.taurusvalue.setLabelWidgetClass(None)
    if model:
        frame.taurusvalue.setModel(model)
    return frame

class QWidgetWithLayout(Qt.QWidget):
    """
    A helper widget that allows to create QWidgets with predefined layouts
    """
    def __init__(self,parent=None,layout=None,child=None):
        Qt.QWidget.__init__(self,parent)

        if layout is None:
            layout = Qt.QHBoxLayout()
        else:
            layout = layout() if isinstance(layout,type) else layout
            
        self.setLayout(layout)
        
        child = fandango.toList(child)
        for c in child:
            if c is not None:
                self.addChildWidget(c)
    
    def addChildWidget(self,child,row=None,column=None):
        child.setParent(self)
        
        if isinstance(self.layout(),Qt.QGridLayout):
            row = fandango.notNone(row,self.layout().rowCount()-1)
            column = fandango.notNone(column,0)
            self.layout().addWidget(child,row,column)
            
        else:
            self.layout().addWidget(child)
    
    def childWidget(self):
        if isinstance(self.layout(),Qt.QGridLayout):
            return self.layout().itemAt(0,0).widget()
        else:
            return self.layout().itemAt(0).widget()
    
    def removeChildWidget(self):
        w = self.childWidget()
        self.layout().removeWidget(w)
        w.setParent(None)
        return w
        
        
class QTableOnWidget(Qt.QWidget):
    """
    A Helper class to easily initialize a QTable from an array
    """
    
    def __init__(self,parent=None,data=None,filters=True):
        Qt.QWidget.__init__(self,parent)
        self.setLayout(Qt.QVBoxLayout())
        if filters:
            self.top = Qt.QWidget()
            self.top.setLayout(Qt.QHBoxLayout())
            self.bar,self.button = Qt.QLineEdit(),Qt.QPushButton('Filter!')
            map(self.top.layout().addWidget,(self.bar,self.button))
            self.button.connect(self.button,Qt.SIGNAL('clicked()'),self.setFiltered)
            self.layout().addWidget(self.top)
        self.table = Qt.QTableWidget(self)
        self.layout().addWidget(self.table)
        for k in type(self.table).__dict__:
            if not k.startswith('_') and k not in type(self).__dict__:
                setattr(self,k,getattr(self.table,k))
        self.data = data
        self.widgets = {}
        if data: self.setData()

    def setData(self,data=None):
        self.data = data or []
        self.setCells()
        
    def setCells(self,data=None):
        data = fandango.notNone(data,self.data)
        if data and not isSequence(data[0]): data = [fandango.toList(r) for r in data]
        height,width = len(data),max(len(r) for r in (data or [[]]))
        self.setRowCount(height),self.setColumnCount(width)
        for i in range(height):
            for j in range(width):
                try:
                    if j>=len(data[i]): continue 
                    o = data[i][j]
                    if isinstance(o,Qt.QWidget):
                        w = self.cellWidget(i,j)
                        self.removeCellWidget(i,j)
                        if w: w.setParent(None)
                        qw = Qt.QWidget()
                        self.setCellWidget(i,j,Qt.QWidget())
                        self.cellWidget(i,j).setLayout(Qt.QVBoxLayout())
                    else:
                        self.setItem(i,j,Qt.QTableWidgetItem(str(o)))
                except:
                    traceback.print_exc()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        
    def setFiltered(self):
        self.data = self.data or []
        data = [d for d in self.data if fandango.searchCl(str(self.bar.text()),str(d))]
        self.setCells(data)

    @staticmethod
    def test(csvfile):
        #import fandango.qt;fandango.qt.QTableOnWidget.__test__(csvfile)
        data = fandango.CSVArray(csvfile)
        app = getApplication()
        w = QTableOnWidget()
        w.setData(data.rows)
        w.show()
        app.exec_()
            
class QEvaluator(Qt.QWidget):
    """
    Default methods:
     mdir(expr,[module]): return elements matching expr, from module or locals()
     help(method): returns source of method or __doc__
     doc(method): idem
     run(module): loads a module (reloads?)
     table/bold/color: html formatting
    """

    def __init__(self,parent=None,model='',filename='~/.qeval_history'): #'import fandango'):
        import fandango.web, fandango.functional
        print('%s()'%type(self).__name__)
        Qt.QWidget.__init__(self,parent)
        try:
            self.name = type(self).__name__
            self._locals = {'self':self,'load':self.setModel,'printf':self.printf,'Qt':Qt}
            self._locals.update([(k,v) for k,v in fandango.functional.__dict__.items() if isCallable(v)])
            self._locals['mdir'] = self.dir_module
            self._locals['help'] = self.help
            self._locals['doc'] = lambda x:x.__doc__
            self._locals['run'] = fandango.objects.loadModule
            self._locals.update((k,getattr(fandango.web,k)) for k in ('table','bold','color'))
            self._modules = {}
            self._instances = {}
            self.history = []
            self.filename = filename.replace('~',os.getenv('HOME')) if filename.startswith('~') else filename
            try:#Enabling Syntax Highlighting
                from pygments import highlight
                from pygments.lexers import PythonLexer
                from pygments.formatters import HtmlFormatter
                lexer,frmt=PythonLexer(),HtmlFormatter()
                self.css=frmt.get_style_defs('.highlight')
                self.highlight = lambda t,l=lexer,f=frmt: highlight(t,l,f) 
                #html='<head><style>%s</style><body>%s</body>'%(css,highlight(code,lexer,frmt))
            except:
                traceback.print_exc()
                self.css = None
                self.highlight = lambda t: '<pre>%s</pre>'%t
            self.evalQ('import fandango')
            self.evalQ('import fandango.qt')
            self.evalQ('f=fandango')
            self.setup_ui()
            self.setEval()
            self.setModel(model or '')
        except:
            traceback.print_exc()
        
    def dir_module(self,*args):
        f = fandango.first((a for a in args if isString(a)),'*')
        if '*' not in f and not f.startswith('_'): f = '*%s*'%f
        ks = fandango.first((dir(a) for a in args if not isString(a)),self._locals.keys())
        return sorted((t for t in fandango.matchAll(f,ks) if f.startswith('_') or not t.startswith('__')),key=str.lower)
    
    def help(self,m=None):
        try:
            if m:
                import inspect
                return '%s\n%s'%(inspect.getsource(m).split(':')[0].replace('\n',''),m.__doc__)
            else:
                return self.__doc__
        except: return str(m)
        
    def setEval(self,m=None):
        self._eval = m or self.evalQ
        
    def setModel(self,model=None):
        """
        setModel(obj) will set the last element of a sequence of commands as Model for the shell
        The Model can be either an object, class, module, ...
        """
        print 'QEvaluator.setModel(%s)'%model
        try:
            if model:
                if isString(model):
                    for c in model.split(';'):
                        try: model,o = c,self.evalQ(c)
                        except: 
                          if len(c.split())==1:
                            model,o = 'import '+c,self.evalQ('import '+c)
                          else:
                            traceback.print_exc()
                    if '=' in model:
                        self.model,dct = model.split()[0],self._locals
                    elif 'import' in model:
                        self.model,dct = model.split()[-1],self._modules
                    else:
                        self.model,dct = model,{model:o}
                    self.target = dct[self.model]
                else:
                    self.model = str(model)
                    self.target = model
                self._locals['model'] = self.target
                self.commands = fandango.matchAll('^[a-zA-Z]*',dir(self.target))
                self.combo.clear()
                self.combo.addItems(sorted(self.commands,key=str.lower))
            else:
                self.model = None
                self.target = None
                self.commands = []
                self.combo.clear()
                self.combo.addItems(list(reversed(self.history)))
            self.setWindowTitle('FANDANGO.%s(%s)'%(self.name,self.model or ''))
        except:
            w = QExceptionMessage()
        
    def evalQ(self,c):
        return fandango.evalX(c,_locals=self._locals,modules=self._modules,instances=self._instances,_trace=True)
        
    def setup_ui(self):
        from PyQt4.QtWebKit import QWebView
        self.combo = Qt.QComboBox(self)
        self.combo.setEditable(True) #self.model in (None,'fandango'))
        self.args = Qt.QComboBox(self) #Qt.QLineEdit(self)
        self.args.setEditable(True)
        self.result = QWebView(self)
        self.result.setHtml('<html><head><style>%s</style></head><body></body></html>'%(self.css))
        self.button = Qt.QPushButton('Execute!')
        self.export = Qt.QPushButton('Save History')
        self.mlbt = Qt.QPushButton('ml')
        self.mlbt.setMaximumWidth(50)
        self.mlload = Qt.QPushButton('load history')
        self.mlex = Qt.QPushButton('Execute!')
        self.mledit = Qt.QTextEdit()
        self.shortcut = Qt.QShortcut(self)
        self.shortcut.setKey(Qt.QKeySequence("Ctrl+Enter"))
        self.connect(self.shortcut, Qt.SIGNAL("activated()"), self.button.animateClick) #self.execute)
        self.check = Qt.QCheckBox('Append')
        self.check.setChecked(True)
        self.setLayout(Qt.QGridLayout())
        self.layout().addWidget(Qt.QLabel('Write python code or load(module) and select from the list'),0,0,1,4)
        self.layout().addWidget(Qt.QLabel('function/statement'),1,0,1,1)
        self.layout().addWidget(self.combo,1,1,1,3)
        self.layout().addWidget(self.mlbt,1,4,1,1)
        self.layout().addWidget(Qt.QLabel('arguments'),2,0,1,1)
        self.layout().addWidget(self.args,2,1,1,3)
        self.layout().addWidget(self.result,3,0,4,5)
        self.layout().addWidget(self.button,8,0,1,2)
        self.layout().addWidget(self.export,8,2,1,1)
        self.layout().addWidget(self.check,8,3,1,1)
        self.connect(self.button,Qt.SIGNAL('clicked()'),self.execute)
        self.connect(self.export,Qt.SIGNAL('clicked()'),self.save_to)
        self.connect(self.mlbt,Qt.SIGNAL('clicked()'),self.multiline_edit)
        self.connect(self.mlex,Qt.SIGNAL('clicked()'),self.multiline_exec)
        self.connect(self.mlload,Qt.SIGNAL('clicked()'),self.multiline_load)
        
    def multiline_edit(self):
        if not hasattr(self,'mlqd'):
            self.mlqd = Qt.QDialog(self)
            self.mlqd.setWindowTitle('Editor'),self.mlqd.setLayout(Qt.QVBoxLayout())
            map(self.mlqd.layout().addWidget,(self.mlload,self.mledit,self.mlex))
        self.mlqd.show()
    def multiline_exec(self):
        [self.execute(l.strip(),'') for l in str(self.mledit.toPlainText()).split('\n')]
    def multiline_load(self):
        self.mledit.setText('\n'.join(self.history))
        
    def execute(self,cmd=None,args=None):
        """
        (Ctrl+Enter) Send the current command,arguments to the eval engine and process the output.
        """
        if not cmd and not args:
            cmd,args = str(self.combo.currentText()),str(self.args.currentText()) #text())
        print('execute: %s(%s)'%(cmd,args))
        if self.filename:
            try: open(self.filename,'a').write('%s.%s(%s)\n'%(self.model,cmd,args))
            except: pass
        try:
            q = cmd if cmd not in self.commands else 'self.target.%s'%(cmd)
            o = self._eval(q)
            if fandango.isCallable(o) and args:
                print '%s(%s)'%(o,args)
                self._locals['_ftmp'] = o
                o = self._eval('_ftmp(%s)'%(args))
                self.history.append('%s(%s)'%(o,args))
            else: self.history.append(q)
            #print(self.history[-1])
        except:
            o = traceback.format_exc()
            print(o)
        txt = '\n'.join(map(str,o.items()) if hasattr(o,'items') else ([(str(t).strip('\n\r ') or getattr(t,'__name__','?')) for t in o] if isSequence(o) else [str(o)]))
        isHtml = txt.strip().startswith('<') and txt.strip().endswith('>') and '</' in txt
        txt = ('execute: %s(%s) => '%(cmd,args))+type(o).__name__+':\n'+'-'*80+'\n' + txt
        self.printf(txt,append=self.check.isChecked(),highlight=not isHtml)
        if self.model is None and not any(i>1 and cmd==str(self.combo.itemText(i)) for i in range(self.combo.count())): 
            self.combo.insertItems(0,[cmd])
        self.args.insertItems(0,[args])
        
    def save_to(self,filename=None,txt=None):
        pass
        
    def printf(self,txt,append=True,highlight=False,curr=''):
        if append: 
            try: 
                curr = self.result.page().currentFrame().toHtml().replace('</body></html>','')
                plain = self.result.page().currentFrame().toPlainText()
            except: 
                traceback.print_exc()
                curr = ''
        txt = self.highlight(txt) if (highlight is True) else txt #highlight=1 can still be used to force highlighting
        if (self.css and '<style>' not in curr) or not curr or not append:
            txt = ('<html><head><style>%s</style></head><body>%s</body></html>'%(self.css,txt))
        else:
            txt = (str(curr)+'<br>'+txt+'</body></html>')
        self.result.setHtml(txt)
        try:
            self.result.keyPressEvent(Qt.QKeyEvent(Qt.QEvent.KeyPress,Qt.Qt.Key_End,Qt.Qt.NoModifier))
            #self.result.page().mainFrame().scroll(0,self.result.page().mainFrame().contentsSize().height())
        except:
            traceback.print_exc()
    
    @staticmethod
    def main(args=[]):
        qapp = getApplication()
        print(len(args),args)
        args = args or sys.argv[1:]
        if args and os.path.isfile(args[0]):
          args = filter(bool,map(str.strip,open(args[0]).readlines()))
        kw = args and {'model':';'.join(args)} or {}
        print('model',kw.get('model'))
        w = QEvaluator(**kw)
        w.show()
        qapp.exec_()        
        

class ApiBrowser(QEvaluator): pass #For backwards compatibility
        
if __name__ == '__main__':
    QEvaluator.main(sys.argv[1:])
