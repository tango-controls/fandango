// File:          TangoSynopticHandler.java
// Created:       2004-10-13 16:45:29, poncet
// By:            <poncet@esrf.fr>
// Time-stamp:    <2004-10-13 16:45:29, poncet>
//
// $Id$
//
// Description:

package fr.esrf.tangoatk.widget.jdraw;


import fr.esrf.Tango.DevFailed;

import fr.esrf.tangoatk.core.*;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.attribute.AttributeFactory;
import fr.esrf.tangoatk.core.attribute.AAttribute;
import fr.esrf.tangoatk.core.attribute.BooleanScalar;
import fr.esrf.tangoatk.core.command.*;
import fr.esrf.tangoatk.widget.command.AnyCommandViewer;
import fr.esrf.tangoatk.widget.command.VoidVoidCommandViewer;
import fr.esrf.tangoatk.widget.util.*;

import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.event.MouseEvent;
import java.awt.event.ComponentEvent;
import java.awt.*;
import javax.swing.*;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.*;
import java.util.List;
import java.io.*;
import java.util.regex.Pattern;

import fr.esrf.tangoatk.widget.util.jdraw.*;
import fr.esrf.tangoatk.widget.attribute.*;
import fr.esrf.tangoatk.widget.util.ErrorPopup;



/**
 * TangoSynopticHandler is the base class used to display and animate any
 * tango synoptic drawing made with the JDraw drawing tool "JDraw".
 *
 * The drawing file is browsed and a behaviour is attached to each drawing
 * component according to the tango object which is associated with.
 *
 * While brawsing the drawing file the name of the graphical component
 * determines the associated tango object:
 *
 * For example if inside the synoptic drawing a simple rectangle is given
 * the name "eas/test-api/1" it will be associated to the tango device
 * eas/test-api/1.
 *
 * The animation on the graphical component depends on the type of the
 * Tango object (device, attribute, command) and the type of JDraw graphical
 * component (simple graphical component, multi-state JDraw object, interactive JDraw object)
 *
 * Here are the default (state) animations provided :
 * <ul>
 * <li>Tango device - simple graphical component : the colour of the graphical
 *  component represents the state of the tango device (on, off, alarm, fault...)
 * <li>Tango device - multi-state JDraw object : the form of the JDraw Object represents the
 * tango device state (on, off, alarm, fault, ...)
 * <li>Tango device command - interactive JDraw object : no state animation
 * <li>Tool Tip : A tooltip can be associated to any tango device. The tooltip can
 * display either the name of the device or it's state according to the tooltip mode used.
 * </ul>
 * <p>
 * In addition to the animation a default interaction behaviour is
 * provided (reaction to mouse clicks). Here are the default interactions :
 *
 * <ul>
 * <li>Tango device - simple graphical component : Click on the graphical component
 * will launch a java class whose name has been specified during the drawing phase.
 * If this class name is missing, the generic tool atkpanel is launched. If the class name is set
 * to the predefined string "noPanel" the atkpanel is not launched.
 * <li>Tango device - multi-state JDraw object : the same interaction model
 * <li>Tango device command - interactive JDraw object : Click on the JDraw object will display
 * an "input / output argument window" if the input is required or execute the
 * associated command on the tango device if no input is required.
 * </ul>
 *
 * There are 4 extensions parsed by default :
 * <ul>
 * <li>className: If the Jdraw component is asscoiated to a Tango device or to a
 * Tango state attribute this extension (className) represents the name of the java class
 * to instantiate when the Jdraw object is clicked. This allows to give the name
 * of the panel to be launched when the object is clicked.
 * If the className is not specified the default panel (atkpanel read-only) is launched.
 * If the className is set to "noPanel" nothing is launched.
 * <li>classParam: first argument (always a string) to be passed to the java panel.
 * If classParam is not specified the name associated to the JD component (device name or
 * state attribute name is passed as the String argument to the constructor.
 * <li>valueList: used by NumberScalarComboEditor and StringScalarComboEditor swing objects to acquire the values list
 * <li>shellCommand(*):It allows to launch any shell command or application (dir, xterm, jive, firefox, etc ...) from the synoptic.
 * If a JDObject is interactive and has the shellCommand extension its content will be executed at each valueExceedBounds event
 * The command is always executed in background. Streams redirection is not allowed (should be done inside an script).
 * Arguments can be passed to the shell command.
 * </ul>
 *
  * @author      Faranguiss  PONCET
  * @since       ATKWidget-1.9.7
  */
  
/** ******************************************************************************************************
srubio@cells.es, oktober 2006.
The TangoSynopticHandler Class has been modified to:
	- Add a stopRefresher command to stop the allAttributes AttributeList refresher thread 
	- Now there's 5 extensions parsed by default:
		className: 
			java panel to be launched when the object is double-clicked
		className=noPanel(*):
			If this extension is present no default panel (atkpanel.MainPanel) is launched for this object
		classParam: 
			first argument to be passed to the java panel
			e.g, if className is a synopticAppli classParam="asynopticfile.jdw"
		valueList: 
			used by *ScalarComboEditor swing objects to acquire the values list
			used also by atkpanel to read the rest of MainPanel arguments (standAlone, keepStateRrep efresh, propertiesButton, readOnly = "0 1 0 0")
			for a Combo editor could be "jive xterm mambo" if it asking for an application to launch
		shellCommand(*):
			It allows to launch any shell command or application (dir, xterm, jive, firefox, etc ...) from the synoptic
			If a JDObject is interactive and has the shellCommand extension its content will be executed at each valueExceedBounds event
			The command is always executed in background
			Streams redirection is not allowed (should be done inside an script)
			Arguments can be passed to the shell command
		tangoColors(*):
			Actual JDraw deprecates standard Tango-State Colors if something is enabled in the interactive panel
			This extension has been added to force JDraw to apply the original TangoColors to this object
		noPrompt(*):
			If this extension is present external applications are executed w/out prompt
		standAlone(*):
			If this extension is present external applications are not killed when Synoptic exits

	EXTENSIONS USED BY SYNOPTIC TREE:

	- isSynoptic: file.jdw	; Allows to setup a jdraw file linked to the actual object, it will be added to the Tree hierarchy

	- xmlFile: file.xml ; Allows to setup an xml file to be added to the actual attributes being shown in the attribute/trends panel

	- addToTrend, addToTable ; Automatically add this attribute to the attributes table/trend panels

srubio@cells.es 22/May2008

NEW EXTENSIONS:
	- Use noTooltip to not generate a tooltip for an object	

	- Added a IgnoreRepaint/ignoreRepaint extension: Color changes (e.g. due to state) are not propagated through this device
		It was previously implemented by setting "IgnoreRepaint" as object's name

	- Add a ExtensionsList extension to introduce as a list in a single field all these extensions that don't require a value

	- Add an ignoreMouse extension just to mark the opposite
		THE OPPOSITE TO WHAT? ... I assume that it means receiving group events but not mouse events.

	- eventReceivers: If an Object's interactivity must affect other devices (e.g change of visibility), its names must be listed here
		Names must be separated by commas (trailing spaces must be removed)
		The difference between eventReceivers and groupHook is that it affects a set of objects independently of its grouping
		This is to affect to pressure values only, although they are grouped with their symbols.
		Content could be a regular expression.
		
	- isContainer: Group objects that are device/attributes/command or interactive will be explored only if this extensions is present.
	 	All the group objects have mouse listener by default; it determines if their children will have also.
	 	A group device could be already mousified! 

PROPOSALS:

	- Add a list with all objects, adding recursively from groups until a device or an interactive object is found
		It will simplify the execution of all the events that affect individual objects independently of their grouping state.

	- Add a groupHook extension to mark an object within a group as the receiver of all mouse events on it
		... as JDObject.groupHook="" ... it receives events, but these are not propagated
			The rest of devices of the group keep its own events like always
		... as JDGroup.groupHook=ObjectName ... it becomes the exclusive receiver 
			Then, for all events within the group this device will execute all (e.g. Tooltip!)
		... as JDObject.groupHook="GroupName" ... it receives the events and propagates the results through the Group (e.g change of visibility)
			To find a group it will ignore any group that is device/attribute or is interactive
			Once it finds a group, it will search for all the interactive objects within the group
			It will apply the new value to all of them ... it can be a value set by clicking or a value depending of state/quality

	srubio@cells.es 07/nov/2006
		- Added a String[] getDeviceList() method to be used from the StateComposer Device
	srubio@cells.es 09/nov/2006
		- Added a new isStateComposer extension: args could be a synoptic filename or a list of devices
		DEPRECATED!!

TODO:
	MOUSEIFICATION MUST BE DONE ON THOSE OBJECTS NOT LINKED TO ANY DEVICE (A Synoptic Could not be necessarily linked to a device!)

EXAMPLES:

	className: fr.esrf.tangoatk.widget.attribute.Trend
	valueList: /homelocal/sicilia/var/aktmoni/test.sim.moni
	
	className: fr.esrf.tangoatk.widget.jdraw.SimpleSynopticAppli
	classParam: s3-s4-linac.jdw

	className: atkpanel.MainPanel
	classParam: test/sim/noisypsu
	valueList: 0 1 0 0

	className: fr.esrf.tangoatk.widget.jdraw.DeviceSynopticFrame
	classParam: s16
	shellCommand: tg_devtest test/sim/beam
*********************************************************************************************************/



