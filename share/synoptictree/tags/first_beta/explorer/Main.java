// File:          Main.java
// Created:       2002-09-13 12:33:17, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-16 15:33:11, erik>
// 
// $Id$
// 
// Description:       
//@SuppressWarnings("unchecked")
package explorer;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.*;
import java.beans.*;
import java.io.File;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Set;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JProgressBar;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JToolBar;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import explorer.ui.DTMenuBar;
import explorer.ui.EditUI;
import explorer.ui.FileHandler;
import explorer.ui.FileUI;
import explorer.ui.RefreshUI;
import explorer.ui.RunUI;
import explorer.ui.UIDialog;
import fr.esrf.tangoatk.core.AEntityList;
import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.IStatusListener;
import fr.esrf.tangoatk.core.StatusEvent;
import fr.esrf.tangoatk.widget.attribute.Trend;
import fr.esrf.tangoatk.widget.util.ErrorHistory;
import fr.esrf.tangoatk.widget.util.ErrorPopup;
import fr.esrf.tangoatk.widget.util.HelpWindow;
import fr.esrf.tangoatk.widget.util.Splash;
import fr.esrf.tangoatk.widget.util.chart.JLDataView;
import fr.esrf.tangoatk.widget.jdraw.*;

/**
 * Schema for the main class. This class contains what's common for the main
 * "admin mode" and the main "user mode"
 * 
 * @author Erik ASSUM
 */
public abstract class Main implements Status, FileHandler, IStatusListener {

    protected static String done = "done";
    //protected static String VERSION = "Device Tree 1.8";
    protected static String VERSION = "SYNOPTIC Tree 0.4";

    protected AttributePanel attributePanel;
    protected AttributeTable attributeTable;
    protected AttributeTableModel attributeTableModel;
    protected CommandTable commandTable;
    protected CommandTableModel commandTableModel;
    protected DTMenuBar menuBar;
    protected ErrorHistory errorHistory;
    protected ErrorPopup errorPopup;
    protected JFrame mainFrame;
    protected JToolBar refreshBar;
    protected JToolBar fileBar;
    protected File file;
    protected Preferences preferences;
    protected explorer.ui.Dialog trendFrame;
    protected JPopupMenu entityPopup;
    protected JPopupMenu treePopup;
    protected JProgressBar progress;
    protected JLabel status;
    protected JSplitPane tableSplit;
    protected JPanel tablePane;
    protected JSplitPane viewSplit;
    protected FileManager fileManager;
    protected JCheckBoxMenuItem synchroBox;

    protected Trend globalTrend;

    protected boolean isAdmin;
    protected SynopticFileViewer synoptic;
    protected JScrollPane synPanel;
    protected boolean isSynoptic = false;
    
    protected Splash splash;
    protected boolean runningFromShell = true;
    protected int windowX, windowY, windowWidth, windowHeight, tableSplitWidth,
            tableSplitHeight;
    protected int viewSplitDividerLocation, tableSplitDividerLocation,
            mainSplitDividerLocation;
    protected RefreshUI refreshui;
    protected boolean fileRecordable = true;
    protected DeviceList deviceList;
    protected boolean isSynopticTabbed=true;

