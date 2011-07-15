
from PyQt4 import Qt,QtCore,QtGui
import Queue,traceback
from functools import partial
from functional import isString
from log import Logger
try: 
    import tau,tau.widget,tau.core
    from tau.widget import taubase,colors
    USE_TAU = True
except:
    USE_TAU = False

if USE_TAU:
    def getColorsForValue(value,palette = colors.QT_DEVICE_STATE_PALETTE):
        """ 
        Get QColor equivalent for a given Tango attribute value 
        It returns a Background,Foreground tuple
        """
        print 'In getColorsForValue(%s)'%value
        if value is None:
            return Qt.QColor(Qt.Qt.gray),Qt.QColor(Qt.Qt.black)
        elif hasattr(value,'value'): #isinstance(value,PyTango.DeviceAttribute):
            if value.type == taubase.PyTango.ArgType.DevState:
                bg_brush, fg_brush = colors.QT_DEVICE_STATE_PALETTE.qbrush(value.value)
            elif value.type == taubase.PyTango.ArgType.DevBoolean:
                bg_brush, fg_brush = colors.QT_DEVICE_STATE_PALETTE.qbrush((taubase.PyTango.DevState.FAULT,taubase.PyTango.DevState.ON)[value.value])                    
            else:
                bg_brush, fg_brush = colors.QT_ATTRIBUTE_QUALITY_PALETTE.qbrush(value.quality)            
        else:
            bg_brush, fg_brush = palette.qbrush(int(value))
            
        return bg_brush.color(),fg_brush.color()
    
    class TauColorComponent(tau.widget.taubase.TauBaseComponent):
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
            self.call__init__(tau.widget.taubase.TauBaseComponent, name, parent)
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
            tau.widget.taubase.TauBaseComponent.setModel(self,model) 
    
        def getParentTauComponent(self):
            """ Returns a parent Tau component or None if no parent TauBaseComponent 
                is found."""
            p = self.parentItem()
            while p and not isinstance(p, TauGraphicsItem):
                p = self.parentItem()
            return p
    
        #def fireEvent(self, evt_src = None, evt_type = None, evt_value = None):
        def handleEvent(self, evt_src = None, evt_type = None, evt_value = None):
            """fires a value changed event to all listeners"""
            self.info('In TauColorComponent(%s).handleEvent(%s,%s)'%(self.__name,evt_src,evt_type))
            if evt_type!=tau.core.enums.TauEventType.Config: 
                #@todo ; added to bypass a problem with getModelValueObj()
                self.__value = evt_value if evt_type!=tau.core.enums.TauEventType.Error else None
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
            return tau.core.TauAttribute
        
try:
    from tau.widget.utils.emitter import modelSetter,TauEmitterThread,SingletonWorker
except:
    import traceback
    print 'Unable to load TauEmitterThread from tau.widget.utils'
    print traceback.format_exc()
    
    #############################################################################################
    ## DO NOT EDIT THIS CLASS HERE, THE ORIGINAL ONE IS IN tau.widget.utils.emitter!!!
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
            
            klass TauGrid(Qt.QFrame, TauBaseWidget):
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
