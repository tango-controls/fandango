/**
 * A set of class to handle a graphical synoptic viewer (vector drawing) and its editor.
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.*;
import java.awt.event.*;
import java.util.Vector;
import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.IOException;

/** ******************************************************************************************************
srubio@cells.es, oktober 2006
The JDrawEditor class has been modified to:
	- Allow contextual menus in MODE_LIB
	- Allow to add new options to the contextual menu

srubio@cells.es, June 2008
	- JDObject Extension "ignoreMouse" disables the relaying of mouse events from the editor to the objects
*********************************************************************************************************/

/** The graph editor/viewer component. */
public class JDrawEditor extends JComponent implements MouseMotionListener, MouseListener,
                                                       ActionListener, KeyListener, ComponentListener {

  // Mode of the editor
  /** Editor is in classic edition mode */
  final static public int MODE_EDIT  = 1;
  /** Group edition mode, this is a restricted edition mode (no undo possible) */
  final static public int MODE_EDIT_GROUP = 2;
  /** Play mode, play object according to their value , in this mode no contextual menu is displayed */
  final static public int MODE_PLAY = 3;
  /** Library mode, allow only selection and clipboard */
  final static public int MODE_LIB = 4;

  /** Creation mode of the editor */
  final static public int CREATE_RECTANGLE = 1;
  /** Creation mode of the editor */
  final static public int CREATE_LINE = 2;
  /** Creation mode of the editor */
  final static public int CREATE_ELLIPSE = 3;
  /** Creation mode of the editor */
  final static public int CREATE_POLYLINE = 4;
  /** Creation mode of the editor */
  final static public int CREATE_LABEL = 5;
  /** Creation mode of the editor */
  final static public int CREATE_SPLINE = 6;
  /** Creation mode of the editor */
  final static public int CREATE_CLIPBOARD = 7;
  /** Creation mode of the editor */
  final static public int CREATE_RRECTANGLE = 8;
  /** Creation mode of the editor */
  final static public int CREATE_IMAGE = 9;
  /** Creation mode of the editor */
  final static public int CREATE_SWINGOBJECT = 10;
  /** Creation mode of the editor */
  final static public int CREATE_AXIS = 11;
  /** Creation mode of the editor */
  final static public int CREATE_BAR = 12;
  /** Creation mode of the editor */
  final static public int CREATE_SLIDER = 13;
  /** Creation mode of the editor */
  final static int CREATE_SLIDER_CURSOR = 14;
  /** Creation mode of the editor */
  final static int CREATE_CONNECT_POLY = 15;

  final static private int undoLength=20;

  // Private declaration
  private Vector objects;
  private Vector clipboard;
  private Vector undo;
  private int undoPos;
  private int curObject;
  private Vector selObjects;
  private boolean isDraggingSummits;
  private int[]   selSummits;
  private boolean isDraggingSummit;
  private int     selSummit;
  private boolean isDraggingObject;
  private boolean isDraggingSelection;
  private boolean hasMoved;
  private int lastX;
  private int lastY;
  private int selX1;
  private int selY1;
  private int selX2;
  private int selY2;
  private int creationMode;
  private JDObject lastCreatedObject=null;
  private Vector tmpPoints;
  private JPopupMenu objMenu;
  private JPopupMenu polyMenu;
  private JDPolyline editedPolyline;
  private int zoomFactor = 0;
  private double autoZoomFactor = 1.0;
  private boolean autoZoom = false;
  private int sizeX;
  private int sizeY;
  private String lastFileName = "";
  private boolean needToSave = false;
  Vector listeners;
  private int mode;
  private int transx;
  private int transy;
  private JDObject pressedObject=null;
  private JDObject motionObject=null;
  private boolean alignToGrid=false;
  private int GRID_SIZE=16;
  private boolean gridVisible=false;
  private String creationParam = null;
  boolean resizeLabelOnFontChange = true;
  boolean resizeLabelOnTextChange = true;
  private JDSlider sliderRef; // Used to pick new cursor
  private JDPolyline connectPolyline;
  private JLabel statusLabel = null;
  private String currentStatus = "";

  // ------- Object Contextual menu ----------------
  private JSeparator sep1;
  private JSeparator sep2;
  private JSeparator sep3;
  private JSeparator sep4;
  private JSeparator sep5;

  private JMenuItem infoMenuItem;

  private JMenuItem cutMenuItem;
  private JMenuItem copyMenuItem;
  private JMenuItem pasteMenuItem;
  private JMenuItem deleteMenuItem;

  private JMenuItem zoomInMenuItem;
  private JMenuItem zoomOutMenuItem;

  private JMenuItem groupMenuItem;
  private JMenuItem ungroupMenuItem;

  private JMenuItem editShapeMenuItem;
  private JMenuItem connectShapeMenuItem;

  private JMenuItem raiseMenuItem;
  private JMenuItem lowerMenuItem;
  private JMenuItem frontMenuItem;
  private JMenuItem backMenuItem;

  // ------------------------------------------------
  /** Views->Transform menu item. */
  public  JMenuItem viewsTransformMenuItem;
  /** Views->Play menu item. */
  public  JMenuItem viewsPlayMenuItem;
  /** Views->Object properties menu item. */
  public  JMenuItem viewsOptionMenuItem;
  /** Views->Browse menu item. */
  public  JMenuItem viewsBrowseMenuItem;
  /** Views->Edit group menu item. */
  private JMenuItem viewsGroupEditMenuItem;
//also added to createContextualMenu
//also added to actionPerformed
//also added to showMenu


  // ------- Polyline Contextual menu ----------------
  private JMenuItem infoPolyMenuItem;

  private JMenuItem delSummitMenuItem;
  private JMenuItem brkShapeMenuItem;
  private JMenuItem set0ShapeMenuItem;
  private JMenuItem reorderShapeMenuItem;
  private JMenuItem cancelShapeMenuItem;

  static private Cursor hCursor = Cursor.getPredefinedCursor(Cursor.W_RESIZE_CURSOR);
  static private Cursor vCursor = Cursor.getPredefinedCursor(Cursor.N_RESIZE_CURSOR);
  static private Cursor nwCursor = Cursor.getPredefinedCursor(Cursor.NW_RESIZE_CURSOR);
  static private Cursor neCursor = Cursor.getPredefinedCursor(Cursor.NE_RESIZE_CURSOR);
  static private Cursor seCursor = Cursor.getPredefinedCursor(Cursor.SE_RESIZE_CURSOR);
  static private Cursor swCursor = Cursor.getPredefinedCursor(Cursor.SW_RESIZE_CURSOR);
  static private Cursor bCursor = Cursor.getPredefinedCursor(Cursor.MOVE_CURSOR);
  static private Cursor dCursor = Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR);

  final static Color defaultBackground = new Color(230, 230, 230);

  // -----------------------------------------------------
  // Construction
  // -----------------------------------------------------

  /**
   * Contruct a JDraw editor in the specified mode.
   * @param mode Mode of the editor
   * @see JDrawEditor#MODE_EDIT
   * @see JDrawEditor#MODE_EDIT_GROUP
   * @see JDrawEditor#MODE_PLAY
   */
  public JDrawEditor(int mode) {
    setLayout(null);
    this.mode = mode;
    initComponents();
  }

  private void initComponents() {

    objects = new Vector();
    selObjects = new Vector();

    // Tests ----------------------------------------------------------

    /*
    Point[] ptl = {new Point(340, 120), new Point(350, 240), new Point(434, 320), new Point(482, 228)};

    objects.add(new JDRectangle("Rectangle1", 100, 100, 80, 50));
    objects.add(new JDRectangle("Rectangle2", 200, 120, 180, 70));
    objects.add(new JDRectangle("Rectangle3", 50, 300, 80, 150));
    objects.add(new JDPolyline("Poly1", ptl));
    objects.add(new JDEllipse("Ellipse1", 150, 300, 80, 150));
    JDLabel jl = new JDLabel("Label", "Jean-Luc\nLigne 2\nLigne 3", 230, 178);
    objects.add(jl);

    ((JDObject) objects.get(1)).setBackground(Color.cyan);
    ((JDObject) objects.get(3)).setBackground(Color.red);
    ((JDObject) objects.get(4)).setBackground(Color.blue);
    */
    //jl.setOrientation(JDLabel.BOTTOM_TO_TOP);

    //--------------------------------------------------------------------

    sizeX = 800;
    sizeY = 600;
    setBackground(defaultBackground);
    setOpaque(true);
    isDraggingSummit = false;
    isDraggingSummits = false;
    isDraggingObject = false;
    isDraggingSelection = false;
    hasMoved=false;
    selX1 = selX2 = selY1 = selY2 = 0;
    creationMode = 0;
    transx = transy = 0;
    listeners = new Vector();
    needToSave = false;
    editedPolyline = null;
    selSummits = new int[0];

    switch(mode) {
      case MODE_EDIT:
        clipboard = new Vector();
        tmpPoints = new Vector();
        undo = new Vector();
        clearUndo();
        createContextualMenu();
        break;
      case MODE_EDIT_GROUP:
        tmpPoints = new Vector();
        clipboard = new Vector();
        createContextualMenu();
        break;
      case MODE_LIB:
      case MODE_PLAY:
        break;
    }


    addKeyListener(this);
    addMouseListener(this);
    addMouseMotionListener(this);

  }

  // -----------------------------------------------------
  // Editing stuff
  // -----------------------------------------------------
  /**
   * Shows or hide the grid.
   * @param b True to show the grid, false otherwise.
   */
  public void setGridVisible(boolean b) {
    gridVisible=b;
    repaint();
  }

  /**
   * Determines whether the grid is visible.
   */
  public boolean isGridVisible() {
    return gridVisible;
  }

  /**
   * Sets the grid step size.
   * @param size Grid size (pixel)
   */
  public void setGridSize(int size) {
    if(size>1) {
      GRID_SIZE = size;
      repaint();
    }
  }

  /**
   * Returns the current gid size.
   * @see #setGridSize
   */
  public int getGridSize() {
    return GRID_SIZE;
  }

  /**
   * When enabled, all moved control points and objects will be aligned
   * to the grid.
   * @param b True to align object to grid , false otherwise.
   */
  public void setAlignToGrid(boolean b) {
    alignToGrid = b;
  }

  /**
   * Determines whether object and control point are aligned to the grid.
   * @see #setAlignToGrid
   * @see #setGridSize
   */
  public boolean isAlignToGrid() {
    return alignToGrid;
  }

  /** Returns the mode of the editor. */
  public int getMode() {
    return mode;
  }

  /**
   * Select the specified object. Does not fire selectionChanged().
   * @param obj Object to be selected.
   */
  public void selectObject(JDObject obj) {
    if (obj != null && mode!=MODE_PLAY) {
      if (!isSelected(obj))
        selObjects.add(obj);
      repaint(obj.getRepaintRect());
    }
  }

  /**
   * Unselect the specified object. Does not fire selectionChanged().
   * @param obj Object to be deselected.
   */
  public void unselectObject(JDObject obj) {
    if (obj != null && mode!=MODE_PLAY) {
      selObjects.remove(obj);
      repaint(obj.getRepaintRect());
    }
  }

  /**
   * Determine wheter the specifed object is selected.
   * @param obj JDObject
   * @see #selectObject
   * @see #unselectObject
   */
  public boolean isSelected(JDObject obj) {
    if( mode==MODE_PLAY ) return false;
    return selObjects.contains(obj);
  }

  /**
   * Selects all specified objects.
   * @param objs Array of JDObject to be selected.
   */
  public void selectObjects(JDObject[] objs) {
    if (objs.length>0 && mode!=MODE_PLAY && selObjects.size()==0) {
      for (int i = 0; i < objs.length; i++)
        selObjects.add(objs[i]);
      repaint(buildRepaintRect(selObjects));
    }
  }

  /** Get number of object */
  public int getObjectNumber() {
    return objects.size();
  }

  /** Get the JDObject at the specified position.
   * @param idx Object index.
   */
  public JDObject getObjectAt(int idx) {
    return (JDObject)objects.get(idx);
  }

  /** Used for read only purpose , vector should not be modified by this way. */
  public Vector getObjects() {
    return objects;
  }

  /** Used for read only purpose , vector should not be modified by this way. */
  public Vector getSelectedObjects() {
    return selObjects;
  }

  /** Used for read only purpose , vector should not be modified by this way. */
  public Vector getClipboardObjects() {
    return clipboard;
  }

  void setClipboard(Vector objects) {
    clipboard.clear();
    clipboard.addAll(objects);
  }

  /** Unselect all object */
  public void unselectAll() {
    unselectAll(true);
  }

  private void unselectAll(boolean fireSelChanged) {
    if(mode==MODE_PLAY) return;
    repaint(buildRepaintRect(selObjects));
    selObjects.clear();
    editedPolyline = null;
    if(fireSelChanged)
      fireSelectionChange();
  }

  /** Select all object */
  public void selectAll() {
    selectAll(true);
  }

  private void selectAll(boolean fireSelChanged) {
    if(mode==MODE_PLAY) return;
    selObjects.clear();
    selObjects.addAll(objects);
    editedPolyline = null;
    repaint(buildRepaintRect(objects));
    if(fireSelChanged)
      fireSelectionChange();
  }

  /** Sets the editor in creation mode.
   *  @param what Object to be created
   *  @see #create(int,String)
   *  @see #CREATE_RECTANGLE
   *  @see #CREATE_LINE
   *  @see #CREATE_ELLIPSE
   *  @see #CREATE_POLYLINE
   *  @see #CREATE_LABEL
   *  @see #CREATE_SPLINE
   *  @see #CREATE_CLIPBOARD
   *  @see #CREATE_RRECTANGLE
   *  @see #CREATE_IMAGE
   *  @see #CREATE_SWINGOBJECT
   *  @see #CREATE_AXIS
   *  @see #CREATE_BAR
   *  @see #CREATE_SLIDER
   */
  public void create(int what) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    initCreate(what);
  }


  /** Sets the editor in creation mode.
   *  @param what Object to be created
   *  @param param Optional parameters (used for JDSwingObject className)
   *  @see #create(int)
   */
  public void create(int what,String param) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    initCreate(what);
    creationParam = param;
  }

  void pickCursor(JDSlider parent) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(parent==null) return;
    initCreate(CREATE_SLIDER_CURSOR);
    sliderRef = parent;
  }

  void pickPolyline() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()>0) {
      JDObject s = (JDObject)selObjects.get(0);
      if(s instanceof JDPolyline) {
        initCreate(CREATE_CONNECT_POLY);
        connectPolyline = (JDPolyline)s;
      }
    }
  }

  /** Get number of selected object */
  public int getSelectionLength() {
    if(mode==MODE_PLAY) return 0;
    return selObjects.size();
  }

  /** Get number of object inside the clipboard */
  public int getClipboardLength() {
    if(mode==MODE_PLAY) return 0;
    if(mode==MODE_LIB) return 0;
    return clipboard.size();
  }

  /** Shows the property window */
  public void showPropertyWindow() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    JDUtils.showPropertyDialog(this, selObjects);
  }

  /** Shows the property window */
  public void showTransformWindow() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    boolean m = JDUtils.showTransformDialog(this, selObjects);
    if (m) setNeedToSave(true,"transform");
  }

  /** Shows the object browser */
  public void showBrowserWindow() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    boolean m = JDUtils.showBrowserDialog(this, selObjects);
    if (m) setNeedToSave(true,"Property change");
  }

  /** Shows the group editor dialog */
  public void showGroupEditorWindow() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if (selObjects.size() == 1) {
      JDObject p =(JDObject)selObjects.get(0);
      if (p instanceof JDGroup) {
        // Init the modified variable at the root level of group hiearchy
        if(mode==MODE_EDIT) JDUtils.modified = false;
        boolean m = JDUtils.showGroupEditorDialog(this, (JDGroup) p);
        if (m) setNeedToSave(true, "Group edit");
      }
    }
  }

  /** Generates java classes from the selection.
   * @see JDGroup#generateJavaClass
   */
  public void generateJavaClasses(String dirName) throws IOException {

    int i;

    String msgInfo="Destination directory: " + dirName + "\n\n";

    for (i = 0; i < selObjects.size(); i++) {
      JDObject p = (JDObject) selObjects.get(i);
      String fileName = dirName + "\\" + p.getName() + ".java";
      FileWriter f = new FileWriter(fileName);
      f.write("/* Class generated by JDraw */\n\n");
      f.write("import java.awt.*;\n\n");
      if (p instanceof JDGroup) {
        ((JDGroup) p).generateJavaClass(f);
        msgInfo += "   " + p.getName()+".java" + " : OK\n";
      } else {
        msgInfo += "   " + p.getName()+".java" + " : generation failed (Invalid object type)\n";
      }
      f.close();
    }

    JOptionPane.showMessageDialog(this,msgInfo,"Message",JOptionPane.INFORMATION_MESSAGE);

  }

  /** Shows the java generation file selection box */
  public void showGroupJavaWindow() {
    if (mode == MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if (selObjects.size() >= 1) {
      JFileChooser jf = new JFileChooser(".");
      jf.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
      jf.setDialogTitle("Choose directory for java classes generation");
      if (jf.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
        try {
          generateJavaClasses(jf.getSelectedFile().getAbsolutePath());
        } catch (IOException e) {
          JOptionPane.showMessageDialog(this, "Error during java code generation.\n" + e.getMessage());
        }
      }
    }
  }

  /**
   * Fill the clipboard with a copy of given objects.
   * @param objs Objects to add
   */
  void addObjectToClipboard(Vector objs) {
    clipboard.clear();
    for (int i = 0; i < objs.size(); i++)
      clipboard.add(((JDObject)objs.get(i)).copy(0,0));
    fireClipboardChange();
  }

  /** Copy selection to clipboard */
  public void copySelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;
    addObjectToClipboard(selObjects);
  }

  /** Paste the selection at the specified pos.
  * @param x Up left corner x coordinate
  * @param y Up left corner y coordinate
  */
  public void pasteClipboard(int x, int y) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(clipboard.size()==0) return;

    unselectAll(false);
    Point org = JDUtils.getTopLeftCorner(clipboard);
    int tx=x - org.x;
    int ty=y - org.y;

    if( alignToGrid ) {
      tx = ((tx + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      ty = ((ty + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
    }

    boolean hasSwing=false;
    for (int i = 0; i < clipboard.size(); i++) {
      JDObject n = ((JDObject) clipboard.get(i)).copy(tx,ty);
      hasSwing = (n instanceof JDSwingObject) || hasSwing;
      objects.add(n);
      selObjects.add(n);
    }

    setNeedToSave(true,"Paste");
    if(!hasSwing)
      repaint(buildRepaintRect(selObjects));
    else
      repaintLater();
    fireSelectionChange();
  }

  /** Scale selection around the selection center.
   * @param rx Horizontal sace ratio.
   * @param ry Vertical sace ratio.
   */
  public void scaleSelection(double rx, double ry) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    // Repaint old rectangle
    repaint(buildRepaintRect(selObjects));

    Point org = JDUtils.getCenter(selObjects);

    for (int i = 0; i < selObjects.size(); i++)
      ((JDObject) selObjects.get(i)).scale(org.x, org.y, rx, ry);

    setNeedToSave(true,"Scale");
    repaint(buildRepaintRect(selObjects));
  }

  /** Move the selection to clipboard */
  public void cutSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;
    clipboard.clear();
    objects.removeAll(selObjects);
    clipboard.addAll(selObjects);
    repaint(buildRepaintRect(selObjects));
    selObjects.clear();
    editedPolyline = null;
    setNeedToSave(true,"Cut");
    fireSelectionChange();
    fireClipboardChange();

  }

  /** Delete selection from the draw */
  public void deleteSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;
    objects.removeAll(selObjects);
    repaint(buildRepaintRect(selObjects));
    selObjects.clear();
    editedPolyline = null;
    setNeedToSave(true,"Delete");
    fireSelectionChange();
  }

  /**
   * Show the file selection box and call saveFile if a file is selected.
   * Trigger valueChanged() if a file is selected to be saved.
   * @param defaultDir default directory
   * @see JDrawEditor#saveFile
   */
  public void showSaveDialog(String defaultDir) {

    int ok = JOptionPane.YES_OPTION;
    JFileChooser chooser = new JFileChooser(defaultDir);
    if(lastFileName.length()>0)
      chooser.setSelectedFile(new File(lastFileName));
    int returnVal = chooser.showSaveDialog(this);

    if (returnVal == JFileChooser.APPROVE_OPTION) {
      File f = chooser.getSelectedFile();
      if (f != null) {
        if (f.exists()) ok = JOptionPane.showConfirmDialog(this, "Do you want to overwrite " + f.getName() + " ?", "Confirm overwrite", JOptionPane.YES_NO_OPTION);
        if (ok == JOptionPane.YES_OPTION) {
          try {
            saveFile(f.getAbsolutePath());
          } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error during saving file.\n" + e.getMessage());
          }
        }
      }
    }

  }

  /**
   * Save the current drawing to a file.
   * @param fileName File name
   * @throws IOException Exception containing error message when failed.
   */
  public void saveFile(String fileName) throws IOException {
    
    if(fileName.endsWith(".jlx")) {
      String fName = fileName.substring(0,fileName.lastIndexOf('.'));
      if( JOptionPane.showConfirmDialog(this,"Cannot save to JLoox (.jlx) format , save to jdw format ?\n"+fName + ".jdw",
                                        "Save confirmation",JOptionPane.YES_NO_OPTION)==JOptionPane.NO_OPTION)
        return;
      fileName = fName + ".jdw";
    }

    if(fileName.endsWith(".g")) {
      String fName = fileName.substring(0,fileName.lastIndexOf('.'));
      if( JOptionPane.showConfirmDialog(this,"Cannot save to Loox (.g) format , save to jdw format ?\n"+fName + ".jdw",
                                        "Save confirmation",JOptionPane.YES_NO_OPTION)==JOptionPane.NO_OPTION)
        return;
      fileName = fName + ".jdw";
    }

    FileWriter fw = new FileWriter(fileName);
    try {
      fw.write("JDFile v11 {\n");
      fw.write("  Global {\n");
      if(getBackground().getRGB()!=defaultBackground.getRGB())
        fw.write("background:" + getBackground().getRed() + "," + getBackground().getGreen() + "," + getBackground().getBlue());
      fw.write("  }\n");
      for (int i = 0; i < objects.size(); i++)
        ((JDObject) objects.get(i)).saveObject(fw, 1);
      fw.write("}\n");
      fw.close();
    } catch (IOException e) {
      fw.close();
      throw e;
    }
    lastFileName = fileName;
    setNeedToSave(false,"Save");

  }

  /** Save the current drawing to the file (Ask for filename if no filename has been previously set) */
  public void instantSave(String defaultDir) {

    if (lastFileName.length()>0) {
      try {
        saveFile(lastFileName);
      } catch (Exception e) {
        JOptionPane.showMessageDialog(this, "Error during saving file.\n" + e.getMessage());
      }
    } else {
      showSaveDialog(defaultDir);
    }

  }

  /** Load a jdraw grpahics file into the editor
   * Trigger valueChanged() if a file is selected to be loaded.
   * @param fileName File name
   * @throws IOException Exception containing error message when failed.
   * @see JDrawEditorListener#valueChanged
   */
  public void loadFile(String fileName) throws IOException {

    Vector objs;
    FileReader fr = new FileReader(fileName);
    System.out.println("In JDrawEditor::loadFile(...) ...");

    if (fileName.endsWith(".jlx")) {

      // JLOOX files
      JLXFileLoader fl = new JLXFileLoader(fr);
      try {
        objs = fl.parseFile();
        fr.close();
      } catch (IOException e) {
        fr.close();
        throw e;
      }

    } else if (fileName.endsWith(".g")) {

      // LOOX files
      LXFileLoader fl = new LXFileLoader(fr);
      try {
        objs = fl.parseFile();
        fr.close();
      } catch (IOException e) {
        fr.close();
        throw e;
      }

    } else {

      //JDRAW files
      JDFileLoader fl = new JDFileLoader(fr);
      try {
        objs = fl.parseFile();
        fr.close();
      } catch (IOException e) {
        fr.close();
        throw e;
      }

      applyGlobalOption(fl);

    }

    // Load success
    clearObjects();
    editedPolyline = null;
    objects = objs;
    for(int i=0;i<objects.size();i++)
      ((JDObject)objects.get(i)).setParent(this);
    lastFileName = fileName;

    if(mode!=MODE_PLAY) {
      clearUndo();
      setNeedToSave(false,"Load");
      fireSelectionChange();
    } else {
      initPlayer();
    }

    computePreferredSize();
    repaintLater();

  }

  /**
   * Show the file selection box and call loadFile if a file is selected.
   * Trigger valueChanged() if a file is selected to be loaded.
   * @param defaultDir default directory
   * @see JDrawEditorListener#valueChanged
   * @see JDrawEditor#loadFile
   */
  public void showOpenDialog(String defaultDir) {

    int ok = JOptionPane.NO_OPTION;
    if (needToSave) ok = JOptionPane.showConfirmDialog(this ,"Your changes will be lost , save before opening a new file ?",
                                        "Open confirmation",JOptionPane.YES_NO_CANCEL_OPTION);

    if(ok == JOptionPane.YES_OPTION)
      instantSave(".");

    if (ok == JOptionPane.YES_OPTION || ok == JOptionPane.NO_OPTION) {

      JFileChooser chooser = new JFileChooser(defaultDir);
      if(lastFileName.length()>0)
        chooser.setSelectedFile(new File(lastFileName));
      JDFileFilter jlxFilter = new JDFileFilter("JLoox vectorial draw",new String[]{"jlx"});
      chooser.addChoosableFileFilter(jlxFilter);
      JDFileFilter lxFilter = new JDFileFilter("Loox vectorial draw",new String[]{"g"});
      chooser.addChoosableFileFilter(lxFilter);
      JDFileFilter jdwFilter = new JDFileFilter("JDraw graphics program",new String[]{"jdw"});
      chooser.addChoosableFileFilter(jdwFilter);

      int returnVal = chooser.showOpenDialog(this);
      File f = chooser.getSelectedFile();

      if (returnVal == JFileChooser.APPROVE_OPTION) {
        try {
          loadFile(f.getAbsolutePath());
        } catch (IOException ex) {
          JOptionPane.showMessageDialog(this, "Error during reading file: " + f.getName() + "\n" + ex.getMessage());
        }
      }

    }

  }

  /** bring selected object to foreground */
  public void frontSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    Vector nObjects = new Vector();

    // Get ordered list of selected object
    for (int i = 0; i < objects.size(); i++) {
      JDObject p = (JDObject)objects.get(i);
      if (isSelected(p)) nObjects.add(p);
    }

    // Remove them then readd them at the end
    objects.removeAll(nObjects);
    objects.addAll(nObjects);

    setNeedToSave(true,"Bring to front");
    repaint(buildRepaintRect(selObjects));
  }

  /** send selected object to background */
  public void backSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    Vector nObjects = new Vector();

    // Get ordered list of selected object
    for (int i = 0; i < objects.size(); i++) {
      JDObject p = (JDObject)objects.get(i);
      if (isSelected(p)) nObjects.add(p);
    }

    // Remove them then readd them at the begining
    objects.removeAll(nObjects);
    objects.addAll(0,nObjects);

    setNeedToSave(true,"Send to back");
    repaint(buildRepaintRect(selObjects));
  }

  /** group selected objects */
  public void groupSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    Vector nObjects = new Vector();

    // Get ordered list of selected object
    for (int i = 0; i < objects.size(); i++) {
      JDObject p = (JDObject) objects.get(i);
      if (isSelected(p)) nObjects.add(p);
    }

    if (nObjects.size() > 0) {
      selObjects.clear();
      // Remove them
      objects.removeAll(nObjects);

      //Create the group
      JDGroup g = new JDGroup("JDGroup", nObjects);
      selObjects.add(g);
      objects.add(g);
      editedPolyline = null;
      fireSelectionChange();
      setNeedToSave(true,"Group");
      repaint(g.getRepaintRect());
    }

  }

  /** ungroup selected object */
  public void ungroupSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    if (selObjects.size() == 1) {
      JDObject p = (JDObject) selObjects.get(0);
      if (p instanceof JDGroup) {
        JDGroup g = (JDGroup) p;
        repaint(g.getRepaintRect());
        int id = objects.indexOf(g);
        objects.remove(g);
        selObjects.clear();
        // Readd objects
        selObjects.addAll(g.getChildren());
        objects.addAll(id,g.getChildren());
        editedPolyline = null;
        fireSelectionChange();
        setNeedToSave(true,"Ungroup");
      }
    }

  }

  /** Zoom In the graph */
  public void zoomIn() {

    zoomFactor++;
    invalidate();
    fireSizeChanged();
    focusZoomSelection();

  }

  /** Zoom Out the graph */
  public void zoomOut() {

    zoomFactor--;
    invalidate();
    fireSizeChanged();
    focusZoomSelection();

  }

  private void focusZoomSelection() {

    if (selObjects.size() > 0) {
      Object p = getParent();
      if (p instanceof JViewport) {

        JViewport vp = (JViewport) p;
        Rectangle r = buildRepaintRect(selObjects);
        Rectangle zr = new Rectangle(zbconvert(r.x, transx), zbconvert(r.y, transy),
                                     zbconvert(r.width, 0), zbconvert(r.height, 0));
        vp.validate();
        Dimension vr = vp.getSize();
        Rectangle nr = new Rectangle(zr.x - (vr.width-zr.width)/2,zr.y - (vr.height-zr.height)/2,
                                     vr.width,vr.height);

        // This to avoid a JViewport.scrollRectToVisible() bug
        // Unfortunaly this generates jirky sometimes
        vp.setViewPosition(new Point(0,0));

        vp.scrollRectToVisible(nr);

      }
    }

  }

  /** Get the zoom factor in percent */
  public int getZoomFactorPercent() {
    return zbconvert(100,0);
  }

  /**
   * Returns the zoom factor value.
   * @see #getZoomFactorPercent
   */
  public int getZoomFactor() {
    return zoomFactor;
  }

  /** Sets the zoom factor. Does not have effect if autoZoom is enabled.
    *  @param z ZoomFactor ( -1=33% , 0=50% , 1=100% , 2=200% )
    * @see #setAutoZoomFactor
    */
  public void setZoomFactor(int z) {
    zoomFactor=z;
    invalidate();
    fireSizeChanged();
  }

  /** Sets the auto zoom. When auto zoom is enabled, the drawing area follows the
   * window size. This works only in MODE_PLAY.
   * @param b True to enable auto zoom, false otherwise.
   * @see #setAutoZoomFactor
   */
  public void setAutoZoom(boolean b) {
    autoZoom = b;
    if(autoZoom) {
      addComponentListener(this);
    } else {
      removeComponentListener(this);
    }
  }

  /**
   * Sets the initial autoZoom factor. This allows to start the
   * player (PLAY_MOE) with an arbitrary size.
   * @param ratio Zoom factor
   */
  public void setAutoZoomFactor(double ratio) {
    autoZoomFactor = ratio;
  }

  /**
   * Returns true is auto zoom is enabled, false otherwise.
   * @see #setAutoZoom
   */
  public boolean isAutoZoom() {
    return autoZoom;
  }

  /** Translate selected Object */
  public void translateSelection(int x, int y) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    if (selObjects.size() > 0 && (x!=0 || y!=0)) {

      Rectangle oldRect = buildRepaintRect(selObjects);
      repaint(oldRect);
      for (int i = 0; i < selObjects.size(); i++)
        ((JDObject)selObjects.get(i)).translate(x, y);
      oldRect.translate(x,y);
      repaint(oldRect);

      if(isDraggingObject)  hasMoved=true;

    }

  }

  /** Get undo state */
  public boolean canUndo() {
    return (mode==MODE_EDIT) && undoPos>=2;
  }

  /** Get redo state */
  public boolean canRedo() {
    return (mode==MODE_EDIT) && undoPos<undo.size();
  }

  /** Get name of the last action */
  public String getLastActionName() {
    if( canUndo() ) return ((UndoBuffer)undo.get(undoPos-1)).getName();
    else return "";
  }

  /** Get name of the action that can be redone */
  public String getNextActionName() {
    if( canRedo() ) return ((UndoBuffer)undo.get(undoPos)).getName();
    else return "";
  }

  /** Undo the last action */
  public void undo() {
    if( canUndo() ) {
      undoPos--;
      rebuildBackup(undoPos-1);
    }
  }

  /** Redo last canceled action */
  public void redo() {
    if( canRedo() ) {
      undoPos++;
      rebuildBackup(undoPos-1);
    }
  }

  /** Clear the undo buffer */
  public void clearUndo() {
    if (mode==MODE_EDIT) {
      undo.clear();
      undo.add(new UndoBuffer(objects, "Init"));
      undoPos = 1;
    }
  }

  /** Align selection to top */
  public void aligntopSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;

    // repaint old rectangle
    repaint(buildRepaintRect(selObjects));

    JDObject first = (JDObject)selObjects.get(0);
    int orgy = first.getBoundRect().y;

    for (int i = 0; i < selObjects.size(); i++) {
      JDObject n = (JDObject) selObjects.get(i);
      double y = n.boundRect.y;
      n.translate(0.0,orgy-y);
    }

    setNeedToSave(true,"Align");
    repaint(buildRepaintRect(selObjects));
  }

  /** Align selection to left */
  public void alignleftSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;

    // repaint old rectangle
    repaint(buildRepaintRect(selObjects));

    JDObject first = (JDObject)selObjects.get(0);
    int orgx = first.getBoundRect().x;

    for (int i = 0; i < selObjects.size(); i++) {
      JDObject n = (JDObject) selObjects.get(i);
      double x = n.boundRect.x;
      n.translate(orgx-x,0.0);
    }

    setNeedToSave(true,"Align");
    repaint(buildRepaintRect(selObjects));
  }

  /** Align selection to bottom */
  public void alignbottomSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;

    // repaint old rectangle
    repaint(buildRepaintRect(selObjects));

    JDObject first = (JDObject)selObjects.get(0);
    int orgy = first.getBoundRect().y + first.getBoundRect().height;

    for (int i = 0; i < selObjects.size(); i++) {
      JDObject n = (JDObject) selObjects.get(i);
      double y = n.boundRect.y+n.boundRect.height;
      n.translate(0.0,orgy-y);
    }

    setNeedToSave(true,"Align");
    repaint(buildRepaintRect(selObjects));
  }

  /** Align selection to right */
  public void alignrightSelection() {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    if(selObjects.size()==0) return;

    // repaint old rectangle
    repaint(buildRepaintRect(selObjects));

    JDObject first = (JDObject)selObjects.get(0);
    int orgx = first.getBoundRect().x + first.getBoundRect().width;

    for (int i = 0; i < selObjects.size(); i++) {
      JDObject n = (JDObject) selObjects.get(i);
      double x = n.boundRect.x+n.boundRect.width;
      n.translate(orgx-x,0.0);
    }

    setNeedToSave(true,"Align");
    repaint(buildRepaintRect(selObjects));
  }

  /**
   * Add an JDrawEditor listener.
   * @param l Editor listener.
   * @see JDrawEditorListener
   */
  public void addEditorListener(JDrawEditorListener l) {
    listeners.add(l);
  }

  /**
   * Remove an JDrawEditor listener.
   * @param l Editor listener.
   * @see JDrawEditorListener
   */
  public void removeEditorListener(JDrawEditorListener l) {
    listeners.remove(l);
  }

  /**
   * Clears the JDrawEditor listener list.
   * @see JDrawEditorListener
   */
  public void clearEditorListener() {
    listeners.clear();
  }

  /** Returns true if the drawing has been modofied and need to be saved */
  public boolean getNeedToSaveState() {
    return needToSave;
  }

  /** Gets the name of the last loaded file */
  public String getFileName() {
    return lastFileName;
  }

  /** Add an object to the drawing. If you want to add dynamcaly object to this
   * editor (in PLAY_MODE) , You should call initPlayer() after all objects
   * are inserted.
   * @see #initPlayer
   */
  public void addObject(JDObject o) {
    objects.add(o);
    o.setParent(this);
  }

  /** Clear all object */
  public void clearObjects() {
    objects.clear();
    if(mode==MODE_PLAY) return;
    selObjects.clear();
  }

  /** Set a global translation for the drawing area */
  public void setTranslation(int x,int y) {
    transx = x;
    transy = y;
  }

  /** Compute the optimal size of the components and trigger sizeChanged() */
  public void computePreferredSize() {
    Dimension d = new Dimension();
    Rectangle old=null;
    System.out.println("In JDrawEditor::computePreferredSize(...) ...");
    for(int i=0;i<objects.size();i++) {
      if(old==null)
        old = getObjectAt(i).getBoundRect();
      else
        old = old.union(getObjectAt(i).getBoundRect());
    }

    if( old==null ) {
      d.width  = 320;
      d.height = 200;
    } else {
      d.width   = old.x + old.width + 1;
      d.height  = old.y + old.height + 1;
    }

    setPreferredSize(d);
    fireSizeChanged();

  }

  public void setPreferredSize(Dimension d) {
    sizeX = d.width;
    sizeY = d.height;
  }

  public Dimension getPreferredSize() {
    return new Dimension(zbconvert(sizeX,0), zbconvert(sizeY,0));
  }

  public Dimension getMinimumSize() {
    Object p = getParent();
    if(p instanceof JSplitPane) {
      return new Dimension(16,16);
    } else {
      return getPreferredSize();
    }
  }

  /** Inits the player, This function should be called only if you want
   * to build dynamicaly a graph with addObject(). Call it after all
   * objects are inserted in the Editor.
   * The call to this function is not absolutly needed. Call it
   * only if you want to PLAY JDSwingObject or if you want to
   * animate objects.
   * @see #addObject
   */
  public void initPlayer() {

    if(mode!=MODE_PLAY)
      return;

    for(int i=0;i<objects.size();i++) {
      getObjectAt(i).saveTransform();
      getObjectAt(i).initValue();
    }

    // Add Swing JDObject into the Container
    removeAll();
    Vector v = getObjectsOfClass(JDSwingObject.class);
    int sz = v.size();
    for(int i=0;i<sz;i++) {
	try {
      	add(((JDSwingObject)v.get(sz-i-1)).getComponent());
	} catch (Exception e) {
		System.out.println("Exception in JDrawEditor.initPlayer: "+e.toString());
	}
    }

  }

  /**
   * Retunrs all objects of the specified class present in the drawing area.
   * @param theClass JDObject subclass
   */
  public Vector getObjectsOfClass(Class theClass) {
    Vector ret = new Vector();
    for(int i=0;i<objects.size();i++)
      ((JDObject)objects.get(i)).getObjectsByClassList(ret,theClass);
    return ret;
  }

  /**
   * Returns all objects having the given name present in the drawing area.
   * @param name JDObject name (Case sensitive)
   * @param recurseGroup true to perform a deep search whithin group, false otherwise.
   */
  public Vector getObjectsByName(String name,boolean recurseGroup) {
    Vector ret = new Vector();
    for(int i=0;i<objects.size();i++)
      ((JDObject)objects.get(i)).getObjectsByName(ret,name,recurseGroup);
    return ret;
  }

  /** Convert the selected objects to JDPolyline. */
  public void convertToPolyline() {

    for(int i=0;i<selObjects.size();i++) {
      JDObject o = (JDObject)selObjects.get(i);
      //if( o instanceof JDPolyConvert ) {
      if (JDUtils.isJDPolyConvertible(o)) {
	if (o instanceof JDGroup) {
		((JDGroup)o).convertToPolyline();
		repaint(o.getRepaintRect());
	} else {
		JDObject n = ((JDPolyConvert)o).convertToPolyline();
		int pos = objects.indexOf(o);
		objects.remove(pos);
		//selObjects.remove(i);
		//i--;
		objects.add(pos,n);
		//selObjects.add(n);
		selObjects.set(i,n);
		repaint(o.getRepaintRect());
		repaint(n.getRepaintRect());
	}
      }
      setNeedToSave(true,"Convert to polyline");
    }

  }

  boolean canConvertToPolyline() {
    boolean ret = selObjects.size()>0;
    for(int i=0;i<selObjects.size() && ret;i++)
	ret = JDUtils.isJDPolyConvertible((JDObject)selObjects.get(i));
    return ret;
  }

  boolean canEditGroup() {
    return (selObjects.size()==1) && (selObjects.get(0) instanceof JDGroup);
  }

  /** Raise selected object. */
  public void raiseObject() {

    if (selObjects.size() == 1) {
      JDObject n = (JDObject) selObjects.get(0);
      int pos = objects.indexOf(n);
      if (pos < objects.size() - 1) {
        objects.remove(pos);
        objects.add(pos + 1, n);
        setNeedToSave(true, "Raise");
        repaint(n.getRepaintRect());
      }
    }

  }

  /** Move down selected object. */
  public void lowerObject() {

    if (selObjects.size() == 1) {
      JDObject n = (JDObject) selObjects.get(0);
      int pos = objects.indexOf(n);
      if (pos > 0) {
        objects.remove(pos);
        objects.add(pos - 1, n);
        setNeedToSave(true, "Lower");
        repaint(n.getRepaintRect());
      }
    }

  }

  /** Return all object that have the "User interaction" flag enabled. */
  public Vector getInteractiveObjects() {
    Vector ret = new Vector();
    for(int i=0;i<objects.size();i++)
      ((JDObject)objects.get(i)).getUserValueList(ret);
    return ret;
  }

  /**
   * Sets the status label where are printed creation information.
   * @param label Label
   */
  public void setStatusLabel(JLabel label) {
    statusLabel = label;
  }

