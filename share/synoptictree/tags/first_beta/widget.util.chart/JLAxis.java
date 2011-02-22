//
// JLAxis.java
// Description: A Class to handle 2D graphics plot
//
// JL Pons (c)ESRF 2002

package fr.esrf.tangoatk.widget.util.chart;

import java.awt.*;
import java.awt.font.*;
import java.awt.geom.*;
import javax.swing.*;
import java.text.SimpleDateFormat;
import java.util.*;

import com.braju.format.Format;

// Inner class to handle label info

class LabelInfo implements java.io.Serializable {

  String value;
  Dimension size;
  double pos;
  Point offset;

  LabelInfo(String lab, int w, int h, double pos) {
    value = lab;
    size = new Dimension(w, h);
    this.pos = pos;
    offset = new Point(0,0);
  }

  public void setOffset(int x,int y) {
    offset.x = x;
    offset.y = y;
  }

  public int getWidth() {
    return size.width + Math.abs(offset.x);
  }

  public int getHeight() {
    return size.height + Math.abs(offset.y);
  }

}

// Inner class to handle XY correlation

class XYData implements java.io.Serializable {

  public DataList d1;
  public DataList d2;  // View plotted on the xAxis

  XYData(DataList d1, DataList d2) {
    this.d1 = d1;
    this.d2 = d2;
  }

  // Find the next point for XY mode
  void toNextXYPoint() {

    // Correlation mode
    d1 = d1.next;
    while (d1 != null && d2 != null && d2.next != null && d2.next.x <= d1.x) d2 = d2.next;

  }

  // Go to starting time position
  void initFirstPoint() {
    if (d1.x < d2.x) {
      while (d1 != null && d1.x < d2.x) d1 = d1.next;
    } else {
      while (d2 != null && d2.next != null && d2.next.x < d1.x) d2 = d2.next;
    }
  }


  boolean isValid() {
    return (d1 != null && d2 != null);
  }

}

/**
 * Class which handles chart axis.
 * @author JL Pons
 */

public class JLAxis implements java.io.Serializable {

  // constant
  /** Horizontal axis at bottom of the chart */
  public static final int HORIZONTAL_DOWN = 1;
  /** Horizontal axis at top of the chart */
  public static final int HORIZONTAL_UP = 2;
  /** Horizontal axis at 0 position (on Y1) */
  public static final int HORIZONTAL_ORG1 = 3;
  /** Horizontal axis at 0 position (on Y2) */
  public static final int HORIZONTAL_ORG2 = 4;
  /** Vertical right axis */
  public static final int VERTICAL_RIGHT = 5;
  /** Vertical left axis */
  public static final int VERTICAL_LEFT = 6;
  /** Vertical axis at X=0 */
  public static final int VERTICAL_ORG = 7;

  /** Draw time annotation for x axis. */
  public static final int TIME_ANNO = 1;
  /** Draw formated annotation  */
  public static final int VALUE_ANNO = 2;

  /** Use linear scale for this axis  */
  public static final int LINEAR_SCALE = 0;
  /** Use logarithmic scale for this axis  */
  public static final int LOG_SCALE = 1;

  /** Use default compiler format to display double */
  public static final int AUTO_FORMAT = 0;
  /** Display value using exponential representation (x.xxEyy) */
  public static final int SCIENTIFIC_FORMAT = 1;
  /** Display number of second as HH:MM:SS */
  public static final int TIME_FORMAT = 2;
  /** Display integer using decimal format */
  public static final int DECINT_FORMAT = 3;
  /** Display integer using haxadecimal format */
  public static final int HEXINT_FORMAT = 4;
  /** Display integer using binary format */
  public static final int BININT_FORMAT = 5;
  /** Display value using exponential representation (xEyy) */
  public static final int SCIENTIFICINT_FORMAT = 6;
  /** Display value as date */
  public static final int DATE_FORMAT = 7;

  /** US date format to format labels as dates */
  public static final String US_DATE_FORMAT = "yyyy-MM-dd HH:mm:ss.SSS";
  /** French date format to format labels as dates */
  public static final String FR_DATE_FORMAT = "dd-MM-yyyy HH:mm:ss.SSS";

  static final double YEAR = 31536000000.0;
  static final double MONTH = 2592000000.0;
  static final double DAY = 86400000.0;
  static final double HOUR = 3600000.0;
  static final double MINU = 60000.0;
  static final double SECO = 1000.0;

  //Local declaration
  private boolean visible;
  private double min = 0.0;
  private double max = 100.0;
  private double minimum = 0.0;
  private double maximum = 100.0;
  private boolean autoScale = false;
  private int scale = LINEAR_SCALE;
  private Color labelColor;
  private Font labelFont;
  private int labelFormat;
  private Vector<LabelInfo> labels;
  private int orientation;  // Axis orientation/position
  private int dOrientation; // Default orientation (cannot be _ORG)
  private boolean subtickVisible;
  private Dimension csize = null;
  private String name;
  private int annotation = VALUE_ANNO;
  private Vector<JLDataView> dataViews;
  private double ln10;
  private boolean gridVisible;
  private boolean subGridVisible;
  private int gridStyle;
  private Rectangle boundRect;
  private boolean lastAutoScate;
  private boolean isZoomed;
  private double percentScrollback;
  private double axisDuration = Double.POSITIVE_INFINITY;
  private String axeName;
  private java.text.SimpleDateFormat useFormat;
  private double desiredPrec;
  private boolean drawOpposite;
  private int tickLength;
  private int subtickLength;
  private int fontOverWidth;
  private boolean inverted = false;
  private double tickStep;    // In pixel
  private double minTickStep;
  private int subTickStep; // 0 => NONE , -1 => Log step , 1.. => Linear step
  private boolean fitXAxisToDisplayDuration;
  
  private boolean zeroAlwaysVisible = false;
  private boolean  autoLabeling = true;
  private String[] userLabel = null;
  private double[] userLabelPos = null;

  private String dateFormat = US_DATE_FORMAT;
  //Global
  static final java.util.GregorianCalendar calendar = new java.util.GregorianCalendar();
  static final java.text.SimpleDateFormat genFormat = new java.text.SimpleDateFormat("dd/MM/yy HH:mm:ss.SSS");
  static final java.text.SimpleDateFormat yearFormat = new java.text.SimpleDateFormat("yyyy");
  static final java.text.SimpleDateFormat monthFormat = new java.text.SimpleDateFormat("MMMMM yy");
  static final java.text.SimpleDateFormat weekFormat = new java.text.SimpleDateFormat("dd/MM/yy");
  static final java.text.SimpleDateFormat dayFormat = new java.text.SimpleDateFormat("EEE dd");
  static final java.text.SimpleDateFormat hour12Format = new java.text.SimpleDateFormat("EEE HH:mm");
  static final java.text.SimpleDateFormat hourFormat = new java.text.SimpleDateFormat("HH:mm");
  static final java.text.SimpleDateFormat secFormat = new java.text.SimpleDateFormat("HH:mm:ss");

  static final double[] timePrecs = {
    1 * SECO, 5 * SECO, 10 * SECO, 30 * SECO,
    1 * MINU, 5 * MINU, 10 * MINU, 30 * MINU,
    1 * HOUR, 3 * HOUR, 6 * HOUR, 12 * HOUR,
    1 * DAY, 7 * DAY, 1 * MONTH, 1 * YEAR, 5 * YEAR,
    10 * YEAR
  };

  static final java.text.SimpleDateFormat timeFormats[] = {
    secFormat, secFormat, secFormat, secFormat,
    secFormat, secFormat, secFormat, hourFormat,
    hourFormat, hourFormat, hourFormat, hour12Format,
    dayFormat, weekFormat, monthFormat, yearFormat,
    yearFormat, yearFormat};

  static final String labelFomats[] = {"%g", "", "%02d:%02d:%02d", "%d", "%X", "%b"};

  static final int triangleX[] = {0, 4, -4};
  static final int triangleY[] = {-3, 3, 3};
  static final Polygon triangleShape = new Polygon(triangleX, triangleY, 3);

  static final int diamondX[] = {0, 4, 0, -4};
  static final int diamondY[] = {4, 0, -4, 0};
  static final Polygon diamondShape = new Polygon(diamondX, diamondY, 4);

  static double logStep[] = {0.301, 0.477, 0.602, 0.699, 0.778, 0.845, 0.903, 0.954};

  static public String getHelpString() {
    return
    "-- Axis settings --\n  Parameter name is preceded by the axis name.\n\n" +
    "visible:true or false   Displays the axis\n" +
    "grid:true or false   Displays the grid\n" +
    "subgrid:true or false   Displays the sub grid\n" +
    "grid_style:style   (0 Solid,1 Dot, 2 Dash, 3 Long Dash)\n" +
    "min:value Axis minimum\n" +
    "max:value Axis maximum\n" +
    "autoscale:true or false Axis autoscale\n" +
    "scale:s   Axis scale (0 Linear ,1 Log)\n" +
    "format:format   Axis format (0 Auto,1 Sci,2 Time,3 Dec,4 Hex,5 Bin))\n" +
    "title:'title'   Axis title ('null' to disable)\n" +
    "color:r,g,b   Axis color\n" +
    "label_font:name,style(0 Plain,1 Bold,2 italic),size\n";
  }

  /** Axis constructor (Expert usage).
   * @param orientation Default Axis placement (cannot be ..._ORG).
   * @param parent (deprecated, not used).
   * @see JLAxis#HORIZONTAL_DOWN
   * @see JLAxis#HORIZONTAL_UP
   * @see JLAxis#VERTICAL_LEFT
   * @see JLAxis#VERTICAL_RIGHT
   * @see JLAxis#setPosition
   */
  public JLAxis(JComponent parent, int orientation) {
    labels = new Vector<LabelInfo>();
    labelFont = new Font("Dialog", Font.PLAIN, 11);
    labelColor = Color.black;
    name = null;
    this.orientation = orientation;
    dOrientation = orientation;
    inverted = !isHorizontal();
    dataViews = new Vector<JLDataView>();
    ln10 = Math.log(10);
    gridVisible = false;
    subGridVisible = false;
    gridStyle = JLDataView.STYLE_DOT;
    labelFormat = AUTO_FORMAT;
    subtickVisible = true;
    boundRect = new Rectangle(0, 0, 0, 0);
    isZoomed = false;
    percentScrollback = 0.0;
    axeName = "";
    visible = true;
    drawOpposite = true;
    tickLength = 4;
    subtickLength = tickLength/2;
    fontOverWidth = 0;
    minTickStep = 50.0;
    fitXAxisToDisplayDuration = true;
  }

  /**
   * Sets the percent scrollback. When using {@link JLChart#addData(JLDataView , double , double ) JLChart.addData}
   * and TIME_ANNO mode for the horizontal axis this property allows to avoid a full graph repaint
   * for every new data entered.
   * @param d Scrollback percent [0..100]
   */
  public void setPercentScrollback(double d) {
    percentScrollback = d / 100;
  }

  /**
   * Gets the percent scrollback
   * @return scrollback percent
   */
  public double getPercentScrollback() {
    return percentScrollback;
  }

  /**
   * Sets the axis color.
   * @param c Axis color
   * @see JLAxis#getAxisColor
   */
  public void setAxisColor(Color c) {
    labelColor = c;
  }

  /**
   * Returns the axis color.
   * @return Axis color
   * @see JLAxis#setAxisColor
   */
  public Color getAxisColor() {
    return labelColor;
  }

  /**
   * Sets the axis label format.
   * @param l Format of values displayed on axis and in tooltips.
   * @see  JLAxis#AUTO_FORMAT
   * @see  JLAxis#SCIENTIFIC_FORMAT
   * @see  JLAxis#TIME_FORMAT
   * @see  JLAxis#DECINT_FORMAT
   * @see  JLAxis#HEXINT_FORMAT
   * @see  JLAxis#BININT_FORMAT
   * @see  JLAxis#SCIENTIFICINT_FORMAT
   * @see  JLAxis#DATE_FORMAT
   * @see  JLAxis#getLabelFormat
   */
  public void setLabelFormat(int l) {
    labelFormat = l;
  }

  /**
   * Returns the axis label format.
   * @return Axis value format
   * @see  JLAxis#setLabelFormat
   */
  public int getLabelFormat() {
    return labelFormat;
  }

  /**
   * Shows the grid.
   * @param b true to make the grid visible; false to hide it
   * @see  JLAxis#isGridVisible
   */
  public void setGridVisible(boolean b) {
    gridVisible = b;
  }

  /**
   * Fit the x axis to display duration (Horizontal axis only).
   * @param b true to fit x axis false otherwise
   */
  public void setFitXAxisToDisplayDuration(boolean b) {
    fitXAxisToDisplayDuration = b;
  }

