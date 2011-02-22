/**
 * User: Jean Luc
 * Date: Aug 9, 2003
 * Time: 7:04:19 PM
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.io.FileWriter;
import java.io.IOException;

/**
 * JDraw Rectanglar graphic object (All object having a rectangular sizing behavior)
 */
public abstract class JDRectangular extends JDObject {
  
  public void paint(JDrawEditor parent,Graphics g) {
    if(!visible) return;

    Graphics2D g2 = (Graphics2D) g;
    prepareRendering(g2);

    if (fillStyle != FILL_STYLE_NONE) {
      Paint p = GraphicsUtils.createPatternForFilling(this);
      if(p!=null) g2.setPaint(p);
      g.fillPolygon(ptsx, ptsy, ptsx.length);
    }

    if (lineWidth > 0) {
      g.setColor(foreground);
      BasicStroke bs = GraphicsUtils.createStrokeForLine(lineWidth, lineStyle);

      if (bs != null) {
        Stroke old = g2.getStroke();
        g2.setStroke(bs);
        g.drawPolygon(ptsx, ptsy, ptsx.length);
        g2.setStroke(old);
      } else {
        g.drawPolygon(ptsx, ptsy, ptsx.length);
      }
    }

    paintShadows(g);
  }

  int getSummitMotion(int id) {
    switch(id) {
      case 0:
      case 2:
      case 4:
      case 6:
        return JDObject.BOTH_SM;
      case 1:
      case 5:
        return JDObject.VERTICAL_SM;
    }
    return JDObject.HORIZONTAL_SM;
  }

  public void moveSummit(int id,double x,double y) {

    switch (id) {
      case 0:
        if (Math.abs(summit[2].x - x) > 0.5) {
          summit[0].x = x;
          summit[6].x = x;
        }
        if (Math.abs(summit[4].y - y) > 0.5) {
          summit[0].y = y;
          summit[2].y = y;
        }
        break;

      case 1:
        if (Math.abs(summit[4].y - y) > 0.5) {
          summit[0].y = y;
          summit[2].y = y;
        }
        break;

      case 2:
        if (Math.abs(summit[0].x - x) > 0.5) {
          summit[2].x = x;
          summit[4].x = x;
        }
        if (Math.abs(summit[4].y - y) > 0.5) {
          summit[0].y = y;
          summit[2].y = y;
        }
        break;

      case 3:
        if (Math.abs(summit[0].x - x) > 0.5) {
          summit[2].x = x;
          summit[4].x = x;
        }
        break;

      case 4:
        if (Math.abs(summit[0].x - x) > 0.5) {
          summit[2].x = x;
          summit[4].x = x;
        }
        if (Math.abs(summit[0].y - y) > 0.5) {
          summit[4].y = y;
          summit[6].y = y;
        }
        break;

      case 5:
        if (Math.abs(summit[0].y - y) > 0.5) {
          summit[4].y = y;
          summit[6].y = y;
        }
        break;

      case 6:
        if (Math.abs(summit[2].x - x) > 0.5) {
          summit[0].x = x;
          summit[6].x = x;
        }
        if (Math.abs(summit[0].y - y) > 0.5) {
          summit[4].y = y;
          summit[6].y = y;
        }
        break;

      case 7:
        if (Math.abs(summit[2].x - x) > 0.5) {
          summit[0].x = x;
          summit[6].x = x;
        }
        break;

    }

    centerSummit();
    updateShape();

  }

  void centerSummit() {
    summit[1].x = (summit[0].x + summit[2].x)/2.0;
    summit[1].y = (summit[0].y + summit[2].y)/2.0;
    summit[3].x = (summit[2].x + summit[4].x)/2.0;
    summit[3].y = (summit[2].y + summit[4].y)/2.0;
    summit[5].x = (summit[6].x + summit[4].x)/2.0;
    summit[5].y = (summit[6].y + summit[4].y)/2.0;
    summit[7].x = (summit[0].x + summit[6].x)/2.0;
    summit[7].y = (summit[0].y + summit[6].y)/2.0;
  }

  void saveSummit(FileWriter f, String decal) throws IOException {

    String to_write;
    to_write = decal + "summit:";
    to_write += roundDouble(summit[0].x) + "," + roundDouble(summit[0].y) + ",";
    to_write += roundDouble(summit[4].x) + "," + roundDouble(summit[4].y) + "\n";
    f.write(to_write, 0, to_write.length());

  }

  public void rotate90(double x,double y) {

    // Rotate summit
    Point.Double d1 = summit[0];
    Point.Double d2 = summit[1];
    for (int i = 2;i<8; i++)
      summit[i-2] = summit[i];
    summit[6]=d1;
    summit[7]=d2;
    super.rotate90(x,y);

  }

}