    /** Application window default X position */
    public static final int DEFAULT_WINDOW_X = 50;
    /** Application window default Y position */
    public static final int DEFAULT_WINDOW_Y = 50;
    /** Application window default width */
    public static final int DEFAULT_WINDOW_WIDTH = 800;
    /** Application window default height */
    public static final int DEFAULT_WINDOW_HEIGHT = 600;
    /** Default location of the split between attributes and commands */
    public static final int DEFAULT_TABLE_SPLIT_DIVIDER_LOCATION = 200;
    /** Default width of the split between attributes and commands */
    public static final int DEFAULT_TABLE_SPLIT_WIDTH = 800;
    /** Default height of the split between attributes and commands */
    public static final int DEFAULT_TABLE_SPLIT_HEIGHT = 400;
    /** Default location of the split between commands and trend */
    public static final int DEFAULT_VIEW_SPLIT_DIVIDER_LOCATION = 400;
    /** Default location of the split between the tree and attributes and commands */
    public static final int DEFAULT_MAIN_SPLIT_DIVIDER_LOCATION = 350;//290;
    /** A String to target main split divider location */
    public static final String MAIN_SPLIT_DIVIDER_LOCATION_KEY = "MAIN_SPLIT_DIVIDER_LOCATION";
    /** A String to target window x position */
    public static final String WINDOW_X_KEY = "MAIN_WINDOW_X";
    /** A String to target window y position */
    public static final String WINDOW_Y_KEY = "MAIN_WINDOW_Y";
    /** A String to target window width */
    public static final String WINDOW_WIDTH_KEY = "MAIN_WINDOW_WIDTH";
    /** A String to target window height */
    public static final String WINDOW_HEIGHT_KEY = "MAIN_WINDOW_HEIGHT";
    /** A String to target table split divider location */
    public static final String TABLE_SPLIT_DIVIDER_LOCATION_KEY = "TABLE_SPLIT_DIVIDER_LOCATION";
    /** A String to target view split divider location */
    public static final String VIEW_SPLIT_DIVIDER_LOCATION_KEY = "VIEW_SPLIT_DIVIDER_LOCATION";
    /** A String to target table split width */
    public static final String TABLE_SPLIT_WIDTH_KEY = "TABLE_SPLIT_WIDTH";
    /** A String to target table split height */
    public static final String TABLE_SPLIT_HEIGHT_KEY = "TABLE_SPLIT_HEIGHT";

    /**
     * Initialization of help page
     */
    protected void initHelp() {
        if (runningFromShell)
            splash.setMessage("Setting up help...");
        HelpWindow.getInstance().setTop("Explorer",
                getClass().getResource("/explorer/html/MainHelp.html"));

        HelpWindow.getInstance().addCategory("Main", "Device tree",
                getClass().getResource("/explorer/html/DeviceTreeHelp.html"));
        HelpWindow.getInstance().addCategory("Main", "Tool bar",
                getClass().getResource("/explorer/html/ToolBarHelp.html"));

        HelpWindow.getInstance().addCategory("Main", "Menu bar",
                getClass().getResource("/explorer/html/MenuBarHelp.html"));
        if (runningFromShell)
            splash.setMessage("Setting up help..." + done);
    }

    /**
     * Initialization of trend panel
     */
    protected void initTrend() {
        if (runningFromShell)
            splash.setMessage("Setting up trend...");

        globalTrend = new Trend();
	//fr.esrf.tangoatk.widget.attribute.Trend class has been modified for making  public theGraph object
	//globalTrend.theGraph.setBackground(java.awt.SystemColor.getColor("activeBackground"));
	
        Font font = new Font("Arial", Font.PLAIN, 10);
        Color color = new Color(0,75,75);
        String title = "Trend Panel";
        TitledBorder tb = BorderFactory.createTitledBorder
                ( BorderFactory.createMatteBorder(1, 1, 1, 1, color) ,
                  title ,
                  TitledBorder.CENTER ,
                  TitledBorder.TOP,
                  font,
                  color
                );
        Border border = ( Border ) ( tb );
        globalTrend.setBorder( border );
        //	globalTrend.setListVisible(false);
        //	globalTrend.setVisible(false);
        //	globalTrend.setLegendVisible(true);
        trendFrame = new explorer.ui.Dialog(globalTrend);

        globalTrend.setButtonBarVisible(false);
        globalTrend.disableButton(Trend.time);
        globalTrend.disableButton(Trend.load);

        attributeTable.setGlobalTrend(globalTrend);
        //globalTrend.repaint();

        if (runningFromShell)
            splash.setMessage("Setting up trend..." + done);
        refreshui.setTrend(globalTrend);
    }

    /**
     * Initialaztion of file manager
     */
    protected void initFileManager() {
        fileManager = FileManager.getInstance();
        fileManager.addErrorListener(errorHistory);
    }

    /**
     * Initialization of tables (attributes, command, etc...)
     */
    protected void initTables() {
        if (runningFromShell)
            splash.setMessage("Initializing components...");

        attributeTableModel.addErrorListener(errorHistory);
        attributeTableModel.addErrorListener(errorPopup);
        commandTableModel.addErrorListener(errorHistory);
        commandTableModel.addErrorListener(errorPopup);

        if (runningFromShell)
            splash.setMessage("Initializing collections..." + done);
    }