  /**
   * Return true if the x axis fit to display duration.
   */
  public boolean isFitXAxisToDisplayDuration() {
    return fitXAxisToDisplayDuration;
  }

  /**
   * Determines whether the axis is showing the grid
   * @return true if the grid is visible, false otherwise
   * @see  JLAxis#setGridVisible
   */
  public boolean isGridVisible() {
    return gridVisible;
  }

  /**
   * Draw a second axis at the opposite side.
   * @param b true to enable the opposite axis.
   */
  public void setDrawOpposite(boolean b) {
    drawOpposite = b;
  }

  /**
   * Determines whether the axis at the opposite side is visible
   * @return true if opposite axis is visible.
   * @see JLAxis#setDrawOpposite
   */
  public boolean isDrawOpposite() {
    return drawOpposite;
  }

  /**
   * Shows the sub grid. More accurate grid displayed with a soft color.
   * @param b true to make the subgrid visible; false to hide it
   * @see  JLAxis#isSubGridVisible
   */
  public void setSubGridVisible(boolean b) {
    subGridVisible = b;
  }

  /** Determines whether the axis is showing the sub grid
   *  @return true if the subgrid is visible, false otherwise
   *  @see JLAxis#setSubGridVisible
   */
  public boolean isSubGridVisible() {
    return subGridVisible;
  }

  /** Sets the grid style.
   * @param s Style of the grid. Can be one of the following:
   * @see JLDataView#STYLE_SOLID
   * @see JLDataView#STYLE_DOT
   * @see JLDataView#STYLE_DASH
   * @see JLDataView#STYLE_LONG_DASH
   * @see JLDataView#STYLE_DASH_DOT
   * @see JLAxis#getGridStyle
   */
  public void setGridStyle(int s) {
    gridStyle = s;
  }

  /**
   * Returns the current grid style.
   * @return the current grid style
   * @see JLAxis#setGridStyle
   */
  public int getGridStyle() {
    return gridStyle;
  }

  /**
   * Sets the label font
   * @param f Sets the font for this components
   * @see JLAxis#getFont
   */
  public void setFont(Font f) {
    labelFont = f;
  }

  /**
   * Gets the label font
   * @return The current label font
   * @see JLAxis#setFont
   */
  public Font getFont() {
    return labelFont;
  }

  /**
   * Set the annotation method
   * @param a Annotation for this axis
   * @see JLAxis#TIME_ANNO
   * @see JLAxis#VALUE_ANNO
   */
  public void setAnnotation(int a) {
    annotation = a;
  }

  /**
   * Returns the annotation method
   * @see JLAxis#setAnnotation
   */
  public int getAnnotation() {
    return annotation;
  }

  /**
   * Display or hide the axis.
   * @param b True to make the axis visible.
   */
  public void setVisible(boolean b) {
    visible = b;
  }

  /**
   * Returns true if the axis is visble, false otherwise
   */
  public boolean isVisible() {
    return visible;
  }

  /** Determines whether the axis is zoomed.
   * @return true if the axis is zoomed, false otherwise
   * @see JLAxis#zoom
   */
  public boolean isZoomed() {
    return isZoomed;
  }

  /** Determines whether the axis is in XY mode. Use only with HORIZONTAL axis.
   *  @return true if the axis is in XY mode, false otherwise
   *  @see JLAxis#addDataView
   */
  public boolean isXY() {
    return (dataViews.size() > 0);
  }

  /**
   * Sets minimum axis value. This value is ignored when using autoscale.
   * @param d Minimum value for this axis. Must be strictly positive for LOG_SCALE.
   * @see JLAxis#getMinimum
   */
  public void setMinimum(double d) {

    minimum = d;

    if (!autoScale) {
      if (scale == LOG_SCALE) {
        if (d <= 0) d = 1;
        min = Math.log(d) / ln10;
      } else
        min = d;
    }

  }

  /**
   * Gets minimum axis value
   * @return  The minimum value for this axis.
   * @see JLAxis#setMinimum
   */
  public double getMinimum() {
    return minimum;
  }

  /**
   * Sets maximum axis value. This value is ignored when using autoscale.
   * @param d Maximum value for this axis. Must be strictly positive for LOG_SCALE.
   * @see JLAxis#getMaximum
   */
  public void setMaximum(double d) {

    maximum = d;

    if (!autoScale) {
      if (scale == LOG_SCALE) {
        if (max <= 0) max = min * 10.0;
        max = Math.log(d) / ln10;
      } else
        max = d;
    }

  }

  /**
   * Gets maximum axis value
   * @return  The maximum value for this axis.
   * @see JLAxis#setMaximum
   */
  public double getMaximum() {
    return maximum;
  }

  /**
   * Expert usage. Get minimum axis value (according to auto scale transformation).
   * @return  The minimum value for this axis.
   */
  public double getMin() {
    return min;
  }

  /**
   * Expert usage. Get maximum axis value (according to auto scale transformation).
   * @return  The maximum value for this axis.
   */
  public double getMax() {
    return max;
  }

  /** Determines whether the axis is autoscaled.
   * @return true if the axis is autoscaled, false otherwise
   * @see JLAxis#setAutoScale
   */
  public boolean isAutoScale() {
    return autoScale;
  }

  /**
   * Sets the autoscale mode for this axis.
   * @param b true if the axis is autoscaled, false otherwise
   * @see JLAxis#isAutoScale
   */
  public void setAutoScale(boolean b) {
    autoScale = b;
  }

  /** Gets the scale mdoe for this axis.
   * @return scale mdoe
   * @see JLAxis#setScale
   */
  public int getScale() {
    return scale;
  }

  /** Sets scale mode
   * @param s Scale mode for this axis
   * @see JLAxis#LINEAR_SCALE
   * @see JLAxis#LOG_SCALE
   * @see JLAxis#getScale
   */
  public void setScale(int s) {

    scale = s;

    if (scale == LOG_SCALE) {
      // Check min and max
      if (minimum <= 0 || maximum <= 0) {
        minimum = 1;
        maximum = 10;
      }
    }

    if (scale == LOG_SCALE) {
      min = Math.log(minimum) / ln10;
      max = Math.log(maximum) / ln10;
    } else {
      min = minimum;
      max = maximum;
    }

  }

  /**
   * Sets the axis orientation and reset position.
   * @param orientation Orientation value
   * @see JLAxis#HORIZONTAL_DOWN
   * @see JLAxis#HORIZONTAL_UP
   * @see JLAxis#VERTICAL_LEFT
   * @see JLAxis#VERTICAL_RIGHT
   * @see #setPosition
   */
  public void setOrientation(int orientation) {
    this.orientation = orientation;
    dOrientation = orientation;
  }

  /**
   * Returns the orientation of this axis.
   * @see #setOrientation
   */
  public int getOrientation() {
    return orientation;
  }

  /** Zoom axis.
   * @param x1 New minimum value for this axis
   * @param x2 New maximum value for this axis
   * @see JLAxis#isZoomed
   * @see JLAxis#unzoom
   */
  public void zoom(int x1, int x2) {

    if (!isZoomed) lastAutoScate = autoScale;

    if (isHorizontal()) {

      // Clip
      if (x1 < boundRect.x) x1 = boundRect.x;
      if (x2 > (boundRect.x + boundRect.width)) x2 = boundRect.x + boundRect.width;

      // Too small zoom
      if ((x2 - x1) < 10) return;

      // Compute new min and max
      double xr1 = (double) (x1 - boundRect.x) / (double) (boundRect.width);
      double xr2 = (double) (x2 - boundRect.x) / (double) (boundRect.width);
      double nmin = min + (max - min) * xr1;
      double nmax = min + (max - min) * xr2;

      // Too small zoom
      double difference = nmax - nmin;
      if (difference < 1E-13) return;

      min = nmin;
      max = nmax;

    } else {

      // Clip
      if (x1 < boundRect.y) x1 = boundRect.y;
      if (x2 > (boundRect.y + boundRect.height)) x2 = boundRect.y + boundRect.height;

      // Too small zoom
      if ((x2 - x1) < 10) return;

      // Compute new min and max
      double yr1 = (double) (boundRect.y + boundRect.height - x2) / (double) (boundRect.height);
      double yr2 = (double) (boundRect.y + boundRect.height - x1) / (double) (boundRect.height);
      double nmin = min + (max - min) * yr1;
      double nmax = min + (max - min) * yr2;

      // Too small zoom
      double difference = nmax - nmin;
      if (difference < 1E-13) return;

      min = nmin;
      max = nmax;

    }

    autoScale = false;
    isZoomed = true;

  }

  /** Unzoom the axis and restores last state.
   * @see JLAxis#isZoomed
   * @see JLAxis#unzoom
   */
  public void unzoom() {
    autoScale = lastAutoScate;
    if (!lastAutoScate) {
      setMinimum(getMinimum());
      setMaximum(getMaximum());
    }
    isZoomed = false;
  }

  /**
   * @deprecated Use getTickSpacing
   * @see JLAxis#getTickSpacing
   */
  public int getTick() {
    return (int)minTickStep;
  }

  /**
   * Returns the current minimum tick spacing (in pixel).
   */
  public double getTickSpacing() {
    return minTickStep;
  }

  /**
   * Sets the minimum tick spacing (in pixel).
   * Allows to control the number of generated labels.
   * @param spacing Minimum tick spacing
   */
  public void setTickSpacing(double spacing) {
    minTickStep = spacing;
  }

  /**
   * @deprecated Use setTickSpacing
   * @see JLAxis#setTickSpacing
   */
  public void setTick(int s) {
    minTickStep = s;
  }

  /**
   * Sets the tick length (in pixel).
   * @param lgth Length
   */
  public void setTickLength(int lgth) {
    tickLength = lgth;
    subtickLength = tickLength/2;
  }

  /**
   * Returns the tick length (in pixel).
   */
  public int getTickLength() {
    return tickLength;
  }

  /** Gets the axis label.
   * @return Axis name.
   * @see JLAxis#setName
   */
  public String getName() {
    return name;
  }

  /**
   * Sets the axis label.
   * Label is displayed along or above the axis.
   * @param s Name of this axis.
   * @see JLAxis#getName
   */
  public void setName(String s) {

    int z = 0;
    if (s != null) z = s.length();

    if (z > 0)
      name = s;
    else
      name = null;

  }

  /**
   * Sets the axis position
   * @param o Axis position
   * @see JLAxis#VERTICAL_LEFT
   * @see JLAxis#VERTICAL_RIGHT
   * @see JLAxis#VERTICAL_ORG
   * @see JLAxis#HORIZONTAL_DOWN
   * @see JLAxis#HORIZONTAL_UP
   * @see JLAxis#HORIZONTAL_ORG1
   * @see JLAxis#HORIZONTAL_ORG2
   */
  public void setPosition(int o) {
    if (isHorizontal()) {
      if (o >= JLAxis.HORIZONTAL_DOWN && o <= JLAxis.HORIZONTAL_ORG2)
        orientation = o;
    } else {
      if (o >= JLAxis.VERTICAL_RIGHT && o <= JLAxis.VERTICAL_ORG)
        orientation = o;
    }
  }

  /**
   * Returns the axis position
   * @return Axis position
   * @see JLAxis#setPosition
   */
  int getPosition() {
    return orientation;
  }

  /** Gets the axis label.
   * @return Axis name.
   * @see JLAxis#setAxeName
   */
  public String getAxeName() {
    return axeName;
  }

  /** Sets the axis name. Name is displayed in tooltips when clicking on the graph.
   * @param s Name of this axis.
   * @see JLAxis#getName
   */
  public void setAxeName(String s) {
    axeName = s;
  }

  /** Displays a DataView on this axis.
   * The graph switches in XY monitoring mode when adding
   * a dataView to X axis. Only one view is allowed on HORIZONTAL Axis.
   * In case of a view plotted along this horizontal axis doesn't have
   * the same number of point as this x view, points are correlated according to
   * their x values.
   * @param v The dataview to map along this axis.
   * @see JLAxis#removeDataView
   * @see JLAxis#clearDataView
   * @see JLAxis#getViews
   */
  public void addDataView(JLDataView v) {

    if (dataViews.contains(v))
      return;

    if (!isHorizontal()) {
      dataViews.add(v);
      v.setAxis(this);
    } else {
      // Switch to XY mode
      // Only one view on X
      dataViews.clear();
      dataViews.add(v);
      v.setAxis(this);
      setAnnotation(VALUE_ANNO);
    }
  }

  /**
   * Add the given dataView at the specifed index.
   * @param index Insertion position
   * @param v DataView to add
   * @see JLAxis#addDataView
   */
  public void addDataViewAt(int index,JLDataView v) {

    if (dataViews.contains(v))
      return;

    if (!isHorizontal()) {
      dataViews.add(index,v);
      v.setAxis(this);
    } else {
      addDataView(v);
    }

  }

