/**
 * User: Jean Luc
 * Date: Aug 9, 2003
 * Time: 7:04:19 PM
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.FileWriter;
import java.io.IOException;

/** JDraw Rectangle graphic object.
  *  <p>Here is an example of few JDRoundRectangle:<p>
  *  <img src="JDRRectangle.gif" border="0" alt="JDRoundRectangle examples"></img>
  */
public class JDRoundRectangle extends JDRectangular implements JDPolyConvert {

  // Default
  static final int stepDefault = 6;
  static final int cornerWidthDefault = 24;

  // Vars
  private int step;
  private int cornerWidth;

  /**
   * Contructs a JDRoundRectangle.
   * @param objectName Object name
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   * @param w Rectangle width
   * @param h Rectangle height
   */
  public JDRoundRectangle(String objectName, int x, int y, int w, int h) {
    initDefault();
    setOrigin(new Point.Double(x, y));
    summit = new Point.Double[8];
    name = objectName;
    createSummit();
    computeSummitCoordinates(x, y, w, h);
    updateShape();
  }

  JDRoundRectangle(JDRoundRectangle e, int x, int y) {
    cloneObject(e, x, y);
    cornerWidth = e.cornerWidth;
    step = e.step;
    updateShape();
  }

  JDRoundRectangle(JLXObject jlxObj,int corner) {

    initDefault();
    loadObject(jlxObj);

    double x = jlxObj.boundRect.getX();
    double y = jlxObj.boundRect.getY();
    double w = jlxObj.boundRect.getWidth();
    double h = jlxObj.boundRect.getHeight();

    setOrigin(new Point2D.Double(x+w/2.0, y+w/2.0));
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
    cornerWidth = corner;

    updateShape();

  }

  // -----------------------------------------------------------
  // Ovverides
  // -----------------------------------------------------------
  void initDefault() {
    super.initDefault();
    step = stepDefault;
    cornerWidth = cornerWidthDefault;
  }

  public JDObject copy(int x, int y) {
    return new JDRoundRectangle(this, x, y);
  }

  public boolean isInsideObject(int x, int y) {

    if (!super.isInsideObject(x, y)) return false;

    boolean found = false;
    int i = 0;

    if (fillStyle != FILL_STYLE_NONE) {

      Polygon p = new Polygon(ptsx, ptsy, ptsx.length);
      found = p.contains(x, y);

    } else {

      while (i < (ptsx.length - 1) && !found) {
        found = isPointOnLine(x, y, ptsx[i], ptsy[i], ptsx[i + 1], ptsy[i + 1]);
        if (!found) i++;
      }

      // Check last line
      if (!found) found = isPointOnLine(x, y, ptsx[i], ptsy[i], ptsx[0], ptsy[0]);

    }

    return found;

  }

