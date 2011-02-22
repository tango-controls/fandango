// File:          EntityTable.java
// Created:       2002-09-13 12:48:25, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-17 11:47:24, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Point;
import java.awt.datatransfer.DataFlavor;
import java.awt.dnd.DnDConstants;
import java.awt.dnd.DropTarget;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Enumeration;

import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JSeparator;
import javax.swing.JTable;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.table.TableModel;

import explorer.ui.RunUI;
import explorer.ui.UIDialog;
import fr.esrf.tangoatk.core.IDevice;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.widget.device.SingletonStatusViewer;
import fr.esrf.tangoatk.widget.dnd.DropTargetListener;
import fr.esrf.tangoatk.widget.dnd.IDropHandler;
import fr.esrf.tangoatk.widget.dnd.NodeFactory;
import fr.esrf.tangoatk.widget.properties.PropertyListViewer2;
import fr.esrf.tangoatk.widget.util.HelpWindow;
import fr.esrf.tangoatk.widget.util.IApplicable;

/**
 * <code>EntityTable</code> represents all things common to the attribute and
 * command table. It takes care of setting up menus, drag listeners and such.
 * This class subclasses JPanel and not JTable, since it was much harder to make
 * dnd work when it subclassed JTable.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version 1.0
 */
public abstract class EntityTable extends JPanel {

    /**
     * variable <code>table</code> which is used to render the table
     *  
     */
    protected JTable table;

    protected boolean admin = true;
    /**
     * variable <code>entityRenderer</code>,<code>deviceRenderer</code>
     * used to contain the renderers for entities and devices
     */
    protected MyCellRenderer entityRenderer, deviceRenderer;

    /**
     * variable <code>flavor</code> tells the dnd which types to accept
     *  
     */
    protected String flavor = NodeFactory.MIME_ENTITY;

    /**
     * The attribute/command property dialog
     */
    protected explorer.ui.Dialog propertyDialog;

    /**
     * The panel of the attribute/command property dialog
     */
    protected PropertyDialog propertyPanel;

    /**
     * The menu that appears by right clicking
     */
    protected JPopupMenu popup;

    /**
     * The preferences associated with the table
     */
    protected Preferences preferences;

    /**
     * variable <code>model</code> holds the model of the table.
     *  
     */
    protected EntityTableModel model;

    protected explorer.ui.Dialog viewDialog;

    /**
     * A widget to see the device status
     */
    protected SingletonStatusViewer statusViewer;

    /** URL of help page */
    protected String helpUrl;

    protected EntityTable() {

    }

    /**
     * <code>setPreferences</code>
     * 
     * @param preferences
     *            a <code>Preferences</code> value
     */
    public void setPreferences(Preferences preferences) {
        this.preferences = preferences;
    }

    /**
     * <code>initComponents</code> sets up the user interface. It is the first
     * method to be called and it does the following.
     * <ol>
     * <li>Initialises the table with the model.
     * <li>Initialises drag'n'drop throuhg initDnd
     * <li>Initialises help through initHelp
     * <li>Initalises the menus with the help of initMenus in subclasses, which
     * is called before the common menus are added to the popupmenu.
     * </ol>
     * 
     * @param model
     *            a <code>EntityTableModel</code>, the model of the table
     * @param isAdmin
     *            a <code>boolean</code> value which decides which menu items
     *            should be enabled. Remove and Remove All are only enabled if
     *            <code>isAdmin</code> is <code>true</code>
     */
    protected void initComponents(EntityTableModel model, boolean isAdmin) {
        entityRenderer = new MyCellRenderer();
        deviceRenderer = new MyCellRenderer();

        table = new JTable(model) {

            public void createDefaultColumnsFromModel() {
                TableColumn[] l;
                EntityTableModel m;
                try {
                    m = (EntityTableModel) this.getModel();
                    if (m == null)
                        return;
                    // we don't want to create stuff
                    // before we've set our own model.

                } catch (ClassCastException e) {
                    return;
                }

                // Remove any current columns
                TableColumnModel cm = getColumnModel();

                while (cm.getColumnCount() > 0) {
                    cm.removeColumn(cm.getColumn(0));
                }

                l = new TableColumn[m.getColumnCount()];

                for (int i = 0; i < m.getColumnCount(); i++) {
                    TableColumn newColumn;
                    String name = m.getColumnName(i);
                    int index = m.getIndex(name, i);

                    // hack for the last column which is none
                    // removable
                    if (i == 0 && l.length == 1) {
                        index = i;
                        m.putIndex(name, i);
                    }

                    if (index == -1 || index >= l.length)
                        continue;

                    newColumn = createTableColumn(name, i);
                    newColumn.setPreferredWidth(getPrefWidth(name, 87));

                    l[index] = newColumn;
                }

                // add all columns in the correctly indexed order.
                for (int i = 0; i < l.length; i++) {
                    if (l[i] == null)
                        continue;
                    addColumn(l[i]);
                }
            }
        };

        table.setRowHeight(18);
        table.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent evt) {
                showPopup(evt);
            }