  /**
   * Get the dataView of this axis at the specified index.
   * @param index DataView index
   * @return Null if index out of bounds.
   */
  public JLDataView getDataView(int index) {

    if(index<0 || index>=dataViews.size()) {
//      System.out.println("JLChart.getDataView(): index out of bounds.");
      return null;
    }
    return dataViews.get(index);

  }

  /** Removes dataview from this axis
   * @param v dataView to remove from this axis.
   * @see JLAxis#addDataView
   * @see JLAxis#clearDataView
   * @see JLAxis#getViews
   */
  public void removeDataView(JLDataView v) {
    dataViews.remove(v);
    v.setAxis(null);
    if (isHorizontal()) {
      // Restore TIME_ANNO and Liner scale
      setAnnotation(TIME_ANNO);
      if (scale != LINEAR_SCALE) setScale(LINEAR_SCALE);
    }
  }

  /** Removes dataview from this axis and returns true if the dataview has been found for this Axis
   * @param v dataView to remove from this axis.
   * @return true if Axis contained the dataview and false if this dataview did not belong to the axis
   * @see JLAxis#addDataView
   * @see JLAxis#clearDataView
   * @see JLAxis#getViews
   */
  public boolean checkRemoveDataView(JLDataView v)
  {
      boolean contained = dataViews.remove(v);
      if (contained == true)
      {
	 v.setAxis(null);
	 if (isHorizontal())
	 {
	   // Restore TIME_ANNO and Liner scale
	   setAnnotation(TIME_ANNO);
	   if (scale != LINEAR_SCALE) setScale(LINEAR_SCALE);
	 }
      }
      return contained;
  }

  /** Clear all dataview from this axis
   * @see JLAxis#removeDataView
   * @see JLAxis#addDataView
   * @see JLAxis#getViews
   */
  public void clearDataView() {
    int sz = dataViews.size();
    JLDataView v;
    for (int i = 0; i < sz; i++) {
      v = dataViews.get(i);
      v.setAxis(null);
    }
    dataViews.clear();
  }

  /** Gets all dataViews displayed on this axis.
   * Do not modify the returned vector (Use as read only).
   * @return Vector of JLDataView.
   * @see JLAxis#addDataView
   * @see JLAxis#removeDataView
   * @see JLAxis#clearDataView
   */
  public Vector<JLDataView> getViews() {
    return dataViews;
  }

  /**
   * Returns the number if dataview in this axis.
   * @return DataView number.
   */
  public int getViewNumber() {
    return dataViews.size();
  }


  /**
   * Invert this axis.
   * @param i true to invert the axis
   */
  public void setInverted(boolean i) {
    inverted = i;
  }

  /**
   * Returns true if this axis is inverted.
   */
  public boolean isInverted() {
    return inverted;
  }

  /**
   * Returns the bouding rectangle of this axis.
   * @return The bounding rectangle
   */
  public Rectangle getBoundRect() {
    return boundRect;
  }

  /** Return a scientific (exponential) representation of the double.
   * @param d double to convert
   * @return A string continaing a scientific representation of the given double.
   */
  public String toScientific(double d) {

    double a = Math.abs(d);
    int e = 0;
    String f = "%.2fe%d";

    if (a != 0) {
      if (a < 1) {
        while (a < 1) {
          a = a * 10;
          e--;
        }
      } else {
        while (a >= 10) {
          a = a / 10;
          e++;
        }
      }
    }

    if (a >= 9.999999999) {
      a = a / 10;
      e++;
    }

    if (d < 0) a = -a;

    Object o[] = {new Double(a), new Integer(e)};

    return Format.sprintf(f, o);
  }

  public String toScientificInt(double d) {

    double a = Math.abs(d);
    int e = 0;
    String f = "%de%d";

    if (a != 0) {
      if (a < 1) {
        while (a < 1) {
          a = a * 10;
          e--;
        }
      } else {
        while (a >= 10) {
          a = a / 10;
          e++;
        }
      }
    }

    if (a >= 9.999999999) {
      a = a / 10;
      e++;
    }

    if (d < 0) a = -a;

    Object o[] = {new Integer((int)Math.rint(a)), new Integer(e)};

    return Format.sprintf(f, o);

  }

  /**
   * Returns a representation of the double in time format "EEE, d MMM yyyy HH:mm:ss".
   * @param vt number of millisec since epoch
   * @return A string continaing a time representation of the given double.
   */
  public static String formatTimeValue(double vt) {
    java.util.Date date;
    calendar.setTimeInMillis((long) vt);
    date = calendar.getTime();
    return genFormat.format(date);
  }


  /**
   * Sets the appropriate time format for the range to display
   */
  private void computeDateformat(int maxLab) {

    //find optimal precision
    boolean found = false;
    int i = 0;
    while (i < timePrecs.length && !found) {
      int n = (int) ((max - min) / timePrecs[i]);
      found = (n <= maxLab);
      if (!found) i++;
    }

    if (!found) {
      // TODO Year Linear scale
      i--;
      desiredPrec = 10 * YEAR;
      useFormat = yearFormat;
    } else {
      desiredPrec = timePrecs[i];
      useFormat = timeFormats[i];
    }

  }

  /**
   * Customize axis labels.
   * @param labels Label values
   * @param labelPos Label positions (in axis coordinates)
   */
  public void setLabels(String[] labels,double[] labelPos) {

    if(labels == null || labelPos == null) {
      userLabel = null;
      userLabelPos = null;
      autoLabeling = true;
      return;
    }

    if(labels.length != labelPos.length) {
      System.out.println("JLAxis.setLabels() : labels and labelPos must have the same size");
      return;
    }

    userLabel = labels;
    // avoiding NullPointerExceptions
    if (userLabel != null) {
        for (int i = 0; i < userLabel.length; i++) {
            if (userLabel[i] == null) {
                userLabel[i] = "" + null;
            }
        }
    }
    userLabelPos = labelPos;
    autoLabeling = false;

  }

  /**
   * Suppress last non significative zeros
   * @param n String representing a floating number
   */
  private String suppressZero(String n) {

    boolean hasDecimal = n.indexOf('.') != -1;

    if(hasDecimal) {

      StringBuffer str = new StringBuffer(n);
      int i = str.length() - 1;
      while( str.charAt(i)=='0' ) {
        str.deleteCharAt(i);
        i--;
      }
      if(str.charAt(i)=='.') {
        // Remove unwanted decimal
        str.deleteCharAt(i);
      }

      return str.toString();

    } else {
      return n;
    }

  }

  /**
   * Returns a representation of the double acording to the format
   * @param vt double to convert
   * @param prec Desired precision (Pass 0 to not perform prec rounding).
   * @return A string continaing a formated representation of the given double.
   */
  public String formatValue(double vt, double prec) {

    if(Double.isNaN(vt))
      return "NaN";

    // Round value to nearest multiple of prec
    // TODO: rounding in LOG_SCALE
    if (prec != 0 && scale == LINEAR_SCALE) {

      boolean isNegative = (vt < 0.0);
      if(isNegative) vt = -vt;

      // Find multiple
      double i = Math.floor(vt/prec + 0.5d);
      vt = i * prec;

      if(isNegative) vt = -vt;

    }

    switch (labelFormat) {
      case SCIENTIFIC_FORMAT:
        return toScientific(vt);

      case SCIENTIFICINT_FORMAT:
        return toScientificInt(vt);

      case DECINT_FORMAT:
      case HEXINT_FORMAT:
      case BININT_FORMAT:
        Object[] o2 = {new Integer((int) (Math.abs(vt)+0.5))};
        if (vt < 0.0)
          return "-" + Format.sprintf(labelFomats[labelFormat], o2);
        else
          return Format.sprintf(labelFomats[labelFormat], o2);

      case TIME_FORMAT:

        int sec = (int) (Math.abs(vt));
        Object[] o3 = {
          new Integer(sec / 3600),
          new Integer((sec % 3600) / 60),
          new Integer(sec % 60)};

        if (vt < 0.0)
          return "-" + Format.sprintf(labelFomats[labelFormat], o3);
        else
          return Format.sprintf(labelFomats[labelFormat], o3);

      case DATE_FORMAT:
        SimpleDateFormat format = new SimpleDateFormat(dateFormat);
        long millisec = (long) (Math.abs(vt)*1000);
        return format.format(new Date(millisec));

      default:

        // Auto format
        if(vt==0.0) return "0";

        if(Math.abs(vt)<=1.0E-4) {

          return toScientific(vt);

        } else {

          int nbDigit = -(int)Math.floor(Math.log10(prec));
          if( nbDigit<=0 ) {
            return suppressZero(Double.toString(vt));
          } else {
            String dFormat = "%." + nbDigit + "f";
            return suppressZero(Format.sprintf(dFormat,new Object[]{new Double(vt)}));
          }

        }

    }

  }

  private boolean isHorizontal() {
    return (dOrientation == HORIZONTAL_DOWN) ||
      (dOrientation == HORIZONTAL_UP);
  }

  // *****************************************************
  // AutoScaling stuff
  // Expert usage

  private double computeHighTen(double d) {
    int p = (int)Math.log10(d);
    return Math.pow(10.0, p + 1);
  }

  private double computeLowTen(double d) {
    int p = (int)Math.log10(d);
    return Math.pow(10.0, p);
  }

  private void computeAutoScale() {

    int i = 0;
    int sz = dataViews.size();
    double mi = 0,ma = 0;

    if (autoScale && sz > 0) {

      JLDataView v;
      min = Double.MAX_VALUE;
      max = -Double.MAX_VALUE;

      for (i = 0; i < sz; i++) {

        v = dataViews.get(i);

        if (v.hasTransform()) {
          double[] mm = v.computeTransformedMinMax();
          mi = mm[0];
          ma = mm[1];
        } else {
          mi = v.getMinimum();
          ma = v.getMaximum();
        }

        if (scale == LOG_SCALE) {

          if (mi <= 0) mi = v.computePositiveMin();
          if (mi != Double.MAX_VALUE) mi = Math.log(mi) / ln10;

          if (ma <= 0)
            ma = -Double.MAX_VALUE;
          else
            ma = Math.log(ma) / ln10;
        }

        if (ma > max) max = ma;
        if (mi < min) min = mi;

      }

      // Check max and min
      if (min == Double.MAX_VALUE && max == -Double.MAX_VALUE) {

        // Only invalid data !!
        if (scale == LOG_SCALE) {
          min = 0;
          max = 1;
        } else {
          min = 0;
          max = 99.99;
        }

      }
      else if (zeroAlwaysVisible)
      {
        if (min < 0 && max < 0)
        {
          max = 0;
        }
        else if (min > 0 && max > 0)
        {
          min = 0;
        }
      }

      if ((max - min) < 1e-100) {
        max += 0.999;
        min -= 0.999;
      }

      double prec = computeLowTen(max - min);

      // Avoid unlabeled axis when log scale
      if( scale==LOG_SCALE && prec<1.0 )
        prec=1.0;

      //System.out.println("ComputeAutoScale: Prec= " + prec );

      if (min < 0)
        min = ((int) (min / prec) - 1) * prec;
      else
        min = (int) (min / prec) * prec;


      if (max < 0)
        max = (int) (max / prec) * prec;
      else
        max = ((int) (max / prec) + 1) * prec;

      //System.out.println("ComputeAutoScale: " + min + "," + max );

    } // end ( if autoScale )

  }
  /**
   * Expert usage. Sets the preferred scale for time axis (HORIZONTAL axis only)
   * @param d Duration (millisec)
   */
  public void setAxisDuration(double d) {
    axisDuration = d;
  }

  /**
   * Expert usage. Compute X auto scale (HORIZONTAL axis only)
   * @param views All views displayed along all Y axis.
   */
  public void computeXScale(Vector views) {

    int i = 0;
    int sz = views.size();
    double mi,ma;

    if (isHorizontal() && autoScale && sz > 0) {

      if (!isXY()) {

        //******************************************************
        // Classic monitoring

        JLDataView v;
        min = Double.MAX_VALUE;
        max = -Double.MAX_VALUE;

        // Horizontal autoScale

        for (i = 0; i < sz; i++) {

          v = (JLDataView) views.get(i);
	  
          ma = v.getMaxXValue();
          mi = v.getMinXValue();

          if (scale == LOG_SCALE) {
            if (mi <= 0) {
              if (annotation == VALUE_ANNO) {
                mi = v.getPositiveMinXValue();
              }
              else {
                mi = v.getPositiveMinTime();
              }
            }
            if (mi != Double.MAX_VALUE) mi = Math.log(mi) / ln10;

            if (ma <= 0)
              ma = -Double.MAX_VALUE;
            else
              ma = Math.log(ma) / ln10;
          }

          if (ma > max) max = ma;
          if (mi < min) min = mi;

        }


        if (min == Double.MAX_VALUE && max == -Double.MAX_VALUE) {

          // Only empty views !

          if (scale == LOG_SCALE) {

            min = 0;
            max = 1;

          } else {

            if (annotation == TIME_ANNO) {
              min = System.currentTimeMillis() - HOUR;
              max = System.currentTimeMillis();
            } else {
              min = 0;
              max = 99.99;
            }

          }

        }

        if (annotation == TIME_ANNO) {

          if( axisDuration != Double.POSITIVE_INFINITY && fitXAxisToDisplayDuration)
            min = max - axisDuration;

          max += (max - min) * percentScrollback;

        }

        if ((max - min) < 1e-100) {
          max += 0.999;
          min -= 0.999;
        }

      } else {

        //******************************************************
        // XY monitoring
        computeAutoScale();

      }

    }


  }

