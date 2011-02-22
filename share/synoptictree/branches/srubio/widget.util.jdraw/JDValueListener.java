package fr.esrf.tangoatk.widget.util.jdraw;

/** An interface for receving JDValue events of a JDObject */
public interface JDValueListener {

  /** Trigerred when the JDObject value change */
  public void valueChanged(JDObject src);

  /** Trigerred when the JDObject value goes out of bounds and is reseted to its minimum value */
  public void valueExceedBounds(JDObject src);

}
