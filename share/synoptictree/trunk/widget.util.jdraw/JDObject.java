package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.awt.event.MouseEvent;
import java.awt.geom.Line2D;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Vector;

/**
 * An abstract class for the JDraw graphics objects. This class handle all common properties
 * of JDObject.
 */
public abstract class JDObject {

  /** Solid line style */
  public static final int LINE_STYLE_SOLID = 0;
  /** Dot line style */
  public static final int LINE_STYLE_DOT = 1;
  /** Dash line style */
  public static final int LINE_STYLE_DASH = 2;
  /** Long Dash line style */
  public static final int LINE_STYLE_LONG_DASH = 3;
  /** Dash + Dot line style */
  public static final int LINE_STYLE_DASH_DOT = 4;

  /** No filling */
  public static final int FILL_STYLE_NONE = 0;
  /** Solid fill style */
  public static final int FILL_STYLE_SOLID = 1;
  /** Hatch fill style */
  public static final int FILL_STYLE_LARGE_RIGHT_HATCH = 2;
  /** Hatch fill style */
  public static final int FILL_STYLE_LARGE_LEFT_HATCH = 3;
  /** Hatch fill style */
  public static final int FILL_STYLE_LARGE_CROSS_HATCH = 4;
  /** Hatch fill style */
  public static final int FILL_STYLE_SMALL_RIGHT_HATCH = 5;
  /** Hatch fill style */
  public static final int FILL_STYLE_SMALL_LEFT_HATCH = 6;
  /** Hatch fill style */
  public static final int FILL_STYLE_SMALL_CROSS_HATCH = 7;
  /** Hatch fill style */
  public static final int FILL_STYLE_DOT_PATTERN_1 = 8;
  /** Hatch fill style */
  public static final int FILL_STYLE_DOT_PATTERN_2 = 9;
  /** Hatch fill style */
  public static final int FILL_STYLE_DOT_PATTERN_3 = 10;
  /** Gradient fill style */
  public static final int FILL_STYLE_GRADIENT = 11;

  /** the object value is incremented (+1) on click */
  public static final int VALUE_INC_ON_CLICK  = 0;
  /** the object value is incremented (+1) on mousePressed or mouseReleased */
  public static final int VALUE_INC_ON_PRESSRELEASE = 1;
  /** the object value receive the x mouse coordinates when dragged (relative to left of object) */
  public static final int VALUE_CHANGE_ON_XDRAG_LEFT = 2;
  /** the object value receive the x mouse coordinates when dragged (relative to right of object) */
  public static final int VALUE_CHANGE_ON_XDRAG_RIGHT = 3;
  /** the object value receive the y mouse coordinates when dragged (relative to top of object) */
  public static final int VALUE_CHANGE_ON_YDRAG_TOP = 4;
  /** the object value receive the y mouse coordinates when dragged (relative to bottom of object) */
  public static final int VALUE_CHANGE_ON_YDRAG_BOTTOM = 5;

  // Summit motion type
  final static int NONE_SM = 0;
  final static int HORIZONTAL_SM = 1;
  final static int VERTICAL_SM = 2;
  final static int BOTH_SM = 3;

  // Event for value processing
  public final static int MPRESSED  = 1;
  public final static int MRELEASED = 2;
  public final static int MDRAGGED  = 3;

  // Default
  private static final Color foregroundDefault = Color.black;
  private static final Color backgroundDefault = Color.white;
  private static final int fillStyleDefault = JDObject.FILL_STYLE_NONE;
  private static final int lineWidthDefault = 1;
  private static final int lineStyleDefault = JDObject.LINE_STYLE_SOLID;
  private static final boolean isShadowedDefault = false;
  private static final boolean invertShadowDefault = false;
  private static final int shadowThicknessDefault = 5;
  private static final boolean visibleDefault = true;
  private static final String nameDefault = "JDObject";
  private static final int minValueDefault  = 0;
  private static final int maxValueDefault  = 1;
  private static final int initValueDefault = 0;
  private static final boolean userValueDefault=false;
  private static final int valueChangeModeDefault=VALUE_INC_ON_CLICK;
  private static final float gradientX1default=0.0F;
  private static final float gradientY1default=0.0F;
  private static final float gradientX2default=70.7F;
  private static final float gradientY2default=70.7F;
  private static final Color gradientC1default=Color.BLACK;
  private static final Color gradientC2default=Color.WHITE;
  private static final boolean gradientCyclicdefault=false;
  private static final boolean antiAliasDefault=false;

  // Vars
  Rectangle boundRect = new Rectangle(0, 0, 0, 0);
  Point.Double origin = new Point.Double(0.0, 0.0);
  Point.Double[] summit;

  // Object properties
  Color foreground;
  int lineStyle;
  int lineWidth;
  Color background;
  int fillStyle;
  boolean visible;
  String name;
  boolean userValue;
  int valueChangeMode;
  boolean antiAlias;

  // Value properties
  private int value;
  int minValue;
  int maxValue;
  int initValue;
  private boolean hasMapper;

  // Value programs
  JDValueProgram backgroundMapper;
  JDValueProgram foregroundMapper;
  JDValueProgram visibilityMapper;
  JDValueProgram invertShadowMapper;
  JDValueProgram hTranslationMapper;
  JDValueProgram vTranslationMapper;
  private Vector valueListener = null;
  private Vector mouseListener = null;
  private JDrawEditor parent = null;

  // Shawdows
  int[] ptsx;
  int[] ptsy;
  double[] normes;
  Polygon[] shadows;
  Color[] shadowColors;
  int shadowThickness;
  Rectangle sBoundRect;
  boolean isShadowed;
  boolean invertShadow;
  double lightx = 1;
  double lighty = 1;

  // Backup for transform
  private double[] sSummit=null;
  private double   sXOrg;
  private double   sYOrg;
  private Rectangle preRefreshRect = null;

  // Gradient paint param
  float   gradientX1;
  float   gradientX2;
  float   gradientY1;
  float   gradientY2;
  float   sGradientX1;
  float   sGradientX2;
  float   sGradientY1;
  float   sGradientY2;
  Color   gradientC1;
  Color   gradientC2;
  boolean gradientCyclic;

  // Extensions
  String[] extParamValue=null;      // Extension param values
  String[] extParamName=null;       // Extension param names

  // -----------------------------------------------------------
  // Initialisation stuff
  // -----------------------------------------------------------
  void initDefault() {

    // normalize light vector
    double n = Math.sqrt(lightx * lightx + lighty * lighty);
    lightx = lightx / n;
    lighty = lighty / n;
    sBoundRect = new Rectangle();

    foreground = foregroundDefault;
    background = backgroundDefault;
    fillStyle = fillStyleDefault;
    lineWidth = lineWidthDefault;
    lineStyle = lineStyleDefault;
    isShadowed = isShadowedDefault;
    invertShadow = invertShadowDefault;
    shadowThickness = shadowThicknessDefault;
    visible = visibleDefault;
    name = nameDefault;
    antiAlias = antiAliasDefault;
    minValue = minValueDefault;
    maxValue = maxValueDefault;
    initValue = initValueDefault;
    userValue = userValueDefault;
    valueChangeMode = valueChangeModeDefault;
    initDefaultMapper();

    gradientX1=gradientX1default;
    gradientX2=gradientX2default;
    gradientY1=gradientY1default;
    gradientY2=gradientY2default;
    gradientC1=gradientC1default;
    gradientC2=gradientC2default;
    gradientCyclic=gradientCyclicdefault;

  }

  void initDefaultMapper() {
    backgroundMapper=null;
    foregroundMapper=null;
    visibilityMapper=null;
    invertShadowMapper=null;
    hTranslationMapper=null;
    vTranslationMapper=null;
  }

  // -----------------------------------------------------------
  // Dynamic value stuff
  // -----------------------------------------------------------

  /** Returns the value of this object.
   * @see #setValue
   */
  public int getValue() {
    return value;
  }

  /**
   * Sets the value of this object and execute the dynamic object program if enabled.
   * If this object is a JDGroup, the specified value is spread all over children of
   * this group.
   * @param v New value
   */
  public void setValue(int v) {
    restoreTransform();
    setVal(v,this);
  }

  /** Overrided setValue */
  void setVal(int v,JDObject master) {
     value=v;
     manageMappers(master);
  }

  /** Initialise value program. */
  void initValue() {
    initVal(this);
  }

  /** Overrided initValue */
  void initVal(JDObject master) {
    hasMapper = hasValueProgram();
    value = initValue;
    manageMappers(master);
  }

  void incValue() {
    if(value+1>maxValue) {
      setValue(minValue);
      fireValueExceed();
    } else {
      setValue(value+1);
    }
  }

  boolean hasValueProgram() {
    return (backgroundMapper!=null) ||
           (foregroundMapper!=null) ||
           (visibilityMapper!=null) ||
           (invertShadowMapper!=null) ||
           (hTranslationMapper!=null) ||
           (vTranslationMapper!=null);
  }

  int saturateValue(int v) {
    if (v > getMaxValue())
      v = getMaxValue();
    if (v < getMinValue())
      v = getMinValue();
    return v;
  }

