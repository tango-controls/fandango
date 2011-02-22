/*
 * TangoTreeNodeCellRenderer.java
 *
 */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.tree.DefaultTreeCellRenderer;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.geom.Rectangle2D;
import java.awt.font.FontRenderContext;

class MasterNodeRenderer extends JComponent {

  String str1;
  String str2;
  Dimension pSize;
  int p1,p2;
  int hText;
  ImageIcon icon;
  static BufferedImage dummy = new BufferedImage(10,10,BufferedImage.TYPE_INT_RGB);

  MasterNodeRenderer() {
    pSize = new Dimension(10,18);
  }

  public void setValues(ImageIcon icon,String s1,String s2) {
    str1 = s1;
    str2 = s2;
    this.icon = icon;
    Graphics2D g2 = (Graphics2D)dummy.getGraphics();
    FontRenderContext frc = g2.getFontRenderContext();
    g2.setRenderingHint(RenderingHints.KEY_FRACTIONALMETRICS,
                        RenderingHints.VALUE_FRACTIONALMETRICS_ON);
    Rectangle2D b1 = JDUtils.labelFontBold.getStringBounds(s1,frc);
    Rectangle2D b2 = JDUtils.labelFont.getStringBounds(s2,frc);
    p1 = icon.getIconWidth() + 3;
    p2 = icon.getIconWidth() + (int)(b1.getWidth()+0.5) + 6;
    if(s2.length()>0) {
      pSize.width = p2 + (int)(b2.getWidth()+0.5) + 2;
    } else {
      pSize.width = p2;      
    }
    pSize.height = icon.getIconHeight();
    hText = (int)(b1.getHeight()*0.333 + icon.getIconHeight()*0.5);
  }

  public Dimension getPreferredSize() {
    return pSize;
  }

  public Dimension getMinimumSize() {
    return getPreferredSize();
  }

  public void paint(Graphics g) {
    Dimension sz = getSize();
    g.setColor(getBackground());
    g.fillRect(0,0,sz.width,sz.height);
    g.drawImage(icon.getImage(),0,0,null);

    // Center texts
    g.setColor(Color.black);
    g.setFont(JDUtils.labelFontBold);
    g.drawString(str1,p1,hText);
    g.setFont(JDUtils.labelFont);
    g.drawString(str2,p2,hText);
  }


}

class JDTreeNodeRenderer extends DefaultTreeCellRenderer {

  ImageIcon lineIcon;
  ImageIcon polyIcon;
  ImageIcon rectangleIcon;
  ImageIcon ellipseIcon;
  ImageIcon labelIcon;
  ImageIcon splineIcon;
  ImageIcon groupIcon;
  ImageIcon rrectangleIcon;
  ImageIcon imgIcon;
  ImageIcon swgIcon;
  ImageIcon axisIcon;
  ImageIcon barIcon;
  ImageIcon sliderIcon;
  MasterNodeRenderer renderMaster;

  private static Color selColor = new Color(204,204,255);

  public JDTreeNodeRenderer() {
    lineIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_line_icon.gif"));
    rectangleIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_rectangle_icon.gif"));
    rrectangleIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_rrectangle_icon.gif"));
    ellipseIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_ellipse_icon.gif"));
    labelIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_label_icon.gif"));
    polyIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_polyline_icon.gif"));
    splineIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_spline_icon.gif"));
    groupIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_group_icon.gif"));
    imgIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_image_icon.gif"));
    swgIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_swing_icon.gif"));
    axisIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_axis_icon.gif"));
    barIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_bar_icon.gif"));
    sliderIcon = new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_slider_icon.gif"));
    renderMaster = new MasterNodeRenderer();
  }

  public Component getTreeCellRendererComponent(
      JTree tree,
      Object value,
      boolean sel,
      boolean expanded,
      boolean leaf,
      int row,
      boolean hasFocus) {

    super.getTreeCellRendererComponent(
        tree, value, sel,
        expanded, leaf, row,
        hasFocus);

    JDTreeNode n = (JDTreeNode) value;
    JDObject o = n.getObject();
    // Root node
    if(o==null) return this;

    renderMaster.setBackground((sel)?selColor:tree.getBackground());

    // Label Icon
    if (n.getObject() instanceof JDLabel) {
      renderMaster.setValues(labelIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDLine) {
      renderMaster.setValues(lineIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDRectangle) {
      renderMaster.setValues(rectangleIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDRoundRectangle) {
      renderMaster.setValues(rrectangleIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDEllipse) {
      renderMaster.setValues(ellipseIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDSpline) {
      renderMaster.setValues(splineIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }
    
    if (n.getObject() instanceof JDPolyline) {
      renderMaster.setValues(polyIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDGroup) {
      renderMaster.setValues(groupIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDImage) {
      renderMaster.setValues(imgIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDSwingObject) {
      renderMaster.setValues(swgIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDBar) {
      renderMaster.setValues(barIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDSlider) {
      renderMaster.setValues(sliderIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    if (n.getObject() instanceof JDAxis) {
      renderMaster.setValues(axisIcon,o.getNodeName(),(o.hasValueProgram())?"[change with value]":"");
      return renderMaster;
    }

    return this;
  }

}
