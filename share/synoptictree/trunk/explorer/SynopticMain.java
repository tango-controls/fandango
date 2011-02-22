// File:          SynopticMain.java
// Created:       2002-12-13 12:55:12, erik
// By:            <Serbi Rubio <srubio@cells.es>><Erik Assum <erik@assum.net>>
// Time-stamp:    <2007-09-01 00:00:00, srubio><2003-01-16 15:12:9, erik>
// 
// 
// Description:       

package explorer;

import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.File;
import java.util.Vector;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JSeparator;
import javax.swing.JSplitPane;
import javax.swing.JTree;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreePath;
import explorer.ui.RunUI;
import explorer.ui.UIBit;
import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.CommandList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.AEntityList;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.widget.device.Tree;
import fr.esrf.tangoatk.widget.device.tree.MemberNode;
import fr.esrf.tangoatk.widget.dnd.AttributeNode;
import fr.esrf.tangoatk.widget.dnd.CommandNode;
import fr.esrf.tangoatk.widget.dnd.EntityNode;
import fr.esrf.tangoatk.widget.device.tree.HierarchyNode;

import fr.esrf.tangoatk.widget.jdraw.*;
import fr.esrf.tangoatk.widget.util.ErrorHistory;
import fr.esrf.tangoatk.widget.util.Splash;
import fr.esrf.tangoatk.widget.util.jdraw.*;

import org.omg.CORBA.FREE_MEM;

/**
 * Class for the administrator view of the device tree program
 * 
 * @author Erik ASSUM
 */
public class SynopticMain extends Main {

    /**
     * The device tree (the one you can see on the left of the screen in admin
     * mode)
     */
    protected JTree deviceTree;

    /**
     * The multi window manager. It is here to split what's common in admin and
     * user mode with what's specific to admin mode
     */
    protected JSplitPane mainSplit;

    protected JPopupMenu devicePopup;
    
    protected JPopupMenu synopticPopup;
    
    /**
     *	The list of StateComposer servers to be configured by the application
     */
    protected Vector composerServers;
    
    /**
     *	The list of DeviceTree Files linked to each Synoptic file 
     */
    protected java.util.Map devtreeFiles;    
       
    
    /**
     * Class constructor, initializer. This method is called when you run device
     * tree from shell
     * 
     * @param args arguments given in shell command
     */
    public SynopticMain(String[] args) {
    //public void init(String[] args) {
    	System.out.println("SynopticMain::SynopticMain(...)");
    	isAdmin = true; // this is a hack! is only used in super.initUI
    	/// srubio: Added Synoptic Handling
    	if (args.length!=0)	
    		isSynoptic = setSynoptic(args[0]);
    	else 
    		isSynoptic = false;	
    	initComponents();	//
    	mainFrame.setTitle(VERSION + " - " + args[0]);

    	//allowing tree refresh from "edit" menu
    	UIBit refreshTreeBit = new UIBit("Refresh Tree...", "Refresh Tree...", new ActionListener() {
    		public void actionPerformed(ActionEvent e) {
    			refreshTree();
    		}
    	}, new ImageIcon(Main.class.getResource("ui/refreshTree.gif")));

    	//allowing tree refresh from "edit" menu
    	JMenuItem refreshTreeItem2 = new JMenuItem("Refresh Tree...");
    	refreshTreeItem2.setIcon(new ImageIcon(Main.class.getResource("ui/refreshTree.gif")));
    	refreshTreeItem2.addActionListener(new ActionListener() {
    		public void actionPerformed(ActionEvent e) {
    			refreshTree();
    		}
    	});
    	menuBar.add2EditMenu(refreshTreeBit.getItem());
    	menuBar.add2RefreshMenu(new JSeparator());
    	menuBar.add2RefreshMenu(refreshTreeItem2);
    	menuBar.repaint();

    	refreshBar.add(refreshTreeBit.getButton());
    	refreshBar.repaint();

    	mainFrame.pack();
    	mainFrame.setVisible(true);

    	String s = globalTrend.getSettings();
    	System.out.println("Updating globalTrend settings, modifying background\n");
    	s=s.replace("graph_background:180,180,180","graph_background:246,245,244");
    	globalTrend.setSetting(s);	
    	//System.out.println("Settings now are:"+globalTrend.getSettings());

	if (deviceTree.getNextMatch(args[0],0,javax.swing.text.Position.Bias.Forward)!=null) {
		if ( ((HierarchyNode)deviceTree.getNextMatch(args[0],0,javax.swing.text.Position.Bias.Forward).getLastPathComponent()).getConfig()!=null
			)
			loadAttribsProfile();
		}
	else System.out.println("The DeviceTree is empty! (or no node matchs!)");
    	System.out.println("-------------end of SynopticMain()----------------------------------");
    }
    
