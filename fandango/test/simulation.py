import traceback,re,sys,json
import fandango as fn 
import fandango.tango as ft
from fandango.tango import *
from fandango.functional import *

###############################################################################
# Miscellaneous methods used for testing and simulating Tango Devices
# Moved here from panic/test/alarm_test.py

def dev2file(d,suffix='.json'):
  return d.replace('/','_')+suffix

def export(devices,suffix='.json',preffix=''):
  """ save devices in .json files """
  devices = fn.toList(devices)
  files = []
  if preffix and not preffix.endswith('/'):
    preffix+='/'
  for d in devices:
    try:
      values = ft.export_device_to_dict(d)
      files.append(preffix+dev2file(d,suffix))
      json.dump(dict2json(values),open(files[-1],'w'))
    except:
      print('%s failed'%d)
      traceback.print_exc()
  return files 

def load(tango_host,instance,devices,replace={},overwrite=False,def_class='SimulatorDS'):
  """ 
  the tango_host variable must match with the current tango_host; it is used to avoid accidental loading
  load .json files into simulated devices; one .json file per device
  devices may be a list of devices, a list of files or a dictionary {device:filename}
  """
  assert tango_host == fn.get_tango_host()
  
  done = []
  if isMapping(devices):
    filenames = devices
  else:
    devices = fn.toList(devices)
    filenames = {}
    for dd in devices:
      if os.path.isfile(dd):
        df,dd = dd,file2dev(dd)
      else:
        df,dd = dev2file(dd),dd
    filenames[dd] = df
      
  for dd,df in filenames.items():
    
    exists =  ft.get_matching_devices(dd)
    if exists and not overwrite:
      raise Exception('Device %s Already Exists!!!'%dd)
    
    data = json.load(open(df))
    props = data['properties']
    props = dict((str(k),map(str,v)) for k,v in props.items())
    
    for r,rr in replace.items():
      dd = clsub(r,rr,dd)
      for p,pp in props.items():
        for i,l in enumerate(pp):
          props[p][i] = clsub(r,rr,l)
          
    if overwrite:
      props['polled_attr'] = []
      props['polled_cmd'] = []
    
    if data['dev_class'] == 'PyAlarm':
      if not exists: ft.add_new_device('PyAlarm/'+instance,'PyAlarm',dd)
      props['AlarmReceivers'] = []
      ft.put_device_property(dd,props)
      
    else:
      if not exists: ft.add_new_device(def_class+'/'+instance,def_class,dd)
        
      ft.put_device_property(dd,props)
      
      #if data['dev_class'] not in ('PySignalSimulator','PyAttributeProcessor','PyStateComposer','CopyCatDS'):
        
      vals = dict((str(k),v['value'] if v else 0) for k,v in data['attributes'].items())
      dynattrs = []
      attrprops = fn.dicts.defaultdict(dict)

      for k,v in sorted(vals.items()):
        if k.lower() in ('state','status'):
          continue
        if v is None:
          continue

        t = type(v).__name__
        if t == 'unicode': t = 'str'
        v = str(v) if t!='str' else "'%s'"%v

        dynattrs.append(
            #'%s = %s(%s) #%s'%(
            '%s = %s(VAR(%s,default=%s,WRITE=True)) #%s'%(k,
            k,t,v,data['attributes'][k]['data_type']))
        
        attrprops[dd][k] = dict((p,data['attributes'][k].get(p,'')) for p in 
            ('format','label','unit','min_alarm','max_alarm'))
      
      ft.put_device_property(dd,'DynamicAttributes',dynattrs)
      try:
        ft.get_database().put_device_attribute_property(dd,
          dict((k,v) for k,v in attrprops[dd].items() if v))
      except:
        fn.time.sleep(3.)
    
    done.append(dd)

  return done