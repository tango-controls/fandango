
"""
this module will be used to document lots of things with sphinx

to see more about sphinx generation, check fandango/scripts/generate-sphinx-docs.sh

Just do that at the end of your modules:

    from fandango.doc import get_autodoc
    __doc__ = get_autodoc(__name__,vars())

"""

## KEEP THIS MODULE CLEAN OF DEPENDENCIES!!
import inspect, os, fandango as fn
from inspect import isclass, getsource, isfunction, ismethod, getdoc

__all__ = [
    'getdoc','getsource','isclass','isfunction','ismethod',
    'get_autodoc','get_class_docs',
    'get_function_docs','get_vars_docs']      

DEFAULT_MODULE = """
%s
%s

.. automodule:: %s

"""

DEFAULT_VARIABLE = """

.. autodata:: %s.%s
   :annotation:

"""

RAW_VARIABLE = """

.. autodata:: %s.%s

"""

DEFAULT_FUNCTION = """

.. autofunction:: %s.%s

"""

DEFAULT_CLASS = """

.. autoclass:: %s.%s
   :members:

"""

TM0 = '=',True
TM1 = '=',False
TM2 = '-',False
TM3 = '~',False
TM4 = '.',False

def generate_rest_files(module,path='source'):
  import fandango
  print '\n'*5
  print 'Writing documentation settings to %s/*rst' % (path)
  if fandango.isString(module): module = fandango.loadModule(module)
  submodules = [(o,v) for o,v in vars(module).items()
    if inspect.ismodule(v) and v.__name__.startswith(module.__name__)]

  for o,v in submodules:
    filename = path+'/'+o+'.rst'
    if not os.path.isfile(filename):
      print('writing %s'%filename)
      open(filename,'w').write(DEFAULT_MODULE%(v.__name__,'='*len(v.__name__),v.__name__))
      
        
  print('\nWrite this into index.rst:\n')
  print("""
  .. toctree::
     :maxdepth: 2
     
     """+
     '\n     '.join([t[0] for t in submodules]))

def get_rest_title(string,char='=',double_line=False):
    txt = char*len(string) if double_line else ''
    txt += '\n'+string+'\n'
    txt += char*len(string)
    txt += '\n\n'
    return txt

def get_vars_docs(module_name,module_vars,title='Variables',subtitle=True):
  defs = [(get_rest_title(f,*TM3) if subtitle else '')+DEFAULT_VARIABLE%(module_name,f) 
          for f in module_vars]
  if defs:
    return '\n'+get_rest_title(title,*TM2)+'\n'.join(defs)
  else:
    return ''

def get_function_docs(module_name,module_vars,title='Functions',subtitle=True):
  functions = [(f,v) for f,v in module_vars.items() 
               if inspect.isfunction(v) and v.__module__==module_name]
  defs = [(get_rest_title(f[0],*TM3) if subtitle else '')+DEFAULT_FUNCTION%(module_name,f[0]) 
          for f in functions]
  if defs:
    return '\n'+get_rest_title(title,*TM2)+'\n'.join(defs)
  else:
    return ''

def get_class_docs(module_name,module_vars,title='Classes',subtitle=True):
  classes = [(f,v) for f,v in module_vars.items() 
             if inspect.isclass(v) and v.__module__==module_name]
  defs = [(get_rest_title(f[0],*TM3) if subtitle else '')+DEFAULT_CLASS%(module_name,f[0]) 
          for f in classes]
  if defs:
    return '\n'+get_rest_title(title,*TM2)+'\n'.join(defs)
  else:
    return ''

def get_autodoc(module_name,module_scope,module_vars=[],module_doc='',module_postdoc='\n----\n'):
    """
    from fandango import get_autodoc
    __doc__ = get_autodoc(__name__,vars())
    """
    module_doc = module_doc or module_scope.get('__doc__','') or ''
    #if not module_doc:
        #module_doc = get_rest_title(module_name,'=',double_line=True)
    #if ".. auto" not in m.__doc__:
    if module_vars:
        module_doc += get_vars_docs(module_name,module_vars)
    module_doc += get_class_docs(module_name,module_scope)
    module_doc += get_function_docs(module_name,module_scope)
    return module_doc+module_postdoc

def get_fn_autodoc(module_name,module_scope,module_vars=[],module_doc='',module_postdoc='\n----\n'):
    try:
      post = '\n----\n\n\n'+get_rest_title('raw autodoc',*TM2)+'\n'
      module_doc = module_doc or module_scope.get('__doc__','') or ''
      if not any(c in module_doc for c in (3*TM1[0],3*TM2[0],3*TM3[0])):
          module_doc = get_rest_title('Description',*TM2) + module_doc
      if not any(c in module_doc for c in ('contents::','toctree::')):
          module_doc = '.. contents::\n\n' + module_doc
      module_doc = get_autodoc(module_name,module_scope,module_vars,module_doc ,module_postdoc=post)
    except: print('failed to update %s.__doc__'%module_name)
    return module_doc

if __name__ == '__main__':
  import sys
  generate_rest_files(sys.argv[1])
    
__doc__ = get_autodoc(__name__,vars())
