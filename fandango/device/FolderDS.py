#=============================================================================
#
# file :        FolderDS.py
#
# description : Python source for the FolderDS and its commands. 
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                FolderDS are implemented in this file.
#
# project :     TANGO Device Server
#
# $Author:  srubio@cells.es
#
#
# copyleft :    European Synchrotron Radiation Facility
#               BP 220, Grenoble 38043
#               FRANCE
#
#=============================================================================
#          This file is generated by POGO
#    (Program Obviously used to Generate tango Object)
#
#         (c) - Software Engineering Group - ESRF
#=============================================================================


import sys,os,re,random
import traceback

import PyTango
import fandango as fn
import fandango.tango as tango
from fandango.log import printtest
from fandango.tango import ProxiesDict
from fandango.servers import ServersDict
from fandango.dynamic import DynamicDS,DynamicDSClass,DynamicAttribute

#==================================================================
#   FolderDS Class Description:
#
#         <p>This device requires <a href="http://www.tango-controls.org/Documents/tools/fandango/fandango">Fandango module<a> to be available in the PYTHONPATH.</p>
#
#==================================================================

class FolderAPI(ProxiesDict,fn.SingletonMap):
    """
    The FolderAPI object will allow to access all FolderDS instances in the system.
    This will allow to easily save, read, list files in the Folder ecosystem.
    Files can be tracked by any host, using get_all_hosts() and get_host_devices() methods.
    """
    
    def __init__(self,mask=None):
        #mask = mask or 'FolderDS/*'
        self.mask = mask
        ProxiesDict.__init__(self)
        devs = tango.get_class_devices('FolderDS')
        extra = fn.get_database().get_class_property('FolderDS',['ExtraDevices'])
        devs.extend(extra.get('ExtraDevices',[]))
        if mask: devs = fn.filtersmart(devs,mask)
        self.hosts = fn.defaultdict(list)

        for d in devs: self[d]; #initialize proxies
        
    def __str__(self):
        return 'FolderAPI(%s[%s])'%(self.mask,len(self))
    
    def __setitem__(self,key,value):
        key = key.replace('folderds:','')
        key = tango.get_full_name(key)
        ProxiesDict.__setitem__(self,key,value)
        try:
            i = fn.get_device_info(key)
            self.hosts[i.host].append(key)
        except: pass
            
    def get_all_devices(self,exported=False):
        devs = self.keys()
        if exported: 
          devs = filter(fn.check_device,devs)
        return devs
            
    def get_host_devices(self,host):
        return self.hosts[host]
    
    def get_device(self,dev,exported=True):
        dev = dev or '*'
        if dev.startswith('folderds:'): #dev.startswith('folderds:'):
            dev = dev.split(':',1)[-1] #replace('folderds:','')
        dev = dev.strip('/')
        if '*' in dev:
            m = [d for d in self.get_all_devices(exported) if fn.clmatch(dev,d)]
            dev = m[random.randint(0,len(m)-1)]
        else:
            dev = fn.clsub('^tango:/{0,2}','',dev)
            parts = dev.split('/')
            dev = '/'.join(parts[0:3+dev.count(':')])
        return self[dev]
      
    def get_device_name(self,proxy):
        name = proxy.name()
        if ':' not in name:
          host = proxy.get_db_host().split('.')[0]
          port = proxy.get_db_port()
          name = '%s:%s/%s' % (host,port,name)
        return tango.get_full_name(name)
    
    def save(self,device,filename,data,add_timestamp=False,asynch=True):
        """
        FolderDS device, filename WITHOUT PATH!, data to be saved
        add_timestamp: whether to add or not timestamp at the end of filename
        asynch: if True, the save() call will not wait for the command to complete
        """
        # Remove device path from filename
        filename = (filename or device).split('/')[-1]
        if add_timestamp:
            t = fn.time2str().replace(' ','_').replace(':','').replace('-','')
            p,s = (filename.rsplit('.',1)) if '.' in filename else (filename,'')
            filename = '.'.join(filter(bool,(p,t,s)))
        d = self.get_device(device) #
        if asynch:
          d.command_inout_asynch('SaveFile',[filename,data],True)
          r = len(data)
        else:
          r = d.SaveFile([filename,data])
        print('%s.SaveFile() : %s)'%(device,r))
        return r

    def read(self,uri,filename=''):
        if not filename: 
          uri,filename = uri.rsplit('/',1)
        return self.get_device(uri).GetFile(filename)
    
    def find(self,device,mask,N=0):
        m = [d for d in self.get_all_devices() if fn.clmatch(device,d)]
        r = []
        for d in m:
            l = fn.get_device(d).ListFiles(mask)
            for f in l:
                r.append((d+':' if len(m)>1 else '')+f)
                if N and N>=len(r):
                  return r
        return r
      
    @staticmethod
    def __test__():
        import fandango.device
        try: reload(fandango.device)
        except: pass
        folders = fandango.device.FolderAPI('*')
        printtest(folders,'get_all_devices')
        printtest(folders,'get_host_devices',args=[folders.hosts.keys()[0]])
        d = printtest(folders,'get_device',args=['*'])
        n = folders.get_device_name(d)
        printtest(folders,'save',[n,'test.txt','----\nHello World!\n----\n'])
        f = printtest(folders,'find',[n,'test.txt'],{'N':1})
        printtest(folders,'read',args=[n,f[0] if f else ''])
        
      
class FolderDS(DynamicDS): #PyTango.Device_4Impl):
    """ The FolderDS Device Server will allow to write/save/list text files between tango devices """

