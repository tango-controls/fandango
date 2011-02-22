#!/usr/bin/env python2.5
""" if @gnuheader
#############################################################################
##
## file :       db.py
##
## description : This module simplifies database access.
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################
@endif

This package implements a simplified acces to MySQL using FriendlyDB object.

"""

import PyTango
from PyTango import *
import time
import datetime

import log
import objects
import MySQLdb,sys

class FriendlyDB(log.Logger):
    """ Class for managing the direct access to the database
    """   
    def __init__(self,db_name,host='',user='',passwd=''):
        """ Initialization of MySQL connection """
        self.call__init__(log.Logger,self.__class__.__name__,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
        self.setLogLevel('DEBUG')
        #def __init__(self,api,db_name,user='',passwd='', host=''):
        #if not api or not database:
            #self.error('ArchivingAPI and database are required arguments for ArchivingDB initialization!')
            #return
        #self.api=api
        self.db_name=db_name
        self.host=host
        self.setUser(user,passwd)
        self.renewMySQLconnection()
        self._cursor=None
        self.tables={}
        
    def __del__(self):
        if hasattr(self,'__cursor') and self._cursor: 
            self._cursor.close()
            del self._cursor
        if hasattr(self,'db') and self.db: 
            self.db.close()
            del self.db
   
    def setUser(self,user,passwd):
        """ Set User and Password to access MySQL """
        self.user=user
        self.passwd=passwd
        
    def renewMySQLconnection(self):
        try:
            if hasattr(self,'db') and self.db: 
                self.db.close()
                del self.db
            self.db=MySQLdb.connect(db=self.db_name,host=self.host,user=self.user,passwd=self.passwd)
        except Exception,e:
            self.error( 'Unable to create a MySQLdb connection to "%s"@%s.%s: %s'%(self.user,self.host,self.db_name,str(e)))
            raise Exception,e
   
    def getCursor(self,renew=True):
        ''' returns the Cursor for the database'''
        if renew and self._cursor: 
            self._cursor.close()
            del self._cursor
        if renew or not self._cursor:
            self._cursor=self.db.cursor()
        return self._cursor
   
    def tuples2lists(self,tuples):
        ''' Converts a N-D tuple to a N-D list '''
        return [self.tuples2lists(t) if type(t) is tuple else t for t in tuples]
   
    def table2dicts(self,keys,table):
        ''' Converts a 2-D table and a set of keys in a list of dictionaries '''
        result = []
        for line in table:
            d={}
            [d.__setitem__(keys[i],line[i]) for i in range(min([len(keys),len(line)]))]
            result.append(d)
        return result
   
    def Query(self,query,export=True):
        ''' Executes a query directly in the database
        @param query SQL query to be executed
        @param export If it's True, it returns directly the values instead of a cursor
        @return the executed cursor, values can be retrieved by executing cursor.fetchall()
        '''
        q=self.getCursor()
        q.execute(query)
        return not export and q or self.tuples2lists(q.fetchall())
   
    def Select(self,what,tables,clause='',group='',order='',limit='',distinct=False,asDict=False,trace=False):
        ''' This allows to create and execute Select queries using Lists as arguments
        @return depending on param asDict it returns a list or lists or a list of dictionaries with results
        '''
        if type(what) is list: what=','.join(what) if len(what)>1 else what[0]
        if type(tables) is list: tables=','.join(tables) if len(tables)>1 else tables[0]
        if type(clause) is list:
            clause=' and '.join('(%s)'%c for c in clause) if len(clause)>1 else clause[0]
        elif type(clause) is dict:
            clause1=''
            for i in range(len(clause)):
                k,v = clause.items()[i]
                clause1+= "%s like '%s'"%(k,v) if type(v) is str else '%s=%s'%(k,str(v))
                if (i+1)<len(clause): clause1+=" and "
            #' and '.join
            clause=clause1   
        if type(group) is list: group=','.join(group) if len(group)>1 else group[0]
       
        query = 'SELECT '+(distinct and ' DISTINCT ' or '') +' %s'%what
        if tables: query +=  ' FROM %s' % tables
        if clause: query += ' WHERE %s' % clause
        if group: group+= ' GROUP BY %s' % group
        if order: query += ' ORDER BY %s' % order
        if limit: query+= ' LIMIT %s' % limit
       
        q=self.Query(query,False)
        result=q.fetchall()
        if not asDict:
            return self.tuples2lists(result)
        elif what=='*':
            l = []
            [l.extend(self.getTableCols(t)) for t in tables.split(',')]
            return self.table2dicts(l,result)
        else:
            return self.table2dicts(what.split(','),result)
   
    def getTables(self):
        ''' Initializes the keys of the tables dictionary and returns these keys. '''
        if not self.tables:
            q=self.Query('show tables',False)
            [self.tables.__setitem__(t[0],[]) for t in self.tuples2lists(q.fetchall())]
        return self.tables.keys()
   
    def getTableCols(self,table):
        ''' Returns the column names for the given table, and stores these values in the tables dict. '''
        self.getTables()
        if not self.tables[table]:
            q=self.Query('describe %s'%table,False)
            [self.tables[table].append(t[0]) for t in self.tuples2lists(q.fetchall())]
        return self.tables[table]

    def get_all_cols(self):
        if not self.tables: self.getTables()
        for t in self.tables:
            if not self.tables[t]: 
                self.getTableCols(t)
        return
