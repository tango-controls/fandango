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

from .methods import *
from .search import *

##############################################################################################################
## Tango formula evaluation

def get_attribute_time(value):
    #Gets epoch for a Tango value
    t = value.time
    if hasattr(t,'tv_sec'):
        t = t.tv_sec + 1e-6*t.tv_usec
    return t

class TangoedValue(object):
  
    def init_values(self,*args,**kwargs):
        self.value = self.type = None
        self.time = 0
        self.name = self.device = self.host = ''
        self.domain = self.family = self.member = ''
        self.quality = ATTR_INVALID
        self.set_quality_flags()
        return self
        
    def set_quality_flags(self,quality=None):
        quality = quality or self.quality
        self.ALARM = quality==ATTR_ALARM
        self.WARNING = quality in (ATTR_ALARM,ATTR_WARNING)
        self.INVALID = quality==ATTR_INVALID
        self.VALID = quality!=ATTR_INVALID
        self.OK = quality==ATTR_VALID

def getTangoValue(obj,device=None):
    """
    This method may be used to return objects from read_attribute or FIND() 
    that are still computable and keep quality/time members
    try to avoid spectrums.; this method doesn't work for numpy arrays 
    so I have to convert them to less efficient lists.
    """
    try:
        p = parse_tango_model(obj if type(obj) is str else (device or ''))
        if p: device,host = p['device'],p['host']+':'+p['port']
        else: host = get_tango_host()
        if type(obj) is str:
            obj = AttributeProxy(obj).read()
        
        if hasattr(obj,'quality'):
            value = obj.value
            w_value = getattr(obj,'w_value',None)
            quality = obj.quality
            t = get_attribute_time(obj)
            name = obj.name
            ty = obj.type
            
            if isSequence(value): 
                value = (value.tolist() if hasattr(value,'tolist') 
                         else list(value))
        else:
            value,quality = obj,AttrQuality.ATTR_VALID
            t,name,ty = time.time(),'',type(obj)
            w_value = None
            
        try: domain,family,member = device.split('/')[-3:]
        except: domain,family,member = '','',''
            
        Type = type(value)
        Type = Type if (Type not in (bool,None,type(None)) \
                        and ty!=CmdArgType.DevState) else int
        nt = type('tangoed_'+Type.__name__,(Type,TangoedValue),{})
        o = nt(value or 0)
        [setattr(o,k,v) for k,v in (('name',name),('type',ty),
            ('value',value),('quality',quality),('time',t),
            ('device',device),('host',host),('w_value',w_value),
            ('domain',domain),('family',family),('member',member),
            )]
        o.set_quality_flags()
        return o
    except:
        print traceback.format_exc()
        return obj
            
    def __repr__(self):
        return 'v(%s)'%(self.value)

FAILED_VALUE = None

