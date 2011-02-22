/**
 * JDraw Label graphic object
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.font.FontRenderContext;
import java.awt.geom.Rectangle2D;
import java.awt.geom.Point2D;
import java.io.FileWriter;
import java.io.IOException;

/** JDraw Label graphic object.
 *  <p>Here is an example of few JDLabel:<p>
 *  <img src="JDLabel.gif" border="0" alt="JDLabel examples"></img>
 */
public class JDLabel extends JDRectangular {

  /** Text is centered */
  final static public int CENTER_ALIGNMENT = 0;
  /** Left justification for text (H alignement) */
  final static public int LEFT_ALIGNMENT = 1;
  /** Right justification for text (H alignement) */
  final static public int RIGHT_ALIGNMENT = 2;
  /** Up justification for text (V alignement) */
  final static public int UP_ALIGNMENT = 1;
  /** Down justification for text (V alignement) */
  final static public int DOWN_ALIGNMENT = 2;

  /** Text orientation */
  final static public int LEFT_TO_RIGHT = 0;
  /** Text orientation */
  final static public int BOTTOM_TO_TOP = 1;
  /** Text orientation */
  final static public int RIGHT_TO_LEFT = 2;
  /** Text orientation */
  final static public int TOP_TO_BOTTOM = 3;

  static final double NINETY_DEGREES = Math.toRadians(90.0);

  // Default properties
  static final String textDefault = "";
  static final Font fontDefault = new Font("Dialog", Font.PLAIN, 14);
  static final int hAlignmentDefault = CENTER_ALIGNMENT;
  static final int vAlignmentDefault = CENTER_ALIGNMENT;
  static final int textOrientationDefault = LEFT_TO_RIGHT;

  // Vars
  static BufferedImage img = new BufferedImage(10, 10, BufferedImage.TYPE_INT_RGB);
  private String theText;
  private Font theFont;
  private int hAlignment;
  private int vAlignment;
  private Dimension preferredSize = null;
  private int textOrientation;
  private int sTextOrientation;

  /**
   * Construcxt a label.
   * @param objectName Name of this label
   * @param text Text
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   */
  public JDLabel(String objectName, String text, int x, int y) {
    initDefault();
    setOrigin(new Point.Double(0.0, 0.0));
    summit = new Point.Double[8];
    name = objectName;
    theText = text;
    lineWidth = 0;
    Dimension d = getMinSize();
    createSummit();
    computeSummitCoordinates(x,y,d.width, d.height);
    updateShape();
    centerOrigin();
  }

  JDLabel(JDLabel e, int x, int y) {
    cloneObject(e, x, y);
    theText = new String(e.theText);
    theFont = new Font(e.theFont.getName(), e.theFont.getStyle(), e.theFont.getSize());
    textOrientation = e.textOrientation;
    hAlignment = e.hAlignment;
    vAlignment = e.vAlignment;
    updateShape();
  }

  JDLabel(JLXObject jlxObj,Font f,String text,int align,boolean resize) {

    initDefault();
    loadObject(jlxObj);

    double x = jlxObj.boundRect.getX();
    double y = jlxObj.boundRect.getY();
    double w = jlxObj.boundRect.getWidth();
    double h = jlxObj.boundRect.getHeight();

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[8];
    createSummit();

    theFont = f;
    theText = text;
    hAlignment = align;
    vAlignment = UP_ALIGNMENT;

    if( resize ) {

      Dimension d = getMinSize();
      computeSummitCoordinates((int)(x+(w-(double)d.width)/2.0),(int)(y+(h-(double)d.height)/2.0),d.width,d.height);

    } else {

      computeSummitCoordinates((int)x,(int)y,(int)w,(int)h);

    }


    updateShape();
  }