// -----------------------------------------------------
// Key listener
// -----------------------------------------------------
  public void keyPressed(KeyEvent e) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;
    int t = (alignToGrid)?GRID_SIZE:1;

    switch (e.getKeyCode()) {
      case KeyEvent.VK_UP:
        if (editedPolyline != null) {
          Rectangle old = editedPolyline.getRepaintRect();
          editedPolyline.translateSummits(selSummits, 0, -t);
          repaint(old.union(editedPolyline.getRepaintRect()));
          setNeedToSave(true, "Shape edit");
        } else {
          translateSelection(0, -t);
          setNeedToSave(true, "Translate");
        }
        // consume event (does not allow the parent ScrollPane to get the keyEvent)
        e.consume();
        break;
      case KeyEvent.VK_DOWN:
        if (editedPolyline != null) {
          Rectangle old = editedPolyline.getRepaintRect();
          editedPolyline.translateSummits(selSummits, 0, t);
          repaint(old.union(editedPolyline.getRepaintRect()));
          setNeedToSave(true, "Shape edit");
        } else {
          translateSelection(0, t);
          setNeedToSave(true, "Translate");
        }
        e.consume();
        break;
      case KeyEvent.VK_LEFT:
        if (editedPolyline != null) {
          Rectangle old = editedPolyline.getRepaintRect();
          editedPolyline.translateSummits(selSummits, -t, 0);
          repaint(old.union(editedPolyline.getRepaintRect()));
          setNeedToSave(true, "Shape edit");
        } else {
          translateSelection(-t, 0);
          setNeedToSave(true, "Translate");
        }
        e.consume();
        break;
      case KeyEvent.VK_RIGHT:
        if (editedPolyline != null) {
          Rectangle old = editedPolyline.getRepaintRect();
          editedPolyline.translateSummits(selSummits, t, 0);
          repaint(old.union(editedPolyline.getRepaintRect()));
          setNeedToSave(true, "Shape edit");
        } else {
          translateSelection(t, 0);
          setNeedToSave(true, "Translate");
        }
        e.consume();
        break;
    }

  }

  public void keyReleased(KeyEvent e) {

  }

  public void keyTyped(KeyEvent e) {

  }

