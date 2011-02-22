/** A panel for JDLine private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;


class JDLinePanel extends JPanel implements ActionListener, ChangeListener {

  private JCheckBox line1CheckBox;
  private JLabel line1Label;

  private JCheckBox line2CheckBox;
  private JLabel line2Label;

  private JCheckBox line3CheckBox;
  private JLabel line3Label;

  private JCheckBox line4CheckBox;
  private JLabel line4Label;

  private JCheckBox line5CheckBox;
  private JLabel line5Label;

  private JCheckBox line6CheckBox;
  private JLabel line6Label;

  private JCheckBox line7CheckBox;
  private JLabel line7Label;

  private JCheckBox line8CheckBox;
  private JLabel line8Label;

  private JCheckBox line9CheckBox;
  private JLabel line9Label;

  private JLabel arrowWidthLabel;
  private JSpinner arrowWidthSpinner;

  private JDLine[] allObjects = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDLinePanel(JDLine[] p, JDrawEditor jc) {

    invoker = jc;
    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel arrowPanel = new JPanel(null);
    arrowPanel.setBorder(JDUtils.createTitleBorder("Arrows"));
    arrowPanel.setBounds(5,5,370,150);

    line1CheckBox = new JCheckBox();
    line1CheckBox.setBounds(20, 20, 20, 24);
    line1CheckBox.addActionListener(this);
    arrowPanel.add(line1CheckBox);

    line1Label = new JLabel();
    line1Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow1.gif")));
    line1Label.setBounds(45, 20, 70, 24);
    arrowPanel.add(line1Label);


    line2CheckBox = new JCheckBox();
    line2CheckBox.setBounds(140, 20, 20, 24);
    line2CheckBox.addActionListener(this);
    arrowPanel.add(line2CheckBox);

    line2Label = new JLabel();
    line2Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow2.gif")));
    line2Label.setBounds(165, 20, 70, 24);
    arrowPanel.add(line2Label);

    line3CheckBox = new JCheckBox();
    line3CheckBox.setBounds(140, 50, 20, 24);
    line3CheckBox.addActionListener(this);
    arrowPanel.add(line3CheckBox);

    line3Label = new JLabel();
    line3Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow3.gif")));
    line3Label.setBounds(165, 50, 70, 24);
    arrowPanel.add(line3Label);

    line4CheckBox = new JCheckBox();
    line4CheckBox.setBounds(140, 80, 20, 24);
    line4CheckBox.addActionListener(this);
    arrowPanel.add(line4CheckBox);

    line4Label = new JLabel();
    line4Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow4.gif")));
    line4Label.setBounds(165, 80, 70, 24);
    arrowPanel.add(line4Label);

    line5CheckBox = new JCheckBox();
    line5CheckBox.setBounds(140, 110, 20, 24);
    line5CheckBox.addActionListener(this);
    arrowPanel.add(line5CheckBox);

    line5Label = new JLabel();
    line5Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow5.gif")));
    line5Label.setBounds(165, 110, 70, 24);
    arrowPanel.add(line5Label);


    line6CheckBox = new JCheckBox();
    line6CheckBox.setBounds(260, 20, 20, 24);
    line6CheckBox.addActionListener(this);
    arrowPanel.add(line6CheckBox);

    line6Label = new JLabel();
    line6Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow6.gif")));
    line6Label.setBounds(285, 20, 70, 24);
    arrowPanel.add(line6Label);

    line7CheckBox = new JCheckBox();
    line7CheckBox.setBounds(260, 50, 20, 24);
    line7CheckBox.addActionListener(this);
    arrowPanel.add(line7CheckBox);

    line7Label = new JLabel();
    line7Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow7.gif")));
    line7Label.setBounds(285, 50, 70, 24);
    arrowPanel.add(line7Label);

    line8CheckBox = new JCheckBox();
    line8CheckBox.setBounds(260, 80, 20, 24);
    line8CheckBox.addActionListener(this);
    arrowPanel.add(line8CheckBox);

    line8Label = new JLabel();
    line8Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow8.gif")));
    line8Label.setBounds(285, 80, 70, 24);
    arrowPanel.add(line8Label);

    line9CheckBox = new JCheckBox();
    line9CheckBox.setBounds(260, 110, 20, 24);
    line9CheckBox.addActionListener(this);
    arrowPanel.add(line9CheckBox);

    line9Label = new JLabel();
    line9Label.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/jdraw/gif/jdraw_arrow9.gif")));
    line9Label.setBounds(285, 110, 70, 24);
    arrowPanel.add(line9Label);

    arrowWidthLabel = new JLabel("Arrow size");
    arrowWidthLabel.setFont(JDUtils.labelFont);
    arrowWidthLabel.setForeground(JDUtils.labelColor);
    arrowWidthLabel.setBounds(10, 80, 80, 25);
    arrowPanel.add(arrowWidthLabel);

    arrowWidthSpinner = new JSpinner();
    arrowWidthSpinner.addChangeListener(this);
    arrowWidthSpinner.setBounds(10, 110, 60, 25);
    arrowPanel.add(arrowWidthSpinner);
    add(arrowPanel);

    updatePanel(p);

  }

  public void updatePanel(JDLine[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      arrowWidthSpinner.setModel(new SpinnerNumberModel(0,0,0,0));
      line1CheckBox.setSelected(false);
      line2CheckBox.setSelected(false);
      line3CheckBox.setSelected(false);
      line4CheckBox.setSelected(false);
      line5CheckBox.setSelected(false);
      line6CheckBox.setSelected(false);
      line7CheckBox.setSelected(false);
      line8CheckBox.setSelected(false);
      line9CheckBox.setSelected(false);

    } else {

      JDLine p = objs[0];

      Integer value = new Integer(p.getArrowSize());
      Integer min = new Integer(0);
      Integer max = new Integer(20);
      Integer step = new Integer(1);
      SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
      arrowWidthSpinner.setModel(spModel);
      updateControls();

    }

    isUpdating = false;

  }

  private void updateControls() {
    line1CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW_NONE);
    line2CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW1_LEFT);
    line3CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW1_RIGHT);
    line4CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW1_BOTH);
    line5CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW1_CENTER);
    line6CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW2_LEFT);
    line7CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW2_RIGHT);
    line8CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW2_BOTH);
    line9CheckBox.setSelected(allObjects[0].getArrow() == JDLine.ARROW2_CENTER);
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
    int i;
    if(allObjects==null || isUpdating) return;

    initRepaint();
    Object src = e.getSource();
    if (src == line1CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW_NONE);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line2CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW1_LEFT);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line3CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW1_RIGHT);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line4CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW1_BOTH);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line5CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW1_CENTER);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line6CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW2_LEFT);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line7CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW2_RIGHT);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line8CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW2_BOTH);
      invoker.setNeedToSave(true,"Change arrow");
    } else if (src == line9CheckBox) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrow(JDLine.ARROW2_CENTER);
      invoker.setNeedToSave(true,"Change arrow");
    }
    updateControls();
    repaintObjects();
  }

  // ---------------------------------------------------------
  //Change listener
  // ---------------------------------------------------------
  public void stateChanged(ChangeEvent e) {

    int i;
    if(allObjects==null || isUpdating) return;
    initRepaint();
    Object src = e.getSource();
    Integer v;

    if (src == arrowWidthSpinner) {
      v = (Integer) arrowWidthSpinner.getValue();
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setArrowSize(v.intValue());
      invoker.setNeedToSave(true,"Change arrow size");
    }
    repaintObjects();

  }


}
