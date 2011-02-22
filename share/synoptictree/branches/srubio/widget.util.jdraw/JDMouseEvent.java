package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.event.MouseEvent;
import java.util.EventObject;

/** JDraw MouseEvent */
public class JDMouseEvent extends EventObject {

  private MouseEvent realSource;

  /**
   * Construct a JDMouseEvent
   * @param source JDObject source
   * @param e0 Initial mouse event.
   */
  public JDMouseEvent(JDObject source,MouseEvent e0) {

    super(source);
    realSource = e0;

  }
  /**
   * Returns the horizontal x position of the intial MouseEvent.
   */
  public int getX() {
      return realSource.getX();
  }

  /**
   * Returns the vetical y position of the intial MouseEvent.
   */
  public int getY() {
    return realSource.getY();
  }

  /**
   * Indicates the number of quick consecutive clicks of
   * a mouse button.
   */
  public int getClickCount() {
    return realSource.getClickCount();
  }

  /**
   * Returns which, if any, of the mouse buttons has changed state.
   * @see MouseEvent#BUTTON1
   * @see MouseEvent#BUTTON2
   * @see MouseEvent#BUTTON3
   */
  public int getButton() {
    return realSource.getButton();
  }

  /**
   * Returns the timestamp of when this event occurred.
   */
  public long getWhen() {
    return realSource.getWhen();
  }

  /**
   * Returns whether or not the Shift modifier is down on this event.
   */
  public boolean isShiftDown() {
    return realSource.isShiftDown();
  }

  /**
   * Returns whether or not the Control modifier is down on this event.
   */
  public boolean isControlDown() {
    return realSource.isControlDown();
  }

  /**
   * Returns whether or not the Meta modifier is down on this event.
   */
  public boolean isMetaDown() {
    return realSource.isMetaDown();
  }

  /**
   * Returns whether or not the Alt modifier is down on this event.
   */
  public boolean isAltDown() {
      return realSource.isAltDown();
  }

  /**
   * Returns whether or not the AltGraph modifier is down on this event.
   */
  public boolean isAltGraphDown() {
      return realSource.isAltGraphDown();
  }

  /**
   * Returns the modifier mask for this event.
   */
  public int getModifiers() {
      return realSource.getModifiers();
  }

  /**
   * Returns the original id for this event (MouseEvent.MOUSE_/PRESSED/ENTERED/...).
   */
  public int getID() {
      return realSource.getID();
  }

  /**
   * Returns the original source for this event.
   */
  public MouseEvent getSourceEvent() {
      return realSource;
  }

}