// -----------------------------------------------------
// Mouse listener
// -----------------------------------------------------
  public void mouseDragged(MouseEvent e) {
    if(mode==MODE_PLAY) {
      relayPlayerMouseMoveEvent(e);
      mouseDraggedPlayer(e);
    } else {
      mouseDraggedEditor(e);
    }
  }

  private void mouseDraggedPlayer(MouseEvent e) {

    int ex = zconvert(e.getX(), transx);
    int ey = zconvert(e.getY(), transy);

    if (selObjects.size() > 0) {
      // repaint old rect
      repaint(buildRepaintRect(selObjects));

      // Forward the event to dragged objects
      // srubio@cells.es: Modified to disable event relaying to those objects with ignoreMouse extension
      for (int i = 0; i < selObjects.size(); i++)
	if (!((JDObject) selObjects.get(i)).hasExtendedParam("ignoreMouse"))
        	((JDObject) selObjects.get(i)).processValue(JDObject.MDRAGGED,ex,ey);

      repaint(buildRepaintRect(selObjects));
    }

  }

  private void mouseDraggedEditor(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);

    //---------------------------------------------------
    if (isDraggingSelection) {

      Rectangle old = buildSelectionRect();
      selX2 = ex;
      selY2 = ey;
      repaint(old.union(buildSelectionRect()));
      return;

    }
    if(mode==MODE_LIB) return;

    //---------------------------------------------------
    if (isDraggingSummits) {

      if( alignToGrid ) {
        ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      }

      Rectangle old = editedPolyline.getRepaintRect();
      editedPolyline.translateSummits(selSummits, ex - lastX, ey - lastY);
      repaint(old.union(editedPolyline.getRepaintRect()));
      hasMoved=true;
      lastX = ex;
      lastY = ey;

    }

    //---------------------------------------------------
    if (isDraggingSummit) {

      if( alignToGrid ) {
        ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      }

      JDObject p = (JDObject) selObjects.get(curObject);
      Rectangle old = p.getRepaintRect();

      switch (p.getSummitMotion(selSummit)) {
        case JDObject.BOTH_SM:
          p.moveSummit(selSummit, ex, ey);
          break;
        case JDObject.HORIZONTAL_SM:
          p.moveSummit(selSummit, ex, p.getSummit(selSummit).y);
          break;
        case JDObject.VERTICAL_SM:
          p.moveSummit(selSummit, p.getSummit(selSummit).x, ey);
          break;
      }

      addStatus("[" + Integer.toString(selSummit) + " @"
                     + Integer.toString(ex) + "," +
                       Integer.toString(ey) + " "+ " ("
                     + Integer.toString(p.getBoundRect().width-1) + "," +
                       Integer.toString(p.getBoundRect().height-1) + ")]");

      hasMoved=true;
      repaint(old.union(p.getRepaintRect()));

    }

    //---------------------------------------------------
    if (isDraggingObject) {

      if( alignToGrid ) {
        ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      }

      translateSelection(ex - lastX, ey - lastY);
      lastX = ex;
      lastY = ey;

    }


  }

  public void mouseMoved(MouseEvent e) {
    if(mode==MODE_LIB) return;
    if(mode==MODE_PLAY) {
      relayPlayerMouseMoveEvent(e);
      return;
    }

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);

    if ((creationMode == CREATE_POLYLINE || creationMode == CREATE_SPLINE) && tmpPoints.size() > 0) {
      if( alignToGrid ) {
        ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      }
      int s = tmpPoints.size();
      Rectangle old = buildRectFromLine((Point) tmpPoints.get(s - 2), (Point) tmpPoints.get(s - 1));
      ((Point) tmpPoints.get(s - 1)).x = ex;
      ((Point) tmpPoints.get(s - 1)).y = ey;
      repaint(old.union(buildRectFromLine((Point) tmpPoints.get(s - 2), (Point) tmpPoints.get(s - 1))));
      return;
    }

    if (!isDraggingSummit && !isDraggingObject && !isDraggingSelection && !isDraggingSummits)
      findSummit(ex, ey);
  }

  public void mouseEntered(MouseEvent e) {
  }

  public void mouseExited(MouseEvent e) {
    if(mode==MODE_PLAY) {
      if(motionObject!=null) {
        motionObject.fireMouseEvent(MouseEvent.MOUSE_EXITED,e);
        motionObject=null;
      }
    }
  }

  public void mouseClicked(MouseEvent e) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);

    if (e.getClickCount() == 2 && e.getButton() == MouseEvent.BUTTON1) {

      boolean found = false;
      int i = selObjects.size() - 1;
      while (!found && i >= 0) {
        found = ((JDObject) selObjects.get(i)).isInsideObject(ex, ey);
        if (!found) i--;
      }

      if (found) showPropertyWindow();

    }

  }

  public void mouseReleased(MouseEvent e) {
    if(mode==MODE_PLAY) {
      relayPlayerMouseReleasedEvent(e);
      mouseReleasedPlayer(e);
    } else {
      mouseReleasedEditor(e);
    }

  }

  private void mouseReleasedPlayer(MouseEvent e) {

    int ex = zconvert(e.getX(), transx);
    int ey = zconvert(e.getY(), transy);

    if (selObjects.size() > 0) {
      // repaint old rect
      repaint(buildRepaintRect(selObjects));

      // Forward the event to clicked objects
     // srubio@cells.es: Modified to disable event relaying to those objects with ignoreMouse extension
      for (int i = 0; i < selObjects.size(); i++)
	if (!((JDObject) selObjects.get(i)).hasExtendedParam("ignoreMouse"))
        	((JDObject) selObjects.get(i)).processValue(JDObject.MRELEASED,ex,ey);

      repaint(buildRepaintRect(selObjects));
      selObjects.clear();
    }

  }

  private void mouseReleasedEditor(MouseEvent e) {

    if((isDraggingSummits || isDraggingSummit || isDraggingObject) && hasMoved) {
      if(isDraggingSummit) {
        if( lastCreatedObject==null ) {
          setNeedToSave(true,"Shape edit");
          setStatus("");
        } else {
          // Creation done
          setNeedToSave(true,"Object creation");
          fireCreationDone();
          lastCreatedObject.centerOrigin();
          lastCreatedObject=null;
        }
      }
      if(isDraggingObject) {
        setNeedToSave(true,"Translate");
        repaint(buildRepaintRect(selObjects));
      }
      if(isDraggingSummits) {
        setNeedToSave(true,"Shape edit");
        repaint(buildRepaintRect(selObjects));
      }
    }

    isDraggingSummit  = false;
    isDraggingSummits = false;
    isDraggingObject  = false;
    hasMoved=false;

    if (isDraggingSelection) {
      isDraggingSelection = false;
      Rectangle sr = buildSelectionRect();
      Rectangle rep = null;
      selX1 = selX2 = selY1 = selY2 = 0;

      if (editedPolyline != null) {

        // Summit selection for editedPolyline
        int[] nSummit = editedPolyline.getSummitsInsideRectangle(sr);
        for(int i=0;i<nSummit.length;i++)
          selectSummit(nSummit[i]);

      } else {

        // Look for all object int the selection rectangle
        for (int i = 0; i < objects.size(); i++) {
          JDObject p = (JDObject) objects.get(i);
          if (p.isVisible() && sr.contains(p.getBoundRect())) {
            if (!isSelected(p)) {
              selObjects.add(p);
            } else {
              if (e.isControlDown()) {
                // Invert selection
                selObjects.remove(p);
              }
            }

            if (rep == null)
              rep = p.getRepaintRect();
            else
              rep = rep.union(p.getRepaintRect());
          }
        }
        fireSelectionChange();

      }

      if( rep!=null ) repaint(sr.union(rep));
      else            repaint(sr);
    }

    setCursor(dCursor);
  }

  public void mousePressedEditorB1(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);

    // -----------------------------------------------------------------------
    if (editedPolyline != null) {

      findSummit(ex, ey);
      if (selSummit == -1) {

        // Starting rectangle selection
        if (!e.isControlDown()) {
          // Empty summit selection
          selSummits = new int[0];
          repaint(editedPolyline.getRepaintRect());
        }
        selX1 = ex;
        selY1 = ey;
        selX2 = ex;
        selY2 = ey;
        isDraggingSelection = true;

      } else {

        if (alignToGrid) {
          ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
          ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        }
        lastX = ex;
        lastY = ey;

        if (isSelectedSummit(selSummit)) {
          isDraggingSummits = true;
        } else {
          if(e.isControlDown()) {
            // Add the summit to selection
            selectSummit(selSummit);
          } else {
            // Select this summit
            selSummits = new int[1];
            selSummits[0] = selSummit;
            isDraggingSummits = true;
          }
          repaint(editedPolyline.getRepaintRect());
        }

      }

      return;
    }

    // -----------------------------------------------------------------------
    if( createObject(ex,ey) )
      return;

    // -----------------------------------------------------------------------
    // Starts by looking if a summit has been hit
    if (mode != MODE_LIB) {
      if (findSummit(ex, ey)) {
        isDraggingSummit = true;
        return;
      }
    }

    JDObject p = findObject(ex,ey);

    if (p!=null) {
      //Select it if not
      if (!isSelected(p)) {
        if (!e.isControlDown()) unselectAll(false);
        selObjects.add(p);
        repaint(p.getRepaintRect());
        fireSelectionChange();
      } else {
        if( e.isControlDown() ) {
          // Unselect it
          selObjects.remove(p);
          repaint(p.getRepaintRect());
          fireSelectionChange();
          return;
        }
      }
      if (mode != MODE_LIB) {
        curObject = selObjects.indexOf(p);
        isDraggingObject = true;
        if (alignToGrid) {
          ex = ((ex + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
          ey = ((ey + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
        }
        lastX = ex;
        lastY = ey;
        setCursor(bCursor);
      }
    } else {
      // Starting rectangle selection
      if (!e.isControlDown()) {
        unselectAll();
      }
      selX1 = ex;
      selY1 = ey;
      selX2 = ex;
      selY2 = ey;
      isDraggingSelection = true;
    }

  }

  public void mousePressedEditorB3(MouseEvent e) {
    //if (mode == MODE_LIB) return;
    if (creationMode == 0) showMenu(e);

    int i;
    
    // --------------------------------------- Creation mode
    
    if (creationMode == CREATE_POLYLINE) {

      if (tmpPoints.size() != 0) {
        // Create the Polyline
        int s = tmpPoints.size();
        Point[] pts = new Point[s];
        for (i = 0; i < s; i++) pts[i] = (Point) tmpPoints.get(i);
        JDObject p = new JDPolyline("Polyline", pts);
        selObjects.add(p);
        objects.add(p);
        repaint(p.getRepaintRect());
        fireCreationDone();
        fireSelectionChange();
        setNeedToSave(true,"Object creation");
      } else {
        // Canceling
        fireCreationDone();
      }
      tmpPoints.clear();
      creationMode = 0;
      return;

    } else if (creationMode == CREATE_SPLINE) {

      // Create the Spline
      int s = tmpPoints.size();
      s = ((s - 1) / 3) * 3 + 1;
      if (s >= 4) {
        Point[] pts = new Point[s];
        for (i = 0; i < s; i++) pts[i] = (Point) tmpPoints.get(i);
        JDObject p = new JDSpline("Spline", pts);
        selObjects.add(p);
        objects.add(p);
        repaint(p.getRepaintRect());
        fireCreationDone();
        fireSelectionChange();
        setNeedToSave(true,"Object creation");
      } else {
        // Not enough point canceling
        fireCreationDone();
        repaint();
      }

      tmpPoints.clear();
      creationMode = 0;
      return;

    } else if (creationMode != 0) {

      // Canceling
      tmpPoints.clear();
      creationMode = 0;
      fireCreationDone();
      repaint();
      return;

    }

    showMenu(e);
  }

  public void mousePressedPlayerB1(MouseEvent e) {

    int ex = zconvert(e.getX(), transx);
    int ey = zconvert(e.getY(), transy);
    int i;

    // Build list of object to be modified
    selObjects.clear();
    selectObjects(ex, ey, selObjects);
    if (selObjects.size() > 0) {

      // repaint old rect
      repaint(buildRepaintRect(selObjects));

      // Execute value program
      // srubio@cells.es: Modified to disable event relaying to those objects with ignoreMouse extension
      for (i = 0; i < selObjects.size(); i++)
	if (!((JDObject) selObjects.get(i)).hasExtendedParam("ignoreMouse"))
        	((JDObject) selObjects.get(i)).processValue(JDObject.MPRESSED,ex,ey);

      repaint(buildRepaintRect(selObjects));

    }

  }

  public void mousePressedPlayerB3(MouseEvent e) {}

  public void mousePressed(MouseEvent e) {

    grabFocus();
    if( mode==MODE_PLAY ) {
      relayPlayerMousePressedEvent(e);
      if (e.getButton() == MouseEvent.BUTTON1) mousePressedPlayerB1(e);
      if (e.getButton() == MouseEvent.BUTTON3) mousePressedPlayerB3(e);
    } else {
      if (e.getButton() == MouseEvent.BUTTON1) mousePressedEditorB1(e);
      if (e.getButton() == MouseEvent.BUTTON3) mousePressedEditorB3(e);
    }

  }

  private void relayPlayerMouseReleasedEvent(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);

    if(pressedObject!=null) {
      if(pressedObject.isInsideObject(ex,ey)) {
        pressedObject.fireMouseEvent(MouseEvent.MOUSE_RELEASED,e);
        pressedObject.fireMouseEvent(MouseEvent.MOUSE_CLICKED,e);
      }
      pressedObject=null;
    }

  }

  private void relayPlayerMousePressedEvent(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);
    pressedObject = findMouseListenerObject(ex,ey);
    if(pressedObject!=null)
      pressedObject.fireMouseEvent(MouseEvent.MOUSE_PRESSED,e);

  }

  private void relayPlayerMouseMoveEvent(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);
    JDObject p = findMouseListenerObject(ex,ey);
    if(motionObject==null) {
      if( p==null ) {
        // Nothing
      } else {
        // Enter object
        motionObject = p;
        motionObject.fireMouseEvent(MouseEvent.MOUSE_ENTERED,e);
      }
    } else {
      if( p==null ) {
        // Leave object
        motionObject.fireMouseEvent(MouseEvent.MOUSE_EXITED,e);
        motionObject=null;
      } else {
        if(p==motionObject) {
          // Still the same object
        } else {
          // Move from motionObject to P
          motionObject.fireMouseEvent(MouseEvent.MOUSE_EXITED,e);
          motionObject = p;
          motionObject.fireMouseEvent(MouseEvent.MOUSE_ENTERED,e);
        }
      }
    }

  }

