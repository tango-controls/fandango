
"""
this module will be used to document lots of things
"""

import vacca,inspect,fandango,os

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

def generate_rest_files(path='source'):
  print '\n'*5
  print 'Writing documentation settings to %s/*rst' % (path)

  submodules = [(o,v) for o,v in vars(vacca).items()
    if inspect.ismodule(v) and v.__name__.startswith('vacca')]

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
  defs = [(get_rest_title(f,*TM2) if subtitle else '')+DEFAULT_VARIABLE%(module_name,f) 
          for f in module_vars]
  if defs:
    return '\n'+get_rest_title(title,*TM1)+'\n'.join(defs)
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
    module_doc = module_doc or module_scope.get('__doc__','') or ''
    #if not module_doc:
        #module_doc = get_rest_title(module_name,'=',double_line=True)
    #if ".. auto" not in m.__doc__:
    if module_vars:
        module_doc += get_vars_docs(module_name,module_vars)
    module_doc += get_class_docs(module_name,module_scope)
    module_doc += get_function_docs(module_name,module_scope)
    return module_doc+module_postdoc

if __name__ == '__main__':
  generate_rest_files()
    
__doc__ = get_autodoc(__name__,vars())