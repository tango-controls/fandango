#!/usr/bin/env python
# Always prefer setuptools over distutils
import os, imp
from setuptools import setup, find_packages

__doc__ = """

To install as system package:

  python setup.py install
  
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

release = open('fandango/VERSION').read()

scripts = [
'./fandango/scripts/fandango.sh',
'./fandango/scripts/fandango.qt',
'./fandango/scripts/DynamicDS',
'./fandango/scripts/WorkerDS',
'./fandango/scripts/CopyCatDS',
'./fandango/scripts/FolderDS',
'./fandango/scripts/tango_servers',
'./fandango/scripts/tango_host',
'./fandango/scripts/tango_property',
'./fandango/scripts/tango_monitor',
]

entry_points = {
        'console_scripts': [
            #'CopyCatDS = fandango.interface.CopyCatDS:main',
            #'WorkerDS = fandango.device.WorkerDS:main',
        ],
}


setup(
    name="fandango",
    version=str(release).strip(),
    packages=find_packages(),
    description="Simplify the configuration of big Tango control systems",
    long_description="Fandango is a Python module created to simplify the "
    "configuration of big control systems; implementing the behavior of Jive "
    "(configuration) and/or Astor (deployment) tools in methods that could "
    "be called from scripts using regexp and wildcards. Fandango provides "
    "functional methods, classes and utilities to develop high-level device "
    "servers and APIs for Tango control system.",
    author="Sergi Rubio",
    author_email="srubio@cells.es",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '\
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
    ],
    platforms=[ "Linux,Windows XP/Vista/7/8" ],
    install_requires=[],
    scripts=scripts,
    entry_points=entry_points,
    include_package_data=True,
    zip_safe=False
  )