// -----------------------------------------------------
// Component listener
// -----------------------------------------------------
  public void componentResized(ComponentEvent e) {

    if(autoZoom && mode==MODE_PLAY) {

      // Compute autoZoomFactor
      Dimension d = getSize();
      double ratioX = (double)d.width  / (double)sizeX;
      double ratioY = (double)d.height / (double)sizeY;
      if(ratioX>ratioY) {
        autoZoomFactor = ratioY;
      } else {
        autoZoomFactor = ratioX;
      }

      // Saturate
      if( autoZoomFactor<0.1 ) autoZoomFactor = 0.1;
      //System.out.println("zoomFactor=" + autoZoomFactor);

      // Do proportionnal resizing for JDSwingObject
      Vector v = getObjectsOfClass(JDSwingObject.class);
      int sz = v.size();
      for(int i=0;i<sz;i++) {
        // Get original coordinates
        JDSwingObject jdw = ((JDSwingObject)v.get(i));
        Rectangle r = new Rectangle(jdw.getBoundRect());
        // Zoom
        r.x      = (int)Math.rint( (double)r.x * autoZoomFactor );
        r.y      = (int)Math.rint( (double)r.y * autoZoomFactor );
        r.width  = (int)Math.rint( (double)r.width * autoZoomFactor );
        r.height = (int)Math.rint( (double)r.height * autoZoomFactor );
        jdw.getComponent().setBounds(r);
        jdw.getComponent().validate();
      }
      repaint();

    }

  }
  public void componentMoved(ComponentEvent e) {}
  public void componentShown(ComponentEvent e) {}
  public void componentHidden(ComponentEvent e) {}

