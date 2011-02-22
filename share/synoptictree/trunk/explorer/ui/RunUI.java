// File: RunIU.java
// Created: 2002-09-26 10:50:19, erik
// By: <erik@assum.net>
// Time-stamp: <2003-01-30 12:55:10, erik>
// 
// $Id$
// 
// Description:

package explorer.ui;

import java.awt.event.*;
import javax.swing.*;

import fr.esrf.tangoatk.core.IDevice;

/**
 * <code>RunUI</code> is responsible for setting up the run part of the menu- and tool-bar.
 */
public class RunUI {
    protected static boolean jive = false;

    protected static boolean atkpanel = false;

    public static String JIVE = "jive3.MainPanel";

    public static String ATKPANEL = "atkpanel.MainPanel";
    
    public static String JDRAW = "fr.esrf.tangoatk.widget.util.jdraw.JDrawEditorFrame";

    static {
        jiveCheck();
        atkCheck();
    }

    /**
     * constructor
     * 
     * @param toolbar
     *            the tool bar in which icons will be set
     * @param menubar
     *            the menu bar containing the "run" menu
     */
    public RunUI(JToolBar toolbar, DTMenuBar menubar) {
        JMenu menu = new JMenu("Run");
        UIBit jiveBit;
        UIBit atkPanelBit;
        UIBit mamboBit;
        UIBit jdrawBit;

        jiveBit = new UIBit("Run jive...", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                runJive();
            }
        });

        atkPanelBit = new UIBit("Run atkpanel...", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                runAtkPanel();
            }
        });
        
        jdrawBit = new UIBit("Run jdraw...", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                runJdraw();
            }
        });  
        
        mamboBit = new UIBit("Run mambo...", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                runMambo();
            }
        });              

        jiveBit.setEnabled(false);//jive);
        atkPanelBit.setEnabled(atkpanel);
        jdrawBit.setEnabled(true);
        mamboBit.setEnabled(true);
        menu.setMnemonic('U');
        menu.add(jiveBit.getItem());
        //	menu.add(atkPanelBit.getItem());
        menu.add(jdrawBit.getItem());
        menu.add(mamboBit.getItem());
        menubar.addMenu(menu);
    }

    /**
     * <code>runAtkPanel</code> runs ATKPanel if it is available.
     *  
     */
    public static void runAtkPanel() {
        if (atkpanel) {
            String[] args = new String[0];
            new atkpanel.MainPanel(args);
        }
    }

    /**
     * <code>runAtkPanel</code> runs ATKPanel if it is available.
     * 
     * @param device
     *            the <code>IDevice</code> AtkPanel has to watch
     */
    public static void runAtkPanel(IDevice device) {
        if (atkpanel) {
            final String[] args = new String[1];
            args[0] = device.getName();
            new Thread() {
                public void run() {
                    new atkpanel.MainPanel(args);
                }
            }.start();
        }
    }

    /**
     * <code>runJive</code> runs Jive if it is available.
     *  
     */
    public static void runJive() {
        if (jive) {
            new jive3.MainPanel();
        }
    }
    
    public static void runJdraw() {
    	if (System.getProperty("JDRAW_PATH")=="") 
    		System.setProperty("JDRAW_PATH","jdraw");    	
    	String command = System.getProperty("JDRAW_PATH");

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
    		rt.exec(command);//.waitFor();
    	} catch(Exception ex) {
    		JOptionPane.showMessageDialog(null,"Failed while executing command: "+command+"\n Exception was: "
    				+ex.getMessage()+ex.toString());
    		System.out.println("ExecutionRejected");    	
    	}    	
    	/*
   	 	System.out.println("Launching JDRAW");
    	try {
    		if (System.getProperty("LIBPATH")=="") 
    			System.setProperty("LIBPATH","/homelocal/sicilia/var/jdraw_lib");
    	} catch(Exception ex) {
    		System.setProperty("LIBPATH","/homelocal/sicilia/var/jdraw_lib");
    	}
    	try {
    		new fr.esrf.tangoatk.widget.util.jdraw.JDrawEditorFrame();
    	} catch(Exception e2) {
    		System.out.println("Exception in JDraw");
    		System.out.println(e2.getMessage());
    	}
    	 */
    }
    
    public static void runMambo() {
	   	 if (System.getProperty("MAMBO_PATH")=="") 
				System.setProperty("MAMBO_PATH","mambo");    	
	   	 String command = System.getProperty("MAMBO_PATH");    	
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
    		 rt.exec(command);//.waitFor();
    	 } catch(Exception ex) {
    		 JOptionPane.showMessageDialog(null,ex.getMessage());
    		 System.out.println("ExecutionRejected");    	
    	 }
    }

    /**
     * <code>isJiveAvailable</code>
     * 
     * @return a <code>boolean</code> value which is true if jive is
     *         available, that is <code>jive.MainPanel</code> is in the
     *         CLASSPATH
     */
    public static boolean isJiveAvailable() {
        return jive;
    }

    /**
     * <code>isATKPanelAvailable</code>
     * 
     * @return a <code>boolean</code> value which is true if ATKPanel is
     *         available, that is <code>apps.atkpanel.MainPanel</code> is in
     *         the CLASSPATH
     */
    public static boolean isATKPanelAvailable() {
        return atkpanel;
    }

    /**
     * checks if jive is available
     */
    protected static void jiveCheck() {
        try {

            Class.forName(JIVE);
            jive = true;
        } catch (Exception e) {
            ;
        }
    }

    /**
     * checks if AtkPanel is available
     */
    protected static void atkCheck() {
        try {
            Class.forName(ATKPANEL);
            atkpanel = true;
        } catch (Exception e) {
            ;
        }
    }
}
