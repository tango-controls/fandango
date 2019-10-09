import fandango as fn, fandango.callbacks as fc

attrs = map(str.lower,fn.get_matching_attributes('bl00*eps*plc*01/*'))

a = 'bl00/ct/eps-plc-01/State'

t0 = fn.now()
sources = dict((d,fc.EventSource(d,asynchronous=True)) for d in sorted(attrs))

#sources.values()[10].read(synch=True)

cache = fn.CaselessDict()

def hook(src,t,value):
    cache[src.normal_name]=(value)

el = fc.EventListener('A Queue for All')
el.set_value_hook(hook)
print('Subscribing %d attributes'%len(attrs))
[s.addListener(el) for k,s in sorted(sources.items())]
print('Subscription took %f seconds'%(fn.now()-t0))

t0 = fn.now()
print('Waiting ...')
while len(cache) < len(attrs):
    if fn.now() > t0+18.:
        break
    fn.wait(1.)
print('Attributes upated in %f seconds'%(fn.now()-t0))

def print_all():
    for i,t in enumerate(sorted(cache.items())):
        k,v = t
        print('%s/%s: %s = %s'%(i,len(attrs),k,str(v)[:40]))
        
print_all()

print('%d attributes were not read'%(len(attrs)-len(cache)))
print(sorted(a for a in attrs if a not in cache.keys()))
print('%d Nones'%len([v for v in cache.values() if v is None]))


