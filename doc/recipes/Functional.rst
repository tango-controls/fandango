==================
Functional Recipes
==================

For using all the useful functional programming methods of fandango see:

:doc:`fandango.functional`

These page just describes other functional tools from other submodules.


Other tools/classes
===================
  
  
Use CSVArray to turn a .csv into a dictionary
---------------------------------------------

::

  cat tmp/tree_test.csv
  A       B       2
          C       3

.. code:: python

  csv = fandango.arrays.CSVArray('tmp/tree_test.csv')
  csv.expandAll()
  csv.getAsTree(lastbranch=1)
  Out[18]: {'A': {'B': ['2'], 'C': ['3']}}

ReversibleDict
--------------

.. code:: python

  ----In [133]: ch = fandango.dicts.ReversibleDict()

  In [134]: ch.update([(unichr(ord('a')+i),i,unichr(ord('A')+i)) for i in range(26)])

  In [135]: ch
  Out[135]: 
  (u'a', 0, u'A')
  (u'b', 1, u'B')
  (u'c', 2, u'C')
  (u'd', 3, u'D')
  ...

  In [136]: ch['a']
  Out[136]: (0, u'A')

  In [137]: ch['A']
  Out[137]: (0, u'a')

  In [138]: ch['a'].keys()
  Out[138]: set([0])

  In [139]: ch['A'].keys()
  Out[139]: set([0])

ThreadDict
----------

from PyPLC:

.. code:: python

    def initThreadDict(self):
        def read_method(args,comm=self.Regs,log=self.debug): #It takes a key with commas and splits it to have a list of arguments
            try:
                log('>'*20 + ' In ThreadDict.read_method(%s)' % args)
                args = [int(s) for s in args.split(',')[:2]]
                return comm(args,asynch=True)
            except PyTango.DevFailed,e:
                print 'Exception in ThreadDict.read_method!!!'
                print str(e).replace('\n','')[:100]
            except Exception,e:
                print '#'*80
                print 'Exception in ThreadDict.read_method!!!'
                print traceback.format_exc()
                print '#'*80
                return [] ## Arrays must not be readable if communication doesn't work!!!!
        
        self.threadDict = fandango.ThreadDict(
            read_method = read_method,
            trace=True)
        self.threadDict.set_timewait(max(0.1,self.ModbusTimeWait/1000.))
            
        self.info('Mapped Arrays are: %s' % self.MapDict)

        for var,maps in self.MapDict.items():
            regs = self.GetCommands4Map(maps)
            for reg in regs:
                vals = ','.join(str(r) for r in reg)
                self.debug('Adding %s(%s) as ThreadDict[%s]' % (var,reg,vals))
                self.threadDict.append(vals,[])#period=[]) #append(key,value='',period=3000)
            
        self.threadDict.start()
        self.info('out of PyPLC.initThreadDict()')

Reading:

.. code:: python

                for reg in regs:
                    key = ','.join(str(r) for r in reg)
                    val = self.threadDict[key]
                    
Piped, iPiped, zPiped interfaces
--------------------------------

Fandango has a set of operators to use regular-or operator ('|') like a linux pipe between operators (inspired by Maxim Krikun [ http://code.activestate.com/recipes/276960-shell-like-data-processing/?in=user-1085177]).

::
    cat('filename') | grep('myname') | printlines
    
Using fandango:

.. code:: python

  from fandango.functional import *

  v | iPiped(rd.get_attribute_values,start_date='2012-07-10',stop_date='2012-07-17') | iPiped(PyTangoArchiving.utils.decimate) | zPiped(time2str) | plist

  #equals to:

  [(time2str(v[0]),v[1]) for v in PyTangoArchiving.utils.decimate(rd.get_Attribute_values(v,start_date='2012-07-10',stop_date='2012-07-17'))]

Available interfaces are:

.. code:: python

  class Piped:
      """This class gives a "Pipeable" interface to a python method:
          cat | Piped(method,args) | Piped(list)
          list(method(args,cat))
      """
      ...

  class iPiped:
      """ Used to pipe methods that already return iterators 
      e.g.: hdb.keys() | iPiped(filter,partial(fandango.inCl,'elotech')) | plist
      """
      ...

  class zPiped:
      """ 
      Returns a callable that applies elements of a list of tuples to a set of functions 
      e.g. [(1,2),(3,0)] | zPiped(str,bool) | plist => [('1',True),('3',False)]
      """
      ...
    
Available operators are:

.. code:: python

  pgrep = lambda exp: iPiped(lambda input: (x for x in input if inCl(exp,x)))
  pmatch = lambda exp: iPiped(lambda input: (x for x in input if matchCl(exp,str(x))))
  pfilter = lambda meth=bool,*args: iPiped(filter,partial(meth,*args))
  ppass = Piped(lambda x:x)
  plist = iPiped(list)
  psorted = iPiped(sorted)
  pdict = iPiped(dict)
  ptuple = iPiped(tuple)
  pindex = lambda i: Piped(lambda x:x[i])
  pslice = lambda i,j: Piped(lambda x:x[i,j])
  penum = iPiped(lambda input: izip(count(),input) )
  pzip = iPiped(lambda i:izip(*i))
  ptext = iPiped(lambda input: '\n'.join(imap(str,input)))
