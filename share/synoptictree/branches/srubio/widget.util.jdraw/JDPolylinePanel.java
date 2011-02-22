/** A panel for JDPolyline private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDPolylinePanel extends JPanel implements ActionListener,ChangeListener {

  JCheckBox closedCheckBox;

  private JLabel stepLabel;
  private JSpinner stepSpinner;

  private JDPolyline[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDPolylinePanel(JDPolyline[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel polyPanel = new JPanel(null);
    polyPanel.setBorder(JDUtils.createTitleBorder("Polyline"));
    polyPanel.setBounds(5,5,370,85);

    closedCheckBox = new JCheckBox("Closed");
    closedCheckBox.setFont(JDUtils.labelFont);
    closedCheckBox.setBounds(5, 20, 100, 24);
    closedCheckBox.addActionListener(this);
    polyPanel.add(closedCheckBox);

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

  public void updatePanel(JDPolyline[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      closedCheckBox.setSelected(false);
      stepSpinner.setModel(new SpinnerNumberModel(0, 0, 0, 0));

    } else {

      JDPolyline p = objs[0];

      closedCheckBox.setSelected(p.isClosed());
      Integer value = new Integer(p.getStep());
      Integer min = new Integer(1);
      Integer max = new Integer(256);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      stepSpinner.setModel(spModel);

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
    if (src == closedCheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setClosed(closedCheckBox.isSelected());
      invoker.setNeedToSave(true,"Change closed");
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
      invoker.setNeedToSave(true,"Change step");
    }
    repaintObjects();

  }

}