  /** Process the value program */
  public void processValue(int type,int ex,int ey) {

    Rectangle b;
    double r;
    int v,oldValue = value;

    switch (getValueChangeMode()) {
      case JDObject.VALUE_INC_ON_CLICK:
        if(type==MPRESSED) {
          incValue();
          fireValueChange();
        }
        break;
      case JDObject.VALUE_INC_ON_PRESSRELEASE:
        if(type==MPRESSED || type==MRELEASED) {
          incValue();
          fireValueChange();
        }
        break;
      case JDObject.VALUE_CHANGE_ON_XDRAG_LEFT:
        // Mouse coordinates to value conversion (Left to Right) => (min=>max)
        b = getBoundRect();
        r = (double) (getMaxValue() + 1 - getMinValue());
        v = getMinValue() + (int) ((double) (ex - b.x) / (double) (b.width) * r);
        setValue(saturateValue(v));
        if(value!=oldValue) fireValueChange();
        break;
      case JDObject.VALUE_CHANGE_ON_XDRAG_RIGHT:
        // Mouse coordinates to value conversion (Right to Left) => (min=>max)
        b = getBoundRect();
        r = (double) (getMaxValue() + 1 - getMinValue());
        v = getMinValue() + (int) ((double) (b.width + b.x - ex) / (double) (b.width) * r);
        setValue(saturateValue(v));
        if(value!=oldValue) fireValueChange();
        break;
      case JDObject.VALUE_CHANGE_ON_YDRAG_TOP:
        // Mouse coordinates to value conversion (Top to Bottom) => (min=>max)
        b = getBoundRect();
        r = (double) (getMaxValue() + 1 - getMinValue());
        v = getMinValue() + (int) ((double) (ey - b.y) / (double) (b.height) * r);
        setValue(saturateValue(v));
        if(value!=oldValue) fireValueChange();
        break;
      case JDObject.VALUE_CHANGE_ON_YDRAG_BOTTOM:
        // Mouse coordinates to value conversion (Bottom to Top) => (min=>max)
        b = getBoundRect();
        r = (double) (getMaxValue() + 1 - getMinValue());
        v = getMinValue() + (int) ((double) (b.height + b.y - ey) / (double) (b.height) * r);
        setValue(saturateValue(v));
        if(value!=oldValue) fireValueChange();
        break;
    }

  }

  /* Find active objects at specified position (including not visible object) and fill the result vector */
  void findObjectsAt(int x,int y,Vector result) {
    boolean oldVisible = visible;
    visible = true;
    if(isInteractive() && isInsideObject(x, y))
      result.add(this);
    visible = oldVisible;
  }

  void getUserValueList(Vector result) {
    if(isInteractive())
      result.add(this);
  }

  private void manageMappers(JDObject master) {
    if(hasMapper) {
      manageBackgroundMapper();
      manageForegroundMapper();
      manageVisibilityMapper();
      manageInvertShadowMapper();
      manageTranslationMapper(master);
    }
  }

  private void manageBackgroundMapper() {
    if( backgroundMapper!=null ) {
       Color nC = backgroundMapper.getColorMappingFor(this);
       setBackground(nC);
    }
  }

  private void manageForegroundMapper() {
    if( foregroundMapper!=null ) {
       Color nC = foregroundMapper.getColorMappingFor(this);
       setForeground(nC);
    }
  }

  private void manageInvertShadowMapper() {
    if( invertShadowMapper!=null ) {
       boolean nS = invertShadowMapper.getBooleanMappingFor(this);
       setInverseShadow(nS);
    }
  }

  private void manageVisibilityMapper() {
    if( visibilityMapper!=null ) {
       boolean nS = visibilityMapper.getBooleanMappingFor(this);
       setVisible(nS);
    }
  }

  private void manageTranslationMapper(JDObject master) {
    int x=0,y=0;
    if (hTranslationMapper != null)
      x = hTranslationMapper.getIntegerMappingFor(this,master);
    if (vTranslationMapper != null)
      y = vTranslationMapper.getIntegerMappingFor(this,master);
    translate((double) x, (double)y);
  }

  /**
   * Adds the specified value listener to this object.
   * @param l Value listener
   */
  public void addValueListener(JDValueListener l) {
    if(valueListener==null)
      valueListener=new Vector();
    valueListener.add(l);
  }

  /**
   * Adds the specified mouse listener to this object.
   * @param l JDMouseListener
   */
  public void addMouseListener(JDMouseListener l) {
    if(mouseListener==null)
      mouseListener=new Vector();
    mouseListener.add(l);
  }

  /**
   * Remove the specified value listener from this object.
   * @param l Listener to be removed.
   */
  public void removeValueListener(JDValueListener l) {
     if(valueListener!=null)
       valueListener.remove(l);
  }

  /**
   * Remove the specified mouse listener from this object.
   * @param l Listener to be removed.
   */
  public void removeMouseListener(JDMouseListener l) {
     if(mouseListener!=null)
       mouseListener.remove(l);
  }

  /** Remove all value listener belonging to this object. */
  public void clearValueListener() {
    if(valueListener!=null)
      valueListener.clear();
    valueListener=null;
  }

  /** Remove all mouse listener belonging to this object. */
  public void clearMouseListener() {
    if(mouseListener!=null)
      mouseListener.clear();
    mouseListener=null;
  }

  public boolean hasMouseListener() {
    if(mouseListener!=null)
      return mouseListener.size()>0;
    return false;
  }

  void fireValueChange() {
    if(valueListener!=null) {
      for(int i=0;i<valueListener.size();i++)
        ((JDValueListener)valueListener.get(i)).valueChanged(this);
    }
  }

  void fireValueExceed() {
    if(valueListener!=null) {
      for(int i=0;i<valueListener.size();i++)
        ((JDValueListener)valueListener.get(i)).valueExceedBounds(this);
    }
  }

  // Changed to public to be able to propagate the MouseEvents inside a JDGroup
  public void fireMouseEvent(int type,MouseEvent e0) {

    if(mouseListener!=null) {
      //srubio@cells.es, I create a new MouseEvent to keep the information about the type of event when it is propagated.
//MouseEvent(Component source, int id, long when, int modifiers, int x, int y, int clickCount, boolean popupTrigger, int button) 
      JDMouseEvent e = new JDMouseEvent(this,
	new MouseEvent((Component)e0.getSource(),type,e0.getWhen(),e0.getModifiers(),e0.getX(),e0.getY(),e0.getClickCount(),e0.isPopupTrigger(),e0.getButton()));
      switch(type) {
        case MouseEvent.MOUSE_PRESSED:
          for(int i=0;i<mouseListener.size();i++)
            ((JDMouseListener)mouseListener.get(i)).mousePressed(e);
          break;
        case MouseEvent.MOUSE_RELEASED:
          for(int i=0;i<mouseListener.size();i++)
            ((JDMouseListener)mouseListener.get(i)).mouseReleased(e);
          break;
        case MouseEvent.MOUSE_CLICKED:
          for(int i=0;i<mouseListener.size();i++)
            ((JDMouseListener)mouseListener.get(i)).mouseClicked(e);
          break;
        case MouseEvent.MOUSE_ENTERED:
	  //System.out.println("JDObject("+getName()+"): MOUSE_ENTERED! MouseEvent("+type+"=="+MouseEvent.MOUSE_ENTERED+").");
          for(int i=0;i<mouseListener.size();i++)
            ((JDMouseListener)mouseListener.get(i)).mouseEntered(e);
          break;
        case MouseEvent.MOUSE_EXITED:
          for(int i=0;i<mouseListener.size();i++)
            ((JDMouseListener)mouseListener.get(i)).mouseExited(e);
          break;
	default:
	  //System.out.println("JDObject("+getName()+"): UNKNOWN MouseEvent("+type+"!="+MouseEvent.MOUSE_ENTERED+").");
      }
    } else System.out.println("JDObject("+getName()+"): MouseEvent discarded as mouseListener is Null.");

  }

  // -----------------------------------------------------------
  // Painting stuff
  // -----------------------------------------------------------
  /**
   * Paints this object.
   * @param parent JdrawEditor parent (Can be null except for JDSwingObject)
   * @param g the specified Graphics window
   */
  public abstract void paint(JDrawEditor parent,Graphics g);

  void getObjectsByClassList(Vector result,Class theClass) {
    if(getClass()==theClass) result.add(this);
  }

  /**
   * Returns all objects having the given name.
   * @param result Result vector (must be constructed by the caller)
   * @param name JDObject name (Case sensitive)
   * @param recurseGroup true to perform a deep search whithin group, false otherwise.
   * @see JDrawEditor#getObjectsByName
   */
  public void getObjectsByName(Vector result,String name,boolean recurseGroup) {
    if(getName().equals(name)) result.add(this);
  }

  Rectangle getRepaintRect() {

    int sw = (lineWidth + 1);
    if (!hasShadow()) {
      return new Rectangle(boundRect.x - sw, boundRect.y - sw,
          boundRect.width + sw * 2, boundRect.height + sw * 2);
    } else {
      Rectangle r = getShadowBoundRect();
      return new Rectangle(r.x - sw, r.y - sw,
          r.width + sw * 2, r.height + sw * 2);
    }

  }

  /**
   * Gets the bounding rectangle of this object.
   */
  public Rectangle getBoundRect() {

    return boundRect;

  }

  void paintShadows(Graphics g) {
    // Paint shadows
    if (hasShadow()) {
      for (int i = 0; i < shadows.length; i++) {
        g.setColor(shadowColors[i]);
        g.fillPolygon(shadows[i]);
      }
    }
  }

