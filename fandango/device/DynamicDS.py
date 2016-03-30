#!/usr/bin/env python

from fandango.dynamic import DynamicServer


if __name__ == '__main__':
    pyds = DynamicServer(add_debug=0)
    pyds.main()
    print('launched ...')