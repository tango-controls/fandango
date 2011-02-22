package fr.esrf.tangoatk.widget.util.jdraw;

import java.util.EventListener;

/**
 * The listener interface for receiving "interesting" mouse events
 * (press, release, click, enter, and exit) on a JDObject.
 */
public interface JDMouseListener extends EventListener {

    /**
     * Invoked when the mouse button has been clicked (pressed
     * and released) on a JDObject.
     */
    public void mouseClicked(JDMouseEvent e);

    /**
     * Invoked when a mouse button has been pressed on a JDObject.
     */
    public void mousePressed(JDMouseEvent e);

    /**
     * Invoked when a mouse button has been released on a JDObject.
     */
    public void mouseReleased(JDMouseEvent e);

    /**
     * Invoked when the mouse enters a JDObject.
     */
    public void mouseEntered(JDMouseEvent e);

    /**
     * Invoked when the mouse exits a JDObject.
     */
    public void mouseExited(JDMouseEvent e);
}
