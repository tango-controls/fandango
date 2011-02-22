/**
 * JDraw Image graphic object
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.geom.Point2D;
import java.awt.image.BufferedImage;
import java.io.FileWriter;
import java.io.IOException;
import java.io.File;

/** JDraw Image graphic object. JDraw supports GIF, JPG and PNG format. Alpha mask is supported for
    PNG image. */
public class JDImage extends JDRectangular {

  // Vars
  static private ImageIcon defaultImage = new ImageIcon(JDImage.class.getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/not_found.gif"));
  private Image theImage = null;
  private int imgWidth = 0;
  private int imgHeight = 0;
  private String fileName;

  /**
   * Contruct an image.
   * @param objectName Image name
   * @param fileName Image file name.
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   */
  public JDImage(String objectName, String fileName, int x, int y) {
    initDefault();
    setOrigin(new Point.Double(0.0, 0.0));
    summit = new Point.Double[8];
    name = objectName;
    this.fileName = fileName;
    lineWidth = 0;
    createSummit();
    loadImage();
    computeSummitCoordinates(x,y,imgWidth,imgHeight);
    updateShape();
    centerOrigin();

  }

  JDImage(JDImage e, int x, int y) {
    cloneObject(e, x, y);
    fileName = new String(e.fileName);
    invalidateImage();
    updateShape();
  }

  JDImage(JLXObject jlxObj,String fileName) {

    initDefault();
    loadObject(jlxObj);

    double x = jlxObj.boundRect.getX();
    double y = jlxObj.boundRect.getY();
    double w = jlxObj.boundRect.getWidth();
    double h = jlxObj.boundRect.getHeight();

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[8];
    createSummit();

    if(fileName.startsWith("file:/"))
      fileName = fileName.substring(6);
    this.fileName = fileName;
    lineWidth = 0;
    fillStyle = JDObject.FILL_STYLE_NONE;

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

    loadImage();

    updateShape();

  }

  JDImage(LXObject lxObj,String fileName) {

    initDefault();
    loadObject(lxObj);

    double x = lxObj.boundRect.getX();
    double y = lxObj.boundRect.getY();
    double w = lxObj.boundRect.getWidth()-1;
    double h = lxObj.boundRect.getHeight()-1;

    setOrigin(new Point2D.Double(x+w/2.0, y+h/2.0));
    summit = new Point2D.Double[8];
    createSummit();

    if(fileName.startsWith("file:/"))
      fileName = fileName.substring(6);
    this.fileName = fileName;
    lineWidth = 0;
    fillStyle = JDObject.FILL_STYLE_NONE;

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

    loadImage();

    updateShape();

  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  public JDObject copy(int x, int y) {
    return new JDImage(this, x, y);
  }

  public void paint(JDrawEditor parent,Graphics g) {

    if (!visible) return;
    prepareRendering((Graphics2D)g);
    super.paint(parent,g);
    loadImage();
    g.drawImage(theImage,boundRect.x, boundRect.y, boundRect.width, boundRect.height,null);

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

  }

  /** Returns false, Image cannot be shadowed. */
  public boolean hasShadow() {
    return false;
  }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------

  /**
   * Loads a new image into this object.
   * @param fileName Image file name.
   */
  public void setFileName(String fileName) {
    this.fileName = fileName;
    invalidateImage();
    loadImage();
    computeSummitCoordinates((int)summit[0].x, (int)summit[0].y, imgWidth,imgHeight);
    updateShape();
    centerOrigin();
  }

  /** Returns current image filename. */
  public String getFileName() {
    return fileName;
  }

  /** Reset the size to its original size. */
  public void resetToOriginalSize() {
    computeSummitCoordinates((int)summit[0].x, (int)summit[0].y, imgWidth,imgHeight);
    updateShape();
    centerOrigin();
  }

  /**
   * Returns original image widht.
   */
  public int getImageWidth() {
    return imgWidth;
  }

  /**
   * Returns original image height.
   */
  public int getImageHeight() {
    return imgHeight;
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  void saveObject(FileWriter f, int level) throws IOException {

    String decal = saveObjectHeader(f, level);
    String to_write;
    to_write = decal + "file_name:\"" + fileName + "\"\n";
    f.write(to_write, 0, to_write.length());
    closeObjectHeader(f, level);

  }

  JDImage(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("file_name")) {
        fileName = f.parseString();
      } else
        loadDefaultPropery(f, propName);
    }

    f.endBlock();

    invalidateImage();
    updateShape();
  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDImage);
    fillUndoPattern(u);
    u.fileName = new String(fileName);

    return u;
  }

  JDImage(UndoPattern e) {

    initDefault();
    applyUndoPattern(e);
    fileName = e.fileName;
    invalidateImage();
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

    summit[2].x = x + width-1;
    summit[2].y = y;

    summit[4].x = x + width-1;
    summit[4].y = y + height-1;

    summit[6].x = x;
    summit[6].y = y + height-1;

    centerSummit();

  }


  private void invalidateImage() {
    theImage=null;
  }

  private void loadImage() {

    if (theImage == null) {

      try {
        File in = new File(fileName);
        theImage = ImageIO.read(in);
        imgWidth = ((BufferedImage)theImage).getWidth();
        imgHeight = ((BufferedImage)theImage).getHeight();
      } catch (IOException e) {
        // Load failure
        System.out.println("JDImage.loadImage() Warning " + fileName + " load failed : " + e.getMessage());
        theImage = defaultImage.getImage();
        imgWidth = defaultImage.getIconWidth();
        imgHeight = defaultImage.getIconHeight();
      }

    }

  }

}