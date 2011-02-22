package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.geom.Point2D;
import java.awt.*;
import java.io.IOException;
import java.io.FileWriter;

/** JDraw Bar graphic object.
 */
public class JDBar extends JDRectangular {

  /** Horizontal bar , min at feft */
  public final static int BAR_HORIZONTAL_LEFT  = 0;
  /** Horizontal bar , min at right */
  public final static int BAR_HORIZONTAL_RIGHT = 1;
  /** Vertical bar , min at top */
  public final static int BAR_VERTICAL_TOP = 2;
  /** Vertical bar , min at bottom */
  public final static int BAR_VERTICAL_BOTTOM = 3;

  // Default Properties
  static final double minDefault             = 0.0;
  static final double maxDefault             = 1.0;
  static final double valueDefault           = 1.0;
  static final boolean outLineVisibleDefault = true;
  static final int orientationDefault        = BAR_VERTICAL_BOTTOM;

  // Vars
  double  min;
  double  max;
  double  value;
  boolean outLineVisible;
  int     orientation;

  /**
   * Contructs a JDBar.
   * @param objectName Object name
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   * @param w Rectangle width
   * @param h Rectangle height
   *
   */
  public JDBar(String objectName, int x, int y, int w, int h) {
    initDefault();
    setOrigin(new Point2D.Double(x, y));
    summit = new Point2D.Double[8];
    name = objectName;
    createSummit();
    computeSummitCoordinates(x, y, w, h);
    updateShape();
  }

  JDBar(JDBar e,int x,int y) {
    cloneObject(e,x,y);
    min = e.min;
    max = e.max;
    value = e.value;
    outLineVisible = e.outLineVisible;
    orientation = e.orientation;
    updateShape();
  }

  JDBar(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if( propName.equals("minBar") ) {
        min = f.parseDouble();
      } else if( propName.equals("maxBar") ) {
        max = f.parseDouble();
      } else if( propName.equals("valueBar") ) {
        value = f.parseDouble();
      } else if( propName.equals("outLineVisible") ) {
        outLineVisible = f.parseBoolean();
      } else if( propName.equals("orientation") ) {
        orientation = (int)f.parseDouble();
      } else
        loadDefaultPropery(f, propName);
    }

