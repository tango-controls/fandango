/** A panel for JDAxis private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKFontChooser;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDAxisPanel extends JPanel implements ActionListener,ChangeListener {

  private JLabel    orientationLabel;
  private JComboBox orientationCombo;

  private JLabel    labelLabel;
  private JComboBox labelCombo;

  private JLabel    scaleLabel;
  private JComboBox scaleCombo;

  private JLabel    formatLabel;
  private JComboBox formatCombo;

  private JLabel fontLabel;
  private JButton fontBtn;

  private JLabel   tickSpacingLabel;
  private JSpinner tickSpacingSpinner;
  private JLabel   tickWidthLabel;
  private JSpinner tickWidthSpinner;
  private JCheckBox tickCenterCheckBox;

  private JLabel     minLabel;
  private JTextField minText;
  private JLabel     maxLabel;
  private JTextField maxText;
  private JCheckBox  invertCheckBox;
  private JButton    applyValueBtn;

  private JDAxis[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDAxisPanel(JDAxis[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel axisPanel = new JPanel(null);
    axisPanel.setBorder(JDUtils.createTitleBorder("Axis style"));
    axisPanel.setBounds(5,5,370,171);

    orientationLabel = JDUtils.createLabel("Orientation");
    orientationLabel.setBounds(10, 20, 200, 20);
    axisPanel.add(orientationLabel);

    orientationCombo = new JComboBox();
    orientationCombo.setFont(JDUtils.labelFont);
    orientationCombo.addItem("Horizontal");
    orientationCombo.addItem("Vertical");
    orientationCombo.addActionListener(this);
    orientationCombo.setBounds(220, 20, 140, 25);
    axisPanel.add(orientationCombo);

    labelLabel = JDUtils.createLabel("Label position (Vertical only)");
    labelLabel.setBounds(10, 50, 200, 20);
    axisPanel.add(labelLabel);

    labelCombo = new JComboBox();
    labelCombo.setFont(JDUtils.labelFont);
    labelCombo.addItem("Left");
    labelCombo.addItem("Right");
    labelCombo.addActionListener(this);
    labelCombo.setBounds(220, 50, 140, 25);
    axisPanel.add(labelCombo);

    scaleLabel = JDUtils.createLabel("Scale");
    scaleLabel.setBounds(10, 80, 200, 20);
    axisPanel.add(scaleLabel);

    scaleCombo = new JComboBox();
    scaleCombo.setFont(JDUtils.labelFont);
    scaleCombo.addItem("Linear");
    scaleCombo.addItem("Logarithmic");
    scaleCombo.addActionListener(this);
    scaleCombo.setBounds(220, 80, 140, 25);
    axisPanel.add(scaleCombo);

    formatLabel = JDUtils.createLabel("Number format");
    formatLabel.setBounds(10, 110, 200, 20);
    axisPanel.add(formatLabel);

    formatCombo = new JComboBox();
    formatCombo.setFont(JDUtils.labelFont);
    formatCombo.addItem("Auto");
    formatCombo.addItem("Scientific");
    formatCombo.addItem("Time");
    formatCombo.addItem("Decimal");
    formatCombo.addItem("Hexadecimal");
    formatCombo.addItem("Binary");
    formatCombo.addItem("Scientific (Int)");
    formatCombo.addActionListener(this);
    formatCombo.setBounds(220, 110, 140, 25);
    axisPanel.add(formatCombo);

    fontLabel = new JLabel("Font");
    fontLabel.setFont(JDUtils.labelFont);
    fontLabel.setForeground(JDUtils.labelColor);
    fontLabel.setBounds(10, 140, 200, 24);
    axisPanel.add(fontLabel);

    fontBtn = new JButton();
    fontBtn.setText("Choose");
    fontBtn.setMargin(new Insets(0, 0, 0, 0));
    fontBtn.setFont(JDUtils.labelFont);
    fontBtn.setBounds(220, 140, 140, 24);
    fontBtn.addActionListener(this);
    axisPanel.add(fontBtn);

    add(axisPanel);

    // ------------------------------------------------------------------------------------
    JPanel tickPanel = new JPanel(null);
    tickPanel.setBorder(JDUtils.createTitleBorder("Axis tick"));
    tickPanel.setBounds(5,232,370,54);

    tickCenterCheckBox = new JCheckBox("Center");
    tickCenterCheckBox.setFont(JDUtils.labelFont);
    tickCenterCheckBox.setForeground(JDUtils.labelColor);
    tickCenterCheckBox.setBounds(10, 20, 100, 25);
    tickCenterCheckBox.addActionListener(this);
    tickPanel.add(tickCenterCheckBox);

    tickSpacingLabel = new JLabel("Spacing");
    tickSpacingLabel.setHorizontalAlignment(JLabel.RIGHT);
    tickSpacingLabel.setFont(JDUtils.labelFont);
    tickSpacingLabel.setForeground(JDUtils.labelColor);
    tickSpacingLabel.setBounds(110, 20, 60, 25);
    tickPanel.add(tickSpacingLabel);

    tickSpacingSpinner = new JSpinner();
    tickSpacingSpinner.addChangeListener(this);
    tickSpacingSpinner.setBounds(175, 20, 60, 25);
    tickPanel.add(tickSpacingSpinner);

    tickWidthLabel = new JLabel("Width");
    tickWidthLabel.setHorizontalAlignment(JLabel.RIGHT);
    tickWidthLabel.setFont(JDUtils.labelFont);
    tickWidthLabel.setForeground(JDUtils.labelColor);
    tickWidthLabel.setBounds(235, 20, 60, 25);
    tickPanel.add(tickWidthLabel);

    tickWidthSpinner = new JSpinner();
    tickWidthSpinner.addChangeListener(this);
    tickWidthSpinner.setBounds(300, 20, 60, 25);
    tickPanel.add(tickWidthSpinner);

    add(tickPanel);

    // ------------------------------------------------------------------------------------
    JPanel rangePanel = new JPanel(null);
    rangePanel.setBorder(JDUtils.createTitleBorder("Axis range"));
    rangePanel.setBounds(5,176,370,54);

    minLabel = new JLabel("Min");
    minLabel.setFont(JDUtils.labelFont);
    minLabel.setForeground(JDUtils.labelColor);
    minLabel.setBounds(10, 20, 35, 25);
    rangePanel.add(minLabel);

    minText = new JTextField();
    minText.setEditable(true);
    minText.setMargin(JDUtils.zMargin);
    minText.setFont(JDUtils.labelFont);
    minText.setBounds(45, 20, 60, 24);
    minText.addActionListener(this);
    rangePanel.add(minText);

    maxLabel = new JLabel("Max");
    maxLabel.setFont(JDUtils.labelFont);
    maxLabel.setForeground(JDUtils.labelColor);
    maxLabel.setBounds(110, 20, 35, 25);
    rangePanel.add(maxLabel);

    maxText = new JTextField();
    maxText.setEditable(true);
    maxText.setMargin(JDUtils.zMargin);
    maxText.setFont(JDUtils.labelFont);
    maxText.setBounds(145, 20, 60, 24);
    maxText.addActionListener(this);
    rangePanel.add(maxText);

    invertCheckBox = new JCheckBox("Invert");
    invertCheckBox.setFont(JDUtils.labelFont);
    invertCheckBox.setForeground(JDUtils.labelColor);
    invertCheckBox.setBounds(210, 20, 70, 25);
    invertCheckBox.addActionListener(this);
    rangePanel.add(invertCheckBox);

    applyValueBtn = new JButton("Apply");
    applyValueBtn.setFont(JDUtils.labelFont);
    applyValueBtn.setBounds(280, 20, 80, 24);
    applyValueBtn.addActionListener(this);
    rangePanel.add(applyValueBtn);

    add(rangePanel);

    updatePanel(p);

  }

  public void updatePanel(JDAxis[] objs) {

    allObjects = objs;
    refreshControl();

  }

  private void refreshControl() {

    isUpdating = true;

    if (allObjects == null || allObjects.length <= 0) {

      SpinnerNumberModel nullModel = new SpinnerNumberModel(0, 0, 0, 0);
      tickWidthSpinner.setModel(nullModel);
      tickSpacingSpinner.setModel(nullModel);

      orientationCombo.setSelectedIndex(-1);
      labelCombo.setSelectedIndex(-1);
      scaleCombo.setSelectedIndex(-1);
      formatCombo.setSelectedIndex(-1);
      fontLabel.setText("Font: ");
      tickCenterCheckBox.setSelected(false);
      invertCheckBox.setSelected(false);
      minText.setText("");
      maxText.setText("");

    } else {

      JDAxis p = allObjects[0];

      Integer value = new Integer(p.getTickWidth());
      Integer min = new Integer(-10);
      Integer max = new Integer(10);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      tickWidthSpinner.setModel(spModel);

      value = new Integer(p.getTickSpacing());
      min = new Integer(1);
      max = new Integer(1000);
      step = new Integer(1);
      SpinnerNumberModel spcModel = new SpinnerNumberModel(value, min, max, step);
      tickSpacingSpinner.setModel(spcModel);

      orientationCombo.setSelectedIndex(p.getOrientation());
      labelCombo.setSelectedIndex(p.getLabelPos());
      formatCombo.setSelectedIndex(p.getFormat());
      scaleCombo.setSelectedIndex(p.getScale());
      fontLabel.setText("Font: [" + JDUtils.buildFontName(p.getFont())+ "]");
      tickCenterCheckBox.setSelected(p.isTickCentered());
      invertCheckBox.setSelected(p.isInverted());
      minText.setText(Double.toString(p.getMin()));
      maxText.setText(Double.toString(p.getMax()));


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
    int i;

    initRepaint();
    Object src = e.getSource();
    if(src==orientationCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setOrientation(orientationCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change axis orientation");
    } else if(src==labelCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setLabelPos(labelCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change axis label");
    } else if(src==scaleCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setScale(scaleCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change axis scale");
    } else if (src == fontBtn) {
      Font newFont = ATKFontChooser.getNewFont(this,"Choose axis font",allObjects[0].getFont());
      if (newFont != null) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].setFont(newFont);
        fontLabel.setText("Font: [" + JDUtils.buildFontName(newFont) + "]");
        invoker.setNeedToSave(true,"Change axis font");
      }
    } else if (src == tickCenterCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setTickCentered(tickCenterCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change axis tick");
    } else if (src == invertCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setInverted(invertCheckBox.isSelected());
      invoker.setNeedToSave(true,"Invert axis");
    } else if(src==formatCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setFormat(formatCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change axis format");
    } else if (src == applyValueBtn || src == minText || src == maxText) {
      try {
        double nMin = Double.parseDouble(minText.getText());
        double nMax = Double.parseDouble(maxText.getText());
        if (nMin >= nMax) {
          JOptionPane.showMessageDialog(this,"Min must be lower than max.","Error",JOptionPane.ERROR_MESSAGE);
          refreshControl();
        } else {
          for (i = 0; i < allObjects.length; i++) {
            allObjects[i].setMin(nMin);
            allObjects[i].setMax(nMax);
          }
          invoker.setNeedToSave(true, "Change axis range");
          minText.setCaretPosition(0);
          maxText.setCaretPosition(0);
        }
      } catch (NumberFormatException ex) {
        JOptionPane.showMessageDialog(this,"Invalid range value.\n" + ex.getMessage(),"Error",JOptionPane.ERROR_MESSAGE);
        refreshControl();
      }
    }
    repaintObjects();

  }


  // ---------------------------------------------------------
  //Change listener
  // ---------------------------------------------------------
  public void stateChanged(ChangeEvent e) {

    if(allObjects==null || isUpdating) return;

    int i;
    initRepaint();
    Object src = e.getSource();
    Integer v;

    if (src == tickWidthSpinner) {
      v = (Integer) tickWidthSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setTickWidth(v.intValue());
      invoker.setNeedToSave(true,"Change tick length");
    } else if (src == tickSpacingSpinner) {
      v = (Integer) tickSpacingSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setTickSpacing(v.intValue());
      invoker.setNeedToSave(true,"Change tick spacing");
    }
    repaintObjects();

  }

}