class TangoEval(object):
    """ 
    Class for Tango formula evaluation; used by Panic-like formulas
    
    ::
    
      example:
        te = fandango.TangoEval(cache=3)
        te.eval('test/sim/test-00/A * test/sim/test-00/S.delta')
        Out: 2.6307095848792521 #A value multiplied by delta of S 
                                in its last 3 values
    
    Attributes in the formulas may be (it is recommended to insert spaces 
    between attribute names and operators):
    THIS REGULAR EXPRESSIONS DOES NOT MATCH THE HOST IN THE FORMULA!!!; IT 
    IS TAKEN AS PART OF THE DEVICE NAME!!
    
    .. code::
    
        dom/fam/memb/attrib >= V1 #Will evaluate the attribute value
        d/f/m/a1 > V2 and d/f/m/a2 == V3 #Comparing 2 attributes
        d/f/m.quality != QALARM #Using attribute quality
        d/f/m/State == UNKNOWN #States can be compared directly
        d/f/m/A.exception #True if exception occurred
        d/f/m/A.time #Attribute value time
        d/f/m/A.value #Explicit value
        d/f/m/A.delta #Increase/decrease of the value since the first 
                        value in cache (if cache and cache_depth are set)
        d/f/m/A.all #Instead of just value will return an AttributeValue object 
    
    All tango-like variables are parsed. TangoEval.macros can be used to do 
    regexp-based substitution. By default FIND(regexp) will be replaced 
    by a list of matching attributes.
    
        FIND([a-zA-Z0-9\/].*) macro allows to get any attribute matching 
        a regular expression
        Any variable in _locals is evaluated or explicitly replaced in 
        the formula if matches $(); e.g. FIND($(VARNAME)/*/*)
        T() < T('YYYY/MM/DD hh:mm') allow to compare actual time with any time
        
    :use_events: will manage events using the callbacks.EventSource object. 
        It will redirect all events to TangoEval.eventReceived method. 
        If an event_hook callback is passed as argument, both TangoEval 
        object and result of eval will be sent to it.
    
    eval() will be triggered by events only if event_hook is True or a callable
    
    """

    ## FIND( optional quotes and whatever is not ')' )
    FIND_EXP = 'FIND\(((?:[ \'\"])?[^)]*(?:[ \'\"])?)\)' 
    
    operators = '[><=][=>]?|and|or|in|not in|not'

    # Using regexps as loaded from fandango.tango.defaults
    alnumdot = alnum # as defined in fandango.tango.defaults
    alnum = '[a-zA-Z0-9-_]+'  # A most restrictive version without ._-
    no_alnum = no_alnum
    no_quotes = no_quotes
    
    #THIS REGULAR EXPRESSIONS DOES NOT MATCH THE HOST IN THE FORMULA!!!; 
    #IT IS TAKEN AS PART OF THE DEVICE NAME!!
    #It matches a device name
    redev = ('(?P<device>(?:'+alnumdot+':[0-9]+/{1,2})?(?:'
                +'/'.join([alnumdot]*3)+'))')
    
    #Matches attribute and extension
    rewhat = '(?:(?:\\.)(?P<what>quality|time|value|exception|delta|all|'\
              'hist|ALARM|WARNING|VALID|INVALID|OK))?'
    reattr = '(?:/(?P<attribute>'+alnum+')'+rewhat+')?' 
    #retango = '(?:tango://)?'+(rehost+'?')+
    retango = redev+reattr #+'(?!/)'
    #Excludes attr_names between quotes, accepts value type methods    
    regexp = no_quotes + retango + no_quotes.replace('\.','').replace(':','=')
    
    def __init__(self,formula='',launch=True,timeout=1000,keeptime=100,
              trace=False, proxies=None, attributes=None, cache=0, 
              use_events = False, event_hook = None,**kwargs):
        #print(self.regexp)
        self.formula = formula
        self.source = ''
        self.variables = []
        self.timeout = timeout
        self.keeptime = keeptime
        
        self.proxies = proxies or ProxiesDict() #use_tau=self.use_tau)
        self.use_events = use_events or kwargs.get('use_tau',False)
        self.event_hook = event_hook
        if attributes:
          self.attributes = attributes
        else:
          from fandango.callbacks import CachedAttributeProxy,EventListener
          if self.use_events:
            proxy = (lambda a: CachedAttributeProxy(a,keeptime=self.keeptime,
                              use_events=self.use_events,listeners=[self]))
          else:
            proxy = (lambda a: CachedAttributeProxy(a,keeptime=self.keeptime))
            
          self.attributes = dicts.CaselessDefaultDict(proxy)

        #Keeps last values for each variable
        self.previous = dicts.CaselessDict() 
        #Keeps values from the last eval execution only
        self.last = dicts.CaselessDict() 
        self.cache_depth = cache
        self.cache = dicts.CaselessDefaultDict(lambda k:list()) \
                        if self.cache_depth else None#Keeps [cache]
        self.result = None
        self.macros = [('FIND(%s)',self.FIND_EXP,self.find_macro)]
        
        self._trace = trace
        
        self.init_locals()
        
        if self.formula and launch: 
            self.eval()
            if not self._trace: 
                print('TangoEval: result = %s' % self.result)
        return
    
    def init_locals(self):
        self._defaults = dict(
            [(str(v),v) for v in DevState.values.values()]+
            [(str(q),q) for q in AttrQuality.values.values()]
            )

        self._defaults['T'] = str2time
        self._defaults['str2time'] = str2time
        self._defaults['time'] = time
        self._defaults['NOW'] = time.time
        #self._locals['now'] = time.time() #Updated at execution time
        
        # Internal objects
        self._defaults['DEVICES'] = self.proxies
        self._defaults['DEV'] = lambda x:self.proxies[x]
        self._defaults['CACHE'] = self.cache
        self._defaults['PREV'] = self.previous
        
        # Tango DB methods
        self._defaults['NAMES'] = lambda x: get_matching_attributes(x) \
                        if parse_tango_model(x).get('attribute') \
                        else get_matching_devices(x)
        self._defaults['CHECK'] = lambda x: read_attribute(x) \
                        if parse_tango_model(x).get('attribute') \
                        else check_device(x)
        self._defaults['READ'] = self.read_attribute
        #For ComposerDS syntax compatibility
        self._defaults['ATTR'] = self._defaults['XATTR'] = self.read_attribute
            
        self._defaults.update((k,v) for k,v in {'get_domain':get_domain,
                                          'get_family':get_family,
                                          'get_member':get_member,
                                          'parse':parse_tango_model
                                          }.items())
        
        #Updating Not allowed models
        #self._defaults.update((k,None) for k in ('os','sys',)) 
        
        #Having 2 dictionaries to reload defaults when needed
        self._locals = dict(self._defaults)    
            
    def trace(self,msg):
        if self._trace: print('TangoEval: %s'%str(msg))
        
    def keys(self):
        return self._locals.keys()
    
    def getter(self,key):
        return self._locals.get(key,None)
    
    def setter(self,key,value):
        self._locals[key] = value
        
    def set_timeout(self,timeout):
        self.timeout = int(timeout)
        self.trace('timeout: %s'%timeout)
        
    def find_macro(self,target):
        """
        Gets a match of FIND_EXP and applies get_matching_attributes 
        to the expresion found.
        """
        exp = target.replace('"','').replace("'",'').strip()
        exp,sep,what = exp.partition('.')
        res = str(sorted(d.lower()+sep+what 
                for d in get_matching_attributes(exp,trace=self._trace)))
        return res.replace('"','').replace("'",'')
    
    def add_macro(self,macro_name,macro_expression,macro_function):
        """
        Add a new macro to be parsed by parse_formula. 
        It will apply macro_function to the target found by macro_expression; 
        the result will later replace macro_name%target
        
        e.g: self.add_macro('FIND(%s)',self.FIND_EXP,self.find_macro) 
            #where FIND_EXP = 'FIND\(((?:[ \'\"])?[^)]*(?:[ \'\"])?)\)'
        """
        self.macros.insert(0,(macro_name,macro_expression,macro_function))
        
    def parse_formula(self,formula,_locals=None):
        """ 
        This method just removes comments and applies self.macros 
        (e.g FIND()) searches in the formula; 
        In this method there is no tango check, neither value replacement 
        """
        _locals = _locals or {}
        _locals.update(self._locals)
        if '#' in formula:
            formula = formula.split('#',1)[0]
        if ':' in formula and not re.match('^',redev):
            tag,formula = formula.split(':',1)
        #explicit replacement of env variables if $() used            
        if _locals and '$(' in formula: 
            for l,v in _locals.items():
                formula = formula.replace('$(%s)'%str(l),str(v))
        for macro_name,macro_exp,macro_fun in self.macros:
            matches = re.findall(macro_exp,formula)
            for match in matches:
                res = macro_fun(match)
                formula = formula.replace(macro_name%match,res)
                self.trace('TangoEval.parse_formula: Replacing %s with %s'%(macro_name%match,res))
        return formula
        
    def parse_variables(self,formula,_locals=None,parsed=False):
        ''' This method parses attributes declarated in formulas with the following formats:
        TAG1: dom/fam/memb/attrib >= V1 #A comment
        TAG2: d/f/m/a1 > V2 and d/f/m/a2 == V3
        TAG3: d/f/m.quality != QALARM #Another comment
        TAG4: d/f/m/State ##A description?, Why not
        :return: 
            - a None value if the alarm is not parsable
            - a list of (device,attribute,value/time/quality) tuples
        '''            

        #self.trace( regexp)
        idev,iattr,ival = 0,1,2 #indexes of the expression matching device,attribute and value
        
        if not parsed: formula = self.parse_formula(formula,_locals)
        
        ##@var all_vars list of tuples with (device,/attribute) name matches
        #self.variables = [(s[idev],s[iattr],s[ival] or 'value') for s in re.findall(regexp,formula) if s[idev]]
        variables = [s for s in re.findall(self.regexp,formula)]
        self.trace('parse_variables(...): %s'%(variables))
        return variables
        
    def read_attribute(self,device,attribute='',what='',_raise=True, timeout=None):
        """
        Executes a read_attribute and returns the value requested
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        """
        timeout = timeout or self.timeout
        self.trace('read_attribute(%s,%s,%s,%s,%s)'%(device,attribute,what,_raise,timeout))
        if not attribute:
          if device.split(':')[-1].count('/')>2:
            device,attribute = device.rsplit('/',1)
          else:
            attribute = 'state'
        aname = (device+'/'+attribute).lower()
        try:
            if aname not in self.attributes:
                dp = self.proxies[device]
                try: dp.set_timeout_millis(timeout)
                except: self.trace('unable to set %s proxy timeout to %s ms: %s'%(device,timeout,except2str()))
                dp.ping()
                # Disabled because we want DevFailed to be triggered
                #attr_list = [a.name.lower()  for a in dp.attribute_list_query()]
                #if attribute.lower() not in attr_list: #raise Exception,'TangoEval_AttributeDoesntExist_%s'%attribute
            value = self.attributes[aname].read()
            if self.cache_depth and not any(get_attribute_time(v)==get_attribute_time(value) for v in self.cache[aname]):
                while len(self.cache[aname])>=self.cache_depth: self.cache[aname].pop(-1)
                self.cache[aname].insert(0,value)
            if what == 'all': 
                if self.cache_depth:
                    try: setattr(value,'delta',self.get_delta(aname))
                    except: pass
                setattr(value,'exception',isinstance(getattr(value,'value',None),PyTango.DevFailed))
            elif what in ('value',''): 
                value = getTangoValue(value,device=device)
            elif what == 'w_value': value = getattr(value,'w_value',None)
            elif what == 'time': value = get_attribute_time(value)
            elif what == 'exception': value = isinstance(getattr(value,'value',None),PyTango.DevFailed)
            elif what == 'delta': value = self.get_delta(aname)
            else: value = getattr(value,what)
            self.trace('read_attribute(%s/%s.%s) => %s'%(device,attribute,what,value))
        except Exception,e:
            if isinstance(e,PyTango.DevFailed) and what=='exception':
                return e
            elif _raise and not isNaN(_raise):
                raise e
            self.trace('TangoEval: ERROR(%s.%s)! Unable to get %s for attribute %s/%s: %s' % (type(e),_raise,what,device,attribute,except2str(e)))
            #self.trace(traceback.format_exc())
            value = _raise
        return value
                
    def update_locals(self,dct=None):
        if dct:
            if not hasattr(dct,'keys'): dct = dict(dct)
            self._locals.update(dct)
            self.trace('update_locals(%s)'%shortstr(dct.keys()))
        self._locals['now'] = self._locals['t'] = time.time()
        self._locals['formula'] = self.formula
        return self._locals
            
    def parse_tag(self,target,wildcard='_'):
        return wildcard+target.replace('/',wildcard).replace('-',wildcard).replace('.',wildcard).replace(':',wildcard).replace('_',wildcard).lower()
    
    def get_delta(self,target):
        """
        target = (device+'/'+attribute).lower() ; returns difference between first and last cached value
        """
        if self.cache and target in self.cache:
            cache = self.cache.get(target)
        else:
            var_name = self.parse_tag(target)
            if var_name in self.previous:
                device,attribute = self.parse_variables(target)[0][:2]
                cache = [self.read_attribute(device,attribute,'all'),self.previous[var_name]]
            else:
                cache = []
        delta = 0 if not cache else (cache[0].value-cache[-1].value)
        self.trace('get_delta(%s); cache[%d] = %s; delta = %s' % (target,len(cache),[v.value for v in cache],delta))
        return delta
      
    def eventReceived(self, src, type_, value):
        """ 
        Method to implement the event notification
        Source will be an object, type a PyTango EventType, evt_value an AttrValue
        Regarding PANIC, the eventReceived hook must be in the PanicAPI, not here
        """
        try:
          self.trace('eventReceived: %s.%s'%(src,type_))
          if self.event_hook:
            if type_ in ('change','archive','quality','user_event','periodic'):
              if 1e3*(now()-self._locals['now'])>self.keeptime:
                r = self.eval()
                if isCallable(self.event_hook):
                  self.event_hook(self,r)
        except:
          self.trace(traceback.format_exc())
    
    def eval(self,formula=None,previous=None,_locals=None ,_raise=FAILED_VALUE):
        ''' 
        Evaluates the given formula.
        Previous can be used to add extra local values, or predefined values for attributes ({'a/b/c/d':1} that would override its reading
        Any variable in locals is evaluated or explicitly replaced in the formula if appearing with brackets (e.g. FIND({VARNAME}/*/*))
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        '''
        self.formula = (formula or self.formula).strip()
        previous = previous or {}
        _locals = _locals or {}

        for x in ['or','and','not','in','is','now']: #Check for case-dependent operators
            self.formula = self.formula.replace(' '+x.upper()+' ',' '+x+' ')
            if self.formula.startswith(x.upper()+' '):
              self.formula = x+self.formula[len(x):]

        self.formula = self.formula.replace(' || ',' or ')
        self.formula = self.formula.replace(' && ',' and ')
        self.update_locals(_locals)
        #self.previous.update(previous or {}) #<<< Values passed as eval locals are persistent, do we really want that?!?
        
        self.formula = self.parse_formula(self.formula) #Replacement of FIND(...), env variables and comments.
        variables = self.parse_variables(self.formula,parsed=True) #Extract the list of tango variables
        self.trace('>'*80)
        self.trace('eval(_raise=%s): variables in formula are %s' % (_raise,variables))
        self.source = self.formula #It will be modified on each iteration
        targets = [(device + (attribute and '/%s'%attribute) + (what and '.%s'%what),device,attribute,what) for device,attribute,what in variables]
        self.last.clear()
        ## NOTE!: It is very important to keep the same order in which expressions were extracted
        for target,device,attribute,what in targets: 
            var_name = self.parse_tag(target)
            #self.trace('\t%s => %s'%(target,var_name))
            try:
                #Reading or Overriding attribute value, if overriden value will not be kept for future iterations
                r = _raise if not any(d==device and a==attribute and w=='exception' for t,d,a,w in targets) else FAILED_VALUE
                if target in previous:
                    self.previous[var_name] = previous.get(target)
                else:
                    self.previous[var_name] = self.read_attribute(device,attribute or 'State',what,_raise=r)
                #Remove attr/name, keep only the variable tag
                self.previous.pop(target,None)  
                #Every occurrence of the attribute is managed separately, read_attribute already uses caches within polling intervals
                self.source = self.source.replace(target,var_name,1) 
                #Used from alarm messages
                self.last[target] = self.previous[var_name] 
            except Exception,e:
                self.trace('eval(r=%s): Unable to obtain %s values'%(r,target))
                self.last[target] = e
                raise e
        self.trace('formula = %s' % (self.source))
        self.trace('previous.items():\n'+'\n'.join(str((str(k),str(i))) for k,i in self.previous.items()))
        self.result = eval(self.source,dict(self.previous),self._locals)
        self.trace('result = %s' % str(self.result))
        return self.result
    pass


