package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import java.util.Vector;
import java.awt.*;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ComponentEvent;

class JDUtils {

  static boolean modified;
  private static Insets bMargin = new Insets(3,3,3,3);
  static Insets zMargin = new Insets(0, 0, 0, 0);
  private static Class theClass=null;
  static Font  labelFont  = new Font("Dialog", Font.PLAIN, 12);
  static Font  labelFontBold  = new Font("Dialog", Font.BOLD, 12);
  static Color labelColor = new Color(85, 87, 140);

  // For non modal property window
  private static JDialog               nonModalPropDlg=null;
  private static JDrawEditor           lastInvoker=null;
  private static Component             lastSelectedPanel=null;
  private static boolean               updatingProp=false;
  private static JTabbedPane           innerPane = null;
  private static JDObjectPanel         objectPanel=null;
  private static JDLabelPanel          labelPanel=null;
  private static JDLinePanel           linePanel=null;
  private static JDPolylinePanel       polylinePanel=null;
  private static JDEllipsePanel        ellipsePanel=null;
  private static JDRoundRectanglePanel roundRectanglePanel=null;
  private static JDImagePanel          imagePanel=null;
  private static JDSwingPanel          swingPanel=null;
  private static JDAxisPanel           axisPanel=null;
  private static JDBarPanel            barPanel=null;
  private static JDSliderPanel         sliderPanel=null;
  private static JDValuePanel          valuePanel=null;
  private static JDExtensionPanel      extensionPanel=null;

  static private void init() {
    if( theClass==null ) {
      String className = "fr.esrf.tangoatk.widget.util.jdraw.JDUtils";
      try {
        theClass = Class.forName(className);
      } catch (Exception e) {
        System.out.println("JDUtils.init() Class not found: " + className);
      }
    }
  }

  static private JDialog buildDialog(JComponent invoker,boolean modal) {

    Object parent = invoker.getRootPane().getParent();
    JDialog dlg;

    if (parent instanceof JDialog) {
      dlg = new JDialog((JDialog) parent, modal);
    } else if (parent instanceof JFrame) {
      dlg = new JDialog((JFrame) parent, modal);
    } else {
      dlg = new JDialog((JFrame) null, modal);
    }

    return dlg;

  }

  static private JDialog buildModalDialog(JComponent invoker) {
    return buildDialog(invoker,true);
  }

