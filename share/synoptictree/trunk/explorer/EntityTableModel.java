// File:          EntityAdapter.java
// Created:       2002-09-13 12:55:58, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-30 11:26:8, erik>
// 
// $Id$
// 
// Description:       
package explorer;

import java.util.ArrayList;
import java.util.List;
import javax.swing.JComponent;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.TableColumnModel;
import fr.esrf.tangoatk.core.AEntityList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.IDevice;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.IErrorListener;

/**
 * <code>EntityTableModel</code> implements parts of the table model needed by
 * EntityTable
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public abstract class EntityTableModel extends AbstractTableModel implements
        explorer.ui.Refresher, explorer.ui.Clearable {

    protected List listenerList = new ArrayList();
    protected List columnIdentifiers, columnNames, adapters;
    protected AEntityList entities;
    protected TableColumnModel columnModel;
    protected Status status;
    protected Preferences preferences;
    protected DeviceList deviceList;
    boolean disregardPreference = false;
    public static String DEVICE = "Device";
    public static String NAME = "Name";
    public static String LEVEL = "Level";
    protected boolean refresherStarted = false;

    /**
     * Adds a ColumnListener in the list of listeners
     * 
     * @param l
     *            the ColumnListener to add
     */
    public void addColumnListener(ColumnListener l) {
        listenerList.add(l);
    }

    /**
     * Removes a ColumnListener from the list of listeners
     * 
     * @param l
     *            the ColumnListener to remove
     */
    public void removeColumnListener(ColumnListener l) {
        listenerList.remove(l);
    }

    /**
     * Sets the preferences to a specified value
     * 
     * @param preferences
     *            the value to set in preferences
     */
    public void setPreferences(Preferences preferences) {
        this.preferences = preferences;
    }

    /**
     * <code>getEntityAlias</code> returns the alias for a given entity. If
     * the alias is <code>null</code> the name is returned.
     * 
     * @param entity
     *            an <code>IEntity</code> value
     * @return a <code>String</code> value
     */
    public String getEntityAlias(IEntity entity) {
        String tmp = entity.getAlias();
        return tmp != null ? tmp : entity.getName();
    }

    /**
     * <code>getDeviceAlias</code> returns the alias for a given device. If
     * the alias is <code>null</code>, the name is returned
     * 
     * @param device
     *            an <code>IDevice</code> value
     * @return a <code>String</code> value
     */
    public String getDeviceAlias(IDevice device) {
        String tmp = device.getAlias();
        return tmp != null ? tmp : device.getName();
    }

    /**
     * <code>setColumnModel</code> sets the columnmodel of the table. we need
     * this for our internal class Column. Maybe a hint of bad design?
     * 
     * @param model
     *            a <code>TableColumnModel</code> value
     */
    public void setColumnModel(TableColumnModel model) {
        columnModel = model;
        initColumns();
    }

    /**
     * <code>storePreferences</code> stores the preferences.
     *  
     */
    public void storePreferences() {
        for (int i = 0; i < columnNames.size(); i++) {
            String name = (String) columnNames.get(i);
            int index = -1;
            try {
                index = columnModel.getColumnIndex(name);
            }
            catch (IllegalArgumentException e) {
                // column name not in columnmodel,
                ;
            }
            putIndex(name, index);
        }

    }

    /**
     * <code>getAdapterAt</code> returns the EntityAdapter for a given row.
     * 
     * @param row
     *            an <code>int</code> value
     * @return an <code>EntityAdapter</code> value
     */
    EntityAdapter getAdapterAt(int row) {
        return (EntityAdapter) adapters.get(row);
    }

    /**
     * <code>getRowCount</code> returns the number of rows
     * 
     * @return an <code>int</code> value
     */
    public int getRowCount() {
        if (adapters == null)
            return 0;
        return adapters.size();
    }

    /**
     * <code>getColumnCount</code> returns the number of columns
     * 
     * @return an <code>int</code> value
     */
    public int getColumnCount() {
        return columnIdentifiers.size();
    }

    /**
     * <code>getColumnName</code>
     * 
     * @param column
     *            an <code>int</code> value
     * @return a <code>String</code> value containing the name of the column,
     *         used for the header.
     */
    public String getColumnName(int column) {
        if (column >= columnIdentifiers.size()) {
            return "URK";
        }

        return columnIdentifiers.get(column).toString();
    }

    /**
     * <code>exists</code> returns true if the given entity exists in the
     * model.
     * 
     * @param entity
     *            an <code>IEntity</code> value
     * @return a <code>boolean</code> value
     */
    public boolean exists(IEntity entity) {
        for (int i = 0; i < adapters.size(); i++) {
            if (getEntityAt(i).getName().equals(entity.getName()))
                return true;
        }
        return false;
    }

    /**
     * Adds a column in the table
     * 
     * @param name
     *            the column name
     */
    public void addColumn(String name) {

        boolean found = false;
        int i = 0;

        while (!found && i < getColumnCount()) {
            found = name.equalsIgnoreCase(columnIdentifiers.get(i).toString());
            if (!found)
                i++;
        }

        // Column already entered and visible
        if (found)
            return;

        columnIdentifiers.add(name);
        putIndex(name, columnIdentifiers.size() - 1);
    }

    /**
     * Removes a column from table
     * 
     * @param name
     *            the column name
     */
    public void removeColumn(String name) {
        boolean found = false;
        int i = 0;

        while (!found && i < getColumnCount()) {
            found = name.equalsIgnoreCase(columnIdentifiers.get(i).toString());
            if (!found)
                i++;
        }

        if (found)
            columnIdentifiers.remove(i);

        putIndex(name, -1);
    }

    /**
     * Reorders columns in the order of the list of visible columns
     */
    public void reorderColumns() {
        if (columnNames == null)
            return;

        for (int i = 0; i < columnNames.size(); i++) {
            String name = (String) columnNames.get(i);
            int index = getIndex(name, -1);
            if (index == -1) {
                removeColumn(name);
            }
            else {
                addColumn(name);
            }
        }
        publishColumnChange();
    }

    /**
     * Notifies listeners about changes in columns
     */
    void publishColumnChange() {
        for (int i = 0; i < listenerList.size(); i++) {
            ((ColumnListener) listenerList.get(i)).columnsChanged();
        }
    }

    /**
     * Tells if a column is visible or not
     * 
     * @param name
     *            the name of the column to test
     * @return <code>true</code> if the column is visible, <code>false</code>
     *         otherwise
     */
    public boolean isVisible(String name) {
        boolean found = false;
        int i = 0;
        while (!found && i < getColumnCount()) {
            found = name.equalsIgnoreCase(columnIdentifiers.get(i).toString());
            if (!found)
                i++;
        }
        return found;
    }

    /**
     * Sets visible or hide columns
     * 
     * @param names
     *            the list of columns to set visible or to hide
     * @param visible
     *            a list of booleans corresponding to the columns list following
     *            this logic :<code>true</code> to set the column visible,
     *            <code>false</code> to hide the column
     */
    public void setVisible(String[] names, boolean[] visible) {
        for (int i = 0; i < names.length; i++) {
            if (visible[i]) {
                addColumn(names[i]);
            }
            else {
                removeColumn(names[i]);
            }
            disregardPreference = true;
            fireTableStructureChanged();
            disregardPreference = false;
        }
    }

    /**
     * <code>containsEntity</code>
     * 
     * @param e
     *            an <code>IEntity</code> value
     * @return a <code>boolean</code> value
     */
    public boolean containsEntity(IEntity e) {
        return entities.contains(e);
    }

    /**
     * <code>addEntities</code>
     * 
     * @param entityList
     *            an <code>AEntityList</code> value
     */
    public void addEntities(AEntityList entityList) {
        for (int i = 0; i < entityList.size(); i++) {
            addEntity((IEntity) entityList.get(i));
        }

        reorderColumns();
        fireTableStructureChanged();
    }

    /**
     * <code>removeEntityAt</code> removes the entity at the given row
     * 
     * @param row
     *            an <code>int</code> value
     */
    public void removeEntityAt(int row) {
        ((EntityAdapter) adapters.get(row)).remove();
        try
        {
            IEntity entity = getEntityAt(row);
            if (deviceList != null)
            {
                deviceList.remove(entity.getDevice());
            }
        }
        catch(Exception e)
        {
            // nothing to do
        }
        adapters.remove(row);
        entities.remove(row);
        fireTableRowsDeleted(row, row);

    }

    /**
     * <code>getList</code> returns the list of this table
     * 
     * @return an <code>AEntityList</code> value
     */
    public AEntityList getList() {
        return entities;
    }

    /**
     * <code>setRefreshInterval</code> sets the refreshinteval of this tables
     * list
     * 
     * @param milliseconds
     *            an <code>int</code> value
     */
    public void setRefreshInterval(int milliseconds) {
        preferences.putInt("refreshInterval", milliseconds);
        entities.setRefreshInterval(milliseconds);
        if (deviceList != null)  deviceList.setRefreshInterval(milliseconds);
    }

    /**
     * <code>startRefresher</code> starts the refresher of this tables list
     */
    public void startRefresher() {
        if (!refresherStarted)
        {
            entities.startRefresher();
            refresherStarted = true;
        }
        if (deviceList != null)  deviceList.start();
    }

    /**
     * <code>stopRefresher</code> stops the refresher of this tables list
     */
    public void stopRefresher() {
        refresherStarted = false;
        entities.stopRefresher();
        if (deviceList != null)  deviceList.stop();
    }

    /**
     * <code>refresh</code> refreshes this tables list once
     *  
     */
    public void refresh() {
        entities.refresh();
        if (deviceList != null)  deviceList.refresh();
    }

    /**
     * <code>addErrorListener</code> adds an <code>IErrorListener</code> to
     * the list of this table.
     * 
     * @param listener
     *            an <code>IErrorListener</code> value
     */
    public void addErrorListener(IErrorListener listener) {
        entities.addErrorListener(listener);
    }

    /**
     * <code>getRefreshInterval</code> returns the refresh interval of this
     * tables list.
     * 
     * @return an <code>int</code> value
     */
    public int getRefreshInterval() {
        return entities.getRefreshInterval();
    }

    /**
     * <code>clear</code> removes all entities and removes all listeners to
     * the attributes/commands contained in entities
     */
    public void clear() {
        int size = adapters.size();

        for (int i = 0; i < size; i++) {
            EntityAdapter adapter = (EntityAdapter) adapters.get(i);
            adapter.remove();
        }

        adapters.clear();
        entities.clear();
        fireTableRowsDeleted(0, size);
    }

    /**
     * <code>getAllColumnNames</code>
     * 
     * @return a <code>java.util.List</code> value containing all column names
     */
    public java.util.List getAllColumnNames() {
        return columnNames;
    }

    /**
     * <code>getEntityAt</code> returns the entity at a given row.
     * 
     * @param row
     *            an <code>int</code> value
     * @return an <code>IEntity</code> value
     */
    public IEntity getEntityAt(int row) {
        return ((EntityAdapter) adapters.get(row)).getEntity();
    }

    /**
     * <code>getIndex</code>
     * 
     * @param name
     *            a <code>String</code> value
     * @param def
     *            an <code>int</code> value
     * @return an <code>int</code> value which is the index set in the
     *         preferences if the preference is found, <code>def</code> if
     *         not.
     */
    int getIndex(String name, int def) {
        if (disregardPreference)
            return def;

        String pref = getPreferencePrefix().append(name).append("Index")
                .toString();
        return preferences.getInt(pref, def);
    }

    /**
     * <code>putIndex</code> sets an index in the preference
     * 
     * @param name
     *            a <code>String</code> value
     * @param val
     *            an <code>int</code> value
     */
    void putIndex(String name, int val) {
        String pref = getPreferencePrefix().append(name).append("Index")
                .toString();
        preferences.putInt(pref, val);
    }

    /**
     * <code>getRenderer</code>
     * 
     * @param o
     *            an <code>Object</code> value being rendered
     * @param column
     *            a <code>String</code> value containing the name of the
     *            column for this renderer
     * @return a <code>JComponent</code> value the renderer.
     */
    JComponent getRenderer(Object o, String column) {
        try {
            int index = columnModel.getColumnIndex(column);
            return ((MyCellRenderer) columnModel.getColumn(index)
                    .getCellRenderer()).getRenderer(o);

        }
        catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
        return null;
    }

    /**
     * <code>getDeviceRenderer</code>
     * 
     * @param deviceName
     *            a <code>String</code> value
     * @return a <code>JComponent</code> value
     */
    JComponent getDeviceRenderer(String deviceName) {
        return getRenderer(deviceName, DEVICE);
    }

    /**
     * <code>getPreferencePrefix</code>
     * 
     * @return a <code>StringBuffer</code> value
     */
    protected abstract StringBuffer getPreferencePrefix();

    /**
     * <code>isExecuteColumn</code>
     * 
     * @param i
     *            an <code>int</code> value
     * @return a <code>boolean</code> value
     */
    protected abstract boolean isExecuteColumn(int i);

    /**
     * <code>initColumns</code> initialises the columns.
     *  
     */
    protected abstract void initColumns();

    /**
     * <code>addEntity</code>
     * 
     * @param entity
     *            an <code>IEntity</code> value
     */
    protected abstract void addEntity(IEntity entity);

    /**
     * <code>load</code> adds an attribute or command to the table.
     * Sets alias to null.
     *
     * @param name a <code>String</code> value containing the name of
     * the attribute or command.
     * @exception ConnectionException if an error occurs
     */
    public void load(String name) throws ConnectionException {
        load(name, null, null);
    }

    /**
     * <code>load</code> adds an attribute or command to the table.
     *
     * @param name a <code>String</code> value containing the name of
     * the attribute or command.
     * @param alias a <code>String</code> value containing the alias of
     * the attribute or command.
     * @param deviceAlias a <code>String</code> value
     * @exception ConnectionException if an error occurs
     */
    public abstract void load(String name, String alias, String deviceAlias)
            throws ConnectionException;

    public DeviceList getDeviceList ()
    {
        return deviceList;
    }

    public void setDeviceList (DeviceList deviceList)
    {
        this.deviceList = deviceList;
    }

    /**
     * Returns a boolean to know wheather the refresher of the entity list is started or not
     * @return A boolean to know wheather the refresher of the entity list is started or not
     */
    public boolean isRefresherStarted ()
    {
        return refresherStarted;
    }

    /**
     * A quick access to the setSynchronizedPeriod() of the AEntityList
     * @param synchro The boolean parameter of the corresponding method
     * @see fr.esrf.tangoatk.core.AEntityList#setSynchronizedPeriod(boolean)
     */
    public void setSynchronizedPeriod(boolean synchro)
    {
        entities.setSynchronizedPeriod(synchro);
    }
}