// -----------------------------------------------------
// Action listener
// -----------------------------------------------------
  public void actionPerformed(ActionEvent e) {
    if(mode==MODE_PLAY) return;
    if(mode==MODE_LIB) return;

    Object src = e.getSource();
    Rectangle rep = null;

    if (src == delSummitMenuItem) {
      rep = editedPolyline.getRepaintRect();
      editedPolyline.deleteSummit();
      selSummits = new int[0];
      setNeedToSave(true,"Delete polyline point");
      repaint(rep.union(editedPolyline.getRepaintRect()));
    } else if (src == brkShapeMenuItem) {
      rep = editedPolyline.getRepaintRect();
      setNeedToSave(true,"Add polyline point");
      editedPolyline.breakShape();
      selSummits = new int[0];
      repaint(rep.union(editedPolyline.getRepaintRect()));
    } else if (src == set0ShapeMenuItem) {
      rep = editedPolyline.getRepaintRect();
      setNeedToSave(true,"Set starting point");
      editedPolyline.setStartingPoint(selSummit);
      selSummits = new int[0];
      repaint(rep.union(editedPolyline.getRepaintRect()));
    } else if (src == reorderShapeMenuItem) {
      rep = editedPolyline.getRepaintRect();
      setNeedToSave(true,"Reorder polyline");
      editedPolyline.invertSummitOrder();
      selSummits = new int[0];
      repaint(rep.union(editedPolyline.getRepaintRect()));
    } else if (src == copyMenuItem) {
      copySelection();
    } else if (src == pasteMenuItem) {
      pasteClipboard(lastX, lastY);
    } else if (src == cutMenuItem) {
      cutSelection();
    } else if (src == deleteMenuItem) {
      deleteSelection();
    } else if (src == raiseMenuItem) {
      raiseObject();
    } else if (src == lowerMenuItem) {
      lowerObject();
    } else if (src == frontMenuItem) {
      frontSelection();
    } else if (src == backMenuItem) {
      backSelection();
    } else if (src == groupMenuItem) {
      groupSelection();
    } else if (src == ungroupMenuItem) {
      ungroupSelection();
    } else if (src == zoomInMenuItem) {
      zoomIn();
    } else if (src == zoomOutMenuItem) {
      zoomOut();
    } else if (src == editShapeMenuItem) {
      if(selObjects.size()>0) {
        selSummits = new int[0];
        editedPolyline = (JDPolyline)selObjects.get(0);
        repaint(editedPolyline.getRepaintRect());
      }
    } else if (src == connectShapeMenuItem) {
      pickPolyline();
    } else if (src == cancelShapeMenuItem) {
      rep = editedPolyline.getRepaintRect();
      editedPolyline = null;
      repaint(rep);

//To actionPerformed, from JDrawEditorFrame
    } else if (src==viewsTransformMenuItem) {
      showTransformWindow();
    } else if (src==viewsOptionMenuItem) {
      showPropertyWindow();
    }  else if (src==viewsBrowseMenuItem) {
      showBrowserWindow();
    } else if (src == viewsGroupEditMenuItem) {
      showGroupEditorWindow();
    }

  }

  /**
   * Paints all JDObjects of the components.
   * @param g Graphics
   */
  public void paintObjects(Graphics g) {
    for (int i = 0; i < objects.size(); i++)
      ((JDObject) objects.get(i)).paint(this,g);
  }

  /**
   * Paints selection area and control points.
   * @param g Graphics
   */
  public void paintSelection(Graphics g) {

    if (mode != MODE_PLAY) {

      int i;

      // Paint selection summit
      if( !isDraggingObject || !hasMoved )
        for (i = 0; i < selObjects.size(); i++)
          ((JDObject) selObjects.get(i)).paintSummit(g, zdconvert(6.0, 0.0));

      // Paint edition polyline
      if(editedPolyline!=null)
        editedPolyline.paintSelectedSummit(g,selSummits,zdconvert(6.0, 0.0));

      // Paint selection rectangle
      if (selX1 != selX2 && selY1 != selY2) {
        g.setColor(Color.darkGray);
        g.drawLine(selX1, selY1, selX2, selY1);
        g.drawLine(selX2, selY1, selX2, selY2);
        g.drawLine(selX2, selY2, selX1, selY2);
        g.drawLine(selX1, selY2, selX1, selY1);
      }

      if (mode != MODE_LIB) {
        // Paint creation polyline
        for (i = 1; i < tmpPoints.size(); i++) {
          g.setColor(Color.darkGray);
          Point p1 = (Point) tmpPoints.get(i - 1);
          Point p2 = (Point) tmpPoints.get(i);
          g.drawLine(p1.x, p1.y, p2.x, p2.y);
        }
      }

    }

  }

  private void paintGrid(Graphics gr) {
    if (mode == MODE_PLAY) return;
    if (mode == MODE_LIB) return;

    if (gridVisible) {
      Dimension d = getSize();
      double gs = zbdconvert((double)GRID_SIZE,0.0);
      int r,g,b,x,y;

      if(getBackground().getRed()<128)
        r = getBackground().getRed() + 64;
      else
        r = getBackground().getRed() - 64;

      if(getBackground().getGreen()<128)
        g = getBackground().getGreen() + 64;
      else
        g = getBackground().getGreen() - 64;

      if(getBackground().getBlue()<128)
        b = getBackground().getBlue() + 64;
      else
        b = getBackground().getBlue() - 64;

      Color gColor = new Color( r , g , b );
      gr.setColor(gColor);

      for (double i = 0.0; i<=d.width; i += gs)
        for (double j = 0.0; j<=d.height; j += gs) {
          x = (int)(i+0.5);
          y = (int)(j+0.5);
          gr.drawLine(x, y, x, y);
        }

    }

  }

