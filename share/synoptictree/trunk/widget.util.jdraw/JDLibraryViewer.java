package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKConstant;
import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.KeyListener;
import java.io.IOException;

/** ******************************************************************************************************
srubio@cells.es, oktober 2006
The Class JDLibraryViewer has been modified to:
	- Use a contextual menu with options Copy and Exit
	- The foot panel is now an option
	- Emulate Drag&Drop behaviour linking Selection events to Paste commands in the parent editor
*********************************************************************************************************/

/**
 * Displays a JDraw file in a library view (only selection and clipboard operations allowed).
 * <p>Example of use: (This example shows how to create a custom editor and add
 * a component library)
 * <pre>
 * public class VacEdit extends JDrawEditorFrame {
 *
 *  private JButton libButton;
 *  private JDLibraryViewer libViewer;
 *  private JDrawEditor ed = new JDrawEditor(JDrawEditor.MODE_EDIT);
 *  private JDrawEditor py = new JDrawEditor(JDrawEditor.MODE_PLAY);
 *
 *public VacEdit() {
 *
 *  ed = new JDrawEditor(JDrawEditor.MODE_EDIT);
 *  py = new JDrawEditor(JDrawEditor.MODE_PLAY);
 *
 *  String libPath = System.getProperty("LIBPATH", "null");
 *  if( libPath.equals("null") )
 *   System.out.println("Warning LIBPATH is not defined.");
 *
 *  // Customize the editor
 *  libViewer = new JDLibraryViewer(libPath+"/jvacuum_lib.jdw",ed);
 *  libViewer.setTitle("ESRF vacuum library");
 *  ATKGraphicsUtils.centerFrameOnScreen(libViewer);
 *
 *  libButton = new JButton(new ImageIcon(getClass().getResource("/jvacuum/vac_button.gif")));
 *  libButton.setPressedIcon(new ImageIcon(getClass().getResource("/jvacuum/vac_button_push.gif")));
 *  libButton.setToolTipText("ESRF vacuum library");
 *  libButton.setMargin(new Insets(3,3,3,3));
 *  libButton.setBorder(null);
 *
 *  libButton.addActionListener(this);
 *  editToolBar.add(new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_separator.gif"))));
 *  editToolBar.add(libButton);
 *
 *  setAppTitle("JVacuum Editor 1.0");
 *  setEditor(ed);
 *  setPlayer(py);
 *
 *}
 *
 *public void actionPerformed(ActionEvent e) {
 *
 *  Object src = e.getSource();
 *  if( src== libButton ) {
 *    libViewer.setVisible(true);
 *  } else {
 *    super.actionPerformed(e);
 *  }
 *
 *}
 *
 *
 *public static void main(String[] args) {
 *
 *  VacEdit v = new VacEdit();
 *  ATKGraphicsUtils.centerFrameOnScreen(v);
 *  v.setVisible(true);
 *
 *}
 *
 *}
 * </pre>
 */
public class JDLibraryViewer extends JFrame implements ActionListener, JDrawEditorListener//, KeyListener 
{

  JDrawEditor libViewer;
  JDrawEditor invoker;
  JPanel      controlPanel;
  JButton     copyButton;
  JButton     closeButton;
  
  JMenuItem copyMenuItem;
  JMenuItem exitMenuItem;
  
  public JDLibraryViewer(String libName,JDrawEditor invoker) {
	  initComponents(libName, invoker, true);
  }
  
  public JDLibraryViewer(String libName,JDrawEditor invoker, boolean lPanel) {
	  initComponents(libName,invoker,lPanel);
  }
  
  public void initComponents(String libName,JDrawEditor invoker, boolean lPanel) {
    this.invoker = invoker;
    Container pane = getContentPane();

    pane.setLayout(new BorderLayout());

    // Library view
    libViewer = new JDrawEditor(JDrawEditor.MODE_LIB);
    try {
      libViewer.loadFile(libName);
    } catch(IOException e) {
      System.out.println("Cannot load library:\n" + e.getMessage());
    }
    libViewer.computePreferredSize();
    libViewer.setBorder(BorderFactory.createEtchedBorder());
    pane.add(libViewer,BorderLayout.CENTER);

    if (lPanel) {
	    // Control panel
	    controlPanel=new JPanel();
	    copyButton=new JButton("Copy");
	    copyButton.setFont(ATKConstant.labelFont);
	    copyButton.setMnemonic(java.awt.event.KeyEvent.VK_C);
	    copyButton.addActionListener(this);    
	    closeButton=new JButton("Close");
	    closeButton.setFont(ATKConstant.labelFont);
	    closeButton.setMnemonic(java.awt.event.KeyEvent.VK_L);
	    closeButton.addActionListener(this);    
	    controlPanel.add(copyButton);
	    controlPanel.add(closeButton);
	    pane.add(controlPanel,BorderLayout.SOUTH);
    }
    
    copyMenuItem = new JMenuItem("Copy");
    //copyMenuItem.setAccelerator(KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_C,java.awt.event.InputEvent.CTRL_MASK));
    copyMenuItem.addActionListener(this);
    //copyMenuItem.fireActionPerformed(new java.awt.event.ActionEvent(copyMenuItem,java.awt.event.ACTION_PERFORMED,"Copy"));
        
    exitMenuItem = new JMenuItem("Exit");
    //exitMenuItem.setAccelerator(KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_ESCAPE,0));
    exitMenuItem.addActionListener(this);
    libViewer.addToMenu(copyMenuItem);
    libViewer.addToMenu(exitMenuItem);
    
    libViewer.addEditorListener(this);
  }

  public void actionPerformed(ActionEvent e) {

    Object src = e.getSource();
    if( src == closeButton || src == exitMenuItem ) {
      setVisible(false);
    } else if (src == copyButton || src == copyMenuItem ) {
      if(invoker!=null)
        invoker.addObjectToClipboard(libViewer.getSelectedObjects());
    }

  }
  
  public void selectionChanged() {
	  if (libViewer.getSelectionLength()>0) {
		  invoker.addObjectToClipboard(libViewer.getSelectedObjects());
		  invoker.create(JDrawEditor.CREATE_CLIPBOARD);
	  }
  }
  
  public void sizeChanged() {}
  public void clipboardChanged() {}
  public void valueChanged() {}
  public void creationDone() {}

  public static void main(String[] args) {

    JDLibraryViewer libView = new JDLibraryViewer(
            "Z:/segfs/blcdas/appli/vacuum/xvacuum/LOOX_files/Lib_Xvacuum.g",
            null);
    libView.setTitle("ESRF Vacuum Library");
    libView.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    ATKGraphicsUtils.centerFrameOnScreen(libView);
    libView.setVisible(true);

  }

}
