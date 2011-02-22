// File:          DeviceAliasDialog.java
// Created:       2002-10-15 11:49:06, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-31 11:18:56, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import fr.esrf.tangoatk.widget.util.*;
import javax.swing.*;
import java.awt.event.*;

import fr.esrf.tangoatk.core.IDevice;

/**
 * Class for the "device alias" panel
 * 
 * @author Erik ASSUM
 */
public class DeviceAliasDialog extends JPanel implements IApplicable {
    /** Text field in which user will write the alias */
    JTextField field;

    /** The device source */
    IDevice device;

    /** The Entity table in which the alias is appliable */
    EntityTable table;

    /** The dialog box to set the alias */
    explorer.ui.Dialog dialog;

    /**
     * Class constructor, initializer. Builds a new panel that allows to make an
     * alias of a device
     * 
     * @param table
     *            the EntityTable in which the alias is appliable
     * @param device
     *            the device source for the alias
     */
    public DeviceAliasDialog(EntityTable table, IDevice device) {
        this.device = device;
        this.table = table;
        add(new JLabel("Enter alias for " + device.getName()));
        field = new JTextField();
        field.setColumns(20);
        field.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                ok();
            }
        });

        add(field);
        dialog = new explorer.ui.Dialog(this);
    }

    /**
     * Creates the alias of the device as defined by user in the panel
     */
    public void apply() {
        /*
         * device.setAlias(field.getText()); table.aliasChanged();
         */
    }

    /**
     * Closes device alias panel
     */
    public void cancel() {
        getRootPane().getParent().setVisible(false);
    }

    /**
     * Creates the alias and closes the panel
     */
    public void ok() {
        apply();
        cancel();
    }

    /**
     * Opens/shows the panel
     */
    public void show() {
        dialog.show();
    }
}