  // -----------------------------------------------------------
  // Selection Summit handling
  // -----------------------------------------------------------
  void createSummit() {
    for (int i = 0; i < summit.length; i++)
      summit[i] = new Point.Double(0, 0);
  }

  /**
   * Determines whether the specified point is inside this object.
   * @param x X coordinate (pixel)
   * @param y Y coordinate (pixel)
   */
  public boolean isInsideObject(int x, int y) {
    if (!visible) return false;
    int lw = (lineWidth + 1) * 2;
    Rectangle r = new Rectangle(boundRect.x - lw/2, boundRect.y - lw/2, boundRect.width + lw, boundRect.height + lw);
    return r.contains(x, y);
  }

  /**
   * Returns the summit number of this object.
   */
  public int getSummitNumber() {
    return summit.length;
  }

  int getSummit(int x, int y,double summitWidth) {
    int i = 0;
    boolean found = false;
    int sw  = (int)(summitWidth/2.0 + 1.0);
    while (i < summit.length && !found) {
      found = (x >= summit[i].x - sw) && (x <= summit[i].x + sw) &&
          (y >= summit[i].y - sw) && (y <= summit[i].y + sw);
      if (!found) i++;
    }
    if (found) return i;

    return -1;
  }

  /**
   * Returns the summit at the specified position. Do not use this
   * to change summit coordinates, Use moveSummit() instead.
   * @param id Summit index
   * @see #getSummitNumber
   * @see #moveSummit
   * @see #moveSummitH
   * @see #moveSummitV
   */
  public Point.Double getSummit(int id) {
    return summit[id];
  }

  void computeBoundRect() {

    double maxx = -65536;
    double maxy = -65536;
    double minx = 65536;
    double miny = 65536;

    for (int i = 0; i < summit.length; i++) {
      if (summit[i].x < minx) minx = summit[i].x;
      if (summit[i].x > maxx) maxx = summit[i].x;
      if (summit[i].y < miny) miny = summit[i].y;
      if (summit[i].y > maxy) maxy = summit[i].y;
    }

    boundRect = new Rectangle((int) minx, (int) miny, (int) (maxx - minx) + 1, (int) (maxy - miny) + 1);

  }

  void paintSummit(Graphics g,double summitWidth) {

    g.setColor(Color.black);
    g.setXORMode(Color.white);
    int sw  = (int)(summitWidth/2.0 + 1.0);
    for (int i = 0; i < summit.length; i++) {
      g.fillRect((int) (summit[i].x+0.5) - sw, (int) (summit[i].y+0.5) - sw, 2*sw, 2*sw);
    }
    g.setPaintMode();
  }

  void paintOrigin(Graphics g) {
    g.setColor(Color.RED);
    g.drawLine((int)(origin.x-10.0),(int)(origin.y), (int)(origin.x+10.0),(int)(origin.y));
    g.drawLine((int)(origin.x),(int)(origin.y-10.0), (int)(origin.x),(int)(origin.y+10));
  }

  /**
   * Moves the specifed summit to the specified position. When using
   * moveSummit() to animate objects, A call to refresh() of this
   * object may be needed.
   * @param id Summit index
   * @param x Absolute X position
   * @param y Absolute Y position
   * @see JDObject#refresh
   */
  public abstract void moveSummit(int id, double x, double y);

  /**
   * Moves horizontaly the specifed summit to the specified position. When using
   * moveSummit() to animate objects, A call to refresh() of this
   * object may be needed.
   * @param id Summit index
   * @param x Absolute X position
   * @see JDObject#refresh
   * @see #moveSummit
   * @see #moveSummitV
   */
  public void moveSummitH(int id,double x) {
    double y = summit[id].y;
    moveSummit(id,x,y);
  }

  /**
   * Moves verticaly the specifed summit to the specified position. When using
   * moveSummit() to animate objects, A call to refresh() of this
   * object may be needed.
   * @param id Summit index
   * @param y Absolute Y position
   * @see JDObject#refresh
   * @see #moveSummit
   * @see #moveSummitH
   */
  public void moveSummitV(int id,double y) {
    double x = summit[id].x;
    moveSummit(id,x,y);
  }

  abstract int getSummitMotion(int id);

  boolean isPointOnLine(int x, int y, int x1, int y1, int x2, int y2) {
    Line2D l = new Line2D.Double((double) x1, (double) y1, (double) x2, (double) y2);
    return l.intersects((double) (x - 2), (double) (y - 2), 4.0, 4.0);
  }

  // -----------------------------------------------------------
  // Copy
  // -----------------------------------------------------------
  /**
   * Returns a copy of this object at the specified location.
   * @param x Horizontal position of the copied object (pixel)
   * @param y Vertical Position of the copied object (pixel)
   * @return The copy of this object.
   */
  public abstract JDObject copy(int x, int y);

  JDPolyline buildDefaultPolyline() {
    JDPolyline ret;
    updateShape();
    Point[] pts = new Point[ptsx.length];
    for(int i=0;i<pts.length;i++)
     pts[i]=new Point(ptsx[i],ptsy[i]);
    ret = new JDPolyline(name,pts);
    ret.copyObjectProperty(this);
    return ret;
  }

  void copyObjectProperty(JDObject e) {

    foreground = new Color(e.getForeground().getRGB());
    background = new Color(e.getBackground().getRGB());
    fillStyle = e.fillStyle;
    lineWidth = e.lineWidth;
    lineStyle = e.lineStyle;
    antiAlias = e.antiAlias;
    isShadowed = e.isShadowed;
    invertShadow = e.invertShadow;
    shadowThickness = e.shadowThickness;
    name = new String(e.name);
    visible = e.visible;
    sBoundRect = new Rectangle();
    minValue  = e.minValue;
    maxValue  = e.maxValue;
    initValue = e.initValue;
    userValue = e.userValue;
    valueChangeMode = e.valueChangeMode;

    // Mapper
    initDefaultMapper();
    if(e.backgroundMapper!=null) backgroundMapper = e.backgroundMapper.copy();
    if(e.foregroundMapper!=null) foregroundMapper = e.foregroundMapper.copy();
    if(e.visibilityMapper!=null) visibilityMapper = e.visibilityMapper.copy();
    if(e.invertShadowMapper!=null) invertShadowMapper = e.invertShadowMapper.copy();
    if(e.hTranslationMapper!=null) hTranslationMapper = e.hTranslationMapper.copy();
    if(e.vTranslationMapper!=null) vTranslationMapper = e.vTranslationMapper.copy();

    gradientX1=e.gradientX1;
    gradientX2=e.gradientX2;
    gradientY1=e.gradientY1;
    gradientY2=e.gradientY2;
    gradientC1=e.gradientC1;
    gradientC2=e.gradientC2;
    gradientCyclic=e.gradientCyclic;

    if( e.extParamName!=null ) {
      extParamName = e.extParamName;
      extParamValue = new String[e.extParamValue.length];
      for(int i=0;i<e.extParamValue.length;i++)
        extParamValue[i] = new String(e.extParamValue[i]);
    } else {
      extParamValue = null;
    }

  }

  void cloneObject(JDObject e, int x, int y) {

    // Clone summit
    summit = new Point.Double[e.summit.length];
    for (int i = 0; i < e.summit.length; i++)
      summit[i] = new Point.Double(e.summit[i].x + x, e.summit[i].y + y);

    origin = new Point.Double(e.origin.x+x, e.origin.y+y);

    copyObjectProperty(e);

  }

  // -----------------------------------------------------------
  // Transformation
  // -----------------------------------------------------------
  /** Translate this object. A call to refresh() is needed after translation.
   * @param x H translation
   * @param y V translation
   * @see #restoreTransform()
   * @see #saveTransform()
   * @see #refresh
   */
  public void translate(double x, double y) {
    for (int i = 0; i < summit.length; i++) {
      summit[i].x += x;
      summit[i].y += y;
    }
    origin.x += x;
    origin.y += y;
    updateShape();
  }

  /** Scale, then translate this object. A call to refresh() is needed after transformation.
   * @param scaleX Scaling origin
   * @param scaleY Scaling origin
   * @param ratioX H scaling ratio
   * @param ratioY V scaling ration
   * @param transX H translation
   * @param transY V translation
   * @see #restoreTransform()
   * @see #saveTransform()
   * @see #refresh
   */
  public void scaleTranslate(double scaleX, double scaleY, double ratioX, double ratioY, double transX, double transY) {

    // Scale
    for (int i = 0; i < summit.length; i++) {
      summit[i].x = scaleX + ratioX * (summit[i].x - scaleX);
      summit[i].y = scaleY + ratioY * (summit[i].y - scaleY);
    }
    origin.x = scaleX + ratioX * (origin.x - scaleX);
    origin.y = scaleY + ratioY * (origin.y - scaleY);

    //Translate
    for (int i = 0; i < summit.length; i++) {
      summit[i].x += transX;
      summit[i].y += transY;
    }
    origin.x += transX;
    origin.y += transY;

    //Rebuild shape
    updateShape();

  }

