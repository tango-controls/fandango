#!/usr/bin/python

__usage__ = """
tango2csv
    This script allows to extract all the device servers matching the given filters.
    The arguments are:
       ./tango2csv filter1 filter2 filter3 filter4 ... destination.csv
       
Sergi Rubio, srubio@cells.es, 2008
"""

import sys
import traceback
import re
from PyTango import *
from fandango.arrays import CSVArray
from fandango.servers import ServersDict

"""
Search: Domain/Family/Member[/Attribute] (QLineEdit)
It must allow wildcards (*) to select any device or attribute from the database.
                 The database allows to search only for devices ... so the search_string must be split in 
                 dev_name and att_name
                    search_string='domain/family/member/attribute'
                    search_string,att_search = search_string.rsplit('/',1) if search_string.count('/')>2 else (search_string,'')

        Results: List of d/f/m or d/f/m/a names (A text widget with multiple lines and scrollable)
                It will show all the device or attribute names matching with the Search string.
                It must allow multiple (shift/ctrl+mouse_button) selection of lines
                How to get the list of running devices from Database:
                    PyTango.Database().get_device_exported('*') or .get_device_exported(search_string)
                How to get the list of attributes from the Device name:
                    import re
                    try:
                        atts_list=[a.name for a in PyTango.DeviceProxy(dev_name).attribute_list_query() if not att_search or re.match(att_search.replace('*','.*'),a.name)]
                    except Exception,e:
                        print 'Unable to contact with device %s: %s'%(dev_name,str(e))
                        atts_list=[]

And two buttons:
        Open/Add: It will return to the main application the list of selected items in Results widget

Future improvements:
        List filtering:
            Add a list of regular expressions or allowed names as an argument for Widgets creation
            The widget will show only those names that match:
                import re
                if any(re.match(reg,item_name) for reg in reg_exps): show_item(item_name)
"""

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

def add_properties_to_csv(out_csv,counter,server,klass,device,properties):        
    all_values = sum(len(v) for v in properties.values())
    if out_csv.size()[0]<(counter+all_values): 
        out_csv.resize(1+counter+all_values,out_csv.ncols)            
    out_csv.set(counter,0,server)
    out_csv.set(counter,1,klass)
    out_csv.set(counter,2,device)
    for prop,values in properties.items():
        if prop in (
          '__SubDevices','polled_attr','polled_cmd',
          'doc_url','ProjectTitle','cvs_location','Description','InheritedFrom'): continue
        print '%s.%s = %s' % (device,prop,values)
        out_csv.set(counter,3,prop)
        for value in values:
            out_csv.set(counter,4,value)
            print 'Added at %d: %s,%s,%s,%s' % (counter,server,device,prop,value)
            counter += 1         
    return counter
    
if __name__ == '__main__':
    try:
        print sys.argv
        filters = sys.argv[1:-1]
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
        counter = 1
        
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
            counter = add_properties_to_csv(out_csv,counter,server,klass,device,properties)
        out_csv.save()
        
        
    except Exception,e:
        print '-------> An unforeseen exception occured....',traceback.format_exc()
