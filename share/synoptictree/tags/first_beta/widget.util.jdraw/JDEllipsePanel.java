/** A panel for JDEllipse private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDEllipsePanel extends JPanel implements ActionListener,ChangeListener {

  private JLabel   startLabel;
  private JSpinner startSpinner;

  private JLabel   extentLabel;
  private JSpinner extentSpinner;

  private JLabel   stepLabel;
  private JSpinner stepSpinner;

  private JLabel    arcTypeLabel;
  private JComboBox arcTypeCombo;

  private JDEllipse[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDEllipsePanel(JDEllipse[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel polyPanel = new JPanel(null);
    polyPanel.setBorder(JDUtils.createTitleBorder("Ellipse"));
    polyPanel.setBounds(5,5,370,120);

    startLabel = new JLabel("Angle start");
    startLabel.setFont(JDUtils.labelFont);
    startLabel.setForeground(JDUtils.labelColor);
    startLabel.setBounds(10, 20, 100, 25);
    polyPanel.add(startLabel);

    startSpinner = new JSpinner();
    startSpinner.addChangeListener(this);
    startSpinner.setBounds(115, 20, 60, 25);
    polyPanel.add(startSpinner);

    extentLabel = new JLabel("Angle extent");
    extentLabel.setFont(JDUtils.labelFont);
    extentLabel.setForeground(JDUtils.labelColor);
    extentLabel.setBounds(190, 20, 100, 25);
    polyPanel.add(extentLabel);

    extentSpinner = new JSpinner();
    extentSpinner.addChangeListener(this);
    extentSpinner.setBounds(295, 20, 60, 25);
    polyPanel.add(extentSpinner);

    stepLabel = new JLabel("Interpolation step");
    stepLabel.setFont(JDUtils.labelFont);
    stepLabel.setForeground(JDUtils.labelColor);
    stepLabel.setBounds(10, 50, 100, 25);
    polyPanel.add(stepLabel);

    stepSpinner = new JSpinner();
    stepSpinner.addChangeListener(this);
    stepSpinner.setBounds(115, 50, 60, 25);
    polyPanel.add(stepSpinner);

    arcTypeLabel = JDUtils.createLabel("Arc Type");
    arcTypeLabel.setBounds(10, 80, 90, 20);
    polyPanel.add(arcTypeLabel);

    arcTypeCombo = new JComboBox();
    arcTypeCombo.setFont(JDUtils.labelFont);
    arcTypeCombo.addItem("Open");
    arcTypeCombo.addItem("Closed");
    arcTypeCombo.addItem("Pie");
    arcTypeCombo.addActionListener(this);
    arcTypeCombo.setBounds(115, 80, 60, 25);
    polyPanel.add(arcTypeCombo);
    add(polyPanel);

    updatePanel(p);

  }

  public void updatePanel(JDEllipse[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      SpinnerNumberModel nullModel = new SpinnerNumberModel(0, 0, 0, 0);
      startSpinner.setModel(nullModel);
      extentSpinner.setModel(nullModel);
      stepSpinner.setModel(nullModel);
      arcTypeCombo.setSelectedIndex(-1);

    } else {

      JDEllipse p = objs[0];

      Integer value = new Integer(p.getAngleStart());
      Integer min = new Integer(-360);
      Integer max = new Integer(360);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      startSpinner.setModel(spModel);

      value = new Integer(p.getAngleExtent());
      min = new Integer(0);
      max = new Integer(360);
      step = new Integer(1);
      spModel = new SpinnerNumberModel(value, min, max, step);
      extentSpinner.setModel(spModel);

      value = new Integer(p.getStep());
      min = new Integer(1);
      max = new Integer(256);
      step = new Integer(1);
      spModel = new SpinnerNumberModel(value, min, max, step);
      stepSpinner.setModel(spModel);

      arcTypeCombo.setSelectedIndex(p.getArcType());

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

    initRepaint();
    Object src = e.getSource();
    if(src==arcTypeCombo) {
      for (int i = 0; i < allObjects.length; i++)
        allObjects[i].setArcType(arcTypeCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change arc type");
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

    if (src == stepSpinner) {
      v = (Integer) stepSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setStep(v.intValue());
      invoker.setNeedToSave(true,"Change arc step");
    } else if (src == startSpinner) {
      v = (Integer) startSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setAngleStart(v.intValue());
      invoker.setNeedToSave(true,"Change arc angle");
    } else if (src == extentSpinner) {
      v = (Integer) extentSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setAngleExtent(v.intValue());
      invoker.setNeedToSave(true,"Change arc angle");
    }
    repaintObjects();

  }

}
