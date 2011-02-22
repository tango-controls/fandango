/** A panel for JDPolyline private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Vector;

class JDSliderPanel extends JPanel implements ActionListener {

  private JLabel     valueLabel;
  private JTextField valueText;
  private JLabel     minValueLabel;
  private JTextField minValueText;
  private JLabel     maxValueLabel;
  private JTextField maxValueText;
  private JButton    applyValueBtn;
  private JLabel     orientationLabel;
  private JComboBox  orientationCombo;
  private JButton    cursorPropBtn;
  private JButton    cursorNewBtn;
  private JButton    cursorCopyBtn;

  private JDSlider[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDSliderPanel(JDSlider[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel barPanel = new JPanel(null);
    barPanel.setBorder(JDUtils.createTitleBorder("Slider Value"));
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
    stylePanel.setBounds(5,65,370,55);

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

    // ----------------------------------------------
    JPanel cursorPanel = new JPanel(null);
    cursorPanel.setBorder(JDUtils.createTitleBorder("Cursor"));
    cursorPanel.setBounds(5,120,370,55);

    cursorPropBtn = new JButton("Properties");
    cursorPropBtn.setFont(JDUtils.labelFont);
    cursorPropBtn.setMargin(new Insets(0, 0, 0, 0));
    cursorPropBtn.setForeground(Color.BLACK);
    cursorPropBtn.addActionListener(this);
    cursorPropBtn.setBounds(10, 20, 110, 25);
    cursorPanel.add(cursorPropBtn);

    cursorNewBtn = new JButton("Pick new");
    cursorNewBtn.setFont(JDUtils.labelFont);
    cursorNewBtn.setMargin(new Insets(0, 0, 0, 0));
    cursorNewBtn.setForeground(Color.BLACK);
    cursorNewBtn.addActionListener(this);
    cursorNewBtn.setBounds(130, 20, 110, 25);
    cursorPanel.add(cursorNewBtn);

    cursorCopyBtn = new JButton("Extract");
    cursorCopyBtn.setFont(JDUtils.labelFont);
    cursorCopyBtn.setMargin(new Insets(0, 0, 0, 0));
    cursorCopyBtn.setForeground(Color.BLACK);
    cursorCopyBtn.addActionListener(this);
    cursorCopyBtn.setBounds(250, 20, 110, 25);
    cursorPanel.add(cursorCopyBtn);

    add(cursorPanel);

    updatePanel(p);

  }

  public void updatePanel(JDSlider[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

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

    JDSlider p = allObjects[0];
    isUpdating = true;

    valueText.setText(Double.toString(p.getSliderValue()));
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
   if( src == minValueText ) {

      try {
        double m = Double.parseDouble( minValueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setMinimum(m);
        invoker.setNeedToSave(true,"Change minimum slider value");
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(this,"Invalid syntax for min value");
      }
      refreshControls();

    } else if( src == maxValueText ) {

      try {
        double m = Double.parseDouble( maxValueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setMaximum(m);
        invoker.setNeedToSave(true,"Change maximum slider value");
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(this,"Invalid syntax for max value");
      }
      refreshControls();

    } else if( src == valueText ) {

      try {
        double m = Double.parseDouble( valueText.getText() );
        for(i=0;i<allObjects.length;i++) allObjects[i].setSliderValue(m);
        invoker.setNeedToSave(true,"Change slider value");
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
          allObjects[i].setSliderValue(init);
        }
        invoker.setNeedToSave(true,"Change slider value range");

      } catch (NumberFormatException ex) {
        JOptionPane.showMessageDialog(this,"One or more value are incorrect");
      }
      refreshControls();

    } else if ( src==orientationCombo ) {

      int s = orientationCombo.getSelectedIndex();
      if(s>=0) {
        for(i=0;i<allObjects.length;i++) allObjects[i].setOrientation(s);
        invoker.setNeedToSave(true,"Change slider orientation");
      }

    } else  if( src==cursorPropBtn ) {

      // Switch to cursor
      Vector tmp = new Vector();
      tmp.add(allObjects[0].getCursor());
      JDUtils.updatePropertyDialog(tmp);
      return;

    } else  if( src==cursorNewBtn ) {

      getRootPane().getParent().setVisible(false);
      invoker.pickCursor(allObjects[0]);
      return;

    } else  if( src==cursorCopyBtn ) {

      JDObject nObject = allObjects[0].getCursor().copy(50,50);
      invoker.addObject(nObject);
      invoker.setNeedToSave(true,"Extract slider cursor");
      nObject.refresh();

    }
    repaintObjects();

  }



}
