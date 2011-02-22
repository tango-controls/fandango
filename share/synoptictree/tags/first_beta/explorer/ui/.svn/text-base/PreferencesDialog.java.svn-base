// File:          PreferencesDialog.java
// Created:       2002-09-19 11:21:21, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 10:46:14, erik>
// 
// $Id$
// 
// Description:       
package explorer.ui;

import java.util.*;
import java.awt.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.tree.*;

import fr.esrf.tangoatk.widget.util.*;

/**
 * <code>PreferencesDialog</code> is a singleton class, since you normally
 * only need one of them in an application. Use <code>getInstance</code> to
 * get hold of it.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class PreferencesDialog extends JDialog implements IControlee {
    JTree tree;
    JSplitPane mainSplit;
    JScrollPane prefPanel;
    ButtonBar buttons;
    PreferenceNode top;
    Map categories;

    protected static PreferencesDialog instance;

    /**
     * constructor
     */
    protected PreferencesDialog() {
        initComponents();
    }

    /**
     * <code>getInstance</code> gets you an instance of the PreferenceDialog
     * 
     * @return a <code>PreferencesDialog</code> value
     */
    public static PreferencesDialog getInstance() {
        if (instance == null) {
            instance = new PreferencesDialog();
        }

        return instance;
    }

    /**
     * called by constructor
     */
    protected void initComponents() {
        top = new PreferenceNode();

        buttons = new ButtonBar();
        buttons.setControlee(this);
        tree = new JTree(top);
        //	tree.setRootVisible(false);
        categories = new HashMap();

        tree.getSelectionModel().setSelectionMode(
                TreeSelectionModel.SINGLE_TREE_SELECTION);
        DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();

        renderer.setLeafIcon(new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/icons/Properties16.gif")));
        tree.setCellRenderer(renderer);
        tree.addTreeSelectionListener(new TreeSelectionListener() {

            public void valueChanged(TreeSelectionEvent e) {

                DefaultMutableTreeNode n = (DefaultMutableTreeNode) tree
                        .getLastSelectedPathComponent();

                if (n == null || !(n instanceof PreferenceNode)) {
                    buttons.setControlee(PreferencesDialog.this);
                    return;
                }
                PreferenceNode node = (PreferenceNode) n;
                showPreference(node.getComponent());
            }
        });

        prefPanel = new JScrollPane();

        JScrollPane treeView = new JScrollPane(tree);
        mainSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, treeView,
                prefPanel);
        mainSplit.setDividerSize(9);
        mainSplit.setOneTouchExpandable(true);
        mainSplit.setDividerLocation(150);

        prefPanel.setPreferredSize(new Dimension(400, 300));
        treeView.setPreferredSize(new Dimension(150, 300));

        getContentPane().setLayout(new GridBagLayout());
        GridBagConstraints constraints = new GridBagConstraints();
        constraints.fill = GridBagConstraints.BOTH;
        constraints.weightx = 1;
        constraints.weighty = 1;
        constraints.gridx = 0;
        constraints.gridy = 0;
        constraints.insets = new java.awt.Insets(5, 10, 0, 10);
        getContentPane().add(mainSplit, constraints);
        constraints.gridy = 1;
        constraints.insets = new java.awt.Insets(0, 0, 0, 0);
        ;
        constraints.weighty = 0;
        getContentPane().add(buttons, constraints);

    }

    protected void showPreference(JComponent component) {
        JScrollPane pane = new JScrollPane(component);
        pane.setPreferredSize(new Dimension(400, 300));
        mainSplit.setRightComponent(pane);
        buttons.setControlee((IControlee) component);
        pack();
    }

    /**
     * <code>setTop</code> sets the top preference screen
     * 
     * @param name
     *            a <code>String</code> value The name shown in the tree
     * @param preferenceDialog
     *            a <code>JComponent</code> value containing the dialog.
     */
    public void setTop(String name, JComponent preferenceDialog) {
        top.setName(name);
        top.setComponent(preferenceDialog);
        showPreference(preferenceDialog);
    }

    /**
     * <code>addTop</code> adds a leaf to the top node
     * 
     * @param name
     *            a <code>String</code> value containing the name of the leaf
     * @param preferenceDialog
     *            a <code>JComponent</code> value
     */
    public void addTop(String name, JComponent preferenceDialog) {
        PreferenceNode node = null;
        node = new PreferenceNode(name, preferenceDialog);
        top.add(node);
        pack();
    }

    /**
     * <code>addCategory</code> adds a preference to the tree. If the category
     * is not already in the tree, the category is created.
     * 
     * @param category
     *            a <code>String</code> value
     * @param name
     *            a <code>String</code> value
     * @param preferenceDialog
     *            a <code>JComponent</code> value
     */
    public void addCategory(String category, String name,
            JComponent preferenceDialog) {
        Enumeration i = top.children();
        CategoryNode node = null;
        boolean found = false;

        while (i.hasMoreElements()) {
            DefaultMutableTreeNode n = (DefaultMutableTreeNode) i.nextElement();
            if (n instanceof PreferenceNode)
                continue;
            node = (CategoryNode) n;
            if (node.getCategory().equals(category)) {
                found = true;
                break;
            }
        }
        if (!found) {
            node = new CategoryNode(category, name, preferenceDialog);
            top.add(node);
        } else {
            node.add(name, preferenceDialog);
        }

    }

    public void ok() {
        getRootPane().getParent().setVisible(false);
    }

    public void show() {
        tree.expandRow(0);
        pack();
        super.show();
    }

    class CategoryNode extends DefaultMutableTreeNode {

        String category;

        public CategoryNode(String category, String name, JComponent comp) {
            this.category = category;
            add(name, comp);
        }

        public String getCategory() {
            return category;
        }

        public String toString() {
            return category;
        }

        public void add(String name, JComponent comp) {
            this.add(new PreferenceNode(name, comp));
        }
    }

    class PreferenceNode extends DefaultMutableTreeNode {
        String name;

        JComponent comp;

        public PreferenceNode() {

        }

        public PreferenceNode(String name, JComponent comp) {
            this.name = name;
            this.comp = comp;
        }

        public String toString() {
            return name;
        }

        public JComponent getComponent() {
            return comp;
        }

        public void setComponent(JComponent comp) {
            this.comp = comp;
        }

        public void setName(String name) {
            this.name = name;
        }
    }

}