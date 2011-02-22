package fr.esrf.tangoatk.widget.util.jdraw;

/**
 * An abstract adapter class for receiving mouse events.
 * The methods in this class are empty. This class exists as
 * convenience for creating listener objects.
 */
public abstract class JDMouseAdapter implements JDMouseListener {
    /**
     * Invoked when the mouse has been clicked on a JDObject.
     */
    public void mouseClicked(JDMouseEvent e) {}

    /**
     * Invoked when a mouse button has been pressed on a JDObject.
     */
    public void mousePressed(JDMouseEvent e) {}

    /**
     * Invoked when a mouse button has been released on a JDObject.
     */
    public void mouseReleased(JDMouseEvent e) {}

    /**
     * Invoked when the mouse enters a JDObject.
     */
    public void mouseEntered(JDMouseEvent e) {}

    /**
     * Invoked when the mouse exits a JDObject.
     */
    public void mouseExited(JDMouseEvent e) {}
}