// -----------------------------------------------------
// Painting stuff
// -----------------------------------------------------
  public void paint(Graphics g) {

    Dimension d = getSize();
    Graphics2D g2 = (Graphics2D) g;

    // Paint Background
    if (isOpaque()) {
      g.setColor(getBackground());
      g.fillRect(0, 0, d.width, d.height);
    }

    // Paint the grid
    paintGrid(g);

    // build the transformation according to the zoom and translation
    AffineTransform oldT = g2.getTransform();
    AffineTransform nT = new AffineTransform(oldT);
    double r = getZoomScaleRatio();
    nT.scale(r,r);
    nT.translate((double)transx,(double)transy);
    g2.setTransform(nT);

    // Paint
    paintObjects(g);
    paintSelection(g);

    // Rectore transform
    g2.setTransform(oldT);

    // Paint swing stuff
    // Use this ugly hack instead of paintComponents() ,
    // but this is the only way to avoid repaint problems.
    boolean oldOpaque = isOpaque();
    setOpaque(false);
    super.paint(g);
    setOpaque(oldOpaque);

  }

  /**
   * Repaint the specified rectangle.
   * @param r Rectangle to be repainted ('not zoomed' coordinates).
   */
  public void repaint(Rectangle r) {
    if (r != null) {
      int m = (int) (zdconvert(3.0, 0.0) + 0.5) + 1; // summitWidth
      Rectangle zr = new Rectangle(zbconvert(r.x, transx) - m, zbconvert(r.y, transy) - m,
              zbconvert(r.width, 0) + 2 * m, zbconvert(r.height, 0) + 2 * m);
      super.repaint(zr);
    }
  }

