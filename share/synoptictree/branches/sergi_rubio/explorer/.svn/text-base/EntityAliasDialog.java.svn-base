// File:          DeviceAliasDialog.java
// Created:       2002-10-15 11:49:06, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-31 11:18:33, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import fr.esrf.tangoatk.widget.util.*;
import java.awt.event.*;
import javax.swing.*;

import fr.esrf.tangoatk.core.IEntity;

/**
 * Class for the "entity (attribute/command) alias" panel
 * 
 * @author Erik ASSUM
 */
public class EntityAliasDialog extends JPanel implements IApplicable {
    /** Text field in which user will write the alias */
    JTextField field;

    /** The entity source */
    IEntity entity;

    /** The Entity table in which the alias is appliable */
    EntityTable table;

    /** The dialog box to set the alias */
    explorer.ui.Dialog dialog;

    /**
     * Class constructor, initializer. Builds a new panel that allows to make an
     * alias of an entity
     * 
     * @param table
     *            the EntityTable in which the alias is appliable
     * @param entity
     *            the entity source for the alias
     */
    public EntityAliasDialog(EntityTable table, IEntity entity) {
        this.entity = entity;
        this.table = table;
        add(new JLabel("Enter alias for " + entity.getName()));
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
     * Creates the alias of the entity as defined by user in the panel
     */
    public void apply() {
        entity.setAlias(field.getText());
        table.aliasChanged();
    }

    /**
     * Closes entity alias panel
     */
    public void cancel() {
        dialog.setVisible(false);
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