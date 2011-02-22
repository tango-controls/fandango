
from PyQt4 import Qt,QtCore,QtGui
import Queue,traceback
from functools import partial
from functional import isString
from log import Logger

def modelSetter(obj,model):
    if hasattr(obj,'setModel') and model:
        obj.setModel(model)
    return

class TauEmitterThread(QtCore.QThread):
    """
    This object get items from a python Queue and performs a thread safe operation on them.
    It is useful to delay signals in a background thread.
    :param parent: a Qt/Tau object
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
        
        klass TauGrid(QtGui.QFrame, TauBaseWidget):
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
    def __init__(self, parent=None,queue=None,method=None,cursor=None,sleep=5000):
        """
        Parent most not be None and must be a TauGraphicsScene!
        :param method: function to be applied for any argument list stored in the queue, if None the first argument of the list will be used as method
        """
        #if not isinstance(parent, TauGraphicsScene):
            #raise RuntimeError("Illegal parent for TauGraphicsUpdateThread")
        QtCore.QThread.__init__(self, parent)
        self.log = Logger('TauEmitterThread')
        self.log.setLogLevel(self.log.Info)
        self.queue = queue or Queue.Queue()
        self.todo = Queue.Queue()
        self.method = method
        self.cursor = Qt.QCursor(Qt.Qt.WaitCursor) if cursor is True else cursor
        self._cursor = False
        self.sleep = sleep
        
        self.emitter = QtCore.QObject()
        self.emitter.moveToThread(QtGui.QApplication.instance().thread())
        self.emitter.setParent(QtGui.QApplication.instance())
        self._done = 0
        QtCore.QObject.connect(self.emitter, QtCore.SIGNAL("doSomething"), self._doSomething)
        QtCore.QObject.connect(self.emitter, QtCore.SIGNAL("somethingDone"), self.next)          
        
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
        self.emitter.emit(QtCore.SIGNAL("somethingDone"))
        self._done += 1
        return
                
    def next(self):
        queue = self.getQueue()
        (queue.empty() and self.log.info or self.log.debug)('At TauEmitterThread.next(), %d items remaining.' % queue.qsize())
        try:
            if not queue.empty():            
                if not self._cursor and self.cursor is not None: 
                    QtGui.QApplication.instance().setOverrideCursor(Qt.QCursor(self.cursor))
                    self._cursor=True                
                item = queue.get(False) #A blocking get here would hang the GUIs!!!
                self.todo.put(item)
                self.log.debug('Item added to todo queue: %s' % str(item))
            elif self._cursor: 
                QtGui.QApplication.instance().restoreOverrideCursor()
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
            self.emitter.emit(QtCore.SIGNAL("doSomething"), item)
            #End of while
        self.log.info('#'*80+'\nOut of TauEmitterThread.run()'+'\n'+'#'*80)
        #End of Thread 
