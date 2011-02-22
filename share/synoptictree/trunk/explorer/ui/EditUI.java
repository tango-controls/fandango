// File:          EditUI.java
// Created:       2002-09-19 11:08:38, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-16 14:37:21, erik>
// 
// $Id$
// 
// Description:       
package explorer.ui;

import java.awt.event.*;
import javax.swing.*;

/**
 * <code>EditUI</code> is responsible for setting up the view part of the
 * menu- and tool-bar. The "Clear attributes" and "Clear command" items are only
 * enabled when <code>isAdmin</code> is true.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class EditUI {
    Clearable attributeTable;

    Clearable commandTable;

    /**
     * Constructor
     * 
     * @param attributeTable
     *            the attribute table of the application
     * @param commandTable
     *            the command table of the application
     * @param toolbar
     *            not used
     * @param menubar
     *            the menu bar containing the "edit" menu
     * @param isAdmin
     *            to know wheather we are in admin mode or not
     */
    public EditUI(Clearable attributeTable, Clearable commandTable,
            JToolBar toolbar, DTMenuBar menubar, boolean isAdmin) {
        JMenuItem properties = new JMenuItem("Preferences...");
        JMenuItem clearAttributes = new JMenuItem("Clear attributes...");
        JMenuItem clearCommands = new JMenuItem("Clear commands...");
        this.attributeTable = attributeTable;
        this.commandTable = commandTable;

        properties.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                properties();
            }
        });

        clearAttributes.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                clearAttributes();
            }
        });

        clearCommands.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                clearCommands();
            }
        });

        properties.setIcon(new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Preferences16.gif")));

        properties.setAccelerator(KeyStroke.getKeyStroke('P',
                KeyEvent.CTRL_MASK));

        menubar.add2EditMenu(clearAttributes, 0);
        menubar.add2EditMenu(clearCommands, 1);
        clearAttributes.setEnabled(isAdmin);
        clearAttributes.setVisible(isAdmin);
        clearCommands.setEnabled(isAdmin);
        clearCommands.setVisible(isAdmin);
        menubar.add2EditMenu(properties, 2);
        PreferencesDialog.getInstance().addTop("Look and feel",
                UIDialog.getInstance());
    }

    /**
     * <code>properties</code> shows the preferences dialog
     *  
     */
    public void properties() {
        PreferencesDialog.getInstance().show();
    }

    /**
     * <code>clearAttributes</code> calls the <code>clear</code> of the
     * first clearable
     */
    public void clearAttributes() {
        if (JOptionPane.showConfirmDialog(null, "Do you really want to "
                + "clear the attribute table?", "Alert",
                JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION)
            attributeTable.clear();

    }

    /**
     * <code>clearCommands</code> calls the <code>clear</code> of the second
     * clearable
     *  
     */
    public void clearCommands() {
        if (JOptionPane.showConfirmDialog(null, "Do you really want to "
                + "clear the command table?", "Alert",
                JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION)
            commandTable.clear();
    }
}