    f.endBlock();
    updateShape();
  }

  public JDObject copy(int x,int y) {
    return new JDBar(this,x,y);
  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  void initDefault() {
    super.initDefault();
    fillStyle = JDObject.FILL_STYLE_SOLID;
    min = minDefault;
    max = maxDefault;
    value = valueDefault;
    outLineVisible = outLineVisibleDefault;
    orientation = orientationDefault;
  }

  public boolean isInsideObject(int x, int y) {
    if(!super.isInsideObject(x,y)) return false;

    if (fillStyle != FILL_STYLE_NONE)
      return boundRect.contains(x, y);
    else {
      int x1 = boundRect.x;
      int x2 = boundRect.x + boundRect.width;
      int y1 = boundRect.y;
      int y2 = boundRect.y + boundRect.height;

      return isPointOnLine(x, y, x1, y1, x2, y1) ||
          isPointOnLine(x, y, x2, y1, x2, y2) ||
          isPointOnLine(x, y, x2, y2, x1, y2) ||
          isPointOnLine(x, y, x1, y2, x1, y1);
    }
  }

  void updateShape() {

    computeBoundRect();
    ptsx = new int[4];
    ptsy = new int[4];

    if (!Double.isNaN(value)) {

      double ratio = 0.0;
      if (min != max) ratio = (value - min) / (max - min);
      if (ratio < 0.0) ratio = 0.0;
      if (ratio > 1.0) ratio = 1.0;

      // Compute bar posision
      switch (orientation) {

        case BAR_HORIZONTAL_LEFT:
          {
            int nWidth = (int) ((double) (boundRect.width - 1) * ratio + 0.5);
            if (nWidth < 0) nWidth = 0;
            ptsx[0] = boundRect.x;
            ptsy[0] = boundRect.y;
            ptsx[1] = boundRect.x + nWidth;
            ptsy[1] = boundRect.y;
            ptsx[2] = boundRect.x + nWidth;
            ptsy[2] = boundRect.y + boundRect.height - 1;
            ptsx[3] = boundRect.x;
            ptsy[3] = boundRect.y + boundRect.height - 1;
          }
          break;

        case BAR_HORIZONTAL_RIGHT:
          {
            int nWidth = (int) ((double) (boundRect.width - 1) * (1.0 - ratio) + 0.5);
            if (nWidth < 0) nWidth = 0;
            ptsx[0] = boundRect.x + nWidth;
            ptsy[0] = boundRect.y;
            ptsx[1] = boundRect.x + boundRect.width - 1;
            ptsy[1] = boundRect.y;
            ptsx[2] = boundRect.x + boundRect.width - 1;
            ptsy[2] = boundRect.y + boundRect.height - 1;
            ptsx[3] = boundRect.x + nWidth;
            ptsy[3] = boundRect.y + boundRect.height - 1;
          }
          break;

        case BAR_VERTICAL_TOP:
          {
            int nHeight = (int) ((double) (boundRect.height - 1) * ratio + 0.5);
            if (nHeight < 0) nHeight = 0;
            ptsx[0] = boundRect.x;
            ptsy[0] = boundRect.y;
            ptsx[1] = boundRect.x + boundRect.width - 1;
            ptsy[1] = boundRect.y;
            ptsx[2] = boundRect.x + boundRect.width - 1;
            ptsy[2] = boundRect.y + nHeight;
            ptsx[3] = boundRect.x;
            ptsy[3] = boundRect.y + nHeight;
          }
          break;

        case BAR_VERTICAL_BOTTOM:
          {
            int nHeight = (int) ((double) (boundRect.height - 1) * (1.0 - ratio) + 0.5);
            if (nHeight < 0) nHeight = 0;
            ptsx[0] = boundRect.x;
            ptsy[0] = boundRect.y + nHeight;
            ptsx[1] = boundRect.x + boundRect.width - 1;
            ptsy[1] = boundRect.y + nHeight;
            ptsx[2] = boundRect.x + boundRect.width - 1;
            ptsy[2] = boundRect.y + boundRect.height - 1;
            ptsx[3] = boundRect.x;
            ptsy[3] = boundRect.y + boundRect.height - 1;
          }
          break;

      }

      // Update shadow coordinates
      if (hasShadow()) {
        computeShadow(true);
        computeShadowColors();
      }

    }
    
  }

  public void paint(JDrawEditor parent,Graphics g) {

    if(!visible) return;
    if (Double.isNaN(value)) return;
    prepareRendering((Graphics2D) g);

    super.paint(parent,g);

    if(outLineVisible) {
      g.setColor(foreground);
      int x1 = (int)(summit[0].x+0.5);
      int y1 = (int)(summit[0].y+0.5);
      int x2 = (int)(summit[4].x+0.5);
      int y2 = (int)(summit[4].y+0.5);
      g.drawLine(x1,y1,x2,y1);
      g.drawLine(x2,y1,x2,y2);
      g.drawLine(x2,y2,x1,y2);
      g.drawLine(x1,y2,x1,y1);
    }

  }

  // -----------------------------------------------------------
  // Property
  // -----------------------------------------------------------
  /**
   * Sets the progress bar's maximum value . It is used to handle
   * the bar position calculation.
   * @param m Maximum value
   */
  public void setMaximum(double m) {
    max = m;
    updateShape();
  }

  /**
   * Returns the progress bar's maximum value.
   * @see #setMaximum
   */
  public double getMaximum() {
    return max;
  }

  /**
   * Sets the progress bar's minimum value . It is used to handle
   * the bar position calculation.
   * @param m Miniimum value
   */
  public void setMinimum(double m) {
    min = m;
    updateShape();
  }

  /**
   * Returns the progress bar's maximum value.
   * @see #setMinimum
   */
  public double getMinimum() {
    return min;
  }

  /**
   * Sets the bar value.
   * @param v Bar value.
   */
  public void setBarValue(double v) {
    value = v;
    updateShape();
  }

  /**
   * Returns the current bar value.
   */
  public double getBarValue() {
    return value;
  }

  /**
   * Displays or hides the outline of the bar.
   * @param visible True to display the outline false otherwize.
   */
  public void setOutLineVisible(boolean visible) {
    outLineVisible = visible;
  }

  /**
   * Determines whether the outline is visible.
   */
  public boolean isOutLineVisible() {
    return outLineVisible;
  }

  /**
   * Sets the bar orientation.
   * @param o Orientation value
   * @see #BAR_HORIZONTAL_LEFT
   * @see #BAR_HORIZONTAL_RIGHT
   * @see #BAR_VERTICAL_TOP
   * @see #BAR_VERTICAL_BOTTOM
   */
  public void setOrientation(int o) {
    orientation = o;
    updateShape();
  }

  /**
   * Returns the current bar orientation.
   * @see #setOrientation
   */
  public int getOrientation() {
    return orientation;
  }

  // -----------------------------------------------------------
  // Configuration management
  // -----------------------------------------------------------
  void saveObject(FileWriter f,int level) throws IOException {

    String decal = saveObjectHeader(f,level);

    if(min!=minDefault) {
      String to_write = decal + "minBar:" + min + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(max!=maxDefault) {
      String to_write = decal + "maxBar:" + max + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(value!=valueDefault) {
      String to_write = decal + "valueBar:" + value + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(orientation!=orientationDefault) {
      String to_write = decal + "orientation:" + orientation + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (outLineVisible != outLineVisibleDefault) {
      String to_write = decal + "outLineVisible:" + outLineVisible + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f,level);

  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDBar);
    fillUndoPattern(u);
    u.min = min;
    u.max = max;
    u.value = value;
    u.isClosed = outLineVisible;
    u.textOrientation = orientation;
    return u;

  }

  JDBar(UndoPattern e) {
     initDefault();
     applyUndoPattern(e);
     min = e.min;
     max = e.max;
     value = e.value;
     outLineVisible = e.isClosed;
     orientation = e.textOrientation;
     updateShape();
   }


  // -----------------------------------------------------------
  // Private stuff
  // -----------------------------------------------------------

  // Compute summit coordinates from width, height
  // 0 1 2
  // 7   3
  // 6 5 4
  private void computeSummitCoordinates(int x,int y,int width, int height) {

    // Compute summit

    summit[0].x = x;
    summit[0].y = y;

    summit[2].x = x + width;
    summit[2].y = y;

    summit[4].x = x + width;
    summit[4].y = y + height;

    summit[6].x = x;
    summit[6].y = y + height;

    centerSummit();

  }

}