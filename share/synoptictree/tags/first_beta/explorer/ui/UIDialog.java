// File:          UIDialog.java
// Created:       2002-11-12 14:39:31, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2002-11-13 16:47:36, erik>
// 
// $Id$
// 
// Description:       
package explorer.ui;

import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import fr.esrf.tangoatk.widget.util.*;
import java.util.List;
import java.util.Vector;

/**
 * A panel to choose the gloabal aspect of the application (metal, etc...)
 * 
 * @author Erik Assum
 */
public class UIDialog extends JPanel implements IApplicable {
    String motiflf = "com.sun.java.swing.plaf.motif.MotifLookAndFeel";
    String metallf = "javax.swing.plaf.metal.MetalLookAndFeel";
    String windowslf = "com.sun.java.swing.plaf.windows.WindowsLookAndFeel";
    String chosen;
    List components;
    static UIDialog instance;

    /**
     * constructor
     */
    protected UIDialog() {
        initComponents();
    }

    /**
     * To get an instance of UIDialog
     */
    public static synchronized UIDialog getInstance() {
        if (instance == null)
            instance = new UIDialog();
        return instance;
    }

    /**
     * called by constructor
     */
    protected void initComponents() {
        ButtonGroup group = new ButtonGroup();
        JRadioButton metal = new JRadioButton("Metal");
        JRadioButton windows = new JRadioButton("Windows");
        JRadioButton motif = new JRadioButton("Motif");
        components = new Vector();

        group.add(metal);
        group.add(windows);
        group.add(motif);
        metal.setSelected(true);
        chosen = metallf;
        add(metal);
        add(windows);
        add(motif);
        motif.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                chosen = motiflf;
            }
        });
        metal.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                chosen = metallf;
            }
        });
        windows.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                chosen = windowslf;
            }
        });

    }

    /**
     * applies changes and closes the parent dialog of this panel
     */
    public void ok() {
        cancel();
        apply();
    }

    /**
     * closes the parent dialog of this panel
     */
    public void cancel() {
        getRootPane().getParent().setVisible(false);
    }

    /**
     * applies changes
     */
    public void apply() {
        try {
            UIManager.setLookAndFeel(chosen);
            SwingUtilities.updateComponentTreeUI(getRootPane().getParent());

            for (int i = 0; i < components.size(); i++) {
                Component component = (Component) components.get(i);
                SwingUtilities.updateComponentTreeUI(component);
            }
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Adds a component
     * 
     * @param c
     *            the component to add
     */
    public void addComponent(Component c) {
        components.add(c);
    }

    /**
     * Removes a component
     * @param c the component to remove
     */
    public void removeComponent(Component c) {
        components.remove(c);
    }

    public static void main(String[] args) {

        UIDialog dialog = new UIDialog();
        Dialog d = new Dialog(dialog);
        d.pack();
        d.show();

    }

}