/**
 * JDraw Swing graphic object
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.border.Border;
import java.awt.*;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Constructor;

/** JDraw Swing graphic object. JDSwingObject allows a JComponent to be edited (and played)
 * within JDraw as if it is a JDObject. The JComponent must implements the JDrawable interface.
 * Implementing JDrawable for a Component is interresting if you want to make your component
 * available in the JDrawEditor. Adding a component for playing only can be done
 * by using the classic add(Component) method, no need here to be JDrawable ,however the add() method
 * shoud be called after initPlayer() or loadFile() is called.
 * Here is an example of a simple JDrawable JButton:<p>
 * <pre>
 public class MyJDButton extends JButton implements JDrawable {

  static String[] extensions = {"text"};

  public void initForEditing() {
    setText("Button");
    setBorder(JDSwingObject.etchedBevelBorder);
  }

  public JComponent getComponent() {
    return this;
  }

  public String[] getExtensionList() {
    return extensions;
  }

  public boolean setExtendedParam(String name,String value,boolean popupAllowed) {
    if(name.equalsIgnoreCase("text")) {
      setText(value);
      return true;
    }
    return false;
  }

  public String getExtendedParam(String name) {
    if(name.equalsIgnoreCase("text")) {
      return getText();
    }
    return "";
  }

  public String getDescription(String extName) {
    if(extName.equalsIgnoreCase("text")) {
      return "JButton label";
    }
    return "";
  }

}
 * </pre>
 * @see JDrawable
 * @see JDrawableList
 * @see JDrawEditorFrame#main
 */

public class JDSwingObject extends JDRectangular {

  /** Swing Lowered border used by JDSwingObject. */
  public static Border lowerBevelBorder  = BorderFactory.createLoweredBevelBorder();
  /** Swing Raised border used by JDSwingObject. */
  public static Border raiseBevelBorder  = BorderFactory.createRaisedBevelBorder();
  /** Swing Etched border used by JDSwingObject. */
  public static Border etchedBevelBorder = BorderFactory.createEtchedBorder();

  /** No border. */
  public final static int NO_BORDER      = 0;
  /** Lowered border. */
  public final static int LOWERED_BORDER = 1;
  /** Raised border. */
  public final static int RAISED_BORDER  = 2;
  /** Etched border. */
  public final static int ETCHED_BORDER  = 3;

  static final int borderDefault = NO_BORDER;

  // Vars
  private String     className = "";
  private JDrawable  swingComp = null;
  private Font       theFont;
  private int        border;

  /**
   * Contruct a JDSwingObject
   * @param objectName Object name
   * @param className Class name of the JDrawable object
   * @param x Up left corner x coordinate
   * @param y Up left corner y coordinate
   */
  public JDSwingObject(String objectName,String className, int x, int y) {

    Dimension d;


    initDefault();
    setOrigin(new Point.Double(0.0, 0.0));
    summit = new Point.Double[8];
    name = objectName;
    this.className = className;
    lineWidth = 0;
    fillStyle = JDObject.FILL_STYLE_SOLID;
    createSummit();
    constructComponent(true);

    if(swingComp!=null) {
      d = swingComp.getComponent().getPreferredSize();
      if(d.width<16) d.width = 16;
      if(d.height<16) d.height = 16;
    } else
      d = new Dimension(16,16);

    computeSummitCoordinates(x,y,d.width,d.height);
    updateShape();
    centerOrigin();

  }

  JDSwingObject(JDSwingObject e, int x, int y) {
    cloneObject(e, x, y);
    className = e.className;
    theFont = new Font(e.theFont.getName(), e.theFont.getStyle(), e.theFont.getSize());
    border = e.border;
    constructComponent(false);
    mapExtensions();
    updateShape();
  }

  // -----------------------------------------------------------
  // Overrides
  // -----------------------------------------------------------
  void initDefault() {
    super.initDefault();
    theFont = JDLabel.fontDefault;
    border = borderDefault;
  }

  public JDObject copy(int x, int y) {
    return new JDSwingObject(this, x, y);
  }

  public void paint(JDrawEditor parent,Graphics g) {

    if(!visible) return;
    if(swingComp==null) return;
    if(parent.getMode()==JDrawEditor.MODE_PLAY)
      // In PLAY_MODE, Paint is done by the JDrawEditor
      return;

    Graphics2D g2 = (Graphics2D) g;
    // No anti aliasing for SwingObject
    antiAlias = false;
    prepareRendering(g2);

    // Ugly sequence to paint a JComponent on an arbitrary Graphics.
    // Tips are welcome...
    swingComp.getComponent().validate();
    SwingUtilities.paintComponent(g,swingComp.getComponent(),parent,boundRect);
    swingComp.getComponent().setBounds(boundRect);

  }