  // *****************************************************
  // Measurements stuff

  /**
   * @deprecated Use getLabelFontDimension() instead
   */
  public int getFontHeight(Graphics g) {
    return getLabelFontDimension(null);
  }

  /**
   * Expert usage.
   * @return Axis font dimension.
   */
  public int getLabelFontDimension(FontRenderContext frc) {

    if(!visible || frc==null)
      return 5; // 5 pixel margin when axis not visible

    int hFont = (int)(labelFont.getLineMetrics("dummyStr0",frc).getHeight() + 0.5);

    if (isHorizontal()) {

      if (name != null) {
        if( orientation==HORIZONTAL_DOWN || orientation==HORIZONTAL_UP )
          return 2*hFont+5;
        else
          return hFont+5;
      } else {
          return hFont+5;
      }

    } else {
      if (name != null)
        return hFont+5;
      else
        return 5;
    }

  }

  public int getFontOverWidth() {
    return fontOverWidth;
  }

  /**
   * Expert usage.
   * Returns axis tichkness in pixel ( shorter side )
   * @return Axis tichkness
   * @see JLAxis#getLength
   */
  public int getThickness() {
    if ((csize != null) && visible) {
      if (!isHorizontal())
        return csize.width;
      else
        return csize.height;
    }
    return 0;
  }

  /**
   * Expert usage.
   * Returns axis lenght in pixel ( larger side ).
   * @return Axis lenght.
   * @see JLAxis#getThickness
   */
  public int getLength() {
    if (csize != null) {
      if (isHorizontal())
        return csize.width;
      else
        return csize.height;
    }
    return 0;
  }

  /**
   * Expert usage.
   * Computes labels and measures axis dimension.
   * @param frc Font render context
   * @param desiredWidth Desired width
   * @param desiredHeight Desired height
   */
  public void measureAxis(FontRenderContext frc, int desiredWidth, int desiredHeight) {

    int i;
    int max_width = 10; // Minimun width
    int max_height = 0;

    computeAutoScale();

    if(autoLabeling) {
      if(!isHorizontal())
        computeLabels(frc, desiredHeight);
      else
        computeLabels(frc, desiredWidth);
    } else {
      if(!isHorizontal())
        computeUserLabels(frc, desiredHeight);
      else
        computeUserLabels(frc, desiredWidth);
    }

    for (i = 0; i < labels.size(); i++) {
      LabelInfo li = labels.get(i);
      if (li.getWidth() > max_width)
        max_width = li.getWidth();
      if (li.getHeight() > max_height)
        max_height = li.getHeight();
    }

    fontOverWidth = max_width/2+1;

    if (!isHorizontal())
      csize = new Dimension(max_width + getLabelFontDimension(frc), desiredHeight);
    else
      csize = new Dimension(desiredWidth, max_height);

  }

  // ****************************************************************
  //	search nearest point stuff

  /**
   * Expert usage.
   * Transfrom given coordinates (real space) into pixel coordinates
   * @param x The x coordinates (Real space)
   * @param y The y coordinates (Real space)
   * @param xAxis The axis corresponding to x coordinates.
   * @return Point(-100,-100) when cannot transform
   */
  public Point transform(double x, double y, JLAxis xAxis) {

    // The graph must have been measured before
    // we can transform
    if (csize == null) return new Point(-100, -100);

    double xlength = (xAxis.getMax() - xAxis.getMin());
    int xOrg = boundRect.x;
    int yOrg = boundRect.y + getLength();
    double vx,vy;

    // Check validity
    if (Double.isNaN(y) || Double.isNaN(x))
      return new Point(-100, -100);

    if (xAxis.getScale() == LOG_SCALE) {
      if (x <= 0)
        return new Point(-100, -100);
      else
        vx = Math.log(x) / ln10;
    } else
      vx = x;

    if (scale == LOG_SCALE) {
      if (y <= 0)
        return new Point(-100, -100);
      else
        vy = Math.log(y) / ln10;

    } else
      vy = y;

    double xratio = (vx - xAxis.getMin()) / (xlength) * (xAxis.getLength());
    double yratio = -(vy - min) / (max - min) * csize.height;

    // Saturate
    if (xratio < -32000) xratio = -32000;
    if (xratio > 32000) xratio = 32000;
    if (yratio < -32000) yratio = -32000;
    if (yratio > 32000) yratio = 32000;

    return new Point((int) (xratio) + xOrg, (int) (yratio) + yOrg);

  }

  //Return the square distance
  private int distance2(int x1, int y1, int x2, int y2) {
    return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
  }

  /** Expert usage.
   * Search the nearest point in the dataViews in normal monitoring mode
   * @param x The x coordinates (Real space)
   * @param y The y coorsinates (Real space)
   * @param xAxis The axis corresponding to x coordinates.
   * @return A structure containing search result.
   * @see JLAxis#searchNearestXY
   */
  public SearchInfo searchNearestNormal(int x, int y, JLAxis xAxis) {

    int sz = dataViews.size();
    int idx = 0;
    int norme2;
    DataList minP = null;
    Point minPt = null;
    int minNorme = Integer.MAX_VALUE;
    JLDataView minDataView = null;
    int minPl = 0;
    int minIdx = -1;

    Rectangle boundRect2 = new Rectangle();
    boundRect2.setBounds(boundRect.x - 2, boundRect.y - 2, boundRect.width + 4, boundRect.height + 4);

    for (int i = 0; i < sz; i++) {

      JLDataView v = dataViews.get(i);
      if (v.isClickable()) {
        DataList e = v.getData();

        idx = 0;
        while (e != null) {

          Point p = transform(e.x, v.getTransformedValue(e.y), xAxis);

          if (boundRect2.contains(p)) {
            norme2 = distance2(x, y, p.x, p.y);
            if (norme2 < minNorme) {

              minNorme = norme2;
              minP = e;
              minDataView = v;
              minPt = p;
              minIdx = idx;

              // Compute placement for the value info window
              if (p.x < (boundRect.x + boundRect.width / 2)) {
                if (p.y < (boundRect.y + boundRect.height / 2)) {
                  minPl = SearchInfo.BOTTOMRIGHT;
                } else {
                  minPl = SearchInfo.TOPRIGHT;
                }
              } else {
                if (p.y < (boundRect.y + boundRect.height / 2)) {
                  minPl = SearchInfo.BOTTOMLEFT;
                } else {
                  minPl = SearchInfo.TOPLEFT;
                }
              }
            }
          }

          e = e.next;
          idx++;

        }
      }
    }

    if (minNorme == Integer.MAX_VALUE)
      return new SearchInfo(); //No item found
    else
      return new SearchInfo(minPt.x, minPt.y, minDataView, this, minP, minNorme, minPl,minIdx);
  }

  /** Expert usage.
   * Search the nearest point in the dataViews in XY monitoring mode
   * @param x The x coordinates (Real space)
   * @param y The y coorsinates (Real space)
   * @param xAxis The axis corresponding to x coordinates.
   * @return A structure containing search result.
   * @see JLAxis#searchNearestNormal
   */

  public SearchInfo searchNearestXY(int x, int y, JLAxis xAxis) {

    int sz = dataViews.size();
    int norme2;
    DataList minP = null;
    DataList minXP = null;
    Point minPt = null;
    int minNorme = Integer.MAX_VALUE;
    JLDataView minDataView = null;
    int minPl = 0;

    JLDataView w = xAxis.getViews().get(0);

    Rectangle boundRect2 = new Rectangle();
    boundRect2.setBounds(boundRect.x - 2, boundRect.y - 2, boundRect.width + 4, boundRect.height + 4);

    for (int i = 0; i < sz; i++) {

      JLDataView v = dataViews.get(i);
      if (v.isClickable()) {
        XYData e = new XYData(v.getData(), w.getData());

        if (e.isValid()) e.initFirstPoint();

        while (e.isValid()) {

          Point p = transform(w.getTransformedValue(e.d2.y), v.getTransformedValue(e.d1.y), xAxis);

          if (boundRect2.contains(p)) {
            norme2 = distance2(x, y, p.x, p.y);
            if (norme2 < minNorme) {

              minNorme = norme2;
              minP = e.d1;
              minXP = e.d2;
              minDataView = v;
              minPt = p;

              // Compute placement for the value info window
              if (p.x < (boundRect.x + boundRect.width / 2)) {
                if (p.y < (boundRect.y + boundRect.height / 2)) {
                  minPl = SearchInfo.BOTTOMRIGHT;
                } else {
                  minPl = SearchInfo.TOPRIGHT;
                }
              } else {
                if (p.y < (boundRect.y + boundRect.height / 2)) {
                  minPl = SearchInfo.BOTTOMLEFT;
                } else {
                  minPl = SearchInfo.TOPLEFT;
                }
              }
            }
          }

          e.toNextXYPoint();

        }
      }

    }

    if (minNorme == Integer.MAX_VALUE)
      return new SearchInfo(); //No item found
    else {
      SearchInfo si = new SearchInfo(minPt.x, minPt.y, minDataView, this, minP, minNorme, minPl,-1);
      si.setXValue(minXP, w);
      return si;
    }

  }

  /**
   * Search the nearest point in the dataViews.
   * @param x The x coordinates (Real space)
   * @param y The y coordinates (Real space)
   * @param xAxis The axis corresponding to x coordinates.
   * @return A structure containing search result.
   */
  public SearchInfo searchNearest(int x, int y, JLAxis xAxis) {

    //Search only in graph area
    if( x<=boundRect.x-10 ||
        x>=boundRect.x+boundRect.width+10 ||
        y<=boundRect.y-10 ||
        y>=boundRect.y+boundRect.height+10
      ) {
      return new SearchInfo();
    }

    if (xAxis.isXY()) {
      return searchNearestXY(x, y, xAxis);
    } else {
      return searchNearestNormal(x, y, xAxis);
    }


  }

  private void computeUserLabels(FontRenderContext frc,double length) {

    double sz = max - min;
    double precDelta = sz / length;

    labels.clear();

    //Adjust labels offset according to tick

    int offX = 0;
    int offY = 0;
    switch(dOrientation) {
      case VERTICAL_LEFT:
        offX = (tickLength<0)?tickLength:0;
        break;
      case VERTICAL_RIGHT:
        offX = (tickLength<0)?-tickLength:0;
        break;
      default: // HORIZONTAL_DOWN
        offY = (tickLength<0)?-tickLength:0;
        break;
    }

    // Create labels

    for(int i=0;i<userLabel.length;i++) {

      double upos;
      if(scale==LOG_SCALE)
        upos = Math.log10(userLabelPos[i]);
      else
        upos = userLabelPos[i];

      if(upos>=(min - precDelta) && upos<=(max + precDelta)) {

          int pos;

          if (inverted)
            pos = (int)Math.rint(length * (1.0 - (upos - min) / sz));
          else
            pos = (int)Math.rint(length * ((upos - min) / sz));

          Rectangle2D bounds = labelFont.getStringBounds(userLabel[i], frc);
          LabelInfo li = new LabelInfo(userLabel[i], (int) bounds.getWidth(),
                                       (int) bounds.getHeight(), pos);
          li.setOffset(offX,offY);
          labels.add(li);

      }

    }

  }

