// File:          CommandTableAdapter.java
// Created:       2002-09-13 13:17:17, erik
// By:            <erik@skiinfo.fr>
// Time-stamp:    <2003-01-30 11:19:23, erik>
// 
// $Id$
// 
// Description:       
package explorer;

import java.util.ArrayList;

import javax.swing.JComponent;

import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.IStateListener;
import fr.esrf.tangoatk.core.StateEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;

/**
 * <code>CommandTableModel</code> implements parts of the table model needed
 * by CommandTable
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class CommandTableModel extends EntityTableModel {
    public final static String COMMAND = "Command";

    /**
     * Class constructor, initializer, with possibility to set status and
     * preferences.
     * 
     * @param status
     *            the status
     * @param preferences
     *            the preferences
     */
    public CommandTableModel(Status status, Preferences preferences) {
        this.status = status;
        entities = new fr.esrf.tangoatk.core.CommandList();
        adapters = new ArrayList();
        columnIdentifiers = new ArrayList();
        this.preferences = preferences;
    }

    /**
     * Columns initialization. Sets the columns titles
     */
    protected void initColumns() {
        columnIdentifiers.add(DEVICE);
        columnIdentifiers.add(COMMAND);
        columnNames = new ArrayList(columnIdentifiers);
        fireTableStructureChanged();
    }

    /**
     * Gives a prefix representing the name of the command table. You might need
     * this to reorganize the table (like adding/removing a column)
     * 
     * @return the <code>StringBuffer</code> containing the prefix
     */
    protected StringBuffer getPreferencePrefix() {
        return new StringBuffer("CommandTable.");
    }

    /**
     * Returns the value to put in the specified row and column
     * 
     * @param row
     *            the row index
     * @param column
     *            the column index
     * @return the corresponding value, <code>"UGLE"</code> when no value can
     *         correspond with the specified row and column
     */
    public Object getValueAt(int row, int column) {
        Object o = adapters.get(row);
        ICommand command = ((CommandAdapter) o).getCommand();

        String header = getColumnName(column);
        if (DEVICE == header)
            return getDeviceAlias(command.getDevice());
        if (COMMAND == header)
            return getEntityAlias(command);

        return "UGLE";
    }

    /**
     * Adds a command in the command table
     * 
     * @param name
     *            the name of the command to add
     */
    protected void addCommand(String name) {
        try {
            load(name, null, null);
        }
        catch (ConnectionException e) {
            status.status("Cannot load command " + name, e);
        }
    }

    public void load(String name, String alias, String deviceAlias)
            throws ConnectionException {

        ICommand command = (ICommand) entities.add(name);
        if (alias != null)
            command.setAlias(alias);
        //	if (deviceAlias != null) command.getDevice().setAlias(deviceAlias);

        addCommand(command);
    }

    /**
     * Adds a command in the table. Uses <code>addCommand(...)</code>
     * 
     * @param command
     *            the command to add
     */
    public void addEntity(IEntity command) {
        entities.add(command);
        if (deviceList != null)
        {
            deviceList.add(command.getDevice());
        }
        addCommand((ICommand) command);
    }

    /**
     * Adds a command in the table if it is not already present.
     * 
     * @param command
     *            the command to add
     */
    public void addCommand(ICommand command) {

        if (exists(command))
            return;
        if (deviceList != null)
        {
            deviceList.add(command.getDevice());
        }
        adapters.add(new CommandAdapter(command, adapters.size()));
        fireTableRowsInserted(adapters.size(), adapters.size());
    }

    /**
     * Method that returns a boolean representing if the specified column is the
     * "Command" column or not
     * 
     * @param i
     *            the column index
     * @return <code>true</code> if the corresponding column is the "Command"
     *         column, <code>false</code> otherwise
     */
    protected boolean isExecuteColumn(int i) {
        if (i == -1)
            return false;

        return columnModel.getColumn(i).getHeaderValue() == COMMAND;
    }

    /**
     * A listener for the commands in table
     * 
     * @author Erik ASSUM
     */
    class CommandAdapter implements IStateListener, EntityAdapter {
        int row;

        ICommand command;

        /**
         * returns the <code>IEntity</code> representation of the command
         */
        public IEntity getEntity() {
            return command;
        }

        /**
         * Refreshes the properties of this command
         */
        public void reloadProperties() {
            fireTableRowsUpdated(row, row);
        }

        /**
         * Class constructor, initializer. Associates the listener with a
         * command and a row in the table
         * 
         * @param command
         *            the command
         * @param row
         *            the row index
         */
        public CommandAdapter(ICommand command, int row) {
            this.row = row;
            this.command = command;
            command.getDevice().addStateListener(this);
        }

        /**
         * useless method (empty)
         * 
         * @param evt
         *            unused
         */
        public void errorChange(ErrorEvent evt) {
            /* RG comment : TODO - what was it for ? */
        }

        /**
         * Changes the state of this listener according a
         * <code>StateEvent</code>
         * 
         * @param evt
         *            the <code>StateEvent</code>
         */
        public void stateChange(StateEvent evt) {
            JComponent r = getDeviceRenderer(getDeviceAlias(command.getDevice()));
            if (r == null)
                return;

            r.setBackground(ATKConstant.getColor4State(evt.getState()));
            r.setToolTipText(evt.getState());
            fireTableRowsUpdated(row, row);
        }

        /**
         * returns the <code>ICommand</code> representation of the command
         */
        public ICommand getCommand() {
            return command;
        }

        /**
         * Method to remove listener from the associated command.
         * Called when removing a command from table
         */
        public void remove() {
            command.getDevice().removeStateListener(this);
        }
    }
}