    /**
     * Class constructor, initializer. This method is called through other
     * classes, not from shell.
     */
    /*
    public SynopticMain() {
	System.out.println("SynopticMain::SynopticMain()");
        runningFromShell = false;

        isAdmin = true; // this is a hack! is only used in super.initUI
        initComponents();
        devtreeFiles = new java.util.HashMap();

        UIBit refreshTreeBit = new UIBit("Refresh Tree...", "Refresh Tree...", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                refreshTree();
            }
        }, new ImageIcon(Main.class.getResource("ui/refreshTree.gif")));

        //allowing tree refresh from "edit" menu
        JMenuItem refreshTreeItem2 = new JMenuItem("Refresh Tree...");
        refreshTreeItem2.setIcon(new ImageIcon(Main.class.getResource("ui/refreshTree.gif")));
        refreshTreeItem2.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                refreshTree();
            }
        });
        menuBar.add2EditMenu(refreshTreeBit.getItem());
        menuBar.add2RefreshMenu(new JSeparator());
        menuBar.add2RefreshMenu(refreshTreeItem2);
        menuBar.repaint();

        refreshBar.add(refreshTreeBit.getButton());
        refreshBar.repaint();

        viewSplit.setLastDividerLocation(tableSplitHeight / 3);

        mainFrame.pack();
        viewSplit.setDividerLocation(1.0d);
        mainFrame.setVisible(true);
	
	//JOptionPane.showMessageDialog(null,"Vamo payá");	
	String s = globalTrend.getSettings();
	s.replace("graph_background:180,180,180","graph_background:246,245,244");
	globalTrend.setSetting(s);		
    }*/

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