  // ****************************************************************
  // Compute labels
  // Expert usage
  private void computeLabels(FontRenderContext frc, double length) {

    // XXX Vincent Hardion max < min ???
    if (max < min) {
//      StringBuffer errorBuffer = new StringBuffer("Error found in JLAxis");
//      errorBuffer.append("\nMethod computeLabels(FontRenderContext,double)");
//      errorBuffer.append("\nmax < min : ");
//      errorBuffer.append("max = ").append(max);
//      errorBuffer.append(", min = ").append(min);
//      errorBuffer.append("\nInverting min and max values to avoid problems");
//      System.err.println( errorBuffer.toString() );
   	  double a = min;
   	  min=max;
   	  max=a;
    }

    double sz = max - min;
    double pos;
    int w,h;
    int lgth = (int) length;
    java.util.Date date;
    String s;
    double startx;
    double prec;
    double precDelta = sz / length;

    labels.clear();
    Rectangle2D bounds;

    switch (annotation) {

      case TIME_ANNO:

        // Only for HORINZONTAL axis !
        // This has nothing to do with TIME_FORMAT
        // 10 labels maximum should be enough...
        computeDateformat(10);

        // round to multiple of prec
        long round;
        round = (long) (min / desiredPrec);
        startx = (round + 1) * desiredPrec;

        if (inverted)
          pos = length * (1.0 - (startx - min) / sz);
        else
          pos = length * ((startx - min) / sz);

        calendar.setTimeInMillis((long) startx);
        date = calendar.getTime();
        s = useFormat.format(date);
        bounds = labelFont.getStringBounds(s, frc);
        w = (int) bounds.getWidth();
        h = (int) bounds.getHeight();
        labels.add(new LabelInfo(s, w, h, pos));

        double minStep = (double) w * 1.3;
        if(minStep<minTickStep) minStep = minTickStep;
        double minPrec = (minStep / length) * sz;

        // Correct to avoid label overlap
        prec = desiredPrec;
        while (prec < minPrec) prec += desiredPrec;

        tickStep = length * prec/sz;
        startx += prec;
        if(inverted) tickStep = -tickStep;
        subTickStep = 0;

        // Build labels
        while (startx <= (max + precDelta)) {

          if (inverted)
            pos = (int)Math.rint(length * (1.0 - (startx - min) / sz));
          else
            pos = (int)Math.rint(length * ((startx - min) / sz));

          calendar.setTimeInMillis((long) startx);
          date = calendar.getTime();
          s = useFormat.format(date);
          bounds = labelFont.getStringBounds(s, frc);

          // Check limit
          if (pos > 0 && pos < lgth) {
            w = (int) bounds.getWidth();
            h = (int) bounds.getHeight();
            labels.add(new LabelInfo(s, w, h, pos));
          }

          startx += prec;

        }
        break;

      case VALUE_ANNO:

        double fontAscent = (double) (labelFont.getLineMetrics("0",frc).getAscent());
        prec = computeLowTen(max - min);
        boolean extractLabel = false;

        // Anticipate label overlap

        int nbMaxLab;

        if(!isHorizontal()) {

          // VERTICAL
          nbMaxLab = (int) (length / (2.0*fontAscent));

        } else {

          // HORIZONTAL
          // The strategy is not obvious here as we can't estimate the max label width
          // Do it with the min and the max
          double minT;
          double maxT;
          if (scale == LOG_SCALE) {
            minT = Math.pow(10.0, min);
            maxT = Math.pow(10.0, max);
          } else {
            minT = min;
            maxT = max;
          }

          double mW;
          s = formatValue(minT, prec);
          bounds = labelFont.getStringBounds(s, frc);
          mW = bounds.getWidth();
          s = formatValue(maxT, prec);
          bounds = labelFont.getStringBounds(s, frc);
          if(bounds.getWidth()>mW) mW = bounds.getWidth();
          mW = 1.5*mW;
          nbMaxLab = (int) (length / mW);

        }

        int n;
        int step = 0;
        int subStep = 0;

        // Overrides maxLab
        int userMaxLab = (int)Math.rint(length / minTickStep);
        if (userMaxLab<nbMaxLab) nbMaxLab = userMaxLab;

        if (nbMaxLab<1) nbMaxLab=1; // At least 1 labels !

        // Find the best precision

        if (scale == LOG_SCALE) {

          prec = 1;   // Decade
          step = -1;  // Logarithm subgrid

          startx = Math.rint(min);

          n = (int)Math.rint((max - min) / prec);

          while (n > nbMaxLab) {
            prec = prec * 2;
            step = 2;
            n = (int)Math.rint((max - min) / prec);
            if (n > nbMaxLab) {
              prec = prec * 5;
              step = 10;
              n = (int)Math.rint((max - min) / prec);
            }
          }

          subStep = step;

        } else {

          // Linear scale

          step = 10;
          n = (int)Math.rint((max - min) / prec);

          if (n <= nbMaxLab) {

            // Look forward
            n = (int)Math.rint((max - min) / (prec / 2.0));

            while (n <= nbMaxLab) {
              prec = prec / 2.0;
              step = 5;
              n = (int)Math.rint((max - min) / (prec / 5.0));
              if (n <= nbMaxLab) {
                prec = prec / 5.0;
                step = 10;
                n = (int)Math.rint((max - min) / (prec / 2.0));
              }
            }

          } else {

            // Look backward
            while(n>nbMaxLab) {
              prec = prec * 5.0;
              step = 5;
              n = (int)Math.rint((max - min) / prec);
              if(n>nbMaxLab) {
                prec = prec * 2.0;
                step = 10;
                n = (int)Math.rint((max - min) / prec);
              }
            }

          }

          // round to multiple of prec (last not visible label)

          round = (long)Math.floor(min / prec);
          startx = round * prec;

          // Compute real number of label

          double sx = startx;
          int nbL = 0;
          while(sx<=(max + precDelta)) {
            if( sx >= (min - precDelta)) {
              nbL++;
            }
            sx += prec;
          }

          if(nbL<=2) {
            // Only one label
            // Go backward and extract the 2 extremity
            if(step==10) {
              step=5;
              prec=prec/2.0;
            } else {
              step=10;
              prec=prec/5.0;
            }
            extractLabel = true;
          }

          // Compute tick sapcing

          double tickSpacing = Math.abs(((prec / sz)*length) / (double)step);
          subStep = step;
          while(tickSpacing<10.0 && subStep>1) {
            switch (subStep) {
              case 10:
               subStep = 5;
               tickSpacing = tickSpacing * 2;
               break;
              case 5:
               subStep = 2;
               tickSpacing = tickSpacing * 2.5;
               break;
              case 2:
               // No sub tick
               subStep = 1;
               break;
            }
          }


        }

        // Compute tickStep

        tickStep = length * prec/sz;
        if(inverted) tickStep = -tickStep;
        subTickStep = subStep;

        //Adjust labels offset according to tick

        int offX = 0;
        int offY = 0;
        switch(dOrientation) {
          case VERTICAL_LEFT:
            offX = (tickLength<0)?tickLength:0;
            break;
          case VERTICAL_RIGHT:
            offX = (tickLength<0)?-tickLength:0;
            break;
          default: // HORIZONTAL_DOWN
            offY = (tickLength<0)?-tickLength:0;
            break;
        }

        //Build labels

        String lastLabelText = "";
        double lastDiff = Double.MAX_VALUE;
        LabelInfo lastLabel = null;
        while (startx <= (max + precDelta)) {

          if (inverted)
            pos = (int)Math.rint(length * (1.0 - (startx - min) / sz));
          else
            pos = (int)Math.rint(length * ((startx - min) / sz));

          double vt;
          if (scale == LOG_SCALE)
            vt = Math.pow(10.0, startx);
          else
            vt = startx;

          String tempValue = formatValue(vt, prec);
          double diff = 0;
          if (labelFormat != TIME_FORMAT && labelFormat != DATE_FORMAT)
          {
              diff = Math.abs(Double.parseDouble(tempValue) - vt);
          }
          if (lastLabelText.equals(tempValue))
          {
            //avoiding label duplication
            if (diff < lastDiff)
            {
              s = new String(tempValue);
              if (lastLabel != null)
              {
                lastLabel.value = "";
              }
            }
            else
            {
              s = "";
            }
          }
          else
          {
            s = new String(tempValue);
          }
          lastDiff = diff;
          lastLabelText = new String(tempValue);
          bounds = labelFont.getStringBounds(s, frc);

          if (startx >= (min - precDelta)) {
            LabelInfo li = new LabelInfo(s, (int) bounds.getWidth(), (int) fontAscent, pos);
            li.setOffset(offX,offY);
            labels.add(li);
            lastLabel = li;
          }

          startx += prec;

        }

        // Extract 2 bounds when we didn't found a correct match.
        if(extractLabel) {
          if(labels.size()>2) {
            Vector<LabelInfo> nLabels = new Vector<LabelInfo>();
            LabelInfo lis = labels.get(0);
            LabelInfo lie = labels.get(labels.size()-1);
            nLabels.add(lis);
            nLabels.add(lie);
            tickStep = lie.pos - lis.pos;
            subTickStep = labels.size()-1;
            labels = nLabels;
          }
        }

        break;

    }

  }

  // ****************************************************************
  // Painting stuff

  /** Expert Usage.
   * Paint last point of a dataView.
   * @param g Graphics object
   * @param lp last point
   * @param p new point
   * @param v view containing the lp and p.
   */
  public void drawFast(Graphics g, Point lp, Point p, JLDataView v) {

    if (lp != null) {
      if (boundRect.contains(lp)) {

        Graphics2D g2 = (Graphics2D) g;
        Stroke old = g2.getStroke();
        BasicStroke bs = GraphicsUtils.createStrokeForLine(v.getLineWidth(), v.getStyle());
        if (bs != null) g2.setStroke(bs);

        // Draw
        g.setColor(v.getColor());
        g.drawLine(lp.x, lp.y, p.x, p.y);

        //restore default stroke
        g2.setStroke(old);
      }
    }

    //Paint marker
    Color oc = g.getColor();
    g.setColor(v.getMarkerColor());
    paintMarker(g, v.getMarker(), v.getMarkerSize(), p.x, p.y);
    g.setColor(oc);

  }

  /** Expert usage.
   * Paint a marker a the specified position
   * @param g Graphics object
   * @param mType Marker type
   * @param mSize Marker size
   * @param x x coordinates (pixel space)
   * @param y y coordinates (pixel space)
   */
  public static void paintMarker(Graphics g, int mType, int mSize, int x, int y) {

    int mSize2 = mSize / 2;
    int mSize21 = mSize / 2 + 1;

    switch (mType) {
      case JLDataView.MARKER_DOT:
        g.fillOval(x - mSize2, y - mSize2, mSize, mSize);
        break;
      case JLDataView.MARKER_BOX:
        g.fillRect(x - mSize2, y - mSize2, mSize, mSize);
        break;
      case JLDataView.MARKER_TRIANGLE:
        triangleShape.translate(x, y);
        g.fillPolygon(triangleShape);
        triangleShape.translate(-x, -y);
        break;
      case JLDataView.MARKER_DIAMOND:
        diamondShape.translate(x, y);
        g.fillPolygon(diamondShape);
        diamondShape.translate(-x, -y);
        break;
      case JLDataView.MARKER_STAR:
        g.drawLine(x - mSize2, y + mSize2, x + mSize21, y - mSize21);
        g.drawLine(x + mSize2, y + mSize2, x - mSize21, y - mSize21);
        g.drawLine(x, y - mSize2, x, y + mSize21);
        g.drawLine(x - mSize2, y, x + mSize21, y);
        break;
      case JLDataView.MARKER_VERT_LINE:
        g.drawLine(x, y - mSize2, x, y + mSize21);
        break;
      case JLDataView.MARKER_HORIZ_LINE:
        g.drawLine(x - mSize2, y, x + mSize21, y);
        break;
      case JLDataView.MARKER_CROSS:
        g.drawLine(x, y - mSize2, x, y + mSize21);
        g.drawLine(x - mSize2, y, x + mSize21, y);
        break;
      case JLDataView.MARKER_CIRCLE:
        g.drawOval(x - mSize2, y - mSize2, mSize + 1, mSize + 1);
        break;
      case JLDataView.MARKER_SQUARE:
        g.drawRect(x - mSize2, y - mSize2, mSize, mSize);
        break;
    }

  }

  private void paintBarBorder(Graphics g, int barWidth, int y0, int x, int y) {
    g.drawLine(x - barWidth / 2, y, x + barWidth / 2, y);
    g.drawLine(x + barWidth / 2, y, x + barWidth / 2, y0);
    g.drawLine(x + barWidth / 2, y0, x - barWidth / 2, y0);
    g.drawLine(x - barWidth / 2, y0, x - barWidth / 2, y);
  }

  private void paintBar(Graphics g, Paint pattern, int barWidth, Color background, int fillStyle, int y0, int x, int y) {

    Graphics2D g2 = (Graphics2D) g;

    if (fillStyle != JLDataView.FILL_STYLE_NONE) {
      if (pattern != null) g2.setPaint(pattern);
      else                 g2.setColor(background);
      if (y > y0) {
        g.fillRect(x - barWidth / 2, y0, barWidth, y-y0);
      } else {
        g.fillRect(x - barWidth / 2, y, barWidth, (y0 - y));
      }
    }

  }

