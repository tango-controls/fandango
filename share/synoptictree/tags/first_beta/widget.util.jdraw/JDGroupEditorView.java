/** A JDGroup editor */
package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.InputEvent;

class JDGroupEditor extends JDrawEditor {

  JDGroupEditor() {
    super(JDrawEditor.MODE_EDIT_GROUP);
  }

}

class JDGroupEditorView extends JComponent implements JDrawEditorListener,ActionListener {

  JDGroup       theGroup;
  JDrawEditor   invoker;
  JDGroupEditor theEditor;
  JScrollPane   theEditorView;
  Rectangle     oldRect;

  JMenuBar   menuBar;

  /* File menu */
  JMenu      fileMenu;
  JMenuItem  exitMenuItem;

  /** Create menu */
  JDCreationMenu creationMenu;

  /* Edit menu */
  JMenu     editMenu;
  JMenuItem editCutMenuItem;
  JMenuItem editCopyMenuItem;
  JMenuItem editPasteMenuItem;
  JMenuItem editDeleteMenuItem;
  JMenuItem editSelectAllMenuItem;
  JMenuItem editSelectNoneMenuItem;

  /* Views menu */
  JMenu     viewsMenu;
  JMenuItem viewsOptionMenuItem;
  JMenuItem viewsGroupEditMenuItem;

  /** Tools menu */
  JMenu     toolsMenu;
  JMenuItem toolsHMirrorMenuItem;
  JMenuItem toolsVMirrorMenuItem;
  JMenuItem toolsAligntopMenuItem;
  JMenuItem toolsAlignleftMenuItem;
  JMenuItem toolsAlignbottomMenuItem;
  JMenuItem toolsAlignrightMenuItem;
  JMenuItem toolsRaiseMenuItem;
  JMenuItem toolsLowerMenuItem;
  JMenuItem toolsFrontMenuItem;
  JMenuItem toolsBackMenuItem;
  JMenuItem toolsConvertPolyMenuItem;
  JCheckBoxMenuItem toolsGridVisible;
  JCheckBoxMenuItem toolsAlignToGrid;
  JMenuItem toolsGridSettings;
  JMenuItem toolsFitToGraph;