  JDLabel(LXObject lxObj,String text) {

    initDefault();
    loadObject(lxObj);

    summit = new Point2D.Double[8];
    createSummit();

    theFont = lxObj.font;
    theText = text;
    hAlignment = LEFT_ALIGNMENT;
    vAlignment = UP_ALIGNMENT;
    lineWidth = 0;

    Dimension d = getMinSize();
    computeSummitCoordinates((int)lxObj.px,(int)lxObj.py,d.width,d.height);

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
  void initDefault() {
    super.initDefault();
    theText = textDefault;
    theFont = fontDefault;
    hAlignment = hAlignmentDefault;
    vAlignment = vAlignmentDefault;
    textOrientation = textOrientationDefault;
  }

  public JDObject copy(int x, int y) {
    return new JDLabel(this, x, y);
  }

  public void paint(JDrawEditor parent,Graphics g) {

    if (!visible) return;
    Graphics2D g2 = (Graphics2D) g;
    prepareRendering(g2);
    super.paint(parent,g);

    // G2 initilialisation ----------------------------------

    g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
        RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
    g2.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS,
        RenderingHints.VALUE_FRACTIONALMETRICS_ON);

    g2.setFont(theFont);
    FontRenderContext frc = g2.getFontRenderContext();
    int fa = (int) Math.ceil(g.getFont().getLineMetrics("ABC", frc).getAscent());

    // Vars -------------------------------------------------------

    double angRot = 0.0;
    int w = boundRect.width;
    int h = boundRect.height;
    int ypos = 0;
    Dimension d = new Dimension(getMinSize());
    String[] nLines = theText.split("\n");
    String[] lines = null;
    int hmax = 0;
    int bw;
    int bh;
    int xpos = 0;
    Rectangle2D bounds = null;
    int nb = nLines.length;
    boolean found;
    int i;

    // Check Visible string -------------------------------------------
    if (w < d.width || h < d.height) {

      // Vertical
      for (found = false, hmax = 0, i = 0; i < nb && !found;) {
        bounds = g.getFont().getStringBounds(nLines[i], frc);
        bh = (int) Math.ceil(bounds.getHeight());
        if (textOrientation == LEFT_TO_RIGHT || textOrientation == RIGHT_TO_LEFT)
          found = (hmax + bh) > h;
        else
          found = (hmax + bh) > w;
        if (!found) {
          i++;
          hmax += bh;
        }
      }

      if (i > 0) {
        lines = new String[i];
        for (i = 0; i < lines.length; i++) lines[i] = nLines[i];
        //Horizontal
        if (textOrientation == LEFT_TO_RIGHT || textOrientation == RIGHT_TO_LEFT) {
          d.height = hmax;
          for (i = 0; i < lines.length; i++) lines[i] = getSegmentString(theFont, frc, lines[i], w);
        } else {
          d.width = hmax;
          for (i = 0; i < lines.length; i++) lines[i] = getSegmentString(theFont, frc, lines[i], h);
        }
      }

    } else {
      lines = nLines;
    }

    if (lines == null) return;
    nb = lines.length;
    hmax = 0;
    // Vertical alignment-------------------------------------------

    switch (textOrientation) {
      case LEFT_TO_RIGHT:
      case RIGHT_TO_LEFT:
        switch (vAlignment) {
          case CENTER_ALIGNMENT:
            ypos = (h - d.height) / 2;
            break;
          case UP_ALIGNMENT:
            ypos = 2;
            break;
          case DOWN_ALIGNMENT:
            ypos = (h - d.height) - 2;
            break;
        }
        break;
      case BOTTOM_TO_TOP:
        angRot = -NINETY_DEGREES;
        switch (vAlignment) {
          case CENTER_ALIGNMENT:
            xpos = (w - d.width) / 2;
            break;
          case UP_ALIGNMENT:
            xpos = 2;
            break;
          case DOWN_ALIGNMENT:
            xpos = (w - d.width) - 2;
            break;
        }
        break;
      case TOP_TO_BOTTOM:
        angRot = NINETY_DEGREES;
        switch (vAlignment) {
          case CENTER_ALIGNMENT:
            xpos = (w - d.width) / 2;
            break;
          case UP_ALIGNMENT:
            xpos = 2;
            break;
          case DOWN_ALIGNMENT:
            xpos = (w - d.width) - 2;
            break;
        }
        break;
    }

    // Rotation ----------------------------------------------------
    if (angRot != 0.0) g2.rotate(angRot);


    // Draw Strings --------------------------------------------------
    g2.setColor(foreground);
    for (i = 0; i < nb; i++) {

      switch (textOrientation) {

        case LEFT_TO_RIGHT:
        case RIGHT_TO_LEFT:
          bounds = g.getFont().getStringBounds(lines[i], frc);
          bw = (int) Math.ceil(bounds.getWidth());
          bh = (int) Math.ceil(bounds.getHeight());

          switch (hAlignment) {
            case CENTER_ALIGNMENT:
              xpos = ptsx[0] + (w - bw) / 2;
              break;
            case LEFT_ALIGNMENT:
              xpos = ptsx[0] + 3;
              break;
            case RIGHT_ALIGNMENT:
              xpos = ptsx[0] + w - bw - 3;
              break;
          }
          g2.drawString(lines[i], xpos, ptsy[0] + ypos + hmax + fa);
          hmax += bh;
          break;

        case BOTTOM_TO_TOP:
          bounds = g.getFont().getStringBounds(lines[i], frc);
          bw = (int) Math.ceil(bounds.getWidth());
          bh = (int) Math.ceil(bounds.getHeight());

          switch (hAlignment) {
            case CENTER_ALIGNMENT:
              ypos = -ptsy[3] + (h - bw) / 2;
              break;
            case LEFT_ALIGNMENT:
              ypos = -ptsy[3] + 3;
              break;
            case RIGHT_ALIGNMENT:
              ypos = -ptsy[3] + h - bw - 3;
              break;
          }
          g2.drawString(lines[i], ypos, ptsx[0] + xpos + hmax + fa);
          hmax += bh;
          break;

        case TOP_TO_BOTTOM:
          bounds = g.getFont().getStringBounds(lines[i], frc);
          bw = (int) Math.ceil(bounds.getWidth());
          bh = (int) Math.ceil(bounds.getHeight());

          switch (hAlignment) {
            case CENTER_ALIGNMENT:
              ypos = ptsy[0] + (h - bw) / 2;
              break;
            case LEFT_ALIGNMENT:
              ypos = ptsy[0] + 3;
              break;
            case RIGHT_ALIGNMENT:
              ypos = ptsy[0] + h - bw - 3;
              break;
          }
          g2.drawString(lines[i], ypos, -ptsx[1] + xpos + hmax + fa);
          hmax += bh;
          break;

      }
    }

    // Restore transform ----------------------------------------------------
    if (angRot != 0.0) g2.rotate(-angRot);

  }