  /** Expert usage.
   * Draw a sample line of a dataview
   * @param g Graphics object
   * @param x x coordinates (pixel space)
   * @param y y coordinates (pixel space)
   * @param v dataview
   */
  public static void drawSampleLine(Graphics g, int x, int y, JLDataView v) {

    Graphics2D g2 = (Graphics2D) g;
    Stroke old = g2.getStroke();
    BasicStroke bs = GraphicsUtils.createStrokeForLine(v.getLineWidth(), v.getStyle());
    if (bs != null) g2.setStroke(bs);

    // Draw
    g.drawLine(x, y, x + 40, y);

    //restore default stroke
    g2.setStroke(old);

    //Paint marker
    Color oc = g.getColor();
    g.setColor(v.getMarkerColor());
    paintMarker(g, v.getMarker(), v.getMarkerSize(), x + 20, y);
    g.setColor(oc);

  }

  //   Expert usage
  //  Paint dataviews along the given axis
  //  xAxis horizonbtal axis of the graph
  //  xOrg x origin (pixel space)
  //  yOrg y origin (pixel space)
  void paintDataViews(Graphics g, JLAxis xAxis, int xOrg, int yOrg) {

    int nbView = dataViews.size();
    int k;
    boolean isXY = xAxis.isXY();
    JLDataView vx = null;

    //-------- Clipping

    int xClip = xOrg + 1;
    int yClip = yOrg - getLength() + 1;
    int wClip = xAxis.getLength() - 1;
    int hClip = getLength() - 1;

    if (wClip <= 1 || hClip <= 1) return;
    g.clipRect(xClip, yClip, wClip, hClip);

    //-------- Draw dataView
    if (isXY) vx = xAxis.getViews().get(0);

    for (k = 0; k < nbView; k++) {

      JLDataView v = dataViews.get(k);

      if (isXY)
        paintDataViewXY(g, v, vx, xAxis, xOrg, yOrg);
      else
        paintDataViewNormal(g, v, xAxis, xOrg, yOrg);

    } // End (for k<nbView)

  }

  // Paint dataviews along the given axis
  // Expert usage

  private int computeBarWidth(JLDataView v, JLAxis xAxis) {

    int defaultWidth = 20;
    double minx = xAxis.getMin();
    double maxx = xAxis.getMax();
    int bw = v.getBarWidth();
    double minI = Double.MAX_VALUE;


    // No auto scale
    if (bw > 0)
      return bw;

    // No autoScale when horizontal axis is logarithmic
    if (xAxis.getScale() == LOG_SCALE)
      return defaultWidth;


    if (xAxis.isXY()) {

      JLDataView vx = xAxis.getViews().get(0);

      // Look for the minimun interval
      DataList d = vx.getData();
      if (d != null) {
        double x = d.y;
        d = d.next;
        while (d != null) {
          double diff = Math.abs(d.y - x);
          if (diff < minI) minI = diff;
          x = d.y;
          d = d.next;
        }
      }

    } else {

      // Look for the minimun interval
      DataList d = v.getData();
      if (d != null) {
        double x = d.x;
        d = d.next;
        while (d != null) {
          double diff = Math.abs(d.x - x);
          if (diff < minI) minI = diff;
          x = d.x;
          d = d.next;
        }
      }

    }

    if (minI == Double.MAX_VALUE)
      return defaultWidth;

    bw = (int) Math.floor(minI / (maxx - minx) * xAxis.getLength()) - 2;

    // Make width multiple of 2 and saturate
    bw = bw / 2;
    bw = bw * 2;
    if (bw < 0) bw = 0;

    return bw;
  }

  private void paintDataViewBar(Graphics2D g2,
                                JLDataView v,
                                int barWidth,
                                BasicStroke bs,
                                Paint fPattern,
                                int y0,
                                int x,
                                int y) {

    if (v.getViewType() == JLDataView.TYPE_BAR) {

      paintBar(g2,
        fPattern,
        barWidth,
        v.getFillColor(),
        v.getFillStyle(),
        y0,
        x,
        y);

      // Draw bar border
      if (v.getLineWidth() > 0) {
        Stroke old = g2.getStroke();
        if (bs != null) g2.setStroke(bs);
        g2.setColor(v.getColor());
        paintBarBorder(g2, barWidth, y0, x, y);
        g2.setStroke(old);
      }

    }

  }

  private void paintDataViewPolyline(Graphics2D g2,
                                     JLDataView v,
                                     BasicStroke bs,
                                     Paint fPattern,
                                     int nb,
                                     int yOrg,
                                     int[] pointX,
                                     int[] pointY) {

    if (nb > 1 && v.getViewType() == JLDataView.TYPE_LINE) {

      // Draw surface
      if (v.getFillStyle() != JLDataView.FILL_STYLE_NONE) {
        int[] Xs = new int[nb + 2];
        int[] Ys = new int[nb + 2];
        for (int i = 0; i < nb; i++) {
          Xs[i + 1] = pointX[i];
          Ys[i + 1] = pointY[i];
        }
        Xs[0] = Xs[1];
        Ys[0] = yOrg;
        Xs[nb + 1] = Xs[nb];
        Ys[nb + 1] = yOrg;
        if (fPattern != null) g2.setPaint(fPattern);
        g2.fillPolygon(Xs, Ys, nb + 2);
      }

      if (v.getLineWidth() > 0) {
        Stroke old = g2.getStroke();
        if (bs != null) g2.setStroke(bs);
        g2.setColor(v.getColor());
        g2.drawPolyline(pointX, pointY, nb);
        g2.setStroke(old);
      }
    }

  }

  private void paintDataViewNormal(Graphics g, JLDataView v, JLAxis xAxis, int xOrg, int yOrg) {

    DataList l = v.getData();

    if (l != null) {

      // Get some variables

      int nbPoint = v.getDataLength();
      int pointX[] = new int[nbPoint];
      int pointY[] = new int[nbPoint];

      double minx,maxx,lx;
      double miny,maxy,ly;
      double xratio;
      double yratio;
      double vt;
      double A0 = v.getA0();
      double A1 = v.getA1();
      double A2 = v.getA2();
      int y0;

      minx = xAxis.getMin();
      maxx = xAxis.getMax();
      lx = xAxis.getLength();
      int sx = xAxis.getScale();

      miny = min;
      maxy = max;
      ly = getLength();


      int j = 0;
      boolean valid = true;

      // Set the stroke mode for dashed line

      Graphics2D g2 = (Graphics2D) g;
      BasicStroke bs = GraphicsUtils.createStrokeForLine(v.getLineWidth(), v.getStyle());

      // Create the filling pattern
      Paint fPattern = GraphicsUtils.createPatternForFilling(v.getFillStyle(), v.getFillColor(), v.getColor());

      // Compute zero vertical offset
      switch (v.getFillMethod()) {
        case JLDataView.METHOD_FILL_FROM_TOP:
          y0 = yOrg - (int) ly;
          break;
        case JLDataView.METHOD_FILL_FROM_ZERO:
          if (scale == LOG_SCALE)
            y0 = yOrg;
          else
            y0 = (int) (miny / (maxy - miny) * ly) + yOrg;
          break;
        default:
          y0 = yOrg;
          break;
      }

      int barWidth = computeBarWidth(v, xAxis);

      while (l != null) {

        while (valid && l != null) {

          // Compute transform here for performance
          vt = A0 + A1 * l.y + A2 * l.y * l.y;
          valid = !Double.isNaN(vt) && (sx != LOG_SCALE || l.x > 1e-100)
            && (scale != LOG_SCALE || vt > 1e-100);

          if (valid) {

            if (sx == LOG_SCALE)
              xratio = (Math.log(l.x) / ln10 - minx) / (maxx - minx) * lx;
            else
              xratio = (l.x - minx) / (maxx - minx) * lx;

            if (scale == LOG_SCALE)
              yratio = -(Math.log(vt) / ln10 - miny) / (maxy - miny) * ly;
            else
              yratio = -(vt - miny) / (maxy - miny) * ly;

            // Saturate
            if (xratio < -32000) xratio = -32000;
            if (xratio > 32000) xratio = 32000;
            if (yratio < -32000) yratio = -32000;
            if (yratio > 32000) yratio = 32000;

            if (j < nbPoint) {
              pointX[j] = (int) (xratio) + xOrg;
              pointY[j] = (int) (yratio) + yOrg;

              // Draw marker
              if (v.getMarker() > JLDataView.MARKER_NONE) {
                g.setColor(v.getMarkerColor());
                paintMarker(g, v.getMarker(), v.getMarkerSize(), pointX[j], pointY[j]);
              }

              // Draw bar
              paintDataViewBar(g2, v, barWidth, bs, fPattern, y0, pointX[j], pointY[j]);

              j++;
            }

            l = l.next;
          }

        }

        // Draw the polyline
        paintDataViewPolyline(g2, v, bs, fPattern, j, y0, pointX, pointY);

        j = 0;
        if (!valid) {
          l = l.next;
          valid = true;
        }

      } // End (while l!=null)

    } // End (if l!=null)

  }

  // Paint dataviews along the given axis in XY mode
  // Expert usage
  private void paintDataViewXY(Graphics g, JLDataView v, JLDataView w, JLAxis xAxis, int xOrg, int yOrg) {

    XYData l = new XYData(v.getData(), w.getData());

    if (l.isValid()) {

      int nbPoint = v.getDataLength() + w.getDataLength(); // Max number of point

      int pointX[] = new int[nbPoint];
      int pointY[] = new int[nbPoint];

      // Transform points

      double minx,maxx,lx;
      double miny,maxy,ly;
      double xratio;
      double yratio;
      double vtx;
      double vty;
      double A0y = v.getA0();
      double A1y = v.getA1();
      double A2y = v.getA2();
      double A0x = w.getA0();
      double A1x = w.getA1();
      double A2x = w.getA2();

      minx = xAxis.getMin();
      maxx = xAxis.getMax();
      lx = xAxis.getLength();
      int sx = xAxis.getScale();

      miny = min;
      maxy = max;
      ly = getLength();
      int y0;

      int j = 0;
      boolean valid = true;

      // Compute zero vertical offset
      switch (v.getFillMethod()) {
        case JLDataView.METHOD_FILL_FROM_TOP:
          y0 = yOrg - (int) ly;
          break;
        case JLDataView.METHOD_FILL_FROM_ZERO:
          if (scale == LOG_SCALE)
            y0 = yOrg;
          else
            y0 = (int) (miny / (maxy - miny) * ly) + yOrg;
          break;
        default:
          y0 = yOrg;
          break;
      }

      // Set the stroke mode for dashed line
      Graphics2D g2 = (Graphics2D) g;
      BasicStroke bs = GraphicsUtils.createStrokeForLine(v.getLineWidth(), v.getStyle());

      // Create the filling pattern
      Paint fPattern = GraphicsUtils.createPatternForFilling(v.getFillStyle(), v.getFillColor(), v.getColor());

      int barWidth = computeBarWidth(v, xAxis);

      while (l.isValid()) {

        // Go to starting time position
        l.initFirstPoint();

        while (valid && l.isValid()) {

          // Compute transform here for performance
          vty = A0y + A1y * l.d1.y + A2y * l.d1.y * l.d1.y;
          vtx = A0x + A1x * l.d2.y + A2x * l.d2.y * l.d2.y;

          valid = !Double.isNaN(vtx) && !Double.isNaN(vty) &&
            (sx != LOG_SCALE || vtx > 1e-100) &&
            (scale != LOG_SCALE || vty > 1e-100);

          if (valid) {

            if (sx == LOG_SCALE)
              xratio = (Math.log(vtx) / ln10 - minx) / (maxx - minx) * lx;
            else
              xratio = (vtx - minx) / (maxx - minx) * lx;

            if (scale == LOG_SCALE)
              yratio = -(Math.log(vty) / ln10 - miny) / (maxy - miny) * ly;
            else
              yratio = -(vty - miny) / (maxy - miny) * ly;

            // Saturate
            if (xratio < -32000) xratio = -32000;
            if (xratio > 32000) xratio = 32000;
            if (yratio < -32000) yratio = -32000;
            if (yratio > 32000) yratio = 32000;
            if (j < nbPoint) {
              pointX[j] = (int) (xratio) + xOrg;
              pointY[j] = (int) (yratio) + yOrg;

              // Draw marker
              if (v.getMarker() > JLDataView.MARKER_NONE) {
                g.setColor(v.getMarkerColor());
                paintMarker(g, v.getMarker(), v.getMarkerSize(), pointX[j], pointY[j]);
              }

              // Draw bar
              paintDataViewBar(g2, v, barWidth, bs, fPattern, y0, pointX[j], pointY[j]);

              j++;
            }
            // Go to next pos
            l.toNextXYPoint();
          }

        }

        // Draw the polyline
        paintDataViewPolyline(g2, v, bs, fPattern, j, y0, pointX, pointY);

        j = 0;
        if (!valid) {
          // Go to next pos
          l.toNextXYPoint();
          valid = true;
        }

      } // End (while l!=null)

    } // End (if l!=null)

  }

