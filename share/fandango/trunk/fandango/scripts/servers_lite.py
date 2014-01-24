
import time,traceback,os,sys,threading,datetime
import collections,re 
from random import randrange
from itertools import chain
import socket

import PyTango
import taurus
from taurus.core.tango.search import isDictionary,isSequence,searchCl,matchCl
from taurus.core.util import Object
from taurus.core.util import CaselessDict

###############################################################################
# from fandango.tango

def get_database():
    return PyTango.Database()

def get_device(device): 
    return taurus.Device(device)

def get_database_device(): 
    return taurus.Device(PyTango.Database().dev_name())

def add_new_device(server,klass,device):
    """
    It can be used create any device, e.g. to create Starter in an init script
    add_new_device('Starter/$HOST','Starter','sys/admin/starter')
        Then:
            ./Starter $HOST &
    """    
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device
    dev_info.klass = klass
    dev_info.server = server
    get_database().add_device(dev_info)    

def get_device_property(device,property):
    """
    It returns device property value or just first item if value list has lenght==1
    """
    prop = list(get_database().get_device_property(device,[property])[property])
    #prop = prop if len(prop)!=1 else prop[0]
    return prop
    
def get_device_properties(device,flt='*'):
    properties = list(get_database().get_device_property_list(device,flt))
    return dict((p,get_device_property(device,p)) for p in properties)
    
def put_device_property(device,property,value=None):
    """
    Two syntax are possible:
     - put_device_property(device,{property:value})
     - put_device_property(device,property,value)
    """
    if not isDictionary(property):
        property = {property:value}
    print device,property
    return get_database().put_device_property(device,property)
    
def get_device_attributes(device):
    return get_device(device).get_attribute_list()

def get_device_attribute_properties(device,attribute):
    props = get_database().get_device_attribute_property(device,{attribute:'*'})[attribute]
    return dict((k,list(p)) for k,p in props.items())

def clean_device_attribute_properties(device):
    attrs = get_device_attributes(device)
    props = dict((a,get_device_attribute_properties(device,a).keys()) for a in attrs)
    #In [153]: db.delete_device_attribute_property('test/test/test-04',{'t2':['unit']})
    for p,v in props.items():
        if not v: continue
        get_database().delete_device_attribute_property(device,{p:v})
        
def clean_device_properties(device):
    props = get_device_properties(device)
    get_database().delete_device_property(device,props.keys())
    
def remove_device_server(server,clean_db=True):
    s = Astor(server)
    assert len(s),'ServerNotFound!'
    assert len(s)==1,'RegexpNotAllowed:%s'%s.keys()
    if clean_db: assert None not in s.states().values(),'DeviceNotRunning'
    devs = s.get_all_devices()
    for device in devs:
        try:
            if clean_db:clean_device_attribute_properties(device)
        except:
            print 'Unable to clean attributes, device not running'
            return
    s.stop_servers()
    for device in devs:
        if clean_db:clean_device_properties(device)
        get_database().delete_device(device)
    get_database().delete_server(server)

class defaultdict_fromkey(collections.defaultdict):
    """ Creates a dictionary with a default_factory function that creates new elements using key as argument.
    Usage : new_dict = defaultdict_fromkey(method); where method like (lambda key: return new_obj(key))
    Each time that new_dict[key] is called with a key that doesn't exist, method(key) is used to create the value
    Copied from PyAlarm device server
    @deprecated now in tau.core.utils.containers
    """
    def __missing__(self, key):
        if self.default_factory is None: raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value

class CaselessDefaultDict(defaultdict_fromkey,CaselessDict):
    """ a join venture between caseless and default dict
    This class merges the two previous ones.
    This declaration equals to:
        CaselessDefaultDict = type('CaselessDefaultType',(CaselessDict,defaultdict_fromkey),{})
    """
    def __getitem__(self, key):
        return defaultdict_fromkey.__getitem__(self, key.lower())
    pass

