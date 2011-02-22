/**
 * User: Jean Luc
 * Date: Aug 9, 2003
 * Time: 7:04:19 PM
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.IOException;
import java.util.Vector;

/** JDraw Spline graphic object.
 *  <p>Here is an example of few JDSpline:<p>
 *  <img src="JDSpline.gif" border="0" alt="JDSpline examples"></img>
 */
public class JDSpline extends JDPolyline implements JDPolyConvert {

  /**
   * Contruct a splie
   * @param objectName spline name
   * @param p Array of control points
   */
  public JDSpline(String objectName, Point[] p) {
    initDefault();
    summit = new Point.Double[p.length];
    for(int i=0;i<p.length;i++) summit[i] = new Point.Double(p[i].x, p[i].y);
    step = 10;
    name = objectName;
    updateShape();
    Point.Double org = new Point.Double(boundRect.x + boundRect.width / 2, boundRect.y + boundRect.height / 2);
    setOrigin(org);
  }

  JDSpline(JDSpline e, int x, int y) {
    cloneObject(e, x, y);
    isClosed = e.isClosed;
    step = e.step;
    updateShape();
  }

  JDSpline(JLXObject jlxObj,JLXPath p) {

    initDefault();
    loadObject(jlxObj);

    double x = jlxObj.boundRect.getX();
    double y = jlxObj.boundRect.getY();
    double w = jlxObj.boundRect.getWidth();
    double h = jlxObj.boundRect.getHeight();
    int nbp=(p.path.size()-1)*3+1;

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[nbp];
    createSummit();

    for(int i=0,k=0;i<p.path.size();i++) {

      double[] pts = (double[]) p.path.get(i);

      if (i == 0) {
        // First point
        summit[k].x = origin.x + pts[0];
        summit[k].y = origin.y + pts[1];
        k++;
      } else {

        if (p.pathType == 2) {
          // Triangular spline
          summit[k].x   = origin.x + pts[0];
          summit[k].y   = origin.y + pts[1];
          summit[k+1].x = origin.x + pts[0];
          summit[k+1].y = origin.y + pts[1];
          summit[k+2].x = origin.x + pts[2];
          summit[k+2].y = origin.y + pts[3];
        } else {
          // General spline
          summit[k].x   = origin.x + pts[0];
          summit[k].y   = origin.y + pts[1];
          summit[k+1].x = origin.x + pts[2];
          summit[k+1].y = origin.y + pts[3];
          summit[k+2].x = origin.x + pts[4];
          summit[k+2].y = origin.y + pts[5];
        }
        k+=3;

      }

    }

    isClosed = p.closed;
    step = 10;

    updateShape();

  }

