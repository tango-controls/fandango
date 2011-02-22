package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.chart.JLAxis;
import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import java.awt.*;
import java.awt.font.FontRenderContext;
import java.io.FileWriter;
import java.io.IOException;

/** JDraw Axis graphic object. JDAxis allows to build easily sizeable gauges, it supports
 *  Font, Label format, auto labelling, and tick.
 *  <p>Here is an example of few JDAxis:<p>
 *  <img src="JDAxis.gif" border="0" alt="JDAxis examples"></img>
 */
public class JDAxis extends JDRectangular {

  /** Horizontal axis */
  public final static int HORIZONTAL_AXIS = 0;
  /** Vertical axis */
  public final static int VERTICAL_AXIS  = 1;

  /** Labels are at the left of the axis (Vertical axis only) */
  public final static int LEFT_LABEL = 0;
  /** Labels are at the right of the axis (Vertical axis only) */
  public final static int RIGHT_LABEL = 1;

  /** Linear scale */
  public final static int LINEAR_SCALE = 0;
  /** Logarithmic scale */
  public final static int LOG_SCALE = 1;

  /** Use default compiler format to display double */
  public static final int AUTO_FORMAT = 0;
  /** Display value using exponential representation (x.xxEyy) */
  public static final int SCIENTIFIC_FORMAT = 1;
  /** Display number of second as HH:MM:SS */
  public static final int TIME_FORMAT = 2;
  /** Display integer using decimal format (%d) */
  public static final int DECINT_FORMAT = 3;
  /** Display integer using haxadecimal format (%x) */
  public static final int HEXINT_FORMAT = 4;
  /** Display integer using binary format (%b) */
  public static final int BININT_FORMAT = 5;
  /** Display value using exponential representation (xEyy) */
  public static final int SCIENTIFICINT_FORMAT = 6;

  // Default
  static private int orientationDefault = VERTICAL_AXIS;
  static private boolean tickCenteredDefault = false;
  static private int tickLengthDefault = 4;
  static private int labelPosDefault = LEFT_LABEL;
  static private int scaleDefault = LINEAR_SCALE;
  static private int formatDefault = AUTO_FORMAT;
  static private double minDefault = 0.0;
  static private double maxDefault = 100.0;
  static private boolean invertedDefault = true;
  static private int tickSpacingDefault = 10;

  // Axis parametres
  private Font    theFont;
  private int     orientation;
  private boolean tickCentered;
  private boolean inverted;
  private int     tickLength;
  private int     labelPos;
  private int     scale;
  private int     format;
  private int     tickSpacing;
  private double  min;
  private double  max;

  // Private vars
  private int     fAscent;
  private JLAxis  theAxis;

  // -----------------------------------------------------------
  // Construction
  // -----------------------------------------------------------
  /**
   * Consttruc a JDAxis object.
   * @param objectName Object name
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   * @param w Widht (pixel)
   * @param h Height (pixel)
   */
  public JDAxis(String objectName, int x, int y,int w, int h) {
    initDefault();
    setOrigin(new Point.Double(0.0, 0.0));
    summit = new Point.Double[8];
    name = objectName;
    createSummit();
    computeSummitCoordinates(x,y,w,h);
    buildAxis();
    updateShape();
    centerOrigin();
  }

