// File:          SynopticFileViewer.java
// Created:       2004-11-09 15:22:29, poncet
// By:            <poncet@esrf.fr>
// Time-stamp:    <2004-11-09 15:22:29, poncet>
// 
// $Id$
// 
// Description:       

package fr.esrf.tangoatk.widget.jdraw;

/**
 *
 * @author  root
 */
import java.awt.event.*;
import java.util.*;
import java.io.*;
import javax.swing.JFrame;

import fr.esrf.tangoatk.widget.util.ErrorHistory;

public class SynopticFileViewer extends TangoSynopticHandler
{

    private String                 jdrawDir = null;    
    private String                 jdrawFileName = null;


    public SynopticFileViewer()
    {
	super();
    }
 
    public SynopticFileViewer(String  jdrawf)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
        this();
        setJdrawFileName(jdrawf);
    }
  
    public SynopticFileViewer(String jdrawd, String  jdrawf)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
        this();
	setJdrawDir(jdrawd);
        setJdrawFileName(jdrawf);
    }
    
    
    public String getJdrawDir()
    {
	String   fn = null;
	
	fn = getSynopticFileName();
	
	if (fn != null)
	{
	   int  indSlash = fn.lastIndexOf('/');
	   try
	   {
	      jdrawDir = fn.substring(0, indSlash-1);
	   }
	   catch (Exception ex)
	   {
	      jdrawDir = null;
	   }
	}
	return jdrawDir;
    }  
    
    
    public void setJdrawDir(String newDir)
    {
	String   fn = null;
	
	fn = getSynopticFileName();
	
	if (fn != null)
	   return;

	if (newDir == null)
	   return;
	if (newDir.length() <= 0)
	   return;
	jdrawDir = new String(newDir);
    }
    
    
   
     
    
    public String getJdrawFileName()
    {
	String   fn = null;
	
	fn = getSynopticFileName();
	
	if (fn == null)
	   jdrawFileName = null;
	else
	{
	   int  indSlash = fn.lastIndexOf('/');
	   int  fnSize = fn.length();
	   try
	   {
	      jdrawFileName = fn.substring(indSlash+1, fnSize-1);
	   }
	   catch (Exception ex)
	   {
	      jdrawFileName = null;
	   }
	}
	return jdrawFileName;
    }  
     
    
    public void setJdrawFileName(String   jdrawf)
              throws MissingResourceException, FileNotFoundException, IllegalArgumentException
    {
       String          fullFileName;

       jdrawFileName = jdrawf;
       
       if (getJdrawDir() == null)
          fullFileName = jdrawFileName;
       else
          fullFileName =  getJdrawDir() + "/" + jdrawFileName;
	  
       
       setSynopticFileName(fullFileName);

    }  


    /**
    * @param args the command line arguments
    */
    public static void main(String args[])
    {
      SynopticFileViewer  sfv;

      JFrame jf = new JFrame();
      // Exit via 'window closing'.
      jf.addWindowListener(  new WindowAdapter()
				 {
				     public void windowClosing(WindowEvent e)
				     {
				       System.exit(0);
				     }
				 });

       ErrorHistory errorHistory = new ErrorHistory();

       try
       {
          sfv = new SynopticFileViewer();
	  sfv.setErrorHistoryWindow(errorHistory);
	  sfv.setToolTipMode(TangoSynopticHandler.TOOL_TIP_NAME);
	  sfv.setAutoZoom(true);
          sfv.setJdrawDir("/segfs/tango/jclient/JLinac/jdraw_file");
          sfv.setJdrawFileName("jlinac.jdw");
          jf.setContentPane(sfv);
       }
       catch (Exception e)
       {
          System.out.println(e);
	  System.out.println("Prog Aborted.");
	  System.exit(-1);
       }
       
       jf.pack();
       jf.setVisible(true);
    }


}