  JDSpline(LXObject lxObj,double[] ptsx,double[] ptsy,boolean closed) {

    double x,y;
    int i;

    initDefault();
    loadObject(lxObj);

    int nbp = ptsx.length;
    Vector newPts = new Vector();

    // First step

    x = (ptsx[0] + ptsx[1]) / 2.0;
    y = (ptsy[0] + ptsy[1]) / 2.0;
    newPts.add(new Point.Double(ptsx[0],ptsy[0]));
    newPts.add(new Point.Double(ptsx[0],ptsy[0]));
    newPts.add(new Point.Double(x,y));
    newPts.add(new Point.Double(x,y));

    // Spline

    for(i=1;i<nbp;i++) {

      if(i<nbp-1) {
        x = (ptsx[i] + ptsx[i+1]) / 2.0;
        y = (ptsy[i] + ptsy[i+1]) / 2.0;
      } else {
        x = (ptsx[i] + ptsx[0]) / 2.0;
        y = (ptsy[i] + ptsy[0]) / 2.0;
      }

      newPts.add(new Point.Double(ptsx[i],ptsy[i]));
      newPts.add(new Point.Double(ptsx[i],ptsy[i]));
      newPts.add(new Point.Double(x,y));

    }

    // Last step

    newPts.add(new Point.Double(x,y));
    newPts.add(new Point.Double(ptsx[0],ptsy[0]));
    newPts.add(new Point.Double(ptsx[0],ptsy[0]));

    summit = new Point2D.Double[newPts.size()];
    for(i=0;i<summit.length;i++)
      summit[i] = (Point.Double)newPts.get(i);

    isClosed = closed;
    step = 10;

    updateShape();

    double bx = boundRect.getX();
    double by = boundRect.getY();
    double bw = boundRect.getWidth();
    double bh = boundRect.getHeight();
    setOrigin(new Point2D.Double(bx+bw/2.0, by+bh/2.0));

  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  public JDObject copy(int x, int y) {
    return new JDSpline(this, x, y);
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

    for (int i = 0; i < ptsx.length; i++) {
      if (ptsx[i] < minx) minx = ptsx[i];
      if (ptsx[i] > maxx) maxx = ptsx[i];
      if (ptsy[i] < miny) miny = ptsy[i];
      if (ptsy[i] > maxy) maxy = ptsy[i];
    }

    boundRect = new Rectangle((int)minx, (int)miny, (int)(maxx - minx) + 1, (int)(maxy - miny) + 1);

  }

  public void setStep(int s) {
    step = s;
    updateShape();
  }

  public JDPolyline convertToPolyline() {
    JDPolyline ret=buildDefaultPolyline();
    ret.setClosed(isClosed());
    ret.updateShape();
    return ret;
  }

  // -----------------------------------------------------------
  // Selection summit
  // -----------------------------------------------------------
  public void moveSummit(int id, double x, double y) {

    if( id%3==0 ) {

      double tx = x - summit[id].x;
      double ty = y - summit[id].y;

      if( id>0 ) {
        summit[id-1].x += tx;
        summit[id-1].y += ty;
      }

      summit[id].x += tx;
      summit[id].y += ty;

      if( id<summit.length-1 ) {
        summit[id+1].x += tx;
        summit[id+1].y += ty;
      }

    } else {
      summit[id].x = x;
      summit[id].y = y;
    }

    updateShape();

  }

  void deleteSummit() {

    if (breakId < 0) return;
    Point.Double[] nSummit = null;

    nSummit = new Point.Double[summit.length - 3];

    if( breakId==0 ) {
      for (int i=3;i<summit.length; i++) nSummit[i-3]=summit[i];
    } else if (breakId==summit.length-1) {
      for (int i=0;i<summit.length-3; i++) nSummit[i]=summit[i];
    } else {
      for (int i = 0,nb = 0; i < summit.length; i++)
        if (i<breakId-1 || i>breakId+1) nSummit[nb++] = summit[i];
    }

    summit = nSummit;
    updateShape();
  }

  boolean canDeleteSummit(int id) {
    if(!visible) return false;

    breakId = -1;
    if ((id < 0) || (id >= summit.length) || summit.length <= 4)
      return false;

    if ((id % 3) != 0)
      return false;

    breakId = id;
    return true;
  }

  void paintSummit(Graphics g,double summitWidth) {

    super.paintSummit(g, summitWidth);
    // Paint tangent segment
    g.setColor(Color.green);
    for (int i = 0; i < summit.length - 1; i += 3) {
      g.drawLine((int) summit[i].x, (int) summit[i].y, (int) summit[i + 1].x, (int) summit[i + 1].y);
      g.drawLine((int) summit[i + 2].x, (int) summit[i + 2].y, (int) summit[i + 3].x, (int) summit[i + 3].y);
    }

  }

  void breakShape() {

    if(breakId<0) return;
    // Add 3 summit

    Point.Double[] nSummit = new Point.Double[summit.length + 3];
    int sumId = breakId/step * 3 + 2;
    double vx;
    double vy;
    double n;
    int i,nb;

    if(sumId<summit.length) {

      vx = (double)(ptsx[breakId+1] - ptsx[breakId]);
      vy = (double)(ptsy[breakId+1] - ptsy[breakId]);

      n  = Math.sqrt(vx*vx+vy*vy);
      if(n<1.0) {
        vx = 30;
        vy = 30;
      } else {
        vx = 30.0 * vx / n;
        vy = 30.0 * vy / n;
      }

      for (i = 0,nb = 0; i < summit.length; i++) {
        if( i==sumId ) {
          // Add the new control point
          nSummit[nb++] = new Point.Double(breakX-(int)(vx),breakY-(int)(vy));
          nSummit[nb++] = new Point.Double(breakX,breakY);
          nSummit[nb++] = new Point.Double(breakX+(int)(vx),breakY+(int)(vy));
        }
        nSummit[nb++] = summit[i];
      }

    } else {

      vx = (double)(ptsx[0] - ptsx[ptsx.length-1]);
      vy = (double)(ptsy[0] - ptsy[ptsx.length-1]);

      n  = Math.sqrt(vx*vx+vy*vy);
      if(n<1.0) {
        vx = 30;
        vy = 30;
      } else {
        vx = 30.0 * vx / n;
        vy = 30.0 * vy / n;
      }

      for (i = 0; i < summit.length; i++)
        nSummit[i] = summit[i];

      // Add the new control point
      nSummit[i++] = new Point.Double(breakX-(int)(vx),breakY-(int)(vy));
      nSummit[i++] = new Point.Double(breakX,breakY);
      nSummit[i++] = new Point.Double(breakX+(int)(vx),breakY+(int)(vy));

    }

    summit=nSummit;
    updateShape();
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  JDSpline(JDFileLoader f) throws IOException {
    initDefault();
    // Default for spline
    int l = f.getCurrentLine();

    f.startBlock();
    summit = f.parseSummitArray();
    if (summit.length < 2)
      throw new IOException("Invalid summit number for JDSpline at line " + l);

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("isClosed")) {
        isClosed = f.parseBoolean();
      } else if (propName.equals("step")) {
        step = (int) f.parseDouble();
      } else
        loadDefaultPropery(f, propName);
    }

    f.endBlock();

    updateShape();
  }