  void setExtendedParam(String name,String value,boolean ignoreError) {
    if(isFixedExtendedParam(name)) {
      swingComp.setExtendedParam(name, value, !ignoreError);
      // Some components may need refresh
      super.setExtendedParam(name, swingComp.getExtendedParam(name));
    } else {
      super.setExtendedParam(name, value);
    }
  }

  /**
   * Returns true if the specified param is fixed. (coming from JDrawable)
   * @param name Param name.
   */
  public boolean isFixedExtendedParam(String name) {
    return getSwingExtensionIdx(name)>=0;
  }

  private int getSwingExtensionIdx(String name) {

    int ret = -1;
    if(swingComp!=null) {

      String[] lst = swingComp.getExtensionList();
      boolean found = false;
      int i=0;
      while(i<lst.length && !found) {
        found = lst[i].equalsIgnoreCase(name);
        if(!found) i++;
      }
      if(found) return i;

    }
    return ret;

  }

  public void setExtendedParam(String name,String value) {
    setExtendedParam(name,value,false);
  }

  public void removeExtension(int idx) {
    if(swingComp!=null) {
      String extName = getExtendedParamName(idx);
      if(isFixedExtendedParam(extName)) {
        // Cannot remove Swing extension
        System.out.println("JDSwingObject.removeExtension() : Warning, trying to remove JDrawable extension '"+extName+"'.");
        return;
      }
    }
    super.removeExtension(idx);
  }

  public String getExtendedParamDesc(String extName) {
    if(swingComp!=null) {
      return swingComp.getDescription(extName);
    }
    return "";
  }

  void updateShape() {

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

    // Boundrect
    computeBoundRect();

    // Map JDObject property to JComponent
    if (swingComp != null) {

      ///srubio@cells.es: All this parameters are set directly to the swing object by setXXX(...) methods
	/// It should not be overrided here
      //swingComp.getComponent().setBackground(background);
      //swingComp.getComponent().setForeground(foreground);
      //swingComp.getComponent().setVisible(visible);
      //swingComp.getComponent().setOpaque(fillStyle != JDObject.FILL_STYLE_NONE);
      swingComp.getComponent().setFont(theFont);
      switch (border) {
        case NO_BORDER:
          swingComp.getComponent().setBorder(null);
          break;
        case LOWERED_BORDER:
          swingComp.getComponent().setBorder(lowerBevelBorder);
          break;
        case RAISED_BORDER:
          swingComp.getComponent().setBorder(raiseBevelBorder);
          break;
        case ETCHED_BORDER:
          swingComp.getComponent().setBorder(etchedBevelBorder);
          break;
      }

      swingComp.getComponent().setBounds(boundRect);

    }

  }

  public void setBackground(Color b) {
    super.setBackground(b);
    if(swingComp!=null)
      swingComp.getComponent().setBackground(b);
  }

  public void setForeground(Color b) {
    super.setForeground(b);
    if(swingComp!=null)
      swingComp.getComponent().setForeground(b);
  }

  public void setVisible(boolean v) {
    super.setVisible(v);
    if(swingComp!=null)
      swingComp.getComponent().setVisible(v);
  }

  public void setFillStyle(int style) {
    super.setFillStyle(style);
    if(swingComp!=null)
      swingComp.getComponent().setOpaque(fillStyle != JDObject.FILL_STYLE_NONE);
  }

  /**
   * Sets the font of this JDSwingObject.
   * @param f Font
   */
  public void setFont(Font f) {
    setFont(f,false);
  }

  /**
   * Sets the font of this JDSwingObject and resize the component if needed.
   * @param f Font
   * @param resize true to resize the component.
   */
  public void setFont(Font f,boolean resize) {
    theFont = f;
    updateComp(resize);
  }

  /**
   * Sets the border of this component.
   * @param border Border
   * @see #NO_BORDER
   * @see #LOWERED_BORDER
   * @see #RAISED_BORDER
   * @see #ETCHED_BORDER
   */
  public void setBorder(int border) {
    this.border = border;
    updateShape();
  }

  /**
   * Returns the current border.
   * @see #setBorder
   */
  public int getBorder() {
    return border;
  }

  /**
   * Returns the current font.
   * @see #setFont(Font)
   * @see #setFont(Font,boolean)
   */
  public Font getFont() {
    return theFont;
  }

  public boolean hasShadow() {
    // SwingObject cannot have shadow
    return false;
  }

  // -----------------------------------------------------------
  // Property stuff
  // -----------------------------------------------------------

  /** Returns class name of the Swing JComponent object. */
  public String getClassName() {
    return className;
  }