// -----------------------------------------------------
// Private stuff
// -----------------------------------------------------
  void setNeedToSave(boolean b,String s) {

    //System.out.println("Need to save:(" + s + ")" + b);

    needToSave = b;

    if(needToSave && (mode==MODE_EDIT)) {
      // Clear upper undo buffer
      for(int i=undo.size()-1;i>=undoPos;i--) {
        undo.removeElementAt(i);
        //System.out.println("Clearing backup #" + i);
      }
      undo.add(new UndoBuffer(objects,s));
      if( undo.size()>=undoLength ) {
        undo.removeElementAt(0);
        //System.out.println("Full!! Clearing backup #0");
      }
      // Reset redo
      undoPos=undo.size();
      //System.out.println("UndoLength=" + undo.size());
    }

    fireValueChanged();
  }

  private double getZoomScaleRatio() {

    if( autoZoom ) {

      return autoZoomFactor;

    } else {

      double r = 1.0;
      if (zoomFactor != 0) {
        if (zoomFactor >= 0)
          r = (double) (zoomFactor + 1);
        else
          r = 1.0 / (double) (-zoomFactor + 1);
      }
      return r;

    }

  }

  private int zconvert(int x,int t) {

    if (autoZoom) {

      return (int) ((double) (x) / autoZoomFactor) - t;

    } else {

      if (zoomFactor == 0) {
        return x - t;
      } else if (zoomFactor > 0) {
        return (int) ((double) (x) / (double) (zoomFactor + 1)) - t;
      } else {
        return (x) * (-zoomFactor + 1) - t;
      }

    }

  }

  private int zbconvert(int x,int t) {

    if (autoZoom) {

      return (int)((x + t) * autoZoomFactor);

    } else {

      if (zoomFactor == 0) {
        return x + t;
      } else if (zoomFactor > 0) {
        return (x + t) * (zoomFactor + 1);
      } else {
        return (int) ((double) (x + t) / (double) (-zoomFactor + 1));
      }

    }

  }

  private double zdconvert(double x,double tx) {

    if (autoZoom) {

      return (x - tx)/autoZoomFactor;

    } else {

      if (zoomFactor == 0) {
        return x - tx;
      } else if (zoomFactor > 0) {
        return (x - tx) / (double) (zoomFactor + 1);
      } else {
        return (x - tx) * (-zoomFactor + 1);
      }

    }

  }

  private double zbdconvert(double x,double tx) {

    if (autoZoom) {

      return (x + tx) * autoZoomFactor;

    } else {

      if (zoomFactor == 0) {
        return x + tx;
      } else if (zoomFactor > 0) {
        return (x + tx) * (double) (zoomFactor + 1);
      } else {
        return (x + tx) / (double) (-zoomFactor + 1);
      }

    }

  }

  public void addToMenu(JMenuItem newItem) {
	  if (objMenu == null) {
		  objMenu = new JPopupMenu();
		  infoMenuItem = new JMenuItem();
		  infoMenuItem.setEnabled(false);
		  objMenu.add(infoMenuItem);
		  sep1 = new JSeparator();
		  objMenu.add(sep1);
	  }		  
	  if (newItem != null)
		  objMenu.add(newItem);
  }
  
  private void showMenu(MouseEvent e) {

    int ex = zconvert(e.getX(),transx);
    int ey = zconvert(e.getY(),transy);
    findSummit(ex, ey);

    if (editedPolyline!=null && mode != MODE_LIB) {

      // Polyline edition mode
      infoPolyMenuItem.setText("Polyline edition");

      delSummitMenuItem.setEnabled(false);
      brkShapeMenuItem.setEnabled(false);
      set0ShapeMenuItem.setEnabled(selSummit != -1);

      if (selSummit != -1) {
        delSummitMenuItem.setEnabled(editedPolyline.canDeleteSummit(selSummit));
        String s = infoPolyMenuItem.getText();
        s = s + " [Summit: " + selSummit+" ]";
        infoPolyMenuItem.setText(s);
      } else {
        brkShapeMenuItem.setEnabled(editedPolyline.canBreakShape(ex, ey));
      }

      // Popup the menu
      lastX = ex;
      lastY = ey;
      polyMenu.show(this, e.getX(), e.getY());

    } else {

      // Object contextual menu

      JDObject p = findObject(ex, ey);

      if (p != null) {
        //Select it if not
        if (!isSelected(p)) {
          unselectAll(false);
          selObjects.add(p);
          repaint(p.getRepaintRect());
          fireSelectionChange();
        }
      }

      int sz = selObjects.size();
      p = null;
      if (sz > 0) p = (JDObject) selObjects.get(0);
      
      if (mode == MODE_LIB && objMenu == null) {
	      addToMenu(null); //Creates a void Library Context Menu
      }

      infoMenuItem.setVisible(sz >= 1);
      if (sz == 1) {
        String sId = (selSummit!=-1) ? " Summit:" + Integer.toString(selSummit) : "";
        infoMenuItem.setText(p.getName() + " [" + p.toString() + "]" + sId);
      } else
        infoMenuItem.setText("Multiple selection");
	
      if (mode == MODE_LIB) {
	      Component[] menuComps = objMenu.getComponents();
	      for (int k=0;k<menuComps.length;k++) {
		      if (k<menuComps.length-1) {
			      menuComps[k].setEnabled(k>1 && sz>0);
			      menuComps[k].setVisible(sz>0);
		      } else { //Exit Command
		      	      menuComps[k].setEnabled(k>1);
			      menuComps[k].setVisible(true);
		      }
	      }
      } else {
	      cutMenuItem.setEnabled((sz > 0));
	      copyMenuItem.setEnabled((sz > 0));
	      pasteMenuItem.setEnabled((clipboard.size() > 0));
	      deleteMenuItem.setEnabled((sz > 0));
	
	      groupMenuItem.setVisible((sz > 0));
	      if (sz == 1) {
		ungroupMenuItem.setVisible(p instanceof JDGroup);
	      } else {
		ungroupMenuItem.setVisible(false);
	      }
	
	      raiseMenuItem.setVisible((sz == 1));
	      lowerMenuItem.setVisible((sz == 1));
	      frontMenuItem.setVisible((sz >= 1));
	      backMenuItem.setVisible((sz >= 1));
	
	      if (p != null) {
		int pos = objects.indexOf(p);
		raiseMenuItem.setEnabled(pos < objects.size() - 1);
		lowerMenuItem.setEnabled(pos > 0);
	      }
	
	      boolean isPoly = (p instanceof JDPolyline) && (sz==1);
	      editShapeMenuItem.setVisible(isPoly);
	      connectShapeMenuItem.setVisible(isPoly);

    		viewsGroupEditMenuItem.setEnabled(canEditGroup());
    		viewsBrowseMenuItem.setEnabled(sz>1);
    		viewsTransformMenuItem.setEnabled(sz>0);
    		viewsOptionMenuItem.setEnabled(sz>0);
    		viewsGroupEditMenuItem.setVisible(canEditGroup());
    		viewsBrowseMenuItem.setVisible(sz>1);
    		viewsTransformMenuItem.setVisible(sz>0);
    		viewsOptionMenuItem.setVisible(sz>0);

	      
	      //Separator
	      sep1.setVisible(infoMenuItem.isVisible());
	      sep2.setVisible(editShapeMenuItem.isVisible());
	      sep3.setVisible(groupMenuItem.isVisible() || ungroupMenuItem.isVisible());
	      sep5.setVisible(raiseMenuItem.isVisible() || frontMenuItem.isVisible());	      
      }

      // Popup the menu
      lastX = ex;
      lastY = ey;
      objMenu.show(this, e.getX(), e.getY());
    }

  }

  private void initCreate(int mode) {
    creationMode = mode;
    creationParam = null;
    sliderRef = null;
    connectPolyline = null;
    if(editedPolyline!=null) {
      Rectangle r = editedPolyline.getRepaintRect();
      editedPolyline = null;
      repaint(r);
    }
    updateCreationStatus();
  }

  void setStatus(String s) {

    if(s==null)
      currentStatus=" ";
    else if (s.length()==0)
      currentStatus=" ";
    else
      currentStatus=s;

    if(statusLabel!=null) {
      statusLabel.setText(currentStatus);
    }

  }

  private void addStatus(String s) {
    if(statusLabel!=null) {
      statusLabel.setText(currentStatus + s);
    }
  }

  private Cursor getCursorForMotion(JDObject p,int summit) {

    switch (p.getSummitMotion(summit)) {
      case JDObject.BOTH_SM:
        if (p instanceof JDRectangular) {
          double x = p.getSummit(summit).getX();
          double y = p.getSummit(summit).getY();
          double xc = p.getBoundRect().x + (double) p.getBoundRect().width / 2.0;
          double yc = p.getBoundRect().y + (double) p.getBoundRect().height / 2.0;
          if (x < xc) {
            if (y < yc)
              return nwCursor;
            else
              return swCursor;
          } else {
            if (y < yc)
              return neCursor;
            else
              return seCursor;
          }
        } else {
          return bCursor;
        }
      case JDObject.NONE_SM:
        return dCursor;
      case JDObject.HORIZONTAL_SM:
        return hCursor;
      case JDObject.VERTICAL_SM:
        return vCursor;
    }

    return dCursor;
  }

  private Rectangle buildSelectionRect() {
    Point p1 = new Point(selX1, selY1);
    Point p2 = new Point(selX2, selY2);
    return buildRectFromLine(p1, p2);
  }

  private Rectangle buildRectFromLine(Point p1, Point p2) {

    Rectangle r = new Rectangle();

    int m = zconvert(1,0);
    if( m<1 ) m = 1;

    if (p1.x < p2.x) {
      if (p1.y < p2.y) {
        r.setRect(p1.x - m, p1.y - m, p2.x - p1.x + 2*m, p2.y - p1.y + 2*m);
      } else {
        r.setRect(p1.x - m, p2.y - m, p2.x - p1.x + 2*m, p1.y - p2.y + 2*m);
      }
    } else {
      if (p1.y < p2.y) {
        r.setRect(p2.x - m, p1.y - m, p1.x - p2.x + 2*m, p2.y - p1.y + 2*m);
      } else {
        r.setRect(p2.x - m, p2.y - m, p1.x - p2.x + 2*m, p1.y - p2.y + 2*m);
      }
    }

    return r;
  }

  private boolean findSummit(int x, int y) {

    boolean found = false;
    int i;
    curObject = -1;
    selSummit = -1;

    if (selObjects.size() != 0) {

      i = 0;
      found = false;
      JDObject p = null;
      while (i < selObjects.size() && !found) {
        p = (JDObject) selObjects.get(i);
        selSummit = p.getSummit(x,y,zdconvert(6.0,0.0));
        found = (selSummit != -1);
        if (!found) i++;
      }

      if (found) {
        curObject = i;
        setCursor(getCursorForMotion(p,selSummit));
      } else {
        setCursor(dCursor);
      }

    }

    return found;

  }

  private JDObject findObject(int x, int y) {

    boolean found = false;
    int i;
    // start looking at front
    i = objects.size() - 1;
    while (!found && i >= 0) {
      found = ((JDObject) objects.get(i)).isInsideObject(x, y);
      if (!found) i--;
    }

    if (found) {
      return (JDObject) objects.get(i);
    } else {
      return null;
    }

  }

  private JDObject findMouseListenerObject(int x, int y) {

    boolean found = false;
    int i;
    JDObject o;
    // start looking at front
    i = objects.size() - 1;
    while (!found && i >= 0) {
      o = ((JDObject) objects.get(i));
      if(o.hasMouseListener())
        found = ((JDObject) objects.get(i)).isInsideObject(x, y);
      if (!found) i--;
    }

    if (found) {
      return (JDObject) objects.get(i);
    } else {
      return null;
    }

  }

  private void selectObjects(int x, int y,Vector found) {
    // Find objects under x,y coordinates
    for(int i=0;i<objects.size();i++)
      getObjectAt(i).findObjectsAt(x,y,found);
  }

  private void createObject(JDObject p, int summit) {
    unselectAll(false);
    lastCreatedObject=p;
    objects.add(p);
    creationMode = 0;
    selObjects.add(p);
    isDraggingSummit = (summit >= 0);
    curObject = 0;
    selSummit = summit;
    editedPolyline = null;
    repaint(p.getRepaintRect());
    fireSelectionChange();

    if (!isDraggingSummit) {
      // Creation done
      setNeedToSave(true, "Object creation");
      fireCreationDone();
      lastCreatedObject = null;
    }

  }

  private void updateCreationStatus() {

    switch (creationMode) {
      case CREATE_RECTANGLE:
        setStatus("Left click and drag to create a rectangle");
        break;
      case CREATE_RRECTANGLE:
        setStatus("Left click and drag to create a rounded rectangle");
        break;
      case CREATE_LINE:
        setStatus("Left click and drag to create a line");
        break;
      case CREATE_ELLIPSE:
        setStatus("Left click and drag to create an ellipse");
        break;
      case CREATE_POLYLINE:
        setStatus("Left click to create a new point and right click to create the last point");
        break;
      case CREATE_LABEL:
        setStatus("Left click to create the label");
        break;
      case CREATE_SPLINE:
        setStatus("Left click to create a new point and right click to create the last point");
        break;
      case CREATE_IMAGE:
        setStatus("Left click to create an image");
        break;
      case CREATE_AXIS:
        setStatus("Left click to create an axis");
        break;
      case CREATE_BAR:
        setStatus("Left click and drag to create a bar");
        break;
      case CREATE_SLIDER:
        setStatus("Left click and drag to create a slider");
        break;
      case CREATE_SLIDER_CURSOR:
        setStatus("Left click on a object to pick up new slider cursor");
        break;
      case CREATE_CONNECT_POLY:
        setStatus("Left click on the polyline to be connected.");
        break;
      case CREATE_SWINGOBJECT:
        setStatus("Left click to create a JDSwingObject : " +
                  JDUtils.buildShortClassName(creationParam));
        break;
      case CREATE_CLIPBOARD:
        setStatus("Left click to paste");
        break;
    }

  }

  private void rebuildBackup(int pos) {

    // Free All
    clearObjects();
    editedPolyline = null;

    //Rebuild form backup
    objects = ((UndoBuffer)undo.get(pos)).rebuild();
    //System.out.println("Rebuild backup #" + pos);

    //Repaint
    repaint();
    fireValueChanged();
    fireSelectionChange();
  }

  void fireSelectionChange() {
    JDUtils.updatePropertyDialog(selObjects);
    for(int i=0;i<listeners.size();i++)
      ((JDrawEditorListener)listeners.get(i)).selectionChanged();
  }

  private void fireCreationDone() {
    setStatus("");
    for(int i=0;i<listeners.size();i++)
      ((JDrawEditorListener)listeners.get(i)).creationDone();
  }

  void fireClipboardChange() {
    for(int i=0;i<listeners.size();i++)
      ((JDrawEditorListener)listeners.get(i)).clipboardChanged();
  }

  void fireValueChanged() {
    for(int i=0;i<listeners.size();i++)
      ((JDrawEditorListener)listeners.get(i)).valueChanged();
  }

  protected void fireSizeChanged() {
    for(int i=0;i<listeners.size();i++)
      ((JDrawEditorListener)listeners.get(i)).sizeChanged();
  }

  private void applyGlobalOption(JDFileLoader f) {
    setBackground(f.globalBackground);
  }

  private void createContextualMenu() {
    objMenu = new JPopupMenu();

    infoMenuItem = new JMenuItem();
    infoMenuItem.setEnabled(false);

    cutMenuItem = new JMenuItem("Cut");
    cutMenuItem.addActionListener(this);

    copyMenuItem = new JMenuItem("Copy");
    copyMenuItem.addActionListener(this);

    pasteMenuItem = new JMenuItem("Paste");
    pasteMenuItem.addActionListener(this);

    deleteMenuItem = new JMenuItem("Delete");
    deleteMenuItem.addActionListener(this);

    editShapeMenuItem =  new JMenuItem("Edit polyline");
    editShapeMenuItem.addActionListener(this);

    connectShapeMenuItem =  new JMenuItem("Connect");
    connectShapeMenuItem.addActionListener(this);

    raiseMenuItem = new JMenuItem("Raise");
    raiseMenuItem.addActionListener(this);

    lowerMenuItem = new JMenuItem("Lower");
    lowerMenuItem.addActionListener(this);

    frontMenuItem = new JMenuItem("Bring to front");
    frontMenuItem.addActionListener(this);

    backMenuItem = new JMenuItem("Send to back");
    backMenuItem.addActionListener(this);

    groupMenuItem = new JMenuItem("Group");
    groupMenuItem.addActionListener(this);

    ungroupMenuItem = new JMenuItem("Ungroup");
    ungroupMenuItem.addActionListener(this);


    zoomInMenuItem = new JMenuItem("Zoom in");
    zoomInMenuItem.addActionListener(this);
    zoomOutMenuItem = new JMenuItem("Zoom out");
    zoomOutMenuItem.addActionListener(this);

    viewsOptionMenuItem = new JMenuItem("Object properties...");
    viewsOptionMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_P,InputEvent.CTRL_MASK));
    viewsOptionMenuItem.addActionListener(this);
    viewsTransformMenuItem = new JMenuItem("Transform view...");
    viewsTransformMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_T,InputEvent.CTRL_MASK));
    viewsTransformMenuItem.addActionListener(this);
    viewsBrowseMenuItem= new JMenuItem("Selection browser...");
    viewsBrowseMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_B,InputEvent.CTRL_MASK));
    viewsBrowseMenuItem.addActionListener(this);
    viewsGroupEditMenuItem = new JMenuItem("Group editor...");
    viewsGroupEditMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_G,InputEvent.CTRL_MASK));
    viewsGroupEditMenuItem.addActionListener(this);

    objMenu.add(infoMenuItem);
    objMenu.add(viewsBrowseMenuItem);
    objMenu.add(viewsOptionMenuItem);
    sep1 = new JSeparator();
    objMenu.add(sep1);
    objMenu.add(cutMenuItem);
    objMenu.add(copyMenuItem);
    objMenu.add(pasteMenuItem);
    objMenu.add(deleteMenuItem);
    sep4 = new JSeparator();
    objMenu.add(sep4);
    objMenu.add(groupMenuItem);
    objMenu.add(ungroupMenuItem);
    objMenu.add(viewsGroupEditMenuItem);
    sep3 = new JSeparator();
    objMenu.add(sep3);
    objMenu.add(editShapeMenuItem);
    objMenu.add(connectShapeMenuItem);
    objMenu.add(viewsTransformMenuItem);
    sep2 = new JSeparator();
    objMenu.add(sep2);
    objMenu.add(raiseMenuItem);
    objMenu.add(lowerMenuItem);
    objMenu.add(frontMenuItem);
    objMenu.add(backMenuItem);
    sep5 = new JSeparator();
    objMenu.add(sep5);
    objMenu.add(zoomInMenuItem);
    objMenu.add(zoomOutMenuItem);

    // Polyline menu
    polyMenu = new JPopupMenu();

    infoPolyMenuItem = new JMenuItem();
    infoPolyMenuItem.setEnabled(false);

    delSummitMenuItem = new JMenuItem("Delete control point");
    delSummitMenuItem.addActionListener(this);

    brkShapeMenuItem = new JMenuItem("Add a control point here");
    brkShapeMenuItem.addActionListener(this);

    set0ShapeMenuItem = new JMenuItem("Set as starting point");
    set0ShapeMenuItem.addActionListener(this);

    reorderShapeMenuItem = new JMenuItem("Invert order");
    reorderShapeMenuItem.addActionListener(this);

    cancelShapeMenuItem = new JMenuItem("Return to normal edition mode");
    cancelShapeMenuItem.addActionListener(this);

    polyMenu.add(infoPolyMenuItem);
    polyMenu.add(new JSeparator());
    polyMenu.add(delSummitMenuItem);
    polyMenu.add(set0ShapeMenuItem);
    polyMenu.add(brkShapeMenuItem);
    polyMenu.add(reorderShapeMenuItem);
    polyMenu.add(cancelShapeMenuItem);

  }

  private boolean isSelectedSummit(int id) {
    boolean found=false;
    int i=0;
    while(i<selSummits.length && !found) {
      found = (selSummits[i]==id);
      if(!found) i++;
    }
    return found;
  }

  private void selectSummit(int id) {
    if (!isSelectedSummit(id)) {
      int i;
      int[] nSelSummits = new int[selSummits.length + 1];
      for (i = 0; i < selSummits.length; i++) {
        nSelSummits[i] = selSummits[i];
      }
      nSelSummits[i] = id;
      selSummits = nSelSummits;
    }
  }

  protected Rectangle buildRepaintRect(Vector obs) {

    Rectangle oldRect = null;

    // Build the rectangle to repaint
    for (int i = 0; i < obs.size(); i++) {
      JDObject p = (JDObject) obs.get(i);
      if (oldRect == null)
        oldRect = p.getRepaintRect();
      else
        oldRect = oldRect.union(p.getRepaintRect());
    }

    return oldRect;

  }

  private void repaintLater() {
    // JDSwingObbjects need repaintLater
    SwingUtilities.invokeLater(new Runnable(){
      public void run() {
        repaint();
      }
    });
  }

  private boolean createObject(int eX,int eY) {

    int ex,ey;
    if( alignToGrid ) {
      ex = ((eX + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
      ey = ((eY + GRID_SIZE / 2) / GRID_SIZE) * GRID_SIZE;
    } else {
      ex = eX;
      ey = eY;
    }

    switch (creationMode) {
      case CREATE_RECTANGLE:
        createObject(new JDRectangle("Rectangle", ex, ey, 4, 4), 4);
        return true;
      case CREATE_RRECTANGLE:
        createObject(new JDRoundRectangle("RoundRectangle", ex, ey, 4, 4), 4);
        return true;
      case CREATE_LINE:
        createObject(new JDLine("Line", ex, ey, ex, ey), 1);
        return true;
      case CREATE_ELLIPSE:
        createObject(new JDEllipse("Ellipse", ex, ey, 4, 4), 4);
        return true;
      case CREATE_POLYLINE:
      case CREATE_SPLINE:
        int s = tmpPoints.size();
        if (s == 0) {
          unselectAll(false);
          tmpPoints.clear();
          tmpPoints.add(new Point(ex, ey));
          tmpPoints.add(new Point(ex + 4, ey + 4));
        } else {
          Rectangle old = buildRectFromLine((Point) tmpPoints.get(s - 2), (Point) tmpPoints.get(s - 1));
          tmpPoints.add(new Point(ex, ey));
          repaint(old.union(buildRectFromLine((Point) tmpPoints.get(s - 1), (Point) tmpPoints.get(s))));
        }
        fireSelectionChange();
        return true;
      case CREATE_LABEL:
        String str = JOptionPane.showInputDialog(this, "Enter a text", "Create label", JOptionPane.INFORMATION_MESSAGE);
        if (str != null)
          createObject(new JDLabel("Label", str, ex, ey), -1);
        else {
          //Canceling
          creationMode = 0;
          fireCreationDone();
        }
        return true;

      case CREATE_IMAGE:
        JFileChooser chooser = new JFileChooser(".");
	//chooser.changeToParentDirectory();
	String currentDir = chooser.getCurrentDirectory().getAbsolutePath();
        String[] exts={"gif","png","jpg"};
        chooser.addChoosableFileFilter(new JDFileFilter("Image file",exts));
        if (chooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
        	//createObject(new JDImage("Image", chooser.getSelectedFile().getAbsolutePath(),ex, ey), -1);
		String filePath = chooser.getSelectedFile().getAbsolutePath();
		if (filePath.startsWith(currentDir)) {
			filePath = filePath.replaceFirst(currentDir,"");
			if (filePath.startsWith("/")) filePath=filePath.replaceFirst("/","");
			if (filePath.startsWith("\\")) filePath=filePath.replaceFirst("\\","");
			}
	
		try {
			System.out.println("The path is : "+currentDir+
					" + "+filePath);
		} catch (Exception e) {}
		createObject(new JDImage("Image", filePath,ex, ey), -1);
		return true;
        }
        break;

      case CREATE_SWINGOBJECT:
        if(creationParam!=null) {
          createObject(new JDSwingObject("SwingObject", creationParam , ex, ey), -1);
          repaintLater();
        }
        return true;

      case CREATE_AXIS:
        createObject(new JDAxis("Axis", ex, ey , 50,100), -1);
        return true;

      case CREATE_BAR:
        createObject(new JDBar("Bar", ex, ey, 4, 4), 4);
        return true;

      case CREATE_SLIDER:
        createObject(new JDSlider("Slider", ex, ey, 4, 4), 4);
        return true;

      case CREATE_SLIDER_CURSOR:
        JDObject e = findObject(eX,eY);
        if(e==null) {
          JOptionPane.showMessageDialog(this, "Cannot pick new cursor for slider:\nNo object found here.");
        } else if (e instanceof JDSlider) {
          JOptionPane.showMessageDialog(this, "Cannot pick new cursor for slider:\n.Slider cannot be taken as cursor.");
        } else {
          sliderRef.setCursor(e.copy(0,0));
          setNeedToSave(true, "Pick new cursor");
        }
        repaint();
        creationMode = 0;
        fireCreationDone();
        return true;

      case CREATE_CONNECT_POLY:
        e = findObject(eX,eY);
        if(e==null) {
          JOptionPane.showMessageDialog(this, "No polyline found here.");
        } else if (!(e instanceof JDPolyline)) {
          JOptionPane.showMessageDialog(this, "This object is not a polyline.");
        } else if (e.equals(connectPolyline)) {
          JOptionPane.showMessageDialog(this, "Cannot connect to itself.");
        } else {
          connectPolyline.connect((JDPolyline)e);
          objects.remove(e);
          setNeedToSave(true, "Connect polyline");
        }
        repaint();
        creationMode = 0;
        fireCreationDone();
        return true;

      case CREATE_CLIPBOARD:
        creationMode = 0;
        pasteClipboard(ex, ey);
        fireCreationDone();
        return true;

    }

    return false;
  }

}