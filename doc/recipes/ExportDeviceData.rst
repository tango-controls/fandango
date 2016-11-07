Export Tango Device Data to .json files
=======================================

To export device properties to a .json file::

 > python -c "\
 import json,fandango;
 d,f = 'bl00/ct/eps-plc-01','bl00.albaplc.json';
 props = fandango.tango.get_matching.device_properties(d,'*');
 fandango.dict2json(props,filename=f);
 "

To export all device data (attribute config and values, command definition, ...)::

 > python -c "\
 import json,fandango;
 d,f = 'bl00/ct/eps-plc-01','bl00.albaplc.json';
 fandango.dict2json(fandango.tango.export_device_to_dict(d),filename=f);
 "

Or just::

 > fandango.sh "dict2json(export_device_to_dict('bl00/ct/eps-plc-01'),'bl00-albaplc.json')
