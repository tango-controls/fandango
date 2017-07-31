#!/usr/bin/env python

#############################################################################
##
## project :     Tango Control System
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
provides tango utilities for fandango, like database search methods and emulated Attribute Event/Value types

This module is a light-weight set of utilities for PyTango.
Classes dedicated for device management will go to fandango.device
Methods for Astor-like management will go to fandango.servers

.. contents::

.

"""

from .defaults import *
from .methods import *

####################################################################################################################
##@name Methods for searching the database with regular expressions
#@{

#Regular Expressions
metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')
#alnum = '[a-zA-Z_\*][a-zA-Z0-9-_\*]*' #[a-zA-Z0-9-_]+ #Added wildcards
alnum = '(?:[a-zA-Z0-9-_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*'
no_alnum = '[^a-zA-Z0-9-_]'
no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
rehost = '(?:(?P<host>'+alnum+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'+'[\:][0-9]+)(?:/))' #(?:'+alnum+':[0-9]+/)?
redev = '(?P<device>'+'(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception|history))?)' #Matches attribute and extension
retango = '(?:tango://)?'+(rehost+'?')+redev+(reattr+'?')+'(?:\$?)' 

def parse_labels(text):
    if any(text.startswith(c[0]) and text.endswith(c[1]) for c in [('{','}'),('(',')'),('[',']')]):
        try:
            labels = eval(text)
            return labels
        except Exception,e:
            print 'ERROR! Unable to parse labels property: %s'%str(e)
            return []
    else:
        exprs = text.split(',')
        if all(':' in ex for ex in exprs):
            labels = [tuple(e.split(':',1)) for e in exprs]
        else:
            labels = [(e,e) for e in exprs]  
        return labels
        
def get_model_name(model):
    if isString(model): 
        m = searchCl(retango,str(model).lower())
        return m.group() if m else str(model).lower()
    try: 
        model = model.getFullName()
    except: 
        try:
            model = model.getModelName()
        except:
            print traceback.format_exc()
    return str(model).lower()
        
def parse_tango_model(name,use_tau=False,use_host=False):
    """
    {'attributename': 'state',
    'attribute': 'state',
    'devicename': 'bo01/vc/ipct-01', #Always short name
    'device': 'cts:10000/bo01/vc/ipct-01', #Will contain host if use_host or host!=TANGO_HOST
    'host': 'cts',
    'port': '10000',
    'scheme': 'tango'}
    """
    values = {'scheme':'tango'}
    values['host'],values['port'] = defhost = get_tango_host().split(':',1)
    try:
        if not use_tau or not TAU: raise Exception('NotTau')
        from taurus.core import tango as tctango
        from taurus.core import AttributeNameValidator,DeviceNameValidator
        validator = {tctango.TangoDevice:DeviceNameValidator,tctango.TangoAttribute:AttributeNameValidator}
        values.update((k,v) for k,v in validator[tctango.TangoFactory().findObjectClass(name)]().getParams(name).items() if v)
    except:
        name = str(name).replace('tango://','')
        m = re.match(fandango.tango.retango,name)
        if m:
            gd = m.groupdict()
            values['device'] = '/'.join([s for s in gd['device'].split('/') if ':' not in s])
            if gd.get('attribute'): values['attribute'] = gd['attribute']
            if gd.get('host'): values['host'],values['port'] = gd['host'].split(':',1)
    if 'device' not in values: 
        return None
    else:
        values['devicename'] = values['device']
        values['model'] = '%s:%s/%s'%(values['host'],values['port'],values['device'])
        if use_host or tuple(defhost) != (values['host'],values['port']): 
            values['device'] = values['model']
        if 'attribute' in values: 
            values['attributename'] = values['attribute']
            values['model'] = values['model']+'/'+values['attribute']

    return Struct(values)

TANGO_KEEPTIME = 60 #This variable controls how often the Tango Database will be queried

class get_all_devices(objects.SingletonMap):
    _keeptime = TANGO_KEEPTIME
    def __init__(self,exported=False,keeptime=None,host=''):
        self._all_devs = []
        self._last_call = 0
        self._exported = exported
        self._host = host and get_tango_host(host)
        if keeptime: self.set_keeptime(keeptime)
    @classmethod
    def set_keeptime(klass,keeptime):
        klass._keeptime = max(keeptime,60) #Only 1 query/minute to DB allowed
    def get_all_devs(self):
        now = time.time()
        if not self._all_devs or now>(self._last_call+self._keeptime):
            #print 'updating all_devs ...............................'
            db = get_database(self._host)
            self._all_devs = sorted(map(str.lower,
                (db.get_device_exported('*') if self._exported 
                 else db.get_device_name('*','*'))))
            self._last_call = now
        return self._all_devs
    def __new__(cls,*p,**k):
        instance = objects.SingletonMap.__new__(cls,*p,**k)
        return instance.get_all_devs()
    
def get_class_devices(klass,db=None):
    """ Returns all registered devices for a given class 
    """
    if not db:
        db = get_database()
    if isString(db): 
        db = get_database(db)
    return sorted(str(d).lower() for d in db.get_device_name('*',klass))
    
    
def get_matching_devices(expressions,limit=0,exported=False,fullname=False,trace=False):
    """ 
    Searches for devices matching expressions, if exported is True only running devices are returned 
    Tango host will be included in the matched name if fullname is True
    """
    if not isSequence(expressions): expressions = [expressions]
    defhost = get_tango_host()
    hosts = list(set((m.groups()[0] if m else None) for m in (matchCl(rehost,e) for e in expressions)))
    fullname = fullname or ':' in str(expressions) or len(hosts)>1 or hosts[0] not in (defhost,None) #Dont count slashes, as regexps may be complex
    all_devs = []
    if trace: print(hosts,fullname)
    for host in hosts:
        if host in (None,defhost):
            db_devs = get_all_devices(exported)
        else:
            print('get_matching_devices(*%s)'%host)
            odb = PyTango.Database(*host.split(':'))
            db_devs = odb.get_device_exported('*') if exported else odb.get_device_name('*','*')
        prefix = '%s/'%(host or defhost)
        all_devs.extend(prefix+d for d in db_devs)
        
    expressions = map(toRegexp,toList(expressions))
    if trace: print(expressions)
    if not fullname: all_devs = [r.split('/',1)[-1] if matchCl(rehost,r) else r for r in all_devs]
    condition = lambda d: any(matchCl("(%s/)?(%s)"%(defhost,e),d,terminate=True) for e in expressions)
    result = sorted(filter(condition,all_devs))
    return sorted(result[:limit] if limit else result)
  
def get_matching_servers(expressions,tango_host='',exported=False):
    """
    Return all servers in the given tango tango_host matching the given expressions.
    :param exported: whether servers should be running or not
    """
    expressions = toSequence(expressions)
    servers = get_database(tango_host).get_server_list()
    servers = sorted(set(s for s in servers if matchAny(expressions,s)))
    if exported:
      exported = get_all_devices(exported=True,host=tango_host)
      servers = [s for s in servers if ('dserver/'+s).lower() in exported]
    return sorted(servers)
    
def find_devices(*args,**kwargs):
    #A get_matching_devices() alias, just for backwards compatibility
    return get_matching_devices(*args,**kwargs) 
    
def get_matching_attributes(expressions,limit=0,fullname=None,trace=False):
    """ 
    Returns all matching device/attribute pairs. 
    regexp only allowed in attribute names
    :param expressions: a list of expressions like [domain_wild/family_wild/member_wild/attribute_regexp] 
    """
    attrs = []
    def_host = get_tango_host()
    matches = []
    if not isSequence(expressions): expressions = [expressions]
    fullname = any(matchCl(rehost,e) for e in expressions)
    
    for e in expressions:
        match = matchCl(retango,e,terminate=True)
        if not match:
            if '/' not in e:
                host,dev,attr = def_host,e.rsplit('/',1)[0],'state'
                #raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
            else:
                host,dev,attr = def_host,e.rsplit('/',1)[0],e.rsplit('/',1)[1]
        else:
            host,dev,attr = [d[k] for k in ('host','device','attribute') for d in (match.groupdict(),)]
            host,attr = host or def_host,attr or 'state'
        if trace: print('get_matching_attributes(%s): match:%s,host:%s,dev:%s,attr:%s'%(e,bool(match),host,dev,attr))
        matches.append((host,dev,attr))
    
    fullname = fullname or any(m[0]!=def_host for m in matches)

    for host,dev,attr in matches:

        if fullname and host not in dev:
            dev = host+'/'+dev
            
        for d in get_matching_devices(dev,exported=True,fullname=fullname):
            if matchCl(attr,'state',terminate=True):
                attrs.append(d+'/State')
            if attr.lower().strip() != 'state':
                try: 
                    ats = sorted(get_device_attributes(d,[attr]),key=str.lower)
                    attrs.extend([d+'/'+a for a in ats])
                    if limit and len(attrs)>limit: break
                except: 
                    print 'Unable to get attributes for %s'%d
                    #print traceback.format_exc()
                    
    result = sorted(set(attrs))
    return result[:limit] if limit else result
                    
def find_attributes(*args,**kwargs):
    #A get_matching_attributes() alias, just for backwards compatibility
    return get_matching_attributes(*args,**kwargs) 
    
def get_all_models(expressions,limit=1000):
    ''' 
    Customization of get_matching_attributes to be usable in Taurus widgets.
    It returns all the available Tango attributes (exported!) matching any of a list of regular expressions.
    '''
    if isinstance(expressions,str): #evaluating expressions ....
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')): expressions = list(eval(expressions))
        else: expressions = expressions.split(',')
    else:
        types = [list,tuple,dict]
        try: 
            from PyQt4 import Qt
            types.append(Qt.QStringList)
        except: pass
        if isinstance(expressions,types):
            expressions = list(str(e) for e in expressions)
    
    print 'In get_all_models(%s:"%s") ...' % (type(expressions),expressions)
    db = get_database()
    if 'SimulationDatabase' in str(type(db)): #used by TauWidgets displayable in QtDesigner
      return expressions
    return get_matching_attributes(expressions,limit)
              
#@}
########################################################################################    

########################################################################################
## Methods for managing device/attribute lists    
    
def get_domain(model):
    if model.count('/') in (2,3): return model.split['/'][0]
    else: return ''
    
def get_family(model):
    if model.count('/') in (2,3): return model.split['/'][1]
    else: return ''
    
def get_member(model):
    if model.count('/') in (2,3): return model.split['/'][2]
    else: return ''
    
def get_distinct_devices(attrs):
    """ It returns a list with the distinct device names appearing in a list """
    return sorted(list(set(a.rsplit('/',1)[0] for a in attrs)))            
            
def get_distinct_domains(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[0].split('-')[0] for a in attrs)))            

def get_distinct_families(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[1].split('-')[0] for a in attrs)))            

def get_distinct_members(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[2].split('-')[0] for a in attrs)))            

def get_distinct_attributes(attrs):
    """ It returns a list with the distinc attribute names (excluding device) appearing in a list """
    return sorted(list(set(a.rsplit('/',1)[-1] for a in attrs)))

def reduce_distinct(group1,group2):
    """ It returns a list of (device,domain,family,member,attribute) keys that appear in group1 and not in group2 """
    vals,rates = {},{}
    try:
        target = 'devices'
        k1,k2 = get_distinct_devices(group1),get_distinct_devices(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'domains'
        k1,k2 = get_distinct_domains(group1),get_distinct_domains(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'families'
        k1,k2 = get_distinct_families(group1),get_distinct_families(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'members'
        k1,k2 = get_distinct_members(group1),get_distinct_members(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'attributes'
        k1,k2 = get_distinct_attributes(group1),get_distinct_attributes(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    return first((vals[k],rates[k]) for k,r in rates.items() if r == max(rates.values()))
 
