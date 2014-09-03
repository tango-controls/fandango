
from PyQt4 import Qt,QtCore,QtGui
import Queue,traceback,time
from functools import partial
import fandango
from functional import isString,isSequence
from fandango.log import Logger,shortstr
from fandango.dicts import SortedDict
from fandango.objects import Singleton

def getStateLed(model):
    from taurus.qt.qtgui.display import TaurusStateLed
    led = TaurusStateLed()
    led.setModel(model)
    print 'In TaurusStateLed.setModel(%s)'%model
    return led

def getApplication(args=None):
    app = Qt.QApplication.instance()
    return app or Qt.QApplication(args or [])

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
        
#from taurus.qt import Qt
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
        
import taurus.core,taurus.qt
import taurus.qt.qtgui.util.tauruscolor as colors
import taurus.qt.qtgui.base as taurusbase
from taurus.core import TaurusEventType,TaurusAttribute
from taurus.qt.qtgui.graphic import TaurusGraphicsItem

def getColorsForValue(value,palette = colors.QT_DEVICE_STATE_PALETTE):
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

class TauColorComponent(taurusbase.TaurusBaseComponent):
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
        
from taurus.qt import Qt
from taurus.qt.qtgui.container.tauruswidget import TaurusWidget

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

#############################################################################################
## DO NOT EDIT THIS CLASS HERE, THE ORIGINAL ONE IS IN taurus utils emitter!!!
#############################################################################################

def modelSetter(obj,model):
    if hasattr(obj,'setModel') and model:
        obj.setModel(model)
    return
        
class TauEmitterThread(Qt.QThread):
    """
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
        return self._done/(self._done+self.getQueue().qsize()) if self._done else 0.

    def _doSomething(self,args):
        self.log.debug('At TauEmitterThread._doSomething(%s)'%str(args))
        if not self.method: 
            method,args = args[0],args[1:]
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
            elif self._cursor: 
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
            
###############################################################################

def DoubleClickable(QtKlass):
    """ 
    This decorator enables a Qt class to execute a 'hook' method every time is double-clicked
    """    
    class DoubleClickableQtKlass(QtKlass):
        def __init__(self,*args):
            self.my_hook = None
            QtKlass.__init__(self,*args)
        def setClickHook(self,hook):
            """ the hook must be a function or callable """
            self.my_hook = hook #self.onEdit
        def mouseDoubleClickEvent(self,event):
            if self.my_hook is not None:
                self.my_hook()
            else:
                try: QtKlass.mouseDoubleClickEvent(self)
                except: pass
    return DoubleClickableQtKlass
                
class TangoHostChooser(Qt.QWidget):
    """
    Allows to choose a tango_host from a list
    """
    def __init__(self,hosts):
        self.hosts = sorted(hosts)
        Qt.QWidget.__init__(self,None)
        self.setLayout(Qt.QVBoxLayout())
        self.layout().addWidget(Qt.QLabel('Choose your TangoHost:'))
        self.chooser = Qt.QComboBox()
        self.chooser.addItems(self.hosts)
        self.layout().addWidget(self.chooser)
        self.button = Qt.QPushButton('Done')
        self.layout().addWidget(self.button)
        self.button.connect(self.button,Qt.SIGNAL('pressed()'),self.done)
        self.button.connect(self.button,Qt.SIGNAL('pressed()'),self.close)
    def done(self):
        import os
        os.environ['TANGO_HOST']=str(self.chooser.currentText())
        new_value = os.getenv('TANGO_HOST')
        print('TANGO_HOST set to %s'% new_value)
        return new_value
    
###############################################################################


class QDropTextEdit(Qt.QTextEdit):
    """
    This method provides a widget that allows drops of text from other widgets.
    As a bonus, it provides a simple hook for DoubleClick events
    """
    def __init__(self,*args):#,**kwargs):
        self.double_click_hook = None
        QtGui.QLineEdit.__init__(self,*args)#,**kwargs)
    
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
        supported = self.mimeTypes()
        formats = mimeData.formats()
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
        for item in self._widgets:
            self.removeWidget(item)
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