  void updateShape() {
    computeBoundRect();

    // Update shadow coordinates
    ptsx = new int[4];
    ptsy = new int[4];

    if (summit[0].x < summit[2].x) {
      if (summit[0].y < summit[6].y) {
        ptsx[0] = (int) summit[0].x;
        ptsy[0] = (int) summit[0].y;
        ptsx[1] = (int) summit[2].x + 1;
        ptsy[1] = (int) summit[2].y;
        ptsx[2] = (int) summit[4].x + 1;
        ptsy[2] = (int) summit[4].y + 1;
        ptsx[3] = (int) summit[6].x;
        ptsy[3] = (int) summit[6].y + 1;
      } else {
        ptsx[0] = (int) summit[6].x;
        ptsy[0] = (int) summit[6].y;
        ptsx[1] = (int) summit[4].x + 1;
        ptsy[1] = (int) summit[4].y;
        ptsx[2] = (int) summit[2].x + 1;
        ptsy[2] = (int) summit[2].y + 1;
        ptsx[3] = (int) summit[0].x;
        ptsy[3] = (int) summit[0].y + 1;
      }
    } else {
      if (summit[0].y < summit[6].y) {
        ptsx[0] = (int) summit[2].x;
        ptsy[0] = (int) summit[2].y;
        ptsx[1] = (int) summit[0].x + 1;
        ptsy[1] = (int) summit[0].y;
        ptsx[2] = (int) summit[6].x + 1;
        ptsy[2] = (int) summit[6].y + 1;
        ptsx[3] = (int) summit[4].x;
        ptsy[3] = (int) summit[4].y + 1;
      } else {
        ptsx[0] = (int) summit[4].x;
        ptsy[0] = (int) summit[4].y;
        ptsx[1] = (int) summit[6].x + 1;
        ptsy[1] = (int) summit[6].y;
        ptsx[2] = (int) summit[0].x + 1;
        ptsy[2] = (int) summit[0].y + 1;
        ptsx[3] = (int) summit[2].x;
        ptsy[3] = (int) summit[2].y + 1;
      }
    }

    if (hasShadow()) {
      computeShadow(true);
      computeShadowColors();
    }
  }

