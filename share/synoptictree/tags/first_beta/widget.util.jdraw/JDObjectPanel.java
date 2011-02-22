package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDObjectPanel extends JPanel implements ActionListener, ChangeListener {

  private JTextField nameText;
  private JButton applyNameBtn;
  private JLabel backgroundLabel;
  private JButton backgroundButton;
  private JLabel foregroundLabel;
  private JButton foregroundButton;
  private JLabel lineWidthLabel;
  private JSpinner lineWidthSpinner;

  private JLabel lineDashLabel;
  private JComboBox lineDashCombo;

  private JLabel fillDashLabel;
  private JComboBox fillDashCombo;
  private JButton fillCustomButton;

  private JCheckBox visibleCheckBox;
  private JCheckBox antiAliasCheckBox;

  private JCheckBox shadowCheckBox;
  private JCheckBox invertShadowCheckBox;
  private JLabel shadowWidthLabel;
  private JSpinner shadowWidthSpinner;

  private JDObject[] allObjects = null;
  private JDrawEditor invoker;
  private JDBrowserPanel invoker2;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDObjectPanel() {
    this(null,null,null);
  }

  public JDObjectPanel(JDObject[] p, JDrawEditor jc,JDBrowserPanel jb) {

    invoker = jc;
    invoker2 = jb;

    setForeground(JDUtils.labelColor);
    setFont(JDUtils.labelFont);
    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel namePanel = new JPanel(null);
    namePanel.setBorder(JDUtils.createTitleBorder("Object name"));
    namePanel.setBounds(5, 5, 370, 55);

    nameText = new JTextField();
    nameText.setMargin(JDUtils.zMargin);
    nameText.setEditable(true);
    nameText.setFont(JDUtils.labelFont);
    nameText.setBounds(10, 20, 260, 24);
    nameText.addActionListener(this);
    namePanel.add(nameText);

    applyNameBtn = new JButton("Apply");
    applyNameBtn.setFont(JDUtils.labelFont);
    applyNameBtn.setBounds(270, 20, 90, 24);
    applyNameBtn.addActionListener(this);
    namePanel.add(applyNameBtn);

    add(namePanel);

    // ------------------------------------------------------------------------------------
    JPanel colorPanel = new JPanel(null);
    colorPanel.setBorder(JDUtils.createTitleBorder("Colors"));
    colorPanel.setBounds(5, 60, 370, 55);

    foregroundLabel = JDUtils.createLabel("Foreground");
    foregroundLabel.setBounds(10, 20, 100, 24);
    colorPanel.add(foregroundLabel);
    foregroundButton = new JButton("...");
    foregroundButton.setMargin(new Insets(0, 0, 0, 0));
    foregroundButton.setForeground(Color.BLACK);
    foregroundButton.addActionListener(this);
    foregroundButton.setBounds(120, 20, 60, 24);
    colorPanel.add(foregroundButton);
    add(colorPanel);

    backgroundLabel = JDUtils.createLabel("Background");
    backgroundLabel.setBounds(190, 20, 100, 24);
    colorPanel.add(backgroundLabel);
    backgroundButton = new JButton("");
    backgroundButton.setMargin(new Insets(0, 0, 0, 0));
    backgroundButton.setForeground(Color.BLACK);
    backgroundButton.addActionListener(this);
    backgroundButton.setBounds(300, 20, 60, 24);
    colorPanel.add(backgroundButton);


    // ------------------------------------------------------------------------------------
    JPanel stylePanel = new JPanel(null);
    stylePanel.setBorder(JDUtils.createTitleBorder("Styles"));
    stylePanel.setBounds(5, 115, 370, 115);

    lineDashLabel = JDUtils.createLabel("Line style");
    lineDashLabel.setBounds(10, 20, 70, 25);
    stylePanel.add(lineDashLabel);

    lineDashCombo = new JComboBox();
    lineDashCombo.setFont(JDUtils.labelFont);
    lineDashCombo.addItem("Solid");
    lineDashCombo.addItem("Point dash");
    lineDashCombo.addItem("Short dash");
    lineDashCombo.addItem("Long dash");
    lineDashCombo.addItem("Dot dash");
    lineDashCombo.addActionListener(this);
    lineDashCombo.setBounds(80, 20, 140, 25);
    stylePanel.add(lineDashCombo);

    lineWidthLabel = JDUtils.createLabel("Line width");
    lineWidthLabel.setHorizontalAlignment(JLabel.RIGHT);
    lineWidthLabel.setBounds(220, 20, 90, 25);
    stylePanel.add(lineWidthLabel);

    lineWidthSpinner = new JSpinner();
    lineWidthSpinner.addChangeListener(this);
    lineWidthSpinner.setBounds(315, 20, 45, 25);
    stylePanel.add(lineWidthSpinner);
    add(stylePanel);

    fillDashLabel = JDUtils.createLabel("Fill style");
    fillDashLabel.setBounds(10, 50, 70, 25);
    stylePanel.add(fillDashLabel);

    fillDashCombo = new JComboBox();
    fillDashCombo.setFont(JDUtils.labelFont);
    fillDashCombo.addItem("No fill");
    fillDashCombo.addItem("Solid");
    fillDashCombo.addItem("Large leff hatch");
    fillDashCombo.addItem("Large right hatch");
    fillDashCombo.addItem("Large cross hatch");
    fillDashCombo.addItem("Small leff hatch");
    fillDashCombo.addItem("Small right hatch");
    fillDashCombo.addItem("Small cross hatch");
    fillDashCombo.addItem("Dot pattern 1");
    fillDashCombo.addItem("Dot pattern 2");
    fillDashCombo.addItem("Dot pattern 3");
    fillDashCombo.addItem("Gradient fill");
    fillDashCombo.addActionListener(this);
    fillDashCombo.setBounds(80, 50, 140, 25);
    stylePanel.add(fillDashCombo);

    fillCustomButton = new JButton("Gradient settings");
    fillCustomButton.setFont(JDUtils.labelFont);
    fillCustomButton.setMargin(new Insets(0, 0, 0, 0));
    fillCustomButton.setForeground(Color.BLACK);
    fillCustomButton.addActionListener(this);
    fillCustomButton.setBounds(230, 50, 130, 25);
    stylePanel.add(fillCustomButton);

    visibleCheckBox = new JCheckBox("Visible");
    visibleCheckBox.setFont(JDUtils.labelFont);
    visibleCheckBox.setForeground(JDUtils.labelColor);
    visibleCheckBox.setBounds(5, 80, 90, 25);
    visibleCheckBox.addActionListener(this);
    stylePanel.add(visibleCheckBox);

    antiAliasCheckBox = new JCheckBox("Anti alias");
    antiAliasCheckBox.setFont(JDUtils.labelFont);
    antiAliasCheckBox.setForeground(JDUtils.labelColor);
    antiAliasCheckBox.setBounds(110, 80, 90, 25);
    antiAliasCheckBox.addActionListener(this);
    stylePanel.add(antiAliasCheckBox);

    // ------------------------------------------------------------------------------------
    JPanel shadowPanel = new JPanel(null);
    shadowPanel.setBorder(JDUtils.createTitleBorder("Shadows"));
    shadowPanel.setBounds(5, 230, 370, 55);

    shadowCheckBox = new JCheckBox("Shadow");
    shadowCheckBox.setFont(JDUtils.labelFont);
    shadowCheckBox.setForeground(JDUtils.labelColor);
    shadowCheckBox.setBounds(5, 20, 90, 25);
    shadowCheckBox.addActionListener(this);
    shadowPanel.add(shadowCheckBox);

    invertShadowCheckBox = new JCheckBox("Invert");
    invertShadowCheckBox.setFont(JDUtils.labelFont);
    invertShadowCheckBox.setForeground(JDUtils.labelColor);
    invertShadowCheckBox.setBounds(110, 20, 90, 25);
    invertShadowCheckBox.addActionListener(this);
    shadowPanel.add(invertShadowCheckBox);

    shadowWidthLabel = JDUtils.createLabel("Thickness");
    shadowWidthLabel.setHorizontalAlignment(JLabel.RIGHT);
    shadowWidthLabel.setBounds(200, 20, 90, 25);
    shadowPanel.add(shadowWidthLabel);

    shadowWidthSpinner = new JSpinner();
    shadowWidthSpinner.addChangeListener(this);
    shadowWidthSpinner.setBounds(295, 20, 65, 25);
    shadowPanel.add(shadowWidthSpinner);
    add(shadowPanel);

    updatePanel(p);
  }

  public void updatePanel(JDObject[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {
      
      nameText.setText("");
      foregroundButton.setBackground(Color.LIGHT_GRAY);
      backgroundButton.setBackground(Color.LIGHT_GRAY);
      lineDashCombo.setSelectedIndex(-1);

      lineWidthSpinner.setModel(new SpinnerNumberModel(0,0,0,0));
      shadowWidthSpinner.setModel(new SpinnerNumberModel(0,0,0,0));

      fillDashCombo.setSelectedIndex(-1);
      fillCustomButton.setEnabled(false);
      visibleCheckBox.setSelected(false);
      antiAliasCheckBox.setSelected(false);
      shadowCheckBox.setSelected(false);
      invertShadowCheckBox.setSelected(false);

    } else {

      JDObject p = objs[0];

      nameText.setText(p.getName());
      foregroundButton.setBackground(p.getForeground());
      backgroundButton.setBackground(p.getBackground());
      lineDashCombo.setSelectedIndex(p.getLineStyle());

      Integer value = new Integer(p.getLineWidth());
      Integer min = new Integer(0);
      Integer max = new Integer(10);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      lineWidthSpinner.setModel(spModel);

      min = new Integer(1);
      max = new Integer(20);
      step = new Integer(1);
      value = new Integer(p.getShadowWidth());
      SpinnerNumberModel sp2Model = new SpinnerNumberModel(value, min, max, step);
      shadowWidthSpinner.setModel(sp2Model);

      fillDashCombo.setSelectedIndex(p.getFillStyle());
      fillCustomButton.setEnabled(p.getFillStyle() == JDObject.FILL_STYLE_GRADIENT);
      visibleCheckBox.setSelected(p.isVisible());
      antiAliasCheckBox.setSelected(p.isAntiAliased());
      shadowCheckBox.setSelected(p.hasShadow());
      invertShadowCheckBox.setSelected(p.hasInverseShadow());

    }

    isUpdating = false;

  }

  private void initRepaint() {
    if(allObjects==null) return;
    oldRect = allObjects[0].getRepaintRect();
    for (int i = 1; i < allObjects.length; i++)
      oldRect = oldRect.union(allObjects[i].getRepaintRect());
  }

  private void repaintObjects() {
    if(allObjects==null) return;
    Rectangle newRect = allObjects[0].getRepaintRect();
    for (int i = 1; i < allObjects.length; i++)
      newRect = newRect.union(allObjects[i].getRepaintRect());
    invoker.repaint(newRect.union(oldRect));
  }

  // ---------------------------------------------------------
  // Action listener
  // ---------------------------------------------------------
  public void actionPerformed(ActionEvent e) {

    if(allObjects==null || isUpdating) return;

    Object src = e.getSource();
    int i;
    initRepaint();

    if (src == backgroundButton) {
      Color c = JColorChooser.showDialog(this, "Choose background color", allObjects[0].getBackground());
      if (c != null) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].setBackground(c);
        backgroundButton.setBackground(c);
        invoker.setNeedToSave(true,"Change background");
      }
    } else if (src == foregroundButton) {
      Color c = JColorChooser.showDialog(this, "Choose foreground color", allObjects[0].getForeground());
      if (c != null) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].setForeground(c);
        foregroundButton.setBackground(c);
        invoker.setNeedToSave(true,"Change foreground");
      }
    } else if (src == lineDashCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setLineStyle(lineDashCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change line style");
    } else if (src == fillDashCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setFillStyle(fillDashCombo.getSelectedIndex());
      fillCustomButton.setEnabled(fillDashCombo.getSelectedIndex()==JDObject.FILL_STYLE_GRADIENT);
      invoker.setNeedToSave(true,"Change fill style");
    } else if (src == shadowCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setShadow(shadowCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change shadow");
    } else if (src == invertShadowCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setInverseShadow(invertShadowCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change invert shadow");
    } else if (src == nameText || src == applyNameBtn) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setName(nameText.getText());
      invoker.setNeedToSave(true,"Change name");
      if(invoker2!=null) invoker2.updateNode();
      nameText.setCaretPosition(0);
    } else if (src == visibleCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setVisible(visibleCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change visible");
    } else if (src == fillCustomButton) {
      JDialog d = (JDialog)getRootPane().getRootPane().getParent();
      JDGradientDialog dlg = new JDGradientDialog(d,allObjects,invoker);
      if(dlg.editGradient()) invoker.setNeedToSave(true,"Change gradient fill");
    } else if (src == antiAliasCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setAntiAlias(antiAliasCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change anti alias");
    }

    repaintObjects();
  }

  // ---------------------------------------------------------
  //Change listener
  // ---------------------------------------------------------
  public void stateChanged(ChangeEvent e) {

    if(allObjects==null || isUpdating) return;

    Object src = e.getSource();
    Integer v;
    int i;
    initRepaint();

    if (src == lineWidthSpinner) {
      v = (Integer) lineWidthSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setLineWidth(v.intValue());
      invoker.setNeedToSave(true,"Change line width");
    } else if (src == shadowWidthSpinner) {
      v = (Integer) shadowWidthSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setShadowWidth(v.intValue());
      invoker.setNeedToSave(true,"Change shadow width");
    }

    repaintObjects();
  }


}