  JDAxis(JDAxis e, int x, int y) {
    cloneObject(e, x, y);
    theFont = new Font(e.theFont.getName(), e.theFont.getStyle(), e.theFont.getSize());
    orientation = e.orientation;
    tickCentered = e.tickCentered;
    tickLength = e.tickLength;
    tickSpacing = e.tickSpacing;
    labelPos = e.labelPos;
    scale = e.scale;
    min = e.min;
    max = e.max;
    format = e.format;
    inverted = e.inverted;
    buildAxis();
    updateShape();
  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  void initDefault() {
    super.initDefault();
    lineWidth = 0;
    theFont = JDLabel.fontDefault;
    orientation = orientationDefault;
    tickCentered = tickCenteredDefault;
    tickLength = tickLengthDefault;
    labelPos = labelPosDefault;
    min = minDefault;
    max = maxDefault;
    scale = scaleDefault;
    format = formatDefault;
    inverted = invertedDefault;
    tickSpacing = tickSpacingDefault;
  }

  public JDObject copy(int x, int y) {
    return new JDAxis(this, x, y);
  }

  public void paint(JDrawEditor parent,Graphics g) {

    if (!visible) return;
    Graphics2D g2 = (Graphics2D) g;
    prepareRendering(g2);
    super.paint(parent,g);

    int tr = 0;
    boolean clipNeeded = false;
    Shape oldClip = null;
    Color backColor = Color.BLACK;
    if(parent!=null) backColor = parent.getBackground();

    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
            RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
    g2.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS,
            RenderingHints.VALUE_FRACTIONALMETRICS_ON);
    FontRenderContext frc = g2.getFontRenderContext();

    if (orientation == VERTICAL_AXIS) {

      theAxis.measureAxis(frc, 0, boundRect.height - 1);

      // Do we need to clip
      int tickLgth = theAxis.getTickLength();
      if (tickLgth < 0) tickLgth = 0;
      clipNeeded = (boundRect.width <= (theAxis.getThickness() + tickLgth));
      if (clipNeeded) {
        oldClip = g.getClip();
        g.setClip(boundRect.x, boundRect.y - fAscent, boundRect.width, boundRect.height + 2 * fAscent);
      }

      // Align axis
      if (labelPos == LEFT_LABEL)
        tr = boundRect.width - theAxis.getThickness() - 1;
      if (tr < 0) tr = 0;

      // Paint it
      theAxis.paintAxisDirect(g,frc,boundRect.x+tr,boundRect.y,backColor,0,0);

    } else {

      theAxis.measureAxis(frc,  boundRect.width - 1, 0);

      // Do we need to clip
      int tickLgth = theAxis.getTickLength();
      if (tickLgth < 0) tickLgth = 0;
      clipNeeded = (boundRect.height <= (theAxis.getThickness() + tickLgth));
      if (clipNeeded) {
        oldClip = g.getClip();
        int fo = theAxis.getFontOverWidth();
        g.setClip(boundRect.x - fo, boundRect.y, boundRect.width + 2*fo, boundRect.height);
      }

      // Paint it
      theAxis.paintAxisDirect(g,frc,boundRect.x,boundRect.y,backColor,0,0);

    }


    if(clipNeeded)
      g.setClip(oldClip);

  }

  Rectangle getRepaintRect() {
    Rectangle r = super.getRepaintRect();
    int tick = theAxis.getTickLength();
    if(tick<0) tick = 0;
    int fo = theAxis.getFontOverWidth();

    if(orientation==VERTICAL_AXIS) {
      r.x      -= tick;
      r.width  += 2*tick;
      r.y      -= fAscent;
      r.height += 2*fAscent;
    } else {
      r.y      -= tick;
      r.height += 2*tick;
      r.x      -= fo;
      r.width  += 2*fo;
    }

    return r;
  }

  void updateShape() {
    computeBoundRect();

    // Update shadow coordinates
    ptsx = new int[4];
    ptsy = new int[4];

    if (summit[0].x < summit[2].x) {
      if (summit[0].y < summit[6].y) {
        ptsx[0] = (int) (summit[0].x+0.5);
        ptsy[0] = (int) (summit[0].y+0.5);
        ptsx[1] = (int) (summit[2].x+0.5);
        ptsy[1] = (int) (summit[2].y+0.5);
        ptsx[2] = (int) (summit[4].x+0.5);
        ptsy[2] = (int) (summit[4].y+0.5);
        ptsx[3] = (int) (summit[6].x+0.5);
        ptsy[3] = (int) (summit[6].y+0.5);
      } else {
        ptsx[0] = (int) (summit[6].x+0.5);
        ptsy[0] = (int) (summit[6].y+0.5);
        ptsx[1] = (int) (summit[4].x+0.5);
        ptsy[1] = (int) (summit[4].y+0.5);
        ptsx[2] = (int) (summit[2].x+0.5);
        ptsy[2] = (int) (summit[2].y+0.5);
        ptsx[3] = (int) (summit[0].x+0.5);
        ptsy[3] = (int) (summit[0].y+0.5);
      }
    } else {
      if (summit[0].y < summit[6].y) {
        ptsx[0] = (int) (summit[2].x+0.5);
        ptsy[0] = (int) (summit[2].y+0.5);
        ptsx[1] = (int) (summit[0].x+0.5);
        ptsy[1] = (int) (summit[0].y+0.5);
        ptsx[2] = (int) (summit[6].x+0.5);
        ptsy[2] = (int) (summit[6].y+0.5);
        ptsx[3] = (int) (summit[4].x+0.5);
        ptsy[3] = (int) (summit[4].y+0.5);
      } else {
        ptsx[0] = (int) (summit[4].x+0.5);
        ptsy[0] = (int) (summit[4].y+0.5);
        ptsx[1] = (int) (summit[6].x+0.5);
        ptsy[1] = (int) (summit[6].y+0.5);
        ptsx[2] = (int) (summit[0].x+0.5);
        ptsy[2] = (int) (summit[0].y+0.5);
        ptsx[3] = (int) (summit[2].x+0.5);
        ptsy[3] = (int) (summit[2].y+0.5);
      }
    }

    // Update axis
    if(theAxis!=null) {

      if(orientation==VERTICAL_AXIS) {

          if(labelPos==LEFT_LABEL) {
            theAxis.setOrientation(JLAxis.VERTICAL_LEFT);
          } else {
            theAxis.setOrientation(JLAxis.VERTICAL_RIGHT);
          }
          if(tickCentered)
            theAxis.setPosition(JLAxis.VERTICAL_ORG);

      } else {

        theAxis.setOrientation(JLAxis.HORIZONTAL_DOWN);
        if(tickCentered)
          theAxis.setPosition(JLAxis.HORIZONTAL_ORG2);

      }

      theAxis.setTickSpacing((double)tickSpacing);
      theAxis.setTickLength(-tickLength);
      theAxis.setScale(scale);
      theAxis.setFont(theFont);
      fAscent = (int)(ATKGraphicsUtils.getLineMetrics("0",theFont).getAscent()+0.5f);
      theAxis.setAxisColor(foreground);
      theAxis.setMinimum(min);
      theAxis.setMaximum(max);
      theAxis.setLabelFormat(format);
      theAxis.setInverted(inverted);
    }

  }

