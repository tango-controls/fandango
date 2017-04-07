
from PyQt4 import Qt
import fandango as fn
import fandango.qt as fqt
from FolderDS import FolderAPI

class FolderGUI(Qt.QSplitter):
  
    def __init__(self,parent=None,mask=None):
      Qt.QSplitter.__init__(self,parent)
      self.api = FolderAPI(mask)
      #self.ui = Qt.QMainWindow()
      #self.ui.setWindowTitle('FolderDS Widget')
      self.setWindowTitle('FolderDS Widget')
      self.rawdata = ''
      self.left = fqt.QWidgetWithLayout(layout=Qt.QGridLayout)
      self.right = fqt.QWidgetWithLayout(layout=Qt.QGridLayout)
      self.insertWidget(0,self.left)
      self.insertWidget(1,self.right)

      self.label = Qt.QLabel('Folder Device')
      self.devices = Qt.QComboBox()
      self.devices.addItems(self.api.get_all_devices())
      self.files = fqt.DoubleClickable(Qt.QListWidget)()
      self.files.setToolTip('double click on a file to show its contents')
      self.filename = Qt.QLineEdit()
      self.mask = Qt.QLineEdit()
      self.mask.setText('*')
      self.mask.setToolTip('CASE SENSITIVE!')
      self.mask2 = Qt.QLineEdit()
      self.mask2.setText('*')
      self.mask2.setToolTip('type a filter to search in the loaded file')
      self.data = Qt.QTextEdit()
      self.list = Qt.QPushButton('List Files')
      self.load =Qt.QPushButton('Load')
      self.new = Qt.QPushButton('Clear')
      #self.save = Qt.QPushButton('Save File')
      self.filter = Qt.QPushButton('Filter')

      put = self.left.layout().addWidget
      put(self.label,0,0,1,1)
      put(self.devices,0,1,1,1)
      put(self.mask,1,0,1,1)
      put(self.list,1,1,1,1)
      put(self.files,2,0,4,2)
      put(self.load,7,1,1,1)

      put = self.right.layout().addWidget
      put(self.filename,0,0,1,2)
      put(self.mask2,1,0,1,1)
      put(self.filter,1,1,1,1)
      put(self.data,2,0,5,2)
      put(self.new,7,1,1,1)
      #put(self.save,7,1,1,1)
      #self.save.setEnabled(False)
      self.data.setReadOnly(True)
      self.filename.setEnabled(False)
      
      self.list.connect(self.list,Qt.SIGNAL("pressed()"),self.listFiles)
      self.files.setClickHook(self.loadFile)
      self.load.connect(self.load,Qt.SIGNAL("pressed()"),self.loadFile)
      self.new.connect(self.new,Qt.SIGNAL("pressed()"),self.newFile)
      self.filter.connect(self.filter,Qt.SIGNAL("pressed()"),self.showFile)
      
    def listFiles(self):
      self.files.clear()
      device = str(self.devices.currentText())
      mask = str(self.mask.text())
      if '*' not in mask: mask = '*%s*'%mask
      files = sorted(fn.clsplit('[:/]',f)[-1] for f in self.api.find(device,mask))
      self.files.addItems(files)
      
    def loadFile(self):
      device = str(self.devices.currentText())
      filename = str(self.files.currentItem().text())
      self.filename.setText(filename)
      self.rawdata = self.api.read(device,filename)
      self.showFile()
      
    def showFile(self):
      mask = str(self.mask2.text())
      data = fn.filtersmart(self.rawdata.split('\n'),mask)
      self.data.setText('\n'.join(data))
      
    def newFile(self):
      self.filename.setText('')
      self.data.setText('')
        
    @staticmethod
    def main(args=[]):
      import fandango.qt as fqt
      app = fqt.getApplication()
      fgui = FolderGUI(mask=args and args[0] or None)
      fgui.show()
      app.exec_()
      
main = FolderGUI.main
      
if __name__ == '__main__':
  main()
