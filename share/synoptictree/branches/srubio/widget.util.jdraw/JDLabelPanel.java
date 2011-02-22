/** A panel for JDLabel private properties */
package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKFontChooser;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class JDLabelPanel extends JPanel implements ActionListener {

  private JScrollPane textView;
  private JTextArea textText;
  private JButton applyTextBtn;

  private JLabel fontLabel;
  private JButton fontBtn;

  private JLabel alignmentLabel;
  private JComboBox alignmentCombo;

  private JLabel alignment2Label;
  private JComboBox alignment2Combo;

  private JLabel orientationLabel;
  private JComboBox orientationCombo;

  private JDLabel allObjects[] = null;
  private JDrawEditor invoker;
  private Rectangle oldRect;
  private boolean isUpdating = false;

  public JDLabelPanel(JDLabel[] p, JDrawEditor jc) {

    invoker = jc;
    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel namePanel = new JPanel(null);
    namePanel.setBorder(JDUtils.createTitleBorder("Text"));
    namePanel.setBounds(5,5,370,130);

    textText = new JTextArea();
    textText.setEditable(true);
    textText.setFont(JDUtils.labelFont);
    textView = new JScrollPane(textText);
    textView.setBounds(10, 20, 350, 70);
    namePanel.add(textView);

    applyTextBtn = new JButton("Apply");
    applyTextBtn.setFont(JDUtils.labelFont);
    applyTextBtn.addActionListener(this);
    applyTextBtn.setBounds(260,95,100,25);
    namePanel.add(applyTextBtn);

    add(namePanel);

    // ------------------------------------------------------------------------------------
    JPanel stylePanel = new JPanel(null);
    stylePanel.setBorder(JDUtils.createTitleBorder("Text styles"));
    stylePanel.setBounds(5,140,370,145);

    fontLabel = new JLabel("Font");
    fontLabel.setFont(JDUtils.labelFont);
    fontLabel.setForeground(JDUtils.labelColor);
    fontLabel.setBounds(10, 20, 135, 24);
    stylePanel.add(fontLabel);

    fontBtn = new JButton();
    fontBtn.setText("Choose");
    fontBtn.setMargin(new Insets(0, 0, 0, 0));
    fontBtn.setFont(JDUtils.labelFont);
    fontBtn.setBounds(220, 20, 140, 24);
    fontBtn.addActionListener(this);
    stylePanel.add(fontBtn);

    alignmentLabel = new JLabel("Horizontal alignment");
    alignmentLabel.setFont(JDUtils.labelFont);
    alignmentLabel.setForeground(JDUtils.labelColor);
    alignmentLabel.setBounds(10, 50, 125, 25);
    stylePanel.add(alignmentLabel);

    alignmentCombo = new JComboBox();
    alignmentCombo.setFont(JDUtils.labelFont);
    alignmentCombo.addItem("Center");
    alignmentCombo.addItem("Left");
    alignmentCombo.addItem("Right");
    alignmentCombo.addActionListener(this);
    alignmentCombo.setBounds(220, 50, 140, 25);
    stylePanel.add(alignmentCombo);

    alignment2Label = new JLabel("Vertical alignment");
    alignment2Label.setFont(JDUtils.labelFont);
    alignment2Label.setForeground(JDUtils.labelColor);
    alignment2Label.setBounds(10, 80, 125, 25);
    stylePanel.add(alignment2Label);

    alignment2Combo = new JComboBox();
    alignment2Combo.setFont(JDUtils.labelFont);
    alignment2Combo.addItem("Center");
    alignment2Combo.addItem("Up");
    alignment2Combo.addItem("Down");
    alignment2Combo.addActionListener(this);
    alignment2Combo.setBounds(220, 80, 140, 25);
    stylePanel.add(alignment2Combo);

    orientationLabel = new JLabel("Text orientation");
    orientationLabel.setFont(JDUtils.labelFont);
    orientationLabel.setForeground(JDUtils.labelColor);
    orientationLabel.setBounds(10, 110, 100, 25);
    stylePanel.add(orientationLabel);

    orientationCombo = new JComboBox();
    orientationCombo.setFont(JDUtils.labelFont);
    orientationCombo.addItem("Left to right");
    orientationCombo.addItem("Bottom to top");
    orientationCombo.addItem("Left to right");
    orientationCombo.addItem("Top to bottom");
    orientationCombo.addActionListener(this);
    orientationCombo.setBounds(220, 110, 140, 25);
    stylePanel.add(orientationCombo);
    add(stylePanel);

    updatePanel(p);

  }

  public void updatePanel(JDLabel[] objs) {

    allObjects = objs;
    isUpdating = true;

    if (objs == null || objs.length <= 0) {

      textText.setText("");
      fontLabel.setText("Font: ");
      alignmentCombo.setSelectedIndex(-1);
      alignment2Combo.setSelectedIndex(-1);
      orientationCombo.setSelectedIndex(-1);

    } else {

      JDLabel p = objs[0];

      fontLabel.setText("Font: [" + JDUtils.buildFontName(p.getFont())+ "]"); 
      textText.setText(p.getText());
      alignmentCombo.setSelectedIndex(p.getHorizontalAlignment());
      alignment2Combo.setSelectedIndex(p.getHorizontalAlignment());
      orientationCombo.setSelectedIndex(p.getOrientation());

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
    if (src == fontBtn) {
      Font newFont = ATKFontChooser.getNewFont(this,"Choose label font",allObjects[0].getFont());
      if (newFont != null) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].setFont(newFont,invoker.resizeLabelOnFontChange);
        fontLabel.setText("Font: [" + JDUtils.buildFontName(newFont) + "]");
        invoker.setNeedToSave(true,"Change font");
      }
    } else if (src == alignmentCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setHorizontalAlignment(alignmentCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change H. alignment");
    } else if (src == alignment2Combo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setVerticalAlignment(alignment2Combo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change V. alignment");
    } else if (src == orientationCombo) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setOrientation(orientationCombo.getSelectedIndex());
      invoker.setNeedToSave(true,"Change orientation");
    } else if (src == applyTextBtn ) {
      for (i = 0; i < allObjects.length; i++)
        allObjects[i].setText(textText.getText(),invoker.resizeLabelOnTextChange);
      invoker.setNeedToSave(true,"Change text");
    }

    repaintObjects();
  }


}