  public boolean hasShadow() {
    // Axis cannot have shadow
    return false;
  }

  public void setForeground(Color f) {
    super.setForeground(f);
    updateShape();
  }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------
  /**
   * Sets the label font of this axis.
   * @param f Axis label font
   */
  public void setFont(Font f) {
    theFont = f;
    updateShape();
  }

  /**
   * Returns the label font.
   * @see #setFont
   */
  public Font getFont() {
    return theFont;
  }

  /**
   * Centers or not axis tick.
   * @param center True to center tick.
   * @see #setTickWidth
   */
  public void setTickCentered(boolean center) {
    tickCentered = center;
    updateShape();
  }

  /**
   * Determines whether axis ticks are centered.
   * @return true if tick are centered.
   * @see #setTickCentered
   */
  public boolean isTickCentered() {
    return tickCentered;
  }

  /**
   * Sets the axis tick width. Passing a negative value will result in displaying tick
   * on the other side of the axis. If tick are centered , negative and positive value
   * will have the same effects.
   * @param width Tick width
   * @see #setTickCentered
   */
  public void setTickWidth(int width) {
    tickLength = width;
    updateShape();
  }

  /**
   * Returns the current axis tick width.
   * @see #setTickWidth
   */
  public int getTickWidth() {
    return tickLength;
  }

  /**
   * Sets the minimum tick spacing (in pixel).
   * Allows to control the number of generated labels.
   * @param spacing Minimum tick spacing
   */
  public void setTickSpacing(int spacing) {
    tickSpacing = spacing;
    updateShape();
  }

  /**
   * Returns the current axis spacing (in pixel).
   * @see #setTickSpacing
   */
  public int getTickSpacing() {
    return tickSpacing;
  }

  /**
   * Sets the max value of this axis.
   * @param m Max value
   */
  public void setMax(double m) {
    max = m;
    updateShape();
  }

  /**
   * Sets the min value of this axis.
   * @param m Min value
   */
  public void setMin(double m) {
    min = m;
    updateShape();
  }

  /**
   * Returns the max value of this axis.
   * @see #setMax
   */
  public double getMax() {
    return max;
  }

  /**
   * Returns the min value of this axis.
   * @see #setMin
   */
  public double getMin() {
    return min;
  }

  /**
   * Sets the label positionning policy. Works only for vertical axis.
   * @param pos Position
   * @see #LEFT_LABEL
   * @see #RIGHT_LABEL
   */
  public void setLabelPos(int pos) {
    labelPos = pos;
    updateShape();
  }

  /**
   * Returns the current label positionning policy.
   * @see #setLabelPos
   */
  public int getLabelPos() {
    return labelPos;
  }

  /**
   * Sets the axis orientation.
   * @param o Orientation value
   * @see #HORIZONTAL_AXIS
   * @see #VERTICAL_AXIS
   */
  public void setOrientation(int o) {
    orientation = o;
    updateShape();
  }

  /**
   * Returns the orientation of this axis.
   * @see #setOrientation
   */
  public int getOrientation() {
    return orientation;
  }

  /**
   * Sets the scale of this axis.
   * @param s Scale value
   * @see #LINEAR_SCALE
   * @see #LOG_SCALE
   */
  public void setScale(int s) {
    scale = s;
    updateShape();
  }

  /**
   * Returns the scale of this axis.
   * @see #setScale
   */
  public int getScale() {
    return scale;
  }

