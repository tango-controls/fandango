/** A panel for JDPolyline private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDBarPanel extends JPanel implements ActionListener {

  JCheckBox          outLineCheckBox;
  private JLabel     valueLabel;
  private JTextField valueText;
  private JLabel     minValueLabel;
  private JTextField minValueText;
  private JLabel     maxValueLabel;
  private JTextField maxValueText;
  private JButton    applyValueBtn;
  private JLabel     orientationLabel;
  private JComboBox  orientationCombo;

  private JDBar[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDBarPanel(JDBar[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel barPanel = new JPanel(null);
    barPanel.setBorder(JDUtils.createTitleBorder("Bar Value"));
    barPanel.setBounds(5,5,370,55);

    valueLabel = JDUtils.createLabel("Val");
    valueLabel.setBounds(10, 20, 30, 25);
    barPanel.add(valueLabel);

    valueText = new JTextField();
    valueText.setMargin(JDUtils.zMargin);
    valueText.setEditable(true);
    valueText.setFont(JDUtils.labelFont);
    valueText.setBounds(45, 20, 50, 24);
    valueText.addActionListener(this);
    barPanel.add(valueText);

    minValueLabel =JDUtils.createLabel("Min");
    minValueLabel.setBounds(100, 20, 30, 25);
    barPanel.add(minValueLabel);

    minValueText = new JTextField();
    minValueText.setMargin(JDUtils.zMargin);
    minValueText.setEditable(true);
    minValueText.setFont(JDUtils.labelFont);
    minValueText.setBounds(135, 20, 50, 24);
    minValueText.addActionListener(this);
    barPanel.add(minValueText);

    maxValueLabel = JDUtils.createLabel("Max");
    maxValueLabel.setBounds(190, 20, 30, 25);
    barPanel.add(maxValueLabel);

    maxValueText = new JTextField();
    maxValueText.setMargin(JDUtils.zMargin);
    maxValueText.setEditable(true);
    maxValueText.setFont(JDUtils.labelFont);
    maxValueText.setBounds(225, 20, 50, 24);
    maxValueText.addActionListener(this);
    barPanel.add(maxValueText);

    applyValueBtn = new JButton("Apply");
    applyValueBtn.setFont(JDUtils.labelFont);
    applyValueBtn.setMargin(new Insets(0, 0, 0, 0));
    applyValueBtn.setForeground(Color.BLACK);
    applyValueBtn.addActionListener(this);
    applyValueBtn.setBounds(285, 20, 75, 25);
    barPanel.add(applyValueBtn);

    add(barPanel);

    // ----------------------------------------------
    JPanel stylePanel = new JPanel(null);
    stylePanel.setBorder(JDUtils.createTitleBorder("Styles"));
    stylePanel.setBounds(5,70,370,90);

    outLineCheckBox = new JCheckBox("Show Outline");
    outLineCheckBox.setFont(JDUtils.labelFont);
    outLineCheckBox.setBounds(5, 50, 150, 24);
    outLineCheckBox.addActionListener(this);
    stylePanel.add(outLineCheckBox);

    orientationLabel = JDUtils.createLabel("Orientation");
    orientationLabel.setBounds(10, 20, 100, 20);
    stylePanel.add(orientationLabel);

    orientationCombo = new JComboBox();
    orientationCombo.setFont(JDUtils.labelFont);
    orientationCombo.addItem("Left to Right");
    orientationCombo.addItem("Right To Left");
    orientationCombo.addItem("Top to Bottom");
    orientationCombo.addItem("Bottom to Top");
    orientationCombo.addActionListener(this);
    orientationCombo.setBounds(120,20, 240, 25);
    stylePanel.add(orientationCombo);

    add(stylePanel);

    updatePanel(p);

  }

  public void updatePanel(JDBar[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      outLineCheckBox.setSelected(false);
      valueText.setText("");
      minValueText.setText("");
      maxValueText.setText("");
      orientationCombo.setSelectedIndex(-1);

    } else {

      refreshControls();

    }

    isUpdating = false;

  }

  private void refreshControls() {

    JDBar p = allObjects[0];
    isUpdating = true;

    outLineCheckBox.setSelected(p.isOutLineVisible());
    valueText.setText(Double.toString(p.getBarValue()));
    minValueText.setText(Double.toString(p.getMinimum()));
    maxValueText.setText(Double.toString(p.getMaximum()));
    orientationCombo.setSelectedIndex(p.getOrientation());

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
    if (src == outLineCheckBox) {

      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setOutLineVisible(outLineCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change OutLine");

    } else if( src == minValueText ) {

      try {
        double m = Double.parseDouble( minValueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setMinimum(m);
        invoker.setNeedToSave(true,"Change minimum bar value");
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(this,"Invalid syntax for min value");
      }
      refreshControls();

    } else if( src == maxValueText ) {

      try {
        double m = Double.parseDouble( maxValueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setMaximum(m);
        invoker.setNeedToSave(true,"Change maximum bar value");
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(this,"Invalid syntax for max value");
      }
      refreshControls();

    } else if( src == valueText ) {

      try {
        double m = Double.parseDouble( valueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setBarValue(m);
        invoker.setNeedToSave(true,"Change bar value");
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(this,"Invalid syntax for value");
      }
      refreshControls();

    } else  if( src==applyValueBtn ) {

      try {

        double min  = Double.parseDouble( minValueText.getText() );
        double max  = Double.parseDouble( maxValueText.getText() );
        double init = Double.parseDouble( valueText.getText() );
        for(i=0;i<allObjects.length;i++) {
          allObjects[i].setMinimum(min);
          allObjects[i].setMaximum(max);
          allObjects[i].setBarValue(init);
        }
        invoker.setNeedToSave(true,"Change bar value range");

      } catch (NumberFormatException ex) {
        JOptionPane.showMessageDialog(this,"One or more value are incorrect");
      }
      refreshControls();

    } else if ( src==orientationCombo ) {

      int s = orientationCombo.getSelectedIndex();
      if(s>=0) {
        for(i=0;i<allObjects.length;i++) allObjects[i].setOrientation(s);
        invoker.setNeedToSave(true,"Change bar orientation");
      }

    }
    repaintObjects();

  }



}
