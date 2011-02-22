/**
 * User: Jean Luc
 * Date: Aug 10, 2003
 * Time: 12:27:00 AM
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Vector;
import java.io.IOException;

/** ******************************************************************************************************
srubio@cells.es, oktober 2006
The Class JDrawEditorFrame has been modified to:
	- Allow opening external files as read-only libraries
	- Use the new FileFinder class to find all the available libraries in the predefined folder $LIB_PATH
	- Add a library selector to the toolbar
*********************************************************************************************************/

/** Main JDrawEditor frame, can be extended to produce customized editor. This class creates all menu and button
 * needed  by the editor. All actions are handled by this class and can be overrided by overriding actionPerformed(). */
public class JDrawEditorFrame extends JFrame implements ActionListener,JDrawEditorListener,JDValueListener {

  /** The editor scroll view. */
  public JScrollPane theEditorView;

  /** The status label (display at the bottom of the frame). */
  public JLabel statusLabel;

  /** File menu. */
  public JMenu     fileMenu;
  /** File->Open menu item. */
  public JMenuItem fileOpenMenuItem;
  /** File->Import menu item. */
  public JMenuItem fileImportMenuItem;
  /** File->Save menu item. */
  public JMenuItem fileSaveMenuItem;
  /** File->Save as menu item. */
  public JMenuItem fileSaveasMenuItem;
  /** File->Exit menu item. */
  public JMenuItem fileExitMenuItem;

  /** Edit menu. */
  public JMenu     editMenu;
  /** Edit->Undo menu item. */
  public JMenuItem editUndoMenuItem;
  /** Edit->Redo menu item. */
  public JMenuItem editRedoMenuItem;
  /** Edit->Cut menu item. */
  public JMenuItem editCutMenuItem;
  /** Edit->Copy menu item. */
  public JMenuItem editCopyMenuItem;
  /** Edit->Paste menu item. */
  public JMenuItem editPasteMenuItem;
  /** Edit->Delete menu item. */
  public JMenuItem editDeleteMenuItem;
  /** Edit->Select All menu item. */
  public JMenuItem editSelectAllMenuItem;
  /** Edit->Select None menu item. */
  public JMenuItem editSelectNoneMenuItem;

  /** Views menu. */
  public  JMenu     viewsMenu;
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
  /** Views->Generate java menu item. */
  private JMenuItem viewsJavaMenuItem;
  /** Views->Global properties menu item. */
  private JMenuItem viewsGlobalMenuItem;

  /** Tools menu. */
  public  JMenu     toolsMenu;
  /** Tools->H Mirror menu item. */
  public  JMenuItem toolsHMirrorMenuItem;
  /** Tools->V Mirror menu item. */
  public  JMenuItem toolsVMirrorMenuItem;
  /** Tools->Align top menu item. */
  public  JMenuItem toolsAligntopMenuItem;
  /** Tools->Align left menu item. */
  public  JMenuItem toolsAlignleftMenuItem;
  /** Tools->Align bottom menu item. */
  public  JMenuItem toolsAlignbottomMenuItem;
  /** Tools->Align rigth item. */
  public  JMenuItem toolsAlignrightMenuItem;
  /** Tools->Raise menu item. */
  private JMenuItem toolsRaiseMenuItem;
  /** Tools->Lower menu item. */
  private JMenuItem toolsLowerMenuItem;
  /** Tools->Front menu item. */
  private JMenuItem toolsFrontMenuItem;
  /** Tools->Back menu item. */
  private JMenuItem toolsBackMenuItem;
  /** Tools->Convert to polyline menu item. */
  private JMenuItem toolsConvertPolyMenuItem;
  /** Tools->Grid visible menu item. */
  private JCheckBoxMenuItem toolsGridVisible;
  /** Tools->Align to grid menu check box item. */
  private JCheckBoxMenuItem toolsAlignToGrid;
  /** Tools->Grid settings menu item. */
  private JMenuItem toolsGridSettings;
  /** Tools->Fit to graph menu item. */
  private JMenuItem toolsFitToGraph;

  /** Creation menus. */
  public  JDCreationMenu createMenu;