  /** Returns the actual JComponent. */
  public JComponent getComponent() {
    if(swingComp!=null)
      return swingComp.getComponent();
    else
      return null;
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  void saveObject(FileWriter f, int level) throws IOException {

    String decal = saveObjectHeader(f, level);
    String to_write;

    to_write = decal + "className:\"" + className + "\"\n";
    f.write(to_write, 0, to_write.length());

    if (theFont.getName() != JDLabel.fontDefault.getName() ||
        theFont.getStyle() != JDLabel.fontDefault.getStyle() ||
        theFont.getSize() != JDLabel.fontDefault.getSize()) {
      to_write = decal + "font:\"" + theFont.getName() + "\"," + theFont.getStyle() + "," + theFont.getSize() + "\n";
      f.write(to_write, 0, to_write.length());
    }

    if (border != borderDefault) {
      to_write = decal + "border:" + border + "\n";
      f.write(to_write, 0, to_write.length());
    }

    closeObjectHeader(f, level);

  }

  JDSwingObject(JDFileLoader f) throws IOException {

    initDefault();
    f.startBlock();
    summit = f.parseRectangularSummitArray();

    while (!f.isEndBlock()) {
      String propName = f.parseProperyName();
      if (propName.equals("className")) {
        className = f.parseString();
      } else if (propName.equals("font")) {
        theFont = f.parseFont();
      } else if (propName.equals("border")) {
        border = (int) f.parseDouble();
      } else
        loadDefaultPropery(f, propName);
    }

    f.endBlock();

    constructComponent(false);
    mapExtensions();
    updateShape();
  }

  // -----------------------------------------------------------
  // Undo buffer
  // -----------------------------------------------------------
  UndoPattern getUndoPattern() {

    UndoPattern u = new UndoPattern(UndoPattern._JDSwingObject);
    fillUndoPattern(u);
    u.className = className;
    u.swingComp = swingComp;
    u.fName = theFont.getName();
    u.fStyle = theFont.getStyle();
    u.fSize = theFont.getSize();
    u.border = border;

    return u;
  }

  JDSwingObject(UndoPattern e) {

    initDefault();
    applyUndoPattern(e);
    className = e.className;
    swingComp = e.swingComp;
    theFont = new Font(e.fName,e.fStyle,e.fSize);
    border = e.border;
    mapExtensions();
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

  private void updateComp(boolean resize) {

    if (swingComp != null) {
      swingComp.getComponent().setFont(theFont);
      if (resize) {
        Dimension d = swingComp.getComponent().getPreferredSize();
        if (d.width < 8) d.width = 8;
        if (d.height < 8) d.height = 8;
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

  }

  private void mapExtensions() {

    // Reapply back externsions to SwingObject
    if (swingComp != null) {
      int nbExt = getExtendedParamNumber();
      for (int i = 0; i < nbExt; i++) {
        swingComp.setExtendedParam(getExtendedParamName(i),
                                   getExtendedParam(i),
                                   false);
      }
    }

  }

  private void constructComponent(boolean loadExtension) {

    // Create the component
    try {

      Class[]      types = new Class[0];
      Object[]     params = new Object[0];
      Class        swingClass = Class.forName(className);
      Constructor  swingNew = swingClass.getConstructor(types);
      swingComp = (JDrawable)swingNew.newInstance(params);
      swingComp.initForEditing();
      String[] extList = swingComp.getExtensionList();

      // Retrieve extension
      if (loadExtension) {

        setExtensionList(extList);
        for (int i = 0; i < extList.length; i++) {
          super.setExtendedParam(i, swingComp.getExtendedParam(extList[i]));
        }
        theFont = swingComp.getComponent().getFont();
        if(theFont==null) {
          theFont = JDLabel.fontDefault;
          swingComp.getComponent().setFont(theFont);
        }
	///To use this values for foreground and background is useless if the configuration for the swing object has not been loaded yet!!!
	/// ... and for any reason it has not been loaded ...
        foreground = swingComp.getComponent().getForeground();
        background = swingComp.getComponent().getBackground();
        Border b = swingComp.getComponent().getBorder();
        if(b == lowerBevelBorder) {
          border = LOWERED_BORDER;
        } else if (b == raiseBevelBorder) {
          border = RAISED_BORDER;
        } else if (b == etchedBevelBorder) {
          border = ETCHED_BORDER;
        }

      } else {

        // Check for new extensions
        for(int i=0;i<extList.length;i++) {
          if(!hasExtendedParam(extList[i])) {
            // New extensions
            addExtension(extList[i]);
            super.setExtendedParam(extList[i], swingComp.getExtendedParam(extList[i]));
          }
        }

      }

    } catch (Exception e) {

      System.out.println("JDraw.constructComponent() : " + e.getClass() + " while trying to construct " + className);
      swingComp = null;

    }

  }

}