            public void mouseReleased(MouseEvent evt) {
                showPopup(evt);
                //entityTableMouseClicked(evt);
            }

            public void mouseClicked(MouseEvent evt) {
                showPopup(evt);
                entityTableMouseClicked(evt);
                
            }
        });

        table.addKeyListener(new KeyAdapter() {
            public void keyPressed(KeyEvent e)
            {
                manageKey(e);
            }
            public void keyReleased(KeyEvent e)
            {
                manageKey(e);
            }
            public void keyTyped(KeyEvent e)
            {
                manageKey(e);
            }
            private void manageKey(KeyEvent e)
            {
                if (e.getKeyCode() == KeyEvent.VK_DELETE || e.getKeyCode() == KeyEvent.VK_BACK_SPACE)
                {
                    if (isAdmin()) removeEntity(true);
                }
            }
        });
        initDnd();
        initHelp();

        popup = new JPopupMenu();
        UIDialog.getInstance().addComponent(popup);
        initMenus();

        //JMenuItem entityAlias = new JMenuItem("Set alias...");
        //JMenuItem deviceAlias = new JMenuItem("Set device alias...");
        JMenuItem view = new JMenuItem("View...");
        JMenuItem remove = new JMenuItem("Remove");
        JMenuItem runJive = new JMenuItem("Run jive");
        JMenuItem runAtk = new JMenuItem("Run atkpanel");
        JMenuItem status = new JMenuItem("Status...");
        JMenuItem properties = new JMenuItem("Properties...");
        JMenuItem helpItem = new JMenuItem("Help...");

        remove.setEnabled(isAdmin);
        //entityAlias.setEnabled(isAdmin);
        //deviceAlias.setEnabled(isAdmin);
        runJive.setEnabled(RunUI.isJiveAvailable());
        runAtk.setEnabled(RunUI.isATKPanelAvailable());

        //popup.add(new JSeparator());
        //popup.add(entityAlias);
        //popup.add(deviceAlias);
        popup.add(new JSeparator());
        popup.add(remove);
        popup.add(new JSeparator());
        //	popup.add(view);
        popup.add(status);
        popup.add(properties);
        popup.add(new JSeparator());
        //	popup.add(runJive); // removed on request from ESRF
        popup.add(runAtk);
        popup.add(new JSeparator());
        popup.add(helpItem);

        /*
         * deviceAlias.addActionListener(new ActionListener() { public void
         * actionPerformed(ActionEvent evt) { showDeviceAliasDialog(); } });
         * 
         * entityAlias.addActionListener(new ActionListener() { public void
         * actionPerformed(ActionEvent evt) { showEntityAliasDialog(); } });
         */

        helpItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                help();
            }
        });

        view.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showViewDialog();
            }
        });

        remove.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                removeEntity(false);
            }
        });

        runJive.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                runJive();
            }
        });

        runAtk.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                runAtk();
            }
        });

        status.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showStatus();
            }
        });

        properties.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showPropertiesDialog();
            }
        });

        GridBagConstraints constraints = new GridBagConstraints();
        setLayout(new GridBagLayout());
        constraints.fill = GridBagConstraints.BOTH;
        constraints.weightx = 1;
        constraints.weighty = 1;
        constraints.gridx = constraints.gridy = 0;
        add(new JScrollPane(table), constraints);
    }

    /**
     * <code>initDnd</code> sets up the handeling of drag and drop. Much of
     * this code is heavy magic.
     */
    protected void initDnd() {
        DropTargetListener dtListener = new DropTargetListener();

        dtListener.setDropHandler(new IDropHandler() {

            public void handleDrop(String object, DataFlavor flavor) {
                dtHandleDrop(object, flavor);
            }

            public boolean isDragOn(DataFlavor[] flavors) {
                return EntityTable.this.isDragOn(flavors);
            }

        });

        // The reason we have two lines like this is that we need to
        // handle drop on the table and on the background.

        new DropTarget(this, DnDConstants.ACTION_COPY, dtListener);
        new DropTarget(table, DnDConstants.ACTION_COPY, dtListener);
    }

    /**
     * <code>createViewDialog</code> creates the dialog which shows the
     * view-fields dialog.
     * 
     * @param model
     *            an <code>EntityTableModel</code> value
     */
    protected void createViewDialog(EntityTableModel model) {
        viewDialog = new explorer.ui.Dialog();
        viewDialog.setComponent(new ViewDialog(model));
    }

    /**
     * <code>setModel</code> sets the table-model of this table. It also calls
     * createViewDialog, which is dependent of the model, in adition to setting
     * up the model.
     * 
     * @param model
     *            the model of this table.
     */
    public void setModel(EntityTableModel model) {
        this.model = model;
        model.setColumnModel(table.getColumnModel());
        createViewDialog(model);
        initPreferences();
    }

    /**
     * <code>storePreferences</code> calls this models storePreferences
     *  
     */
    public void storePreferences() {
        model.storePreferences();
        Enumeration e = table.getColumnModel().getColumns();
        while (e.hasMoreElements()) {
            TableColumn c = (TableColumn) e.nextElement();
            putWidth(c.getHeaderValue().toString(), c.getPreferredWidth());
        }

    }

    /**
     * <code>removeEntity</code> removes entry on selected row
     * 
     * @param confirm
     *            A boolean to tell wheather you need deletion confirmation or
     *            not
     */
    protected void removeEntity(boolean confirm) {
        boolean suppress = true;
        if (confirm)
        {
            String message = "Do you wish to remove these ";
            if (this instanceof AttributeTable)
            {
                message += "attributes";
            }
            else if (this instanceof CommandTable)
            {
                message += "commands";
            }
            else
            {
                message += "entities";
            }
            message += " from table ?";
            int ok = JOptionPane.showConfirmDialog(this,
                    message,
                    "Deletion Confirmation",
                    JOptionPane.YES_NO_OPTION);
            if (ok != JOptionPane.OK_OPTION)
            {
                suppress = false;
            }
        }

        while(suppress)
        {
            int[] rows = getSelectedRows();
            if (rows.length == 0) return;
            model.removeEntityAt(rows[0]);
        }
    }

    /**
     * <code>showViewDialog</code> shows the dialog for choosing which fields
     * to view in the table.
     */
    protected void showViewDialog() {
        viewDialog.pack();
        viewDialog.show();
    }

    /**
     * <code>showEntityAliasDialog</code> shows the dialog for entering
     * command and attribute aliases.
     */
    protected void showEntityAliasDialog() {
        IEntity entity;
        EntityAliasDialog dialog;

        if (getSelectedRow() == -1)
            return;

        entity = model.getEntityAt(getSelectedRow());
        dialog = new EntityAliasDialog(this, entity);
        dialog.show();
    }

    /**
     * <code>showDeviceAliasDialog</code> shows the dialog for entering device
     * aliases
     */
    protected void showDeviceAliasDialog() {
        IDevice device;
        DeviceAliasDialog dialog;

        if (getSelectedRow() == -1)
            return;
        device = model.getEntityAt(getSelectedRow()).getDevice();

        dialog = new DeviceAliasDialog(this, device);
        dialog.show();

    }

    /**
     * <code>showPropertiesDialog</code> shows the dialog displaying the
     * properties of the command or attribute.
     */
    protected void showPropertiesDialog() {
        EntityAdapter adapter = model.getAdapterAt(getSelectedRow());

        if (propertyDialog == null) {
            propertyDialog = new explorer.ui.Dialog();
            propertyPanel = new PropertyDialog();
            propertyDialog.setComponent(propertyPanel);
        }

        propertyPanel.setModel(adapter);
        propertyDialog.pack();
        propertyDialog.show();
    }

    /**
     * <code>aliasChanged</code> is called when an entity or device gets a new
     * alias so that the table can repaint it self.
     *  
     */
    public void aliasChanged() {
        getRootPane().repaint();
    }

    /**
     * <code>runAtk</code> runs ATKPanel with the device on the selected row.
     */
    protected void runAtk() {
        int row = getSelectedRow();
        IEntity entity = model.getEntityAt(row);
        RunUI.runAtkPanel(entity.getDevice());
    }

    /**
     * <code>runJive</code> runs jive
     *  
     */
    protected void runJive() {
        //int row = getSelectedRow();
        //IEntity entity = model.getEntityAt(row);
        RunUI.runJive();
    }

    /**
     * <code>showStatus</code> shows the status of the device on the selected
     * row.
     */
    protected void showStatus() {
        IEntity entity = model.getEntityAt(getSelectedRow());
        if (statusViewer == null) {
            statusViewer = SingletonStatusViewer.getInstance();
        }
        statusViewer.setModel(entity.getDevice());
        statusViewer.show();
    }

    /**
     * <code>getSelectedRow</code> convenience method. Wraps
     * JTable.getSelectedRow
     * 
     * @return an <code>int</code> value, the selected row.
     */
    public int getSelectedRow() {
        return table.getSelectedRow();
    }

    /**
     * <code>getSelectedRows</code> convenience method. Wraps
     * JTable.getSelectedRows
     * 
     * @return an <code>int[]</code> value, the selected rows.
     */
    public int[] getSelectedRows() {
        return table.getSelectedRows();
    }

    /**
     * <code>getRowAtPoint</code> convenience method. Wraps JTable.rowAtPoint
     * 
     * @param point
     *            a <code>Point</code> value normally obtained from a
     *            MouseEvent
     * @return an <code>int</code> value, the row.
     */
    public int getRowAtPoint(Point point) {
        return table.rowAtPoint(point);
    }

    /**
     * <code>getColumnAtPoint</code> convenience method. Wraps
     * JTable.columnAtPoint
     * 
     * @param point
     *            a <code>Point</code> value normally obtained from a
     *            MouseEvent
     * @return an <code>int</code> value, the column.
     */
    public int getColumnAtPoint(Point point) {
        return table.columnAtPoint(point);
    }

    /**
     * <code>setRowSelectionInterval</code> wraps
     * JTable.setRowSelectionInterval
     * 
     * @param start
     *            an <code>int</code> value
     * @param end
     *            an <code>int</code> value
     */
    public void setRowSelectionInterval(int start, int end) {
        table.setRowSelectionInterval(start, end);
    }

    /**
     * <code>getValueAt</code> wraps JTable.getValueAt
     * 
     * @param row
     *            an <code>int</code> value
     * @param column
     *            an <code>int</code> value
     * @return an <code>Object</code> value
     */
    public Object getValueAt(int row, int column) {
        return table.getValueAt(row, column);
    }

    /**
     * <code>getSelectedColumn</code> wraps JTable.getSelectedColumn
     * 
     * @return an <code>int</code> value
     */
    public int getSelectedColumn() {
        return table.getSelectedColumn();
    }

    /**
     * <code>help</code> shows the helpwindow with help for this table.
     */
    public void help() {
        HelpWindow.getInstance().showUrl(getClass().getResource(helpUrl));
    }

    /**
     * <code>isDragOn</code> is called to decide if the object being dragged
     * over us is wanted or not.
     * 
     * @param flavors
     *            a <code>DataFlavor[]</code> value
     * @return a <code>boolean</code> value, true if we accept the dragged
     *         object.
     * @see fr.esrf.tangoatk.dnd
     */
    protected boolean isDragOn(DataFlavor[] flavors) {
        for (int i = 0; i < flavors.length; i++)
            if (flavors[i].getMimeType().startsWith(flavor))
                return true;
        return false;
    }

    /**
     * <code>getModel</code>
     * 
     * @return a <code>TableModel</code> value
     */
    public TableModel getModel() {
        return table.getModel();
    }

    /**
     * <code>initPreferences</code> initialises the preferences for the
     * subclasses of this class
     *  
     */
    protected abstract void initPreferences();

    /**
     * <code>initHelp</code> initialises the help for the subclasses of this
     * class.
     *  
     */
    protected abstract void initHelp();

    /**
     * <code>initMenus</code> initialises the menus for the subclasses of this
     * class
     */
    protected abstract void initMenus();

    /**
     * <code>dtHandleDrop</code> is called when something is dragged over the
     * table if <code>isDragOn</code> has returned true.
     * 
     * @param obj
     *            a <code>String</code> value, the thingy being dropped,
     *            normally name of the entity.
     * @param flavor
     *            a <code>DataFlavor</code> value, the mimetype of the entity
     *            being dropped.
     * @see fr.esrf.tangoatk.dnd
     */
    protected abstract void dtHandleDrop(String obj, DataFlavor flavor);

    /**
     * <code>showPopup</code> is called each time a mouse is pressed, released
     * or clicked on the table.
     * 
     * @param evt
     *            a <code>MouseEvent</code> value
     */
    protected abstract void showPopup(MouseEvent evt);

    /**
     * <code>entityTableMouseClicked</code> is called each time a mouse is
     * clicked on the table.
     * 
     * @param evt
     *            a <code>MouseEvent</code> value
     */
    protected abstract void entityTableMouseClicked(MouseEvent evt);

    /**
     * <code>getPrefWidth</code>
     *
     * @param name a <code>String</code> value
     * @param def an <code>int</code> value
     * @return an <code>int</code> value
     */
    protected int getPrefWidth(String name, int def) {
        String pref = model.getPreferencePrefix().append(name).append("Width")
                .toString();

        return preferences.getInt(pref, def);
    }

    /**
     * <code>putWidth</code>
     *
     * @param name a <code>String</code> value
     * @param val an <code>int</code> value
     */
    protected void putWidth(String name, int val) {
        String pref = model.getPreferencePrefix().append(name).append("Width")
                .toString();
        preferences.putInt(pref, val);
    }

    /**
     * <code>createTableColumn</code> creates a default tablecolumn, to be
     * overriden in subclasses.
     *
     * @param name a <code>String</code> value, the header name
     * @param i an <code>int</code>, value the model index
     * @return a <code>TableColumn</code> value
     */
    protected TableColumn createTableColumn(String name, int i) {
        return new TableColumn(i);
    }

    /**
     * A class to manage attributes/commands properties
     * @author SOLEIL
     */
    class PropertyDialog extends JPanel implements IApplicable {
        PropertyListViewer2 propertyPanel;

        EntityAdapter adapter;

        PropertyDialog() {
            initComponents();
        }

        public void ok() {
            apply();
            cancel();
        }

        public void apply() {
            propertyPanel.store();
            // make sure the changes are reflected on the table.
            adapter.reloadProperties();
        }

        public void cancel() {
            this.getRootPane().getParent().setVisible(false);
        }

        protected void initComponents() {
            propertyPanel = new PropertyListViewer2();
            propertyPanel.setEditable(true);
            this.add(propertyPanel);
        }

        void setModel(EntityAdapter adapter) {
            this.adapter = adapter;
            propertyPanel.setModel(adapter.getEntity().getPropertyMap());
        }
    }

    public boolean isAdmin ()
    {
        return admin;
    }

    public void setAdmin (boolean admin)
    {
        this.admin = admin;
    }
}