public class TangoSynopticHandler extends JDrawEditor
                                  implements IStateListener, IStatusListener,
                                             INumberScalarListener, IDevStateScalarListener,
                                             WindowListener
{

   /** Does not display tooltip */
   public static final int          TOOL_TIP_NONE = 0;
   /** Displays device state within tooltip */
   public static final int          TOOL_TIP_STATE = 1;
  /** Displays device status within tooltip */
   public static final int          TOOL_TIP_STATUS = 2;
  /** Displays device name within tooltip */
   public static final int          TOOL_TIP_NAME = 3;


   private static final int         STATE_INDEX = 0;
   private static final int         STATUS_INDEX = 1;


   private static Map               dynoState;

   private    int                   toolTipMode;
   private    String                jdrawFileFullName = null;

   private    AttributeFactory      aFac = null;
   private    CommandFactory        cFac = null;
   private    DeviceFactory         dFac = null;

   private    AttributeList         allAttributes = null;


   private    Map                   jdHash;
   private    Map                   stateCashHash;

   private    AnyCommandViewer      acv = null;
   private    JFrame                argFrame = null;

   private    ErrorHistory          errorHistWind = null;
   private    ErrorPopup            errPopup = null;

   private    Vector                panelList = new Vector();
   private    Vector                appList = new Vector();
   private    Vector                flagList = new Vector();



   // The HashMap for Dynamic Objects in  Jdraw (isProgrammed() = true)
   // This hashmap allows to convert an Atk State to the "numeric" value to be
   // sent to the Dynamic Object.
   static 
   {
       /*  Old HashMap did not allow a one to one mapping of Tango states
       dynoState = new HashMap();
       dynoState.put("UNKNOWN", new Integer(0));
       dynoState.put("OFF",     new Integer(1));
       dynoState.put("CLOSE",   new Integer(1));
       dynoState.put("EXTRACT", new Integer(1));
       dynoState.put("INIT",    new Integer(1));
       dynoState.put("DISABLE", new Integer(1));
       dynoState.put("ON",      new Integer(2));
       dynoState.put("OPEN",    new Integer(2));
       dynoState.put("INSERT",  new Integer(2));
       dynoState.put("ALARM",   new Integer(3));
       dynoState.put("FAULT",   new Integer(4));
       dynoState.put("MOVING",  new Integer(5));
       dynoState.put("RUNNING", new Integer(5));
       dynoState.put("STANDBY", new Integer(6));
       */

       /*
       The HashMap has been modified such that each single Tango state is
       handled. When an ATK state is received it is converted to a numeric
       value. This numeric values used here are the same as the Tango definition different
       tango device state. The numeric value is used in the drawing phase to associate
       a drawing to a state.
       */
       dynoState = new HashMap();
       dynoState.put("ON",      new Integer(fr.esrf.Tango.DevState._ON));       //Jdraw value = 0
       dynoState.put("OFF",     new Integer(fr.esrf.Tango.DevState._OFF));      //Jdraw value = 1
       dynoState.put("CLOSE",   new Integer(fr.esrf.Tango.DevState._CLOSE));    //Jdraw value = 2
       dynoState.put("OPEN",    new Integer(fr.esrf.Tango.DevState._OPEN));     //Jdraw value = 3
       dynoState.put("INSERT",  new Integer(fr.esrf.Tango.DevState._INSERT));   //Jdraw value = 4
       dynoState.put("EXTRACT", new Integer(fr.esrf.Tango.DevState._EXTRACT));  //Jdraw value = 5
       dynoState.put("MOVING",  new Integer(fr.esrf.Tango.DevState._MOVING));   //Jdraw value = 6
       dynoState.put("STANDBY", new Integer(fr.esrf.Tango.DevState._STANDBY));  //Jdraw value = 7
       dynoState.put("FAULT",   new Integer(fr.esrf.Tango.DevState._FAULT));    //Jdraw value = 8
       dynoState.put("INIT",    new Integer(fr.esrf.Tango.DevState._INIT));     //Jdraw value = 9
       dynoState.put("RUNNING", new Integer(fr.esrf.Tango.DevState._RUNNING));  //Jdraw value = 10
       dynoState.put("ALARM",   new Integer(fr.esrf.Tango.DevState._ALARM));    //Jdraw value = 11
       dynoState.put("DISABLE", new Integer(fr.esrf.Tango.DevState._DISABLE));  //Jdraw value = 12
       dynoState.put("UNKNOWN", new Integer(fr.esrf.Tango.DevState._UNKNOWN));  //Jdraw value = 13 or default
   }


  /**
   * Construct a TangoSynopticHandler (A JDrawEditor in MODE_PLAY).
   * @see JDrawEditor#MODE_PLAY
   */
   public TangoSynopticHandler()
   {

      super(JDrawEditor.MODE_PLAY);
      toolTipMode = TOOL_TIP_NONE;
      jdrawFileFullName = null;

      aFac = AttributeFactory.getInstance();
      cFac = CommandFactory.getInstance();
      dFac = DeviceFactory.getInstance();
      
      errPopup = ErrorPopup.getInstance();
      allAttributes = new AttributeList();
   }


  /**
   * Construct a TangoSynopticHandler (A JDrawEditor in MODE_PLAY).
   * @param jdFileName Filename of the JDraw (jdw) synptic to load.
   * @see #setSynopticFileName
   */
   public TangoSynopticHandler(String  jdFileName)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
   {
      this();

/*
      boolean b;
      b = isDeviceName ("toto");
      b = isDeviceName ("toto:tata");
      b = isDeviceName ("toto/tata");
      b = isDeviceName ("toto:tata/titi");
      b = isDeviceName ("toto:tata/titi/tutu");
      b = isDeviceName ("//popo");
      b = isDeviceName ("//popo/toto:tata");
      b = isDeviceName ("//popo/toto/tata");
      b = isDeviceName ("//popo/toto:tata/titi");
      b = isDeviceName ("//popo/toto/tata/titi");
      b = isDeviceName ("//popo/toto:tata/titi/tutu");
      b = isDeviceName ("//popo:kkkkl/toto/tata/titi");
      b = isDeviceName ("");
      b = isDeviceName (":");
      b = isDeviceName ("/");
      b = isDeviceName (":/");
      b = isDeviceName ("/dd/");
      b = isDeviceName (":/dd/");
      b = isDeviceName ("//");
      b = isDeviceName ("///:");
      b = isDeviceName ("////");
      b = isDeviceName ("///:/");
      b = isDeviceName ("///://");
      b = isDeviceName ("/////");
      b = isDeviceName ("//:///");
      b = isDeviceName ("//:102///");

      b = isDeviceName ("toto/tata/titi");
      b = isDeviceName ("toto-dd/tata-dd/titi-dd");
      b = isDeviceName ("taco:tata/titi/tutu");
      b = isDeviceName ("//popo:102/toto/tata/titi");
      b = isDeviceName ("//popo:102/toto-dd/tata-dd/titi-dd");

      b = isDeviceName ("toto/tata/titi/aaaa");
      b = isDeviceName ("taco:tata/titi/tutu/aaaaa");
      b = isDeviceName ("//popo:102/toto/tata/titi/aaaaa");

      b = isDeviceName ("tango://popo:102/toto/tata/titi");
      b = isDeviceName ("tango://160.103.5.10:102/toto/tata/titi");
      b = isDeviceName ("tango:toto/tata/titi");
      b = isDeviceName ("tango://popo/toto/tata/titi");
      b = isDeviceName ("//160.103.5.10:102/toto/tata/titi");
      b = isDeviceName ("//160.103.5.10.1:102/toto/tata/titi");
      b = isDeviceName ("//name:102/toto/tata/titi");
*/
      setSynopticFileName(jdFileName);
   }

/**
 * Construct a TangoSynopticHandler (A JDrawEditor in MODE_PLAY).
 * @param jdFileName Filename of the JDraw (jdw) synptic to load.
 * @param errh ErrorHistory window which will receive errors.
 * @see #setSynopticFileName
 * @see ErrorHistory
 */
   public TangoSynopticHandler(String  jdFileName, ErrorHistory errh)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
   {
      this();

      if (errh != null)
         errorHistWind = errh;

      setSynopticFileName(jdFileName);
   }



/**
 * Construct a TangoSynopticHandler (A JDrawEditor in MODE_PLAY).
 * @param jdFileName Filename of the JDraw (jdw) synptic to load.
 * @param ttMode Tooltip mode
 * @see #TOOL_TIP_NONE
 * @see #TOOL_TIP_STATE
 * @see #TOOL_TIP_STATUS
 * @see #TOOL_TIP_NAME
 */
   public TangoSynopticHandler(String  jdFileName, int ttMode)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
   {
      this();

      if (     (ttMode == TOOL_TIP_NONE)    ||  (ttMode == TOOL_TIP_STATE)
           ||  (ttMode == TOOL_TIP_STATUS)  ||  (ttMode == TOOL_TIP_NAME)   )
	  toolTipMode = ttMode;

      setSynopticFileName(jdFileName);
   }


/**
 * Returns the current Tooltip Mode
 * @see #setToolTipMode
 */
   public int getToolTipMode()
   {
     return(toolTipMode);
   }


/**
 * Sets the current tooltip mode (device object only)
 * @param ttMode Tooltip mode
 * @see #TOOL_TIP_NONE
 * @see #TOOL_TIP_STATE
 * @see #TOOL_TIP_STATUS
 * @see #TOOL_TIP_NAME
 */
   public void setToolTipMode( int  ttMode)
   {

      if (     (ttMode == TOOL_TIP_NONE)    ||  (ttMode == TOOL_TIP_STATE)
           ||  (ttMode == TOOL_TIP_STATUS)  ||  (ttMode == TOOL_TIP_NAME)   )
      {
	  if (toolTipMode != ttMode)
	  {
	     toolTipMode = ttMode;
	  }
      }

   }


/**
 * Returns the current error history window
 * @see #setErrorHistoryWindow
 */
   public ErrorHistory getErrorHistoryWindow()
   {
     return(errorHistWind);
   }


/**
 * Sets the current error history window. Note that the error history window
 * should be set before the jdraw file is parsed (before the call to the setSynopticFileName)
 */
   public void setErrorHistoryWindow( ErrorHistory  errh)
   {
        if (errh == null)
	   return;

	if (jdrawFileFullName != null)
	   return;

	errorHistWind = errh;
   }

/**
 * Returns the current synoptic filename.
 * @see #getSynopticFileName
 */
   public String getSynopticFileName()
   {
      return (jdrawFileFullName);
   }

  /**
   * Returns a Handle to the global attribute list which is used
   * internaly to monitor attributes. This list is filled after
   * setSynopticFileName() is called. To add an error listener
   * to this list, you have to register it before loading a synoptic.
   * @see #setSynopticFileName
   */
   public AttributeList getAttributeList()
   {
      return allAttributes;
   }
   
/**
 * Returns a list with all the device names
 * 
 */
   public String[] getDeviceList() {
	 //java.util.Vector devsList = new Vector();
	 String[] devsList=new String[getObjectNumber()];
	 if (getObjectNumber()==0) {
		 System.out.println("TangoSynopticHandler.getObjectNumber()=0!!!");
	 }
     int nDevs = 0;
     for (int i = 0; i < getObjectNumber(); i++) {
       JDObject jdObj = getObjectAt(i);
       String s = jdObj.getName();
       if (java.util.Arrays.toString(devsList).indexOf(s)<0 && isDevice(s)) {
         devsList[nDevs++]=s;
	   }
	   else if (isAttribute(s) || isCommand(s)) {
		   s = s.substring(0, s.lastIndexOf("/"));
		   if (java.util.Arrays.toString(devsList).indexOf(s)<0 && isDevice(s)) {
			   devsList[nDevs++]=s;
		   }
	   }
	 }
	 String[] returnList=new String[nDevs];
	 for (int i=0;i<nDevs;i++) returnList[i]=devsList[i];
	 return returnList;
   }

/**
 * Reads the Jdraw file, browses and parses the synoptic components.
 * The main purpose of this function is to attach Tango entity model to
 * JDraw component.
 * @param jdFileName Filename of the JDraw (jdw) synptic to load.
 */
   public void setSynopticFileName( String  jdFileName)
               throws MissingResourceException, FileNotFoundException, IllegalArgumentException
   {
      System.out.println("In TangoSynopticHandler::setSynopticFileName(...) ...");
      jdHash = new HashMap();
      stateCashHash = new HashMap();
      // Here should disconnect from all attributes and devices in the previous
      // Jdraw file.

      try
      {
         loadFile(jdFileName);
      }
      catch (IOException e)
      {
         throw new IllegalArgumentException(e.getMessage());
      }

      if (getObjectNumber() == 0)
         throw new MissingResourceException(
             "The Jdraw file has no component inside. First draw a Jdraw File.",
             "JDrawEditor", null);

      jdrawFileFullName = jdFileName;

      //srubio@cells.es: I've put devices/attributes initialization in a separate thread, just to avoid a long time wait of the user 
      // this behaviour is optional through a property
      String libPath = System.getProperty("THREADED", "null");
      if ( libPath.equals("null") || libPath.equals("no") || libPath.equals("NO")) {
		parseJdrawComponents();
	}
      else {
		new Thread () {
			public void run() {
				parseJdrawComponents();
			// We need to refresh all attributes because if several JDObject
			// has the same model , only the first one get the event. (API
			// specification )
			
			if (allAttributes.size()>0) {
				for(int i=0;i<allAttributes.size();i++)
				((AAttribute)allAttributes.elementAt(i)).refresh();
				allAttributes.startRefresher();
				}
			}
		}.start();
      }
      computePreferredSize();

      // We need to refresh all attributes because if several JDObject
      // has the same model , only the first one get the event. (API
      // specification )
/*
      if (allAttributes.size()>0) {
        for(int i=0;i<allAttributes.size();i++)
          ((AAttribute)allAttributes.elementAt(i)).refresh();
        allAttributes.startRefresher();
      }
*/

// not needed : automatically started in dFac class      dFac.startRefresher();
   }
   
/**
 * Stops the Refresher thread of the attribute list
 * Added to be used when a not stand-alone synoptic is closed
 * THE REFRESHER THREADS ARE NOT BEING STOPPED!!!
 */   
   public void stopRefresher() {
	   allAttributes.stopRefresher(); 
   }

   /**
    * Parses JDraw components , detects tango entity name and attatch a model.
    * This method does not recurse group and use isDevice() , isAttribute()
    * and isDevice() to detect entity name.
    * srubio@cells.es: I've split parseJdrawComponents in two methods to allow objects inside Groups to be parsed.
    * @see #isDevice
    * @see #isAttribute
    * @see #isCommand
    */
   protected void parseJdrawComponent(JDObject jdObj) {
       String s = jdObj.getName();
       if (isDevice(s)) {
         addDevice(jdObj, s);
       } else {
         // Add attribute before command to avoid that the State attribute
         // is taken as a command.
         // But there is still a potential problem for attributes and commands
         // which have the same name...
         if (isAttribute(s)) {
           addAttribute(jdObj, s);
         } else {
           if (isCommand(s)) {
             addCommand(jdObj, s);
           } else {
             //System.out.println(s+" is not an attribute, nor a command, nor a device; ignored.");

           } //end of not-command
         } //end of not-attribute
       } //end of not-device
       
       // INDEPENDENT BEHAVIOURS!
       // It should be independent of isDevice/isAttribute/isCommand behaviour
       
		//srubio@cells.es: added to parse JDGroups recursively
       // Groups that already has been mousified (devices/attributes/commands) will be recursively 
       // parsed only if they have the "isContainer" extension; if not, internal objects will be ignored.
		if ((jdObj instanceof JDGroup) && (!jdObj.hasMouseListener() || jdObj.hasExtendedParam("isContainer")))
		{
			JDGroup    jdg=null;
			int        nbChild=0;
			int        idx;
			JDObject   currChild=null;
			jdg = (JDGroup) jdObj;
			mouseifyGroup(jdObj);
			nbChild = jdg.getChildrenNumber();
			for (idx=0; idx < nbChild; idx++)
			{
				currChild = jdg.getChildAt(idx);
				if (currChild != null)	parseJdrawComponent(currChild);
			}
		} //end of is-group

		// Objects with a className associated (if not already mousified as devices or attributes)
		//Mouseify those objects that have an assigned class to them
		if(!jdObj.hasMouseListener() && jdObj.hasExtendedParam("className")) {
			//If they are interactive, the launchPanel will be assigned with a button behaviour.
		     //System.out.println("Mouseifying object: "+jdObj.getName());
			if (jdObj.isInteractive()) {
				jdObj.addValueListener(new JDValueListener() {
		       			public void valueChanged(JDObject comp) {launchPanel(comp,comp.getName(),false);}
					public void valueExceedBounds(JDObject comp) {}
				});
			} else {
				jdObj.addMouseListener(new JDMouseAdapter() {
						public void mousePressed(JDMouseEvent evt) {
							JDObject comp = (JDObject) evt.getSource();
							//System.out.println("Mouse pressed ("+e.getID()+") on device: "+((JDObject)e.getSource()).getName());
							launchPanel(comp,comp.getName(),false);
						}
						/*      public void mouseEntered(JDMouseEvent e) {
							//System.out.println("Mouse entered ("+e.getID()+") on device: "+((JDObject)e.getSource()).getName());
							devDisplayToolTip(e);
						}
						public void mouseExited(JDMouseEvent e) {
							devRemoveToolTip();
						}*/
					});
			}
		}

		//Mouseifying Group Hooks (objects that propagate its events to others)
		if (jdObj.hasExtendedParam("groupHook") || jdObj.hasExtendedParam("eventReceivers")) {
			mouseifyHook(jdObj);
		}
       
		// InteractiveButtons for shellCommands
		if (jdObj.isInteractive() && jdObj.hasExtendedParam("shellCommand")) {
			jdObj.addValueListener(new JDValueListener() {
				public void valueChanged(JDObject src) {}
				public void valueExceedBounds(JDObject comp) {
					String compName=comp.getName();
					String command = comp.getExtendedParam("shellCommand");
					System.out.println("Interactive Object "+compName+" value Exceed Bounds");
					int option = JOptionPane.YES_OPTION;
					if (!comp.hasExtendedParam("noPrompt")) {
						option = JOptionPane.showConfirmDialog(null,"This Shell Command is going to be executed, Are you sure?\n>"+command,
							compName+": Shell Command",JOptionPane.YES_NO_OPTION);
						}
					if (option == JOptionPane.YES_OPTION) {
						try {
						System.out.println("The osName is "+System.getProperty("os.name" ));
						//Runtime.exec(comm) does not accept any command line parameters,
						//it also includes the run-in-background param (&)
						//also redirection is not allowed, code-management of the streams will be necessary
						//The Execution is already done in background by default
						//Normal arguments can be used
						if(command.endsWith("&")) command = command.substring(0,command.length()-1);
						System.out.println("ExecutionAccepted:"+command);
						Runtime rt = Runtime.getRuntime();
						appList.add(rt.exec(command));//.waitFor();
						flagList.add(new Boolean(comp.hasExtendedParam("standAlone")));
						} catch(Exception ex) {
						JOptionPane.showMessageDialog(null,ex.getMessage());
						}
					} else System.out.println("ExecutionRejected");
				}
			});
		}


	
	// 
	
	//Auto configuration of StateComposers for sub-Synoptic files ... It is only related to Devices!!!!
	//DISABLED!!!
	/*if (jdObj.hasExtendedParam("isStateComposer")) {
			String devname = jdObj.getName();
			String param = jdObj.getExtendedParam("isStateComposer");
			System.out.println("The JDObject named "+devname+" has the isStateComposer extension defined as "+param);
	
			//fr.esrf.TangoApi.DeviceData argout = dev.command_inout("",argin);
	
			//String[] deviceNameList;
			Vector deviceNameList = new Vector();
			String[] result = param.split("\\s"); // \\s is the regular expresion constant for " "
			if (result.length==0) {
				System.out.println("No device has been specified for StateComposer");
			} else for (int idev=0;idev<result.length;idev++) {
				System.out.println("Readed from extension param: "+result[idev]);
				if (isDevice(result[idev])) {
					deviceNameList.add(result[idev]);
					System.out.println(result[idev]+"="+deviceNameList.get(idev)+" is Device, added");
				} else if (result[idev].indexOf(jdrawFileFullName)>=0) {
					System.out.println("The whole synoptic cannot be StateComposed recursively!");
				} else if (result[idev].indexOf(".jdw")>0) {
					System.out.println("initializing StateComposer from synoptic file "+result[idev]);
					try {
						fr.esrf.tangoatk.widget.jdraw.TangoSynopticHandler tangoSynopHandler = 
							new fr.esrf.tangoatk.widget.jdraw.TangoSynopticHandler();
						tangoSynopHandler.setSynopticFileName(result[idev]);
						System.out.println("Reading device list ...");
						String[] devlist1 = tangoSynopHandler.getDeviceList();
						System.out.println("The device list readed from "+result[idev]+" is:");
						for (int j=0;j<devlist1.length;j++) { 
							deviceNameList.add(devlist1[j]);
							System.out.print(devlist1[j]+", ");
						}
						System.out.print("\n");
						System.out.println("devlist1 printed directly as array: "+devlist1);
						Vector devlist2 = new Vector(); 
						for (int k=0;k<devlist1.length;k++) devlist2.addElement(devlist1[k]);
						System.out.println("devlist2 printed as vector: "+devlist2);
						System.out.println("devlist2 printed as vector.toArray(String[]): "+devlist2.toArray(new String[1]));
						//System.out.println("devlist2 printed as (String[])vector.toArray(): "+(String[])(devlist2.toArray()));
					} catch (FileNotFoundException  fnfEx) {
						javax.swing.JOptionPane.showMessageDialog(
						null, "Cannot find the synoptic file : " + result[idev] + ".\n"
							+ "Check the file name you entered;"
							+ " Application will abort ...\n"
							+ fnfEx,
							"No such file",
							javax.swing.JOptionPane.ERROR_MESSAGE);
					} catch (IllegalArgumentException  illEx) {
						javax.swing.JOptionPane.showMessageDialog(
						null, "Cannot parse the synoptic file : " + result[idev] + ".\n"
							+ "Check if the file is a Jdraw file."
							+ " Application will abort ...\n"
							+ illEx,
							"Cannot parse the file",
							javax.swing.JOptionPane.ERROR_MESSAGE);
					} catch (MissingResourceException  mrEx) {
						javax.swing.JOptionPane.showMessageDialog(
						null, "Cannot parse the synoptic file : " + result[idev] + ".\n"
							+ " Application will abort ...\n"
							+ mrEx,
							"Cannot parse the file",
							javax.swing.JOptionPane.ERROR_MESSAGE);
					}
				}
			}
			try {
				fr.esrf.TangoApi.DeviceProxy devproxy = new fr.esrf.TangoApi.DeviceProxy(devname);
				fr.esrf.TangoApi.DeviceData argin = new fr.esrf.TangoApi.DeviceData();
				if (deviceNameList.size()>0) {
					argin.insert((String[])deviceNameList.toArray(new String[1]));
					fr.esrf.TangoApi.DeviceData argout = devproxy.command_inout("SetDeviceNameList",argin);
					//String[] answer = argout.extractStringArray();
				}
			} catch (fr.esrf.Tango.DevFailed e) { 
				System.out.println(e.toString()); 
				//throw new fr.esrf.Tango.DevFailed(e); 
			}
		} // End of isStateComposer parsing
		*/
   }

   /**
    * Parses JDraw components , detects tango entity name and attatch a model.
    * This method does not recurse group and use isDevice() , isAttribute()
    * and isDevice() to detect entity name.
    * srubio@cells.es: I've split parseJdrawComponents in two methods to allow objects inside Groups to be parsed.
    * @see #isDevice
    * @see #isAttribute
    * @see #isCommand
    */
   protected void parseJdrawComponents()
   {
     System.out.println("In TangoSynopticHandler::parseJDrawComponents(...) ...");
     for (int i = 0; i < getObjectNumber(); i++) {
	System.out.println("Parsing JDObject "+(i+1)+"/"+getObjectNumber());
       JDObject jdObj = getObjectAt(i);
	parseJdrawComponent(jdObj);
     } // End of for
   }

  /**
   * Return true only if the given name matches a Tango attribute name.
    * <p>Attribute name allowed syntax ( Can be preceded by tango: ):<p>
    * <pre>
    *   Full syntax: //hostName:portNumber/domain/family/member/attName
    *   Full syntax: //ipAddress:portNumber/domain/family/member/attName
    *   Short syntax: domain/family/member/attName
    * </pre>
    * @param s Attribute name
    */
   protected boolean isAttribute(String s)
   {
       String     attDevName, attName;
       int        lastSlash;
       boolean    isdev;

       lastSlash = s.lastIndexOf("/");

       if ( (lastSlash <= 0) || (lastSlash >= s.length()) )
          return false;

       try
       {
	  attDevName = s.substring(0, lastSlash);

	  isdev = isDevice(attDevName);

	  if (isdev == false)
             return false;

	  attName = s.substring(lastSlash, s.length());

	  boolean   attPattern;

	  attPattern = Pattern.matches("/[a-zA-Z_0-9[-]]+", attName);
	  if (attPattern == false)
	     return false;
	  else
             return aFac.isAttribute(s);
       }
       catch (IndexOutOfBoundsException ex)
       {
          return false;
       }
   }

  /**
   * Return true only if the given name matches a Tango command name.
   * <p>Command name allowed syntax ( Can be preceded by tango: ):<p>
   * <pre>
   *   Full syntax: //hostName:portNumber/domain/family/member/cmdName
   *   Full syntax: //ipAddress:portNumber/domain/family/member/cmdName
   *   Short syntax: domain/family/member/cmdName
   * </pre>
   * @param s Command name
   */
   protected boolean isCommand(String s)
   {
       String     cmdDevName, cmdName;
       int        lastSlash;
       boolean    isdev;

       lastSlash = s.lastIndexOf("/");

       if ( (lastSlash <= 0) || (lastSlash >= s.length()) )
          return false;

       try
       {
	  cmdDevName = s.substring(0, lastSlash);

	  isdev = isDevice(cmdDevName);

	  if (isdev == false)
             return false;

	  cmdName = s.substring(lastSlash, s.length());

	  boolean   cmdPattern;

	  cmdPattern = Pattern.matches("/[a-zA-Z_0-9[-]]+", cmdName);
	  if (cmdPattern == false)
	     return false;
	  else
             return cFac.isCommand(s);
       }
       catch (IndexOutOfBoundsException ex)
       {
          return false;
       }
   }

  /**
   * Return true only if the given name matches a Tango device name.
   * <p>Device name allowed syntax ( Can be preceded by tango: ):<p>
   * <pre>
   *   Full syntax: //hostName:portNumber/domain/family/member
   *   Full syntax: //ipAddress:portNumber/domain/family/member
   *   Short syntax: domain/family/member
   * </pre>
   * @param devName Device name
   */
   protected boolean isDevice(String devName)
   {

       // Check syntax
       if(!isDeviceName(devName))
         return false;

       // Now check that the deivce is well defined in the Tango system
       return dFac.isDevice(devName);

   }

  /**
   * Return true if the given name has a correct tango syntax.
   * @param devName Device name to check
   */
   private boolean isDeviceName(String devName)
   {

    boolean   devNamePattern;

    String s = new String(devName);

    // Remove the 'tango:'
    if(s.startsWith("tango:")) s = s.substring(6);

    // Check full syntax: //hostName:portNumber/domain/family/member
    devNamePattern = Pattern.matches("//[a-zA-Z_0-9]+:[0-9]+/[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+", s);

    // Check classic syntax: domain/family/member
    if (devNamePattern == false)
       devNamePattern = Pattern.matches("[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+/[[a-zA-Z_0-9][-]]+", s);

    // Check taco syntax: taco:domain/family/member
    if (devNamePattern == false)
       devNamePattern = Pattern.matches("taco:[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+", s);

    // Change added to support device names beginning with TANGO_HOST ip adress
    // Check full syntax: //ipAddress:portNumber/domain/family/member
    // Modification sent by  "Alan David Zoldan" <alan@dataeco.com.br>
    // Change included by F. Poncet on 15th April 2005
    if (devNamePattern == false)
       devNamePattern = Pattern.matches("//[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+:[0-9]+/[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+/[a-zA-Z_0-9[-]]+", s);

    return devNamePattern;

   }


// Adding a device
// ---------------

   private void addDevice(JDObject jdObj, String s)
   {
      try
      {
	 System.out.println("Adding device " + jdObj.getName());
	 addDeviceListener(dFac.getDevice(s));
	 mouseifyDevice(jdObj);
	 stashComponent(s, jdObj);
	 addDevToStateCashHashMap(s);
      } catch (ConnectionException connectionexception)
      {
	 System.out.println("Couldn't load device " + s + " " +
			    connectionexception);
      }
   }

   private void addDeviceListener(Device device)
   {
      System.out.println("connecting to a device : " + device);
      device.addStateListener(this);
      /* Added on 16/june/2003 to add status tooltip into synoptic */
      device.addStatusListener(this);
      /* Added on 23/june/2003 to add the errors of state reading into error history window */
      if (errorHistWind != null)
         device.addErrorListener(errorHistWind);
   }


   private void mouseifyDevice(JDObject jdObj)
   {
     //System.out.println("Mouseifying object: "+jdObj.getName());
     /* Attach a JDMouse listener to the device component. */
     jdObj.addMouseListener(
             new JDMouseAdapter() {
               public void mousePressed(JDMouseEvent e) {
		//System.out.println("Mouse pressed ("+e.getID()+") on device: "+((JDObject)e.getSource()).getName());
                 deviceClicked(e);
               }
               public void mouseEntered(JDMouseEvent e) {
		 //System.out.println("Mouse entered ("+e.getID()+") on device: "+((JDObject)e.getSource()).getName());
                 devDisplayToolTip(e);
               }
               public void mouseExited(JDMouseEvent e) {
                 devRemoveToolTip();
               }
             });

   }

   private void mouseifyHook(JDObject jdObj)
   {
     //System.out.println("Mouseifying group: "+jdObj.getName());
     /* Attach a JDMouse listener to the device component. */
     jdObj.addMouseListener(
             new JDMouseAdapter() {
               public void mousePressed(JDMouseEvent e) {
		//System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
		hookMoused(e);
               }
               public void mouseEntered(JDMouseEvent e) {
		 //System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
                 hookMoused(e);
               }
               public void mouseExited(JDMouseEvent e) {
		 //System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
                 hookMoused(e);
               }
             });
   }

   private Vector<JDObject> getMatchingObjects(String[] regexps)
   {
 	System.out.println("In TangoSynopticHandler::getMatchingObjects("+regexps.toString()+") ...");
	Vector<JDObject> matches = new Vector<JDObject>();
	//Vector<String> done = new Vector<String>();
	for (int i = 0; i < getObjectNumber(); i++) {
		JDObject jdObj = getObjectAt(i);
		String objname = jdObj.getName();
     		for (int j = 0; j < regexps.length; j++) {
			if (objname.matches(regexps[j])) {
				matches.add(jdObj);
				break;
			}
		}
	} // End of for
	return matches;
   }

   private void hookMoused(JDMouseEvent e) {
	int x=e.getX();
	int y=e.getY();
	JDObject jdg = ((JDObject)e.getSource());
	if (!jdg.hasExtendedParam("eventReceivers")) return;
	String[] regexps = jdg.getExtendedParam("eventReceivers").split(",");
	Vector<JDObject> receivers = getMatchingObjects(regexps);
	for (int i=0; i<receivers.size(); i++) {
		JDObject currChild = receivers.get(i);
		//currChild.fireMouseEvent(e.getID(),e.getSourceEvent());
		if (e.getID() == MouseEvent.MOUSE_PRESSED)
			currChild.processValue(JDObject.MPRESSED,x,y);
		if (e.getID() == MouseEvent.MOUSE_RELEASED)
			currChild.processValue(JDObject.MRELEASED,x,y);
	}
	//fireSizeChanged();
	componentResized(new ComponentEvent((Component)this,ComponentEvent.COMPONENT_SHOWN));
	repaint(buildRepaintRect(receivers));
   }

   private void mouseifyGroup(JDObject jdObj)
   {
     //System.out.println("Mouseifying group: "+jdObj.getName());
     /* Attach a JDMouse listener to the device component. */
     jdObj.addMouseListener(
             new JDMouseAdapter() {
               public void mousePressed(JDMouseEvent e) {
		//System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
		groupMoused(e);
               }
               public void mouseEntered(JDMouseEvent e) {
		 //System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
                 groupMoused(e);
               }
               public void mouseExited(JDMouseEvent e) {
		 //System.out.println("Mouse Event("+e.getID()+") on group: "+((JDObject)e.getSource()).getName());
                 groupMoused(e);
               }
             });
   }

  private void groupMoused(JDMouseEvent e) {
		//System.out.println("Mouse Event on group: "+((JDObject)e.getSource()).getName());
		 int x=e.getX();
		 int y=e.getY();
		/// Horreur!!! findObjects only returns INTERACTIVE Objects!!! (It should be called findInteractiveObjects!)
		 //Vector result = new Vector();
		 //((JDGroup)e.getSource()).findObjectsAt(x,y,result);
		// Using isInsideObject instead ...
			JDGroup    jdg=null;
			int        nbChild=0;
			int        idx;
			JDObject   currChild=null;
			jdg = ((JDGroup)e.getSource());
			nbChild = jdg.getChildrenNumber();
			for (idx=0; idx < nbChild; idx++)
			{
				currChild = jdg.getChildAt(idx);
				if (currChild.hasExtendedParam("ignoreMouse")) continue;
				if (currChild.isInsideObject(x,y) || currChild.hasExtendedParam("groupHook")) {
					//System.out.println("Mouse Event("+e.getID()+") on group - element: "+((JDObject)e.getSource()).getName()+" - "+currChild.getName());
					String s = currChild.getName();
					currChild.fireMouseEvent(e.getID(),e.getSourceEvent());
				}
			}
		

	/*
			if (isDevice(s)) {
				//... code for deviceClicked(e) ...
				theChild.fireMouseEvent(e.getID(),e.getSourceEvent());
			} else {
				// Add attribute before command to avoid that the State attribute
				// is taken as a command.
				// But there is still a potential problem for attributes and commands
				// which have the same name...
				if (isAttribute(s)) {
				//code for attributeClicked(e)
				} else {
				if (isCommand(s)) {
				//code for commandClicked(e)
				} else {
				//System.out.println(s+" is not an attribute, nor a command, nor a device; ignored.");
				}
				}
			}
	*/
  }

  private void mouseifyAttribute(JDObject jdObj)
  {

    /* Attach a JDMouse listener to the attribute component. */
    jdObj.addMouseListener(
            new JDMouseAdapter() {
              public void mousePressed(JDMouseEvent e) {
//System.out.println("Mouse Event(clicked) on object: "+((JDObject)e.getSource()).getName());
                attributeClicked(e);
              }
              public void mouseEntered(JDMouseEvent e) {
//System.out.println("Mouse Event(entered) on object: "+((JDObject)e.getSource()).getName());
                attDisplayToolTip(e);
              }
              public void mouseExited(JDMouseEvent e) {
//System.out.println("Mouse Event(exited) on object: "+((JDObject)e.getSource()).getName());
                attRemoveToolTip();
              }
            });

  }

  private void mouseifyStateAttribute(JDObject jdObj)
  {

    /* Attach a JDMouse listener to the state attribute component. */
    jdObj.addMouseListener(
            new JDMouseAdapter() {
              public void mousePressed(JDMouseEvent e) {
                stateAttributeClicked(e);
              }
              public void mouseEntered(JDMouseEvent e) {
                devDisplayToolTip(e);
              }
              public void mouseExited(JDMouseEvent e) {
                devRemoveToolTip();
              }
            });

  }

  private void deviceClicked(JDMouseEvent evt) {

    JDObject comp = (JDObject) evt.getSource();
    String devName = comp.getName();     // The name of the device
    launchPanel(comp,devName, true);

  }

  private void attributeClicked(JDMouseEvent evt)
  {

    JDObject comp = (JDObject) evt.getSource();
    String attName = comp.getName();
    launchPanel(comp,attName, false);
  }

  private void stateAttributeClicked(JDMouseEvent evt) {

    JDObject comp = (JDObject) evt.getSource();
    String attName = comp.getName();
    int i = attName.lastIndexOf('/');
    if(i>0) {
      String devName = attName.substring(0,i);
      launchPanel(comp,devName, true);
    }

  }
  
  private boolean isNoPanel(String panelName)
  {
      if ( panelName.equalsIgnoreCase("noPanel") )
         return true;
      else
         if ( panelName.equalsIgnoreCase("no panel") )
	    return true;

      return false;
  }

  private void launchPanel(JDObject comp,String compName, boolean isAdevice)
  {

    // Added 27/november/2006 : if className extension IS DEFINED and equals to
    // noPanel then the default panel (atkpanel) IS NOT launched when the JDobject is clicked
    if (comp.hasExtendedParam("className"))
    {
        String   pname = comp.getExtendedParam("className");
        if (isNoPanel(pname)) return;
    }
    
    if (!comp.hasExtendedParam("className"))
    {
       if (isAdevice)
       {
    	   Window w = getPanel("atkpanel.MainPanel",compName);
    	   if (w==null)
    	   {
    		   showDefaultPanel(compName);
    	   }
    	   else
    	   {
    		   showPanelWindow(w);
    	   }
       	}
       	return;
    }

    String clName = comp.getExtendedParam("className");
    String constParam = comp.getExtendedParam("classParam");

    // The case standard for user defined panel class :

    if (constParam.length() == 0)
      constParam = null;

    System.out.println("clName = " + clName + "  constParam = " + constParam + " compName = " + compName);

    Class panelCl;
    Constructor panelClNew;
    Class[] paramCls = new Class[1];
    Object[] params = new Object[1];

    // Passe either the constructor parameter specified by the user or
    // the device name to the class constructor
    if (constParam == null) {
      params[0] = compName;
    } else {
      params[0] = constParam;
    }
    System.out.println("params[0]= " + params[0]);

    // Check whether this panel has already been started
    Window w = getPanel(clName,(String)params[0]);
    if (w!=null)
    {
	showPanelWindow(w);
        return;
    }

    try // Load the class and the constructor (one String argument) of the device panel
    {
       panelCl = Class.forName(clName);
       paramCls[0] = compName.getClass();
       panelClNew = panelCl.getConstructor(paramCls);
    } 
    catch (ClassNotFoundException clex)
    {
       showErrorMsg("The panel class : " + clName + " not found; ignored.\n");
       return;
    }
    catch (Exception e)
    {
       showErrorMsg("Failed to load the constructor " + clName + "( String ) for the panel class.\n");
       return;
    }


    try // Instantiate the device panel class
    {
		Object obj = panelClNew.newInstance(params);
		PanelItem newPanel = addNewPanel(obj,clName,(String)params[0]);
		//if (newPanel != null) // Workaround : to avoid the panel window go behind when excuting throught JVM in Linux
		   showPanelWindow (newPanel.parent);
		System.out.println("New panel has been showed!");
    } 
    catch (InstantiationException instex)
    {
	showErrorMsg("Failed to instantiate 1 the panel class : " + clName + ".\n");
    } 
    catch (IllegalAccessException accesex)
    {
	showErrorMsg("Failed to instantiate 2 the panel class : " + clName + ".\n");
    }
    catch (IllegalArgumentException argex)
    {
	showErrorMsg("Failed to instantiate 3 the panel class : " + clName + ".\n");
    }
    catch (InvocationTargetException invoqex)
    {
	showErrorMsg("Failed to instantiate 4 the panel class : " + clName + ".\n");
	System.out.println(invoqex);
	System.out.println(invoqex.getMessage());
	invoqex.printStackTrace();
    }
    catch (Exception e)
    {
	showErrorMsg("Got an exception when instantiate the panel class : " + clName + ".\n");
    }

  }
  
  private void showErrorMsg(String  msg)
  {
      try // Workaround : to avoid the JOptionPane window go behind when excuting throught JVM in Linux
      {
	   Thread.sleep(100);
      }
      catch (InterruptedException intExcept) { }
      JOptionPane.showMessageDialog(null, msg);  
  }
  
  private void showPanelWindow(Window  pw)
  {
      if (pw == null) return;
// Workaround : to avoid the panel window go behind when excuting throught JVM in Linux

      try
      {
           Thread.sleep(100);
      }
      catch (InterruptedException intExcept) { }
      //pw.show();
/// srubio@cells.es, 2008/06: I had to force setVisible to true to show SimpleSynopticAppli panels
      pw.setVisible(true);
      if (pw.isVisible())
      { 
      //System.out.println("Call pw.toFront()"); 
	 pw.toFront();
	 
      }
  }

  // Return a handle to the panel launched with className and param, null otherwise
  private Window getPanel(String className,String param) {

    boolean found = false;
    int i=0;
    PanelItem panel = null;
    while(i<panelList.size() && !found) {
      panel = (PanelItem)panelList.get(i);
      found = (panel.className.equals(className)) && (panel.param.equals(param));
      if(!found) i++;
    }
    if(found)
      return panel.parent;
    return null;

  }

  private PanelItem addNewPanel(Object obj,String className,String param) {

    PanelItem panel =  new PanelItem(obj,className,param);
    if(panel.parent!=null) {
      panelList.add(panel);
      panel.parent.addWindowListener(this);
      return panel;
    }
    else
        return null;
  }

  public void windowClosed(WindowEvent e) {
    // Search which panel has been closed
    boolean found = false;
    int i=0;
    PanelItem panel = null;
    while(i<panelList.size() && !found) {
      panel = (PanelItem)panelList.get(i);
      found =  (panel.parent== e.getSource());
      if(!found) i++;
    }
    if(found) {
      // Remove this entry from the global list
      panelList.remove(i);
    }
	i=0;
	while (i<appList.size()) {
		System.out.println("TangoSynopticHandler::windowClosed(): Killing external apps ("+i+"/"+appList.size()+")\n");
		if (!(Boolean)flagList.get(i)) {
			Process proc=(Process)appList.get(i);
			proc.destroy();
		}
		i++;
	}
  }

  public void windowOpened(WindowEvent e) {};
  public void windowClosing(WindowEvent e) {};
  public void windowIconified(WindowEvent e){}
  public void windowDeiconified(WindowEvent e) {}
  public void windowActivated(WindowEvent e) {}
  public void windowDeactivated(WindowEvent e) {}

   private void showDefaultPanel(String devName)
   {
      // The default panel is atkpanel.MainPanel in read-only mode
      // atkpanel.MainPanel in read-only mode is instantiated by the following constructor
      // public MainPanel(String  deviceName, Boolean standAlone=false,
      //                          Boolean keepStateRefresherThreadWhenExiting=true,
      //                          Boolean propertyButtonVisible = false,
      //                          Boolean atkpanelReadOnly = true)
      // So the constructor has five arguments one String followed by four Booleans

       Class          atkpanelCl;
       Constructor    atkpanelClNew;
       Class[]        atkpanelParamCls = new Class[5];
       Object[]       params = new Object[5];

System.out.println("showDefaultPanel called");

      try // Load the class and the constructor of the device panel
      {
         atkpanelCl = Class.forName("atkpanel.MainPanel");
      }
      catch (ClassNotFoundException clex)
      {
	 showErrorMsg("showDefaultPanel : atkpanel.MainPanel not found; ignored.\n");
	 return;
      }

      try
      {
         atkpanelParamCls[0] = devName.getClass();
         atkpanelParamCls[1] = Class.forName("java.lang.Boolean");
         atkpanelParamCls[2] = atkpanelParamCls[1];
         atkpanelParamCls[3] = atkpanelParamCls[1];
         atkpanelParamCls[4] = atkpanelParamCls[1];
         atkpanelClNew = atkpanelCl.getConstructor(atkpanelParamCls);
      }
      catch (ClassNotFoundException clex)
      {
	 showErrorMsg("showDefaultPanel :java.lang.Boolean not found; ignored.\n");
	 return;
      }
      catch (Exception e)
      {
	 showErrorMsg("showDefaultPanel : Failed to load the constructor (five arguments) for atkpanel read-only.\n");
	 return;
      }

      // Initialize the values for the constructor arguments
      params[0] = devName; // device name
      params[1] = Boolean.FALSE; // atkpanel.standAlone (don't exit when ending)
      params[2] = Boolean.TRUE; // keepStateRefresher (the stateRefresher thread will be kept running at the end)
      params[3] = Boolean.FALSE; //  the property button (not visible)
      params[4] = Boolean.TRUE; // the atkpanel read only

      try // Instantiate the read-only atkpanel for the device
      {
         Object obj = atkpanelClNew.newInstance(params);
         PanelItem newPanel = addNewPanel(obj,"atkpanel.MainPanel",devName);
	 if (newPanel != null) // Workaround : to avoid the atkpanel window go behind when excuting throught JVM in Linux
	    showPanelWindow (newPanel.parent);
      }
      catch (InstantiationException  instex)
      {
	 showErrorMsg("Failed to instantiate 1 the atkpanel read-only.\n");
      }
      catch (IllegalAccessException  accesex)
      {
	 showErrorMsg("Failed to instantiate 2 the atkpanel read-only.\n");
      }
      catch (IllegalArgumentException argex)
      {
	 showErrorMsg("Failed to instantiate 3 the atkpanel read-only.\n");
      }
      catch (InvocationTargetException invoqex)
      {
	 showErrorMsg("Failed to instantiate 4 the atkpanel read-only.\n");
System.out.println(invoqex);
System.out.println(invoqex.getMessage());
invoqex.printStackTrace();
      }
      catch (Exception e)
      {
	 showErrorMsg("Got an exception when instantiate the default panel : atkpanel readonly.\n");
      }

   }


   private void stashComponent(String s, JDObject jdObj)
   {
      List list = (List)jdHash.get(s);
      if (list == null)
	  list = new Vector();
      list.add(jdObj);
      jdHash.put(s, list);
   }


   private void addDevToStateCashHashMap(String s)
   {
      List        list;
      String      str;

      list = (List)stateCashHash.get(s);
      if (list != null)
         return;

      System.out.println("Adding a new Device to stateCashHash: "+s+"\n");
      list = new Vector();
      str = new String("no status");
      list.add(STATE_INDEX, str);
      list.add(STATUS_INDEX, str);
      stateCashHash.put(s, list);
   }


// Adding a command
// ----------------

  private void addCommand(JDObject jdObj, String s) {

    ICommand cmd = null;

    try {
      cmd = cFac.getCommand(s);
      if (cmd != null) {

        if(jdObj instanceof JDSwingObject) {

          JComponent swingComp = ((JDSwingObject)jdObj).getComponent();
          if(swingComp instanceof VoidVoidCommandViewer) {
            ((VoidVoidCommandViewer)swingComp).setModel(cmd);
          }

        } else {

          // Default behavior
          if (jdObj.isInteractive())
            mouseifyCommand(jdObj, cmd);

        }
        cmd.addErrorListener(this);

      }
    } catch (ConnectionException connectionexception) {
      System.out.println("Couldn't load device for command" + s + " " + connectionexception);
    } catch (DevFailed dfEx) {
      System.out.println("Couldn't find the command" + s + " " + dfEx);
    }

  }

   private void mouseifyCommand(JDObject jdpb, ICommand devCmd)
   {

      final  ICommand  cmd = devCmd;
      /* Attach a mouse listener to the jdpushbutton component for mouse press */
      jdpb.addValueListener ( new JDValueListener() {
        public void valueChanged(JDObject jdObject) {}
        public void valueExceedBounds(JDObject jdObject) {
       	    System.out.println("Acommand is " + cmd);
            commandClicked(cmd);
    	   }
       });

   }

   private void commandClicked(ICommand  ic)
   {
      if (ic instanceof InvalidCommand)
      {
	  javax.swing.JOptionPane.showMessageDialog(this, ic.getName() + " is not supported. ", "Error", 1);
	  return;
      }

      if (ic instanceof VoidVoidCommand)
      {
	  ic.execute();
	  return;
      }

      if ( acv==null )
      {
	  argFrame = new JFrame();
	  acv      = new AnyCommandViewer();
	  argFrame.getContentPane().add(acv);
      }

      acv.initialize(ic);
      acv.setBorder(null);
      acv.setInputVisible(true);
      acv.setDeviceButtonVisible(true);
      acv.setDescriptionVisible(true);
      acv.setInfoButtonVisible(true);

      if (!ic.takesInput())
      {
	  ic.execute();
      }

      argFrame.setTitle(ic.getName());
      argFrame.pack();
      argFrame.setVisible(true);
   }


// Adding an attribute
// -------------------

  private void addStateScalarAttribute(JDObject jdObj,IDevStateScalar model) {

    String attName = model.getName();
    System.out.println("Connecting to a StateScalar attribute : " + attName);
    mouseifyStateAttribute(jdObj);
    stashComponent(attName, jdObj);
    addDevToStateCashHashMap(attName);
    model.addDevStateScalarListener(this);
    allAttributes.add(model);
    if (errorHistWind != null)
       model.addErrorListener(errorHistWind);

  }

  private void addBooleanScalarAttribute(JDObject jdObj,IBooleanScalar model) {

    if (jdObj instanceof JDSwingObject) {

      JComponent atkObj = ((JDSwingObject) jdObj).getComponent();

      if (atkObj instanceof BooleanScalarCheckBoxViewer) {
        ((BooleanScalarCheckBoxViewer) atkObj).setAttModel(model);
        allAttributes.add(model);
        model.addSetErrorListener(errPopup);
        if (errorHistWind != null)
           model.addErrorListener(errorHistWind);
      } else {
        System.out.println(atkObj.getClass().getName() + " does not accept IBooleanScalar model");
      }

    }

  }

  private void addNumberScalarAttribute(JDObject jdObj,INumberScalar model)
  {
     if (jdObj instanceof JDSwingObject)
     {
	JComponent atkObj = ((JDSwingObject) jdObj).getComponent();

	if (atkObj instanceof SimpleScalarViewer)
	{
	  ((SimpleScalarViewer) atkObj).setModel(model);
	  ((SimpleScalarViewer) atkObj).setHasToolTip(true);
	  allAttributes.add(model);
	}
	else 
	   if (atkObj instanceof NumberScalarWheelEditor)
	   {
	      ((NumberScalarWheelEditor) atkObj).setModel(model);
	      allAttributes.add(model);
	      model.addSetErrorListener(errPopup);
	   }
	   else
	      if (atkObj instanceof NumberScalarComboEditor)
	      {
		 String valList = jdObj.getExtendedParam("valueList");
		 if (valList != null)
		 {
		    if (valList.length() != 0)
		    {
		       double [] possVals=parsePossNumberValues(valList);
		       if (possVals != null)
		          if (possVals.length != 0)
			     model.setPossibleValues(possVals);
		    }
		 }
        	 ((NumberScalarComboEditor) atkObj).setNumberModel(model);
        	 allAttributes.add(model);
        	 model.addSetErrorListener(errPopup);
	      }
	      else
	      {
		System.out.println(atkObj.getClass().getName() + " does not accept INumberScalar model");
	      }
     }
     else
     {
	// Default behavior for JDBar,JDSlider and JDObject value (dyno).
	mouseifyAttribute(jdObj);
	String attName = model.getName();
	System.out.println("connecting to a NumberScalar attribute : " + attName);
	allAttributes.add(model);
	model.addNumberScalarListener(this);
	stashComponent(model.getName(), jdObj);
     }

     if (errorHistWind != null)
	model.addErrorListener(errorHistWind);
  }
  
  private double[]  parsePossNumberValues(String vals)
  {
     String[] c = vals.split(",");
     if (c.length == 0)
	return null;

     if (c.length < 0)
     {
	return null;
     }
     else
     {
	double[]  dvals = new double[c.length];
	int  j=0;
	for (int i=0; i<c.length; i++)
	{
	   try
	   {
	       double dval = Double.parseDouble(c[i]);
	       dvals[j] = dval;
	       j++;		       
	   }
	   catch (Exception  ex)
	   {
               continue;
	   }
	}
	if (j<=0)
	   return null;
	if (j != c.length) //Copy into a new array with an appropriate length
	{
	   double[]  retVals = new double[j];
	   for (int i=0; i<j; i++)
	      retVals[i] = dvals[i];
	   
	   return retVals;
	}
	else
	   return dvals;
     }
  }

  private void addNumberSpectrumAttribute(JDObject jdObj,INumberSpectrum model) {

    if (jdObj instanceof JDSwingObject) {
      JComponent atkObj = ((JDSwingObject) jdObj).getComponent();

      if (atkObj instanceof NumberSpectrumViewer) {
        ((NumberSpectrumViewer) atkObj).setModel(model);
        allAttributes.add(model);
        if (errorHistWind != null)
           model.addErrorListener(errorHistWind);
      } else {
        System.out.println(atkObj.getClass().getName() + " does not accept INumberSpectrum model");
      }
    }

  }

  private void addNumberImageAttribute(JDObject jdObj,INumberImage model) {

     if (jdObj instanceof JDSwingObject) {
       JComponent atkObj = ((JDSwingObject) jdObj).getComponent();

       if (atkObj instanceof NumberImageViewer) {
         ((NumberImageViewer) atkObj).setModel(model);
         allAttributes.add(model);
         if (errorHistWind != null)
            model.addErrorListener(errorHistWind);
       } else {
         System.out.println(atkObj.getClass().getName() + " does not accept INumberImage model");
       }
     }

   }

  private void addStringScalarAttribute(JDObject jdObj,IStringScalar model)
  {
     if (jdObj instanceof JDSwingObject)
     {
	JComponent atkObj = ((JDSwingObject) jdObj).getComponent();

	if (atkObj instanceof SimpleScalarViewer)
	{
		((SimpleScalarViewer) atkObj).setModel(model);
		allAttributes.add(model);
		if (errorHistWind != null)
		model.addErrorListener(errorHistWind);
	}
	else if (atkObj instanceof StringScalarComboEditor) 
	{
		String valList = jdObj.getExtendedParam("valueList");
		if (valList != null)
		{
			if (valList.length() != 0)
			{
			String[] possStrVals=parsePossStringValues(valList);
			if (possStrVals != null)
				if (possStrVals.length != 0)
				model.setPossibleValues(possStrVals);
			}
		}
		((StringScalarComboEditor) atkObj).setStringModel(model);
		allAttributes.add(model);
		model.addSetErrorListener(errPopup);
	}
	else
	{
		System.out.println(atkObj.getClass().getName() + " does not accept IStringScalar model");
	}
     }
  }
  
  private String[]  parsePossStringValues(String vals)
  {
     String[] c;
     
     try
     {
        c = vals.split(",");
     }
     catch (Exception ex)
     {
        c = null;
     }
     return c;
  }

  private void addAttribute(JDObject jddg, String s) {
    IAttribute att = null;

    try {
      att = aFac.getAttribute(s);

	///srubio@cells.es: I refactored this switch/case to mouseify those type of attributes not mouseified by default
      if (att != null) {
        // DevStateScalar attributes
        if(att instanceof IDevStateScalar)
          addStateScalarAttribute(jddg,(IDevStateScalar)att);
        // BooleanScalar attributes
        else if (att instanceof BooleanScalar) 
          addBooleanScalarAttribute(jddg,(IBooleanScalar) att);
        // NumberScalar attributes
        else if (att instanceof INumberScalar)
          addNumberScalarAttribute(jddg,(INumberScalar) att);
        // StringScalar attributes
        else if (att instanceof IStringScalar)
          addStringScalarAttribute(jddg,(IStringScalar) att);
        // NumberSpectrum attributes
        else if (att instanceof INumberSpectrum)
          addNumberSpectrumAttribute(jddg,(INumberSpectrum) att);
        // Number image attribute
        else if (att instanceof INumberImage)
          addNumberImageAttribute(jddg,(INumberImage) att);

	if (!jddg.hasExtendedParam("ignoreMouse"))// && !jddg.hasMouseListener()) 
		mouseifyAttribute(jddg);
      }

    } catch (ConnectionException connectionexception) {
      System.out.println("Couldn't load device for attribute" + s + " " + connectionexception);
    } catch (DevFailed dfEx) {
      System.out.println("Couldn't find the attribute" + s + " " + dfEx);
    }

  }



// Implement the interface methods for synoptic animation
// -------------------------------------------------------


   // Interface INumberScalarListener
   public void numberScalarChange(NumberScalarEvent evt) {

     JDObject jdObj;
     INumberScalar ins;
     double value = evt.getValue();

     ins = null;
     ins = evt.getNumberSource();

     String s = ins.getName();

     if (ins != null) {

       List list = (List) jdHash.get(s);
       if (list == null)
         return;

       int nbJdObjs = list.size();
       int i;

       for (i = 0; i < nbJdObjs; i++) {
         jdObj = null;
         jdObj = (JDObject) list.get(i);

         if (jdObj != null) {

           // Sets the dyno value
           if (jdObj.isProgrammed()) {
             int jdValue = 0;
             if(!Double.isNaN(value))
               jdValue = (int)Math.rint(value);
             if(jdObj.getValue()!=jdValue) {
               jdObj.preRefresh();
               jdObj.setValue(jdValue);
               jdObj.refresh();
             }
           }

           // Management for specific JDObject
           if (jdObj instanceof JDBar) {
             JDBar bar = (JDBar) jdObj;
             if(bar.getBarValue()!=value) {
               bar.setBarValue(value);
               jdObj.refresh();
             }
           } else if (jdObj instanceof JDSlider) {
             JDSlider slider = (JDSlider) jdObj;
             if(slider.getSliderValue()!=value) {
               jdObj.preRefresh();
               ((JDSlider) jdObj).setSliderValue(value);
               jdObj.refresh();
             }
           }

         }
       }

     }

   }


   // Interface INumberScalarListener (superclass of IStateListener and INumberScalarListener)
   public void stateChange(AttributeStateEvent evt)
   {
   }

   // Interface ISetErrorListener
   /*
   public void setErrorOccured(ErrorEvent e) {
     Object source = e.getSource();
     if(source instanceof IEntity) {
       IEntity model = (IEntity)source;
       ErrorPane.showErrorMessage(this,model.getName(),(ATKException)e.getError());
     }
   }
   */

   // Interface IErrorListener (superclass of IStateListener and INumberScalarListener)
   public void errorChange(ErrorEvent event)
   {

     Object source = event.getSource();

     if( source instanceof IDevStateScalar ) {
       IDevStateScalar src = (IDevStateScalar)event.getSource();
       String state = Device.UNKNOWN;
       manageStateChange(src.getName() , state);
       return;
     }

     if( source instanceof INumberScalar ) {
       // What should we do here ?
       // Let's fire NaN
       NumberScalarEvent e = new NumberScalarEvent((INumberScalar)source,Double.NaN,event.getTimeStamp());
       numberScalarChange(e);
       return;
     }

     if( source instanceof ICommand ) {
       ICommand src = ((ICommand)source);
       ErrorPane.showErrorMessage(this,src.getName(),(ATKException)event.getError());
     }

   }

  private void manageStateChange(String entityName, String state) {

    //long before, after, duree;
    //before = System.currentTimeMillis();

    // Update and test the "cashed" state
    List stateStatusCash = null;

    stateStatusCash = (List) stateCashHash.get(entityName);
    if (stateStatusCash != null) {
      String stateCash = null;
      try {
        stateCash = (String) stateStatusCash.get(STATE_INDEX);

        if (stateCash != null) {
          if (stateCash.equals(state))
            return;
        }

        stateCash = new String(state);
        stateStatusCash.set(STATE_INDEX, stateCash);
        stateCashHash.put(entityName, stateStatusCash);
      } catch (IndexOutOfBoundsException iob) {
      }
    }

    // Here we are sure that the new state is different from the "cashed" state
    // System.out.println("State has changed for " + entityName + " : " + state);
    JDObject jdObj;

    List list = (List) jdHash.get(entityName);
    if (list == null)
      return;

    int nbJdObjs = list.size();
    int i;

    for (i = 0; i < nbJdObjs; i++) {
      jdObj = (JDObject) list.get(i);
      if (jdObj.isProgrammed()) {
        jdObj.setValue(getDynoState(state));
        jdObj.refresh();
      } 
      //if (!jdObj.isProgrammed() || jdObj.hasExtendedParam("tangoColors"))  // not a Dyno
      if (!jdObj.hasExtendedParam("ignoreRepaint"))  // not a Dyno
      {
        changeJDobjColour(jdObj, state);
      }
    }

    //System.out.println("Left state change for "+s);
    //after = System.currentTimeMillis();
    //duree = after - before;
    //System.out.println("TangoSynopticHandler.stateChange took "+  duree + " milli seconds.");

  }

   // Interface IDevStateScalarListener (Listen on attribute state change)
   public void devStateScalarChange(DevStateScalarEvent event) {

     IDevStateScalar src = (IDevStateScalar)event.getSource();
     String state = event.getValue();
     manageStateChange(src.getName() , state);

   }

   // Interface IStateListener
   public void stateChange(StateEvent event)
   {

      Device device = (Device)event.getSource();
      String state = event.getState();
      manageStateChange(device.getName(),state);

   }


   /* 1- If the JDobject associated with the device is not a JDgroup only the background
      colour will change if the JDobject is filled and if it is not filled the
      foreground will change instead.
      2- If the JDobject associated with the device is a JDgroup all the children of
      the group are examined. For each child if the JDobject names equals to the string
      "IgnoreRepaint" none of the colours is changed. If the name is not
      "IgnoreRepaint" only the background colour is changed if filled, the
      forground colour if not filled and the children are examined recursively if
      the object is a group. */
   private void changeJDobjColour (JDObject jdo, String state)
   {
      //System.out.println("changeJDobjColour("+jdo.getName()+","+state+")");
      if (jdo.getName().equalsIgnoreCase("IgnoreRepaint") || jdo.hasExtendedParam("IgnoreRepaint") || jdo.hasExtendedParam("ignoreRepaint")) 
	 return;
      if (jdo instanceof JDGroup && !jdo.hasExtendedParam("tangoColors"))
      {
         changeJDgroupColour(jdo, state);
	 return;
      }

      if (jdo.getFillStyle() == JDObject.FILL_STYLE_NONE)
	jdo.setForeground(ATKConstant.getColor4State(state));
      else
	jdo.setBackground(ATKConstant.getColor4State(state));
      jdo.refresh();
   }


   private void changeJDgroupColour (JDObject jdo, String state)
   {
      JDGroup    jdg=null;
      int        nbChild=0;
      int        idx;
      JDObject   currChild=null;

      if (!(jdo instanceof JDGroup))
	 return;

      //System.out.println("changeJDgroupColour("+jdo.getName()+","+state+")");

      if (jdo.getName().equalsIgnoreCase("IgnoreRepaint") || jdo.hasExtendedParam("IgnoreRepaint") || jdo.hasExtendedParam("ignoreRepaint")) {
	 //System.out.println(jdo.getName()+" has an ignoreRepaint extension");
	 return;
	}

      jdg = (JDGroup) jdo;
      nbChild = jdg.getChildrenNumber();
      for (idx=0; idx < nbChild; idx++)
      {
	 currChild = jdg.getChildAt(idx);
	 if (currChild == null) continue;
	 else changeJDobjColour((JDObject)currChild,state);
/*
	 if (currChild.getName().equalsIgnoreCase("IgnoreRepaint") || currChild.hasExtendedParam("ignoreRepaint"))
	    continue;

	 if (currChild instanceof JDGroup)
	 {
            changeJDgroupColour(currChild, state);
	    continue;
         }


	 // Change the colour of the object inside a group 
	 if (currChild.getFillStyle() == JDObject.FILL_STYLE_NONE)
	   currChild.setForeground(ATKConstant.getColor4State(state));
	 else
	   currChild.setBackground(ATKConstant.getColor4State(state));
	 currChild.refresh();
*/
      }
   }


   // Interface IStatusListener
   public void statusChange(StatusEvent event)
   {

      Device device = (Device)event.getSource();
      String s = device.getName();

      List  stateStatusCash = null;

      stateStatusCash = (List) stateCashHash.get(s);
      if (stateStatusCash != null)
      {
         String  statusCash = null;

	 try
	 {
	    statusCash = (String) stateStatusCash.get(STATUS_INDEX);

	    if (statusCash != null)
	    {
	       if (statusCash.equals(event.getStatus()))
		  return;
	    }

	    statusCash = new String(event.getStatus());
	    stateStatusCash.set(STATUS_INDEX, statusCash);
            stateCashHash.put(s, stateStatusCash);
	 }
	 catch (IndexOutOfBoundsException  iob)
	 {
	    return;
	 }
      }
      /* */
   }

   private int getDynoState(String deviceState)
   {
      Integer   intObj;

      intObj = (Integer) dynoState.get(deviceState);
      return (intObj.intValue());
   }

   /** srubio@cells.es: modified to disable tooltips using noTooltip extension.
    */
   private void devDisplayToolTip(JDMouseEvent e)
   {
       String              devName;
       JDObject            jdObj;
       List                stateStatusCash = null;
       String              stateCash = null;

       if ( toolTipMode == TOOL_TIP_NONE )
       {
          setToolTipText(null);
	      return;
       }

       jdObj = (JDObject)e.getSource();
       if (jdObj.hasExtendedParam("noTooltip")) {
		setToolTipText(null);
		return;
	}

       devName = jdObj.getName();     // The name of the device

       if ( toolTipMode == TOOL_TIP_NAME)
       {
          setToolTipText(devName);
	  return;
       }

       if ( toolTipMode == TOOL_TIP_STATE)
       {
	  // get the "cashed" state for the device
	  stateStatusCash = (List) stateCashHash.get(devName);
	  if (stateStatusCash == null)
	  {
	     setToolTipText(null);
	     return;
	  }

	  try
	  {
	     stateCash = (String) stateStatusCash.get(STATE_INDEX);
	     if (stateCash == null)
	     {
		setToolTipText(null);
		return;
	     }

	     setToolTipText(stateCash);
	     return;
	  }
	  catch (IndexOutOfBoundsException  iob)
	  {
	     setToolTipText(null);
	     return;
	  }
       }

       setToolTipText(null);
   }

   private void devRemoveToolTip()
   {
       setToolTipText(null);
   }

   private void attDisplayToolTip(JDMouseEvent e)
   {
       String              attName;
       JDObject            jdObj;

       if ( toolTipMode != TOOL_TIP_NAME )
       {
          setToolTipText(null);
	      return;
       }

       jdObj = (JDObject)e.getSource();
       if (jdObj.hasExtendedParam("noTooltip")) {
		setToolTipText(null);
		return;
	}

       attName = jdObj.getName();     // The name of the attribute
//System.out.println("setToolTipText("+attName+")");
       setToolTipText(attName);
   }

   private void attRemoveToolTip()
   {
//System.out.println("removeToolTipText()");
       setToolTipText(null);
   }

   public static void main(String args[]) {

     TangoSynopticHandler tsh = null;

     try {
       //DeviceFactory.getInstance().setTraceMode(DeviceFactory.TRACE_REFRESHER);
       //tsh = new TangoSynopticHandler("/segfs/tango/jclient/JLinac/jdraw_file/test_taco.jdw");
       tsh = new TangoSynopticHandler("Z:/atk_test/jdraw/jlinac-atts.jdw",TOOL_TIP_NAME);
     } catch (Exception e) {
       System.out.println(e);
       System.out.println("Prog Aborted.");
       System.exit(-1);
     }

     JFrame jf = new JFrame();
     // Exit via 'window closing'.
     jf.addWindowListener(new WindowAdapter() {
       public void windowClosing(WindowEvent e) {
         System.exit(0);
       }
     });

     jf.setContentPane(tsh);
     jf.pack();
     jf.setVisible(true);

   }


}

/**
 * Class which handle panel unicity.
 */
class PanelItem {

  Window parent = null;
  String className = "";
  String param = "";

  PanelItem(Object parent,String className,String param) {

    if(parent instanceof Window) {
      this.parent = (Window)parent;
    } else {
      System.out.println("Warning, " + className + "is not a Window");
    }
    this.className = className;
    this.param = param;

  }

}