  /** The Edition toolbar toolbar. */
  public JToolBar editToolBar;
  /** 'Open' toolbar button. */
  public JButton  editToolFileOpenBtn;
  /** 'Save' toolbar button. */
  public JButton  editToolFileSaveBtn;
  /** 'Undo' toolbar button. */
  public JButton  editToolUndoBtn;
  /** 'Redo' toolbar button. */
  public JButton  editToolRedoBtn;
  /** 'Cut' toolbar button. */
  public JButton  editToolCutBtn;
  /** 'Copy' toolbar button. */
  public JButton  editToolCopyBtn;
  /** 'Paste' toolbar button. */
  public JButton  editToolPasteBtn;
  /** 'Zoom In' toolbar button. */
  public JButton  editToolZoomInBtn;
  /** 'Zoom Out' toolbar button. */
  public JButton  editToolZoomOutBtn;
  /** 'Zoom percent' toolbar label. */
  public JLabel   editToolZoomLabel;
  /** 'Object properties' toolbar button. */
  public JButton  editToolOptionBtn;
  /** 'Transform' toolbar button. */
  public JButton  editToolTransformBtn;
  /** 'H Mirror' toolbar button. */
  public JButton  editToolHMirrorBtn;
  /** 'V Mirror' toolbar button. */
  public JButton  editToolVMirrorBtn;
  /** 'Align Left' toolbar button. */
  public JButton  editToolAlignLeftBtn;
  /** 'Align Top' toolbar button. */
  public JButton  editToolAlignTopBtn;
  /** 'Align Right' toolbar button. */
  public JButton  editToolAlignRightBtn;
  /** 'Align Bottom' toolbar button. */
  public JButton  editToolAlignBottomBtn;

  // Private stuff
  private JDrawEditor theEditor;
  private JDrawEditor thePlayer;
  private JFrame      framePlayer;
  private JScrollPane fpTextView;
  private JTextArea   fpText;
  private JMenuItem   viewDebugOutput;
  private JMenuItem   hideDebugOutput;
  private JMenuItem   clearDebugOutput;
  private StringBuffer fpStr;
  private JPanel      statusLine;
  private JMenuBar    theMenu;
  private String      APP_RELEASE;
  private JSplitPane  splitPane;
  
  private JButton[] libButton;
  private JComboBox libCombo;
  private JDLibraryViewer[] libViewer;
  private int nLibs;
  
