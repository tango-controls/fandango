// File:          AdminMain.java
// Created:       2002-12-13 12:55:12, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2003-01-16 15:12:9, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
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
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.widget.device.Tree;
import fr.esrf.tangoatk.widget.device.tree.MemberNode;
import fr.esrf.tangoatk.widget.dnd.AttributeNode;
import fr.esrf.tangoatk.widget.dnd.CommandNode;
import fr.esrf.tangoatk.widget.dnd.EntityNode;

/**
 * Class for the administrator view of the device tree program
 * 
 * @author Erik ASSUM
 */
public class AdminMain extends Main {

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
    
    /**
     * Class constructor, initializer. This method is called when you run device
     * tree from shell
     * 
     * @param args arguments given in shell command
     */
    public AdminMain(String[] args) {
        isAdmin = true; // this is a hack! is only used in super.initUI
        initComponents();

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
    }

    /**
     * Class constructor, initializer. This method is called through other
     * classes, not from shell.
     */
    public AdminMain() {
        runningFromShell = false;

        isAdmin = true; // this is a hack! is only used in super.initUI
        initComponents();

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
        attributeTableModel.clear();
        commandTableModel.clear();
    }

    /**
     * Opens and loads a device tree file
     * 
     * @param file the device tree file to open
     */
    public void open(File file) {
        super.open(file);
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
        mainFrame.setTitle(VERSION + " - " + name);
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

    protected JTree treeInitialization()
    {
        Tree tree = new Tree();
        MouseListener[] liste = tree.getMouseListeners();
        if(liste.length > 0)
        {
            tree.removeMouseListener(liste[liste.length - 1]);
        }
        tree.addErrorListener(errorHistory);
        tree.importFromDb();
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

        /*tree.getSelectionModel().setSelectionMode(
                TreeSelectionModel.SINGLE_TREE_SELECTION);*/

        tree.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent evt) {
                treePressed(evt);
                treeClicked(evt);
            }

            public void mouseReleased(MouseEvent evt) {
                treeClicked(evt);
            }
        });

        tree.setDragEnabled(true);
        return tree;
    }

    protected void runAtk(){
        Object node = deviceTree.getLastSelectedPathComponent();
        if (node == null && !(node instanceof DefaultMutableTreeNode))
            return;

        if (node instanceof MemberNode) {
            try {
                Device d = DeviceFactory.getInstance().getDevice(((MemberNode)node).getName());
                RunUI.runAtkPanel(d);
            }
            catch (ConnectionException e) {
                JOptionPane.showMessageDialog(
                        mainFrame,
                        "Failed to connect to" + ((MemberNode)node).getName(),
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
        return (path != null && path.getPathCount() < 6);
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

        if (selectedRow != -1 && evt.isPopupTrigger()) {

            int[] rows = deviceTree.getSelectionRows();
            if (rows == null)
            {
                rows = new int[0];
            }
            if (evt.isControlDown())
            {
                deviceTree.addSelectionInterval(selectedRow,selectedRow);
                rows = deviceTree.getSelectionRows();
            }
            else if (evt.isShiftDown())
            {
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
                entityPopup.show(evt.getComponent(), evt.getX(), evt.getY());
                return;
            }

            if (n instanceof MemberNode) {
                devicePopup.show(evt.getComponent(), evt.getX(), evt.getY());
                return;
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
        preferences.putInt(TABLE_SPLIT_DIVIDER_LOCATION_KEY, tableSplit
                .getDividerLocation());
        preferences.putInt(MAIN_SPLIT_DIVIDER_LOCATION_KEY, mainSplit
                .getDividerLocation());
        preferences.putDouble(VIEW_SPLIT_DIVIDER_LOCATION_KEY, viewSplit
                .getDividerLocation());
        preferences.putInt(TABLE_SPLIT_WIDTH_KEY, tableSplit.getWidth());
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

}