    	attributePanel.add("Commands",commandTable);
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
    		//tableSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT); //Do it before!?

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
     * Sets up the device tree window with specific constraints
     * 
     * @param constraints the specific constraints
     */
    protected void specificSetup(GridBagConstraints constraints) {
        deviceTree = initTree();
        if (splash.isVisible()) splash.setMessage("Adding tree...");
        JScrollPane treePane = new JScrollPane(deviceTree);
        Font font = new Font("Arial", Font.PLAIN, 10);
        Color color = Color.BLACK;
        String title = "Device Browsing Panel";
        TitledBorder tb = BorderFactory.createTitledBorder
                ( BorderFactory.createMatteBorder(1, 1, 1, 1, color) ,
                  title ,
                  TitledBorder.CENTER ,
                  TitledBorder.TOP,
                  font,
                  color
                );
        Border border = ( Border ) ( tb );
        treePane.setBorder( border );
        treePane.setBackground(Color.WHITE);

        treePane.setPreferredSize(new Dimension(300, 600));
        mainSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, treePane,
                viewSplit);
        mainSplit.setDividerSize(9);
        mainSplit.setOneTouchExpandable(true);
        mainSplit.setDividerLocation(mainSplitDividerLocation);
        mainFrame.getContentPane().add(mainSplit, constraints);
        if (splash.isVisible()) splash.setMessage("Adding tree..." + done);
    }

    /**
     * Prepares a new device tree file creation
     */
    public void newFile() {
        //attributeTableModel.clear();
        //commandTableModel.clear();
    	close();
    }

    /**
     * Opens and loads a device tree file
     * 
     * @param file the device tree file to open
     */
    public void open(File file) {
        java.lang.String filename = file.getAbsolutePath();
        if (filename.endsWith("jdw")) {
        	isSynoptic = setSynoptic(filename);
        	if (isSynoptic) initComponents();
        } else {
            super.open(file);
        }    	
        mainSplit.setDividerLocation(mainSplitDividerLocation);
    }

    /**
     * Saves a device tree file
     * 
     * @param file
     *            the device tree file to save
     */
    public void save(File file) {
        String name = file.getAbsolutePath();
        //mainFrame.setTitle(VERSION);// + " - " + name);
        progress.setIndeterminate(true);
        status.setText("Saving to " + file.getAbsolutePath());

        try {
            storePreferences();
            fileManager.setAttributes((AttributePolledList) attributeTableModel.getList());
            fileManager.setCommands((CommandList) commandTableModel.getList());

            fileManager.save(file);
            status.setText("Saving ok");
        }
        catch (Exception e) {
            status(mainFrame, "Could not save " + file, e);
        }
        progress.setValue(progress.getMinimum());
        progress.setIndeterminate(false);
    }

    /**
     * Initialization of the device tree (the tree on the left of the screen in
     * admin mode)
     */
    protected JTree initTree() {
        String message = "Initializing device tree...";
        if (splash.isVisible()) splash.setMessage(message);
        Tree tree = (Tree) treeInitialization();
        message += "done";
        if (splash.isVisible()) splash.setMessage(message);
        return tree;
    }

    /**
     * This method doesn't perform the full Synoptic loading.
     * It requires initComponents() to be executed after.
     * Then it will launch: ->specificSetup()->treeInitialization()->loadJDObjects()
     * 
     * @param filename
     */
    public boolean setSynoptic(String filename) {
    	try {
			synoptic = new SynopticFileViewer(filename);
			//synoptic cannot be initialized in Main.main(...) because is not an static variable
			synoptic.setToolTipMode(TangoSynopticHandler.TOOL_TIP_NAME);
			synoptic.setAutoZoom(true);
			return true;
    	} catch (Exception e) {
			return false;
		} 
    }
    
    /**
     * It will load the information of all the objects in a set of jdraw files and configure
     * a Tree to navigate to its internal hierarchy.
     * 
     * @param tree
     * @param filename
     * @return
     */
    protected Vector<String> loadJDObjects(Tree tree, String filename) {
    	System.out.println("explorer.SynopticMain.loadJDObjects("+filename+"): entering ...");
    	JDrawEditor jde = new JDrawEditor(JDrawEditor.MODE_PLAY);
    	try {	 
    		jde.loadFile(filename);
    	} catch (Exception e) {
    		System.out.println("explorer.SynopticMain.loadJDObjects("+filename+"): file was not loadable!!!!");
    		return new Vector<String>();
    	}
    	fr.esrf.tangoatk.widget.device.tree.HierarchyNode node=tree.addNewNode(tree.getRootName(),filename);
    	Vector jobjs = jde.getObjects();
    	Vector devsList = new Vector();
    	fr.esrf.TangoApi.Database db = null;
    	fr.esrf.tangoatk.core.DeviceFactory factory = null;	
    	try {
    		db = new fr.esrf.TangoApi.Database();
    		factory = fr.esrf.tangoatk.core.DeviceFactory.getInstance();
    		for (int i=0; i<jobjs.size(); i++) {
    			String oname=((JDObject)jobjs.get(i)).getName(); 
    			//if (oname.length()>0) System.out.println( "JDObject["+i+"]=\""+oname+"\"");
    			JDObject jdobj=((JDObject)jobjs.get(i));
    			if (jdobj.hasExtendedParam("isSynoptic")) {
    				String filename2 = ((JDObject)jobjs.get(i)).getExtendedParam("isSynoptic");
    				System.out.println( "SynopticMain.loadJDObjects: "+filename+"["+i+"]=\""+oname+"\" is a Synoptic Object, loading "+filename2);
    				tree.addNewNode(filename,filename2);
    				Vector<String> devsvect = loadJDObjects(tree,filename2);
    				
    				if (jdobj.hasExtendedParam("isStateComposer")) {
    					/** The value of this extension gives to the GUI the information about the instance
    					 *	of the StateComposer used to compose its state.
    					 *	The GUI will register the internal objects if it has not been done before.
    					 */
    					/* srubio: I will finish this later ...
    					 * --------------------------------------------------
    					String instance = jdobj.getExtendedParam("isSynoptic");
    					System.out.println( "JDObject is a StateComposer! Using instance "+instance);

    					/// Create the composer device if it does not exists!
    					//Device dev = null;
    					try {
    						System.out.println("\tSynopticMain.loadJDObjects: verifying that StateComposer "+oname+" exists");
    						//dev = factory.getDevice(oname);
    						String[] devsarr = db.get_device_property(oname,"DevicesList").extractStringArray();
    						for (int j=0;j<devsarr.length; j++) {
    							if (!devsvect.contains(devsarr[j]))
    								devsvect.add(devsarr[j]);
    						}
    					} catch (fr.esrf.Tango.DevFailed e) { /// The Device does not exists
    						System.out.println("\tSynopticMain.loadJDObjects: StateComposer "+oname+" doesn't exist, creating ...");
    						db.add_device(oname,"PyStateComposer",instance);
    						/// Add the composer to the list of servers to restart
    						if (!composerServers.contains(instance))
    							composerServers.add(instance);
    					}

    					/// ADD each of the devices (including the actual values readed from DevicesList attribute) 
    					/// to its DevicesList property		    
    					fr.esrf.TangoApi.DbDatum[] dbd = new fr.esrf.TangoApi.DbDatum[1];
    					dbd[0] = new fr.esrf.TangoApi.DbDatum("DevicesList",(String[])devsvect.toArray());
    					db.put_device_property(oname,dbd);
    					*/
    				}	    		    		
    			}
    			else if (oname.split("/").length>2) {
    				System.out.println( "JDObject["+i+"]=\""+oname+"\" is a TANGO Object");
    				if (oname.split("/").length>3) oname=oname.substring(0,oname.lastIndexOf("/"));
    				try {
    					//Device dev=DeviceFactory.getInstance().getDevice(oname);
    					String dev = oname;
    					if (!devsList.contains(dev)) {
    						devsList.add(dev);
    						//System.out.println("SynopticMain.loadJDObjects: Device "+oname+" added to "+filename+" node");
    					}
    				} catch (Exception e) {
    					System.out.println( "SynopticMain.loadJDObjects: Exception in DeviceFactory.getDevice() method: "+e.toString());
    				}
    			}    			
    			if (jdobj.hasExtendedParam("xmlFile")) {
    				String filename2 = ((JDObject)jobjs.get(i)).getExtendedParam("xmlFile");
    				System.out.println( "SynopticMain.loadJDObjects: "+filename+"["+i+"]=\""+oname+"\" is linked to an xml file, "+filename2);
    				node.setConfig(filename2);
    				
    			}    			
    		}
    	} catch (Exception e) {
    		System.out.println("loadJDObjects: Exception trying to connect to database!!");
    		return null;
    	}	
    	tree.importDeviceList(filename,devsList);
    	return (Vector)devsList;
    }
    
    protected JTree treeInitialization()
    {
        Tree tree = new fr.esrf.tangoatk.widget.device.Tree();
        MouseListener[] liste = tree.getMouseListeners();
        if(liste.length > 0)
        {
            tree.removeMouseListener(liste[liste.length - 1]);
        }
        tree.addErrorListener(errorHistory);
        if (!isSynoptic) {
        	tree.importFromDb();
        } else {
        	String parent = "Synoptics";
        	String filename = synoptic.getFileName();
        	tree.setRootName(parent);
        	//tree.addNewNode(parent,filename); //It is done inside loadJDObjects
        	composerServers=new Vector(); //This vector will be used to manage the state composers for all the tree 
        	loadJDObjects(tree, filename);
        	/* srubio: Feature temporary disabled ...
        	try {
        		for (int i=0;i<composerServers.size();i++) {
        			Device dev=DeviceFactory.getInstance().getDevice("dserver/"+composerServers.get(i));
        			dev.command_inout("RestartServer");
        		}
        	} catch (Exception e) {
        		System.out.println( "SynopticMain.treeInitialization: Exception while configuring StateComposer instances method: "+e.toString());

        	}*/
        }
	
        treePopup = new JPopupMenu();
        devicePopup = new JPopupMenu();

        //tree.addStatusListener(this);
        tree.setShowEntities(true);

        entityPopup = new JPopupMenu();
        JMenuItem atkPanelItem = new JMenuItem("Run atkpanel");
        JMenuItem refreshItem = new JMenuItem("Refresh Tree...");
        JMenuItem addItem = new JMenuItem("Add to table");
        
        atkPanelItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                runAtk();
            }
        });

        addItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                add2Table();
            }
        });

        refreshItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                refreshTree();
            }
        });

        treePopup.add(refreshItem);
        entityPopup.add(addItem);
        devicePopup.add(atkPanelItem);
        
        JMenuItem xmlFileItem = new JMenuItem("Load Attribs/Trends profile");
        synopticPopup = new JPopupMenu();
        xmlFileItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                loadAttribsProfile();
            }
        });
        synopticPopup.add(xmlFileItem);        

        /*tree.getSelectionModel().setSelectionMode(
                TreeSelectionModel.SINGLE_TREE_SELECTION);*/

        tree.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent evt) {
                treePressed(evt);
                treeClicked(evt);
            }

            public void mouseReleased(MouseEvent evt) {
                //treeClicked(evt);
            }
        });

        tree.setDragEnabled(true);
        return tree;
    }
    
    protected void loadAttribsProfile() { //throws Exception {
    	if (synoptic==null) {
    		//javax.swing.JOptionPane.showMessageDialog(null,"There's no synoptic!");
    		return;// throw new Exception("Synoptic object not initialized!");
    	}
    	Vector jobjs = synoptic.getObjects();
    	Vector devsList = new Vector();
    	fr.esrf.TangoApi.Database db = null;
    	fr.esrf.tangoatk.core.DeviceFactory factory = null;	
    	try {
    		boolean somethingToLoad=false;
    		db = new fr.esrf.TangoApi.Database();
    		factory = fr.esrf.tangoatk.core.DeviceFactory.getInstance();
    		for (int i=0; i<jobjs.size(); i++) {
    			JDObject jdobj=((JDObject)jobjs.get(i));
    			if (jdobj.hasExtendedParam("xmlFile")) {
    				String filename2 = ((JDObject)jobjs.get(i)).getExtendedParam("xmlFile");
    				open(filename2);
    				somethingToLoad=true;
    				break;
    			}
    		}
    		for (int i=0; i<jobjs.size(); i++) {
    			JDObject jdobj=((JDObject)jobjs.get(i));
    			//if (oname.length()>0) System.out.println( "JDObject["+i+"]=\""+oname+"\"");
    			if (jdobj.hasExtendedParam("addToTable")) {
                    try
                    {
            			String oname=jdobj.getName(); 
                        attributeTableModel.load( oname );
                        attributePanel.setSelectedComponent(attributeTable);
                        /*
                         * ************************** * 
                         * Synchronization with Trend *
                         * ************************** *
                         */
                        AttributePolledList attrList = new AttributePolledList();
                        IAttribute attr = (IAttribute) attrList
                                .add( oname );
                        if ( globalTrend.getModel() != null
                                && globalTrend.getModel().contains( attr ) )
                        {
                            attributeTableModel.removeFromRefresher( attr );
                        }
                        attrList.removeAllElements();
                        attrList = null;
                        /*
                         * ********************************* * 
                         * End of synchronization with Trend *
                         * ********************************* *
                         */
                        somethingToLoad=true;
                    }
                    catch (ConnectionException e)
                    {
                        Main.status( mainFrame, "Error loading attribute ", e );
                    }    				
        			if (jdobj.hasExtendedParam("addToTrend")) {
        				
        			}
    			}
    		}    
    		if (!somethingToLoad) javax.swing.JOptionPane.showMessageDialog(null,"There's no attribute profile for this Synoptic");
    	} catch (Exception e){}
    }

    protected void runAtk(){
        Object node = deviceTree.getLastSelectedPathComponent();
        if (node == null && !(node instanceof DefaultMutableTreeNode))
            return;

        if (node instanceof MemberNode) {
            try {
                Device d = DeviceFactory.getInstance().getDevice(((MemberNode)node).getShortName());
                RunUI.runAtkPanel(d);
            }
            catch (ConnectionException e) {
                JOptionPane.showMessageDialog(
                        mainFrame,
                        "Failed to connect to " + ((MemberNode)node).getShortName(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
            return;
        }
    }
    
    /**
     * Refreshes the device tree (the tree on the left of the screen in admin
     * mode)
     */
    public void refreshTree() {
        status.setText("Refreshing Tree...");
        Container c = deviceTree.getParent();
        c.remove(deviceTree);
        ((Tree) deviceTree).removeListeners();
        deviceTree = null;
        deviceTree = treeInitialization();
        c.add(deviceTree);
        status.setText("Tree Refreshed");
    }

    /**
     * Manages a mouse press on the device tree (the tree on the left of the
     * screen in admin mode). This method is used to clear former selections
     * when the path does not correspond to an attribute or a command.
     * 
     * @param evt the mouse event for the "click"
     */
    protected void treePressed(MouseEvent evt) {
        TreePath path = deviceTree.getPathForLocation(evt.getX(),evt.getY());
        if (isNotEntityPath(path))
        {
            deviceTree.clearSelection();
            deviceTree.setSelectionPath( deviceTree.getPathForLocation(evt.getX(),evt.getY()) );
        }
    }

    protected boolean isNotEntityPath(TreePath path)
    {
        //return (path != null && path.getPathCount() < 6);
	Object n = deviceTree.getLastSelectedPathComponent();
        if (n == null || !(n instanceof DefaultMutableTreeNode))
            return false;
        Object node = ((DefaultMutableTreeNode) n).getUserObject();
        if (node instanceof EntityNode) {
            return true;
        }	
	else return false;
    }

    /**
     * Manages a mouse click on the device tree (the tree on the left of the
     * screen in admin mode). This method is used to show the correct Popup Menu
     * corresponding to the selected node.
     * 
     * @param evt
     *            the mouse event for the "click"
     */
    public void treeClicked(MouseEvent evt) {
    	int selectedRow = deviceTree.getRowForLocation(evt.getX(), evt.getY());
    	//System.out.println("treeClicked");
    	if (selectedRow != -1) {
    		//System.out.println("treeClicked isPopupTrigger");
    		int[] rows = deviceTree.getSelectionRows();
    		if (rows == null)
    		{
    			rows = new int[0];
    		}
    		if (evt.isControlDown())
    		{
    			System.out.println("evt.isControlDown()");
    			deviceTree.addSelectionInterval(selectedRow,selectedRow);
    			rows = deviceTree.getSelectionRows();
    		}
    		else if (evt.isShiftDown())
    		{
    			System.out.println("evt.isShiftDown()");
    			int min = rows[0];
    			for (int i = 0; i < rows.length; i++)
    			{
    				if (rows[i] < min) min = rows[i];
    			}
    			deviceTree.addSelectionInterval(min, selectedRow);
    			rows = deviceTree.getSelectionRows();
    		}
    		else
    		{
    			boolean isInSelection = false;
    			for (int i = 0; i < rows.length; i++)
    			{
    				if (rows[i] == selectedRow)
    				{
    					isInSelection = true;
    					break;
    				}
    			}
    			if (!isInSelection)
    			{
    				deviceTree.setSelectionInterval(selectedRow,selectedRow);
    			}
    		}

    		Object n = deviceTree.getLastSelectedPathComponent();

    		if (n == null && !(n instanceof DefaultMutableTreeNode))
    			return;

    		Object node = ((DefaultMutableTreeNode) n).getUserObject();

    		if (node instanceof EntityNode) {
    			System.out.println("Node object '"+node.toString()+"' is an EntityNode instance");
    			if  (evt.isPopupTrigger()) entityPopup.show(evt.getComponent(), evt.getX(), evt.getY());
    			return;
    		}

    		if (n instanceof MemberNode) {
    			System.out.println("Node '"+n.toString()+"' is a MemberNode instance");
    			if  (evt.isPopupTrigger()) devicePopup.show(evt.getComponent(), evt.getX(), evt.getY());
    			return;
    		} else if (n instanceof HierarchyNode) {
    			System.out.println("Node '"+n.toString()+"' is a HierarchyNode instance");
    			if (evt.isPopupTrigger() && ((HierarchyNode)n).getConfig()!=null) 
    				synopticPopup.show(evt.getComponent(), evt.getX(), evt.getY());
    			else {
    				fr.esrf.tangoatk.widget.device.tree.HierarchyNode nh = (fr.esrf.tangoatk.widget.device.tree.HierarchyNode)n;
    				if (nh.getFileName()!=null && nh.getFileName()!=synoptic.getFileName()) {
    					System.out.println("Loading new synoptic file: "+nh.getFileName());
    					try {
    						Dimension d = new Dimension();//=synoptic.getSize();
    						Dimension d2=synoptic.getSize();
    						Dimension d3 = new Dimension();

    						//synoptic.
    						d.width=tableSplit.getWidth();
    						d.height=tableSplit.getDividerLocation();
    						
    						synoptic.clearObjects();
    						synoptic.setSize(0,0);
    						synoptic.setJdrawFileName(nh.getFileName());
    						synoptic.setSize(d2);
    						/*
    						//d2 = synoptic.getPreferredSize();
    						System.out.println("DEBUG: Synoptic dimension(w,h) = ("+d2.width+","+d2.height+")");
    						d3.height=d2.height; d3.width=d2.width;
    						if (d2.height>d.height) {
    							//d3.width=(d2.width*(d.height/d2.height));
    							System.out.println("DEBUG: d3.w="+d2.width+"*"+d.height+"/"+d2.height);
    							d3.width=(int)(d2.width*((float)d.height/(float)d2.height));
    							d3.height=d.height;
    						} 
    						System.out.println("DEBUG: Arranged dimension(w,h) = ("+d3.width+","+d3.height+")");
    						if (d3.width>d.width) {
    							//d3.height=(int)(d3.height*((float)d.width/d3.width));
    							System.out.println("DEBUG: d3.w="+d3.height+"*"+d.height+"/"+d3.height);
    							d3.height=(int)(d3.height*((float)d.width/(float)d3.width));
    							d3.width=d.width;
    						}
    						System.out.println("DEBUG: Arranged dimension(w,h) = ("+d3.width+","+d3.height+")");
    						//JOptionPane.showMessageDialog(null,"setSize d3");
    						JOptionPane.showMessageDialog(null,"setSize arranged");
    						synoptic.setSize(d3.width,d3.height);
							*/
    						if (isSynopticTabbed)
    							attributePanel.setSelectedComponent(synoptic);
    						else {
    							//tableSplit.setTopComponent(synoptic);
    							//System.out.println("DEBUG: tablesSplit.setTopComponent(synoptic)");
    						}
    						/*
    						if (((HierarchyNode)n).getConfig()!=null) {
    							System.out.println("Opening Hierarchy Node config file!");
    							open(((HierarchyNode)n).getConfig());
    						}*/
    						//JOptionPane.showMessageDialog(null,"Done");
    					} catch (Exception e) {
    						System.out.println("Exception loading "+nh.getFileName()+": "+e.toString());
    					}
    				}	
    			}
    		} else if (n instanceof fr.esrf.tangoatk.widget.device.tree.FamilyNode) {
    			System.out.println("Node '"+n.toString()+"' is a FamilyNode instance");
    		} else if (n instanceof fr.esrf.tangoatk.widget.device.tree.DomainNode) {
    			System.out.println("Node '"+n.toString()+"' is a DomainNode instance");
    		}

    		if (selectedRow == 0) {
    			treePopup.show(evt.getComponent(), evt.getX(), evt.getY());
    		}
    	}
    }

    /**
     * Method used to add an attribute/a command, from the tree, in the list of
     * attributes/commands to check/manage in table
     */
    public void add2Table ()
    {
        TreePath[] paths = deviceTree.getSelectionPaths();
        for (int i = 0; i < paths.length; i++)
        {
            Object n = paths[i].getLastPathComponent();
            if ( n == null && !( n instanceof DefaultMutableTreeNode ) ) continue;
            Object node = ( (DefaultMutableTreeNode) n ).getUserObject();
            if ( node instanceof AttributeNode )
            {
                try
                {
                    attributeTableModel.load( ( (AttributeNode) node )
                            .getFQName() );
                    attributePanel.setSelectedComponent(attributeTable);
                    /*
                     * ************************** * 
                     * Synchronization with Trend *
                     * ************************** *
                     */
                    AttributePolledList attrList = new AttributePolledList();
                    IAttribute attr = (IAttribute) attrList
                            .add( ( (AttributeNode) node ).getFQName() );
                    if ( globalTrend.getModel() != null
                            && globalTrend.getModel().contains( attr ) )
                    {
                        attributeTableModel.removeFromRefresher( attr );
                    }
                    attrList.removeAllElements();
                    attrList = null;
                    /*
                     * ********************************* * 
                     * End of synchronization with Trend *
                     * ********************************* *
                     */
                }
                catch (ConnectionException e)
                {
                    Main.status( mainFrame, "Error loading attribute ", e );
                }
                continue;
            }
            if ( node instanceof CommandNode )
            {
                try
                {
                    commandTableModel.load( ( (CommandNode) node ).getFQName() );
                    attributePanel.setSelectedComponent(commandTable);
                }
                catch (ConnectionException e)
                {
                    Main.status( mainFrame, "Error loading command ", e );
                }
                continue;
            }
        }
    }

    /**
     * Stores the device tree window appearence preferences
     */
    public void storePreferences() {
        attributeTable.storePreferences();
        commandTable.storePreferences();
        preferences.putInt(WINDOW_WIDTH_KEY, mainFrame.getWidth());
        preferences.putInt(WINDOW_HEIGHT_KEY, mainFrame.getHeight());
        preferences.putInt(WINDOW_X_KEY, mainFrame.getX());
        preferences.putInt(WINDOW_Y_KEY, mainFrame.getY());
        if (tableSplit!=null) 
	    preferences.putInt(TABLE_SPLIT_DIVIDER_LOCATION_KEY, tableSplit
                .getDividerLocation());
        preferences.putInt(MAIN_SPLIT_DIVIDER_LOCATION_KEY, mainSplit
                .getDividerLocation());
        preferences.putDouble(VIEW_SPLIT_DIVIDER_LOCATION_KEY, viewSplit
                .getDividerLocation());
        if (tableSplit!=null) 
	    preferences.putInt(TABLE_SPLIT_WIDTH_KEY, tableSplit.getWidth());
        if (tableSplit!=null) 
	    preferences.putInt(TABLE_SPLIT_HEIGHT_KEY, tableSplit.getHeight());

        fileManager.setPreferences(preferences);

        // Save trend settings for all specturm attribute
        EntityTableModel model = (EntityTableModel) attributeTable.getModel();
        for (int i = 0; i < model.getRowCount(); i++) {
            IEntity att = model.getEntityAt(i);
            if (att instanceof INumberSpectrum) {
                String keyname = att.getName() + ".GraphSettings";
                preferences.putString(keyname, attributePanel
                        .getSpectrumGraphSettings(att));
            }
        }
    }

    /**
     * Exits program, stores preferences, saves the current device tree file and terminates 
     * the currently running Java Virtual Machine.
     */
    public void quit() {
        storePreferences();
        if ((file != null) && (fileRecordable)) {
            if ( JOptionPane.showConfirmDialog(
                    mainFrame,
                    "Save before exit ?",
				    "Alert",
				    JOptionPane.YES_NO_OPTION
				 ) == JOptionPane.YES_OPTION 
				){
                save(file);
            }
        }
        super.quit();
    }

    /**
     * quits if necessary
     */
    public void exit() {
        if (mainFrame.isVisible()) {
            quit();
        }
    }
    
    public static void main(String[] args)
    {
    	if (args.length > 0 && args[0].indexOf("jdw")>=0)
    	{
    		new SynopticMain(args);
    	}
    	else
    	{
    		System.out.println("A JDraw file is required as argument");
    		JOptionPane.showMessageDialog(null,"A JDraw file is required as argument");
    	}
    }
}