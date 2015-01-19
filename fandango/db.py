#!/usr/bin/env python

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
## $Revision: 2014 $
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

"""
This package implements a simplified acces to MySQL using FriendlyDB object.

Go to http://mysql-python.sourceforge.net/MySQLdb.html for further information
"""

import time,datetime,log,traceback,sys
import MySQLdb

class FriendlyDB(log.Logger):
    """ 
    Class for managing direct access to MySQL databases using mysql-python module
    """   
    def __init__(self,db_name,host='',user='',passwd='',autocommit=True,loglevel='WARNING',use_tuples=False,default_cursor=None):
        """ Initialization of MySQL connection """
        self.call__init__(log.Logger,self.__class__.__name__,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
        self.setLogLevel(loglevel or 'WARNING')
        #def __init__(self,api,db_name,user='',passwd='', host=''):
        #if not api or not database:
            #self.error('ArchivingAPI and database are required arguments for ArchivingDB initialization!')
            #return
        #self.api=api
        self.db_name=db_name
        self.host=host
        self.use_tuples = use_tuples #It will control if data is returned in tuples or lists
        self.setUser(user,passwd)
        self.autocommit = autocommit
        self.renewMySQLconnection()
        self.default_cursor = default_cursor or MySQLdb.cursors.Cursor
        self._cursor=None
        self._recursion = 0
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
        
    def setAutocommit(self,autocommit):
        try:
            self.db.autocommit(autocommit)
            self.autocommit = autocommit
        except Exception,e:
            self.error('Unable to set MySQLdb.connection.autocommit to %s'%autocommit)
            raise Exception,e
        
        
    def renewMySQLconnection(self):
        try:
            if hasattr(self,'db') and self.db: 
                self.db.close()
                del self.db
            self.db=MySQLdb.connect(db=self.db_name,host=self.host,user=self.user,passwd=self.passwd)
            self.db.autocommit(self.autocommit)
        except Exception,e:
            self.error( 'Unable to create a MySQLdb connection to "%s"@%s.%s: %s'%(self.user,self.host,self.db_name,str(e)))
            raise Exception,e
   
    def getCursor(self,renew=True,klass=None):
        ''' 
        returns the Cursor for the database
        renew will force the creation of a new cursor object
        klass may be any of MySQLdb.cursors classes (e.g. DictCursor)
        MySQLdb.cursors.SSCursor allows to minimize mem usage in clients (although it relies memory cleanup to the server!)
        '''
        try:
            if klass in ({},dict):
                klass = MySQLdb.cursors.DictCursor
            if (renew or klass) and self._cursor: 
                if not self._recursion:
                    self._cursor.close()
                    del self._cursor
            if renew or klass or not self._cursor:
                self._cursor = self.db.cursor(self.default_cursor) if klass is None else self.db.cursor(cursorclass=klass)
            return self._cursor
        except:
            print traceback.format_exc()
            self.renewMySQLconnection()
            self._recursion += 1
            return self.getCursor(renew=True,klass=klass)
   
    def tuples2lists(self,tuples):
        ''' 
        Converts a N-D tuple to a N-D list 
        '''
        return [self.tuples2lists(t) if type(t) is tuple else t for t in tuples]
   
    def table2dicts(self,keys,table):
        ''' Converts a 2-D table and a set of keys in a list of dictionaries '''
        result = []
        for line in table:
            d={}
            [d.__setitem__(keys[i],line[i]) for i in range(min([len(keys),len(line)]))]
            result.append(d)
        return result
        
    def fetchall(self,cursor=None):
        """
        This method provides a custom replacement to cursor.fetchall() method.
        It is used to return a list instead of a big tuple; what seems to cause trouble to python garbage collector.
        """
        vals = []
        cursor = cursor or self.getCursor()
        while True:
            v = cursor.fetchone()
            if v is None: break
            vals.append(v)
        return vals
   
    def Query(self,query,export=True,asDict=False):
        ''' Executes a query directly in the database
        @param query SQL query to be executed
        @param export If it's True, it returns directly the values instead of a cursor
        @return the executed cursor, values can be retrieved by executing cursor.fetchall()
        '''
        try:
            q=self.getCursor(klass = dict if asDict else self.default_cursor)
            q.execute(query)
        except:
            self.renewMySQLconnection()
            q=self.getCursor(klass = dict if asDict else None)
            q.execute(query)
            
        if not export:
            return q
        elif asDict or not self.use_tuples:
            return self.fetchall(q) #q.fetchall()
        else:
            return self.tuples2lists(self.fetchall(q)) #q.fetchall()
   
    def Select(self,what,tables,clause='',group='',order='',limit='',distinct=False,asDict=False,trace=False):
        ''' 
        Allows to create and execute Select queries using Lists as arguments
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
       
        result = self.Query(query,True,asDict=asDict)
        if not asDict and not self.use_tuples:
            return self.tuples2lists(result)
        else:
            return result
        #else: return self.table2dicts(what.split(',') if what!='*' else [k for t in tables.split(',') for k in self.getTableCols(t)],result)
   
    def getTables(self,load=False):
        ''' Initializes the keys of the tables dictionary and returns these keys. '''
        if load or not self.tables:
            q=self.Query('show tables',False)
            [self.tables.__setitem__(t[0],[]) for t in self.tuples2lists(q.fetchall())]
        return sorted(self.tables.keys())
   
    def getTableCols(self,table):
        ''' Returns the column names for the given table, and stores these values in the tables dict. '''
        self.getTables()
        if not self.tables[table]:
            q=self.Query('describe %s'%table,False)
            [self.tables[table].append(t[0]) for t in self.tuples2lists(q.fetchall())]
        return self.tables[table]
        
    def getTableSize(self,table=''):
        table = table or '%';
        res = self.Query("select table_name,table_rows from information_schema.tables where table_schema = '%s' and table_name like '%s';"%(self.db_name,table))
        if not res: 
            return 0
        elif len(res)==1:
            return res[0][1]
        else:
            return dict(res)

    def get_all_cols(self):
        if not self.tables: self.getTables()
        for t in self.tables:
            if not self.tables[t]: 
                self.getTableCols(t)
        return