    /**
     * Sets preferences default values
     */
    protected void resetPreferences() {
        windowX = preferences.getInt(WINDOW_X_KEY, DEFAULT_WINDOW_X);
        windowY = preferences.getInt(WINDOW_Y_KEY, DEFAULT_WINDOW_Y);
        windowWidth = preferences
                .getInt(WINDOW_WIDTH_KEY, DEFAULT_WINDOW_WIDTH);
        windowHeight = preferences.getInt(WINDOW_HEIGHT_KEY,
                DEFAULT_WINDOW_HEIGHT);
        tableSplitHeight = preferences.getInt(TABLE_SPLIT_HEIGHT_KEY,
                DEFAULT_TABLE_SPLIT_HEIGHT);
        tableSplitWidth = preferences.getInt(TABLE_SPLIT_WIDTH_KEY,
                DEFAULT_TABLE_SPLIT_WIDTH);

        tableSplitDividerLocation = preferences.getInt(
                TABLE_SPLIT_DIVIDER_LOCATION_KEY,
                DEFAULT_TABLE_SPLIT_DIVIDER_LOCATION);
        viewSplitDividerLocation = preferences.getInt(
                VIEW_SPLIT_DIVIDER_LOCATION_KEY,
                DEFAULT_VIEW_SPLIT_DIVIDER_LOCATION);

        mainSplitDividerLocation = preferences.getInt(
                MAIN_SPLIT_DIVIDER_LOCATION_KEY,
                DEFAULT_MAIN_SPLIT_DIVIDER_LOCATION);
    }

    /**
     * Preferences initialization. You have to initialize file manager first
     */
    protected void initPreferences() {
        if (runningFromShell)
            splash.setMessage("Getting preferences...");
        preferences = FileManager.getInstance().getPreferences();
        resetPreferences();
        if (runningFromShell)
            splash.setMessage("Getting preferences..." + done);
    }

    /**
     * Main window initialization.
     * 
     * @param isAdmin
     *            to know if UI is launched in "admin" (<code>true</code>)
     *            or "user" (<code>false</code>) mode
     */
    protected void initUI(boolean isAdmin) {
        if (runningFromShell)
            splash.setMessage("Initializing ui...");
        deviceList = new DeviceList();

        Font font = new Font("Dialog", 0, 12);
        UIManager.put("Label.font", font);
        UIManager.put("MenuBar.font", font);
        UIManager.put("MenuItem.font", font);
        UIManager.put("Menu.font", font);
        UIManager.put("Button.font", font);
        UIManager.put("TabbedPane.font", font);
        UIManager.put("CheckBox.font", font);
        UIManager.put("ProgressBar.font", font);

        errorPopup = ErrorPopup.getInstance();
        menuBar = new DTMenuBar(errorHistory);

        refreshBar = new JToolBar();
        fileBar = new JToolBar();
        mainFrame = new JFrame(VERSION);
        mainFrame.setIconImage(new ImageIcon(getClass().getResource("ui/dtree.gif")).getImage());
        status = new JLabel();
        status.setBorder(BorderFactory.createLoweredBevelBorder());
        status.setText("Ready...");
        progress = new JProgressBar();
        progress.setBorder(BorderFactory.createLoweredBevelBorder());
        mainFrame.setJMenuBar(menuBar);
        mainFrame.setBounds(windowX, windowY, windowWidth, windowHeight);

        attributeTableModel = new AttributeTableModel(this, preferences);
        attributeTableModel.setDeviceList(deviceList);
        attributeTable = new AttributeTable(attributeTableModel, preferences,
                isAdmin);

        commandTableModel = new CommandTableModel(this, preferences);
        commandTableModel.setDeviceList(deviceList);
        commandTable = new CommandTable(commandTableModel, preferences, isAdmin);

        refreshui = new RefreshUI(attributeTableModel, refreshBar, menuBar);
        new FileUI(this, fileBar, menuBar, isAdmin, mainFrame);
        new EditUI(attributeTableModel, commandTableModel, fileBar, menuBar,
                   isAdmin);
        new RunUI(fileBar, menuBar);
        attributeTable.setRefreshUI(refreshui);

        UIDialog.getInstance().addComponent(mainFrame);
        attributePanel = new AttributePanel();

        attributePanel.setTable(attributeTable);
        
        synchroBox = new JCheckBoxMenuItem("synchronized period");
        synchroBox.setToolTipText("Check this box to force the refreshers to resynchronize their period with the refresh interval");
        synchroBox.addActionListener(new ActionListener(){

            public void actionPerformed (ActionEvent arg0)
            {
                attributeTable.setSynchronizedPeriod(synchroBox.isSelected());
                attributeTableModel.setSynchronizedPeriod(synchroBox.isSelected());
                commandTableModel.setSynchronizedPeriod(synchroBox.isSelected());
            }
            
        });
        menuBar.add2RefreshMenu(synchroBox);
        attributeTable.setSynchronizedPeriod(synchroBox.isSelected());
        attributeTableModel.setSynchronizedPeriod(synchroBox.isSelected());
        commandTableModel.setSynchronizedPeriod(synchroBox.isSelected());

        if (runningFromShell)
            splash.setMessage("Initializing ui..." + done);
    }