  static public void updatePropertyDialog(Vector objects) {

    if(nonModalPropDlg==null)
      return;

    if(objects.size()==0) {
      nonModalPropDlg.setTitle("Properties [None selected]");
      objectPanel.updatePanel(null);
      labelPanel.updatePanel(null);
      linePanel.updatePanel(null);
      polylinePanel.updatePanel(null);
      ellipsePanel.updatePanel(null);
      roundRectanglePanel.updatePanel(null);
      imagePanel.updatePanel(null);
      swingPanel.updatePanel(null);
      axisPanel.updatePanel(null);
      barPanel.updatePanel(null);
      valuePanel.updatePanel(null);
      extensionPanel.updatePanel(null);
      return;
    }

    updatingProp = true;

    // Check object instance and make object array
    JDObject[] objs = new JDObject[objects.size()];
    boolean sameClass = true;
    int i = 1;
    objs[0] = (JDObject) objects.get(0);
    Class firstClass = objs[0].getClass();
    for (i = 1; i < objs.length; i++) {
      objs[i] = (JDObject) objects.get(i);
      sameClass &= firstClass.equals(objs[i].getClass());
    }

    innerPane.removeAll();
    innerPane.add(objectPanel,"Graphics");
    objectPanel.updatePanel(objs);

    // Specific properties
    if (sameClass && objs[0] instanceof JDLabel) {
      JDLabel[] objs2 = new JDLabel[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDLabel) objs[i];
      labelPanel.updatePanel(objs2);
      innerPane.add(labelPanel, "Text");
    }

    if (sameClass && objs[0] instanceof JDLine) {
      JDLine[] objs2 = new JDLine[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDLine) objs[i];
      linePanel.updatePanel(objs2);
      innerPane.add(linePanel, "Line");
    }

    if (sameClass && objs[0] instanceof JDPolyline) {
      JDPolyline[] objs2 = new JDPolyline[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDPolyline) objs[i];
      polylinePanel.updatePanel(objs2);
      innerPane.add(polylinePanel, "Polyline");
    }

    if (sameClass && objs[0] instanceof JDEllipse) {
      JDEllipse[] objs2 = new JDEllipse[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDEllipse) objs[i];
      ellipsePanel.updatePanel(objs2);
      innerPane.add(ellipsePanel, "Ellipse");
    }

    if (sameClass && objs[0] instanceof JDRoundRectangle) {
      JDRoundRectangle[] objs2 = new JDRoundRectangle[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDRoundRectangle) objs[i];
      roundRectanglePanel.updatePanel(objs2);
      innerPane.add(roundRectanglePanel, "Corner");
    }

    if (sameClass && objs[0] instanceof JDImage) {
      JDImage[] objs2 = new JDImage[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDImage) objs[i];
      imagePanel.updatePanel(objs2);
      innerPane.add(imagePanel, "Image");
    }

    if (sameClass && objs[0] instanceof JDSwingObject) {
      JDSwingObject[] objs2 = new JDSwingObject[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDSwingObject) objs[i];
      swingPanel.updatePanel(objs2);
      innerPane.add(swingPanel, "Swing");
    }

    if (sameClass && objs[0] instanceof JDAxis) {
      JDAxis[] objs2 = new JDAxis[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDAxis) objs[i];
      axisPanel.updatePanel(objs2);
      innerPane.add(axisPanel, "Axis");
    }

    if (sameClass && objs[0] instanceof JDBar) {
      JDBar[] objs2 = new JDBar[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDBar) objs[i];
      barPanel.updatePanel(objs2);
      innerPane.add(barPanel, "Bar");
    }

    if (sameClass && objs[0] instanceof JDSlider) {
      JDSlider[] objs2 = new JDSlider[objs.length];
      for (i = 0; i < objs.length; i++) objs2[i] = (JDSlider) objs[i];
      sliderPanel.updatePanel(objs2);
      innerPane.add(sliderPanel, "Slider");
    }

    // Dynamic properties
    valuePanel.updatePanel(objs);
    innerPane.add(valuePanel, "Value");
    extensionPanel.updatePanel(objs);
    innerPane.add(extensionPanel, "Extensions");

    String title = "Properties";
    JDObject p = (JDObject) objects.get(0);
    if (sameClass) title += " [" + objects.size() + " " + p.toString() + " selected]";
    else           title += " [" + objects.size() + " objects selected]";
    nonModalPropDlg.setTitle(title);

    // Reselect last panel if possible
    try {
      innerPane.setSelectedComponent(lastSelectedPanel);
    } catch (IllegalArgumentException e) {}

    // Work around a X11 JVM bug
    innerPane.getSelectedComponent().setVisible(true);

    updatingProp = false;

  }

  static public void showPropertyDialog(JDrawEditor invoker,Vector objects) {

    if(nonModalPropDlg!=null ) {
      if( lastInvoker!=invoker ) {
        // We need to reconstruct the dialog
        nonModalPropDlg.dispose();
        nonModalPropDlg = null;
      }
    }

    if(nonModalPropDlg==null ) {

      // Construct the dialog
      nonModalPropDlg = buildDialog(invoker,false);
      lastInvoker = invoker;

      // Create panel
      JPanel innerPanel = new JPanel();
      innerPanel.setLayout(new BorderLayout());

      JPanel buttonPanel= new JPanel();
      FlowLayout fl = new FlowLayout();
      fl.setAlignment(FlowLayout.RIGHT);
      buttonPanel.setLayout(fl);

      JButton dismissBtn = new JButton("Dismiss");
      dismissBtn.setFont(labelFont);
      dismissBtn.addActionListener(new ActionListener() {
        public void actionPerformed(ActionEvent e) {
          nonModalPropDlg.setVisible(false);
        }
      });
      buttonPanel.add(dismissBtn);
      innerPanel.add(buttonPanel,BorderLayout.SOUTH);

      // Tabbed pane
      innerPane = new JTabbedPane();
      objectPanel = new JDObjectPanel(null, invoker, null);
      labelPanel = new JDLabelPanel(null, invoker);
      linePanel = new JDLinePanel(null, invoker);
      polylinePanel = new JDPolylinePanel(null, invoker);
      ellipsePanel = new JDEllipsePanel(null, invoker);
      roundRectanglePanel = new JDRoundRectanglePanel(null, invoker);
      imagePanel = new JDImagePanel(null, invoker);
      swingPanel = new JDSwingPanel(null, invoker);
      axisPanel = new JDAxisPanel(null, invoker);
      barPanel = new JDBarPanel(null, invoker);
      sliderPanel = new JDSliderPanel(null, invoker);
      valuePanel = new JDValuePanel(null, invoker, null);
      extensionPanel = new JDExtensionPanel(null, invoker);

      innerPanel.add(innerPane,BorderLayout.CENTER);
      nonModalPropDlg.setContentPane(innerPanel);
      nonModalPropDlg.setResizable(false);

      innerPane.addChangeListener(new ChangeListener() {
        public void stateChanged(ChangeEvent e) {
          if(innerPane.getSelectedComponent()!=null && !updatingProp) {
            lastSelectedPanel = innerPane.getSelectedComponent();
          }
        }
      });

    }

    updatePropertyDialog(objects);

    // Recenter on show
    if (!nonModalPropDlg.isVisible())
      ATKGraphicsUtils.centerDialog(nonModalPropDlg);

    nonModalPropDlg.setVisible(true);

  }