  /**
   * Sets the label format of this axis.
   * @param f Format value
   * @see #AUTO_FORMAT
   * @see #SCIENTIFIC_FORMAT
   * @see #TIME_FORMAT
   * @see #DECINT_FORMAT
   * @see #HEXINT_FORMAT
   * @see #BININT_FORMAT
   * @see #SCIENTIFICINT_FORMAT
   *
   */
  public void setFormat(int f) {
    format = f;
    updateShape();
  }

  /**
   * Returns the label format of this axis.
   * @see #setFormat
   */
  public int getFormat() {
    return format;
  }

  /**
   * Invert or not this axis. When enabled , label are going in the opposite side
   * of the screen orientation.
   * @param i True to invert this axis.
   */
  public void setInverted(boolean i) {
    inverted = i;
    updateShape();
  }

  /**
   * Determines whether this axis is inverted.
   * @see #setInverted
   */
  public boolean isInverted() {
    return inverted;
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  void saveObject(FileWriter f, int level) throws IOException {

    String decal = saveObjectHeader(f, level);
    String to_write;

     if (theFont.getName() != JDLabel.fontDefault.getName() ||
        theFont.getStyle() != JDLabel.fontDefault.getStyle() ||
        theFont.getSize() != JDLabel.fontDefault.getSize()) {
      to_write = decal + "font:\"" + theFont.getName() + "\"," + theFont.getStyle() + "," + theFont.getSize() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (tickCentered != tickCenteredDefault) {
      to_write = decal + "tickCentered:" + tickCentered + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (inverted != invertedDefault) {
      to_write = decal + "inverted:" + inverted + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (tickSpacing != tickSpacingDefault) {
      to_write = decal + "tickSpacing:" + tickSpacing + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (tickLength != tickLengthDefault) {
      to_write = decal + "tickLength:" + tickLength + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (max != maxDefault) {
      to_write = decal + "max:" + max + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (min != minDefault) {
      to_write = decal + "min:" + min + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (labelPos != labelPosDefault) {
      to_write = decal + "labelPos:" + labelPos + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (orientation != orientationDefault) {
      to_write = decal + "orientation:" + orientation + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (scale != scaleDefault) {
      to_write = decal + "scale:" + scale + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (format != formatDefault) {
      to_write = decal + "format:" + format + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f, level);

  }

  JDAxis(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("font")) {
        theFont = f.parseFont();
      } else if (propName.equals("tickCentered")) {
        tickCentered = f.parseBoolean();
      } else if (propName.equals("inverted")) {
        inverted = f.parseBoolean();
      } else if (propName.equals("tickLength")) {
        tickLength = (int) f.parseDouble();
      } else if (propName.equals("tickSpacing")) {
        tickSpacing = (int) f.parseDouble();
      } else if (propName.equals("labelPos")) {
        labelPos = (int) f.parseDouble();
      } else if (propName.equals("orientation")) {
        orientation = (int) f.parseDouble();
      } else if (propName.equals("scale")) {
        scale = (int) f.parseDouble();
      } else if (propName.equals("min")) {
        min = f.parseDouble();
      } else if (propName.equals("max")) {
        max = f.parseDouble();
      } else if (propName.equals("format")) {
        format = (int) f.parseDouble();
      } else
        loadDefaultPropery(f, propName);
    }

    f.endBlock();

    buildAxis();
    updateShape();
  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDAxis);
    fillUndoPattern(u);
    u.fName = theFont.getName();
    u.fStyle = theFont.getStyle();
    u.fSize = theFont.getSize();
    u.tickCentered = tickCentered;
    u.arrowWidth = tickLength;
    u.cornerWidth = tickSpacing;
    u.vAlignment = labelPos;
    u.arrowMode = orientation;
    u.arcType = scale;
    u.min = min;
    u.max = max;
    u.axis = theAxis;
    u.angleExtent = format;
    u.isClosed = inverted;
    return u;
  }

  JDAxis(UndoPattern e) {
    initDefault();
    applyUndoPattern(e);
    theFont = new Font(e.fName,e.fStyle,e.fSize);
    tickCentered = e.tickCentered;
    tickLength = e.arrowWidth;
    tickSpacing = e.cornerWidth;
    labelPos = e.vAlignment;
    orientation = e.arrowMode;
    scale = e.arcType;
    min = e.min;
    max = e.max;
    format = e.angleExtent;
    theAxis = e.axis;
    inverted = e.isClosed;
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

  private void buildAxis() {
    if(orientation==VERTICAL_AXIS)
      theAxis = new JLAxis(null,JLAxis.VERTICAL_LEFT);
    else
      theAxis = new JLAxis(null,JLAxis.HORIZONTAL_DOWN);
    theAxis.setAutoScale(false);
    theAxis.setAnnotation(JLAxis.VALUE_ANNO);
  }

}