    /**
     * Initialization of the different components of the application
     */
    protected void initComponents() {
    	Runtime.getRuntime().addShutdownHook(new Thread() {
    		public void run() {
    			exit();
    		}
    	});

    	/*try {
    		UIManager.setLookAndFeel("com.birosoft.liquid.LiquidLookAndFeel");
    		//-Dswing.defaultlaf=com.birosoft.liquid.LiquidLookAndFeel
    		//LiquidLookAndFeel.setLiquidDecorations(true);
    		com.birosoft.liquid.LiquidLookAndFeel.setLiquidDecorations(true, "mac");
    		//} catch (java.lang.ClassNotFoundException e) {
    	} catch (Exception e) {
    	}*/

    	if (runningFromShell) {
    		splash = new Splash();
    		splash.setTitle(VERSION);
    		splash.setMaxProgress(10);
    		splash.progress(1);
    	}

    	DeviceFactory.setAutoStart(false);
    	errorHistory = new ErrorHistory();
    	initFileManager();
    	initPreferences();
    	if (runningFromShell)
    		splash.progress(2);
    	initUI(isAdmin);

    	// allowing printing

    	if (runningFromShell)
    		splash.progress(3);
    	initTables();
    	if (runningFromShell)
    		splash.progress(4);

    	if (runningFromShell)
    		splash.progress(6);
    	initHelp();
    	if (runningFromShell)
    		splash.progress(7);
    	initTrend();
    	if (runningFromShell)
    		splash.progress(8);

    	if (runningFromShell)
    		splash.setMessage("Setting up frame...");

    	// There seems to be a bug in jdk1.4 which makes JSplitPane
    	// angry if you try to specify its size when adding its
    	// subcomponents in the constructor. Therefore I've chosen
    	// to add them after I've specified the size
    	// Erik.

    	viewSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT);

    	viewSplit.setPreferredSize(new Dimension(800, 200));
    	viewSplit.setDividerSize(9);
    	
