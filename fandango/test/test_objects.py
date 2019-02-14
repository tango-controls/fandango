import fandango as fn

class _Tester(object):
    
    def __init__(self,name):
        self.name = name
    
    def __enter__(self):
        print('testing %s' % self.name)
        
    def __exit__(self, et, ev, etb):
        if et:
            print('Failed!',etb)

def test_Cached():
    class mysum(object):
        __name__ = 'mysum'
        def __init__(self):
            self.counter = 0

        def add(self,a,b):
            print("""adding""")
            self.counter += 1
            return a + b
        add = fn.objects.Cached.new_wrapped_instance(add,expire=10,depth=5)
        
        @fn.Cached
        def subs(self,a,b):
            """subs""" 
            self.counter += 1
            return a - b

    m = mysum()
    csum = m.add
    assert csum(2,2) == 4
    print(csum.__doc__,'-',type(csum))
    #assert csum.__doc__ == 'adding'
    assert csum(1.2,1.3) == 2.5
    assert csum(2,2) ==  4
    assert m.counter == 2
    assert len(csum.cache) == 2
    assert m.subs(2,3) == -1
    assert m.subs(2,3) == -1
    print(m.subs.__doc__)
    assert m.counter == 3
    return True
    
def main():
    for f in globals().values():
        if str(getattr(f,'__name__','')).startswith('test_'):
            with _Tester(f.__name__) as t:
                print(f())
    return True

if __name__ == '__main__':
    main()
