// File:          UIBit.java
// Created:       2002-09-18 14:08:47, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-11-12 14:38:6, erik>
// 
// $Id$
// 
// Description:       

package explorer.ui;

import java.awt.Insets;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JMenuItem;
import javax.swing.KeyStroke;

/**
 * <code>UIBit</code> is a convenience class for creating menus and buttons.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class UIBit {
    JMenuItem item;
    JButton button;
    ImageIcon icon;
    String tip;

    /**
     * Creates a new <code>UIBit</code> instance.
     * 
     * @param name
     *            the text on the menu item.
     * @param tip
     *            the text in the tooltip
     * @param listener
     *            the code to be executed when the bit is chosen
     * @param icon
     *            the icon for this bit.
     */
    public UIBit(String name, String tip, ActionListener listener, Icon icon) {
        item = new JMenuItem(name);
        button = new JButton();
        button.setMargin(new Insets(5,5,5,5));

        if (icon != null) {
            item.setIcon(icon);
            button.setIcon(icon);
        }

        button.setToolTipText(tip);

        item.addActionListener(listener);
        button.addActionListener(listener);
    }

    /**
     * Creates a new <code>UIBit</code> instance where the name of the menu
     * item and the tool-tip of the toolbar button are the same.
     * 
     * @param name
     *            the text of the menu item and the tooltip
     * @param listener
     *            the object holding the action to be performed on a click
     * @param icon
     *            the icon for this bit
     */
    public UIBit(String name, ActionListener listener, Icon icon) {
        this(name, name, listener, icon);
    }

    /**
     * Creates a new <code>UIBit</code> without icons
     * 
     * @param name
     *            the text of the menu item and the tooltip
     * @param listener
     *            the object holding the action to be performed on a click
     */
    public UIBit(String name, ActionListener listener) {
        this(name, name, listener, null);
    }

    /**
     * <code>setAccelerator</code> Sets the accelerator for the menu-item of
     * this uibit. The accelerator is used with the control-key
     * 
     * @param key
     *            a <code>char</code> value
     */
    public void setAccelerator(char key) {
        item.setAccelerator(KeyStroke.getKeyStroke(key, KeyEvent.CTRL_MASK));
    }

    /**
     * sets the key control associated to this item
     * 
     * @param key
     *            the key to call tis item
     */
    public void setAccelerator(String key) {
        item.setAccelerator(KeyStroke.getKeyStroke(key));
    }

    /**
     * @return the <code>JMenuItem</code> representation of this element
     */
    public JMenuItem getItem() {
        return item;
    }

    /**
     * @return the <code>JButton</code> representation of this element
     */
    public JButton getButton() {
        return button;
    }

    /**
     * to know wheather this element is enabled or not
     * 
     * @return a <code>boolean</code> value
     */
    public boolean isEnabled() {
        return item.isEnabled();
    }

    /**
     * <code>setEnabled</code> enables the menu-item and the button.
     * 
     * @param b
     *            a <code>boolean</code> value
     */
    public void setEnabled(boolean b) {
        item.setEnabled(b);
        button.setEnabled(b);
    }

    /**
     * to know wheather this element is visible or not
     * 
     * @return a <code>boolean</code> value
     */
    public boolean isVisible() {
        return item.isVisible();
    }

    /**
     * <code>setVisible</code> sets visible the menu-item and the button.
     * 
     * @param b
     *            a <code>boolean</code> value
     */
    public void setVisible(boolean b) {
        item.setVisible(b);
        button.setVisible(b);
    }
}