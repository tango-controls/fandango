package fr.esrf.tangoatk.widget.util.jdraw;

/** Interface implemented by JDObject that can be rotated */
public interface JDRotatable {
  /**
   * Rotates this object.
   * @param angle Angle value
   * @param xCenter Rotation center vertical pos
   * @param yCenter Rotation center horizontal pos
   */
  public void rotate(double angle,double xCenter,double yCenter);

}