  // Paint sub tick outside label limit
  // Expert usage
  private void paintYOutTicks(Graphics g, int x0, double ys, int y0, int la, BasicStroke bs, int tr,int off,boolean grid) {

    int j,h;
    Graphics2D g2 = (Graphics2D) g;
    Stroke old = g2.getStroke();

    if (subtickVisible) {

      if (subTickStep == -1) {

        for (j = 0; j < logStep.length; j++) {
          h = (int)Math.rint(ys + tickStep * logStep[j]);
          if (h >= y0 && h <= (y0 + csize.height)) {
            g.drawLine(x0 + tr + off , h, x0 + tr + off + subtickLength, h);
            if (gridVisible && subGridVisible && grid) {
              if (bs != null) g2.setStroke(bs);
              g.drawLine(x0, h, x0 + la, h);
              g2.setStroke(old);
            }
          }
        }

      } else if (subTickStep > 0) {

        double r = 1.0 / (double)subTickStep;
        for (j = 0; j < subTickStep; j ++) {
          h = (int)Math.rint(ys + tickStep * r * j);
          if (h >= y0 && h <= (y0 + csize.height)) {
            g.drawLine(x0 + tr + off, h, x0 + tr + off + subtickLength, h);
            if ((j > 0) && gridVisible && subGridVisible && grid) {
              if (bs != null) g2.setStroke(bs);
              g.drawLine(x0, h, x0 + la, h);
              g2.setStroke(old);
            }
          }
        }

      }


    }

  }

  // Paint sub tick outside label limit
  // Expert usage
  private void paintXOutTicks(Graphics g, int y0, double xs, int x0, int la, BasicStroke bs, int tr,int off,boolean grid) {

    int j,w;
    Graphics2D g2 = (Graphics2D) g;
    Stroke old = g2.getStroke();

    if (subtickVisible) {

      if (subTickStep == -1) {

        for (j = 0; j < logStep.length; j++) {
          w = (int)Math.rint(xs + tickStep * logStep[j]);
          if (w >= x0 && w <= (x0 + csize.width)) {
            g.drawLine(w, y0 + tr + off, w, y0 + tr + off + subtickLength);
            if (gridVisible && subGridVisible && grid) {
              if (bs != null) g2.setStroke(bs);
              g.drawLine(w, y0, w, y0 + la);
              g2.setStroke(old);
            }
          }
        }

      } else if (subTickStep > 0) {

        double r = 1.0 / (double)subTickStep;
        for (j = 0; j < subTickStep; j ++) {
          w = (int)Math.rint(xs + tickStep * r * j);
          if (w >= x0 && w <= (x0 + csize.width)) {
            g.drawLine(w, y0 + tr + off, w, y0 + tr + off + subtickLength);
            if ((j > 0) && gridVisible && subGridVisible && grid) {
              if (bs != null) g2.setStroke(bs);
              g.drawLine(w, y0, w, y0 + la);
              g2.setStroke(old);
            }
          }
        }

      }

    }

  }

  private int getTickShift(int width) {

    // Calculate position
    int off=0;
    switch(dOrientation) {
      case VERTICAL_LEFT:
        if(orientation==VERTICAL_ORG)
          off=-width/2;
        break;
      case VERTICAL_RIGHT:
        if(orientation==VERTICAL_ORG)
          off=-width/2;
        else
          off=-width;
        break;
      case HORIZONTAL_DOWN:
      case HORIZONTAL_UP:
        if(orientation==HORIZONTAL_ORG1 || orientation==HORIZONTAL_ORG2)
          off=-width/2;
        else if (orientation==HORIZONTAL_UP)
          off=0;
        else
          off=-width;
        break;
    }

    return off;
  }

  private int getTickShiftOpposite(int width) {

    // Calculate position
    int off=0;
    switch(dOrientation) {
      case VERTICAL_RIGHT:
        if(orientation==VERTICAL_ORG)
          off=-width/2;
        break;
      case VERTICAL_LEFT:
        if(orientation==VERTICAL_ORG)
          off=-width/2;
        else
          off=-width;
        break;
      case HORIZONTAL_DOWN:
      case HORIZONTAL_UP:
        if(orientation==HORIZONTAL_ORG1 || orientation==HORIZONTAL_ORG2)
          off=-width/2;
        else if (orientation==HORIZONTAL_UP)
          off=-width;
        else
          off=0;
        break;
    }

    return off;
  }

  // Paint Y sub tick and return tick spacing
  // Expert usage
  private void paintYTicks(Graphics g, int i, int x0, double y, int la, BasicStroke bs, int tr,int off,boolean grid) {

    int j,h;
    Graphics2D g2 = (Graphics2D) g;
    Stroke old = g2.getStroke();

    if (subtickVisible && i < (labels.size() - 1)) {

      // Draw ticks

      if (subTickStep == -1) {  // Logarithmic step

        for (j = 0; j < logStep.length; j++) {
          h = (int)Math.rint(y + tickStep * logStep[j]);
          g.drawLine(x0 + tr + off, h, x0 + tr + off + subtickLength, h);
          if (gridVisible && subGridVisible && grid) {
            if (bs != null) g2.setStroke(bs);
            g.drawLine(x0, h, x0 + la, h);
            g2.setStroke(old);
          }
        }

      } else if (subTickStep > 0) {  // Linear step

        double r = 1.0 / (double)subTickStep;
        for (j = 0; j < subTickStep; j ++) {
          h = (int)Math.rint(y + tickStep * r * j);
          g.drawLine(x0 + tr + off , h, x0 + tr + off + subtickLength, h);
          if ((j > 0) && gridVisible && subGridVisible && grid) {
            if (bs != null) g2.setStroke(bs);
            g.drawLine(x0, h, x0 + la, h);
            g2.setStroke(old);
          }
        }

      }

    }

  }

  // Paint X sub tick and return tick spacing
  // Expert usage
  private void paintXTicks(Graphics g, int i, int y0, double x, int la, BasicStroke bs, int tr,int off,boolean grid) {

    int j,w;
    Graphics2D g2 = (Graphics2D) g;
    Stroke old = g2.getStroke();

    if (subtickVisible && i < (labels.size() - 1)) {

      if (subTickStep == -1) {  // Logarithmic step

        for (j = 0; j < logStep.length; j++) {
          w = (int)Math.rint(x + tickStep * logStep[j]);
          g.drawLine(w, y0 + tr + off, w, y0 + tr + off + subtickLength);
          if (gridVisible && subGridVisible && grid) {
            if (bs != null) g2.setStroke(bs);
            g.drawLine(w, y0, w, y0 + la);
            g2.setStroke(old);
          }
        }


      } else if (subTickStep > 0) {  // Linear step

        double r = 1.0 / (double)subTickStep;
        for (j = 0; j < subTickStep; j++ ) {
          w = (int)Math.rint(x + tickStep * r * j);
          g.drawLine(w, y0 + tr + off, w, y0 + tr + off + subtickLength);
          if ((j > 0) && gridVisible && subGridVisible && grid) {
            if (bs != null) g2.setStroke(bs);
            g.drawLine(w, y0, w, y0 + la);
            g2.setStroke(old);
          }
        }

      }

    }

  }

  /**
   * Compute the medium color of c1,c2
   * @param c1 Color 1
   * @param c2 Color 2
   * @return Averaged color.
   */
  public Color computeMediumColor(Color c1, Color c2) {
    return new Color((c1.getRed() + 3 * c2.getRed()) / 4,
      (c1.getGreen() + 3 * c2.getGreen()) / 4,
      (c1.getBlue() + 3 * c2.getBlue()) / 4);
  }

  /** Expert usage.
   * Paint the axis and its DataView at the specified position along the given axis.
   * @param g Graphics object
   * @param frc Font render context
   * @param x0 Axis x position (pixel space)
   * @param y0 Axis y position (pixel space)
   * @param xAxis Horizontal axis of the graph
   * @param xOrg X origin for transformation (pixel space)
   * @param yOrg Y origin for transformation (pixel space)
   * @param back Background color
   * @param oppositeVisible Oposite axis is visible.
   *
   */
  void paintAxis(Graphics g, FontRenderContext frc, int x0, int y0, JLAxis xAxis, int xOrg, int yOrg, Color back,boolean oppositeVisible) {

    int la = 0;
    int tr = 0;
    Point p0 = null;

    // Do not paint vertical axis without data
    if (!isHorizontal() && dataViews.size() == 0) return;

    // Do not paint when too small
    if (getLength() <= 1) {
      boundRect.setRect(0,0,0,0);
      return;
    }

    la = xAxis.getLength();

    // Do not paint when out of bounds
    if(la<=0) {
      boundRect.setRect(0,0,0,0);
      return;
    }

    // Update bounding rectangle

    switch (dOrientation) {

      case VERTICAL_LEFT:
        boundRect.setRect(x0 + getThickness(), y0, la, csize.height);

        if (orientation == VERTICAL_ORG) {
          p0 = transform(0.0, 1.0, xAxis);
          if ((p0.x >= (x0 + csize.width)) && (p0.x <= (x0 + csize.width + la)))
            tr = p0.x - (x0 + csize.width);
          else
          // Do not display axe ot of bounds !!
            return;
        }
        break;

      case VERTICAL_RIGHT:
        boundRect.setRect(x0 - la - 1, y0, la, csize.height);

        if (orientation == VERTICAL_ORG) {
          p0 = transform(0.0, 1.0, xAxis);
          if ((p0.x >= (x0 - la - 1)) && (p0.x <= x0))
            tr = p0.x - x0;
          else
          // Do not display axe ot of bounds !!
            return;
        }
        break;

      case HORIZONTAL_DOWN:
      case HORIZONTAL_UP:
        boundRect.setRect(x0, y0 - la, csize.width, la);

        if (orientation == HORIZONTAL_ORG1 || orientation == HORIZONTAL_ORG2) {

          p0 = xAxis.transform(1.0, 0.0, this);
          if ((p0.y >= (y0 - la)) && (p0.y <= y0))
            tr = p0.y - y0;
          else
          // Do not display axe ot of bounds !!
            return;

        }

        break;

      default:
        System.out.println("JLChart warning: Wrong axis position");
        break;

    }

    if(!visible)
      return;

    paintAxisDirect(g,frc,x0,y0,back,tr,xAxis.getLength());
    if(drawOpposite && oppositeVisible) {
      if(orientation==VERTICAL_ORG || orientation == HORIZONTAL_ORG1 || orientation == HORIZONTAL_ORG2)
        paintAxisOppositeDouble(g,frc,x0,y0,back,tr,xAxis.getLength());
      else
        paintAxisOpposite(g,frc,x0,y0,back,tr,xAxis.getLength());
    }

  }

  /**
   * Paint this axis.
   * @param g Graphics context
   * @param frc Font render context
   * @param x0 Axis position
   * @param y0 Axis position
   * @param back background Color (used to compute subTick color)
   * @param tr Translation from x0 to axis.
   * @param la Translation to opposite axis (used by grid).
   */
  public void paintAxisDirect(Graphics g, FontRenderContext frc, int x0, int y0,Color back,int tr,int la) {

    int i,x,y,tickOff,subTickOff,labelShift;
    BasicStroke bs = null;
    Graphics2D g2 = (Graphics2D) g;

    Color subgridColor = computeMediumColor(labelColor, back);
    if (gridVisible) bs = GraphicsUtils.createStrokeForLine(1, gridStyle);
    g.setFont(labelFont);

    tickOff = getTickShift(tickLength);
    subTickOff = getTickShift(subtickLength);

    switch (dOrientation) {

      case VERTICAL_LEFT:

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintYOutTicks(g, x0 + csize.width, (double)y0 + lis.pos - tickStep, y0, la, bs, tr,subTickOff,true);
          paintYOutTicks(g, x0 + csize.width, (double)y0 + lie.pos, y0, la, bs, tr,subTickOff,true);
        }

        for (i = 0; i < labels.size(); i++) {

          // Draw labels
          g.setColor(labelColor);
          LabelInfo li = labels.get(i);

          x = x0 + (csize.width - 4) - li.size.width;
          y = (int)Math.rint(li.pos) + y0;
          g.drawString(li.value, x + tr + li.offset.x, y + li.offset.y + li.size.height / 3);

          //Draw the grid
          if (gridVisible) {
            Stroke old = g2.getStroke();
            if (bs != null) g2.setStroke(bs);
            g.drawLine(x0 + (csize.width + 1), y, x0 + (csize.width + 1) + la, y);
            g2.setStroke(old);
          }

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintYTicks(g, i, x0 + csize.width,li.pos + (double)y0, la, bs, tr,subTickOff,true);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(x0 + tr + csize.width + tickOff, y, x0 + tr + csize.width + tickOff + tickLength, y);

        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x0 + tr + csize.width, y0, x0 + tr + csize.width, y0 + csize.height);

        if (name != null) {
          // Draw vertical label
          g2.rotate(-Math.PI/2.0);
          Rectangle2D bounds = labelFont.getStringBounds(name, frc);
          int fontAscent = (int)(labelFont.getLineMetrics("0",frc).getAscent()+0.5f);
          g.drawString(name,- y0 - (csize.height + (int)(bounds.getWidth()))/2,x0 + fontAscent - 2);
          g2.rotate(Math.PI/2.0);
        }
        break;

      case VERTICAL_RIGHT:

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintYOutTicks(g, x0, (double)y0 + lis.pos - tickStep, y0, -la, bs, tr,subTickOff,true);
          paintYOutTicks(g, x0, (double)y0 + lie.pos, y0, -la, bs, tr,subTickOff,true);
        }

