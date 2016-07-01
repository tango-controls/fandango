import fandango as fn
import inspect
import imp,traceback

FANDANGO_TEST = fn.dicts.SortedDict()
FANDANGO_TEST['.servers.Astor'] = (None,[],{})

class TestModule(fn.Object):
  """
  The TestModule allows generic testing of modules and classes.
  
  Specific tests will be setup using the __test__ dictionary declared on each module.
  
  on __init__.py : __test__ = ['submodule','submodule2']
  on submodule.py : 
      __test__ = {'method1':[result,callable,callable],'method2':[result,args,kwargs]}
      __test__['kmap'] = [
        {'args':[str.lower,'BCA','YZX',False],
        'result':[('A', 'x'), ('B', 'y'), ('C', 'z')]}
        ]
  
  aliases = {'hdb':'PyTangoArchiving.ArchivingAPI'}
  tests = {}
  tests['module.class.method'] = [
    (args,kwargs,result or None),
    (args,kwargs,result or None),
    ...]
  tests['PyTangoArchiving.ArchivingAPI'] = [(None,['hdb'],{'load':False})]}
  
  tc = TestModule('PyTangoArchiving',tests)
  tc.test()
  
  
  
  """
  
  def __init__(self,module,tests={}):
    self.module = module
    self.modules = fn.dicts.defaultdict_fromkey(self.load_module)
    self.objects = fn.dicts.defaultdict_fromkey(self.load_object)
    self.results = fn.dicts.defaultdict()
    self.tests = tests
    
  def get_module_callables(self,module):
    print('get_module_callables(%s)'%module)
    try:
      m = self.modules[module]
      result = set()
      l = list(getattr(m,'__test__',dir(m)))
      for o in l:
        o = o.split('.')[-1]
        if self.is_local(getattr(m,o),module):
          result.add(module+'.'+o)
    except Exception,e:
      print('get_module_callables(%s)'%module)
      traceback.print_exc()
      raise e
    return result
  
  def get_all_callables(self,module=None):
    module = module or self.module
    print 'get_all_callables(%s)'%module
    result = set()
    for s in [self.module]+list(self.get_submodules()):
      result = result.union(self.get_module_callables(s))
    return sorted(result)
    
  def get_submodules(self,module=None,nr=0):
    print('get_submodules(%s)'%module)
    try:
      module = module or self.module
      if fn.isString(module):
        m = self.load_module(module)
      else:
        m,module = module,module.__name__
      result = set()
      l = getattr(m,'__test__',dir(m))
      print m,l
      l = list(l)
      for o in l:
        o = o.split('.')[-1]
        n = getattr(m,o)
        if self.is_module(n) and module == n.__package__:
          o = module+'.'+o
          result.add(o)
          if nr<10:
            result = result.union(self.get_submodules(n,nr=nr+1))
    except Exception,e:
      print('get_submodules(%s)'%module)
      traceback.print_exc()
      raise e
    return result 
  
  @staticmethod
  def is_module(module):
    return type(module) == type(fn)

  @staticmethod
  def is_local(obj,module):
    if not fn.isCallable(obj): return False
    m = getattr(obj,'__module__',None)
    if m is not None:
      if not m or m == module:
        return True
      else:
        return False
    #class R():pass
    #classobj = type(R)
    #if isinstance(obj,R): return True
    return True

  @staticmethod
  def load_module(module):
    print('load_module(%s)'%module)
    path = module.replace('.','/')
    obj = imp.load_module(module,*imp.find_module(path))
    return obj
    
  def load_object(self,obj):
    if obj.startswith('.'): 
      obj = self.module+obj
    module,obj = obj.rsplit('.',1)
    mod = self.modules[module]
    obj = getattr(mod,obj)
    return obj
  
  def test_object(self,obj,result=None,*args,**kwargs):
    try:
      obj = self.objects[obj]
      if self.is_module(obj):
        return True
      r = obj(*args,**kwargs)
      self.results[obj] = r
      if result is None or r == result:
        print("test_object('%s : %s == %s')"%(obj,r,result))
        return r or True
    except:
      traceback.print_exc()
      return False
    
  def test(self,tests=[]):
    """
    Tests would be a list of (name,result,args,kwargs) values
    """
    print('test(',tests,')')
    try:
      tests = tests or self.tests
      if not fn.isSequence(tests): tests = [tests]
      passed = 0
      if fn.isMapping(tests):
        tests = [
          [k]+list(t if not isMapping(t) else 
            (t.get('result',None),t.get('args',[]),t.get('kwargs',[]))
            )
          for k,t in tests.items()]
      for t in tests:
        t = fn.toList(t)
        print t
        t[0] = t[0]
        t[1] = (t[1:] or [None])[0]
        t[2] = (t[2:] or [[]])[0]
        t[3] = (t[3:] or [{}])[0]
        v = self.test_object(t[0],t[1],*t[2],**t[3])
        if v: passed += 1
        self.results[t[0]] = v
        
      print('-'*80)
      for t in tests:
        v = self.results[fn.toList(t)[0]]
        print('%s testing: %s : %s' % (self.module,t,['Failed','Ok'][bool(v)]))
        
      print('%s : %d / %d tests passed'%(self.module,passed,len(tests)))
    except:
      traceback.print_exc()
      print(tests)
    return passed
  
  def test_all(self,module=None):
    module = module or self.module
    ms = self.get_submodules()
    cs = self.get_all_callables(module)
    print '%d submodules'%len(ms)
    print '%d callables'%len(cs)
    self.test(list(ms)+list(cs))
    
class TestModuleSet(TestModule):
  """
  Class that allows filtered testing on python Modules
  """
  
  def __init__(self,module,include=[],exclude=[]):
    TestModule.__init__(self,module)
    self.include = include
    self.exclude = exclude
    
  def get_submodules(self,module=None,nr=0):
    r = TestModule.get_submodules(self,module,nr)
    fs = self.include + ['!%s'%e for e in self.exclude]
    r = fn.filtersmart(r,fs)
    return r
  
  def get_module_callables(self,module=None):
    r = TestModule.get_module_callables(self,module)
    fs = self.include + ['!%s'%e for e in self.exclude]
    r = fn.filtersmart(r,fs)
    return r    
    
def main(args):
  m = args[0]
  tc = TestModule(m)
  tc.test_all()
  
if __name__ == '__main__':
  import sys
  main(sys.argv[1:])