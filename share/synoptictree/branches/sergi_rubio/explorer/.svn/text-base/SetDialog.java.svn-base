// File:          SetDialog.java
// Created:       2002-09-30 13:32:29, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-31 11:18:29, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JTextField;

import fr.esrf.tangoatk.core.AttributeSetException;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.IScalarAttribute;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.widget.attribute.NumberScalarWheelEditor;
import fr.esrf.tangoatk.widget.util.ButtonBar;
import fr.esrf.tangoatk.widget.util.HelpWindow;
import fr.esrf.tangoatk.widget.util.IApplicable;

/**
 * Class that manages the "set" dialog box for an attribute
 * 
 * @author Erik ASSUM
 */
public class SetDialog extends JDialog implements IApplicable {
    /** The <code>ButtonBar</code> for this window */
    ButtonBar bb;

    /** The textfield to set the value when attribute is a <code>String</code> */
    JTextField value;

    /** The label in the "set" dialog (exemple : "New Value") */
    JLabel label;

    /** The attribute to set */
    IScalarAttribute attribute;

    /** URL of associated help page */
    String helpUrl;

    /** The component with arrow buttons to redefine the attribute value */
    NumberScalarWheelEditor setter;

    /**
     * Class constructor, initializer.
     * 
     * @param model
     *            the attribute for which the set dialog is made
     */
    public SetDialog(IScalarAttribute model) {
        initComponents(model instanceof INumberScalar);
        setModel(model);
    }

    /**
     * Applies changes
     */
    public void apply() {
        if (attribute instanceof IStringScalar) {
            try {
                ((IStringScalar) attribute).setValue(value.getText());
            }
            catch (AttributeSetException e) {
                Main.status(getRootPane().getParent(), "Cannot set attribute "
                        + attribute.getName(), e);
            }
        }

    }

    /**
     * Closes window and applies changes
     */
    public void ok() {
        apply();
        cancel();
    }

    /**
     * Closes window
     */
    public void cancel() {
        getRootPane().getParent().setVisible(false);
    }

    /**
     * Initializes the components of the window
     * 
     * @param useWheel
     *            a boolean to know if <code>NumberScalarWheelEditor</code>
     *            can be used (attribute is a number) or not (attribute is a
     *            String)
     */
    protected void initComponents(boolean useWheel) {
        helpUrl = "/explorer/html/SetDialogHelp.html";

        bb = new ButtonBar();
        bb.setControlee(this);
        bb.setHelpUrl(getClass().getResource(helpUrl));
        if (useWheel) {
            setter = new NumberScalarWheelEditor();
        }
        else {
            value = new JTextField();
            value.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent evt) {
                    ok();
                }
            });
        }

        label = new JLabel("New value: ");

        getContentPane().setLayout(new GridBagLayout());

        GridBagConstraints c = new GridBagConstraints();
        c.fill = GridBagConstraints.HORIZONTAL;
        c.gridx = 0;
        c.gridy = 0;
        c.weightx = .5;
        c.insets = new Insets(11, 10, 0, 0);
        getContentPane().add(label, c);
        c.gridx = 1;
        c.insets = new Insets(10, 0, 0, 10);

        if (useWheel)
            getContentPane().add(setter, c);
        else
            getContentPane().add(value, c);

        c.insets = new Insets(0, 0, 0, 0);
        c.gridy = 1;
        c.gridx = 0;
        c.gridwidth = 2;
        getContentPane().add(bb, c);
        HelpWindow.getInstance().addCategory("Attribute Table", "Set dialog",
                getClass().getResource(helpUrl));
    }

    /**
     * Sets the global appearence of the window depending on the attribute
     * 
     * @param attribute
     *            the attribute on which the appearence will depend
     */
    public void setModel(IScalarAttribute attribute) {
        setTitle(attribute.getName());
        this.attribute = attribute;

        if (attribute instanceof INumberScalar) {
            INumberScalar scalar = (INumberScalar) attribute;
            setter.setModel(scalar);
        }
        else {
            IStringScalar scalar = (IStringScalar) attribute;
            value.setText(scalar.getStringValue());
        }
        pack();
    }

}