  public JDGroupEditorView(JDGroup g, JDrawEditor jc) {

    int margin=20;
    int i;
    theGroup = g;
    invoker = jc;
    oldRect = g.getRepaintRect();
    setLayout(new BorderLayout());

    // Create the editor
    theEditor = new JDGroupEditor();
    Rectangle r = g.getBoundRect();
    theEditor.addEditorListener(this);
    int gSize = jc.getGridSize();
    theEditor.setTranslation(round(-r.x + margin,gSize) ,round(-r.y + margin,gSize));
    theEditor.setPreferredSize(new Dimension(r.width+2*margin,r.height+2*margin));

    for(i=0;i<g.getChildrenNumber();i++)
      theEditor.addObject(g.getChildAt(i));

    theEditorView = new JScrollPane(theEditor);
    add(theEditorView,BorderLayout.CENTER);

    theEditor.setZoomFactor(invoker.getZoomFactor());

    // --- toolbar
    creationMenu = new JDCreationMenu();
    creationMenu.setEditor(theEditor);
    add(creationMenu.getToolbar(),BorderLayout.WEST);

    // -----------------------------
    JMenuBar  menuBar = new JMenuBar();

    JMenu     fileMenu = new JMenu("File");
    fileMenu.setMnemonic('E');
    menuBar.add(fileMenu);

    exitMenuItem = new JMenuItem("Close");
    exitMenuItem.addActionListener(this);
    fileMenu.add(exitMenuItem);

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
    editMenu.add(new JSeparator());
    editMenu.add(editCutMenuItem);
    editMenu.add(editCopyMenuItem);
    editMenu.add(editPasteMenuItem);
    editMenu.add(editDeleteMenuItem);
    editMenu.add(new JSeparator());
    editMenu.add(editSelectAllMenuItem);
    editMenu.add(editSelectNoneMenuItem);

    menuBar.add(editMenu);
    menuBar.add(creationMenu.getMenu());

    viewsOptionMenuItem = new JMenuItem("Object properties...");
    viewsOptionMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_P,InputEvent.CTRL_MASK));
    viewsOptionMenuItem.addActionListener(this);
    viewsGroupEditMenuItem = new JMenuItem("Group editor...");
    viewsGroupEditMenuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_G,InputEvent.CTRL_MASK));
    viewsGroupEditMenuItem.addActionListener(this);

    viewsMenu = new JMenu("Views");
    viewsMenu.setMnemonic('V');
    viewsMenu.add(viewsOptionMenuItem);
    viewsMenu.add(viewsGroupEditMenuItem);

    menuBar.add(viewsMenu);

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

    menuBar.add(toolsMenu);

    add(menuBar,BorderLayout.NORTH);

    // Copy clipboard
    theEditor.setClipboard(invoker.getClipboardObjects());

    // Update controls
    selectionChanged();
    valueChanged();
    clipboardChanged();
  }

  // ---------------------------------------------------------
  private int round(int value,int prec) {
    return (value / prec) * prec;
  }

  // ---------------------------------------------------------

  public void creationDone() {}

  public void selectionChanged() {

    int sz = theEditor.getSelectionLength();

    editCutMenuItem.setEnabled(sz>0);
    editCopyMenuItem.setEnabled(sz>0);
    editPasteMenuItem.setEnabled(theEditor.getClipboardLength()>0);
    editDeleteMenuItem.setEnabled(sz>0);
    editSelectAllMenuItem.setEnabled(sz<theEditor.getObjectNumber());
    editSelectNoneMenuItem.setEnabled(sz>0);

    viewsGroupEditMenuItem.setEnabled(theEditor.canEditGroup());
    viewsOptionMenuItem.setEnabled(sz>0);

    toolsHMirrorMenuItem.setEnabled(sz>0);
    toolsVMirrorMenuItem.setEnabled(sz>0);
    toolsAlignleftMenuItem.setEnabled(sz>1);
    toolsAligntopMenuItem.setEnabled(sz>1);
    toolsAlignrightMenuItem.setEnabled(sz>1);
    toolsAlignbottomMenuItem.setEnabled(sz>1);
    toolsConvertPolyMenuItem.setEnabled(theEditor.canConvertToPolyline());
    toolsRaiseMenuItem.setEnabled((sz == 1));
    toolsLowerMenuItem.setEnabled((sz == 1));
    toolsFrontMenuItem.setEnabled((sz >= 1));
    toolsBackMenuItem.setEnabled((sz >= 1));
    toolsAlignToGrid.setSelected(theEditor.isAlignToGrid());
    toolsGridVisible.setSelected(theEditor.isGridVisible());

  }

  public void clipboardChanged() {
    int sz=theEditor.getClipboardLength();
    editPasteMenuItem.setEnabled(sz>0);
  }

  public void valueChanged() {
    rebuildGroup();
  }

  public void sizeChanged() {
    theEditorView.revalidate();
    repaint();
  }

  // ---------------------------------------------------------

  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    if (src==editCutMenuItem) {
      theEditor.cutSelection();
    } else if (src==editCopyMenuItem) {
      theEditor.copySelection();
    } else if (src==editPasteMenuItem) {
      Point p = JDUtils.getTopLeftCorner(theEditor.getClipboardObjects());
      theEditor.pasteClipboard(p.x+30, p.y+30);
    } else if (src==editDeleteMenuItem) {
      theEditor.deleteSelection();
    } else if (src==editSelectAllMenuItem) {
      theEditor.selectAll();
    } else if (src==editSelectNoneMenuItem) {
      theEditor.unselectAll();
    } else if (src==exitMenuItem) {
      ATKGraphicsUtils.getWindowForComponent(this).setVisible(false);
      invoker.setClipboard(theEditor.getClipboardObjects());
      invoker.fireClipboardChange();
    } else if (src==viewsOptionMenuItem) {
      theEditor.showPropertyWindow();
    } else if (src == viewsGroupEditMenuItem) {
      theEditor.showGroupEditorWindow();
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
    } else if (src==toolsHMirrorMenuItem) {
      theEditor.scaleSelection(-1.0,1.0);
    } else if (src==toolsVMirrorMenuItem) {
      theEditor.scaleSelection( 1.0,-1.0);
    } else if (src==toolsAligntopMenuItem) {
      theEditor.aligntopSelection();
    } else if (src==toolsAlignleftMenuItem) {
      theEditor.alignleftSelection();
    } else if (src==toolsAlignbottomMenuItem) {
      theEditor.alignbottomSelection();
    }  else if (src==toolsAlignrightMenuItem) {
      theEditor.alignrightSelection();
    }

  }

  // ---------------------------------------------------------
  private void rebuildGroup() {
     // Rebuild the group
     theGroup.setChildrenList(theEditor.getObjects());
     Rectangle r = theGroup.getRepaintRect();
     invoker.repaint(oldRect.union(r));
     // Trigger the parent valueChanged
     invoker.fireValueChanged();
     oldRect=r;
     JDUtils.modified=true;
  }

}