    	tableSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT); ///Not always used, but initialized to avoid future null assignments

    	if (isSynoptic) {
    		attributePanel.add(commandTable, "Commands");
    		isSynopticTabbed=false;
    		if (isSynopticTabbed) {
    			System.out.println("explorer.Main.initComponents(): adding Synoptic in a new Tab");
    			attributePanel.insertTab( "Synoptic",null,synoptic,"Synoptic",0);
    			attributePanel.setSelectedComponent(synoptic);//Index(0);
    			viewSplit.setTopComponent(attributePanel);
        		//synoptic.setSize(attributePanel.getSize()); 
        		//synoptic.setSize(attributePanel.getSize().getWidth()-30,attributePanel.getSize().getHeight()-30);
        		/*
    		    attributePanel.addPropertyChangeListener(new PropertyChangeListener() {
    			public void propertyChange(PropertyChangeEvent pce) {
    			    //synoptic.setSize(attributePanel.getSize());
    			    synoptic.setSize(
    				    (int)(attributePanel.getSize().getWidth()-30),
    				    (int)(attributePanel.getSize().getHeight()-30)
    				    );
    			}
    		    });*/    
    		} else {
    			System.out.println("explorer.Main.initComponents(): adding Synoptic in a new Split");
    			tableSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT);

    			tableSplit.setPreferredSize(new Dimension(tableSplitWidth,
    					tableSplitHeight));
    			tableSplit.setDividerSize(9);

    			//JPanel synpan = new JPanel();synpan.add(synoptic,BorderLayout.CENTER);
    			//tableSplit.setTopComponent(synpan);
    			tableSplit.setTopComponent(synoptic);
    			tableSplit.setBottomComponent(attributePanel);

    			tableSplit.setOneTouchExpandable(true);

    			tableSplit.setDividerLocation(DEFAULT_TABLE_SPLIT_DIVIDER_LOCATION);
    			tableSplit.setResizeWeight(0.5);

    			viewSplit.setTopComponent(tableSplit);	    		
    		}
    		//tableSplit.setContinuousLayout(true);
		    //tableSplit.setTopComponent(attributePanel);   
    	} else {
    		tableSplit.setPreferredSize(new Dimension(tableSplitWidth,
    				tableSplitHeight));
    		tableSplit.setDividerSize(9);

    		tableSplit.setTopComponent(attributePanel);
    		tableSplit.setBottomComponent(commandTable);

    		tableSplit.setOneTouchExpandable(true);

    		tableSplit.setDividerLocation(DEFAULT_TABLE_SPLIT_DIVIDER_LOCATION);
    		tableSplit.setResizeWeight(0.5);

    		viewSplit.setTopComponent(tableSplit);	    
    	}

    	//viewSplit.setBottomComponent(new JScrollPane(globalTrend));
    	viewSplit.setBottomComponent(globalTrend);

    	viewSplit.setOneTouchExpandable(true);

    	viewSplit.setDividerLocation(DEFAULT_VIEW_SPLIT_DIVIDER_LOCATION);
    	viewSplit.setResizeWeight(4d / 5d);

    	mainFrame.getContentPane().setLayout(new GridBagLayout());

    	GridBagConstraints constraints = new GridBagConstraints();

    	constraints.weightx = 0;
    	constraints.gridy = 0;
    	constraints.gridx = 0;
    	mainFrame.getContentPane().add(refreshBar, constraints);
    	constraints.gridx = 1;
    	mainFrame.getContentPane().add(fileBar, constraints);
    	constraints.fill = GridBagConstraints.BOTH;
    	constraints.gridx = 2;
    	constraints.weightx = 1;
    	mainFrame.getContentPane().add(new JLabel(), constraints);
    	constraints.gridx = 0;
    	constraints.gridy = 1;
    	constraints.weighty = 0.5;
    	constraints.fill = GridBagConstraints.BOTH;
    	constraints.gridwidth = GridBagConstraints.REMAINDER;

    	constraints.gridx = 0;

    	if (runningFromShell)
    		splash.setMessage("Setting up frame..." + done);
    	if (runningFromShell)
    		splash.progress(9);
    	specificSetup(constraints); ///<-- It's Here where the Tree is initialized!!!
    	if (runningFromShell)
    		splash.progress(10);
    	//	constraints.gridy++;
    	//	mainFrame.getContentPane().add(globalTrend, constraints);

    	initStatus(constraints);
    	menuBar.setAboutHandler(new ActionListener() {
    		public void actionPerformed(ActionEvent evt) {
    			new About().show();

    		}
    	});

    	mainFrame.addWindowListener(new WindowAdapter() {
    		public void windowClosing(WindowEvent we) {
    			if (mainFrame.isVisible())
    			{
    				quit();
    			}
    		}
    	});

    	//	commandTableModel.addEntities(fileManager.getCommandList());
    	//	attributeTableModel.addEntities(fileManager.getAttributeList());
    	if (runningFromShell)
    		splash.setVisible(false);
    	if (runningFromShell)
    		splash.dispose();

    	//resetPreferences();attributeTable.setPreferences(preferences);
    }

    /**
     * Initialization of status panel following constraints
     * 
     * @param constraints
     *            the constraints
     */
    protected void initStatus(GridBagConstraints constraints) {
        JPanel p = new JPanel();
        constraints.gridy++;
        constraints.weightx = 0.1;
        constraints.weighty = 0;
        constraints.gridx = 0;
        constraints.fill = GridBagConstraints.BOTH;
        constraints.anchor = GridBagConstraints.WEST;
        constraints.gridwidth = GridBagConstraints.REMAINDER;
        constraints.gridx = 0;
        constraints.weightx = 0.9;
        mainFrame.getContentPane().add(p, constraints);
        p.setLayout(new GridBagLayout());
        constraints.gridx = 0;
        constraints.gridy = 0;
        constraints.gridwidth = 1;
        constraints.weightx = 0;
        p.add(progress, constraints);
        constraints.gridx = 1;
        constraints.weightx = 1;
        p.add(status, constraints);
    }
    
    /**
     * Closes the actual configuration file
     * 
     */
    public void close() {
    	/*
    	 * clear configuration
    	 */
    	mainFrame.setTitle(VERSION);
    	attributePanel.clear();
    	progress.setIndeterminate(true);
    	progress.setStringPainted(true);
  	
    	attributeTableModel.clear();
    	commandTableModel.clear();
    	AttributePolledList attrList = new AttributePolledList();
       	if (globalTrend.getModel()!=null){
    		for (int i=0; i<globalTrend.getModel().getSize();i++){
    			attrList.add((IAttribute)globalTrend.getModel().get(i));
    		}
    		for (int i=0; i<attrList.getSize();i++){
    			globalTrend.removeAttribute((INumberScalar)attrList.get(i));
    		}
    	}    	
    }
    

    /**
     * Opens a file
     * 
     * @param file
     *            the file
     */
    public void open(File file) {
        this.file = file;
      	fileRecordable = open(file.getAbsolutePath());

        attributeTable.setSynchronizedPeriod(synchroBox.isSelected());
        attributeTableModel.setSynchronizedPeriod(synchroBox.isSelected());
        commandTableModel.setSynchronizedPeriod(synchroBox.isSelected());
    }

    /**
     * Opens a file following a path
     * 
     * @param source
     *            the path
     */
    protected boolean open(String source) {
        int refInt = refreshui.getRefreshInterval();
        boolean success = false;
        //final String src = source;

    	String[] attrNames = new String[attributeTableModel.getRowCount()];
    	for (int i=0; i< attrNames.length; i++){
    		attrNames[i] = attributeTableModel.getEntityAt(i).getName();
    	}
    	String[] comNames = new String[commandTableModel.getRowCount()];
    	for (int i=0; i< comNames.length; i++){
    		comNames[i] = commandTableModel.getEntityAt(i).getName();
    	}
    	AttributePolledList attrList = new AttributePolledList();
    	if (globalTrend.getModel()!=null){
    		for (int i=0; i<globalTrend.getModel().getSize();i++){
    			attrList.add((IAttribute)globalTrend.getModel().get(i));
    		}
    	}    	
        close(); //@srubio: it clears all the attributes from tables and trends

        try {
            /*
             * load configuration
             */
            mainFrame.setTitle(VERSION + " - " + source);
            if (source.indexOf("jdw")>=0) {
            		System.out.println("explorer.Main.open("+source+"): opening a Synoptic file!");
            		synoptic = new SynopticFileViewer(source);
            		//synoptic cannot be initialized in Main.main(...) because is not an static variable
            		synoptic.setToolTipMode(TangoSynopticHandler.TOOL_TIP_NAME);
            		synoptic.setAutoZoom(true);		
            		isSynoptic = true;
            		initComponents();
            		success = true;
            } else {
            	success = fileManager.open(source);
            	resetPreferences();

            	tableSplit.setDividerLocation(tableSplitDividerLocation);
            	tableSplit.setPreferredSize(new Dimension(tableSplitWidth,
            			tableSplitHeight));
            	mainFrame.setBounds(windowX, windowY, windowWidth, windowHeight);

            	SwingUtilities.updateComponentTreeUI(mainFrame);
            	viewSplit.setDividerLocation(viewSplitDividerLocation);
            	AEntityList attributes = fileManager.getAttributeList();
            	AEntityList commands = fileManager.getCommandList();
            	commandTable.setPreferences(preferences);
            	attributeTableModel.setPreferences(preferences);
            	commandTableModel.setPreferences(preferences);
            	attributeTable.setPreferences(preferences);// trend is set here

            	Hashtable trendTable = new Hashtable();
            	Hashtable trendDataViewTable = new Hashtable();

            	if (globalTrend.getModel() != null)
            	{
            		for (int i = 0; i < globalTrend.getModel().size(); i++)
            		{
            			IEntity trendAttr = (IEntity)globalTrend.getModel().get(i);
            			Integer axis = new Integer(globalTrend.getAxisForAttribute(trendAttr.getName()));
            			IEntity attr = attributes.get(trendAttr.getName());
            			if (attr != null)
            			{
            				trendTable.put(attr,axis);
            				JLDataView data = globalTrend.getDataViewForAttribute(attr.getName());
            				if (data != null)
            				{
            					JLDataView copy = new JLDataView();
            					copy.setBarWidth(data.getBarWidth());
            					copy.setColor(data.getColor());
            					copy.setFill(data.isFill());
            					copy.setFillColor(data.getFillColor());
            					copy.setFillMethod(data.getFillMethod());
            					copy.setFillStyle(data.getFillStyle());
            					copy.setLabelVisible(data.isLabelVisible());
            					copy.setLineWidth(data.getLineWidth());
            					copy.setMarker(data.getMarker());
            					copy.setMarkerColor(data.getMarkerColor());
            					copy.setMarkerSize(data.getMarkerSize());
            					copy.setName(data.getName());
            					copy.setStyle(data.getStyle());
            					copy.setUnit(data.getUnit());
            					copy.setUserFormat(data.getUserFormat());
            					copy.setViewType(data.getViewType());
            					copy.setClickable(data.isClickable());
            					copy.setA0(data.getA0());
            					copy.setA1(data.getA1());
            					copy.setA2(data.getA0());
            					trendDataViewTable.put(attr.getName(), copy);
            				}
            				data = null;
            			}
            			else trendTable.put(trendAttr,axis);
            		}
            		globalTrend.clearModel();
            		Set attrSet = trendTable.keySet();
            		Iterator attrIterator = attrSet.iterator();
            		while (attrIterator.hasNext())
            		{
            			IEntity attribute = (IEntity)attrIterator.next();
            			Integer axis = (Integer)trendTable.get(attribute);
            			attributeTable.addTrend(attribute, axis.intValue());
            		}
            		trendTable.clear();
            		trendTable = null;
            		Set dataSet = trendDataViewTable.keySet();
            		Iterator dataIterator = dataSet.iterator();
            		while (dataIterator.hasNext())
            		{
            			String attributeName = (String) dataIterator.next();
            			JLDataView refData = (JLDataView) trendDataViewTable.get(attributeName);
            			JLDataView currentData = globalTrend.getDataViewForAttribute(attributeName);
            			if (currentData != null)
            			{
            				currentData.setBarWidth(refData.getBarWidth());
            				currentData.setColor(refData.getColor());
            				currentData.setFill(refData.isFill());
            				currentData.setFillColor(refData.getFillColor());
            				currentData.setFillMethod(refData.getFillMethod());
            				currentData.setFillStyle(refData.getFillStyle());
            				currentData.setLabelVisible(refData.isLabelVisible());
            				currentData.setLineWidth(refData.getLineWidth());
            				currentData.setMarker(refData.getMarker());
            				currentData.setMarkerColor(refData.getMarkerColor());
            				currentData.setMarkerSize(refData.getMarkerSize());
            				currentData.setName(refData.getName());
            				currentData.setStyle(refData.getStyle());
            				currentData.setUnit(refData.getUnit());
            				currentData.setUserFormat(refData.getUserFormat());
            				currentData.setViewType(refData.getViewType());
            				currentData.setClickable(refData.isClickable());
            				currentData.setA0(refData.getA0());
            				currentData.setA1(refData.getA1());
            				currentData.setA2(refData.getA0());
            			}
            			refData = null;
            			currentData = null;
            		}
            		trendDataViewTable.clear();
            		trendDataViewTable = null;
            	}
            	attributeTableModel.addEntities(attributes);
            	commandTableModel.addEntities(commands);

            	// Restore trenp options
            	AttributeTableModel model = (AttributeTableModel) attributeTable.getModel();
            	for (int i = 0; i < model.getRowCount(); i++) {
            		IEntity att = model.getEntityAt(i);
            		if (att instanceof INumberSpectrum) {
            			String keyname = att.getName() + ".GraphSettings";
            			String st = preferences.getString(keyname, "");
            			String err = attributePanel.setSpectrumGraphSettings(att,st);
            			if (err.length() > 0){
            				JOptionPane.showMessageDialog(null,
            						"Failed apply trend configuration: " + err,
            						"Error", JOptionPane.ERROR_MESSAGE);
            				/*
            				 * restore former Trend
            				 */
            				for (int j=0; j<attrList.getSize();j++){
            					globalTrend.getModel().add((IAttribute)attrList.get(j));
            				}
            				break;
            			}
            		}
            	}
            	/*
            	 * ***************************************************
            	 * Re-synchronizing Trend with the rest of application
            	 * ***************************************************
            	 */
            	if (globalTrend.getModel() != null) {
            		for (int i = 0; i < globalTrend.getModel().getSize(); i++) {
            			IAttribute attr = (IAttribute) globalTrend.getModel().get(i);
            			attributeTableModel.removeFromRefresher(attr);
            		}
            		if (!globalTrend.getModel().isEmpty()){
            			refreshui.enableStopBit();
            			refreshui.enableStartAndRefreshBit();
            		}
            	}
            }
            refreshui.setRefreshInterval(preferences.getInt("refreshInterval",refInt));
        }
        catch (Exception e) {
            status("Could not open " + file, e);
            e.printStackTrace();
            /*
             * restore former command configuration
             */
            for (int i=0; i< comNames.length; i++){
                commandTableModel.removeEntityAt(i);
            }
            for (int i = 0; i < comNames.length; i++){
                try {
                    commandTableModel.load(comNames[i]);
                }
                catch (ConnectionException e1) {
                    JOptionPane.showMessageDialog(
                        null,
                        "Error with file.\nTried to restore former command configuration but failed:\nCould not connect to "
                         + comNames[i],
                        "Error",
                        JOptionPane.ERROR_MESSAGE
                    );
                }
            }
            /*
             * restore former attribute configuration
             */
            for (int i=0; i< attrNames.length; i++){
                attributeTableModel.removeEntityAt(i);
            }
            for (int i = 0; i < attrNames.length; i++){
                try {
                    attributeTableModel.load(attrNames[i]);
                }
                catch (ConnectionException e1) {
                    JOptionPane.showMessageDialog(
                        null,
                        "Error with file.\nTried to restore former attribute configuration but failed:\nCould not connect to "
                         + attrNames[i],
                        "Error",
                        JOptionPane.ERROR_MESSAGE
                    );
                }
            }
            /*
             * restore former Trend
             */
            for (int i=0; i<attrList.getSize();i++){
                globalTrend.getModel().add((IAttribute)attrList.get(i));
            }
            /*
             * ***************************************************
             * Re-synchronizing Trend with the rest of application
             * ***************************************************
             */
            if (globalTrend.getModel() != null) {
                for (int i = 0; i < globalTrend.getModel().getSize(); i++) {
                    IAttribute attr = (IAttribute) globalTrend.getModel().get(i);
                    attributeTableModel.removeFromRefresher(attr);
                }
                if (!globalTrend.getModel().isEmpty()){
                    refreshui.enableStopBit();
                    refreshui.enableStartAndRefreshBit();
                }
            }
            refreshui.setRefreshInterval(preferences.getInt("refreshInterval",refInt));
            return false;
        }
        progress.setIndeterminate(false);
        return success;
    }

    /**
     * Displays the status panel
     * @param msg the message to display in status panel
     * @param e exception received to display in status panel
     */
    public void status(String msg, Exception e) {
        status(mainFrame, msg, e);
    }

    /**
     * Displays the status panel
     * @param comp the component in whch the status panel will be displayed
     * @param msg the message to display in status panel
     * @param e exception received to display in status panel
     */
    public static void status(Component comp, String msg, Exception e) {
        JOptionPane.showMessageDialog(comp, msg + " " + e.toString(), "Error",
                JOptionPane.ERROR_MESSAGE);
    }

    /**
     * To display changes in status panel
     * @param evt the event that changed the status
     */
    public void statusChange(StatusEvent evt) {
        status.setText(evt.getStatus());
    }

    /**
     * To quit
     */
    public void quit() {
        mainFrame.hide();
        mainFrame.dispose();
        if (runningFromShell) {
            System.exit(0);
        }
    }

    /**
     * quits if necessary
     */
    public void exit() {
        if (mainFrame.isVisible()) {
            quit();
        }
    }

    /**
     * To run application with specific setup defined by constraints
     * @param constraints the constraints
     */
    protected abstract void specificSetup(GridBagConstraints constraints);
    
    /**
     * Run the Device Tree application.
     * 
     * @param args
     *            leave it empty to start application in admin mode <br>
     *            or put your file path to start in viewer mode as if it just
     *            opened the file
     */
    public static void main(String[] args)
    {
    	if (args.length == 0 || args[0].indexOf("jdw")>=0)
    	{
    		new AdminMain(args);
    	}
    	else
    	{
    		new ViewerMain(args);
    	}
    }
}