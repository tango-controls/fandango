import os, imp

from setuptools import setup, find_packages

ReleaseNumber = type('ReleaseNumber',(tuple,),
                     {'__repr__':(lambda self:'.'.join(map(str,self)))})
release = ReleaseNumber(
    imp.load_source('changelog',os.path.join('.', 'fandango', 'CHANGES'))
    .RELEASE)

setup(
    name="fandango",
    version=str(release),
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
    include_package_data=True,
    zip_safe=False)