class ProxiesDict(CaselessDefaultDict,Object): #class ProxiesDict(dict,log.Logger):
    ''' Dictionary that stores PyTango.DeviceProxies
    It is like a normal dictionary but creates a new proxy each time that the "get" method is called
    An earlier version is used in PyTangoArchiving.utils module
    This class must be substituted by Tau.Core.TauManager().getFactory()()
    '''
    def __init__(self):
        self.call__init__(CaselessDefaultDict,self.__default_factory__)
    def __default_factory__(self,dev_name):
        '''
        Called by defaultdict_fromkey.__missing__ method
        If a key doesn't exists this method is called and returns a proxy for a given device.
        If the proxy caused an exception (usually because device doesn't exists) a None value is returned
        '''        
        if dev_name not in self.keys():
            try:
                devklass,attrklass = (taurus.Device,taurus.Attribute)
                dev = (attrklass if str(dev_name).count('/')==(4 if ':' in dev_name else 3) else devklass)(dev_name)
            except Exception,e:
                print('ProxiesDict: %s doesnt exist!'%dev_name)
                print traceback.format_exc()
                dev = None
        return dev
            
    def get(self,dev_name):
        return self[dev_name]   
    def get_admin(self,dev_name):
        '''Adds to the dictionary the admin device for a given device name and returns a proxy to it.'''
        dev = self[dev_name]
        class_ = dev.info().dev_class
        admin = dev.info().server_id
        return self['dserver/'+admin]
    def pop(self,dev_name):
        '''Removes a device from the dict'''
        if dev_name not in self.keys(): return
        return CaselessDefaultDict.pop(self,dev_name)
        
####################################################################################################################

class TServer(Object):
    '''Class used by ServerDict to manage TangoDeviceServer admin devices.'''
    def __init__(self,name='', host='', parent=None):
        if not name or '/' not in name: raise Exception,'TServer_WrongServerName_%s' % name
        self.name=self.get_simple_name(name)        
        self.update_level(host,0)
        self.controlled = False
        self.level = 0
        self._classes = None
        self.state=None #PyTango.DevState.UNKNOWN
        self.state_lock = threading.Lock()
        
        if parent: self.proxies=parent.proxies
        else: self.proxies=ProxiesDict()
        pass
        
    def set_state(self,state):
        self.state_lock.acquire()
        self.state=state
        self.state_lock.release()
        
    def ping(self,dname=None):
        '''Executes .ping() and .state() methods of the admin device.'''
        name = dname or self.get_admin_name()
        wait = threading.Event().wait
        if not dname: self.set_state(None)
        try: proxy = self.get_proxy(name)
        except: 
            print('%s.ping() ... %s not in database!!!' % (self.name,name))
            return None
        wait(.01) #this wait allows parallel threads
        try: proxy.ping()
        except:
            return None
        if not dname: self.set_state(PyTango.DevState.FAULT) #Device pings but its state is not readable (ZOMBIE)
        wait(.01) #this wait allows parallel threads
        try: 
            result = proxy.state()
            if not dname: self.set_state(result)
            return result
        except:
            if not dname: return self.state
            else: return None
            
    def init_from_db(self,db=None,load_devices=False):
        """ Gets name, classes, devices, host, level information from Tango Database. """
        self._db = db or (self._db if hasattr(self,'_db') else PyTango.Database())
        ssi = self._db.get_server_info(self.name)
        self.update_level(ssi.host,ssi.level)
        if load_devices:
            self.get_classes()
    
    def update_level(self,host,level=0):
        """ It only initializes the values, does not get values from database. """
        self.controlled = True if host or level else False
        if type(level) is str: level=level.strip()
        if self.controlled: self.host,self.level = host.split('.')[0].strip(),int(level or 0)
        else: self.host,self.level = '',0
        
    def get_classes(self,load=False):
        if not load and self._classes is not None:
            return self._classes
        devs = self._db.get_device_class_list(self.name)
        self._classes = collections.defaultdict(list)
        #print 'loading from %s server:%s'%(s,str(devs))
        for i in range(0,len(devs),2):
            klass = devs[i+1]
            self._classes[klass].append(devs[i].lower())
        return self._classes
        
    classes = property(fget=get_classes)
        
    def get_server_level(self):
        """ It returns initialized values, does not get values from database. """
        if self.controlled and self.host: return self.host,self.level
        else: return '',0
    
    def get_simple_name(self,name=''): 
        '''Returns the name of the server in the Server/Instance format.'''
        name = name or self.name
        return name if name.count('/')==1 else name.split('/',1)[1]
    
    def get_admin_name(self): 
        '''Returns the name of the server in the dserver/Server/Instance format.'''
        return 'dserver/'+self.name if self.name.count('/')==1 else self.name
    
    def get_starter_name(self):
        """Returns the starter on charge of controlling this server."""
        return 'tango/admin/%s' % self.host if self.host else None
    
    def get_device_list(self): 
        '''Returns a list of devices declared for this server.'''
        result=[]
        [result.extend(v) for c,v in self.classes.items() if c.lower()!='dserver']
        return result
    
    def get_proxy(self,device=''): 
        '''Returns a proxy to the given device; or the admin device if no device name is provided.'''
        return self.proxies.get(device or self.get_admin_name())
    
    def get_admin(self): return self.get_proxy()
    def get_device(self,device): return self.get_proxy(device)
    
    def get_all_states(self):
        """Returns a dictionary with the individual states of the inner devices."""
        result = {}
        for klass in self.classes:
            for device in self.classes[klass]:
                try:
                    result[device] = self.proxies[device].State()
                except Exception,e:
                    #self.log.warning('Unable to read %s state: %s' % (device,str(e)[:100]+'...'))
                    result[device] = None #PyTango.DevState.UNKNOWN
        return result
                
    def get_all_status(self):
        """Returns a dictionary with the individual status of the inner devices."""
        result = {}
        group = PyTango.Group(self.name)
        [group.add(dev) for dev in self.get_device_list() if not dev.startswith('dserver')]
        try:
            answers = group.command_inout('Status',[])
            for reply in answers:
                result[reply.dev_name()] = reply.get_data()
            return result
        except Exception,e:
            print 'Unable to read all Status from %s: %s' % (self.name,str(e)[:100]+'...')
            return result
    
