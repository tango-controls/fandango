---------------------------------------------------
Fandango, functional tools for Tango Control System
---------------------------------------------------

Fandango ("functional" programming for Tango) is a Python library for 
developing functional and multithreaded control applications and scripts.
It is mostly (but not only) used in the scope of Tango Control System and 
PANIC Alarm System projects.

Fandango is available at:

* github: https://github.com/tango-controls/fandango/
* pypi: https://pypi.python.org/pypi/fandango

::

  pip install fandango

Description
===========

Fandango was developed to simplify the configuration of big control systems; implementing the behavior of Jive (configuration) and/or Astor (deployment) tools in methods that could be called from scripts using regexp and wildcards.

It has been later extended with methods commonly used in some of our python API's (archiving, CCDB, alarms, vacca) or generic devices (composers, simulators, facades).

Fandango python modules provides functional methods, classes and utilities to develop high-level device servers and APIs for Tango control system.

Fandango is published using the same licenses than other TANGO projects; the license will be kept up to date in the `LICENSE file <https://github.com/tango-controls/fandango/blob/documentation/LICENSE>`_

FANDANGO IS TESTED ON LINUX ONLY, WINDOWS/MAC MAY NOT BE FULLY SUPPORTED IN MASTER BRANCH

For more comprehensive documentation:

* http://pythonhosted.org/fandango/

Checkout for more updated recipes at:

* https://github.com/tango-controls/fandango/blob/documentation/doc/recipes

Authors
=======

Fandango library was originally written by Sergi Rubio Manrique for the ALBA Synchrotron. Later authors will be acknowledged in the `AUTHORS file <https://github.com/tango-controls/fandango/blob/documentation/AUTHORS>`_

Features
========

This library provides submodules with utilities for PyTango device servers and applications written in python:

 * :doc:`functional: functional programming, data format conversions, caseless regular expressions <fandango.functional>`
 * :doc:`tango : tango api helper methods, search/modify using regular expressions <fandango.tango>`
 * :doc:`dynamic : dynamic attributes, online python code evaluation <fandango.dynamic>`
 * server : Astor-like python API
 * device : some templates for Tango device servers.
 * interface: device server inheritance
 * db: MySQL access
 * :doc:`dicts,arrays: advanced containers, sorted/caseless list/dictionaries, .csv parsing <fandango.arrays>`
 * log: logging
 * objects: object templates, singletones, structs
 * threads: serialized hardware access, multiprocessing
 * linos: some linux tricks
 * web: html parsing
 * qt: some custom Qt classes, including worker-like threads.
 * ... 

Main Classes
============

 * DynamicDS/DynamicAttributes
 * ServersDict
 * TangoEval
 * ThreadDict/SingletoneWorker
 * TangoInterfaces(FullTangoInheritance) 

 
Where it is used
================

Several PyTango APIs and device servers use Fandango modules:

 * PyTangoArchiving
 * PyPLC
 * SplitterBoxDS
 * PyStateComposer
 * PySignalSimulator
 * PyAlarm
 * CSVReader
 * ... 

 
Requirements
============

 * The functional, object submodules doesn't have any dependency
 * It requires PyTango to use tango, device, dynamic and callback submodules
 * Some submodules have its own dependencies (Qt,MySQL), so they are always imported within try,except clauses. 

Downloading
===========

Fandango module is available from github (>=T9) and sourceforge (<=T9):

 git clone https://github.com/tango-controls/fandango

 svn co https://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/fandango/trunk fandango.src

Warranty
========

see `WARRANTY file <https://github.com/tango-controls/fandango/blob/documentation/WARRANTY>`_



