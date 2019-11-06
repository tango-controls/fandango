#!/usr/bin/env python

__doc__ = """
script to generate all test_method or test_class functions for a module

if a module is passed, docs and test cases are added to the resulting file

Usage:
    gen_test_file.py [generate|check] [src/module] [dest]
    
"""

import sys, os, traceback, fandango

try:
    outs = []
    docs =  fandango.defaultdict(str)
    tests = fandango.defaultdict(str)
    action = sys.argv[1]
    fname = sys.argv[2]
    modname = ''
    
    if not os.path.exists(fname):
        print('loading %s module' % fname)
        mod = fandango.objects.loadModule(sys.argv[1])
        fname = fandango.objects.findModule(sys.argv[1])
        modname = mod.__name__
        docs.update((k,getattr(v,'__doc__','')) for k,v in mod.__dict__.items())
        tests = getattr(mod,'__test__',{})
        
    else:
        try:
            mod = fandango.objects.loadModule(fname)
            modname = mod.__name__
            docs.update((k,getattr(v,'__doc__','')) for k,v in mod.__dict__.items())
            tests = getattr(mod,'__test__',{})
        except:
            pass
        
    f = open(fname)
    lines = f.readlines()
    f.close()
    
    if sys.argv[3:]:
        fname2 = sys.argv[3]
    else:
        fname2 = 'test_' + fname.split('/')[-1]
    
    decs = []
    for l in lines:
        if fandango.clmatch('^(def|class)[\ ].*',l):
            decs.append(l.split()[1].split('(')[0].strip(':').strip())

    if action == 'generate':
        if os.path.exists(fname2) and not fname2.endswith('.tmp'):
            fname2+='.tmp'

        outs.append('#!/usr/bin/env python\n'
                    '# -*- coding: utf-8 -*-'
                    '#\n'
                    '#   %s test template generated\n'
                    '#   from %s\n'
                    '#   \n' % (fname2, fname))
        outs.append('\n')
        if mod:
            outs.append('import %s\n' % mod.__name__)

        print('%d declarations found' % len(decs))
        print('%d test cases found: %s' % (len(tests),tests.keys()))
        for l in decs:
            outs.append('def test_%s():' % l)
            if docs[l]:
                outs.append('    """')
                outs.append('    '+docs[l].strip())
                outs.append('    """')
            else:
                outs.append('    ')
            if tests.get(l):
                t = repr(tests.get(l))
                try:
                    eval(t)
                except:
                    t = "''' %s '''" %t
                outs.append('    __test_%s = %s' % (l,t))
            
            # asserts are added commented to force you to write the tests
            outs.append('    #assert %s.%s' 
                    % (fname.replace('/','.').replace('.py',''), l))
            outs.append('')
            
        print('writing %s' % fname2)
        f = open(fname2,'w')
        f.write('\n'.join(outs))
        f.close()

    else:
        f = open(fname2)
        lines = f.readlines()
        f.close()
        decs2 = []
        for l in lines:
            if fandango.clmatch('^(def|class)[\ ].*',l):
                decs2.append(l.split()[1].split('(')[0].strip(':').strip())
        print('Functions not found:\n')
        done = 0
        for d in decs:
            if 'test_'+d not in decs2:
                print('%s is not tested!'%d)
            else:
                done += 1

        print('\n coverage = %d / %d = %f' 
              % (len(decs),done,float(len(decs))/done))
except:
    traceback.print_exc()
    print(__doc__)
