#!/usr/bin/env python

__doc__ = """
tango2csv

    This script allows to extract all the device servers matching the given filters.
    The arguments are:
    
       ./tango2csv filter1 filter2 filter3 filter4 ... destination.csv
       
    Since fandango 13 it returns the new format as a nested dictionary. 
    To use the new treeish format without column headers use the --tree option.
    New implementation is imported from fandango/tango/export.py
    
"""

import sys
import traceback
import re
from PyTango import *
import fandango as fd
from fandango.arrays import CSVArray
from fandango.servers import ServersDict

def isregexp(s): 
    return any(c in s for c in ['.','[','(','{','|','^'])

def get_all_devices(db=None):
    if not db: db = PyTango.Database()
    all_devs = []
    doms = dict.fromkeys(db.get_device_domain('*'))
    for d in doms:
        doms[d] = dict.fromkeys(db.get_device_family(d+'/*'))
        for f in doms[d]:
            doms[d][f] = db.get_device_member(d+'/'+f+'/*')
            [all_devs.append('/'.join([d,f,m])) for m in doms[d][f]]
    return all_devs #doms

def get_filtered_devs(filters):
    for f in filters:
        
        domain,family,member = f.split('/') if '/' in f else (f,f,f)
        if not isregexp(domain) and '*' not in domain: domain = '*'+domain+'*'
        if not isregexp(family) and '*' not in family: family = '*'+family+'*'
        if not isregexp(member) and '*' not in member: member = '*'+member+'*'
        domains = db.get_device_domain(domain)
        for dom in domains:
            families = db.get_device_family(dom+'/'+family)
            for fam in families:
                members = db.get_device_member(dom+'/'+fam+'/'+('*' if isregexp(member) else member))
        #TODO: unfinished
    return

def add_properties_to_csv(out_csv,counter,server,klass,device,properties,exclude=[]):
    exclude = exclude or ['__SubDevices']
    try:
        [properties.pop(e) for e in exclude if e in properties]
        all_values = sum(len(v) for v in properties.values()) or 1
        print('add_properties_to_csv(...,%s,%s,[%d],...)'%(counter,device,all_values))
        if out_csv.size()[0]<(counter+all_values): 
            out_csv.resize(counter+all_values,out_csv.ncols)            
        out_csv.set(counter,0,server)
        out_csv.set(counter,1,klass)
        out_csv.set(counter,2,device)

        dprops = sorted(p for p in properties if '.' not in p)
        aprops = sorted(p for p in properties if '.' in p)

        for prop in (dprops+aprops):
            values = properties[prop]
            #if prop in (
            #'__SubDevices','polled_attr','polled_cmd',
            #'doc_url','ProjectTitle','cvs_location','Description','InheritedFrom'): continue
            print '%s.%s = %s' % (device,prop,values)
            out_csv.set(counter,3,prop)
            for value in values:
                out_csv.set(counter,4,value)
                #print 'Added at %d: %s,%s,%s,%s' % (counter,server,device,prop,value)
                counter += 1         
        return counter if properties else counter+1
    except Exception,e:
        print('add_properties_to_csv(%s,%s,%s,%s): failed!: %s'%(
            counter,server,klass,device,traceback.format_exc()))
    

def tango2csv(filters,options=[]):
    """
    Old method with fixed format
    
    This method is now deprecated by fandango.tango.export.tango2table
    """
    try:
        print('DEPRECATED: use fandango/tango/export.py instead')
        
        print filters
        if not filters:
            print __usage__ #'Syntax is ./tango2csv filter1 [more filters] destination.csv'
            exit()
        out_file = sys.argv[-1]# if len(sys.argv)>1 else 'output.csv'
        
        """
        How to do it?
        if / in filter : split('/') and use each filter independently
        The filter could be an string ASF, a dom/fam/mem, something like *PLC* or re/re/re or re
        if *PLC* and not . in filter: apply directly to db
            if any(.,(,^,),[,]) in filter ... try to get all and apply regular expressions
        if ASF and not *; db('*'+filter+'*')
        """

        db = Database()
        all_devs = get_all_devices(db)
        devices = []
        for f in filters:
            if '*' in f and not isregexp(f): 
                f=f.replace('*','.*')
            if isregexp(f):
                devices+=[d.lower() for d in all_devs if re.match(f.lower(),d.lower()) and ('dserver' in f or not d.startswith('dserver'))]
            else:
                devices+=[d.lower() for d in all_devs if f.lower() in d.lower() and ('dserver' in f or not d.startswith('dserver'))]
                
        print 'Creating %s file for TangoProperties configuration for %d devices' % (out_file,len(devices))
        out_csv = CSVArray(out_file)
        out_csv.resize(1,1) #It cleans the content of the file
        out_csv.save() #It is really needed!
        out_csv.resize(len(devices),5)
        [out_csv.set(0,i,['server','class','device','property','value'][i]) for i in range(5)]
        out_csv.setOffset(1)
        counter = 0
        
        print ('Creating a dict with servers/classes/devices from the database ...')
        servers = ServersDict()
        klasses = {}
        
        print ('Generating output file ...')
        for device in sorted(devices):
            servers.load_by_name(device)
            server = servers.get_device_server(device)
            klass = servers.get_device_class(device,server)
            #Adding a Class to the file
            if klass not in klasses:
                property_names = list(db.get_class_property_list(klass))
                if len(property_names):
                  print 'Adding %s class properties'%klass
                  klasses[klass] = db.get_class_property(klass,property_names)
                  counter = add_properties_to_csv(out_csv,counter,klass,klass,'#CLASS',klasses[klass])
            #Adding a device to the file
            property_names = list(db.get_device_property_list(device,'*'))
            if property_names:
                print '%d: reading device %s properties: %s' % (counter,device,property_names)
                properties = db.get_device_property(device,property_names)
            else: properties = {}

            attr_props = fd.tango.get_attributes_properties(device)
            print('loading %d attribute properties'%len(attr_props))
            for a,ps in attr_props.items():
                for p,v in ps.items():
                    properties['%s.%s'%(a,p)] = fd.toList(v)
                if '--value' in options:
                    properties['%s.value'%(a)] = fd.toList(fd.read_attribute('%s/%s'%(device,a)))
            
            counter = add_properties_to_csv(out_csv,counter,server,klass,device,properties)
        out_csv.save()
        
        
    except Exception,e:
        print '-------> An unforeseen exception occured....',traceback.format_exc()



def main():
    opts = [a for a in sys.argv[1:] if a.startswith('-')]
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not args:
        print(__doc__)
    elif '--tree' not in opts:
        tango2csv(args, opts)
    else:
        if len(args) > 1:
            fout = args[-1]
            args = args[:-1]
        else:
            fout = ''

        text = fd.tango.tango2table(args, opts=opts + ['--text'])

        if fout:
            fout = open(fout, 'w')
            fout.write(text)
            fout.close()
        else:
            print(text)

if __name__ == '__main__':
    main()


