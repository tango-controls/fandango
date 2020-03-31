#!/usr/bin/python

__doc__ = """
usage: 
  tango_monitor <device name> [ <attr regexp> ]*
  
  tango_monitor <attr_exp1> <attr_exp2> [ period=3000 ]
"""

import sys
import time
import PyTango
import fandango as fn

class MyCallback(object):
    
    counter = 0
    
    def __init__(self):
        self.t0 = time.time()
        self.counters = fn.dicts.defaultdict(int)
        self.values = fn.dicts.defaultdict(str)
        self.dups = fn.dicts.defaultdict(int)
        self.ratios = fn.dicts.defaultdict(float)

    def push_event(self,event):
        MyCallback.counter+=1
        aname = fn.tango.get_normal_name(event.attr_name)
        self.counters[aname] = self.counters[aname] + 1
        self.ratios[aname] = self.counters[aname] / (time.time()-self.t0)
        value = getattr(event.attr_value,'value',event.attr_value)
        value = fn.shortstr(value)
        if self.values[aname] == value:
            self.dups[aname] += 1
            
        self.values[aname] = value
        print('%s:%s = %s; %s; ct=%d/%d, e/s=%2.2f, dups=%d' %
                (fn.time2str(),aname,value,event.event, self.counters[aname],
                MyCallback.counter,self.ratios[aname],self.dups[aname]))
        

def monitor(*args, **kwargs):
    """
    monitor(device,[attributes])
    
    kwargs: events (event types), period (polling period)
    """
    # Old syntax (device, attrs regexp)
    print(args)
    if (fn.clmatch(fn.tango.retango,args[0]) and args[1:] and
            not any(fn.clmatch(fn.tango.retango,a) for a in args[1:])):
        args = [args[0]+'/'+a for a in args[1:]]

    attrs = fn.join(fn.find_attributes(a) for a in args)
    print('matched %d attributes: %s' % (len(attrs),attrs))
    
    # event filters (deprecated)
    events = kwargs.get('events',[PyTango.EventType.CHANGE_EVENT])

    eis,worked,failed = [],[],[]
    sources = []
    cb = MyCallback() #PyTango.utils.EventCallBack()
    
    models = [(a if '/' in a else d+'/'+a) for a in attrs]
    for a in models:
        (failed,worked)[bool(fn.tango.check_attribute_events(a))].append(a)
        
    for m in models:
        try:
            sources.append(fn.EventSource(m,enablePolling=True,
                listeners=[cb], pollingPeriod=kwargs.get('period',3000)))
            #for e in events:
                #eis.append(dp.subscribe_event(a,e,cb))
            #worked.append(a)
        except:
            print(fn.except2str())
            #failed.append(a)

    print('%d attributes NOT provide events: %s' % (len(failed),failed))      
    print('%d attributes provide events: %s' % (len(worked),worked))
    print('-'*80 + '\n' + '-'*80)
    try:
        while True:
            time.sleep(1)
    except: #KeyboardInterrupt
        print(fn.except2str())
        print('-'*80)
        print "Finished monitoring"
        
    #[dp.unsubscribe_event(ei) for ei in eis];
        
def main():
    import sys
    try:
        args = sys.argv[1:]
        if not args:
            raise Exception('No arguments provided!')
        opts = [a for a in args if '=' in a]
        args = [a.strip() for a in args if a not in opts] or ["state"]
        opts = dict((k,fn.str2type(v)) for k,v in (o.split('=',1) 
                                                   for o in opts))
        monitor(*args,**opts)
    except:
        print(fn.except2str())
        print(__doc__)
    

if __name__ == '__main__':
    main()