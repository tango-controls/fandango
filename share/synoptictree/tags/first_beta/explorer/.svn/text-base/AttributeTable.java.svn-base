// File:          AttributeTable.java
// Created:       2002-09-10 10:04:14, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-16 15:48:31, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.Color;
import java.awt.Component;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.Transferable;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JSeparator;
import javax.swing.JTable;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import explorer.ui.PreferencesDialog;
import explorer.ui.RefreshUI;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IBooleanScalar;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.IScalarAttribute;
import fr.esrf.tangoatk.widget.attribute.Trend;
import fr.esrf.tangoatk.widget.dnd.NodeFactory;
import fr.esrf.tangoatk.widget.dnd.NumberScalarNode;
import fr.esrf.tangoatk.widget.util.HelpWindow;

/**
 * <code>AttributeTable</code> implements the table holding the attributes.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class AttributeTable extends EntityTable {
    /** Allows in menu to set an attribute */
    protected JMenuItem set;
    /** Allows in menu to add an attribute in global trend */
    protected JMenu globalTrendMenu;
    /** Allows in menu to add an attribute in Y1 axis of global trend */
    protected JMenuItem globalTrendY1MenuItem;
    /** Allows in menu to add an attribute in Y2 axis of global trend */
    protected JMenuItem globalTrendY2MenuItem;
    /** Allows in menu to add an attribute in X axis of global trend */
    protected JMenuItem globalTrendXMenuItem;
    /** Allows in menu to add an attribute global trend and remove it from axis*/
    protected JMenuItem globalTrendNoneMenuItem;
    /** Allows in menu to remove an attribute from trend */
    protected JMenuItem removeTrend;
    /** Allows in menu to refresh attributes */
    protected JMenuItem refresh;
    /** The trend */
    protected Trend trendPanel;
    /** The global trend */
    protected Trend globalTrend;
    /** The trend frame */
    protected explorer.ui.Dialog trendFrame;
    /** The "set" dialog box for attributes */
    protected SetDialog setDialog;

    protected boolean synchronizedPeriod = false;

    private RefreshUI refreshui;

    /**
     * Creates a new <code>AttributeTable</code> instance
     * 
     * @param isAdmin
     *            a <code>boolean</code> value, is true if the table is used
     *            in administrator mode.
     */
    public AttributeTable(AttributeTableModel model, Preferences prefs,
            boolean isAdmin) {
        setAdmin(isAdmin);
        refreshui = null;
        preferences = prefs;
        initComponents(model, isAdmin);
        table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        for (int i = 0; i < table.getColumnCount(); i++)
        {
            table.getColumn(table.getColumnName(i)).setPreferredWidth(87);
            table.getColumn(table.getColumnName(i)).setWidth(87);
        }
        flavor = NodeFactory.MIME_ATTRIBUTE;
        table.setTransferHandler( 
            new fr.esrf.tangoatk.widget.dnd.TransferHandler() {
                protected Transferable createTransferable (JComponent comp)
                {
                    if ( !( comp instanceof JTable ) ) return null;
                    // JTable t = (JTable) comp;
                    IEntity entity = ( (AttributeTableModel) getModel() )
                            .getEntityAt( getSelectedRow() );
                    if ( !( entity instanceof INumberScalar ) ) return null;
                    INumberScalar scalar = (INumberScalar) entity;
                    return new NumberScalarNode( scalar );
                }
            }
        );

        table.setDragEnabled(true);
        setModel(model);
    }

    public JTable getMyTable(){
        return table;
    }

    public void setRefreshUI(RefreshUI ref) {
        refreshui = ref;
    }

    /**
     * <code>dtHandleDrop</code> handles the dropping of an object onto this
     * table. The object is an attribute.
     * 
     * @param name
     *            a <code>String</code> value
     * @param flavor
     *            a <code>DataFlavor</code> value
     * @see fr.esrf.tangoatk.widget.dnd
     */
    protected void dtHandleDrop(String name, DataFlavor flavor) {
        String mimeType = flavor.getMimeType();

        if (mimeType.startsWith(NodeFactory.MIME_STRINGSCALAR)) {
            ((AttributeTableModel) model).addStringScalar(name);
            return;
        }

        if (mimeType.startsWith(NodeFactory.MIME_NUMBERSCALAR)) {
            ((AttributeTableModel) model).addNumberScalar(name);
            return;
        }

        if (mimeType.startsWith(NodeFactory.MIME_NUMBERSPECTRUM)) {
            ((AttributeTableModel) model).addNumberSpectrum(name);
            return;
        }

        if (mimeType.startsWith(NodeFactory.MIME_NUMBERIMAGE)) {
            ((AttributeTableModel) model).addNumberImage(name);
            return;
        }
    }

    /**
     * Shows the "set" dialog box of the selected attribute in the table
     */
    protected void showSetDialog() {
        IAttribute attribute;
        int row = getSelectedRow();
        if (row == -1)
            return;
        attribute = (IAttribute) model.getEntityAt(row);
        if (!attribute.isWritable())
            return;

        if (attribute instanceof IBooleanScalar)
        {
            boolean val = ((IBooleanScalar)attribute).getValue();
            ((IBooleanScalar)attribute).setValue(!val);
            repaint();
        }
        else if (attribute instanceof IScalarAttribute)
        {
            setDialog = new SetDialog((IScalarAttribute) attribute);
            setDialog.setVisible(true);
        }
    }

    /**
     * Refreshes informations (like value) about the selected attribute in the
     * table
     */
    protected void refreshEntity() {
        int[] rows = getSelectedRows();
        for (int i = 0; i < rows.length; i++)
        {
            IAttribute attribute = (IAttribute) model.getEntityAt(rows[i]);
            attribute.refresh();
            attribute.getDevice().refresh();
        }
    }

    /**
     * Sets the trend to a specified trend
     * 
     * @param trend
     *            the trend
     */
    public void setGlobalTrend(Trend trend) {
        globalTrend = trend;
        if (globalTrend != null && globalTrend.getModel() != null)
            globalTrend.getModel().setSynchronizedPeriod(synchronizedPeriod);
    }

    /**
     * Adds the selected attribute in the trend
     */
    protected void addGlobalTrend(int axis)
    {
        int[] rows = getSelectedRows();
        for (int i = 0; i < rows.length; i++)
        {
            IAttribute attr = (IAttribute) model.getEntityAt(rows[i]);
            if (attr instanceof INumberScalar)
            {
                //globalTrend.addAttribute((INumberScalar) attr);
                globalTrend.addToAxis((INumberScalar)attr, axis, true);
                ((AttributeTableModel) model).removeFromRefresher(attr);
            }
            else continue;
        }
        if (globalTrend.getModel()!=null)
        {
            if ( !globalTrend.getModel().isEmpty() 
                 && !globalTrend.getModel().isRefresherStarted()
               )
            {
                globalTrend.getModel().startRefresher();
            }
            globalTrend.getModel().setSynchronizedPeriod(synchronizedPeriod);

        }
        if (refreshui != null)
        {
            refreshui.enableStopBit();
            refreshui.enableStartAndRefreshBit();
        }
    }

    /**
     * Adds an attribute in trend
     * @param attr The attribute to add in trend
     * @param axis The axis on which you want to set your attribute.
     * @see fr.esrf.tangoatk.widget.attribute.Trend#SEL_Y1
     * @see fr.esrf.tangoatk.widget.attribute.Trend#SEL_Y2
     * @see fr.esrf.tangoatk.widget.attribute.Trend#SEL_X
     * @see fr.esrf.tangoatk.widget.attribute.Trend#SEL_NONE
     */
    public void addTrend(IEntity attr, int axis)
    {
        if (attr instanceof INumberScalar)
        {
            globalTrend.addToAxis((INumberScalar) attr, axis, true);
            ((AttributeTableModel) model).removeFromRefresher((IAttribute)attr);
        }
        if (globalTrend.getModel()!=null)
        {
            if ( !globalTrend.getModel().isEmpty() 
                 && !globalTrend.getModel().isRefresherStarted()
               )
            {
                globalTrend.getModel().startRefresher();
            }
            globalTrend.getModel().setSynchronizedPeriod(synchronizedPeriod);
        }
        if (refreshui != null)
        {
            refreshui.enableStopBit();
            refreshui.enableStartAndRefreshBit();
        }
    }

    /**
     * Removes the selected attribute from trend
     */
    protected void removeTrend() {
        int[] rows = getSelectedRows();
        for (int i = 0; i < rows.length; i++)
        {
            IAttribute attr;
            attr = (IAttribute) model.getEntityAt(rows[i]);
            if (attr instanceof INumberScalar)
            {
                globalTrend.removeAttribute((INumberScalar) attr);
                ((AttributeTableModel) model).addToRefresher(attr);
            }
        }
        if ( refreshui != null
             && ( globalTrend.getModel() == null 
                  || globalTrend.getModel().isEmpty() 
                 ) 
           )
        {
            if ( ( (AttributeTableModel) model ).isRefresherStarted() )
            {
                refreshui.enableStopBit();
                refreshui.disableStartAndRefreshBit();
            }
            else
            {
                refreshui.disableStopBit();
                refreshui.enableStartAndRefreshBit();
            }
        }
        if ( globalTrend.getModel() != null
             && globalTrend.getModel().isEmpty()
           )
        {
            globalTrend.getModel().stopRefresher();
        }
    }

    /**
     * Initializes the help page
     */
    protected void initHelp() {
        helpUrl = "/explorer/html/AttributeTableHelp.html";

        HelpWindow.getInstance().addCategory("Attribute Table",
                "Attribute table", getClass().getResource(helpUrl));
    }

    /**
     * Initializes the menu panel (obtained with right click)
     */
    protected void initMenus() {
        refresh = new JMenuItem("Refresh");
        set = new JMenuItem("Set last selected attribute...");
        //	trend = new JMenuItem("Trend...");
        globalTrendMenu = new JMenu("Add to trend");
        globalTrendY1MenuItem = new JMenuItem("set to Y1 axis");
        globalTrendY2MenuItem = new JMenuItem("set to Y2 axis");
        globalTrendXMenuItem = new JMenuItem("set to X axis");
        globalTrendNoneMenuItem = new JMenuItem("do not set to any axis");
        removeTrend = new JMenuItem("Remove from trend");

        refresh.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                refreshEntity();
            }
        });

        set.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showSetDialog();
            }
        });

        globalTrendY1MenuItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                addGlobalTrend(Trend.SEL_Y1);
            }
        });

        globalTrendY2MenuItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                addGlobalTrend(Trend.SEL_Y2);
            }
        });

        globalTrendXMenuItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                addGlobalTrend(Trend.SEL_X);
            }
        });

        globalTrendNoneMenuItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                addGlobalTrend(Trend.SEL_NONE);
            }
        });

        removeTrend.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                removeTrend();
            }
        });

        globalTrendMenu.add(globalTrendY1MenuItem);
        globalTrendMenu.add(globalTrendY2MenuItem);
        globalTrendMenu.add(globalTrendXMenuItem);
        globalTrendMenu.add(globalTrendNoneMenuItem);

        popup.add(refresh);
        popup.add(new JSeparator());
        //	popup.add(set);
        popup.add(globalTrendMenu);
        popup.add(removeTrend);
    }

    /**
     * Initializes the presentation preferences panel
     */
    protected void initPreferences() {
        PreferencesDialog.getInstance().addCategory("Attribute table",
                "visible fields", new ViewDialog(model));
    }

    /**
     * Shows the menu panel (obtained with right click)
     * 
     * @param evt
     *            the mouse event for the "click"
     */
    protected void showPopup(MouseEvent evt) {
        int row = getRowAtPoint(evt.getPoint());

        if (row == -1)
            return;

        int[] rows = getSelectedRows();


        if (evt.isPopupTrigger()) {

            if (evt.isControlDown())
            {
                table.addRowSelectionInterval(row,row);
            }
            else if (evt.isShiftDown())
            {
                int min = rows[0];
                for (int i = 0; i < rows.length; i++)
                {
                    if (rows[i] < min) min = rows[i];
                }
                table.addRowSelectionInterval(min, row);
            }
            else
            {
                boolean isInSelection = false;
                for (int i = 0; i < rows.length; i++)
                {
                    if (rows[i] == row)
                    {
                        isInSelection = true;
                        break;
                    }
                }
                if (!isInSelection)
                {
                    table.clearSelection();
                    table.setRowSelectionInterval(row,row);
                }
            }
            rows = getSelectedRows();
            
            boolean addTrend = false;
            boolean remTrend = false;
            for (int i = 0; i < rows.length; i++)
            {
                IAttribute attribute = (IAttribute) model.getEntityAt(rows[i]);
                if (attribute instanceof INumberScalar
                        && globalTrend.getModel() != null
                        && globalTrend.getModel().contains(attribute))
                {
                    remTrend = true;
                }
                if (attribute instanceof INumberScalar
                        && (globalTrend.getModel() == null || !globalTrend
                                .getModel().contains(attribute)))
                {
                    addTrend = true;
                }
            }

            set.setEnabled( ((IAttribute) model.getEntityAt(row)).isWritable() );
            removeTrend.setEnabled(remTrend);
            globalTrendMenu.setEnabled(addTrend);

            popup.show(evt.getComponent(), evt.getX(), evt.getY());
        }
    }

    /**
     * Manages the consequences of a mouse click on the table
     * 
     * @param evt
     *            the mouse "click" event
     */
    protected void entityTableMouseClicked(MouseEvent evt) {
        int row = getRowAtPoint(evt.getPoint());
        if (row == -1)
            return;

        IAttribute attribute = (IAttribute) model.getEntityAt(row);

        if (model.isExecuteColumn(getColumnAtPoint(evt.getPoint()))// used getColumnAtPoint(evt.getPoint()) instead of getSelectedColumn for right click compatibility
                && !evt.isPopupTrigger()
                && attribute.isWritable()) {
            showSetDialog();
        }
    }

    protected TableColumn createTableColumn(String name, int i) {
        //final AttributeTableModel myModel = (AttributeTableModel) model;
        int tempcol = -1;
        try
        {
            tempcol = table.getColumnModel().getColumnIndex(name);
        }
        catch(Exception e)
        {
            tempcol = -1;
        }
        final int col = tempcol;
        if (AttributeTableModel.DEVICE == name) {
            return new TableColumn(i, 75, deviceRenderer, null);
        }
        if (AttributeTableModel.VALUE == name) {
            return new TableColumn(i, 75, entityRenderer, null);
        }

        if (AttributeTableModel.SET == name) {
            return new TableColumn(i, 75, new TableCellRenderer() {
                JButton renderer;

                public Component getTableCellRendererComponent(JTable table,
                        Object value, boolean select, boolean focus, int row,
                        int column) {
                    if (renderer == null)
                        renderer = new JButton(getValueAt(row,col==-1?column:col).toString());
                    else renderer.setText(getValueAt(row,col==-1?column:col).toString());

                    JButton dummy = new JButton();
                    if (select)
                    {
                        renderer.setBackground(Color.DARK_GRAY);
                        renderer.setForeground(Color.WHITE);
                    }
                    else
                    {
                        renderer.setBackground(dummy.getBackground());
                        renderer.setForeground(dummy.getForeground());
                    }

                    IAttribute attribute = (IAttribute) model.getEntityAt(row);
                    renderer.setEnabled(attribute.isWritable());
                    return renderer;
                }
            }, null);
        }

        return new TableColumn(i, 75);
    }

    /**
     * Sets preferences to a certain preferences value
     * @param preferences the preferences value
     */
    public void setPreferences(Preferences preferences) {
    	super.setPreferences(preferences);
    	String s = preferences.getString("globalGraphSettings", null);
    	if (s != null) {
    		//JOptionPane.showMessageDialog(null, "S is not null and is:"+s);
    		/*try {System.out.println("AttributeTable:setPreferences(), trend settings are: \n"+globalTrend.getSettings());
    		} catch (Exception e) {System.out.println("AttributeTable:setPreferences(), Exception ("+e.getMessage()+") getting trend settings"); }*/
        	System.out.println("Updating globalTrend settings, modifying background\n");
        	s=s.replace("graph_background:180,180,180","graph_background:246,245,244");
    		String err = globalTrend.setSetting(s);
    		/*try {System.out.println("AttributeTable:setPreferences(), trend settings now are: \n"+globalTrend.getSettings());
    		} catch (Exception e) {System.out.println("AttributeTable:setPreferences(), Exception ("+e.getMessage()+") getting trend settings"); }*/
    		if (err.length() > 0)
    			JOptionPane.showMessageDialog(null,
    					"Failed apply trend configuration: " + err, "Error",
    					JOptionPane.ERROR_MESSAGE);
    	}// end if (s != null)
    }// end setPreferences

    /**
     * Calls this models storePreferences
     */
    public void storePreferences() {
        super.storePreferences();

        // Save global trend settings
        preferences.putString("globalGraphSettings", globalTrend.getSettings());
    }

    /**
     * A quick access to the setSynchronizedPeriod() of the AEntityList of the trend
     * @param synchro The boolean parameter of the corresponding method
     * @see fr.esrf.tangoatk.core.AEntityList#setSynchronizedPeriod(boolean)
     */
    public void setSynchronizedPeriod(boolean synchro)
    {
        synchronizedPeriod = synchro;
        if (globalTrend != null && globalTrend.getModel() != null)
            globalTrend.getModel().setSynchronizedPeriod(synchronizedPeriod);
    }

}