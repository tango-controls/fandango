#!/usr/bin/env python

from fandango.dynamic import DynamicServer

def main():
    pyds = DynamicServer(add_debug=0)
    pyds.main()  
    print('launched ...')

if __name__ == '__main__':
    main()