  public void rotate90(double x,double y) {
    super.rotate90(x,y);
    textOrientation++;
    if(textOrientation>TOP_TO_BOTTOM)
      textOrientation=LEFT_TO_RIGHT;
  }

  public void restoreTransform() {
    textOrientation = sTextOrientation;
    super.restoreTransform();
  }

  public void saveTransform() {
    sTextOrientation = textOrientation;
    super.saveTransform();
  }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------
  /**
   * Sets the Font of this label.
   * @param f Font
   */
  public void setFont(Font f) {
    setFont(f,false);
  }

  /**
   * Sets the font of this label and resize it if needed and specified.
   * @param f Font
   * @param resize true to resize label when text is out of bounds.
   */
  public void setFont(Font f,boolean resize) {
    theFont = f;
    updateLabel(resize);
  }

  /**
   * Returns the current font of this label.
   */
  public Font getFont() {
    return theFont;
  }

  /**
   * Sets the horizontal alignement of this label.
   * @param a Alignement value
   * @see #CENTER_ALIGNMENT
   * @see #LEFT_ALIGNMENT
   * @see #RIGHT_ALIGNMENT
   */
  public void setHorizontalAlignment(int a) {
    hAlignment = a;
  }

  /**
   * Returns the current horizontal text alignement.
   * @see #setHorizontalAlignment
   */
  public int getHorizontalAlignment() {
    return hAlignment;
  }

  /**
   * Sets the vertical alignement of this label.
   * @param a Alignement value
   * @see #CENTER_ALIGNMENT
   * @see #UP_ALIGNMENT
   * @see #DOWN_ALIGNMENT
   */
  public void setVerticalAlignment(int a) {
    vAlignment = a;
  }

  /**
   * Returns the current vetical text alignement.
   * @see #setHorizontalAlignment
   */
  public int setVerticalAlignment() {
    return vAlignment;
  }

  /**
   * Sets the text orientation.
   * @param a Orientation
   * @see #LEFT_TO_RIGHT
   * @see #BOTTOM_TO_TOP
   * @see #RIGHT_TO_LEFT
   * @see #TOP_TO_BOTTOM
   */
  public void setOrientation(int a) {
    textOrientation = a;
    updateLabel(true);
  }

  /**
   * Gets the current text orientation.
   * @see #setOrientation
   */
  public int getOrientation() {
    return textOrientation;
  }

  /**
   * Sets the text of this label.
   * @param s Text value
   */
  public void setText(String s) {
    setText(s,false);
  }

  /**
   * Sets the text of this label and resize label if desried.
   * @param s Text value
   * @param resize true to resize label when text is out of bounds.
   */
  public void setText(String s,boolean resize) {
    theText = s;
    updateLabel(resize);
  }