  static public boolean showBrowserDialog(JDrawEditor invoker, Vector objects) {

    if (objects.size() == 0)
      return false;

    if(nonModalPropDlg!=null)
      nonModalPropDlg.setVisible(false);

    JDialog propDlg = buildModalDialog(invoker);

    // Set the browser panel
    JDObject[] objs = new JDObject[objects.size()];
    for(int i=0;i<objs.length;i++) objs[i]=(JDObject)objects.get(i);
    JDBrowserPanel bp = new JDBrowserPanel(objs, invoker);
    propDlg.setContentPane(bp);
    bp.postInit();
    ATKGraphicsUtils.centerDialog(propDlg);

    // Set minimum dialog size
    propDlg.addComponentListener(new ComponentListener() {
      public void componentResized(ComponentEvent e) {
        JDialog dlg = (JDialog)e.getSource();
        dlg.setSize(
              Math.max(460, dlg.getWidth()),
              Math.max(400, dlg.getHeight()));
      }
      public void componentMoved(ComponentEvent e) {}
      public void componentShown(ComponentEvent e) {}
      public void componentHidden(ComponentEvent e) {}

    });

    modified=false;
    propDlg.setVisible(true);
    propDlg.dispose();

    // Rebuild old selection
    invoker.unselectAll();
    invoker.selectObjects(objs);
    invoker.fireSelectionChange();

    return modified;

  }

  static public boolean showGroupEditorDialog(JDrawEditor invoker, JDGroup g) {

    if(nonModalPropDlg!=null)
      nonModalPropDlg.setVisible(false);

    JDialog propDlg = buildModalDialog(invoker);
    JDGroupEditorView gEdit = new JDGroupEditorView(g, invoker);
    propDlg.setContentPane(gEdit);
    propDlg.setTitle("Group Editor [" + g.getName() + "]");
    propDlg.setResizable(true);
    ATKGraphicsUtils.centerDialog(propDlg);
    propDlg.setVisible(true);
    propDlg.dispose();
    return modified;

  }

  static public boolean showTransformDialog(JComponent invoker, Vector objects) {

    if (objects.size() == 0)
      return false;

    if(nonModalPropDlg!=null)
      nonModalPropDlg.setVisible(false);

    JDialog propDlg = buildModalDialog(invoker);

    JDObject[] objs = new JDObject[objects.size()];
    for (int i = 0; i < objs.length; i++)
      objs[i] = (JDObject) objects.get(i);
    // Transform properties
    propDlg.setContentPane(new JDTransformPanel(objs, invoker));

    String title = "Transformation";
    JDObject p = (JDObject) objects.get(0);
    if (objects.size() == 1) title += ": " + p.getName();
    propDlg.setTitle(title);
    ATKGraphicsUtils.centerDialog(propDlg);
    propDlg.setResizable(false);

    modified=false;
    propDlg.setVisible(true);
    propDlg.dispose();
    return modified;

  }

  static public boolean showGlobalDialog(JDrawEditor invoker) {

    if(nonModalPropDlg!=null)
      nonModalPropDlg.setVisible(false);

    JDialog propDlg = buildModalDialog(invoker);

    // Transform properties
    propDlg.setContentPane(new JDGlobalPanel(invoker));

    String title = "Global graph properties";
    propDlg.setTitle(title);
    ATKGraphicsUtils.centerDialog(propDlg);
    propDlg.setResizable(false);

    modified=false;
    propDlg.setVisible(true);
    propDlg.dispose();
    return modified;

  }

