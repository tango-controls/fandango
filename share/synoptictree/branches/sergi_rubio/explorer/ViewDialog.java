// File:          PropertySelector.java
// Created:       2002-09-12 14:44:21, erik
// By:            <erik@skiinfo.fr>
// Time-stamp:    <2003-01-16 13:19:37, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.util.List;
import java.util.Vector;

import javax.swing.JCheckBox;
import javax.swing.JPanel;

import fr.esrf.tangoatk.widget.util.HelpWindow;
import fr.esrf.tangoatk.widget.util.IApplicable;
import fr.esrf.tangoatk.widget.util.IHelpful;

/**
 * The panel that manages the preferences like the visible fields in table
 * 
 * @author SOLEIL
 */
public class ViewDialog extends JPanel implements IApplicable, IHelpful,
        ColumnListener {
    java.util.List checkBoxes = new Vector();

    EntityTableModel tableModel;

    String helpUrl = "/explorer/html/ViewDialogHelp.html";

    /**
     * Constructor
     * 
     * @param tableModel
     *            the EntityTableModel to which the view preferences must be set
     */
    public ViewDialog(EntityTableModel tableModel) {
        this.tableModel = tableModel;
        tableModel.addColumnListener(this);
        initComponents(tableModel);
    }

    public java.net.URL getHelpUrl() {
        return getClass().getResource(helpUrl);
    }

    /**
     * applies the view preferences
     */
    public void apply() {
        boolean[] visible = new boolean[checkBoxes.size()];
        String[] names = new String[checkBoxes.size()];
        for (int i = 0; i < checkBoxes.size(); i++) {
            JCheckBox tmp = (JCheckBox) checkBoxes.get(i);
            visible[i] = tmp.isSelected();
            names[i] = tmp.getText();
        }
        tableModel.setVisible(names, visible);
    }

    /**
     * closes the parent of this panel
     */
    public void cancel() {
        getRootPane().getParent().setVisible(false);
    }

    /**
     * Applies preferences and closes the parent of this panel
     */
    public void ok() {
        getRootPane().getParent().setVisible(false);
        apply();
    }

    /**
     * calls help window
     */
    public void help() {
        HelpWindow.getInstance().showUrl(getClass().getResource(helpUrl));
    }

    /**
     * Selects the checkboxes corresponding to the visible fields in table,
     * unselects the other ones
     */
    public void columnsChanged() {
        for (int i = 0; i < checkBoxes.size(); i++) {
            JCheckBox tmp = (JCheckBox) checkBoxes.get(i);
            tmp.setSelected(tableModel.isVisible(tmp.getText()));
        }
    }

    /**
     * called by constructor
     */
    protected void initComponents(EntityTableModel tableModel) {
        HelpWindow.getInstance().addCategory("Dialogs", "View dialog",
                getClass().getResource(helpUrl));
        List properties = tableModel.getAllColumnNames();

        setLayout(new GridBagLayout());
        GridBagConstraints constraints = new GridBagConstraints();

        constraints.gridx = 0;
        constraints.gridy = 0;
        constraints.fill = GridBagConstraints.HORIZONTAL;

        for (int i = 0; i < properties.size(); i++) {
            String name = (String) properties.get(i);
            if (name == AttributeTableModel.NAME
                    || name == CommandTableModel.COMMAND)
                continue;

            JCheckBox tmp = new JCheckBox(name, tableModel.isVisible(name));
            checkBoxes.add(tmp);
            add(tmp, constraints);
            constraints.gridy++;
            if (constraints.gridy == 4) {
                constraints.gridy = 0;
                constraints.gridx++;
            }

        }

        constraints.gridwidth = constraints.gridx + 1;
        constraints.gridy = 5;
        constraints.gridx = 0;
        constraints.weightx = 1;
    }

    public static void main(String[] args) {
        new ViewDialog(new AttributeTableModel(null, null)).show();
    }
}