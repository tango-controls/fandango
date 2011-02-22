// File:          ViewerMain.java
// Created:       2002-12-13 12:55:59, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2002-12-13 13:52:56, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.io.*;
import java.awt.*;

/**
 * Main class for device tree application in "user" mode
 * 
 * @author Erik ASSUM
 */
public class ViewerMain extends Main {

    /**
     * Default constructor
     * 
     * @param args
     *            arguments given in shell
     */
    public ViewerMain(String[] args) {
        isAdmin = false;
        file = new File(args[0]);
        initComponents();
        /**       mainFrame.show();*/
    	mainFrame.pack();
    	mainFrame.setVisible(true);

    	String s = globalTrend.getSettings();
    	System.out.println("Updating globalTrend settings, modifying background\n");
    	s=s.replace("graph_background:180,180,180","graph_background:246,245,244");
    	globalTrend.setSetting(s);
    	
        open(file);
    }

    /**
     * Constructor for ATK JLoox synoptic handler
     * 
     * @param filename
     *            the name of the file to load on startup
     */
    public ViewerMain(String filename) {
        isAdmin = false;
        runningFromShell = false;
        file = new File(filename);
        initComponents();
 /**       mainFrame.show();*/
    	mainFrame.pack();
    	mainFrame.setVisible(true);

    	String s = globalTrend.getSettings();
    	System.out.println("Updating globalTrend settings, modifying background\n");
    	s=s.replace("graph_background:180,180,180","graph_background:246,245,244");
    	globalTrend.setSetting(s);
    	
        open(file);
    }

    /**
     * To set appearence constraints
     * 
     * @param constraints
     *            the constraints
     */
    protected void specificSetup(GridBagConstraints constraints) {
        mainFrame.getContentPane().add(viewSplit, constraints);
    }

    /**
     * useless (empty)
     */
    public void newFile() {
        // we ain't doing any new files here
    }

    /**
     * useless (empty)
     */
    public void save(File f) {
        // we aint' saving anything here
    }

}