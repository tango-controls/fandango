// File:          Dialog.java
// Created:       2002-10-10 18:47:19, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-11-14 16:0:39, erik>
// 
// $Id$
// 
// Description:
package explorer.ui;

import javax.swing.*;
import java.awt.*;

import fr.esrf.tangoatk.widget.util.*;

/**
 * <code>Dialog</code> is a convenience class for constructing dialogs.
 * Basically it takes a component which implements the dialog ui, and adds a
 * fr.esrf.tangoatk.widget.util.ButtonBar to it.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class Dialog extends JDialog implements IControlee {
    ButtonBar bb;

    GridBagConstraints constraints;

    public Dialog() {
        initComponents();
    }

    /**
     * Creates a new <code>Dialog</code> instance.
     * 
     * @param component
     *            a <code>JComponent</code> value
     * @see #setComponent(JComponent component)
     */
    public Dialog(JComponent component) {
        initComponents();
        setComponent(component);
    }

    /**
     * Components initialization (used by constructor)
     */
    void initComponents() {
        constraints = new GridBagConstraints();
        getContentPane().setLayout(new GridBagLayout());
        bb = new ButtonBar();
        constraints.gridx = 0;
        constraints.gridy = 1;
        constraints.weightx = 1;

        constraints.fill = GridBagConstraints.BOTH;
        getContentPane().add(bb, constraints);
    }

    /**
     * <code>ok</code> is the default close method.
     *  
     */
    public void ok() {
        setVisible(false);
    }

    /**
     * <code>setComponent</code>
     * 
     * @param component
     *            a <code>JComponent</code> value. If the component implements
     *            the fr.esrf.tangoatk.widget.util.IControlee interface, it is
     *            set as the controlee of the buttonbar, if not this dialog is
     *            set as the controlee.
     */
    public void setComponent(JComponent component) {
        constraints.gridx = 0;
        constraints.gridy = 0;
        constraints.weighty = 1;
        constraints.weightx = 1;
        constraints.insets = new Insets(10, 10, 5, 10);

        if (component instanceof IControlee) {
            bb.setControlee((IControlee) component);
        } else {
            bb.setControlee(this);
        }

        getContentPane().add(component, constraints);
        pack();
    }
}