package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.FileWriter;
import java.io.IOException;

/** JDraw Ellipse graphic object.
 *  <p>Here is an example of few JDEllipse:<p>
 *  <img src="JDEllipse.gif" border="0" alt="JDEllipse examples"></img>
 */
public class JDEllipse extends JDRectangular implements JDPolyConvert {

  /** Opened arc */
  public final static int ARC_OPEN   = 0;
  /** Closed arc */
  public final static int ARC_CLOSED = 1;
  /** Pie arc */
  public final static int ARC_PIE    = 2;

  // Default Properties
  static final int stepDefault        = 36;
  static final int angleStartDefault  = 0;
  static final int angleExtentDefault = 360;
  static final int arcTypeDefault     = ARC_OPEN;

  // Vars
  int step;
  int arcType;
  int angleStart;
  int angleExtent;
  int sAngleStart;
  private boolean useOval = false;
  private double x1;
  private double y1;
  private double width;
  private double height;

  /**
   * Construct a JDEllipse.
   * @param objectName
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   * @param w Ellipse width
   * @param h Ellipse height
   */
  public JDEllipse(String objectName,int x,int y,int w,int h) {
    initDefault();
    setOrigin(new Point.Double(x,y));
    summit = new Point.Double[8];
    name = objectName;
    createSummit();
    computeSummitCoordinates(x, y, w,h);
    updateShape();
  }

  JDEllipse(JDEllipse e,int x,int y) {
    cloneObject(e,x,y);
    step = e.step;
    arcType = e.arcType;
    angleStart = e.angleStart;
    angleExtent = e.angleExtent;
    updateShape();
  }

  JDEllipse(JLXObject jlxObj,int a,int b,int atype) {

    initDefault();
    loadObject(jlxObj);

    double x = jlxObj.boundRect.getX();
    double y = jlxObj.boundRect.getY();
    double w = jlxObj.boundRect.getWidth();
    double h = jlxObj.boundRect.getHeight();

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[8];
    createSummit();

    summit[0].x = x;
    summit[0].y = y;

    summit[1].x = x+w/2;
    summit[1].y = y;

    summit[2].x = x+w;
    summit[2].y = y;

    summit[3].x = x+w;
    summit[3].y = y+h/2;

    summit[4].x = x+w;
    summit[4].y = y+h;

    summit[5].x = x+w/2;
    summit[5].y = y+h;

    summit[6].x = x;
    summit[6].y = y+h;

    summit[7].x = x;
    summit[7].y = y+h/2;

    step = stepDefault;
    angleStart  = a;
    angleExtent = b;
    if(fillStyle==JDObject.FILL_STYLE_NONE)
      arcType = ARC_OPEN;
    else
      arcType = (atype==1)?ARC_CLOSED:ARC_PIE;

    updateShape();

  }