        for (i = 0; i < labels.size(); i++) {

          // Draw labels
          g.setColor(labelColor);
          LabelInfo li = labels.get(i);

          y = (int)Math.rint(li.pos) + y0;
          g.drawString(li.value, x0 + tr + li.offset.x + 6, y + li.offset.y + li.size.height / 3);

          //Draw the grid
          if (gridVisible) {
            Stroke old = g2.getStroke();
            if (bs != null) g2.setStroke(bs);
            g.drawLine(x0, y, x0- la, y);
            g2.setStroke(old);
          }

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintYTicks(g, i, x0, li.pos + (double)y0, -la, bs, tr,subTickOff,true);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(x0 + tr + tickOff , y, x0 + tr + tickOff + tickLength, y);
        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x0 + tr, y0, x0 + tr, y0 + csize.height);

        if (name != null) {
          // Draw vertical label
          g2.rotate(-Math.PI/2.0);
          Rectangle2D bounds = labelFont.getStringBounds(name, frc);
          g.drawString(name,- y0 - (csize.height + (int)(bounds.getWidth()))/2, x0 + tr + csize.width - 2);
          g2.rotate(Math.PI/2.0);
        }

        break;

      case HORIZONTAL_UP:
      case HORIZONTAL_DOWN:

        if(orientation==HORIZONTAL_UP) {
          tr = -la;
          labelShift = 1;
        } else {
          if(orientation==HORIZONTAL_ORG1 || orientation==HORIZONTAL_ORG2)
            labelShift = 1;
          else
            labelShift = 2;
        }

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintXOutTicks(g, y0, (double)x0 + lis.pos - tickStep,  x0, -la, bs, tr,subTickOff,true);
          paintXOutTicks(g, y0, (double)x0 + lie.pos,  x0, -la, bs, tr,subTickOff,true);
        }

        for (i = 0; i < labels.size(); i++) {

          // Draw labels
          g.setColor(labelColor);
          LabelInfo li = labels.get(i);

          x = (int)Math.rint(li.pos)+x0;
          y = y0;
          if (orientation==HORIZONTAL_UP) {
            g.drawString(li.value, x + li.offset.x - li.size.width / 2, y + tr - 2);
          }
          else {
            g.drawString(li.value, x + li.offset.x - li.size.width / 2, y + tr + li.offset.y + li.size.height + 2);
          }

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintXTicks(g, i, y, li.pos+(double)x0, -la, bs, tr,subTickOff,true);
          }

          //Draw the grid
          g.setColor(labelColor);
          if (gridVisible) {
            Stroke old = g2.getStroke();
            if (bs != null) g2.setStroke(bs);
            g.drawLine(x, y0, x, y0 - la);
            g2.setStroke(old);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(x, y0 + tr + tickOff, x, y0 + tr + tickOff + tickLength);

        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x0, y0 + tr, x0 + csize.width, y0 + tr);

        if (name != null) {
          Rectangle2D bounds = labelFont.getStringBounds(name, frc);

          g.drawString(name, x0 + ((csize.width) - (int) bounds.getWidth()) / 2,
            y0 + labelShift * (int) bounds.getHeight());
        }

        break;

    }

  }

  public void paintAxisOpposite(Graphics g, FontRenderContext frc, int x0, int y0,Color back,int tr,int la) {

    int i,x,y,tickOff,subTickOff;
    BasicStroke bs = null;

    Color subgridColor = computeMediumColor(labelColor, back);

    tickOff = getTickShiftOpposite(tickLength);
    subTickOff = getTickShiftOpposite(subtickLength);

    switch (dOrientation) {

      case VERTICAL_RIGHT:

        int nX0 = x0 - la - csize.width;

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintYOutTicks(g, nX0 + csize.width, (double)y0 + lis.pos - tickStep, y0, la, bs, tr,subTickOff,false);
          paintYOutTicks(g, nX0 + csize.width, (double)y0 + lie.pos, y0, la, bs, tr,subTickOff,false);
        }

        for (i = 0; i < labels.size(); i++) {

          LabelInfo li = labels.get(i);
          x = nX0 + (csize.width - 4) - li.size.width;
          y = (int)Math.rint(li.pos) + y0;

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintYTicks(g, i, nX0 + csize.width, li.pos + (double)y0, la, bs, tr,subTickOff,false);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(nX0 + tr + csize.width + tickOff, y, nX0 + tr + csize.width + tickOff + tickLength, y);

        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(nX0 + tr + csize.width, y0, nX0 + tr + csize.width, y0 + csize.height);
        break;

      case VERTICAL_LEFT:

        x = x0 + la + csize.width;

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintYOutTicks(g, x, (double)y0 + lis.pos - tickStep, y0, -la, bs, tr,subTickOff,false);
          paintYOutTicks(g, x, (double)y0 + lie.pos, y0, -la, bs, tr,subTickOff,false);
        }

        for (i = 0; i < labels.size(); i++) {

          LabelInfo li = labels.get(i);
          y = (int)Math.rint(li.pos) + y0;

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintYTicks(g, i, x, li.pos + (double)y0, -la, bs, tr,subTickOff,false);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(x + tr + tickOff , y, x + tr + tickOff + tickLength, y);
        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x + tr, y0, x + tr, y0 + csize.height);
        break;

      case HORIZONTAL_UP:
      case HORIZONTAL_DOWN:

        if(orientation==HORIZONTAL_DOWN)
          tr = -la;

        //Draw extra sub ticks (outside labels limit)
        if (labels.size()>0 && autoLabeling) {
          LabelInfo lis = labels.get(0);
          LabelInfo lie = labels.get(labels.size()-1);
          g.setColor(subgridColor);
          paintXOutTicks(g, y0, (double)x0 + lis.pos - tickStep, x0, -la, bs, tr,subTickOff,false);
          paintXOutTicks(g, y0, (double)x0 + lie.pos, x0, -la, bs, tr,subTickOff,false);
        }

        for (i = 0; i < labels.size(); i++) {

          LabelInfo li = labels.get(i);
          x = (int)Math.rint(li.pos) + x0;
          y = y0;

          //Draw sub tick
          if(autoLabeling) {
            g.setColor(subgridColor);
            paintXTicks(g, i, y, li.pos + (double)x0, -la, bs, tr,subTickOff,false);
          }

          //Draw tick
          g.setColor(labelColor);
          g.drawLine(x, y0 + tr + tickOff, x, y0 + tr + tickOff + tickLength);

        }

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x0, y0 + tr, x0 + csize.width, y0 + tr);
        break;

    }

  }

  public void paintAxisOppositeDouble(Graphics g, FontRenderContext frc, int x0, int y0,Color back,int tr,int la) {

    int nX0;

    switch (dOrientation) {

      case VERTICAL_RIGHT:

        nX0 = x0 - la;

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(nX0, y0, nX0 , y0 + csize.height);

        // Draw Axe
        g.drawLine(nX0 + la , y0, nX0 + la, y0 + csize.height);
        break;

      case VERTICAL_LEFT:

        nX0 = x0 + csize.width;

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(nX0, y0, nX0 , y0 + csize.height);

        // Draw Axe
        g.drawLine(nX0 + la , y0, nX0 + la, y0 + csize.height);

        break;

      case HORIZONTAL_UP:
      case HORIZONTAL_DOWN:

        // Draw Axe
        g.setColor(labelColor);
        g.drawLine(x0, y0 - la, x0 + csize.width, y0 - la);

        // Draw Axe
        g.drawLine(x0, y0, x0 + csize.width, y0);
        break;

    }

  }

  /**
   * Apply axis configuration.
   * @param prefix Axis settings prefix
   * @param f CfFileReader object wich contains axis parametters
   * @see JLChart#applyConfiguration
   * @see JLDataView#applyConfiguration
   */
  public void applyConfiguration(String prefix, CfFileReader f) {

    Vector p;
    p = f.getParam(prefix + "visible");
    if (p != null) setVisible(OFormat.getBoolean(p.get(0).toString()));
    p = f.getParam(prefix + "grid");
    if (p != null) setGridVisible(OFormat.getBoolean(p.get(0).toString()));
    p = f.getParam(prefix + "subgrid");
    if (p != null) setSubGridVisible(OFormat.getBoolean(p.get(0).toString()));
    p = f.getParam(prefix + "grid_style");
    if (p != null) setGridStyle(OFormat.getInt(p.get(0).toString()));
    p = f.getParam(prefix + "min");
    if (p != null) setMinimum(OFormat.getDouble(p.get(0).toString()));
    p = f.getParam(prefix + "max");
    if (p != null) setMaximum(OFormat.getDouble(p.get(0).toString()));
    p = f.getParam(prefix + "autoscale");
    if (p != null) setAutoScale(OFormat.getBoolean(p.get(0).toString()));
    p = f.getParam(prefix + "scale");
    if (p != null) {
      setScale(OFormat.getInt(p.get(0).toString()));
    } else {
      // To handle a bug in older version
      p = f.getParam(prefix + "cale");
      if (p != null) setScale(OFormat.getInt(p.get(0).toString()));
    }
    p = f.getParam(prefix + "format");
    if (p != null) setLabelFormat(OFormat.getInt(p.get(0).toString()));
    p = f.getParam(prefix + "title");
    if (p != null) setName(OFormat.getName(p.get(0).toString()));
    p = f.getParam(prefix + "color");
    if (p != null) setAxisColor(OFormat.getColor(p));
    p = f.getParam(prefix + "label_font");
    if (p != null) setFont(OFormat.getFont(p));
    p = f.getParam(prefix + "fit_display_duration");
    if (p != null) this.setFitXAxisToDisplayDuration(OFormat.getBoolean(p.get(0).toString()));

  }

  /**
   * Builds a configuration string that can be write into a file and is compatible
   * with CfFileReader.
   * @param prefix Axis settings prefix
   * @return A string containing param
   * @see JLAxis#applyConfiguration
   * @see JLChart#getConfiguration
   * @see JLDataView#getConfiguration
   */
  public String getConfiguration(String prefix) {

    String to_write = "";

    to_write += prefix + "visible:" + isVisible() + "\n";
    to_write += prefix + "grid:" + isGridVisible() + "\n";
    to_write += prefix + "subgrid:" + isSubGridVisible() + "\n";
    to_write += prefix + "grid_style:" + getGridStyle() + "\n";
    to_write += prefix + "min:" + getMinimum() + "\n";
    to_write += prefix + "max:" + getMaximum() + "\n";
    to_write += prefix + "autoscale:" + isAutoScale() + "\n";
    to_write += prefix + "scale:" + getScale() + "\n";
    to_write += prefix + "format:" + getLabelFormat() + "\n";
    to_write += prefix + "title:\'" + getName() + "\'\n";
    to_write += prefix + "color:" + OFormat.color(getAxisColor()) + "\n";
    to_write += prefix + "label_font:" + OFormat.font(getFont()) + "\n";
    to_write += prefix + "fit_display_duration:" + isFitXAxisToDisplayDuration() + "\n";

    return to_write;
  }

  /**
   * Allaws user to know if the 0 value will always be visible in case of auto scale
   * @return a boolean value
   */
  public boolean isZeroAlwaysVisible ()
  {
    return zeroAlwaysVisible;
  }

  /**
   * Sets if 0 must always be visible in case of auto scale or not
   * @param zeroAlwaysVisible a boolean value. True for always visible, false otherwise.
   */
  public void setZeroAlwaysVisible (boolean zeroAlwaysVisible)
  {
    this.zeroAlwaysVisible = zeroAlwaysVisible;
  }

  public String getDateFormat ()
  {
    return dateFormat;
  }

  /**
   * Sets date format chen chosen label format is DATE_FORMAT
   * @param dateFormat
   * @see #US_DATE_FORMAT
   * @see #FR_DATE_FORMAT
   */
  public void setDateFormat (String dateFormat)
  {
    this.dateFormat = dateFormat;
  }

}