#######################################################################################

class DeprecatedCachedAttributeProxy(PyTango.AttributeProxy):
    """ 
    This subklass of AttributeProxy keeps the last read value for a fixed keeptime (in milliseconds).
    DEPRECATED: Use callbacks.EventSource instead, AttributeProxy is not as well supported as DeviceProxy
    
    It is used to avoid abusive attribute access from composers (fandango.dynamic) or alarm servers (fandango.tango)
    In comparison to AttributeValue, it can be used for attribute configuration setup (including polling/events)
    And it is WRITABLE!!
    
    This class does not implement any kind of Event management, this will be done by EventSource subclass instead.
    """
    def __init__(self,name,keeptime=1000.,fake=False):
        self.keeptime = keeptime
        self.last_read_value = None
        self.last_read_time = 0
        self.fake = fake
        if not fake: PyTango.AttributeProxy.__init__(self,name)
        else: self.name = name
        
    def set_cache(self,value,t=None):
        #"""
        #set_cache and fake are used by PyAlarm.update_locals
        #used to emulate alarm state reading from other devices
        #"""
        self.last_read_time = t or time.time()
        self.last_read_value = hasattr(value,'value') and value or fakeAttributeValue('',value)
    
    def read(self,cache=True):
        now = time.time()
        if not cache or (now-self.last_read_time)>(self.keeptime/1e3):
            self.last_read_time = now
            try:
                self.last_read_value = None if self.fake else PyTango.AttributeProxy.read(self)
            except Exception,e:
                self.last_read_value = e
        if isinstance(self.last_read_value,Exception): raise self.last_read_value
        else: return self.last_read_value