  /** Scale this object. A call to refresh() is needed after transformation.
   * @param x Scaling origin
   * @param y Scaling origin
   * @param rx H scaling ratio
   * @param ry V scaling ration
   * @see #restoreTransform()
   * @see #saveTransform()
   * @see #refresh
   */
  public void scale(double x, double y, double rx, double ry) {
    for (int i = 0; i < summit.length; i++) {
      summit[i].x = x + rx * (summit[i].x - x);
      summit[i].y = y + ry * (summit[i].y - y);
    }
    origin.x = x + rx * (origin.x - x);
    origin.y = y + ry * (origin.y - y);
    updateShape();
  }

  /**
   * Rotate the object by 90deg. A call to refresh() is needed after transformation.
   * @param x Rotation center horizontal pos
   * @param y Rotation center vertical pos
   * @see #refresh
   */
  public void rotate90(double x,double y) {

    double px,py;
    int lgth = summit.length;

    // Rotate summit
    for (int i = 0;i<lgth; i++) {
      px = summit[i].x;
      py = summit[i].y;
      summit[i].x = x + (py-y);
      summit[i].y = y - (px-x);
    }

    // Rotate origin
    px = origin.x;
    py = origin.y;
    origin.x = x + (py-y);
    origin.y = y - (px-x);

    // Rotate gradient
    px = gradientX1;
    py = gradientY1;
    gradientX1 = (float) py;
    gradientY1 = (float)-px;
    px = gradientX2;
    py = gradientY2;
    gradientX2 = (float) py;
    gradientY2 = (float)-px;

    updateShape();

  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  abstract void saveObject(FileWriter f, int level) throws IOException;

  void loadDefaultPropery(JDFileLoader f, String propName) throws IOException {

    if (propName.equals("origin")) {
      origin = f.parsePoint();
    } else if (propName.equals("foreground")) {
      foreground = f.parseColor();
    } else if (propName.equals("background")) {
      background = f.parseColor();
    } else if (propName.equals("fillStyle")) {
      fillStyle = (int) f.parseDouble();
    } else if (propName.equals("lineWidth")) {
      lineWidth = (int) f.parseDouble();
    } else if (propName.equals("lineStyle")) {
      lineStyle = (int) f.parseDouble();
    } else if (propName.equals("antiAlias")) {
      antiAlias = f.parseBoolean();
    } else if (propName.equals("isShadowed")) {
      isShadowed = f.parseBoolean();
    } else if (propName.equals("invertShadow")) {
      invertShadow = f.parseBoolean();
    } else if (propName.equals("name")) {
      name = f.parseString();
    } else if (propName.equals("shadowThickness")) {
      shadowThickness = (int) f.parseDouble();
    } else if (propName.equals("visible")) {
      visible = f.parseBoolean();
    } else if (propName.equals("minvalue")) {
      minValue = (int)f.parseDouble();
    } else if (propName.equals("maxvalue")) {
      maxValue = (int)f.parseDouble();
    } else if (propName.equals("initvalue")) {
      initValue = (int)f.parseDouble();
    } else if (propName.equals("uservalue")) {
      userValue = f.parseBoolean();
    } else if (propName.equals("valuechangemode")) {
      valueChangeMode = (int)f.parseDouble();
    } else if (propName.equals("gradX1")) {
      gradientX1 = (int)f.parseDouble();
    } else if (propName.equals("gradY1")) {
      gradientY1 = (int)f.parseDouble();
    } else if (propName.equals("gradX2")) {
      gradientX2 = (int)f.parseDouble();
    } else if (propName.equals("gradY2")) {
      gradientY2 = (int)f.parseDouble();
    } else if (propName.equals("gradCyclic")) {
      gradientCyclic = f.parseBoolean();
    } else if (propName.equals("gradC1")) {
      gradientC1 = f.parseColor();
    } else if (propName.equals("gradC2")) {
      gradientC2 = f.parseColor();
    } else if (propName.equals("backgroundmapper")) {
      backgroundMapper = new JDValueProgram(f);
    } else if (propName.equals("foregroundmapper")) {
      foregroundMapper = new JDValueProgram(f);
    } else if (propName.equals("visibilitymapper")) {
      visibilityMapper = new JDValueProgram(f);
    } else if (propName.equals("htranslationmapper")) {
      hTranslationMapper = new JDValueProgram(f);
    } else if (propName.equals("vtranslationmapper")) {
      vTranslationMapper = new JDValueProgram(f);
    } else if (propName.equals("invertshadowmapper")) {
      invertShadowMapper = new JDValueProgram(f);
    } else if (propName.equals("extensions")) {
      loadObjectExtension(f);
    } else {
      System.out.println("Unknown property found:" + propName);
      f.jumpPropertyValue();
    }

  }

  private void loadObjectExtension(JDFileLoader f) throws IOException {

    Vector extN = new Vector();
    Vector extV = new Vector();

    f.startBlock();
    while (!f.isEndBlock()) {
      extN.add(f.parseProperyName());
      extV.add(f.parseParamString());
    }
    f.endBlock();

    int sz = extN.size();
    int i;

    if (sz > 0) {
      String[] strs = new String[sz];
      for (i = 0; i < sz; i++)
        strs[i] = (String) (extN.get(i));
      setExtensionList(strs);
      for (i = 0; i < sz; i++)
        setExtendedParam(i, (String) (extV.get(i)));
    }

  }

  void loadObject(JDFileLoader f) throws IOException {

    f.startBlock();
    summit = f.parseSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      loadDefaultPropery(f, propName);
    }

    f.endBlock();

  }

  void loadObject(JLXObject o) {

      foreground = o.style.lineColor;
      background = o.style.fillColor;
      fillStyle = o.style.fillStyle;
      lineWidth = o.style.lineWidth;
      lineStyle = o.style.lineStyle;
      isShadowed = (o.shadowWidth!=0);
      invertShadow = o.shadowWidth<0;
      name = o.name;
      shadowThickness = (o.shadowWidth<0)?-o.shadowWidth:o.shadowWidth;
      if(shadowThickness==0) shadowThickness=1;
      visible = o.visible;

      gradientX1 = o.style.gradientX1;
      gradientY1 = o.style.gradientY1;
      gradientX2 = o.style.gradientX2;
      gradientY2 = o.style.gradientY2;
      gradientC1 = o.style.gradientC1;
      gradientC2 = o.style.gradientC2;
      gradientCyclic = o.style.gradientCyclic;

  }

  void loadObject(LXObject o) {

      foreground = o.foreground;
      background = o.background;
      fillStyle = o.fillStyle;
      lineWidth = o.lineWidth;
      lineStyle = o.lineStyle;
      isShadowed = (o.shadowWidth!=0);
      invertShadow = o.invertShadow;
      name = o.name;
      shadowThickness = (o.shadowWidth<0)?-o.shadowWidth:o.shadowWidth;
      if(shadowThickness==0) shadowThickness=1;
      visible = o.visible;
      if(o.userClass!=0) {
        addExtension("UserClass");
        setExtendedParam("UserClass",Integer.toString(o.userClass));
      }

  }

  String roundDouble(double d) {

    String ret=null;
    boolean checkZero=false;
    boolean sign=false;

    if(d<0.0) {
      d=-d;
      sign=true;
    }

    int i = (int)(d*10000.0 + 0.5);
    int ipart = i/10000;
    int fpart = i%10000;

    if( fpart == 0 ) {
      ret = Integer.toString(ipart);
    } else if(fpart>0 && fpart<10) {
      ret = Integer.toString(ipart) + ".000" + Integer.toString(fpart);
    } else if(fpart>=10 && fpart<100) {
      checkZero = true;
      ret = Integer.toString(ipart) + ".00" + Integer.toString(fpart);
    } else if(fpart>=100 && fpart<1000) {
      checkZero = true;
      ret = Integer.toString(ipart) + ".0" + Integer.toString(fpart);
    } else {
      checkZero = true;
      ret = Integer.toString(ipart) + "." + Integer.toString(fpart);
    }

    if( checkZero ) {

      i = ret.length() - 1;
      while(checkZero && i>=0)  {
        checkZero = ret.charAt(i)=='0';
        if(checkZero) i--;
      }
      ret = ret.substring(0,i+1);

    }

    if( sign ) ret = "-" + ret;

    return ret;
  }

  private void saveMapper(FileWriter f,String name,JDValueProgram vm,String decal) throws IOException {

    String to_write;

    to_write = decal + name + ":{\n";
    f.write(to_write);
    vm.saveObject(f,decal+"  ");
    to_write = decal + "}\n";
    f.write(to_write);

  }

  private void saveExtensions(FileWriter f,String decal) throws IOException {

    String to_write;

    int sz = getExtendedParamNumber();
    if( sz>0 ) {
      int i,j;

      to_write = decal + "extensions:{\n";
      f.write(to_write);

      for (i = 0; i < sz; i++) {

        // Write extension name
        if( extParamName[i].indexOf(' ')>0 ) {
          to_write = decal + "  \"" + extParamName[i] + "\":";
        } else {
          to_write = decal + "  " + extParamName[i] + ":";
        }

        // Write extension value
        String decal2 = "";
        String[] vals = JDUtils.makeStringArray(extParamValue[i]);
        for(j=0;j<to_write.length();j++) decal2 += " ";

        for(j=0;j<vals.length;j++) {
          if(j>0) to_write = decal2;
          to_write += "\"";
          to_write += vals[j];
          to_write += "\"";
          if(j<vals.length-1) to_write += ",";
          to_write += "\n";
          f.write(to_write);
        }

      }

      to_write = decal + "}\n";
      f.write(to_write);

    }

  }

