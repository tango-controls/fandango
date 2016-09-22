#!/usr/bin/env python
# Always prefer setuptools over distutils
import os,imp
from setuptools import setup, find_packages

DS = os.getenv('DS','DynamicDS')
description = '%s Tango Device Server'%DS
package = DS

__doc__ = """
Generic Device Server setup.py file copied from fandango/scripts/setup.ds.py

To install as system package:

  python setup.py install
  
To build src package:

  python setup.py sdist
  
To install as local package, just run:

  mkdir /tmp/builds/
  python setup.py install --root=/tmp/builds
  /tmp/builds/usr/bin/$DS -? -v4

To tune some options:

  RU=/opt/control
  python setup.py egg_info --egg-base=tmp install --root=$RU/files --no-compile \
    --install-lib=lib/python/site-packages --install-scripts=ds

-------------------------------------------------------------------------------
"""

print(__doc__)

license = 'GPL-3.0'
install_requires = ['fandango',
                    'PyTango',]

## All the following defines are OPTIONAL
version = '1.0.0' #open('VERSION').read().strip()

## For setup.py located in root folder or submodules
package_dir = {
    DS: '.',
    #'DS/tools': './tools',
}
packages = package_dir.keys()

## Additional files, remember to edit MANIFEST.in to include them in sdist
package_data = {'': [
  #'VERSION',
  #'./tools/icon/*',
  #'./tools/*ui',
]}

## Launcher scripts
scripts = ['./bin/%s'%DS,]

## This option relays on DS.py having a main() method
entry_points = {
        'console_scripts': [
            '%s = %s.%s:main'%(DS,DS,DS),
        ],
}


setup(
    name=package,
    version=version,
    license=license,
    description=description,
    install_requires=install_requires,    
    packages=find_packages(),
    #packages = packages,
    #package_dir= package_dir,
    entry_points=entry_points,    
    #scripts = scripts,
    #include_package_data = True,
    #package_data = package_data    
)


