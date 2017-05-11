"""
This script will regenerate recipes and devices .rst files
"""

import os

print('Updating .rst index files ...')

rheader = """
================
Fandango Recipes
================

.. toctree::
   :maxdepth: 2

"""

dheader = """
================
Fandango Devices
================

.. toctree::
   :maxdepth: 2

"""

#contents::

recipes = ('recipes',rheader,'recipes.rst')
devices = ('devices',dheader,'devices.rst')

for data in (recipes,devices):

  folder,header,filename = data
  files = [f for f in os.listdir(folder) if '.rst' in f]
  for f in files:
    header += '\n   '+folder+'/'+f.split('.rst')[0]
  header += '\n\n'
  o = open(filename,'w')
  o.write(header)
  o.close()
  
  
  
