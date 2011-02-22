/*	Synchrotron Soleil 
 *  
 *   File          :  DTMenuBar.java
 *  
 *   Project       :  devicetree
 *  
 *   Description   :  
 *  
 *   Author        :  SOLEIL
 *  
 *   Original      :  2 août 2005 
 *  
 *   Revision:  					Author:  
 *   Date: 							State:  
 *  
 *   Log: DTMenuBar.java,v 
 *
 */

package explorer.ui;

import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JSeparator;
import javax.swing.KeyStroke;
import fr.esrf.tangoatk.widget.util.ErrorHistory;
import fr.esrf.tangoatk.widget.util.HelpWindow;

/**
 * A Menu Bar for Device Tree
 * @author SOLEIL
 */
public class DTMenuBar extends JMenuBar {

    JMenu file;
    JMenu view;
    JMenu edit;
    JMenu help;
    JMenu refresh;
    JMenuItem exitItem;
    JMenuItem aboutItem;
    JMenuItem errorItem;
    JMenuItem helpItem;
    GridBagConstraints constraints;
    ErrorHistory errorHistory;

    /**
     * Constructs the Menu Bar and associates an ErrorHistory
     * @param errorHistory the ErrorHistory
     */
    public DTMenuBar(ErrorHistory errorHistory) {
        this();
        setErrorHistory(errorHistory);
        setMargin(new Insets(2,2,2,2));
    }

    /**
     * Sets the <code>ErrorHistory</code> so that this bar can report errors
     * @param errorHistory 21 sept. 2005
     */
    public void setErrorHistory(ErrorHistory errorHistory) {
        this.errorHistory = errorHistory;
    }

    /**
     * @return the <code>ErrorHistory</code> associated with this menu bar
     */
    public ErrorHistory getErrorHistory() {
        return errorHistory;
    }

    /**
     * shows the <code>ErrorHistory</code> associated with this menu bar
     */
    protected void showErrorHistory() {
        if (errorHistory == null)
            return;
        errorHistory.show();
    }

    /**
     * shows the help window
     */
    protected void showHelpWindow() {
        HelpWindow.getInstance().show();
    }

    /**
     * constructor
     */
    public DTMenuBar() {
        constraints = new GridBagConstraints();
        constraints.gridx = 0;
        setLayout(new GridBagLayout());

        add(file = new JMenu("File"), constraints);
        constraints.gridx++;
        add(edit = new JMenu("Edit"), constraints);
        constraints.gridx++;
        add(view = new JMenu("View"), constraints);
        constraints.gridx++;
        add(refresh = new JMenu("Refresh"), constraints);

        constraints.fill = GridBagConstraints.HORIZONTAL;
        constraints.weightx = 0.1;
        constraints.gridx = 200;
        add(new JLabel(""), constraints);
        constraints.fill = GridBagConstraints.NONE;
        constraints.gridx = 201;
        constraints.weightx = 0;
        add(help = new JMenu("Help"), constraints);
        constraints.gridx = 3;

        exitItem = new JMenuItem("Quit");
        aboutItem = new JMenuItem("About...");
        helpItem = new JMenuItem("Help");

        file.setMnemonic('F');
        view.setMnemonic('V');
        edit.setMnemonic('E');
        help.setMnemonic('H');

        exitItem.setAccelerator(KeyStroke.getKeyStroke('Q', KeyEvent.CTRL_MASK));
        helpItem.setAccelerator(KeyStroke.getKeyStroke("F1"));
        helpItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showHelpWindow();
            }
        });

        errorItem = new JMenuItem("Error history...");
        errorItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showErrorHistory();
            }
        });
        errorItem.setAccelerator(KeyStroke.getKeyStroke('E', KeyEvent.CTRL_MASK));
        add2ViewMenu(errorItem, 0);

        file.add(new JSeparator());
        file.add(exitItem);

        help.add(aboutItem);
        help.add(helpItem);
    }

    /**
     * Sets the font of the text of this bar
     */
    public void setFont(Font f) {
        super.setFont(f);
        if (file == null)
            return;

        file.setFont(f);
        view.setFont(f);
        edit.setFont(f);
        help.setFont(f);
        exitItem.setFont(f);
        errorItem.setFont(f);
        aboutItem.setFont(f);
        helpItem.setFont(f);
    }

    /**
     * Adds a listener to the "quit" item in file menu
     * @param listener the listener
     */
    public void setQuitHandler(ActionListener listener) {
        exitItem.addActionListener(listener);
    }

    /**
     * Adds a listener to the "about" item in help menu
     * @param listener the listener
     */
    public void setAboutHandler(ActionListener listener) {
        aboutItem.addActionListener(listener);
    }

    /**
     * adds an element in "view" menu at the specified position
     * @param item the element to add
     * @param i the position
     */
    public void add2ViewMenu(JComponent item, int i) {
        item.setFont(getFont());
        view.add(item, i);
    }

    /**
     * adds an element in "view" menu
     * @param item the element to add
     */
    public void add2ViewMenu(JComponent item) {
        item.setFont(getFont());
        view.add(item);
    }

    /**
     * adds an element in "edit" menu at the specified position
     * @param item the element to add
     * @param i the position
     */
    public void add2EditMenu(JComponent item, int i) {
        item.setFont(getFont());
        edit.add(item, i);
    }

    /**
     * adds an element in "edit" menu
     * @param item the element to add
     */
    public void add2EditMenu(JComponent item) {
        item.setFont(getFont());
        edit.add(item);
    }

    /**
     * adds an element in "help" menu at the specified position
     * @param item the element to add
     * @param i the position
     */
    public void add2HelpMenu(JComponent item, int i) {
        item.setFont(getFont());
        help.add(item, i);
    }

    /**
     * adds an element in "help" menu
     * @param item the element to add
     */
    public void add2HelpMenu(JComponent item) {
        item.setFont(getFont());
        help.add(item);
    }

    /**
     * adds an element in "file" menu at the specified position
     * @param item the element to add
     * @param i the position
     */
    public void add2FileMenu(JComponent item, int i) {
        item.setFont(getFont());
        file.add(item, i);
    }

    /**
     * adds an element in "file" menu
     * @param item the element to add
     */
    public void add2FileMenu(JComponent item) {
        item.setFont(getFont());
        file.add(item);
    }

    /**
     * adds an element in "refresh" menu at the specified position
     * @param item the element to add
     * @param i the position
     */
    public void add2RefreshMenu(JComponent item, int i) {
        item.setFont(getFont());
        refresh.add(item, i);
    }

    /**
     * adds an element in "refresh" menu
     * @param item the element to add
     */
    public void add2RefreshMenu(JComponent item) {
        item.setFont(getFont());
        refresh.add(item);
    }

    /**
     * Adds a menu in bar
     * @param menu the menu to add
     */
    public void addMenu(JMenu menu) {
        constraints.gridx++;
        menu.setFont(getFont());
        add(menu, constraints);
    }

}