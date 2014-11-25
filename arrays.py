#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       arrays.py
##
## description : Module developed to manage CSV-like files and generic 2D arrays, using headers for columns
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##              Grid Class thanks to Kent Johnson kent37 at tds.net
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
"""


import csv
import sys
import operator

__all__ = ['Grid','CSVArray','tree2table']

#from excepts import *
#from ExceptionWrapper import *

class Grid(dict):
    """ Sat May 28 13:07:53 CEST 2005
    You caught me in a good mood this morning. I woke to sunshine for the first time in
    many days, that
    might have something to do with it :-)
    Here is a dict subclass that extends __getitem__ and __setitem__ to allow setting
    an entire row. I
    included extensive doctests to show you what it does.
    Note: you can write d['A',1] instead of d[('A',1)], which looks a little cleaner.
    Kent
    
    A two-dimensional array that can be accessed by row, by column, or by cell.
    Create with lists of row and column names plus any valid dict() constructorargs.
    >>> data = Grid( ['A', 'B'], [1, 2] )
    Row and column lists must not have any values in common.
    >>> data = Grid([1, 2], [2, 3])
    Traceback (most recent call last): ValueError: Row and column lists must not have any values in common
    """
    def __init__(self, rowNames, colNames, *args, **kwds):
        dict.__init__(self, *args, **kwds)
        self.rowNames = list(rowNames)
        self.colNames = list(colNames)
        # Check for no shared row and col names
        if set(rowNames).intersection(colNames):
            raise ValueError, 'Row and column lists must not have any values in common'
    def __getitem__(self, key):
        """
        Here is an example with data:
        >>> rowNames = ['A','B','C','D']
        >>> colNames = [1,'J']
        >>> rawData = [ 'cat', 3, object, 9, 4, [1], 5, 6 ]
        >>> indices = [ (row, col) for col in colNames for row in rowNames ]
        >>> data = Grid(rowNames, colNames, zip(indices, rawData))
        Data can be accessed by cell:
        >>> for i in indices:
        ...    print i, data[i]
        ('A', 1) cat
        ('B', 1) 3
        ('C', 1) <type 'object'>
        ('D', 1) 9
        ('A', 'J') 4
        ('B', 'J') [1]
        ('C', 'J') 5
        ('D', 'J') 6
        >>> data['B', 'J'] = 5
        Cell indices must contain valid row and column names:
        >>> data[3]
        Traceback (most recent call last):
        ...
        KeyError: 3
        >>> data['C', 2] = 5
        Traceback (most recent call last): ValueError: Invalid key or value: Grid[('C', 2)] = 5
        Data can be accessed by row or column index alone to set or retrieve
        an entire row or column:
        >>> print data['A']
        ['cat', 4]
        >>> print data[1]
        ['cat', 3, <type 'object'>, 9]
        >>> data['A'] = ['dog', 2]
        >>> print data['A']
        ['dog', 2]
        When setting a row or column, data must be the correct length.
        >>> data['A'] = ['dog']
        Traceback (most recent call last): ValueError: Invalid key or value: Grid['A'] = ['dog']
        """
        if self._isCellKey(key):
            return dict.__getitem__(self, key)
        elif key in self.rowNames:
            return [ dict.__getitem__(self, (key, col)) for col in self.colNames ]
        elif key in self.colNames:
            return [ dict.__getitem__(self, (row, key)) for row in self.rowNames ]
        else:
            raise KeyError, key
    def __setitem__(self, key, value):
        if self._isCellKey(key):
            return dict.__setitem__(self, key, value)
        elif key in self.rowNames and len(value) == len(self.colNames):
            for col, val in zip(self.colNames, value):
                dict.__setitem__(self, (key, col), val)
        elif key in self.colNames and len(value) == len(self.rowNames):
            for row, val in zip(self.rowNames, value):
                dict.__setitem__(self, (row, key), val)
        else:
            raise ValueError, 'Invalid key or value: Grid[%r] = %r' % (key, value)
    def _isCellKey(self, key):
        """ Is key a valid cell index? """
        return isinstance(key, tuple) \
            and len(key) == 2 \
            and key[0] in self.rowNames \
            and key[1] in self.colNames
if __name__ == '__main__':
    import doctest
    doctest.testmod()


class CSVArray:
      
    def size(self):
        return (len(self.rows)-self.xoffset, len(self.cols)-self.yoffset)
    
    #@Catched
    def __init__(self,filename=None,header=None,labels=None,comment=None):
        """
        @param[in] filename file to load
        @param[in] header row to use as column headers
        @param[in] labels column to use as row labels
        """
        self.rows = []
        self.cols = []
        self.nrows = 0
        self.ncols = 0
        self.filename = None
        self.xoffset = 0
        self.yoffset = 0
        self.comment = None
        self.dialect = None
        self.header = header
        self.labels = labels
        self.filename = filename
        if filename is not None: self.load(filename)
        self.comment=comment
        return
       
    def __str__(self):
        result = ''
        for row in self.rows:
            for n in range(self.ncols):
                result = result + str(row[n]) + ('\t' if n<self.ncols-1 else '\n')
        return result
       
    #@Catched
    def load(self,filename,comment=None,delimiter=None,prune_empty_lines=True):
        if not comment: comment=self.comment
        rows = [];cols = []; readed = [];
        
        try:
            fl=open(filename)
            flines = fl.readlines()
            if not delimiter:
                index = self.header if self.header is not None else self.xoffset
                sample = flines[index]
                print 'Dialect read from sample line (%d): %s' % (index,sample)
                self.dialect = csv.Sniffer().sniff(sample)
                print 'Dialect extracted is %s'%(str(self.dialect.__dict__))
                readed = [r for r in csv.reader(flines, self.dialect)]
            else:
                readed = [ r for r in csv.reader(flines, delimiter=delimiter)]
                #readed = csv.reader(fl, delimiter='\t')
            fl.close()
        except Exception,e:
            print 'Exception while reading %s: %s' % (filename,str(e))
        
        if readed:
            i = 0
            for row in readed:
                #Empty rows are avoided, Row is added only if not commented
                if (not prune_empty_lines) or \
                        max([len(el) for el in row] or [0]) is not 0 and \
                        (not comment or not str(row[0]).startswith(comment)):
                    row2 = [str(r).strip() for r in row] 
                    rows.append(row2)
                #Correcting initial header and offset when previous lines are being erased
                else: #The row is discarded
                    print 'removing line %d'%i
                    if i<=self.header: 
                        self.header-=1
                        print 'header updated to %d'%self.header
                    if i<=self.xoffset: 
                        self.xoffset-=1
                        print 'xoffset updated to %d'%self.xoffset
                i=i+1
            #print 'Header line is %d: %s' % (len(rows[self.header]),rows[self.header])
            ncols = max(len(row) for row in rows) if rows else 0
            for i in range(len(rows)):
                while len(rows[i])<ncols:
                    rows[i].append('')#'\t')
    
            for i in range(ncols):
                #cols.append([(lambda x,i: x[i])(row,i) for row in rows]) 
                cols.append([str(row[i]).strip() for row in rows])

        del self.rows; del self.cols
        self.rows=rows;self.cols=cols; self.nrows=len(rows); self.ncols=len(cols)
        print 'CSVArray initialized as a ',self.nrows,'x',self.ncols,' matrix'
    
    #@Catched
    def save(self,filename=None):
        if filename is not None:
            self.filename=filename
        if self.filename is None:
            return
        fl = open(self.filename,'w')
        writer = csv.writer(fl,delimiter='\t')
        writer.writerows(self.rows);
        print 'CSVArray written as a ',self.nrows,'x',self.ncols,' matrix'
        fl.close()
        
    #@Catched
    def setOffset(self,x=0,y=0):
        self.xoffset=x; self.yoffset=y;
        
    #@Catched
    def resize(self, x, y):
        """def resize(self, x(rows), y(columns)):
        TODO: This method seems quite buggy, a refactoring should be done
        """
        print 'CSVArray.resize(',x,',',y,'), actual size is (%d,%d)' % (self.nrows,self.ncols)
        if len(self.rows)!=self.nrows: 'The Size of the Array has been corrupted!'
        if len(self.cols)!=self.ncols: 'The Size of the Array has been corrupted!'
        
        if x<self.nrows:
            print 'Deleting %d rows' % (self.nrows-x)
            self.rows = self.rows[:x]
            for i in range(self.ncols):
                self.cols[i]=self.cols[i][0:x]  
        
        elif x>self.nrows:
            print 'Adding %d new rows' % (x-self.nrows)
            for i in range(x-self.nrows):
                self.rows.append(y*[''])
            for i in range(self.ncols):
                self.cols[i]=self.cols[i]+['']*(x-self.nrows)
        self.nrows = x
        if len(self.rows)!=self.nrows: 'The Size of the Array Rows has been corrupted!'
        
        if y<self.ncols:
            print 'Deleting %d columns' % (self.ncols-y)
            self.cols = self.cols[:y]
            for i in range(self.nrows):
                self.rows[i]=self.rows[i][0:y]
        elif y>self.ncols:
            print 'Adding %d new columns' % (y-self.ncols)
            for i in range(y-self.ncols):
                self.cols.append(x*[''])
            for i in range(self.nrows):
                self.rows[i]=self.rows[i] + (y-len(self.rows[i]))*['']
        self.ncols = y
        if len(self.cols)!=self.ncols: 'The Size of the Array Columns has been corrupted!'
        
        print 'CSVArray.rows dimension is now ',len(self.rows),'x',max([len(r) for r in self.rows])
        print 'CSVArray.cols dimension is now ',len(self.cols),'x',max([len(c) for c in self.cols])
        return x,y
        
    ###########################################################################
    # Methods for addressing (get/set/etc)
    ###########################################################################
      
    #@Catched
    def get(self,x=None,y=None,head=None,distinct=False,xsubset=[],ysubset=[]):
        trace=False
        """
        def get(self,x=None,y=None,head=None,distinct=False):
        """
        result = []
        #if isinstance(y,basestring): head=y
        if type(y)==type('y'): 
            head,y = y,None
        if head: y = self.colByHead(head)

        ##Getting row/column/cell using 'axxis is None' as a degree of freedom
        if y is None: #Returning a row
            x = x or 0
            if trace: print 'Getting the row ',x
            result = self.rows[self.xoffset+x][self.yoffset:]
        elif x is None: #Returning a column
            if trace: print 'Getting the column ',y
            result = self.cols[self.yoffset+y][self.xoffset:]
        else: #Returning a single Cell
            result = self.rows[self.xoffset+x][self.yoffset+y]

        if trace and xsubset: print 'using xsubset ',xsubset
        if trace and ysubset: print 'using ysubset ',ysubset
        
        if not distinct: 
            #if getting a column and theres an xsubset ... prune the rows not in xsubset
            if x is None and xsubset: result = [result[i] for i in xsubset]
            if y is None and ysubset: result = [result[i] for i in ysubset]
            return result

        if trace: print 'Getting only distinct values from ',['%d:%s'%(i,result[i]) for i in range(len(result))]
        ## DISTINCT VALUES, returns a dictionary with the distinct values (initialized with first match)
        #values={result[0]:[0]} #Doesn't add self.xoffset here, it has been done before!
        values={}
        #for i in range(1,len(result)):
        for i in range(len(result)):
            #If we are returning a column, rows must be in the subset
            if x is None and xsubset and i not in xsubset: continue
            #If we are returning a row, columns must be in the subset
            if y is None and ysubset and i not in ysubset: continue
            if result[i] not in values.keys():
                values[result[i]]=[i]
            else:
                values[result[i]].append(i)
        if trace: print 'Values are ',values
        return values
    
    def getd(self,x):
        """This method returns a line as a dictionary using the headers as keys"""
        d = {}
        Hrow = self.rows[self.header or 0]
        line = self.get(x=x)
        for i in range(len(line)): d[Hrow[i]]=line[i]
        return d
    
    def Labeled(self,fun):
        def labelator(self,*args,**kwargs):
            return self.fun(*args,**kwargs)
        return labelator
    
    #@Labeled(self)
    def find(self,values):
        #Values is a dict that contains {Column:regexp,Column2:regexp2,...}
        #The command will return all the matching rows for all columns given
        pass
    
    #@Catched   
    def set(self,x,y,val):
        """
        def set(self,x,y,val):
        """
        #print 'CSVArray.set(x=',x,',y=',y,',val=',val,',xoffset=',self.xoffset,',yoffset=',self.yoffset,')'
        val = val if type(val) in [int,long,float] else (val or '')
        if x is None or x<0:
           #Setting a column
           if len(val)>self.nrows or len(val)<0: 
               raise Exception('CSVArray.set(column) ... wrong size of column')
           for i,v in enumerate(val):
               self.cols[y][i]=v
               self.rows[i][y]=v;
        elif y is None or y<0:
            #Setting an entire row
            if len(val)>self.ncols or len(val)<0: 
                raise Exception('CSVArray.set(row) ... wrong size of row')           
            for i,v in enumerate(val):
               self.rows[x][i]=v
               self.cols[i][x]=v;             
        else:
            self.rows[self.xoffset+x][self.yoffset+y]=val
            self.cols[self.yoffset+y][self.xoffset+x]=val
    
    def setRow(self,x,val):
        self.set(x,None,val)
    def setColumn(self,y,val):
        self.set(None,y,val)

    def getHeaders(self):
        index = self.header or 0
        return self.rows[index] if index<len(self.rows) else []

    #@Catched
    def colByHead(self,head,header=None):
        """
        Get the index of the column headed by 'head'
        """
        if not head: return head
        self.header = self.header or 0
        head = head.strip()
        if header is None:
            Hrow = self.rows[self.header]
        else:
            Hrow = self.rows[header]
        if head not in Hrow:
            print 'colByHead: Head="',head,'" does not exist in: %s'%Hrow
            return None
        return Hrow.index(head)
        
    ###########################################################################
    # Methods for conversion from/to Dictionary Trees
    ###########################################################################
        
    #@Catched
    def fill(self,y=None,head=None,previous=[]):
        """Fill all the empty cells in a column with the last value introduced on it
        By default this method adds new values to a column only when the previous column remains unchanged
        To force all the values to be filled set previous=True
        """
        #print 'CSVArray.fill(%s,%s,%s)'%tuple(str(s) for s in [y,head,previous])
        if type(y) is str: head,y =  y,None
        c = y if y in range(self.ncols+1) else self.colByHead(head)
        column = self.get(y=c)
        last = ''
        previous = (type(previous) is list and previous) or (previous and len(column)*[previous]) or (c and self.get(y=c-1)) or []
        for r in range(len(column)):
            if r and column[r]=='' and (not previous or previous[r-1]==previous[r]):
                self.set(r,c,last)
            else: last = column[r]

    #@Catched
    def expandAll(self):
        for c in range(self.ncols): self.fill(y=c)
        return self
        
    def getAsTree(self,root=0,xsubset=[],lastbranch=None):
        """
        This method returns the content of the array as recursive dicts
        It will produce the right output only if the array has been filled before!
        [self.fill(head=h) for h in self.getHeaders()]
        
        headers={dict with headers as keys}
        for h in headers: fill with distinct keys on each column
        get the keys on first column
            for each key, get the distinct keys in the next column matching lines
                for each key, get the distinct keys in the next column matching lines       
        """
        if lastbranch is None: lastbranch=self.ncols
        elif type(lastbranch) is str: lastbranch=self.colByHead(lastbranch)
            
        klines=self.get(y=root,distinct=True,xsubset=xsubset)
        if root+1>=self.ncols: #Last column
            return dict.fromkeys(klines.keys(),{})
        elif len(klines)==1 and root>lastbranch: #Return resting columns in a single line
            return self.get(x=klines.values()[0][0],ysubset=range(root,self.ncols))
        else:
            tree={}
            for k in klines.keys():
                if not k: 
                    #print 'WARNING! %s has not been properly filled' % k
                    pass
                else:
                    #if root+1==self.ncols: tree[k]=self.get(y=root+1,xsubset=klines[k])
                    tree[k]=self.getAsTree(root=root+1,xsubset=klines[k],lastbranch=lastbranch)
            return tree
            
    def updateFromTree(self,tree):
        """
        This method takes a dictionary of type {level0:{level1:{level2:{}}}}
        and converts it into a grid like level0 \t level1 \t level2
        WARNING!: This method deletes the actual content of the array!
        """
        print 'WARNING!: updateFromTree deletes the actual content of the array!'
        table = tree2table(tree)
        self.resize(1,1)
        self.resize(len(table),max(len(line) for line in table))
        [self.setRow(i,table[i]) for i in range(len(table))]

    #def printTree(self,level=None,depth=0):
        #if not level: level=self.getAsTree()
        #MAX_DEPTH=10
        #if depth>MAX_DEPTH or not hasattr(level,'items'): return
        #for k,l in level.iteritems():
            #if operator.isMappingType(l):
                #print (' '*depth),k,'=',l.keys()
                #self.printTree(l,depth+1)
            #else:
                #print (' '*depth),k,'=',l
                
    def printArray(self):
        for r in range(len(self.rows)):
            print r,':','\t'.join([str(e) for e in self.rows[r]])
        #for r in range(len(self.rows)):
            #print r,':','\t'.join([self.cols[c][r] for c in range(len(self.cols))])
    
    pass #END OF CSVARRAY

def tree2table(tree):
    """
    {A:{AA:{1:{}},AB:{2:{}}},B:{BA:{3:{}},BB:{4:{}}}}
    should be represented like
    A    AA 1
        AB    2
    B    BA 3
        BB    4
    """
    from collections import deque
    result = []
    for k in sorted(tree.keys()): #K=AA; v = {1:{}}
        v = tree[k]
        #print '%s:%s' % (k,v)
        if not v:
            #print '%s is empty' % k
            result.append([k])
        else:
            _lines = tree2table(v)
            #print 'tree2table(%s): tree2table(v) returned: %s' % (k,_lines)
            lines = [deque(dq) for dq in _lines]
            lines[0].appendleft(k)
            [line.appendleft('') for line in lines[1:]]
            [result.append(list(line)) for line in lines]
    #print 'result: tree2table(tree) returned: %s' % (result)
    return result