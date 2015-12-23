#!/usr/bin/env python

import sys,traceback
class Skip(Exception): pass

#Testing fandango imports
try:
    m = 'fandango.__all__'
    print 'Loading fandango ...'
    import fandango
    print 'ReleaseNumber = %s'%str(fandango.RELEASE)
    from fandango import *
    import fandango.functional as fun
    print '\n\n'+m+': OK'
except Exception,e:
    traceback.print_exc()
    print m+': KO!'
    sys.exit(1)

#Testing fandango.$module passed as argument
a = fun.first(sys.argv[1:],'*')

try:
    m = 'fandango.functional'
    if not fun.searchCl(a,m): raise Skip()

    assert fun.searchCl('id24eu & xbpm','id24eu_XBPM_naaa',extend=True)
    assert not fun.searchCl('id24eu & !xbpm','id24eu_XBPM_naaa',extend=True)
    assert fun.searchCl('id24eu & !xbpm','id24eu_PM_naaa',extend=True)
    assert not fun.searchCl('id24eu & xbpm','id24eu_PM_naaa',extend=True)
    assert None is fun.first([],None)
    assert 1 is fun.first((i for i in range(1,3)))
    assert 2 is fun.last((i for i in range(1,3)))
    assert 0 is fun.last([],default=0)
    print m+': OK'
except Skip:pass
except Exception,e: 
    traceback.print_exc()
    print m+': KO!'
    sys.exit(1)
    
try:
    m = 'fandango.excepts'
    if not fun.searchCl(a,m): raise Skip()
    import fandango.excepts as f_excepts
    assert 1 == f_excepts.trial(lambda:1/1,lambda e:10,return_exception=True)
    assert 10 == f_excepts.trial(lambda:1/0,lambda e:10,return_exception=True)
    print m+': OK'
except Skip:pass
except Exception,e: 
    traceback.print_exc()
    print m+': KO!'
    sys.exit(1)
    
try:
    m = 'fandango.tango'
    if not fun.searchCl(a,m): raise Skip()
    import fandango.tango as f_tango
    assert isinstance(f_tango.get_proxy('sys/database/2'),fandango.tango.PyTango.DeviceProxy)
    assert isinstance(f_tango.get_proxy('sys/database/2/state'),fandango.tango.PyTango.AttributeProxy)
    assert isinstance(f_tango.TGet(),fandango.tango.PyTango.Database)
    assert isinstance(f_tango.TGet(f_tango.TGet('sys/database/*')[0]),fandango.tango.PyTango.DeviceProxy)
    assert isinstance(f_tango.TGet(f_tango.TGet('sys/database/*/st[a]te')[0]),int)
    assert f_tango.get_device_info('sys/database/2').dev_class == 'DataBase'
    assert fandango.isNaN(f_tango.TangoEval(trace=False).eval('da/do/di/du',_raise=fandango.NaN))
    assert fandango.tango.TangoEval(trace=False).eval('sys/database/2',_raise=None) in (0,None)
    print m+': OK'
except Skip:pass
except Exception,e: 
    traceback.print_exc()
    print m+': KO!'
    sys.exit(1)
    
sys.exit(0)