  /**
   * Returns the current label text.
   */
  public String getText() {
    return theText;
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  void saveObject(FileWriter f, int level) throws IOException {

    String decal = saveObjectHeader(f, level);
    String to_write;

    if (theFont.getName() != fontDefault.getName() ||
        theFont.getStyle() != fontDefault.getStyle() ||
        theFont.getSize() != fontDefault.getSize()) {
      to_write = decal + "font:\"" + theFont.getName() + "\"," + theFont.getStyle() + "," + theFont.getSize() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (!theText.equals(textDefault)) {
      int i;
      String lines[] = theText.split("\n");
      to_write = decal + "text:";
      for (i = 0; i < lines.length; i++) {
        if (i == 0) {
          to_write += "\"" + lines[i] + "\"";
        } else {
          to_write += decal + "     \"" + lines[i] + "\"";
        }
        if (i == lines.length - 1) {
          to_write += "\n";
        } else {
          to_write += ",\n";
        }
      }
      f.write(to_write, 0, to_write.length());
    }

    if (hAlignment != hAlignmentDefault) {
      to_write = decal + "hAlignment:" + hAlignment + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (vAlignment != vAlignmentDefault) {
      to_write = decal + "vAlignment:" + vAlignment + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (textOrientation != textOrientationDefault) {
      to_write = decal + "textOrientation:" + textOrientation + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f, level);

  }

  JDLabel(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("text")) {
        theText = f.parseStringArray();
      } else if (propName.equals("hAlignment")) {
        hAlignment = (int) f.parseDouble();
      } else if (propName.equals("vAlignment")) {
        vAlignment = (int) f.parseDouble();
      } else if (propName.equals("textOrientation")) {
        textOrientation = (int) f.parseDouble();
      } else if (propName.equals("font")) {
        theFont = f.parseFont();
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

    UndoPattern u = new UndoPattern(UndoPattern._JDLabel);
    fillUndoPattern(u);
    u.fName = theFont.getName();
    u.fStyle = theFont.getStyle();
    u.fSize = theFont.getSize();
    u.textOrientation = textOrientation;
    u.vAlignment = vAlignment;
    u.hAlignment = hAlignment;
    u.text = new String(theText);

    return u;
  }

  JDLabel(UndoPattern e) {
    initDefault();
    applyUndoPattern(e);
    theFont = new Font(e.fName,e.fStyle,e.fSize);
    textOrientation = e.textOrientation;
    vAlignment = e.vAlignment;
    hAlignment = e.hAlignment;
    theText = e.text;

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

  private void updateLabel(boolean resize) {
    preferredSize = null;
    Dimension d = getMinSize();
    if (resize) {
      if ((summit[2].x - summit[0].x <= d.width) ||
              (summit[6].y - summit[0].y <= d.height)) {
        // Need resize
        // System.out.println("Resize label");
        double x = summit[0].x + d.width;
        double y = summit[0].y + d.height;
        summit[2].x = x;
        summit[4].x = x;
        summit[4].y = y;
        summit[6].y = y;
        centerSummit();
        updateShape();
      }
    }
  }

  private String getSegmentString(Font f, FontRenderContext frc, String str, int wmax) {

    int j,bw;
    boolean found = false;
    String s = "";

    j = str.length();
    while (j > 0 && !found) {
      s = str.substring(0, j);
      Rectangle2D bounds = f.getStringBounds(s, frc);
      bw = (int) Math.ceil(bounds.getWidth());
      found = (bw < wmax);
      j--;
    }

    if (!found)
      return "";
    else
      return s;

  }

  private Dimension getMinSize() {

    if (preferredSize == null) {
      Graphics g = img.getGraphics();
      g.setFont(theFont);
      Graphics2D g2 = (Graphics2D) g;
      g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
          RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
      g2.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS,
          RenderingHints.VALUE_FRACTIONALMETRICS_ON);
      FontRenderContext frc = g2.getFontRenderContext();

      String[] lines = theText.split("\n");
      int wmax = 0;
      int hmax = 0;
      int w,h;
      for (int i = 0; i < lines.length; i++) {
        Rectangle2D bounds = g.getFont().getStringBounds(lines[i], frc);
        w = (int) Math.ceil(bounds.getWidth());
        h = (int) Math.ceil(bounds.getHeight());
        if (w > wmax) wmax = w;
        hmax += h;
      }
      g.dispose();
      if (textOrientation == LEFT_TO_RIGHT || textOrientation == RIGHT_TO_LEFT) {
        preferredSize = new Dimension(wmax + 6, hmax + 4);
      } else {
        preferredSize = new Dimension(hmax + 4, wmax + 6);
      }
    }

    return preferredSize;

  }

}