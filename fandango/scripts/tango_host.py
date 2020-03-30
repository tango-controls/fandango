#!/usr/bin/env python

def main():
    try:
      rc = open('/etc/tangorc').readlines()
      rc = [l.split('=')[1].strip() for l in rc if l.startswith('TANGO_HOST=')]
      assert rc
      print(rc[0])
    except:
      import traceback
      #traceback.print_exc()
      import PyTango
      db = PyTango.Database()
      print('%s:%s'%(db.get_db_host(),db.get_db_port()))


if __name__ == '__main__':
  main()