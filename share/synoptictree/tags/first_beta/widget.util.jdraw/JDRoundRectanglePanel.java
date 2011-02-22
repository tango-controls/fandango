package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDRoundRectanglePanel extends JPanel implements ActionListener,ChangeListener {

  private JLabel stepLabel;
  private JSpinner stepSpinner;

  private JLabel cornerWidthLabel;
  private JSpinner cornerWidthSpinner;

  private JDRoundRectangle[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDRoundRectanglePanel(JDRoundRectangle[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel polyPanel = new JPanel(null);
    polyPanel.setBorder(JDUtils.createTitleBorder("Corner"));
    polyPanel.setBounds(5,5,370,85);

    cornerWidthLabel = new JLabel("Corner width");
    cornerWidthLabel.setFont(JDUtils.labelFont);
    cornerWidthLabel.setForeground(JDUtils.labelColor);
    cornerWidthLabel.setBounds(10, 20, 100, 25);
    polyPanel.add(cornerWidthLabel);

    cornerWidthSpinner = new JSpinner();
    cornerWidthSpinner.addChangeListener(this);
    cornerWidthSpinner.setBounds(115, 20, 60, 25);
    polyPanel.add(cornerWidthSpinner);

    stepLabel = new JLabel("Interpolation step");
    stepLabel.setFont(JDUtils.labelFont);
    stepLabel.setForeground(JDUtils.labelColor);
    stepLabel.setBounds(10, 50, 100, 25);
    polyPanel.add(stepLabel);

    stepSpinner = new JSpinner();
    stepSpinner.addChangeListener(this);
    stepSpinner.setBounds(115, 50, 60, 25);
    polyPanel.add(stepSpinner);
    add(polyPanel);

    updatePanel(p);

  }

  public void updatePanel(JDRoundRectangle[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      SpinnerNumberModel nullModel = new SpinnerNumberModel(0, 0, 0, 0);
      cornerWidthSpinner.setModel(nullModel);
      stepSpinner.setModel(nullModel);

    } else {

      JDRoundRectangle p = objs[0];

      Integer value = new Integer(p.getCornerWidth());
      Integer min = new Integer(1);
      Integer max = new Integer(256);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      cornerWidthSpinner.setModel(spModel);

      Integer value2 = new Integer(p.getStep());
      Integer min2 = new Integer(1);
      Integer max2 = new Integer(256);
      Integer step2 = new Integer(1);
      SpinnerNumberModel spModel2 = new SpinnerNumberModel(value2, min2, max2, step2);
      stepSpinner.setModel(spModel2);

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
      invoker.setNeedToSave(true,"Change step");
    }
    if (src == cornerWidthSpinner) {
      v = (Integer) cornerWidthSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setCornerWidth(v.intValue());
      invoker.setNeedToSave(true,"Change corner width");
    }
    repaintObjects();

  }

}