####################################################################################################################
####################################################################################################################

class ServersDict(CaselessDict,Object):
    ''' 
    Dictionary of TServer classes indexed by server/instance names and loaded using wildcard expressions.
    Provides Jive/Astor functionality to a list of servers and allows to select/start/stop them by host, class or devices
    Its purpose is to allow generic start/stop of lists of Tango DeviceServers.
    This methods of selection provide new ways of search apart of Jive-like selection.
       
    @attention Dict keys are lower case, to get the real server name each key returns a TServer object with a .name attribute
    
    @par Usage:
    <pre>
    from fandango import Astor
    astor = Astor()
    astor.load_by_name('snap*')
    astor.keys()
      ['snapmanager/1', 'snaparchiver/1', 'snapextractor/1']
    server = astor['snaparchiver/1']
    server.get_device_list()
        ['dserver/snaparchiver/1', 'archiving/snaparchiver/1']
    astor.states()
    server.get_all_states()
        dserver/snaparchiver/1: ON
        archiving/snaparchiver/1: ON
     astor.get_device_host('archiving/snaparchiver/1')
        palantir01
     astor.stop_servers('snaparchiver/1')
     astor.stop_all_servers()
     astor.start_servers('snaparchiver/1','palantir01',wait=1000)
     astor.set_server_level('snaparchiver/1','palantir01',4)

     #Setting the polling of a device:
     server = astor['PySignalSimulator/bl11']
     for dev_name in server.get_device_list():
         dev = server.get_device(dev_name)
         attrs = dev.get_attribute_list()
         [dev.poll_attribute(attr,3000) for attr in attrs] 
     </pre>
    '''
    def __init__(self,pattern='',klass='',devs_list='',servers_list='',hosts='',loadAll=False,tango_host=''):
        ''' def __init__(self,pattern='', klass='',devs_list='',servers_list=''):
        The ServersDict can be initialized using any of the three argument lists or a wildcard for Database.get_server_list(pattern) 
        ServersDict('*') can be used to load all servers in database
        '''
        self.call__init__(CaselessDict,self)        
        
        ## proxies will keep a list of persistent device proxies
        self.proxies = ProxiesDict()
        ## db will keep a persistent link to PyTango database
        self.db = PyTango.Database() if not tango_host else PyTango.Database(*(tango_host.split(':')))
        
        self.server_names = self.keys
        self.servers = self.values
                
        if loadAll: self.load_all_servers()
        elif klass: self.load_by_exec(klass)
        elif devs_list: self.load_from_devs_list(devs_list)
        elif servers_list: self.load_from_servers_list(servers_list)
        #elif pattern: self.load_from_servers_list(self.db.get_server_list(pattern))
        elif hosts: 
            hosts = type(hosts) is str and (',' in hosts and hosts.split(',') or [hosts]) or hosts
            for h in hosts: self.load_by_host(h)
        elif pattern: self.load_by_name(pattern)
        #dict.__init__(self)
    
    ## @name Dict methods
    # @{
    
    def __arranged_key(self,key): return key if key.count('/')<=1 else key.split('/',1)[1]
    #def __getitem__(self,key): dicts.CaselessDict.__getitem__(self,self.__arranged_key(key))
    #def __setitem__(self,key,value): dicts.CaselessDict.__setitem__(self,self.__arranged_key(key),value)
    #def __delitem__(self,key): dicts.CaselessDict.__delitem__(self,self.__arranged_key(key))   
    #def __contains__(self,key): dicts.CaselessDict.__contains__(self,self.__arranged_key(key))
    #def has_key(self,key): dicts.CaselessDict.has_key(self,self.__arranged_key(key))
    #def get(self,key,def_val=None): dicts.CaselessDict.get(self,self.__arranged_key(key),def_val)
    #def pop(self,key,def_val=None): dicts.CaselessDict.pop(self,self.__arranged_key(key),def_val)
    #def setdefault(self,key,def_val=None): dicts.CaselessDict.pop(self,self.__arranged_key(key),def_val)   
    
    def __repr__(self): return self.get_report()
    def __str__(self): return self.get_report()
    
    ## @}
    
    ## @name Database access
    # @{
       
    def load_all_servers(self):
        """ It loads all device servers declared in Tango database """
        #classes = self.db.get_device_family('dserver/*')
        #for c in classes:
        #    self.load_by_exec(c)
        self.load_from_servers_list(self.db.get_server_list())
        
    def load_by_name(self,name):
        ''' Initializes the dict with all the servers matching a given name (usually the executable name or class). A list of names is also possible.'''
        if type(name) in (list,set):
            for pattern in name:
                self.load_by_name(pattern)
        else:
            if name.count('/')==2 and not name.startswith('dserver/'):
                return self.load_from_devs_list([name])
            else:
                server_name = name.replace('dserver/','')
                #self.log.info('loading by %s server_name'%server_name)
                family = server_name.split('/')[0] if '/' in server_name else server_name
                member = server_name.split('/')[1] if '/' in server_name else '*'
                servers_list = self.get_devs_from_db('dserver/%s/%s' % (family,member))
                #servers_list = [s for s in self.db.get_server_list() if fun.matchCl('%s/%s'%(family,member),s)]
                if servers_list:
                    self.load_from_servers_list([d.replace('dserver/','') for d in servers_list],check=False)
                    #self.log.info('%d servers loaded'%len(servers_list))
                    return len(servers_list)
                else:
                    #self.log.warning('No server matches with %s (family=%s).'%(server_name,family))
                    return 0
        return
        
    def load_by_host(self,host):
        """ Initializes the dict with all the servers assigned to a given host. """
        servers = self.get_db_device().DbGetHostServerList(host)
        #self.log.warning("%d servers assigned in DB to host %s: %s" % (len(servers),host,servers))
        if servers: self.load_from_servers_list(servers)
        return len(servers)
    
    def load_from_devs_list(self,devs_list):
        ''' Initializes the dict using a list of devices; a query to the database is used to identify the server for each device.  '''
        if type(devs_list) is str: devs_list = devs_list.split(',')
        if type(devs_list) not in [list,set,tuple]: devs_list = [devs_list]
        servers_list=set()
        for d in devs_list:
            devs = self.get_devs_from_db(d) if '*' in d else [d] 
            [servers_list.add(self.get_device_server(dev)) for dev in devs if dev]
        #self.log.info('Loading %d servers matching %s devices'%(len(servers_list),len(devs_list)))
        self.load_from_servers_list([s for s in servers_list if s])
    
    def load_from_servers_list(self,servers_list,check=True):
        """ Initializes the dictionary using a list of server_names like ['Exec/Instance'] """
        t0 = time.time()
        if type(servers_list) is str: servers_list = servers_list.split(',')
        if check: self.check_servers_names(servers_list)
        for s in servers_list:
            try:           
                #self.log.debug('loading from %s server'%s)
                ss=TServer(name=s,parent=self)
                ss.init_from_db(self.db)
                self[s] = ss
            except Exception,e:
                print('exception loading %s server: %s' % (s,str(e)[:100]+'...'))
                print(traceback.format_exc())
        #print 'load_from_servers_list(%d) took %f seconds' % (len(servers_list),time.time()-t0)
                    
    def check_servers_names(self,servers_list):
        """ Crosschecks the name of servers (case sensitive) with names retrieved by self.db.get_server_list() """
        all_servers = self.db.get_server_list()
        for i,s in enumerate(servers_list):
            if s not in all_servers:
                good = [v for v in all_servers if s.lower() == v.lower()]
                if good:
                    servers_list.pop(i)
                    servers_list.insert(i,good[0])
                else:
                    raise Exception('ServerNotFound_%s' % s)
        pass

    def get_db_device(self):
        """ It creates a proxy to a dbserver device declared inside sys/database/* branch of Tango database. """
        dev = [d for d in self.proxies.keys()[:] if d.lower().startswith('sys/database/')]
        if dev: return self.proxies[dev[0]]
        else:
            member = self.db.get_device_member('sys/database/*')
            if member: 
                dev = 'sys/database/%s' % (member[0])
                #self.log.info('get_db_device: creating a new proxy for %s' % dev)
                return self.proxies[dev]
            else:
                raise Exception('ServersDict_UnableToGetDBDevice')
        return
        
    def get_devs_from_db(self,dev_name):
        """ Using a PyTango.Database object returns a list of all devices matching the given name (domain*/family*/member*)"""
        #self.log.info('get_devs_from_db(%s)'%dev_name)
        if dev_name.count('/')<2: raise Exception('ThisIsNotAValidDeviceName')
        domain,family,member = dev_name.split('/',2)
        result = set()
        domains = self.db.get_device_domain(dev_name)
        for d in domains:
            families = self.db.get_device_family('%s/%s/%s'%(d,family,member))
            for f in families:
                members = self.db.get_device_member('%s/%s/%s'%(d,f,member))
                [result.add('%s/%s/%s'%(d,f,m)) for m in members]
        if not result:
            print('get_devs_from_db(%s): no matches found.'%dev_name)
        return result
            
    def get_hosts_from_db(self,filt='*'):
        """ Using a PyTango.Database proxy returns a list with all registered hosts in database. """
        return sorted(set(name.split('.')[0] for name in self.get_db_device().DbGetHostList(filt)))
    
    ## @}
    
    ## @name Get Servers / Classes
    # This methods supply information about device/classes/servers hierarchy
    # @{
                
    def get_device_server(self,device):
        """This method gets the server related to a device; if it is not in the dict gets it from the Database."""
        device = device.lower()
        for s in self.values():
            if device in s.get_device_list():
                return s.name
        #Using database because DeviceProxy.info() was terribly slow if timeout
        try:
            db_dev = self.get_db_device()
            info = db_dev.command_inout('DbImportDevice',device)
            server,host,klass = info[1][3:6]
            return server
        except Exception,e:
            print('Impossible to retrieve server for device %s: %s'%(device,str(e)[:100]+'...' ))
            #self.log.warning('Try ServersDict.load_all_servers (time consuming)')
        pass
        
    def get_device_class(self,device,server=''):
        """This method gets the server related to a device; if it is not in the dict gets it from the Database."""
        for s in [self[server]] if server else self.values():
            for klass,devs in s.classes.items():
                if device in devs:
                    return klass
        #self.log.warning('get_class_for_device doesnt provide information for servers not loaded yet.')
        return None    
            
    def get_device_host(self,device):
        """This method gets the server related to a device; if it is not in the dict gets it from the Database."""
        for s in self.values():
            if device in s.get_device_list():
                return s.host
        #self.log.warning('get_device_host doesnt provide information for servers not loaded yet.')
        return None
        
    def get_host_servers(self,host):
        """It inspects all pre-loaded servers and returns those controlled in the specified host."""
        return [ss.name for ss in self.values() if ss.host.lower() == host.lower().split('.')[0].strip()]
    
    def get_host_level_servers(self,host,level=0,controlled=True):
        """It inspects all pre-loaded servers and returns those controlled in the specified host and level."""
        return [ss.name for ss in self.values() if ss.host.lower() == host.lower().split('.')[0].strip() and (ss.level==level or (not ss.controlled and not controlled))]    
    
    def get_class_servers(self,klass):
        """This method gets the servers related to a Class."""
        result = [s.name for s in self.itervalues() if klass in s.classes];
        if not result:
            #Use the Database to get the values
            #self.log.error('Impossible to retrieve server for class %s'%(klass))
            #self.log.warning('Try ServersDict.load4class')
            pass
        return result
            
    def get_class_devices(self,klass):
        """This method gets the devices related to a Class."""
        result = set()
        [result.update(s.classes[klass]) for s in self.values() if klass in s.classes];
        if not result:
            #Use the Database to get the values
            #self.log.error('Impossible to retrieve server for class %s'%(klass))
            #self.log.warning('Try ServersDict.load4class')
            pass
        return list(result)
            
    def get_all_classes(self):
        """It returns all classes appearing in servers."""
        result = set()
        for s in self.values():
            [result.add(c) for c in s.classes.keys()]
        return list(filter(bool,result))
        
    def get_all_hosts(self):
        """It returns all hosts containing servers."""
        return list(filter(bool,set(s.host for s in self.values())))
    
    def get_all_devices(self):
        """It returns all devices contained in servers."""
        return list(chain(*[s.get_device_list() for s in self.values()]))
    
    def get_server_states(self,update=False):
        result = {}
        if update: self.update_states()
        [result.__setitem__(s.name,s.state) for s in self.values()]
        return result
    
    def get_server_tree(self):
        """ @todo It returns a dictionary with the shape {'server':{'class':'device'}} """
        result = dict.fromkeys(self.keys())
        for k in result:
            result[k] = self[k].classes
        return result
    
    def get_class_tree(self):
        """ @todo It returns a dictionary with the shape {'class':{'server':'device'}} """
        return {}
    
    def get_device_tree(self):
        """ @todo It returns a dictionary with the shape {'server':{'class':'device'}} """
        devices = set()
        classes = self.get_all_classes()
        return {}
    
    def get_host_overview(self,host=''):
        """Returns a dictionary with astor-like information
        @param host the host to display
        @return {'level':{'server':{'device':State}}}
        """
        result = {}
        if not host: 
            for h in self.get_all_hosts():
                result[h]=self.get_host_overview(h)
        else:
            for level in range(10):
                servers = self.get_host_level_servers(host,level)
                if servers: result[level]={}
                for server in servers:
                    result[level][server] = self[server].get_all_states()
            #if not result: self.log.warning('No servers has been loaded for host %s'%host)
        return result
    
    ## @}
    
    ## @name Operation methods
    # @{
       
    def states(self,servers=[],class_type='',asynch=True,timeout=60.):
        """ Updates states for given servers or the given class or all states if no class is given.
        The asynch argument controls if the state test is done in a separate thread for each server or not.
        """
        servers = servers or (class_type and self.get_class_servers(class_type)) or self.keys()
        result = dict.fromkeys(servers,None)
        try:
            if not asynch: raise ImportError
            from threads import AsynchronousFunction
            #print 'UPDATE_STATES USING ASYNCHRONOUS CALLS'
            def try_device(sdict,server):
                try:
                    #self.log.debug('try_device(%s)'% (server))
                    value = sdict[server].ping()
                    #if value is None: self.log.debug('%s.ping() ... failed!'%(server)) #LOG DOESNT WORK IN THREADS
                    #else: self.log.debug('%s.ping() ... Alive'%(server)) #LOG DOESNT WORK IN THREADS
                    return value
                except Exception,e:
                    return str(e)[:100]+'...'#str(traceback.format_exc())
            lock = threading.Lock()
            wait = threading.Event().wait
            start = time.time()
            threads = {}
            for s_name in sorted(servers):
                self.get_server_level(s_name)
                if s_name not in threads:
                    fun = lambda s=s_name: try_device(self,s)
                    #self.log.debug('try_device(%s)'%s_name)
                    threads[s_name] = AsynchronousFunction(fun)
                    threads[s_name].start()
            wait(0.1)
            
            while len(threads):
                for s_name,thread in threads.items():
                    if not thread.isAlive():
                        result[s_name]=thread.result
                        #self.log.debug('%s thread finished! (%s)' % (s_name,thread.result))
                        threads.pop(s_name)
                    wait(0.01)
                if time.time()-start > timeout: 
                    #self.log.error('Threads not finished in %s seconds!' % timeout)
                    break
                wait(0.1)
            #if not threads: self.log.info('All Threads finished!')
        except ImportError:
            for s_name in servers:
                state = self[s_name].ping()
                ##if state is None: self.log.debug( '%s.ping() ... failed!'%(admin))
                #elif state==PyTango.DevState.FAULT: self.log.debug( '%s.ping() ... ZOMBIE!!'%s_name)
                #else: self.log.debug( '%s.ping() ... Alive'%s_name)
                result[s_name]=state
        return result
    
    ##Aliases for backward compatibility
    refresh = update_states = states

    def start_servers(self,servers_list=None,host='',wait=10.):
        '''def server_Start(self,servers_list,host='',wait=3):
        Starting a list of servers or a single one in the given host(argument could be an string or a list)
        The wait parameter forces to wait several seconds until the device answers to an State command.
        wait=0 performs no wait
        '''
        if servers_list is None: 
            servers_list = sorted(self.keys(),key=(lambda s: s in self and self[s].level or 0))
        elif type(servers_list) not in [list,set,tuple]: 
            servers_list = [servers_list]
        done = False
        event = threading.Event()
        new_servers = [s for s in servers_list if s not in self]
        if new_servers:
            self.load_from_servers_list(new_servers)
            
        full_servers_list = []
        for s_name in servers_list:
            if s_name in self and str(self[s_name].ping()) == 'ON':
                print('Server %s is already running'%s_name)
                continue
            if not host: 
                try:
                    if s_name in self: self[s_name].init_from_db(self.db)
                    self[s_name].get_server_level()
                except Exception,e: 
                    print('start/stop_servers(%s): Unable to retrieve host/level information: %s'%(s_name,e))
            s_host = host or self[s_name].host or socket.gethostname()
            s_host = s_host.split('.')[0].strip() 
            s_level = s_name in self and self[s_name].level or 0
            full_servers_list.append((s_level,s_host,s_name))
            #self.log.info('Server added to list: %s'%[s_level,s_host,s_name])
            
        for level,host,s_name in sorted(full_servers_list):
            t0 = time.time()
            target = self[s_name].name
            if host:
                starter = 'tango/admin/%s'%host
            else:
                #self.log.error('Host has not been defined; server  %s cannot be started'%target)
                continue
            print( 'StartingServer '+target+' using '+starter+' ...')
            try:
                done = False
                self.proxies.get(starter).command_inout('DevStart',target)
                ct = int(wait/3)
                dp = self.proxies.get(s_name if 'dserver' in s_name else 'dserver/'+s_name)
                while ct>0:
                    event.wait(3)
                    try: 
                        dp.state()
                        ct=0
                        done=True
                    except: pass
                    ct-=1
            except Exception,e:
                print 'Exception StartingServer %s: %s'%(s_name,str(e)[:100]+'...')
                #self.log.error('Exception StartingServer %s: %s'%(s_name,str(e)[:100]+'...'))
            t1 = time.time()
            #if not done:
                #self.log.warning('The server %s Start couldnt be verified after %s seconds'%(s_name,(t1-t0)))
            #else:
                #self.log.info('The server %s Start verified after %s seconds'%(s_name,(t1-t0)))             
            if host and 'tango/admin/%s'%host in self.proxies:
                try: self.proxies['tango/admin/%s'%host].UpdateServersInfo()   
                except Exception,e: print('Unable to update %s Starter: %s'%(host,e))
        return done
            
    def start_all_servers(self): 
        return self.start_servers(sorted(self.keys(),key=(lambda s: s in self and self[s].level or 0)))
        
    #def server_StartNForClass(self,c_name,N,wait=3):
        #'''def server_StartNForClass(self,c_name,N,wait=3):Starts N servers of a given Class'''
        #servers=self.servers[c_name][:N]
        #return self.server_Start(self,servers,wait)
    
    #def server_StartALL4Classes(self,classes=None):
        #'''def server_StartALL4Classes(self,classes=None):Starts all the server for given classes or previously declared in self.ArchivingClasses'''
        #if not classes: classes = self.ArchivingClasses
        #for cl in self.classes: self.server_StartNForClass(cl,self.MAX_SERVERS_FOR_CLASS,3)
        
    def stop_servers(self,servers_list=None):
        '''def server_Stop(self,dev_name):
        Stops a list of SERVERs by sending a Kill command to the admin device server.
        If the argument is a single device it will kill all the devices running in the same server!
        '''
        done = False
        if servers_list is None: 
            servers_list = sorted(self.keys(),key=(lambda s: s in self and (-self[s].level) or 0))
        elif type(servers_list) not in [list,set,tuple]:
            servers_list = [servers_list]
        new_servers = [s for s in servers_list if s not in self]
        if new_servers:
            self.check_servers_names(new_servers)
            self.load_from_servers_list(new_servers)        
        for server_name in servers_list:
            server = self[server_name]
            if server.ping() is not None:
                #self.log.info( 'StoppingServer '+server.name)
                try:
                    server.get_proxy().command_inout('Kill')
                    done = True
                except Exception,e:
                    print('Exception in server_Stop(%s): %s'%(server.name,str(e)[:100]+'...'))
            else:
                print( 'KillingServer %s (idle or not running)' % server.name)
                try:
                    self.proxies[server.get_starter_name()].HardKillServer(server.name)
                    done = True
                except Exception,e:
                    print('Exception in server_Kill(%s): may be not running'%(server.name))
        
        hosts = [self[s].host for s in servers_list if s in self]
        for host in hosts:
            if host:
                try:
                    starter = self.proxies['tango/admin/%s'%host]
                    starter.UpdateServersInfo()
                except Exception,e:
                    print('Unable to contact with Starter in host %s: %s' % (host,e))
        return done
            
    def stop_all_servers(self): 
        return self.stop_servers(sorted(self.keys(),key=(lambda s: s in self and (-self[s].level) or 0)))    
            
    def restart_servers(self,servers_list=None,wait=5.):
        '''Performs stop_servers followed by start_servers.'''
        if servers_list is None: servers_list = self.keys()
        self.stop_servers(servers_list)
        print('Waiting %f seconds ...'%wait)
        threading.Event().wait(wait)
        self.start_servers(servers_list)
        return
        
    def kill_servers(self,servers_list):
        '''
        Kills a list of SERVERs by sending a HardKillServer to the Starter of their hosts.
        '''
        done = False
        if servers_list is None: 
            servers_list = self.keys()
        elif type(servers_list) not in [list,set,tuple]:
            servers_list = [servers_list]
        new_servers = [s for s in servers_list if s not in self]
        if new_servers:
            self.check_servers_names(new_servers)
            self.load_from_servers_list(new_servers)        
        for server_name in servers_list:
            server_name = self[server_name].name
            print( 'KillingServer '+server_name)
            try:
                host = self[server_name].host
                starter = self.proxies['tango/admin/%s'%host]
                starter.HardKillServer(server_name)
                done = True
            except Exception,e:
                print('Exception in kill_servers(%s): %s'%(server_name,str(e)[:100]+'...'))
                        
        hosts = [self[s].host for s in servers_list if s in self]
        for host in hosts:
            if host:
                try:
                    starter = self.proxies['tango/admin/%s'%host]
                    starter.UpdateServersInfo()
                except Exception,e:
                    print('Unable to contact with Starter in host %s: %s' % (host,e))
        return done        
            
    def kill_os(self,name):
        print 'in kill_os(%s)'%name
        if type(name) is not list:
            name = name.split('/')
        import subprocess
        ps = subprocess.Popen('ps a',shell=True,stdout=subprocess.PIPE)
        prev = ps
        greps = []
        for n in name:
            command = 'grep -i %s'%n
            print 'command is %s' % command
            greps.append(subprocess.Popen(command,shell=True,stdin=prev.stdout,stdout=subprocess.PIPE))
            prev = greps[-1]
        result = prev.communicate()[0]
        if result:
            proc = result.split('\n')[0] 
            print 'hard_kill: killing %s'%proc
            pid = proc.split(' ')[0]
            comm = 'kill -9 %s'%pid
            print 'hard_killed: %s' % comm
            try:
                os.system(comm)
                print 'hard_kill: Process killed'
            except Exception,e:
                print 'hard_kill: Unable to kill process, %s' % (str(e)[:100]+'...')
            return True
        else:
            print('hard_kill: Process %s not found, not killed.')
            return False


    #def StopALL(self):
        #'''def server_StopALL(self): Stop ALL servers for ALL ArchivingClasses '''
        #self.server_Check('ALL')
        #for cl in self.ArchivingClasses:
            #devs = self.servers[cl]
            #for d in devs: 
                #if self.servers_state[d]==PyTango.DevState.ON:
                    #self.server_Stop(d)
                       
    def get_report(self):
        '''def server_Report(self): The status of Servers '''
        report='The status of device servers is:\n'
        for k in sorted(self.keys()):
            report+='%s:\t%s\n'%(self[k].name,self[k].state)
        #self.log.debug(report)
        return report
        
    ## @}
    
    ## @name Server Creation methods
    # @{
    
    def get_server_level(self,server_name):
        """ It executes a DbGetServerInfo command in dbserver device. """
        
        ##commented because failed with C++ pointer exceptions!
        #name,host,mode,level = self.get_db_device().DbGetServerInfo(server_name)
        #
        ssi = self.db.get_server_info(server_name)
        host,level = ssi.host,ssi.level
        if server_name in self: self[server_name].update_level(host,level)
        return host.split('.')[0].strip(),level
        
    def set_server_level(self,server_name,host,level):
        """ It executes a DbPutServerInfo command in dbserver device. """
        print 'DUE TO export_device ISSUES THIS METHOD IS NOT SUITABLE FOR ADDING NEW SERVERS, USE devs2starter.jy INSTEAD'
        mode = 1 if host or level else 0
        host = host.split('.')[0].strip() or 'localhost' if mode else ''
        level = int(level) if level else 0
        dbserver = self.get_db_device()
        print 'ServersDict.set_server_level(%s,%s,%s)'%(server_name,host,level)
        dbserver.DbPutServerInfo([str(s) for s in (server_name,host,mode,level)])
        if server_name in self: self[server_name].update_level(host,level)
        if host: self.proxies['tango/admin/%s'%host].UpdateServersInfo()
        
    def reset_server_level(self,server_name):
        """ It sets host = '', mode = 0, level = 0 """
        host,level = self.get_server_level(server_name)
        self.set_server_level(server_name,'',None)
        if host: self.proxies['tango/admin/%s'%host].UpdateServersInfo()
    
    def create_new_server(self,server_name,class_name,devs_list):
        """It creates a new server in the database, using Jive's like input."""
        #di = PyTango.DbDevInfo()
        #di.server,di.class_name,di.name = server_name,class_name,devs_list[0]
        #self.db.add_server(server_name,[di])
        for dev in devs_list:
            di = PyTango.DbDevInfo()
            di.server,di._class,di.name = server_name,class_name,dev
            self.db.add_device(di)
            print 'added %s.%s.%s to Database' % (di.server,di._class,di.name)
        return
    ## @}
Astor = ServersDict