  /**
   * Connects this spline to an other spline. Points
   * are added to the end of this spline. if pline
   * if not a JDSpline, nothing happens.
   * @param pline Polyline to be concatened.
   */
  public void connect(JDPolyline pline) {

    if(pline instanceof JDSpline) {

      int i;
      Point.Double[] nSummit = new Point.Double[summit.length + pline.getSummitNumber()+2];
      for(i=0;i<summit.length;i++)
        nSummit[i] = summit[i];

      // Add 2 point here
      double x1 = summit[i-1].x;
      double y1 = summit[i-1].y;
      double vx = pline.getSummit(0).x - summit[i-1].x;
      double vy = pline.getSummit(0).y - summit[i-1].y;
      nSummit[i]   = new Point.Double(x1+vx*0.33,y1+vy*0.33);
      nSummit[i+1] = new Point.Double(x1+vx*0.66,y1+vy*0.66);

      for(i=0;i<pline.getSummitNumber();i++)
        nSummit[i+2+summit.length] = new Point.Double(pline.getSummit(i).x, pline.getSummit(i).y);

      summit = nSummit;
      updateShape();


    } else {
      // Cannot connect
      System.out.println("JDSpline.connect() : Cannot connect a JDSpline to JDPolyline.");
    }

  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDSpline);
    fillUndoPattern(u);
    u.step = step;
    u.isClosed = isClosed;
    return u;
  }

  JDSpline(UndoPattern e) {
     initDefault();
     applyUndoPattern(e);
     step = e.step;
     isClosed = e.isClosed;
     updateShape();
   }

  // -----------------------------------------------------------
  // Private stuff
  // -----------------------------------------------------------

  // Compute pts
  void updateShape() {

    int i,nb = 0;

    ptsx = new int[summit.length / 3 * step + 1];
    ptsy = new int[summit.length / 3 * step + 1];

    for (i = 0; i < summit.length - 1; i += 3) {

      JDUtils.computeSpline(summit[i + 0].x, summit[i + 0].y,
                            summit[i + 1].x, summit[i + 1].y,
                            summit[i + 2].x, summit[i + 2].y,
                            summit[i + 3].x, summit[i + 3].y,
                            step,i == (summit.length - 4),nb,
                            null,ptsx,ptsy
                            );

      nb+=step;

    }

    if (hasShadow()) {
      computeShadow(isClosed());
      computeShadowColors();
    }
    computeBoundRect();
    
  }

}