  /**
   * Contruct an Editor frame.
   * @see #main
   */
  public JDrawEditorFrame() {
	System.out.println("JDrawEditorFrame()");
    setTitle(APP_RELEASE);
    Container pane=getContentPane();
    pane.setLayout(new BorderLayout());

    // Help label
    statusLine = new JPanel(new GridLayout(1,1));
    pane.add(statusLine,BorderLayout.SOUTH);

    statusLabel = new JLabel();
    statusLabel.setFont(JDUtils.labelFont);
    statusLabel.setHorizontalAlignment(JLabel.LEFT);
    statusLine.add(statusLabel);

    // -------------------------------------
    // The toolbar
    // -------------------------------------
    createMenu = new JDCreationMenu();
    pane.add(createMenu.getToolbar(),BorderLayout.WEST);

    // -------------------------------------
    // The edit toolbar
    // -------------------------------------
    editToolBar = new JToolBar();

    editToolZoomLabel = new JLabel();
    editToolZoomLabel.setFont(JDUtils.labelFont);
    editToolZoomLabel.setText("100%");
    editToolZoomLabel.setHorizontalAlignment(JLabel.CENTER);
    editToolZoomLabel.setMaximumSize(new Dimension(50,32));
    editToolZoomLabel.setPreferredSize(new Dimension(50,32));
    editToolZoomLabel.setMinimumSize(new Dimension(50,32));

    editToolFileOpenBtn = JDUtils.createIconButton("jdraw_fileopen",true,"Open File",this);
    editToolFileSaveBtn = JDUtils.createIconButton("jdraw_filesave",true,"Save File",this);
    editToolUndoBtn = JDUtils.createIconButton("jdraw_undo",true,"Undo the last action",this);
    editToolRedoBtn = JDUtils.createIconButton("jdraw_redo",true,"Redo the last canceled action",this);
    editToolCutBtn = JDUtils.createIconButton("jdraw_cut",true,"Cut selection",this);
    editToolCopyBtn = JDUtils.createIconButton("jdraw_copy",true,"Copy selection to clipboard",this);
    editToolPasteBtn = JDUtils.createIconButton("jdraw_paste",true,"Paste selection",this);
    editToolZoomInBtn = JDUtils.createIconButton("jdraw_zoom",true,"Zoom In",this);
    editToolZoomOutBtn = JDUtils.createIconButton("jdraw_zoomm",true,"Zoom Out",this);
    editToolOptionBtn = JDUtils.createIconButton("jdraw_option",true,"Show selected object(s) properties",this);
    editToolTransformBtn = JDUtils.createIconButton("jdraw_transform",true,"Show transformation dialog",this);
    editToolHMirrorBtn = JDUtils.createIconButton("jdraw_hmirror",true,"Horizontal mirror on selected object(s)",this);
    editToolVMirrorBtn = JDUtils.createIconButton("jdraw_vmirror",true,"Vertical mirror on selected object(s)",this);
    editToolAlignTopBtn = JDUtils.createIconButton("jdraw_aligntop",true,"Align selected objects",this);
    editToolAlignLeftBtn = JDUtils.createIconButton("jdraw_alignleft",true,"Align selected objects",this);
    editToolAlignBottomBtn = JDUtils.createIconButton("jdraw_alignbottom",true,"Align selected objects",this);
    editToolAlignRightBtn = JDUtils.createIconButton("jdraw_alignright",true,"Align selected objects",this);

    editToolBar.add(editToolFileOpenBtn);
    editToolBar.add(editToolFileSaveBtn);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(editToolUndoBtn);
    editToolBar.add(editToolRedoBtn);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(editToolCutBtn);
    editToolBar.add(editToolCopyBtn);
    editToolBar.add(editToolPasteBtn);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(editToolZoomInBtn);
    editToolBar.add(editToolZoomOutBtn);
    editToolBar.add(editToolZoomLabel);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(editToolOptionBtn);
    editToolBar.add(editToolTransformBtn);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(editToolHMirrorBtn);
    editToolBar.add(editToolVMirrorBtn);
    editToolBar.add(editToolAlignTopBtn);
    editToolBar.add(editToolAlignLeftBtn);
    editToolBar.add(editToolAlignBottomBtn);
    editToolBar.add(editToolAlignRightBtn);
    
    editToolBar.setOrientation(JToolBar.HORIZONTAL);
    pane.add(editToolBar,BorderLayout.NORTH);
    // -------------------------------------
    // Main menu
    // -------------------------------------
    theMenu = new JMenuBar();

    // File ----------------------------------------
    fileExitMenuItem = new JMenuItem("Exit");
    fileExitMenuItem.addActionListener(this);
    fileOpenMenuItem = new JMenuItem("Open...");
    fileOpenMenuItem.addActionListener(this);
    fileImportMenuItem = new JMenuItem("Import...");
    fileImportMenuItem.addActionListener(this);
    fileSaveMenuItem = new JMenuItem("Save");
    fileSaveMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_S,InputEvent.CTRL_MASK));
    fileSaveMenuItem.addActionListener(this);
    fileSaveasMenuItem = new JMenuItem("Save as...");
    fileSaveasMenuItem.addActionListener(this);

    fileMenu = new JMenu("File");
    fileMenu.setMnemonic('F');
    fileMenu.add(fileOpenMenuItem);
    fileMenu.add(fileImportMenuItem);
    fileMenu.add(fileSaveMenuItem);
    fileMenu.add(fileSaveasMenuItem);
    fileMenu.add(new JSeparator());
    fileMenu.add(fileExitMenuItem);

    theMenu.add(fileMenu);

    // Edit -----------------------------------------
    editUndoMenuItem = new JMenuItem("Undo");
    editUndoMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_Z,InputEvent.CTRL_MASK));
    editUndoMenuItem.addActionListener(this);
    editRedoMenuItem = new JMenuItem("Redo");
    editRedoMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_Z,InputEvent.SHIFT_MASK + InputEvent.CTRL_MASK));
    editRedoMenuItem.addActionListener(this);
    editCutMenuItem = new JMenuItem("Cut");
    editCutMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_X,InputEvent.CTRL_MASK));
    editCutMenuItem.addActionListener(this);
    editCopyMenuItem = new JMenuItem("Copy");
    editCopyMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_C,InputEvent.CTRL_MASK));
    editCopyMenuItem.addActionListener(this);
    editPasteMenuItem = new JMenuItem("Paste");
    editPasteMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_V,InputEvent.CTRL_MASK));
    editPasteMenuItem.addActionListener(this);
    editDeleteMenuItem = new JMenuItem("Delete");
    editDeleteMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_DELETE,0));
    editDeleteMenuItem.addActionListener(this);
    editSelectAllMenuItem = new JMenuItem("Select all");
    editSelectAllMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_A,InputEvent.CTRL_MASK));
    editSelectAllMenuItem.addActionListener(this);
    editSelectNoneMenuItem = new JMenuItem("Select none");
    editSelectNoneMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_N,InputEvent.CTRL_MASK));
    editSelectNoneMenuItem.addActionListener(this);


    editMenu = new JMenu("Edit");
    editMenu.setMnemonic('E');
    editMenu.add(editUndoMenuItem);
    editMenu.add(editRedoMenuItem);
    editMenu.add(new JSeparator());
    editMenu.add(editCutMenuItem);
    editMenu.add(editCopyMenuItem);
    editMenu.add(editPasteMenuItem);
    editMenu.add(editDeleteMenuItem);
    editMenu.add(new JSeparator());
    editMenu.add(editSelectAllMenuItem);
    editMenu.add(editSelectNoneMenuItem);

    theMenu.add(editMenu);

    theMenu.add(createMenu.getMenu());

    // Views -----------------------------------------
    viewsPlayMenuItem = new JMenuItem("Player view");
    viewsPlayMenuItem.addActionListener(this);
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
    viewsJavaMenuItem = new JMenuItem("Java code generator...");
    viewsJavaMenuItem.addActionListener(this);
    viewsGlobalMenuItem = new JMenuItem("Global properties...");
    viewsGlobalMenuItem.addActionListener(this);

    viewsMenu = new JMenu("Views");
    viewsMenu.setMnemonic('V');
    viewsMenu.add(viewsPlayMenuItem);
    viewsMenu.add(viewsGlobalMenuItem);
    viewsMenu.add(viewsTransformMenuItem);
    viewsMenu.add(viewsOptionMenuItem);
    viewsMenu.add(viewsBrowseMenuItem);
    viewsMenu.add(viewsGroupEditMenuItem);
    viewsMenu.add(viewsJavaMenuItem);

    theMenu.add(viewsMenu);

    // Tools -----------------------------------------
    toolsHMirrorMenuItem = new JMenuItem("Horizontal mirror");
    toolsHMirrorMenuItem.addActionListener(this);
    toolsVMirrorMenuItem = new JMenuItem("Vertical mirror");
    toolsVMirrorMenuItem.addActionListener(this);
    toolsAligntopMenuItem = new JMenuItem("Align top");
    toolsAligntopMenuItem.addActionListener(this);
    toolsAlignleftMenuItem = new JMenuItem("Align left");
    toolsAlignleftMenuItem.addActionListener(this);
    toolsAlignbottomMenuItem = new JMenuItem("Align bottom");
    toolsAlignbottomMenuItem.addActionListener(this);
    toolsAlignrightMenuItem = new JMenuItem("Align right");
    toolsAlignrightMenuItem.addActionListener(this);
    toolsConvertPolyMenuItem = new JMenuItem("Convert to Polyline");
    toolsConvertPolyMenuItem.addActionListener(this);
    toolsRaiseMenuItem = new JMenuItem("Raise");
    toolsRaiseMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_Q,InputEvent.SHIFT_MASK +InputEvent.CTRL_MASK));
    toolsRaiseMenuItem.addActionListener(this);
    toolsLowerMenuItem = new JMenuItem("Lower");
    toolsLowerMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_W,InputEvent.SHIFT_MASK +InputEvent.CTRL_MASK));
    toolsLowerMenuItem.addActionListener(this);
    toolsFrontMenuItem = new JMenuItem("Bring to front");
    toolsFrontMenuItem.addActionListener(this);
    toolsBackMenuItem = new JMenuItem("Send to back");
    toolsBackMenuItem.addActionListener(this);
    toolsAlignToGrid = new JCheckBoxMenuItem("Align to grid");
    toolsAlignToGrid.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_A,InputEvent.SHIFT_MASK +InputEvent.CTRL_MASK));
    toolsAlignToGrid.setSelected(false);
    toolsAlignToGrid.addActionListener(this);
    toolsGridVisible = new JCheckBoxMenuItem("Show grid");
    toolsGridVisible.setSelected(false);
    toolsGridVisible.addActionListener(this);
    toolsGridSettings = new JMenuItem("Grid settings...");
    toolsGridSettings.addActionListener(this);
    toolsFitToGraph = new JMenuItem("Fit view to graph");
    toolsFitToGraph.addActionListener(this);

    toolsMenu = new JMenu("Tools");
    toolsMenu.setMnemonic('T');
    toolsMenu.add(toolsHMirrorMenuItem);
    toolsMenu.add(toolsVMirrorMenuItem);
    toolsMenu.add(new JSeparator());
    toolsMenu.add(toolsAligntopMenuItem);
    toolsMenu.add(toolsAlignleftMenuItem);
    toolsMenu.add(toolsAlignbottomMenuItem);
    toolsMenu.add(toolsAlignrightMenuItem);
    toolsMenu.add(new JSeparator());
    toolsMenu.add(toolsRaiseMenuItem);
    toolsMenu.add(toolsLowerMenuItem);
    toolsMenu.add(toolsFrontMenuItem);
    toolsMenu.add(toolsBackMenuItem);
    toolsMenu.add(new JSeparator());
    toolsMenu.add(toolsConvertPolyMenuItem);
    toolsMenu.add(new JSeparator());
    toolsMenu.add(toolsAlignToGrid);
    toolsMenu.add(toolsGridVisible);
    toolsMenu.add(toolsGridSettings);
    toolsMenu.add(new JSeparator());
    toolsMenu.add(toolsFitToGraph);

    theMenu.add(toolsMenu);

    setJMenuBar(theMenu);

  }

  // ----------------------------------------------------
  // Property
  // ----------------------------------------------------
  /** Sets the editor of this EditorFrame. */
  public void setEditor(JDrawEditor editor) {
    theEditor = editor;
    theEditor.setStatusLabel(statusLabel);
    theEditor.setStatus("");
    theEditor.addEditorListener(this);
    createMenu.setEditor(editor);
    theEditor.setBorder(BorderFactory.createEtchedBorder());
    theEditorView = new JScrollPane(editor);
    theEditorView.setWheelScrollingEnabled(true);
    getContentPane().add(theEditorView,BorderLayout.CENTER);
    // Update controls
    selectionChanged();
    valueChanged();
    clipboardChanged();
  }

  /** Sets the player of this EditorFrame. (for the play mode) */
  public void setPlayer(JDrawEditor editor) {
    framePlayer = new JFrame();
    framePlayer.getContentPane().setLayout(new BorderLayout());
     JMenuBar fpBar= new JMenuBar();
     JMenu fpMenu = new JMenu("Debug");
     viewDebugOutput = new JMenuItem("View output");
     viewDebugOutput.addActionListener(this);
     fpMenu.add(viewDebugOutput);
     hideDebugOutput = new JMenuItem("Hide output");
     hideDebugOutput.addActionListener(this);
     fpMenu.add(hideDebugOutput);
     clearDebugOutput = new JMenuItem("Clear history");
     clearDebugOutput.addActionListener(this);
     fpMenu.add(clearDebugOutput);
    fpBar.add(fpMenu);

    splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT);
    fpText = new JTextArea();
    fpText.setEditable(false);
    fpText.setFont(JDUtils.labelFont);
    fpTextView = new JScrollPane(fpText);
    thePlayer = new JDrawEditor(JDrawEditor.MODE_PLAY);
    splitPane.add(thePlayer);
    splitPane.add(fpTextView);
    framePlayer.getContentPane().add(splitPane,BorderLayout.CENTER);
    fpTextView.setPreferredSize(new Dimension(0,60));
    framePlayer.setTitle("Play mode");
    framePlayer.setJMenuBar(fpBar);
    framePlayer.addWindowListener(new WindowAdapter() {
      public void windowClosing(WindowEvent e) {
        fpStr = new StringBuffer();
        fpText.setText("");
      }
    });

  }

  /** Name used to build the frame title. */
  public void setAppTitle(String title) {
    APP_RELEASE = title;
  }

  // -------------------------------------
  // Palette Libraries
  // -------------------------------------
  public void setLibraries(String path) {
    String libPath;
    if (path == null) libPath = System.getProperty("LIBPATH", "null");
    else libPath = path;
    if ( libPath.equals("null") ) System.out.println("Warning LIBPATH is not defined.");
    FileFinder ff = new FileFinder(libPath,".lib",12);
    String[] fileList = ff.getList(true);
    if (fileList == null) {
        // Either dir does not exist or is not a directory
	System.out.println("No libraries found in "+libPath);
	return;
    }
    // Customize the editor
    nLibs = fileList.length;
    libViewer = new JDLibraryViewer[nLibs];
    libButton = new JButton[nLibs];
    libCombo = new JComboBox();
    libCombo.addItem("Palette Libraries");
    for (int i=0; i<nLibs; i++) {
	    libViewer[i] = new JDLibraryViewer(libPath+(!libPath.endsWith("/")?"/":"")+fileList[i],theEditor,false);
	    libViewer[i].setTitle("JDraw library: "+fileList[i]);
	    //ATKGraphicsUtils.centerFrameOnScreen(libViewer[i]);
	    final Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
	    libViewer[i].pack();
	    libViewer[i].setBounds(
		    screenSize.width-libViewer[i].getPreferredSize().width-15,
		    (screenSize.height-libViewer[i].getPreferredSize().height)/2,
		    (libViewer[i].getPreferredSize().width<screenSize.width?libViewer[i].getPreferredSize().width:screenSize.width),
		    (libViewer[i].getPreferredSize().height<screenSize.height?libViewer[i].getPreferredSize().height:screenSize.width));
	    libCombo.addItem(fileList[i]);
    }
    libCombo.addItem("Choose a file ...");
    libCombo.setSelectedIndex(0);
    libCombo.addActionListener(this);
    editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
    editToolBar.add(libCombo);
    //end-----------------------------------
  }

  // ----------------------------------------------------
  // ACtion listener
  // ----------------------------------------------------
  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    if( src==fileExitMenuItem ) {
      exitApp();
    } else if (src==editToolPasteBtn || src==editPasteMenuItem) {
      theEditor.create(JDrawEditor.CREATE_CLIPBOARD);
    } else if (src==editToolCopyBtn || src==editCopyMenuItem) {
      theEditor.copySelection();
    } else if (src==editToolCutBtn || src==editCutMenuItem) {
      theEditor.cutSelection();
    } else if (src==editDeleteMenuItem) {
      theEditor.deleteSelection();
    } else if (src==editToolOptionBtn || src==viewsOptionMenuItem) {
      theEditor.showPropertyWindow();
    } else if (src==editToolTransformBtn || src==viewsTransformMenuItem) {
      theEditor.showTransformWindow();
    } else if (src==editToolHMirrorBtn || src==toolsHMirrorMenuItem) {
      theEditor.scaleSelection(-1.0,1.0);
    } else if (src==editToolVMirrorBtn || src==toolsVMirrorMenuItem) {
      theEditor.scaleSelection( 1.0,-1.0);
    } else if (/*src==editToolFileSaveBtn || */src==fileSaveasMenuItem) {
      theEditor.showSaveDialog(".");
    } else if (src==editToolFileOpenBtn || src==fileOpenMenuItem) {
      theEditor.showOpenDialog(".");
    } else if(src==editToolFileSaveBtn || src==fileSaveMenuItem) {
      theEditor.instantSave(".");
    } else if (src==editToolZoomInBtn) {
      theEditor.zoomIn();
    } else if (src==editToolZoomOutBtn) {
      theEditor.zoomOut();
    } else if (src==editSelectAllMenuItem) {
      theEditor.selectAll();
    } else if (src==editSelectNoneMenuItem) {
      theEditor.unselectAll();
    } else if (src==editToolUndoBtn || src==editUndoMenuItem) {
      theEditor.undo();
    } else if (src==editToolRedoBtn || src==editRedoMenuItem) {
      theEditor.redo();
    } else if (src==editToolAlignTopBtn || src==toolsAligntopMenuItem) {
      theEditor.aligntopSelection();
    } else if (src==editToolAlignLeftBtn || src==toolsAlignleftMenuItem) {
      theEditor.alignleftSelection();
    } else if (src==editToolAlignBottomBtn || src==toolsAlignbottomMenuItem) {
      theEditor.alignbottomSelection();
    }  else if (src==editToolAlignRightBtn || src==toolsAlignrightMenuItem) {
      theEditor.alignrightSelection();
    }  else if (src==viewsBrowseMenuItem) {
      theEditor.showBrowserWindow();
    } else if (src==viewsPlayMenuItem) {
      showPlayer();
    } else if (src == viewsGroupEditMenuItem) {
      theEditor.showGroupEditorWindow();
    } else if (src == viewsJavaMenuItem) {
      theEditor.showGroupJavaWindow();
    } else if (src == viewsGlobalMenuItem) {
      JDUtils.showGlobalDialog(theEditor);
    } else if (src == toolsConvertPolyMenuItem) {
      theEditor.convertToPolyline();
    } else if (src == toolsRaiseMenuItem) {
      theEditor.raiseObject();
    } else if (src == toolsLowerMenuItem) {
      theEditor.lowerObject();
    } else if (src == toolsFrontMenuItem) {
      theEditor.frontSelection();
    } else if (src == toolsBackMenuItem) {
      theEditor.backSelection();
    } else if (src == viewDebugOutput) {
      fpTextView.setVisible(true);
      splitPane.setDividerLocation(splitPane.getHeight()-80);
      splitPane.revalidate();
    } else if (src == hideDebugOutput) {
      fpTextView.setVisible(false);
      splitPane.revalidate();
    } else if (src == clearDebugOutput) {
      fpStr = new StringBuffer();
      fpText.setText("");
    } else if (src == toolsAlignToGrid) {
      theEditor.setAlignToGrid(toolsAlignToGrid.isSelected());
    } else if (src == toolsGridVisible) {
      theEditor.setGridVisible(toolsGridVisible.isSelected());
    } else if (src == toolsGridSettings) {
      String newSize = JOptionPane.showInputDialog("Enter Grid Size",new Integer(theEditor.getGridSize()));
      if( newSize!=null ) {
        try {
          int sz = Integer.parseInt(newSize);
          theEditor.setGridSize(sz);
        } catch (NumberFormatException e2) {
          JOptionPane.showMessageDialog(this,"Wrong integer value\n" + e2.getMessage());
        }
      }
    } else if (src == toolsFitToGraph) {
      theEditor.computePreferredSize();      
    } else if( src==libCombo) {
	    if ( libCombo.getSelectedIndex()>libViewer.length) {
		    String fullFileName;
		    JFileChooser chooser = new JFileChooser(".");
		    chooser.setDialogTitle("[SimpleSynopticAppli] Open a synoptic file.");
		    int returnVal = chooser.showOpenDialog(null);
		    if (returnVal == JFileChooser.APPROVE_OPTION) {
			    java.io.File f = chooser.getSelectedFile();
			    fullFileName = f.getAbsolutePath();
		    } else {
			return;
		    }	
		    JDLibraryViewer noLib = new JDLibraryViewer(fullFileName,theEditor,false);
		    noLib.setTitle("JDraw library: "+fullFileName);
		    final Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		    noLib.pack();
		    noLib.setBounds(
			    screenSize.width-noLib.getPreferredSize().width-15,
			    (screenSize.height-noLib.getPreferredSize().height)/2,
			    (noLib.getPreferredSize().width<screenSize.width?noLib.getPreferredSize().width:screenSize.width),
			    (noLib.getPreferredSize().height<screenSize.height?noLib.getPreferredSize().height:screenSize.width));
		    noLib.setVisible(true);
		    libCombo.setSelectedIndex(0);
		    return;		    
	    } else if ( libCombo.getSelectedIndex()>0 ) {
		    libViewer[libCombo.getSelectedIndex()-1].setVisible(true);
		    libCombo.setSelectedIndex(0);
		    return;
	    }
    }

  }

  // ---------------------------------------------------
  // Editor listener
  // ---------------------------------------------------
  public void creationDone() {}

  public void selectionChanged() {
    int sz=theEditor.getSelectionLength();
    editToolCutBtn.setEnabled(sz>0);
    editCutMenuItem.setEnabled(sz>0);
    editToolCopyBtn.setEnabled(sz>0);
    editCopyMenuItem.setEnabled(sz>0);
    editDeleteMenuItem.setEnabled(sz>0);
    editToolOptionBtn.setEnabled(sz>0);
    viewsOptionMenuItem.setEnabled(sz>0);
    editToolTransformBtn.setEnabled(sz>0);
    viewsTransformMenuItem.setEnabled(sz>0);
    editToolHMirrorBtn.setEnabled(sz>0);
    toolsHMirrorMenuItem.setEnabled(sz>0);
    editToolVMirrorBtn.setEnabled(sz>0);
    toolsVMirrorMenuItem.setEnabled(sz>0);
    editToolAlignLeftBtn.setEnabled(sz>1);
    toolsAlignleftMenuItem.setEnabled(sz>1);
    editToolAlignTopBtn.setEnabled(sz>1);
    toolsAligntopMenuItem.setEnabled(sz>1);
    editToolAlignRightBtn.setEnabled(sz>1);
    toolsAlignrightMenuItem.setEnabled(sz>1);
    editToolAlignBottomBtn.setEnabled(sz>1);
    toolsAlignbottomMenuItem.setEnabled(sz>1);
    editSelectAllMenuItem.setEnabled(sz<theEditor.getObjectNumber());
    editSelectNoneMenuItem.setEnabled(sz>0);
    viewsBrowseMenuItem.setEnabled(sz>0);
    toolsConvertPolyMenuItem.setEnabled(theEditor.canConvertToPolyline());
    viewsGroupEditMenuItem.setEnabled(theEditor.canEditGroup());
    viewsJavaMenuItem.setEnabled(sz>0);
    toolsRaiseMenuItem.setEnabled((sz == 1));
    toolsLowerMenuItem.setEnabled((sz == 1));
    toolsFrontMenuItem.setEnabled((sz >= 1));
    toolsBackMenuItem.setEnabled((sz >= 1));
    toolsAlignToGrid.setSelected(theEditor.isAlignToGrid());
    toolsGridVisible.setSelected(theEditor.isGridVisible());

  }

  public void clipboardChanged() {
    int sz=theEditor.getClipboardLength();
    editToolPasteBtn.setEnabled(sz>0);
    editPasteMenuItem.setEnabled(sz>0);
  }

  public void valueChanged() {

    editUndoMenuItem.setText("Undo " + theEditor.getLastActionName());
    editUndoMenuItem.setEnabled(theEditor.canUndo());
    editRedoMenuItem.setText("Redo " + theEditor.getNextActionName());
    editRedoMenuItem.setEnabled(theEditor.canRedo());
    editToolUndoBtn.setEnabled(theEditor.canUndo());
    editToolRedoBtn.setEnabled(theEditor.canRedo());

    String title = APP_RELEASE;
    if(theEditor.getFileName().length()>0) {
      title += " [" + theEditor.getFileName() + "]";
    }

    if( theEditor.getNeedToSaveState() )  setTitle(title+"*");
    else                           setTitle(title);

  }

  public void sizeChanged() {
    theEditorView.revalidate();
    repaint();
    editToolZoomLabel.setText( theEditor.getZoomFactorPercent() + "%" );
  }

  // ----------------------------------------------------
  // JDValue Listener
  // ----------------------------------------------------
  public void valueChanged(JDObject src) {
    if (fpTextView.isVisible()) {
      fpStr.append(src.getName() + " valueChanged(value=" + src.getValue() + ")\n");
      fpText.setText(fpStr.toString());
    }
  }

  public void valueExceedBounds(JDObject src) {
    if (fpTextView.isVisible()) {
      fpStr.append(src.getName() + " valueExceedBounds(value=" + src.getValue() + ")\n");
      fpText.setText(fpStr.toString());
    }
  }

  // ----------------------------------------------------
  // Private stuff
  // ----------------------------------------------------
  private void showPlayer() {
    int i;
    thePlayer.clearObjects();

    // Duplicate global option
    thePlayer.setBackground(theEditor.getBackground());

    fpStr = new StringBuffer();

    for(i=0;i<theEditor.getObjectNumber();i++) {

      JDObject p = theEditor.getObjectAt(i).copy(0,0);
      thePlayer.addObject(p);
      if(p.isProgrammed())
        fpStr.append(p.getName() + " is programmed.\n");

      /*
      p.addMouseListener(new JDMouseAdapter() {
        public void mouseReleased(JDMouseEvent e) {
          if (fpTextView.isVisible()) {
            fpStr.append(((JDObject)e.getSource()).getName() + " mouseReleased()\n");
            fpText.setText(fpStr.toString());
          }
        }
        public void mouseClicked(JDMouseEvent e) {
          if (fpTextView.isVisible()) {
            fpStr.append(((JDObject)e.getSource()).getName() + " mouseClicked() clickCount="+e.getClickCount()+"\n");
            fpText.setText(fpStr.toString());
          }
        }
        public void mousePressed(JDMouseEvent e) {
          if (fpTextView.isVisible()) {
            fpStr.append(((JDObject)e.getSource()).getName() + " mousePressed()\n");
            fpText.setText(fpStr.toString());
          }
        }
        public void mouseEntered(JDMouseEvent e) {
          if (fpTextView.isVisible()) {
            fpStr.append(((JDObject)e.getSource()).getName() + " mouseEntered()\n");
            fpText.setText(fpStr.toString());
          }
        }
        public void mouseExited(JDMouseEvent e) {
          if (fpTextView.isVisible()) {
            fpStr.append(((JDObject)e.getSource()).getName() + " mouseExited()\n");
            fpText.setText(fpStr.toString());
          }
        }
      });
      */

    }
    thePlayer.initPlayer();
    thePlayer.computePreferredSize();
    Vector inter = thePlayer.getInteractiveObjects();
    for(i=0;i<inter.size();i++) {
      JDObject o = (JDObject)inter.get(i);
      fpStr.append(o.getName() + " has user value enabled.\n");
      o.addValueListener(this);
    }

    fpText.setText(fpStr.toString());
    ATKGraphicsUtils.centerFrameOnScreen(framePlayer);
    framePlayer.setVisible(true);
  }

  /** Ask to save if some modifications are still unsaved then exit the application. Called
   * when the file exit menu is selected or when the frame is closed */
  public void exitApp() {
    int rep = JOptionPane.YES_OPTION;
    if(theEditor.getNeedToSaveState()) {
      rep = JOptionPane.showConfirmDialog(this,"Your changes will be lost , save before exiting ?",
                                        "Exit confirmation",JOptionPane.YES_NO_CANCEL_OPTION);
      if(rep==JOptionPane.YES_OPTION)
        theEditor.instantSave(".");
    }
    if(rep!=JOptionPane.CANCEL_OPTION)
      System.exit(0);
  }

  protected void processWindowEvent(WindowEvent e) {
      if (e.getID() == WindowEvent.WINDOW_CLOSING) {
        exitApp();
      } else {
        super.processWindowEvent(e);
      }
  }

  /** Main function of the Jdraw editor. You can create yourself the editor in order
   * to customize it. Here is an example of a main function:<p>
   * <pre>
   * public static void main(String[] args) {
   *   final JDrawEditor ed = new JDrawEditor(JDrawEditor.MODE_EDIT);
   *   final JDrawEditor py = new JDrawEditor(JDrawEditor.MODE_PLAY);
   *   JDrawableList.addClass("myClass");
   *   final JDrawEditorFrame jde = new JDrawEditorFrame();
   *   jde.setAppTitle("My Editor");
   *   jde.setEditor(ed);
   *   jde.setPlayer(py);
   *   ATKGraphicsUtils.centerFrameOnScreen(jde);
   *   jde.setVisible(true);
   * }
   </pre>
   * @param args Filename to be loaded
   */
  public static void main(String[] args) {
	System.out.println("JDrawEditorFrame.main(...)");
    final JDrawEditor ed = new JDrawEditor(JDrawEditor.MODE_EDIT);
    final JDrawEditor py = new JDrawEditor(JDrawEditor.MODE_PLAY);
    final JDrawEditorFrame jde = new JDrawEditorFrame();
    //jde.setAppTitle("JDraw Editor 1.10");
    jde.setAppTitle("JDraw Editor 1.2, ALBA edition");
    jde.setEditor(ed);
    jde.setPlayer(py);
    jde.setLibraries(null);
    if(args.length==1) {
      System.out.println("Starting JDrawEditorFrame.main("+args[0]+")");
      try {
        ed.loadFile(args[0]);
      } catch (IOException e) {
        JOptionPane.showMessageDialog(null,"Error, cannot load " + args[0] + "\n" + e.getMessage(),
                                      "JDrawEditor",JOptionPane.ERROR_MESSAGE);
      }
    } else System.out.println("Starting JDrawEditorFrame.main( )");
    ATKGraphicsUtils.centerFrameOnScreen(jde);
    jde.setVisible(true);
  }

}
