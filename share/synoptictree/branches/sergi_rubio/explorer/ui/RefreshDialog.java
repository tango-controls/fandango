// File:          RefreshDialog.java
// Created:       2002-09-23 15:37:12, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-11-12 14:48:20, erik>
// 
// $Id$
// 
// Description:
package explorer.ui;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

import javax.swing.InputVerifier;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.PlainDocument;

import fr.esrf.tangoatk.widget.util.HelpWindow;
import fr.esrf.tangoatk.widget.util.IApplicable;
import fr.esrf.tangoatk.widget.util.IHelpful;

/**
 * The Panel of the dialog to set the refreshing period
 * 
 * @author Erik Assum
 */
class RefreshDialog extends JPanel implements IApplicable, IHelpful {

    JTextField value;
    InputVerifier fmt;
    JLabel label;
    RefreshUI ui;
    String helpUrl = "/explorer/html/RefreshDialogHelp.html";

    /**
     * Constructor
     * 
     * @param ui
     *            the RefreshUI that calls this dialog
     */
    RefreshDialog(RefreshUI ui) {
        super();
        this.ui = ui;
        initComponents();
    }

    /**
     * called by constructor
     */
    protected void initComponents() {

        value = new JTextField();
        value.setDocument(new PlainDocument() {
            public void insertString(int offs, String str, AttributeSet a)
                    throws BadLocationException {
                for (int i = 0; i < str.length(); i++)
                    if (!(Character.isDigit(str.charAt(i))))
                        return;
                super.insertString(offs, str, a);
            }
        });

        value.setText(Integer.toString(ui.getRefreshInterval()));
        label = new JLabel("Refresh interval: ");
        setLayout(new GridBagLayout());
        GridBagConstraints c = new GridBagConstraints();
        c.fill = GridBagConstraints.HORIZONTAL;
        c.insets = new java.awt.Insets(10, 10, 0, 0);
        c.gridx = 0;
        c.gridy = 0;
        c.weightx = .5;
        add(label, c);
        c.insets = new java.awt.Insets(10, 0, 0, 10);
        c.gridx = 1;
        add(value, c);
        HelpWindow.getInstance().addCategory("Dialogs", "Refresh dialog",
                getClass().getResource(helpUrl));

    }

    /**
     * applies the refreshing period and hides the parent dialog
     */
    public void ok() {
        cancel();
        apply();
    }

    /**
     * hides the parent dialog
     */
    public void cancel() {
        getRootPane().getParent().setVisible(false);
    }

    /**
     * applies the refreshing period
     */
    public void apply() {
        ui.setRefreshInterval(Integer.parseInt(value.getText()));
    }

    /**
     * returns the url of the help window
     */
    public java.net.URL getHelpUrl() {
        return getClass().getResource(helpUrl);
    }
}