  static public JDValueProgram showValueMappingDialog(JComponent invoker, JDObject[] objs,String desc,int type,JDValueProgram defMapper) {

    if (objs.length == 0)
      return null;

    JDialog propDlg = buildModalDialog(invoker);
    JDValueMappingPanel vp = new JDValueMappingPanel(objs, invoker,desc,type,defMapper);

    // Transform properties
    propDlg.setContentPane(vp);

    String title = "Mapping for " + desc;
    title += " [" + objs.length + " objects selected]";
    propDlg.setTitle(title);
    ATKGraphicsUtils.centerDialog(propDlg);
    propDlg.setResizable(false);
    propDlg.setVisible(true);
    propDlg.dispose();
    if(vp.hasChanged())
      return vp.getMapper();
    else
      return null;
  }

  static boolean showBooleanDialog(JComponent invoker,String name,boolean defaultValue) {

    JDialog propDlg = buildModalDialog(invoker);
    JPanel panel = new JPanel();
    panel.setLayout(null);
    JComboBox boolCombo = new JComboBox();
    boolCombo.setFont(labelFont);
    boolCombo.addItem("False");
    boolCombo.addItem("True");
    boolCombo.setSelectedIndex(defaultValue?1:0);
    panel.add(boolCombo);
    boolCombo.setBounds(10,10,150,25);
    panel.setPreferredSize(new Dimension(170,40));
    propDlg.setContentPane(panel);
    propDlg.setTitle(name);
    ATKGraphicsUtils.centerDialog(propDlg);
    propDlg.setVisible(true);
    propDlg.dispose();
    return (boolCombo.getSelectedIndex()==1);

  }

  static int showIntegerDialog(JComponent invoker,String name,int defaultValue) {
    String str = JOptionPane.showInputDialog(invoker, "Integer value", name, JOptionPane.INFORMATION_MESSAGE);
    int ret = defaultValue;
    if (str != null) {
      try {
        ret = Integer.parseInt(str);
      } catch (Exception e) {
      }
    }
    return ret;
  }

  static public boolean isJDPolyConvertible(JDObject obj) {
	if (!(obj instanceof JDPolyConvert)) return false;
	if (!(obj instanceof JDGroup)) return true;
	if (((JDGroup)obj).isPolyConvertible()) return true;
	return false;
  }

  static public boolean isJDObjectRotable(JDObject obj) {
	if (!(obj instanceof JDRotatable)) return false;
	if (!(obj instanceof JDGroup)) return true;
	if (((JDGroup)obj).isRotable()) return true;
	return false;
  }

  static public Point getTopLeftCorner(JDObject[] list) {
    // Compute scaling origin
    int xOrg = 65536;
    int yOrg = 65536;
    Rectangle r;
    for (int i = 0; i < list.length; i++) {
      r = list[i].getBoundRect();
      if (r.x < xOrg) xOrg = r.x;
      if (r.y < yOrg) yOrg = r.y;
    }
    return new Point(xOrg, yOrg);
  }

  static public Point getTopLeftCorner(Vector list) {
    // Compute scaling origin
    int xOrg = 65536;
    int yOrg = 65536;
    Rectangle r;
    for (int i = 0; i < list.size(); i++) {
      r = ((JDObject) list.get(i)).getBoundRect();
      if (r.x < xOrg) xOrg = r.x;
      if (r.y < yOrg) yOrg = r.y;
    }
    return new Point(xOrg, yOrg);
  }

  static public Point getCenter(Vector list) {
    // Compute scaling origin
    Rectangle r;
    int x1 = 65536;
    int y1 = 65536;
    int x2 = -65536;
    int y2 = -65536;
    for (int i = 0; i < list.size(); i++) {
      r = ((JDObject) list.get(i)).getBoundRect();
      if (r.x < x1) x1 = r.x;
      if (r.x + r.width > x2) x2 = r.x + r.width;
      if (r.y < y1) y1 = r.y;
      if (r.y + r.height > y2) y2 = r.y + r.height;
    }
    return new Point((x1 + x2) / 2, (y1 + y2) / 2);
  }

  static public Point getCenter(JDObject[] list) {
    // Compute scaling origin
    Rectangle r;
    int x1 = 65536;
    int y1 = 65536;
    int x2 = -65536;
    int y2 = -65536;
    for (int i = 0; i < list.length; i++) {
      r = list[i].getBoundRect();
      if (r.x < x1) x1 = r.x;
      if (r.x + r.width > x2) x2 = r.x + r.width;
      if (r.y < y1) y1 = r.y;
      if (r.y + r.height > y2) y2 = r.y + r.height;
    }
    return new Point((x1 + x2) / 2, (y1 + y2) / 2);
  }