  void saveSummit(FileWriter f, String decal) throws IOException {

    String to_write;
    int i;

    to_write = decal + "summit:";
    for (i = 0; i < summit.length; i++) {
      if (i != summit.length - 1) {
        to_write += roundDouble(summit[i].x) + "," + roundDouble(summit[i].y) + ",";
      } else {
        to_write += roundDouble(summit[i].x) + "," + roundDouble(summit[i].y) + "\n";
      }
    }
    f.write(to_write, 0, to_write.length());

  }
  
  String saveObjectHeader(FileWriter f, int level) throws IOException {

    String to_write;
    String decal = "";
    int i;
    for (i = 0; i < level; i++) decal += "  ";

    to_write = decal + toString() + " {\n";
    f.write(to_write, 0, to_write.length());
    decal += "  ";

    saveSummit(f,decal);

    to_write = decal + "origin:" + roundDouble(origin.x) + "," + roundDouble(origin.y) + "\n";
    f.write(to_write, 0, to_write.length());

    if (foreground.getRGB() != foregroundDefault.getRGB()) {
      to_write = decal + "foreground:" + foreground.getRed() + "," + foreground.getGreen() + "," + foreground.getBlue() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (background.getRGB() != backgroundDefault.getRGB()) {
      to_write = decal + "background:" + background.getRed() + "," + background.getGreen() + "," + background.getBlue() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (fillStyle != fillStyleDefault) {
      to_write = decal + "fillStyle:" + fillStyle + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (lineWidth != lineWidthDefault) {
      to_write = decal + "lineWidth:" + lineWidth + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( antiAlias != antiAliasDefault ) {
      to_write = decal + "antiAlias:" + antiAlias + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (lineStyle != lineStyleDefault) {
      to_write = decal + "lineStyle:" + lineStyle + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (isShadowed != isShadowedDefault) {
      to_write = decal + "isShadowed:" + isShadowed + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (invertShadow != invertShadowDefault) {
      to_write = decal + "invertShadow:" + invertShadow + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (shadowThickness != shadowThicknessDefault) {
      to_write = decal + "shadowThickness:" + shadowThickness + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (visible != visibleDefault) {
      to_write = decal + "visible:" + visible + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( minValue != minValueDefault ) {
      to_write = decal + "minvalue:" + minValue + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( maxValue != maxValueDefault ) {
      to_write = decal + "maxvalue:" + maxValue + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( initValue != initValueDefault ) {
      to_write = decal + "initvalue:" + initValue + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( userValue != userValueDefault ) {
      to_write = decal + "uservalue:" + userValue + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( valueChangeMode != valueChangeModeDefault ) {
      to_write = decal + "valuechangemode:" + valueChangeMode + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (!name.equals(nameDefault)) {
      to_write = decal + "name:\"" + name + "\"\n";
      f.write(to_write, 0, to_write.length());
    }

    if( gradientX1 != gradientX1default ) {
      to_write = decal + "gradX1:" + gradientX1 + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( gradientX2 != gradientX2default ) {
      to_write = decal + "gradX2:" + gradientX2 + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( gradientY1 != gradientY1default ) {
      to_write = decal + "gradY1:" + gradientY1 + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if( gradientY2 != gradientY2default ) {
      to_write = decal + "gradY2:" + gradientY2 + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (gradientCyclic != gradientCyclicdefault) {
      to_write = decal + "gradCyclic:" + gradientCyclic + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (gradientC1.getRGB() != gradientC1default.getRGB()) {
      to_write = decal + "gradC1:" + gradientC1.getRed() + "," + gradientC1.getGreen() + "," + gradientC1.getBlue() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (gradientC2.getRGB() != gradientC2default.getRGB()) {
      to_write = decal + "gradC2:" + gradientC2.getRed() + "," + gradientC2.getGreen() + "," + gradientC2.getBlue() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    saveExtensions(f,decal);
    if(hasBackgroundMapper()) saveMapper(f,"backgroundmapper",backgroundMapper,decal);
    if(hasForegroundMapper()) saveMapper(f,"foregroundmapper",foregroundMapper,decal);
    if(hasVisibilityMapper()) saveMapper(f,"visibilitymapper",visibilityMapper,decal);
    if(hasInvertShadowMapper()) saveMapper(f,"invertshadowmapper",invertShadowMapper,decal);
    if(hasHTranslationMapper()) saveMapper(f,"htranslationmapper",hTranslationMapper,decal);
    if(hasVTranslationMapper()) saveMapper(f,"vtranslationmapper",vTranslationMapper,decal);

    return decal;
  }

  void closeObjectHeader(FileWriter f, int level) throws IOException {

    String to_write;
    String decal = "";
    for (int i = 0; i < level; i++) decal += "  ";

    to_write = decal + "}\n";
    f.write(to_write, 0, to_write.length());

  }

  // -----------------------------------------------------------
  // Undo
  // -----------------------------------------------------------
  abstract UndoPattern getUndoPattern();

  void fillUndoPattern(UndoPattern e) {

    e.xOrigin = origin.x;
    e.yOrigin = origin.y;
    e.summit = new double[summit.length * 2];
    for (int i = 0; i < summit.length; i++) {
      e.summit[2 * i + 0] = summit[i].x;
      e.summit[2 * i + 1] = summit[i].y;
    }
    e.rgbForeground = foreground.getRGB();
    e.rgbBackground = background.getRGB();
    e.fillStyle = fillStyle;
    e.lineWidth = lineWidth;
    e.lineStyle = lineStyle;
    e.antiAlias = antiAlias;
    e.isShadowed = isShadowed;
    e.invertShadow = invertShadow;
    e.name = new String(name);
    e.shadowThickness = shadowThickness;
    e.visible = visible;
    e.minValue = minValue;
    e.maxValue = maxValue;
    e.initValue = initValue;
    e.userValue = userValue;
    e.valueChangeMode = valueChangeMode;

    if (hasBackgroundMapper()) e.backgroundMapper = backgroundMapper.copy();
    if (hasForegroundMapper()) e.foregroundMapper = foregroundMapper.copy();
    if (hasVisibilityMapper()) e.visibilityMapper = visibilityMapper.copy();
    if (hasInvertShadowMapper()) e.invertShadowMapper = invertShadowMapper.copy();
    if (hasHTranslationMapper()) e.hTranslationMapper = hTranslationMapper.copy();
    if (hasVTranslationMapper()) e.vTranslationMapper = vTranslationMapper.copy();

    e.gradientX1 = gradientX1;
    e.gradientX2 = gradientX2;
    e.gradientY1 = gradientY1;
    e.gradientY2 = gradientY2;
    e.gradientC1 = gradientC1;
    e.gradientC2 = gradientC2;
    e.gradientCyclic = gradientCyclic;

    e.extsN = extParamName;
    if (e.extsN != null) {
      e.extsV = new String[e.extsN.length];
      for (int i = 0; i < e.extsN.length; i++) e.extsV[i] = new String(extParamValue[i]);
    }


  }

  void applyUndoPattern(UndoPattern e) {

    int nbS = e.summit.length/2;
    origin = new Point.Double(e.xOrigin, e.yOrigin);
    summit = new Point.Double[nbS];
    for(int i=0;i<nbS;i++) summit[i] = new Point.Double(e.summit[2*i], e.summit[2*i+1]);
    foreground = new Color(e.rgbForeground);
    background = new Color(e.rgbBackground);
    fillStyle = e.fillStyle;
    lineWidth = e.lineWidth;
    lineStyle = e.lineStyle;
    antiAlias = e.antiAlias;
    isShadowed = e.isShadowed;
    invertShadow = e.invertShadow;
    name = e.name;
    shadowThickness = e.shadowThickness;
    visible = e.visible;
    minValue  = e.minValue;
    maxValue  = e.maxValue;
    initValue = e.initValue;
    userValue = e.userValue;
    valueChangeMode = e.valueChangeMode;

    if(e.backgroundMapper!=null)   backgroundMapper = e.backgroundMapper.copy();
    if(e.foregroundMapper!=null)   foregroundMapper = e.foregroundMapper.copy();
    if(e.visibilityMapper!=null)   visibilityMapper = e.visibilityMapper.copy();
    if(e.invertShadowMapper!=null) invertShadowMapper = e.invertShadowMapper.copy();
    if(e.hTranslationMapper!=null) hTranslationMapper = e.hTranslationMapper.copy();
    if(e.vTranslationMapper!=null) vTranslationMapper = e.vTranslationMapper.copy();

    gradientX1=e.gradientX1;
    gradientX2=e.gradientX2;
    gradientY1=e.gradientY1;
    gradientY2=e.gradientY2;
    gradientC1=e.gradientC1;
    gradientC2=e.gradientC2;
    gradientCyclic=e.gradientCyclic;

    extParamName = e.extsN;
    if (e.extsN != null) {
      extParamValue = new String[e.extsN.length];
      for (int i = 0; i < e.extsN.length; i++)
        extParamValue[i] = new String(e.extsV[i]);
    }

  }

  /** Restore original shape previously backuped by saveTransform
   * @see #saveTransform
   */
  public void restoreTransform() {

    origin.x = sXOrg;
    origin.y = sYOrg;
    for(int i=0;i<sSummit.length/2;i++) {
      summit[i].x = sSummit[2*i];
      summit[i].y = sSummit[2*i+1];
    }
    gradientX1=sGradientX1;
    gradientX2=sGradientX2;
    gradientY1=sGradientY1;
    gradientY2=sGradientY2;

    updateShape();

  }

  /** Backup the shape. This can be usefull when making scaling animation, after
   * multiple scale the rounding may result in deformed shape. To avoid this
   * you can use saveTransform() and restoreTransform().
   * Note: This is done once when JDrawEditor.loadFile() is called().
   * @see #restoreTransform
   */
  public void saveTransform() {

    sSummit = new double[summit.length*2];
    for(int i=0;i<summit.length;i++) {
      sSummit[2*i] = summit[i].x;
      sSummit[2*i+1] = summit[i].y;
    }
    sXOrg = origin.x;
    sYOrg = origin.y;

    sGradientX1=gradientX1;
    sGradientX2=gradientX2;
    sGradientY1=gradientY1;
    sGradientY2=gradientY2;

  }

  // -----------------------------------------------------------
  // Shadow stuff
  // -----------------------------------------------------------

  abstract void updateShape();

  Rectangle getShadowBoundRect() {
    return sBoundRect;
  }

  void getMinMax(int[] p, int[] m) {

    int min = 65536;
    int max = 0;

    for (int i = 0; i < p.length; i++) {
      if (p[i] <= min) min = p[i];
      if (p[i] >= max) max = p[i];
    }

    if (min < 0) min = 0;
    if (max > 65536) max = 65536;
    m[0] = min;
    m[1] = max;
  }

  void computeNextShadowSegment(int i, Polygon p, double[] ret) {

    double ux;
    double uy;
    double vx;
    double vy;
    double cx;
    double cy;
    double n;
    int inext;
    int icur;
    double s;
    int nb = ptsx.length;

    inext = i + 2;
    if (inext >= nb) inext -= nb;
    icur = i + 1;
    if (icur >= nb) icur -= nb;

    if (normes[i] < 1.0 || normes[icur] < 1.0) {
      cx = 0.0;
      cy = 0.0;
    } else {

      ux = (double) (ptsx[inext] - ptsx[icur]) / normes[icur];
      uy = (double) (ptsy[inext] - ptsy[icur]) / normes[icur];
      vx = (double) (ptsx[i] - ptsx[icur]) / normes[i];
      vy = (double) (ptsy[i] - ptsy[icur]) / normes[i];
      cx = ux + vx;
      cy = uy + vy;
      n = Math.sqrt(cx * cx + cy * cy);

      if (n <= 1e-5) {

        // Flat line return normal vector
        cx = -(ptsy[icur] - ptsy[i]);
        cy = (ptsx[icur] - ptsx[i]);
        n = Math.sqrt(cx * cx + cy * cy);
        if (n < 1.0) {
          cx = 0.0;
          cy = 0.0;
        } else {
          cx = cx / n;
          cy = cy / n;
        }

      } else {
        cx = cx / n;
        cy = cy / n;
        s = cx * ux + cy * uy;
        s = Math.sqrt(1.0 - s * s);
        //System.out.println("Scalaire[" + i + "]=" + s);
        cx = cx / s;
        cy = cy / s;
      }

      // Check if generated point is inside the polygon
      if (!p.contains(ptsx[icur] + (int) (cx * 4.0), ptsy[icur] + (int) (cy * 4.0))) {
        cx = -cx;
        cy = -cy;
      }


    }

    ret[0] = cx;
    ret[1] = cy;
  }

  Color computeShadowColor(int i, int inext, Polygon p, double[] yuv) {

    double nx = -(ptsy[inext] - ptsy[i]);
    double ny = (ptsx[inext] - ptsx[i]);
    double n = Math.sqrt(nx * nx + ny * ny);
    double l;

    if (n < 1.0) {
      nx = 0.0;
      ny = 0.0;
    } else {
      nx = nx / n;
      ny = ny / n;
    }

    int vx = (int) (nx * 4.0);
    int vy = (int) (ny * 4.0);
    if (!p.contains((ptsx[inext] + ptsx[i]) / 2 + vx, (ptsy[inext] + ptsy[i]) / 2 + vy)) {
      nx = -nx;
      ny = -ny;
    }

    //Color depends on cosine between normal and light vector
    if (!invertShadow)
      l = lightx * nx + lighty * ny;
    else
      l = lightx * (-nx) + lighty * (-ny);

    double Y;
    double delta = l * 128;

    if (delta > 0.0 && delta < 80.0) {
      delta = 80;
    }

    if (delta <= 0.0 && delta > -20.0) {
      delta = -20;
    }

    Y = yuv[0] + delta;
    if (Y < 0.0) Y = 0.0;
    if (Y > 255.0) Y = 255.0;

    return createColorFromYUV(Y, yuv[1], yuv[2]);
  }

  void RGBtoYUV(Color c, double[] yuv) {
    double R = (double) c.getRed();
    double G = (double) c.getGreen();
    double B = (double) c.getBlue();

    yuv[0] = 0.299 * R + 0.587 * G + 0.114 * B;
    yuv[1] = -0.169 * R - 0.331 * G + 0.500 * B + 128.0;
    yuv[2] = 0.500 * R - 0.419 * G - 0.081 * B + 128.0;
  }

  Color createColorFromYUV(double Y, double U, double V) {

    int r = (int) (Y + 1.4075 * (V - 128.0));
    int g = (int) (Y - 0.7169 * (V - 128.0) - 0.3455 * (U - 128.0));
    int b = (int) (Y + 1.779 * (U - 128.0));

    if (r > 255) r = 255;
    if (r < 0) r = 0;
    if (g > 255) g = 255;
    if (g < 0) g = 0;
    if (b > 255) b = 255;
    if (b < 0) b = 0;
    return new Color(r, g, b);

  }

  void computeShadow(boolean isClosed) {

    int i;
    int nb;
    int minx = 65536;
    int miny = 65536;
    int maxx = 0;
    int maxy = 0;

    if( isClosed )
      nb = ptsx.length;
    else
      nb = ptsx.length-1;

    Polygon poly = new Polygon(ptsx, ptsy, ptsx.length);

    // Tmp variable
    double[] c = new double[2];
    normes = new double[ptsx.length];
    Polygon[] nShadows = new Polygon[nb];
    double cx;
    double cy;
    int[] shx = new int[4];
    int[] shy = new int[4];
    double st = (double) shadowThickness;
    int[] m = new int[2];

    // --------------------------------------------------------------------
    // Compute norme off all segments in the polyline
    // --------------------------------------------------------------------
    for (i = 0; i <  ptsx.length - 1; i++) {
      cx = (double) ((ptsx[i + 1] - ptsx[i]) * (ptsx[i + 1] - ptsx[i]));
      cy = (double) ((ptsy[i + 1] - ptsy[i]) * (ptsy[i + 1] - ptsy[i]));
      normes[i] = Math.sqrt(cx + cy);
    }
    cx = (double) ((ptsx[0] - ptsx[i]) * (ptsx[0] - ptsx[i]));
    cy = (double) ((ptsy[0] - ptsy[i]) * (ptsy[0] - ptsy[i]));
    normes[i] = Math.sqrt(cx + cy);

    // --------------------------------------------------------------------
    // Compute shapes
    // --------------------------------------------------------------------

    //Initialise first calcul step
    computeNextShadowSegment(ptsx.length - 1, poly, c);

    for (i = 0; i < nb; i++) {

      //Calculate shadow coodinates
      shx[0] = ptsx[i];
      shy[0] = ptsy[i];
      shx[1] = ptsx[i] + (int)Math.round(st * c[0]);
      shy[1] = ptsy[i] + (int)Math.round(st * c[1]);

      computeNextShadowSegment(i, poly, c);

      //Calculate shadow coodinates
      int inext = i + 1;
      if (inext >= ptsx.length) inext = 0;
      shx[2] = ptsx[inext] + (int)Math.round(st * c[0]);
      shy[2] = ptsy[inext] + (int)Math.round(st * c[1]);
      shx[3] = ptsx[inext];
      shy[3] = ptsy[inext];

      //Get Bounding rect
      getMinMax(shx, m);
      if (m[0] <= minx) minx = m[0];
      if (m[1] >= maxx) maxx = m[1];
      getMinMax(shy, m);
      if (m[0] <= miny) miny = m[0];
      if (m[1] >= maxy) maxy = m[1];

      //Create the polygon
      nShadows[i] = new Polygon(shx, shy, 4);

    }

    // Set up shadow
    shadows = nShadows;

    // Create the shadow boundRect
    sBoundRect.setBounds(minx, miny, maxx - minx + 1, maxy - miny + 1);
    sBoundRect = sBoundRect.union(boundRect);

  }

  void computeShadowColors() {

    int nb = ptsx.length;
    // Convert color to YUV space
    double[] yuv = new double[3];
    if (foreground != null)
      RGBtoYUV(foreground, yuv);
    else {
      yuv[0] = 0.0;
      yuv[1] = 128.0;
      yuv[2] = 128.0;
    }

    Polygon poly = new Polygon(ptsx, ptsy, nb);
    shadowColors = new Color[nb];
    int inext;
    for (int i = 0; i < nb; i++) {
      inext = i + 1;
      if (inext >= nb) inext = 0;
      shadowColors[i] = computeShadowColor(i, inext, poly, yuv);
    }

  }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------
  String getNodeName() {

    String className = getClass().toString();
    int idx = className.lastIndexOf('.');
    if(idx>0) className = className.substring(idx+1);

    String treeName = (name.length()>=0)?name:className;

    if( isInteractive() )
      treeName += "*";

    return treeName;

  }

  /**
   * Shows or hides this object.
   * @param b True to show, false otherwise.
   */
  public void setVisible(boolean b) {
    visible = b;
  }

  /**
   * Determines whether this object is visible.
   */
  public boolean isVisible() {
    return visible;
  }

  /**
   * Sets the name of this object.
   * @param s Object name
   */
  public void setName(String s) {
    name = s;
  }

  /**
   * Returns the current name of this object.
   */
  public String getName() {
    return name;
  }

  /**
   * Sets the background color (usualy fill color) of this object.
   * @param c Background color
   */
  public void setBackground(Color c) {
    background = c;
  }

  /**
   * Returns the current background color of this object.
   * @see #setBackground
   */
  public Color getBackground() {
    return background;
  }

  /**
   * Sets the foreground color (usualy line color) of this object.
   * This color is also used for base shadow color.
   * @param c Foreground color
   */
  public void setForeground(Color c) {
    foreground = c;
    if (hasShadow()) computeShadowColors();
  }

  /**
   * Returns the current foreground color of this object.
   * @see #setForeground
   */
  public Color getForeground() {
    return foreground;
  }

  /**
   * Sets the origin of this object.
   * @param p Origin point.
   */
  public void setOrigin(Point.Double p) {
    origin = p;
  }

  /** Center the origin. */
  public void centerOrigin() {
    origin.x = boundRect.x + boundRect.width/2;
    origin.y = boundRect.y + boundRect.height/2;
  }

  /**
   * Returns the current origin.
   */
  public Point.Double getOrigin() {
    return origin;
  }

  public String toString() {
    String className = getClass().getName();
    int pos = className.lastIndexOf('.');
    if (pos != -1) className = className.substring(pos + 1);
    return className;
  }

  /**
   * Sets the fill style of this object.
   * @param style Fill style
   * @see #FILL_STYLE_NONE
   * @see #FILL_STYLE_SOLID
   * @see #FILL_STYLE_LARGE_RIGHT_HATCH
   * @see #FILL_STYLE_LARGE_LEFT_HATCH
   * @see #FILL_STYLE_LARGE_CROSS_HATCH
   * @see #FILL_STYLE_SMALL_RIGHT_HATCH
   * @see #FILL_STYLE_SMALL_LEFT_HATCH
   * @see #FILL_STYLE_SMALL_CROSS_HATCH
   * @see #FILL_STYLE_DOT_PATTERN_1
   * @see #FILL_STYLE_DOT_PATTERN_2
   * @see #FILL_STYLE_DOT_PATTERN_3
   * @see #FILL_STYLE_GRADIENT
   */
  public void setFillStyle(int style) {
    fillStyle = style;
  }

  /**
   * Returns the current fill style of this object.
   * @see #setFillStyle
   */
  public int getFillStyle() {
    return fillStyle;
  }

  /**
   * Sets the line style.
   * @param style Line style
   * @see #LINE_STYLE_SOLID
   * @see #LINE_STYLE_DOT
   * @see #LINE_STYLE_DASH
   * @see #LINE_STYLE_LONG_DASH
   * @see #LINE_STYLE_DASH_DOT
   */
  public void setLineStyle(int style) {
    lineStyle = style;
  }

  /**
   * Returns the current line style of this object.
   * @see #setLineStyle
   */
  public int getLineStyle() {
    return lineStyle;
  }

  /**
   * Enables or disables the anti aliasing for this object.
   * @param aliasing True to enable antialiasing, false otherwise
   */
  public void setAntiAlias(boolean aliasing) {
    antiAlias = aliasing;
  }

  /**
   * Determines wheter this object is anti aliased.
   */
  public boolean isAntiAliased() {
    return antiAlias;
  }

  /**
   * Sets the line width of this object.
   * @param width Line width (pixel)
   */
  public void setLineWidth(int width) {
    lineWidth = width;
  }

  /**
   * Returns the current line width of this object.
   */
  public int getLineWidth() {
    return lineWidth;
  }

  /**
   * Returns true only if this object is shadowed.
   */
  public boolean hasShadow() {
    return isShadowed;
  }

  /**
   * Enables or disabled shadow for this object. By default
   * shadow represents a lowered bevel border. To change
   * the shadow orientation, you can call setInverseShadow().
   * @param b Shadow flag.
   * @see #setInverseShadow
   */
  public void setShadow(boolean b) {
    isShadowed = b;
    updateShape();
  }

  /**
   * Sets the shadow thickness of this object.
   * @param w Shadow thickness.
   */
  public void setShadowWidth(int w) {
    shadowThickness = w;
    updateShape();
  }

  /**
   * Returns the current shadow thickness.
   * @see #setShadowWidth
   */
  public int getShadowWidth() {
    return shadowThickness;
  }

  /**
   * Determines whether this object has inverse shadow.
   * @see #setInverseShadow
   */
  public boolean hasInverseShadow() {
    return invertShadow;
  }

  /**
   * Sets inverse shadow for this object.
   * @param b Inverse shadow flag.
   * @see #setShadow
   */
  public void setInverseShadow(boolean b) {
    invertShadow = b;
    if (hasShadow()) computeShadowColors();
  }

  /**
   * Sets the minimum value of this object.
   * @param min Min value
   * @see #setInitValue
   * @see #setMaxValue
   * @see #setValue
   */
  public void setMinValue(int min) {
    minValue = min;
  }

  /**
   * Returns the minimum value of this object.
   * @see #setMinValue
   */
  public int getMinValue() {
    return minValue;
  }

  /**
   * Sets the max value of this object.
   * @param max Max value
   * @see #setInitValue
   * @see #setMinValue
   * @see #setValue
   */
  public void setMaxValue(int max) {
    maxValue = max;
  }

  /**
   * Returns the maximum value of this object.
   * @see #setMaxValue
   */
  public int getMaxValue() {
    return maxValue;
  }

  /**
   * Sets the init value of this object.
   * @param i Initial value object.
   * @see #setMaxValue
   * @see #setMinValue
   * @see #setValue
   */
  public void setInitValue(int i) {
    initValue = i;
  }

  /**
   * Returns the init value of this object.
   * @see #setInitValue
   */
  public int getInitValue() {
    return initValue;
  }

  /**
   * Determines whether this object is interactive.
   * @see #setInteractive
   */
  public boolean isInteractive() {
    return userValue;
  }

  /**
   * Enables or disabled the interactivity. When enabled the object value
   * change with user interaction.
   * @param b Interactive flag.
   * @see #setValueChangeMode
   * @see #setValue
   */
  public void setInteractive(boolean b) {
    userValue=b;
  }

  /**
   * Returns the value change mode of this object for user interaction.
   * @see #setValueChangeMode
   */
  public int getValueChangeMode() {
    return valueChangeMode;
  }

  /**
   * Sets the value change mode of this object for user interaction.
   * @param m Interaction mode
   * @see #VALUE_INC_ON_PRESSRELEASE
   * @see #VALUE_CHANGE_ON_XDRAG_LEFT
   * @see #VALUE_CHANGE_ON_XDRAG_RIGHT
   * @see #VALUE_CHANGE_ON_YDRAG_TOP
   * @see #VALUE_CHANGE_ON_YDRAG_BOTTOM
   */
  public void setValueChangeMode(int m) {
    valueChangeMode=m;
  }

  /**
   * Determines whether this object has a value program for background color.
   * @see #setBackgroundMapper
   */
  public boolean hasBackgroundMapper() {
    return backgroundMapper!=null;
  }

  /**
   * Sets the value program for background color of this object.
   * @param m Value program.
   * @see #isProgrammed
   */
  public void setBackgroundMapper(JDValueProgram m) {
    backgroundMapper=m;
  }

  /**
   * Returns the current value program for background color of this object.
   */
  public JDValueProgram getBackgroundMapper() {
    return backgroundMapper;
  }


  /**
   * Determines whether this object has a value program for foreground color.
   * @see #setForegroundMapper
   */
  public boolean hasForegroundMapper() {
    return foregroundMapper!=null;
  }

  /**
   * Sets the value program for foreground color of this object.
   * @param m Value program.
   * @see #isProgrammed
   */
  public void setForegroundMapper(JDValueProgram m) {
    foregroundMapper=m;
  }

  /**
   * Returns the current value program for foreground color of this object.
   */
  public JDValueProgram getForegroundMapper() {
    return foregroundMapper;
  }

  /**
   * Determines whether this object has a value program for visibility.
   * @see #setVisibilityMapper
   */
  public boolean hasVisibilityMapper() {
    return visibilityMapper!=null;
  }

 /**
  * Sets the value program for visibility of this object.
  * @param m Value program.
  * @see #isProgrammed
  */
  public void setVisibilityMapper(JDValueProgram m) {
    visibilityMapper=m;
  }

  /**
   * Returns the current value program for visibility of this object.
   */
  public JDValueProgram getVisibilityMapper() {
    return visibilityMapper;
  }

  /**
   * Determines whether this object has a value program for invert shadow.
   * @see #setInvertShadowMapper
   */
  public boolean hasInvertShadowMapper() {
    return invertShadowMapper!=null;
  }

  /**
   * Sets the value program for invert shadow of this object.
   * @param m Value program.
   * @see #isProgrammed
   */
  public void setInvertShadowMapper(JDValueProgram m) {
    invertShadowMapper=m;
  }

  /**
   * Returns the current value program for invert shadow of this object.
   */
  public JDValueProgram getInvertShadowMapper() {
    return invertShadowMapper;
  }

  /**
   * Determines whether this object has a value program for horizontal translation.
   * @see #setHTranslationMapper
   */
  public boolean hasHTranslationMapper() {
    return hTranslationMapper!=null;
  }

  /**
   * Sets the value program for horizontal translation of this object.
   * @param m Value program.
   * @see #isProgrammed
   */
  public void setHTranslationMapper(JDValueProgram m) {
    hTranslationMapper=m;
  }

  /**
   * Returns the current value program for horizontal translation of this object.
   */
  public JDValueProgram getHTranslationMapper() {
    return hTranslationMapper;
  }

  /**
   * Determines whether this object has a value program for vertical translation.
   * @see #setVTranslationMapper
   */
  public boolean hasVTranslationMapper() {
    return vTranslationMapper!=null;
  }

  /**
   * Sets the value program for vertical translation of this object.
   * @param m Value program.
   * @see #isProgrammed
   */
  public void setVTranslationMapper(JDValueProgram m) {
    vTranslationMapper=m;
  }

  /**
   * Returns the current value program for vertical translation of this object.
   */
  public JDValueProgram getVTranslationMapper() {
    return vTranslationMapper;
  }

  void prepareRendering(Graphics2D g2) {
    if(antiAlias)
      g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
    else
      g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_OFF);
  }

  /**
   * Sets the gradient of this object. Has effects only if fill style is FILL_STYLE_GRADIENT.
   * @param x1 x coordinate of the first specified
   * <code>Point</code> in user space
   * @param y1 y coordinate of the first specified
   * <code>Point</code> in user space
   * @param color1 <code>Color</code> at the first specified
   * <code>Point</code>
   * @param x2 x coordinate of the second specified
   * <code>Point</code> in user space
   * @param y2 y coordinate of the second specified
   * <code>Point</code> in user space
   * @param color2 <code>Color</code> at the second specified
   * <code>Point</code>
   * @param cyclic <code>true</code> if the gradient pattern should cycle
   * repeatedly between the two colors; <code>false</code> otherwise
   * @see #setFillStyle
   */
  public void setGradientFillParam(float x1, float y1, Color color1, float x2, float y2, Color color2, boolean cyclic) {
    gradientX1=x1;
    gradientX2=x2;
    gradientY1=y1;
    gradientY2=y2;
    gradientC1=color1;
    gradientC2=color2;
    gradientCyclic=cyclic;
  }

  void setParent(JDrawEditor p) {
    parent = p;
  }

  JDrawEditor getParent() {
    return parent;
  }

  /** Determines whether this object has a programmed behavior. If this object is
    * a JDGroup, the function return true if at least one of grouped JDObject is programmed.
    * @see #setValue
    */
  public boolean isProgrammed() {
    return hasValueProgram();
  }

  /**
   * Refresh the JDObject on the screen by repainting
   * its bounding rectangle. This method
   * shoud be called after a property change.
   * @see #translate
   * @see #scaleTranslate
   * @see #scale
   * @see #moveSummit
   * @see #preRefresh
   */
  public void refresh() {
    if ( parent!=null ) {
      if(preRefreshRect!=null)
        parent.repaint(preRefreshRect.union(getRepaintRect()));
      else
        parent.repaint(getRepaintRect());
    }
    preRefreshRect = null;
  }

  /**
   * Prepare this object to be repainted. Certain modifications
   * of the object may need to be repainted outside the new bounding
   * rectangle. So before applying modifcations to the object , a call
   * to preRefresh() will memorize the current repaint region
   * then a call to refresh() after mofications will repaint the
   * union of the 2 rectangles.
   * @see #refresh
   */
  public void preRefresh() {
    preRefreshRect = getRepaintRect();
  }

  /**
   * Sets the list of extended parameter name for this object.
   * Note: All value are reseted.
   * @param names List of names
   */
  public void setExtensionList(String[] names) {
    extParamName  = names;
    extParamValue = new String[names.length];
    for(int i=0;i<extParamValue.length;i++)
      extParamValue[i] = "";
  }

  /**
   * Add an extension to this object.
   * @param name Name of the extension.
   * @see #setExtensionList
   */
  public void addExtension(String name) {

    int i = getExtendedParamIndex(name);
    if(i!=-1) {
      //Extension already exists
      return;
    }

    int nbExt = getExtendedParamNumber();

    String[] newExts   = new String[nbExt+1];
    String[] newValues = new String[nbExt+1];

    for(i=0;i<nbExt;i++) {
      newExts[i] = extParamName[i];
      newValues[i] = extParamValue[i];
    }
    newExts[i]=name;
    newValues[i]="";

    extParamName=newExts;
    extParamValue=newValues;

  }

  /**
   * Sets the extended param value.
   * @param name Param name
   * @param value Param value
   * @see #setExtensionList
   */
  public void setExtendedParam(String name,String value) {

    int i = getExtendedParamIndex(name);
    if(i!=-1) extParamValue[i] = value;
    else System.out.println("JDObject.setExtendedParam() : " + name + " does not exist for " + getName() + ".");

  }

  /**
   * Remove the extended param at the specified index.
   * @param extIdx Index of the extension.
   */
  public void removeExtension(int extIdx) {

    int nbExt = getExtendedParamNumber();
    if(extIdx >= nbExt || extIdx<0) {
      System.out.println("JDObject.removeExtension() : " + extIdx + " index out of bounds.");
      return;
    }
    int i;

    String[] newExts   = new String[nbExt-1];
    String[] newValues = new String[nbExt-1];

    for(i=0;i<extIdx;i++) {
      newExts[i] = extParamName[i];
      newValues[i] = extParamValue[i];
    }

    for(i=extIdx+1;i<nbExt;i++) {
      newExts[i-1] = extParamName[i];
      newValues[i-1] = extParamValue[i];
    }

    extParamName=newExts;
    extParamValue=newValues;

  }

  /**
   * Sets the extended param value.
   * @param extIdx Index of the extensions.
   * @param value param value
   * @see #setExtensionList
   */
  public void setExtendedParam(int extIdx,String value) {
    int n = getExtendedParamNumber();
    if( extIdx<0 || extIdx>=n ) {
      System.out.println("JDObject.setExtendedParam() : index of of bounds.");
      return;
    }
    extParamValue[extIdx] = value;
  }

  /**
   * Returns the value of the specified extended param, an empty string if not found.
   * @param name Extension name
   * @return param value
   * @see #setExtensionList
   */
  public String getExtendedParam(String name) {
    int i = getExtendedParamIndex(name);
    if(i!=-1) return extParamValue[i];
    else {
      System.out.println("JDObject.getExtendedParam() : " + name + " does not exist.");
      return "";
    }
  }

  /**
   * Returns the value of the specified extended param, an empty string if not found.
   * @param extIdx Index of the extension.
   * @return param value
   * @see #setExtensionList
   */
  public String getExtendedParam(int extIdx) {
    int n = getExtendedParamNumber();
    if( extIdx<0 || extIdx>=n ) {
      System.out.println("JDObject.getExtendedParam() : index of of bounds.");
      return "";
    }
    return extParamValue[extIdx];
  }

  /**
   * Returns the name of the extended param at the specified index.
   * @param extIdx Index of the extension.
   * @return param name
   * @see #setExtensionList
   */
  public String getExtendedParamName(int extIdx) {

    int n = getExtendedParamNumber();
    if( extIdx<0 || extIdx>=n ) {
      System.out.println("JDObject.getExtendedParamName() : index of of bounds.");
      return "";
    }
    return extParamName[extIdx];

  }

  /**
   * Returns the description of the specified extension.
   * @param extName Extension name
   */
  public String getExtendedParamDesc(String extName) {
    return "";
  }

  /** Returns the number of extensions */
  public int getExtendedParamNumber() {
   if( extParamValue == null )
     return 0;
    else
     return extParamValue.length;
  }

  /** Returns the index of the specified extended param , -1 when not found */
  public int getExtendedParamIndex(String name) {

    if( extParamName==null )
      return -1;

    boolean found = false;
    int i=0;
    while(i<extParamName.length && !found) {
      found = name.equalsIgnoreCase(extParamName[i]);
      if(!found) i++;
    }

    if( found )
      return i;
    else
      return -1;

  }

  /** returns true if the specified extended param exists , false otherwise 
   *  srubio@cells.es: modified to search within ExtensionsLists extension for new non-valued extensions.
   */
  public boolean hasExtendedParam(String name) {
    if (getExtendedParamIndex(name)>=0) return true;
    int idx=getExtendedParamIndex("ExtensionsList");
    if (idx>=0) {
		if (getExtendedParam(idx).toLowerCase().indexOf(name.toLowerCase())>=0) return true;
		else return false;
    } else return false;
  }

  /** returns true if this parameters is fixed and cannot be removed. */
  public boolean isFixedExtendedParam(String name) {
    return false;
  }

}