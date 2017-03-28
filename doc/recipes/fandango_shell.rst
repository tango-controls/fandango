
Using Fandango from the Linux Shell
===================================

The tango_servers script allows to start/stop/check devices::

  > tango_servers stop "PyPLC/plctest*"
  
  > tango_servers start "PyPLC/plctest*"
 
  > tango_servers status "*/*otr*"  
  
    Loading */*otr* devices

    ds_imggrabber/bo01_fsotr01:     ON
            bo01/di/fsotr-01-ccd:   OPEN
            bo01/di/fsotr-01-iba:   RUNNING
            dserver/ds_imggrabber/bo01_fsotr01:     ON

    ds_imggrabber/bo02_fsotr01:     ON
            bo02/di/fsotr-01-ccd:   OPEN
            bo02/di/fsotr-01-iba:   RUNNING
            dserver/ds_imggrabber/bo02_fsotr01:     ON

    ds_imggrabber/bo03_fsotr01:     ON
            bo03/di/fsotr-01-ccd:   OPEN
            bo03/di/fsotr-01-iba:   RUNNING
            dserver/ds_imggrabber/bo03_fsotr01:     ON  
            
You can also start devices on an specific host::

  > tango_servers stop PyPLC/plctest12
  
  > tango_servers ctlabserver start PyPLC/plctest12
  

Most fandango methods can be launched from Unix shell (the launcher was called fandango.sh in previous versions)::

  > fandango get_tango_host
  
    localhost:10000
  
  > fandango findModule fandango
    
    /usr/lib/python2.7/site-packages/fandango
    
  > fandango get_matching_attributes "mach/ct/composer/*"
  
    mach/ct/composer/averagepressure
    mach/ct/composer/averagecurrent
  
  > fandango read_attribute mach/ct/composer/averagecurrent
  
    119.1
    
  > fandango get_matching_device_properties sr04/vc/eps-plc-01 "*"

    DynamicQualities,(*)_VAL=ATTR_ALARM if ATTR('$_ALRM') else ATTR_VALID
            (*)_CONFIG_Status=ATTR_ALARM if ATTR('$_CONFIG_ALRM') else ATTR_VALID
    DynamicStates,
    KeepAttributes,CPUStatus
            TestMode
            *
    KeepTime,1500
    Mapping,DigitalsREAD=0,+240
            AnalogIntsREAD=835,+280
            AnalogRealsREAD=2135,+350
            AnalogIntsWRITE=1155,+280
            AnalogRealsWRITE=2455,+350
            AnalogIntsDeltaREAD=5000,+252
            AnalogIntsDeltaWRITE=6000,+42
    MappingUnused,DigitalsWRITE=390,+240
    ModbusCacheConfig,0
    ModbusTimeWait,200
    Modbus_name,SR04/VC/EPS-PLC-01-MBUS
    

