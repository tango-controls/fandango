// File:          About.java
// Created:       2002-10-15 14:42:10, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-11-14 16:1:53, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import fr.esrf.tangoatk.widget.util.*;
import javax.swing.*;
import java.awt.*;

/**
 * class called to show/hide the "about" window
 * 
 * @author Erik ASSUM
 */
public class About extends JEditorPane implements IControlee {
    /** The visible window */
    explorer.ui.Dialog dialog;

    /**
     * class constructor, initializer
     */
    public About() {
        setEditable(false);
        try {
            setPage(getClass().getResource("/explorer/html/about.html"));
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        setPreferredSize(new Dimension(300, 200));
        dialog = new explorer.ui.Dialog(new JScrollPane(this));
        dialog.pack();
    }

    /**
     * Hides the "about" window <br>
     * You can call this fonction when user clicks on the [x] or [cancel] button
     * of the "about" window
     */
    public void cancel() {
        dialog.setVisible(false);
    }

    /**
     * Hides the "about" window <br>
     * You can call this fonction when user clicks on the [ok] button of the
     * "about" window
     */
    public void ok() {
        cancel();
    }

    /**
     * Shows the "about" window
     */
    public void show() {
        dialog.pack();
        dialog.show();
    }

}