  JDEllipse(LXObject lxObj,int a,int b,int atype) {

    initDefault();
    loadObject(lxObj);

    double x = lxObj.boundRect.getX();
    double y = lxObj.boundRect.getY();
    double w = lxObj.boundRect.getWidth();
    double h = lxObj.boundRect.getHeight();

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[8];
    createSummit();

    summit[0].x = x;
    summit[0].y = y;

    summit[1].x = x+w/2;
    summit[1].y = y;

    summit[2].x = x+w;
    summit[2].y = y;

    summit[3].x = x+w;
    summit[3].y = y+h/2;

    summit[4].x = x+w;
    summit[4].y = y+h;

    summit[5].x = x+w/2;
    summit[5].y = y+h;

    summit[6].x = x;
    summit[6].y = y+h;

    summit[7].x = x;
    summit[7].y = y+h/2;

    step = stepDefault;
    angleStart  = a;
    angleExtent = b;
    if(fillStyle==JDObject.FILL_STYLE_NONE)
      arcType = ARC_OPEN;
    else
      arcType = (atype==1)?ARC_CLOSED:ARC_PIE;

    updateShape();

  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  void initDefault() {
    super.initDefault();
    step = stepDefault;
    arcType = arcTypeDefault;
    angleStart = angleStartDefault;
    angleExtent = angleExtentDefault;
  }

  public JDObject copy(int x,int y) {
    return new JDEllipse(this,x,y);
  }

  public boolean isInsideObject(int x,int y) {

    if(!super.isInsideObject(x,y)) return false;

    boolean found = false;
    int i = 0;

    if (fillStyle != FILL_STYLE_NONE) {

      Polygon p = new Polygon(ptsx,ptsy,ptsx.length);
      found = p.contains(x,y);

    } else {

      while (i < (ptsx.length - 1) && !found) {
        found = isPointOnLine(x, y, ptsx[i], ptsy[i], ptsx[i + 1], ptsy[i + 1]);
        if (!found) i++;
      }

      if(!found)
        found = isPointOnLine(x, y, ptsx[i], ptsy[i], ptsx[0], ptsy[0]);

    }

    return found;

  }

  void updateShape() {
    computeBoundRect();    
    makePolygon();
    if (hasShadow()) {
      computeShadow(isClosed());
      computeShadowColors();
    }
  }

  public JDPolyline convertToPolyline() {
    JDPolyline ret=buildDefaultPolyline();
    ret.setClosed(isClosed());
    ret.updateShape();
    return ret;
  }

  boolean isClosed() {
    return angleExtent==360 || arcType!=ARC_OPEN;
  }

  public void rotate90(double x,double y) {
    angleStart += 90;
    angleStart = angleStart % 360;
    super.rotate90(x,y);
  }

  public void restoreTransform() {
    angleStart = sAngleStart;
    super.restoreTransform();
  }

  public void saveTransform() {
    sAngleStart = angleStart;
    super.saveTransform();
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

    x1 = minx;
    y1 = miny;
    width = maxx - minx;
    height = maxy - miny;

    boundRect = new Rectangle((int) minx, (int) miny, (int) (maxx - minx) + 1, (int) (maxy - miny) + 1);

  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  JDEllipse(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while(!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if( propName.equals("step") ) {
        step = (int)f.parseDouble();
      } else if( propName.equals("angle_start") ) {
        angleStart = (int)f.parseDouble();
      } else if( propName.equals("angle_extent") ) {
        angleExtent = (int)f.parseDouble();
      } else if( propName.equals("arc_type") ) {
        arcType = (int)f.parseDouble();
      } else
        loadDefaultPropery(f,propName);
    }

    f.endBlock();

    updateShape();
  }

  void saveObject(FileWriter f,int level) throws IOException {

    String decal = saveObjectHeader(f,level);

    if(step!=stepDefault) {
      String to_write = decal + "step:" + step + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(angleStart!=angleStartDefault) {
      String to_write = decal + "angle_start:" + angleStart + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(angleExtent!=angleExtentDefault) {
      String to_write = decal + "angle_extent:" + angleExtent + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if(arcType!=arcTypeDefault) {
      String to_write = decal + "arc_type:" + arcType + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f,level);
  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {
    UndoPattern u = new UndoPattern(UndoPattern._JDEllipse);
    fillUndoPattern(u);
    u.step = step;
    u.arcType = arcType;
    u.angleStart = angleStart;
    u.angleExtent = angleExtent;
    return u;
  }

  JDEllipse(UndoPattern e) {
    initDefault();
    applyUndoPattern(e);
    step=e.step;
    arcType = e.arcType;
    angleStart = e.angleStart;
    angleExtent = e.angleExtent;
    updateShape();
  }

  // -----------------------------------------------------------
  // property stuff
  // -----------------------------------------------------------
  /**
   * Sets the interpolation step of this ellispe.
   * @param s Interpolation step (Default is 10)
   */
  public void setStep(int s) {
    step=s;
    updateShape();
  }

  /**
   * Returns the interpolation step.
   * @see #setStep
   */
  public int getStep() {
    return step;
  }

  /**
   * Sets the arc type for this ellipse.
   * @param type Arc type
   * @see #ARC_OPEN
   * @see #ARC_CLOSED
   * @see #ARC_PIE
   */
  public void setArcType(int type) {
    arcType=type;
    updateShape();
  }

  /**
   * Returns the current arc type.
   * @see #setArcType
   */
  public int getArcType() {
    return arcType;
  }

  /**
   * Sets the starting angle of the arc.
   * @param a Angle in degrees.
   */
  public void setAngleStart(int a) {
    angleStart=a;
    updateShape();
  }

  /** Returns the starting angle of the arc.
   * @see #setAngleStart
   */
  public int getAngleStart() {
    return angleStart;
  }

  /**
   * Sets the arc angle extent.
    * @param a Angle extent in degrees.
   */
  public void setAngleExtent(int a) {
    angleExtent=a;
    updateShape();
  }

  /**
   * Returns the arc angle extent.
   * @see #setAngleExtent
   */
  public int getAngleExtent() {
    return angleExtent;
  }

  public void paint(JDrawEditor parent,Graphics g) {
    if(!visible) return;

    Graphics2D g2 = (Graphics2D) g;
    prepareRendering(g2);

    if (fillStyle != FILL_STYLE_NONE && isClosed()) {

      Paint p = GraphicsUtils.createPatternForFilling(this);
      if(p!=null) {
        g2.setPaint(p);
        if(useOval)
          g.fillOval((int)(x1+0.5), (int)(y1+0.5), (int)(width+1), (int)(height+1));
        else
          g.fillPolygon(ptsx, ptsy, ptsx.length);
      }

    }

    if (lineWidth > 0) {

      g.setColor(foreground);
      BasicStroke bs = GraphicsUtils.createStrokeForLine(lineWidth, lineStyle);
      Stroke old = null;

      if (bs != null) {
        old = g2.getStroke();
        g2.setStroke(bs);
      }

      if(isClosed()) {
        if(useOval)
          g.drawOval((int)(x1+0.5), (int)(y1+0.5), (int)(width), (int)(height));
        else
          g.drawPolygon(ptsx, ptsy, ptsx.length);
      } else
        g.drawPolyline(ptsx, ptsy, ptsx.length);

      if(bs != null) g2.setStroke(old);

    }

    paintShadows(g);

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

  // Compute ellispe polygon from the bounding rect
  private void makePolygon() {

    double w=width/2.0;
    double h=height/2.0;

    double xc =x1 + w;
    double yc =y1 + h;

    // For double to int rounding, remove a half pixel.
    w -= 0.5;
    h -= 0.5;

    int nbp = (arcType==ARC_PIE && angleExtent!=360)?step+1:step;
    ptsx = new int[nbp];
    ptsy = new int[nbp];
    double r  = ((double)angleExtent/180.0)*Math.PI / (double)step;
    double r0 = ((double)angleStart/180.0)*Math.PI;

    int i;
    for(i=0;i<step;i++) {
      double x = w * Math.cos(r0 + r * (double)i);
      double y = h * Math.sin(r0 + r * (double)i);
      ptsx[i]        = (int)(xc + x);
      ptsy[i]        = (int)(yc + y);
    }

    if(arcType==ARC_PIE && angleExtent!=360) {
      ptsx[i] = (int)(xc);
      ptsy[i] = (int)(yc);
    }

    useOval = (angleExtent==360) && (step==stepDefault);

  }


}