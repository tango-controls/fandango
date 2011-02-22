// File:          DeviceSynopticFrame.java
// Created:       2004-11-09 15:22:29, poncet
// By:            <poncet@esrf.fr>
// Time-stamp:    <2004-11-09 15:22:29, poncet>
// 
// $Id$
// 
// Description:       


package fr.esrf.tangoatk.widget.jdraw;


import java.awt.event.*;
import java.util.*;
import java.io.*;
import javax.swing.JFrame;


public class DeviceSynopticFrame extends javax.swing.JFrame
{
    //private static final String    defaultJdrawDir = "/users/poncet/ATK_OLD/jloox_files";
    private static final String    defaultJdrawDir = ".";

    private String                 jdrawDir = null;    
    private String                 devName = null;
    private DeviceSynopticViewer   dsv = null;


    public DeviceSynopticFrame()
    {
	System.out.println("DeviceSynopticFrame on constructor 1 ...");
	initComponents();
    }

 
    public DeviceSynopticFrame(String  dev)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
	this();
	System.out.println("DeviceSynopticFrame on constructor 2 ...");
	jdrawDir = defaultJdrawDir;
        setDevName(dev);
        setContentPane(dsv);
	pack();
	setVisible(true);
    }
  
    public DeviceSynopticFrame(String jdrd, String  dev)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
        this();
	System.out.println("DeviceSynopticFrame on constructor 3 ...");
	setJdrawDir(jdrd);
        setDevName(dev);
        setContentPane(dsv);
	pack();
	setVisible(true);
    }
    
    
    public String getJdrawDir()
    {
	return jdrawDir;
    }  
    
    
    public void setJdrawDir(String newDir)
    {
        if (newDir == null)
	   return;
	if (newDir.length() <= 0)
	   return;
	jdrawDir = new String(newDir);
    }
     
    
    public String getDevName()
    {
	return devName;
    }  
     
    
    public void setDevName(String   dev)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
       String          fullFileName;

       devName = dev;
       dsv = new DeviceSynopticViewer(jdrawDir, dev);
    }  

    
    public String getFileNameFromDev(String dev)
    {
        String     devFile;
	int        firstSlash, secondSlash;
	
	if (dev == null)
	   return dev;
	   
	devFile = dev.replace('/', '_');	
	return(devFile);
    }
    
    
    private void initComponents()
    {//initComponents
       addWindowListener(  
                 new WindowAdapter()
                     {
                	  public void windowClosing(java.awt.event.WindowEvent evt)
			  {
                	      exitForm(evt);
                	  }
		      });
    }//initComponents
    
    private void exitForm(java.awt.event.WindowEvent evt)
    {
       this.dispose();
    }
     
    /**
    * @param args the command line arguments
    */
    public static void main(String args[])
    {
       String              deviceName;
       WindowListener[]    wl;
       
       System.out.println("DeviceSynopticFrame on main ...");
       if (args.length <= 0)
          deviceName = "id14/eh3_mono/diamond";
       else
          deviceName = args[0];
	  
       try
       {
	  DeviceSynopticFrame  dsf = new DeviceSynopticFrame(deviceName);
	  wl = dsf.getWindowListeners();
	  for (int i = 0; i < wl.length; i++)
	  {
	     dsf.removeWindowListener(wl[i]);
	     System.out.println("windowListener["+i+"]");
	  }

	  dsf.addWindowListener(
	         new WindowAdapter()
                     {
                	public void windowClosing(java.awt.event.WindowEvent evt)
			{
                	    System.exit(0);
                	}
                     });
       }
       catch (Exception e)
       {
          System.out.println(e);
	  System.out.println("Prog Aborted.");
	  System.exit(-1);
       }
      
    }


}
