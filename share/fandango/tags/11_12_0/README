---------------------------------------------------
Fandango, functional tools for Tango Control System
---------------------------------------------------

Description
===========

Fandango is a Python module created to simplify the configuration of big control systems; implementing the behavior of Jive (configuration) and/or Astor (deployment) tools in methods that could be called from scripts using regexp and wildcards.

It has been later extended with methods commonly used in some of our python API's (archiving, CCDB, alarms, vacca) or generic devices (composers, simulators, facades).

Fandango python modules provides functional methods, classes and utilities to develop high-level device servers and APIs for Tango control system.

Fandango is published using the same licenses than other TANGO projects; the license will be kept up to date in the LICENSE file.

Authors
=======

Fandango library was originally written by Sergi Rubio Manrique for the ALBA Synchrotron. Later authors will be acknowledged in the AUTHORS file

Features
========

This library provides submodules with utilities for PyTango device servers and applications written in python:

 * functional: functional programming, data format conversions, caseless regular expressions
 * tango: tango api helper methods, search/modify using regular expressions
 * dynamic: dynamic attributes, online python code evaluation
 * server: Astor-like python API
 * device: some templates for Tango device servers, TangoEval for fast "tango code" evaluation.
 * interface: device server inheritance
 * db: MySQL access
 * dicts,arrays: advanced containers, sorted/caseless list/dictionaries, .csv parsing
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

 * It requires PyTango to access Tango
 * It requires Taurus to use Tango Events.
 * Some submodules have its own dependencies (Qt,MySQL), so they are always imported within try,except clauses. 

Downloading
===========

Fandango module is available at sourceforge:

svn co https://tango-cs.svn.sourceforge.net/svnroot/tango-cs/share/fandango/trunk fandango.src

Warranty
========

see WARRANTY file