  static public Point getBottomRightCorner(Vector list) {
    // Compute origin
    int xOrg = -65536;
    int yOrg = -65536;
    Rectangle r;
    for (int i = 0; i < list.size(); i++) {
      r = ((JDObject) list.get(i)).getBoundRect();
      if (r.x+r.width  > xOrg) xOrg = r.x+r.width;
      if (r.y+r.height > yOrg) yOrg = r.y+r.height;
    }
    return new Point(xOrg, yOrg);

  }

  static public JButton createIconButton(String name,boolean hasDisa,String tipText,ActionListener l) {
    init();
    if( theClass!=null ) {
      JButton nB = new JButton(new ImageIcon(theClass.getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/" + name + ".gif")));
      nB.setPressedIcon(new ImageIcon(theClass.getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/" + name + "_push.gif")));
      if (hasDisa)
        nB.setDisabledIcon(new ImageIcon(theClass.getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/" + name + "_disa.gif")));
      nB.setToolTipText(tipText);
      nB.setMargin(bMargin);
      nB.setBorder(null);
      nB.addActionListener(l);
      return nB;
    } else {
      return new JButton(name);
    }
  }

  static public JButton createSetButton(ActionListener l) {
    JButton b = new JButton("...");
    b.setMargin(zMargin);
    b.setForeground(Color.BLACK);
    if(l!=null) b.addActionListener(l);
    return b;
  }

  static public JLabel createLabel(String name) {
    JLabel ret = new JLabel(name);
    ret.setFont(labelFont);
    ret.setForeground(labelColor);
    return ret;
  }

  static public Border createTitleBorder(String name) {
    return BorderFactory.createTitledBorder(BorderFactory.createEtchedBorder(), name,
                                            TitledBorder.LEFT, TitledBorder.DEFAULT_POSITION,
                                            labelFontBold, labelColor);
  }

  static public JCheckBox createCheckBox(String name,ActionListener l) {
    JCheckBox cb = new JCheckBox(name);
    cb.setFont(labelFont);
    cb.setForeground(labelColor);
    if(l!=null) cb.addActionListener(l);
    return cb;
  }

  static String buildFontName(Font f) {
    String name = f.getName();
    String size = Integer.toString(f.getSize());
    String style = "";
    switch(f.getStyle()) {
      case Font.PLAIN:
        style="Plain";
        break;
      case Font.ITALIC:
        style="Italic";
        break;
      case Font.BOLD:
        style="Bold";
        break;
      case Font.BOLD+Font.ITALIC:
        style="Italic Bold";
        break;
    }
    return name + "," + style + "," + size;
  }

  static String[] makeStringArray(String value) {
    // Remove extra \n at the end of the string (not handled by split)
    while (value.endsWith("\n")) value = value.substring(0, value.length() - 1);
    return value.split("\n");
  }

  static String buildShortClassName(String className) {
    if(className==null)
      return "";    
    int i = className.lastIndexOf('.');
    if(i!=-1) {
      return className.substring(i+1);
    } else {
      return className;
    }
  }

  static void computeSpline(double x1,double y1,double x2,double y2,
                            double x3,double y3,double x4,double y4,
                            int step,boolean full,int start,
                            Vector pts,int[] ptsx,int[] ptsy) {

    double k,ks,kc;
    int j;
    double x,y;

    //************************
    // Compute the spline
    //************************

    double stp = 1.0 / (double) step;
    k = 0;
    j = 0;

    while (j <= step) {
      ks = k * k;
      kc = ks * k;

      x = (1.0 - 3.0 * k + 3.0 * ks - kc) * x1
              + 3.0 * (k - 2.0 * ks + kc) * x2
              + 3.0 * (ks - kc) * x3
              + kc * x4;

      y = (1.0 - 3.0 * k + 3.0 * ks - kc) * y1
              + 3.0 * (k - 2.0 * ks + kc) * y2
              + 3.0 * (ks - kc) * y3
              + kc * y4;

      // Don't forget the last point
      if((full) || (j < step)) {
        if(pts!=null) {
          double[] pt = new double[2];
          pt[0] = (int)(x+0.5);
          pt[1] = (int)(y+0.5);
          pts.add(pt);
        } else {
          ptsx[start+j] = (int)(x+0.5);
          ptsy[start+j] = (int)(y+0.5);
        }
      }

      k = k + stp;
      j++;
    }

  }

}