#--------- Add you global variables here --------------------------

    def save_text_file(self,filename,data):
        print('In FolderDS.save_text_file(%s,%d)'%(filename,sys.getsizeof(data)))
        #if self.SaveFolder and not filename.startswith('/'):
        filename = self.SaveFolder + '/' + filename #SAFER TO FORCE  ALWAYS PATH
        f = open(filename,'w')
        f.write(data)
        f.close()
        #filename,data = argin[0],'\n'.join(argin[1:])
        #fc=filename.replace('.','_').replace('/','.').replace(' ','_').replace('\\','_')
        #cmd = "%s=open('%s/%s','w')"%(fc,self.SaveFolder,filename)
        #print(cmd)
        #self.worker.put(cmd)
        #self.worker.locals().__setitem__(fc+'_data',data)
        #self.worker.put("%s.write(%s_data)"%(fc,fc))
        #self.worker.put("%s.close()"%fc)    
        
    def list_files(self,mask,files=None):
        if not files:
            if '/' in mask:
                folder,mask = mask.rsplit('/',1)
            else:
                folder,mask = '',mask
            #if self.SaveFolder and not folder.startswith('/'):
            folder = self.SaveFolder + '/' + folder  #SAFER TO FORCE  ALWAYS PATH
            return fandango.listdir(folder,mask)
        else:
            #using cache
            return [f for f in files if fandango.clmatch(mask,f)]        
        
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        #PyTango.Device_4Impl.__init__(self,cl,name)        
        ##Loading special methods to be available in formulas
        _locals = {}        
        DynamicDS.__init__(self,cl,name,_locals=_locals,useDynStates=True)
        FolderDS.init_device(self)
        self.worker = fandango.threads.WorkerThread()
        self.worker.start()
        self.worker.put('1')

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        print "[Device delete_device method] for device",self.get_name()


#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
        print "In ", self.get_name(), "::init_device()"
        DynamicDS.init_device(self)
        if self.DynamicStates: self.set_state(PyTango.DevState.UNKNOWN)
        print "Out of ", self.get_name(), "::init_device()"

#------------------------------------------------------------------
#    Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"
        DynamicDS.always_executed_hook(self)

#==================================================================
#
#    FolderDS read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#    Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self,data):
        print "In ", self.get_name(), "::read_attr_hardware()"


#==================================================================
#
#    FolderDS command methods
#
#==================================================================

    def SaveFile(self,argin):
        df = getattr(self,self.DefaultMethod)
        return df(argin)
        
    def SaveText(self,argin):
        filename,data = argin[0],'\n'.join(argin[1:])
        self.worker.put([self.save_text_file,filename,data])
        return [str(filename),str(len(data))]
    
    def GetFile(self,filename):
        filename = self.SaveFolder + '/' + filename #SAFER TO FORCE  ALWAYS PATH
        f = open(filename)
        data = f.read()
        f.close()
        return data
    
    def GetFileTime(self,filename):
        filename = self.SaveFolder + '/' + filename #SAFER TO FORCE  ALWAYS PATH
        if not os.path.exists(filename): return 0
        return os.path.getmtime(filename)    
    
    def ListFiles(self,mask):
        return self.list_files(mask)
    
#==================================================================
#
#    FolderDSClass class definition
#
#==================================================================
class FolderDSClass(DynamicDSClass):

    #    Class Properties
    class_property_list = {
      'ExtraDevices':
            [PyTango.DevVarStringArray,
            "Devices from other tango hosts to be shown in FolderGUI",
            [ ] ],                    
        }


    #    Device Properties
    device_property_list = {
       'DefaultMethod':
            [PyTango.DevString,
            "Method to be used when calling SaveFile()",
            [ 'SaveText' ] ],
       'SaveFolder':
            [PyTango.DevString,
            "Folder for saving/retrieving data files",
            [ '/tmp/folderds' ] ],            
        }


    #    Command definitions
    cmd_list = {
        'SaveFile':
            [[PyTango.DevVarStringArray, "filename,contents"],
            [PyTango.DevVarStringArray, "filename, size"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],        
        'SaveText':
            [[PyTango.DevVarStringArray, "filename,contents"],
            [PyTango.DevVarStringArray, "filename, size"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],        
        'GetFile':
            [[PyTango.DevString, "filename"],
            [PyTango.DevString, "contents"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],        
        'GetFileTime':
            [[PyTango.DevString, "filename"],
            [PyTango.DevDouble, "modified timestamp"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],            
        'ListFiles':
            [[PyTango.DevString, "filename mask"],
            [PyTango.DevVarStringArray, "file list"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],         
        'Help':DynamicDSClass.cmd_list['Help'],
        }


    #    Attribute definitions
    attr_list = {
        }


#------------------------------------------------------------------
#    FolderDSClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);
        print "In FolderDSClass  constructor"

#==================================================================
#
#    FolderDS class main method
#
#==================================================================
def main(args = None):
    try:
        py = PyTango.Util(args or sys.argv)
        py.add_TgClass(FolderDSClass,FolderDS,'FolderDS')
        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print( '-------> Received a DevFailed exception:',traceback.format_exc())
    except Exception,e:
        print( '-------> An unforeseen exception occured....',traceback.format_exc())
        
def test(args = None):
    print('\n')
    args = args or sys.argv[2:]
    FolderAPI.__test__()
    #api = FolderAPI()
    #print(api.states())
    #if args:
        #c = args[0]
        #a = args[1:]
        #print(c,a)
        #print(getattr(api,c)(*a))

if __name__ == '__main__':
    if '--test' in sys.argv:
        test()
    if '--gui' in sys.argv:
        from FolderGUI import FolderGUI
        FolderGUI.main()
    else:
        main()
