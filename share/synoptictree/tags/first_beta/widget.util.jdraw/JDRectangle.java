/**
 * JDraw Rectangle graphic object
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.geom.Point2D;
import java.io.FileWriter;
import java.io.IOException;

/** JDraw Rectangle graphic object.
 *  <p>Here is an example of few JDRectangle:<p>
 *  <img src="JDRectangle.gif" border="0" alt="JDRectangle examples"></img>
 */
public class JDRectangle extends JDRectangular implements JDPolyConvert {

  /**
   * Contructs a JDRectangle.
   * @param objectName Object name
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   * @param w Rectangle width
   * @param h Rectangle height
   */
  public JDRectangle(String objectName, int x, int y, int w, int h) {
    initDefault();
    setOrigin(new Point2D.Double(x, y));
    summit = new Point2D.Double[8];
    name = objectName;
    createSummit();
    computeSummitCoordinates(x, y, w, h);
    updateShape();
  }

  JDRectangle(JDRectangle e,int x,int y) {
    cloneObject(e,x,y);
    updateShape();
  }

  JDRectangle(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      loadDefaultPropery(f, propName);
    }

    f.endBlock();
    updateShape();
  }

  JDRectangle(JLXObject jlxObj) {

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

    updateShape();

  }

  JDRectangle(LXObject lxObj) {

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

    updateShape();

  }

  public JDObject copy(int x,int y) {
    return new JDRectangle(this,x,y);
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

    // Update shadow coordinates
    ptsx = new int[4];
    ptsy = new int[4];
    ptsx[0] = (int)(summit[0].x+0.5);
    ptsy[0] = (int)(summit[0].y+0.5);
    ptsx[1] = (int)(summit[2].x+0.5);
    ptsy[1] = (int)(summit[2].y+0.5);
    ptsx[2] = (int)(summit[4].x+0.5);
    ptsy[2] = (int)(summit[4].y+0.5);
    ptsx[3] = (int)(summit[6].x+0.5);
    ptsy[3] = (int)(summit[6].y+0.5);
    if( hasShadow() ) {
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
  // Configuration management
  // -----------------------------------------------------------
  void saveObject(FileWriter f,int level) throws IOException {

    saveObjectHeader(f,level);
    closeObjectHeader(f,level);

  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDRectangle);
    fillUndoPattern(u);
    return u;

  }

  JDRectangle(UndoPattern e) {
     initDefault();
     applyUndoPattern(e);
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