  void updateShape() {
    computeBoundRect();
    if ((boundRect.width <= cornerWidth * 2) || (boundRect.height <= cornerWidth * 2)) {

      //Build non rounded rect
      ptsx = new int[4];
      ptsy = new int[4];
      ptsx[0] = (int) (summit[0].x+0.5);
      ptsy[0] = (int) (summit[0].y+0.5);
      ptsx[1] = (int) (summit[2].x+0.5);
      ptsy[1] = (int) (summit[2].y+0.5);
      ptsx[2] = (int) (summit[4].x+0.5);
      ptsy[2] = (int) (summit[4].y+0.5);
      ptsx[3] = (int) (summit[6].x+0.5);
      ptsy[3] = (int) (summit[6].y+0.5);

    } else {

      double k,ks,kc;
      double p1x,p2x,p3x,p4x;
      double p1y,p2y,p3y,p4y;
      int i = 0,j,nb = 0;
      int x,y;

      ptsx = new int[(step + 1) * 4];
      ptsy = new int[(step + 1) * 4];


      for (i = 0; i < 4; i++) {

        // Get corner spline tangent
        switch (i) {
          case 0:
            p1x = boundRect.x;
            p2x = boundRect.x;
            p3x = boundRect.x + cornerWidth / 4;
            p4x = boundRect.x + cornerWidth;

            p1y = boundRect.y + cornerWidth;
            p2y = boundRect.y + cornerWidth / 4;
            p3y = boundRect.y;
            p4y = boundRect.y;
            break;
          case 1:
            p1x = boundRect.x + boundRect.width - 1 - cornerWidth;
            p2x = boundRect.x + boundRect.width - 1 - cornerWidth / 4;
            p3x = boundRect.x + boundRect.width - 1;
            p4x = boundRect.x + boundRect.width - 1;

            p1y = boundRect.y;
            p2y = boundRect.y;
            p3y = boundRect.y + cornerWidth / 4;
            p4y = boundRect.y + cornerWidth;
            break;
          case 2:
            p1x = boundRect.x + boundRect.width - 1;
            p2x = boundRect.x + boundRect.width - 1;
            p3x = boundRect.x + boundRect.width - 1 - cornerWidth / 4;
            p4x = boundRect.x + boundRect.width - 1 - cornerWidth;

            p1y = boundRect.y + boundRect.height - 1 - cornerWidth;
            p2y = boundRect.y + boundRect.height - 1 - cornerWidth / 4;
            p3y = boundRect.y + boundRect.height - 1;
            p4y = boundRect.y + boundRect.height - 1;
            break;
          default:
            p1x = boundRect.x + cornerWidth;
            p2x = boundRect.x + cornerWidth / 4;
            p3x = boundRect.x;
            p4x = boundRect.x;

            p1y = boundRect.y + boundRect.height - 1;
            p2y = boundRect.y + boundRect.height - 1;
            p3y = boundRect.y + boundRect.height - 1 - cornerWidth / 4;
            p4y = boundRect.y + boundRect.height - 1 - cornerWidth;
            break;
        }

        //************************
        // Compute the spline
        //************************

        double stp = 1.0 / (double) step;
        k = 0;
        j = 0;


        while (j <= step) {
          ks = k * k;
          kc = ks * k;

          x = (int) ((1.0 - 3.0 * k + 3.0 * ks - kc) * p1x
              + 3.0 * (k - 2.0 * ks + kc) * p2x
              + 3.0 * (ks - kc) * p3x
              + kc * p4x + 0.5);

          y = (int) ((1.0 - 3.0 * k + 3.0 * ks - kc) * p1y
              + 3.0 * (k - 2.0 * ks + kc) * p2y
              + 3.0 * (ks - kc) * p3y
              + kc * p4y + 0.5);

          if (j == 0) {
            ptsx[nb] = (int) (p1x+0.5);
            ptsy[nb] = (int) (p1y+0.5);
          }
          if (j == step) {
            ptsx[nb] = (int) (p4x+0.5);
            ptsy[nb] = (int) (p4y+0.5);
          } else {
            ptsx[nb] = x;
            ptsy[nb] = y;
          }
          nb++;
          k = k + stp;
          j++;
        }

      }
    }

    if (hasShadow()) {
      computeShadow(true);
      computeShadowColors();
    }
  }

  public JDPolyline convertToPolyline() {
    JDPolyline ret=buildDefaultPolyline();
    ret.setClosed(true);
    ret.updateShape();
    return ret;

  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  void saveObject(FileWriter f, int level) throws IOException {

    String decal = saveObjectHeader(f, level);

    String to_write;

    if (step != stepDefault) {
      to_write = decal + "step:" + step + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (cornerWidth != cornerWidthDefault) {
      to_write = decal + "cornerWidth:" + cornerWidth + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f, level);

  }

  JDRoundRectangle(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("cornerWidth")) {
        cornerWidth = (int) f.parseDouble();
      } else if (propName.equals("step")) {
        step = (int) f.parseDouble();
      } else
        loadDefaultPropery(f, propName);
    }
    f.endBlock();

    updateShape();
  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDRoundRectangle);
    fillUndoPattern(u);
    u.step = step;
    u.cornerWidth = cornerWidth;
    return u;

  }

  JDRoundRectangle(UndoPattern e) {
     initDefault();
     applyUndoPattern(e);
     step = e.step;
     cornerWidth = e.cornerWidth;
     updateShape();
   }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------
  /**
   * Returns the interpolation of rounded corner.
   * @see #setStep
   */
  public int getStep() {
    return step;
  }

  /**
   * Sets the interpolation step of the rounded corner.
   * @param s Interpolation step
   */
  public void setStep(int s) {
    step = s;
    updateShape();
  }

  /**
   * Returns the rouded corner width.
   * @see #setCornerWidth
   */
  public int getCornerWidth() {
    return cornerWidth;
  }

  /**
   * Sets the rounded corner width.
   * @param w Corner width
   */
  public void setCornerWidth(int w) {
    cornerWidth = w;
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