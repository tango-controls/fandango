package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.*;
import java.awt.event.*;


class JDGradientDialog extends JDialog implements ActionListener,ChangeListener {

  private JDGradientViewer viewer;
  private JLabel color1Label;
  private JButton color1Button;
  private JLabel color2Label;
  private JButton color2Button;
  private JLabel   ampLabel;
  private JSpinner ampSpinner;
  private JLabel   offLabel;
  private JSpinner offSpinner;
  private JCheckBox cyclicCheckBox;
  private JDObject[] allObjects;
  private JComponent invoker;
  private JButton applyButton;
  private JButton dismissButton;
  private boolean modified = false;

  public JDGradientDialog(JDialog parent,JDObject[] p, JComponent jc) {

    super(parent,true);
    allObjects = p;
    invoker = jc;
    initComponents();

  }

  public JDGradientDialog(JFrame parent,JDObject[] p, JComponent jc) {

    super(parent,true);
    allObjects = p;
    invoker = jc;
    initComponents();

  }

  private void initComponents() {

    Integer value;
    Integer min;
    Integer max;
    Integer step;
    SpinnerNumberModel spModel;

    JPanel innerPanel = new JPanel();
    innerPanel.setLayout(null);

    viewer = new JDGradientViewer();
    viewer.setGradient(allObjects[0].gradientX1,
                       allObjects[0].gradientY1,
                       allObjects[0].gradientC1,
                       allObjects[0].gradientX2,
                       allObjects[0].gradientY2,
                       allObjects[0].gradientC2,
                       allObjects[0].gradientCyclic);
    viewer.setBorder(BorderFactory.createEtchedBorder());
    viewer.setBounds(5,5,200,200);
    innerPanel.add(viewer);

    color1Label = JDUtils.createLabel("Color 1");
    color1Label.setBounds(210, 5, 90, 24);
    innerPanel.add(color1Label);
    color1Button = new JButton("...");
    color1Button.setMargin(new Insets(0, 0, 0, 0));
    color1Button.setBackground(allObjects[0].gradientC1);
    color1Button.addActionListener(this);
    color1Button.setBounds(300, 5, 60, 24);
    innerPanel.add(color1Button);

    color2Label = JDUtils.createLabel("Color 2");
    color2Label.setBounds(210, 35, 90, 24);
    innerPanel.add(color2Label);
    color2Button = new JButton("...");
    color2Button.setMargin(new Insets(0, 0, 0, 0));
    color2Button.setBackground(allObjects[0].gradientC2);
    color2Button.addActionListener(this);
    color2Button.setBounds(300, 35, 60, 24);
    innerPanel.add(color2Button);

    ampLabel = new JLabel("Amplitude");
    ampLabel.setFont(JDUtils.labelFont);
    ampLabel.setForeground(JDUtils.labelColor);
    ampLabel.setBounds(210, 65, 90, 24);
    innerPanel.add(ampLabel);

    ampSpinner = new JSpinner();
    value = new Integer(viewer.getAmplitupe());
    min = new Integer(1);
    max = new Integer(65535);
    step = new Integer(1);
    spModel = new SpinnerNumberModel(value, min, max, step);
    ampSpinner.setModel(spModel);
    ampSpinner.addChangeListener(this);
    ampSpinner.setBounds(300, 65, 60, 26);
    innerPanel.add(ampSpinner);

    offLabel = new JLabel("Offset");
    offLabel.setFont(JDUtils.labelFont);
    offLabel.setForeground(JDUtils.labelColor);
    offLabel.setBounds(210, 95, 90, 24);
    innerPanel.add(offLabel);

    offSpinner = new JSpinner();
    value = new Integer(viewer.getOffset());
    min = new Integer(0);
    max = new Integer(65535);
    step = new Integer(1);
    spModel = new SpinnerNumberModel(value, min, max, step);
    offSpinner.setModel(spModel);
    offSpinner.addChangeListener(this);
    offSpinner.setBounds(300, 95, 60, 26);
    innerPanel.add(offSpinner);

    cyclicCheckBox = new JCheckBox("Cyclic");
    cyclicCheckBox.setFont(JDUtils.labelFont);
    cyclicCheckBox.setForeground(JDUtils.labelColor);
    cyclicCheckBox.setBounds(210, 125, 150, 25);
    cyclicCheckBox.setSelected(viewer.isCyclic());
    cyclicCheckBox.addActionListener(this);
    innerPanel.add(cyclicCheckBox);

    applyButton = new JButton("Apply");
    applyButton.setFont(JDUtils.labelFont);
    applyButton.addActionListener(this);
    applyButton.setBounds(5, 210, 100, 26);
    innerPanel.add(applyButton);

    dismissButton = new JButton("Dismiss");
    dismissButton.setFont(JDUtils.labelFont);
    dismissButton.addActionListener(this);
    dismissButton.setBounds(260, 210, 100, 26);
    innerPanel.add(dismissButton);

    setTitle("Gradient properties");
    setContentPane(innerPanel);

  }

  private void repaintObjects() {
    Rectangle newRect = allObjects[0].getRepaintRect();
    for (int i = 1; i < allObjects.length; i++)
      newRect = newRect.union(allObjects[i].getRepaintRect());
    invoker.repaint(newRect);
  }

  public boolean editGradient() {

    ATKGraphicsUtils.centerDialog(this,367,240);
    setVisible(true);
    return modified;

  }

  public void actionPerformed(ActionEvent e) {

    Object src = e.getSource();
    if( src==color1Button ) {
      Color c = JColorChooser.showDialog(this, "Choose 1st color", color1Button.getBackground());
      if (c != null) {
        viewer.setColor1(c);
        color1Button.setBackground(c);
      }
    } else if( src==color2Button ) {
      Color c = JColorChooser.showDialog(this, "Choose 2nd color", color2Button.getBackground());
      if (c != null) {
        viewer.setColor2(c);
        color2Button.setBackground(c);
      }
    } else if( src==cyclicCheckBox ) {
      viewer.setCyclic(cyclicCheckBox.isSelected());
    } else if( src==applyButton ) {
      for(int i=0;i<allObjects.length;i++) {
        allObjects[i].setGradientFillParam(viewer.getX1(),viewer.getY1(),viewer.getColor1(),
                                           viewer.getX2(),viewer.getY2(),viewer.getColor2(),
                                           viewer.isCyclic());
      }
      modified = true;
      repaintObjects();
    } else if( src==dismissButton ) {
      dispose();
      setVisible(false);
    }

  }

  public void stateChanged(ChangeEvent e) {

    Object src = e.getSource();
    Integer v;
    if (src == ampSpinner) {
      v = (Integer) ampSpinner.getValue();
      viewer.setAmplitute(v.intValue());
    } else if (src == offSpinner) {
      v = (Integer) offSpinner.getValue();
      viewer.setOffset(v.intValue());
    }

  }

}
