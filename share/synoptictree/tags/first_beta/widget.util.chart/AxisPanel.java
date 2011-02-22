//
// AxisPanel.java
// Description: A Class to handle 2D graphics plot
//
// JL Pons (c)ESRF 2002

package fr.esrf.tangoatk.widget.util.chart;


import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

/**
 * A class to build a axis setting panel.
 */
public class AxisPanel extends JPanel implements ActionListener, KeyListener {

  private JLAxis  pAxis;
  private JLChart pChart;
  int     type;

  private JPanel scalePanel;
  private JPanel settingPanel;

  private JLabel MinLabel;
  private JTextField MinText;
  private JLabel MaxLabel;
  private JTextField MaxText;
  private JCheckBox AutoScaleCheck;

  private JLabel ScaleLabel;
  private JComboBox ScaleCombo;
  private JCheckBox SubGridCheck;
  private JCheckBox VisibleCheck;
  private JCheckBox OppositeCheck;

  private JComboBox FormatCombo;
  private JLabel FormatLabel;

  private JLabel TitleLabel;
  private JTextField TitleText;

  private JLabel ColorLabel;
  private JLabel ColorView;
  private JButton ColorBtn;

  private JLabel PositionLabel;
  private JComboBox PositionCombo;

  public final static int Y1_TYPE = 1;
  public final static int Y2_TYPE = 2;
  public final static int X_TYPE  = 3;

  /**
   * Construct an axis setting panel.
   * @param a Axis
   * @param axisType Type of axe
   * @param parentChart parent chart (can be null)
   */
  public AxisPanel(JLAxis a,int axisType,JLChart parentChart)  {

    pAxis  = a;
    pChart = parentChart;
    type   = axisType;
    setLayout(null);

    scalePanel = new JPanel();
    scalePanel.setLayout(null);
    scalePanel.setBorder(GraphicsUtils.createTitleBorder("Scale"));

    settingPanel = new JPanel();
    settingPanel.setLayout(null);
    settingPanel.setBorder(GraphicsUtils.createTitleBorder("Axis settings"));

    MinLabel = new JLabel("Min");
    MinLabel.setFont(GraphicsUtils.labelFont);
    MinText = new JTextField();
    MinLabel.setForeground(GraphicsUtils.fColor);
    MinLabel.setEnabled(!a.isAutoScale());
    MinText.setText(Double.toString(a.getMinimum()));
    MinText.setEditable(true);
    MinText.setEnabled(!a.isAutoScale());
    MinText.setMargin(GraphicsUtils.zInset);
    MinText.addKeyListener(this);

    MaxLabel = new JLabel("Max");
    MaxLabel.setFont(GraphicsUtils.labelFont);
    MaxText = new JTextField();
    MaxLabel.setForeground(GraphicsUtils.fColor);
    MaxLabel.setHorizontalAlignment(JLabel.RIGHT);
    MaxLabel.setEnabled(!a.isAutoScale());
    MaxText.setText(Double.toString(a.getMaximum()));
    MaxText.setEditable(true);
    MaxText.setEnabled(!a.isAutoScale());
    MaxText.setMargin(GraphicsUtils.zInset);
    MaxText.addKeyListener(this);

    AutoScaleCheck = new JCheckBox("Auto scale");
    AutoScaleCheck.setFont(GraphicsUtils.labelFont);
    AutoScaleCheck.setForeground(GraphicsUtils.fColor);
    AutoScaleCheck.setSelected(a.isAutoScale());
    AutoScaleCheck.addActionListener(this);

    ScaleLabel = new JLabel("Mode");
    ScaleLabel.setFont(GraphicsUtils.labelFont);
    ScaleLabel.setForeground(GraphicsUtils.fColor);
    ScaleCombo = new JComboBox();
    ScaleCombo.setFont(GraphicsUtils.labelFont);
    ScaleCombo.addItem("Linear");
    ScaleCombo.addItem("Logarithmic");
    ScaleCombo.setSelectedIndex(a.getScale());
    ScaleCombo.addActionListener(this);

    SubGridCheck = new JCheckBox("Show sub grid");
    SubGridCheck.setFont(GraphicsUtils.labelFont);
    SubGridCheck.setForeground(GraphicsUtils.fColor);
    SubGridCheck.setSelected(a.isSubGridVisible());
    SubGridCheck.setToolTipText("You have to select the grid in the general option panel");
    SubGridCheck.addActionListener(this);

    VisibleCheck = new JCheckBox("Visible");
    VisibleCheck.setFont(GraphicsUtils.labelFont);
    VisibleCheck.setForeground(GraphicsUtils.fColor);
    VisibleCheck.setSelected(a.isVisible());
    VisibleCheck.setToolTipText("Display/Hide the axis");
    VisibleCheck.addActionListener(this);

    OppositeCheck = new JCheckBox("Draw opposite");
    OppositeCheck.setFont(GraphicsUtils.labelFont);
    OppositeCheck.setForeground(GraphicsUtils.fColor);
    OppositeCheck.setSelected(a.isDrawOpposite());
    OppositeCheck.setToolTipText("Dupplicate the axis at the opposite side");
    OppositeCheck.addActionListener(this);

    FormatCombo = new JComboBox();
    FormatCombo.setFont(GraphicsUtils.labelFont);
    FormatCombo.addItem("Automatic");
    FormatCombo.addItem("Scientific");
    FormatCombo.addItem("Time (hh:mm:ss)");
    FormatCombo.addItem("Decimal int");
    FormatCombo.addItem("Hexadecimal int");
    FormatCombo.addItem("Binary int");
    FormatCombo.addItem("Scientific int");
    FormatCombo.addItem("Date");
    FormatCombo.setSelectedIndex(a.getLabelFormat());
    FormatCombo.addActionListener(this);

    FormatLabel = new JLabel("Label format");
    FormatLabel.setFont(GraphicsUtils.labelFont);
    FormatLabel.setForeground(GraphicsUtils.fColor);

    TitleLabel = new JLabel("Title");
    TitleLabel.setFont(GraphicsUtils.labelFont);
    TitleLabel.setForeground(GraphicsUtils.fColor);
    TitleText = new JTextField();
    TitleText.setEditable(true);
    TitleText.setText(a.getName());
    TitleText.setMargin(GraphicsUtils.zInset);
    TitleText.addKeyListener(this);

    ColorLabel = new JLabel("Color");
    ColorLabel.setFont(GraphicsUtils.labelFont);
    ColorLabel.setForeground(GraphicsUtils.fColor);
    ColorView = new JLabel("");
    ColorView.setOpaque(true);
    ColorView.setBorder(BorderFactory.createLineBorder(Color.black));
    ColorView.setBackground(a.getAxisColor());
    ColorBtn = new JButton("...");
    ColorBtn.addActionListener(this);
    ColorBtn.setMargin(GraphicsUtils.zInset);

    PositionLabel = new JLabel("Position");
    PositionLabel.setFont(GraphicsUtils.labelFont);
    PositionLabel.setForeground(GraphicsUtils.fColor);
    PositionCombo = new JComboBox();
    PositionCombo.setFont(GraphicsUtils.labelFont);
    switch(type) {

      case X_TYPE:
        PositionCombo.addItem("Down");
        PositionCombo.addItem("Up");
        PositionCombo.addItem("Y1 Origin");
        PositionCombo.addItem("Y2 Origin");
        PositionCombo.setSelectedIndex(a.getPosition()-1);
        break;

      case Y1_TYPE:
        PositionCombo.addItem("Left");
        PositionCombo.addItem("X Origin");
        PositionCombo.setSelectedIndex((a.getPosition() == JLAxis.VERTICAL_ORG) ? 1 : 0);
        break;

      case Y2_TYPE:
        PositionCombo.addItem("Right");
        PositionCombo.addItem("X Origin");
        PositionCombo.setSelectedIndex((a.getPosition() == JLAxis.VERTICAL_ORG) ? 1 : 0);
        break;

    }
    PositionCombo.addActionListener(this);

    scalePanel.add(MinLabel);
    scalePanel.add(MinText);
    scalePanel.add(MaxLabel);
    scalePanel.add(MaxText);
    scalePanel.add(AutoScaleCheck);
    scalePanel.add(ScaleLabel);
    scalePanel.add(ScaleCombo);
    add(scalePanel);

    settingPanel.add(SubGridCheck);
    settingPanel.add(OppositeCheck);
    settingPanel.add(VisibleCheck);
    settingPanel.add(FormatCombo);
    settingPanel.add(FormatLabel);
    settingPanel.add(TitleLabel);
    settingPanel.add(TitleText);
    settingPanel.add(ColorLabel);
    settingPanel.add(ColorView);
    settingPanel.add(ColorBtn);
    settingPanel.add(PositionLabel);
    settingPanel.add(PositionCombo);
    add(settingPanel);

    MinLabel.setBounds(10, 20, 35, 25);
    MinText.setBounds(50, 20, 90, 25);
    MaxLabel.setBounds(145, 20, 40, 25);
    MaxText.setBounds(190, 20, 90, 25);
    ScaleLabel.setBounds(10, 50, 100, 25);
    ScaleCombo.setBounds(115, 50, 165, 25);
    AutoScaleCheck.setBounds(5, 80, 275, 25);
    scalePanel.setBounds(5,10,290,115);

    FormatLabel.setBounds(10, 20, 100, 25);
    FormatCombo.setBounds(115, 20, 165, 25);
    TitleLabel.setBounds(10, 50, 100, 25);
    TitleText.setBounds(115, 50, 165, 25);
    ColorLabel.setBounds(10, 80, 100, 25);
    ColorView.setBounds(115, 80, 130, 25);
    ColorBtn.setBounds(250, 80, 30, 25);
    PositionLabel.setBounds(10, 110, 100, 25);
    PositionCombo.setBounds(115, 110, 165, 25);
    SubGridCheck.setBounds(5, 140, 130, 25);
    OppositeCheck.setBounds(140, 140, 130, 25);
    VisibleCheck.setBounds(5, 170, 280, 25);
    settingPanel.setBounds(5,130,290,205);
  }

  public void actionPerformed(ActionEvent e) {

    if (e.getSource() == AutoScaleCheck) {

      boolean b = AutoScaleCheck.isSelected();

      pAxis.setAutoScale(b);

      if (!b) {
        try {

          double min = Double.parseDouble(MinText.getText());
          double max = Double.parseDouble(MaxText.getText());

          if (max > min) {
             pAxis.setMinimum(min);
             pAxis.setMaximum(max);
          }

        } catch (NumberFormatException err) {

        }
      }

      MinLabel.setEnabled(!b);
      MinText.setEnabled(!b);
      MaxLabel.setEnabled(!b);
      MaxText.setEnabled(!b);

      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == FormatCombo) {

      int s = FormatCombo.getSelectedIndex();
      pAxis.setLabelFormat(s);
      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == PositionCombo) {
      int s = PositionCombo.getSelectedIndex();
      switch(type) {

        case X_TYPE:
          pAxis.setPosition(s+1);
          break;

        case Y1_TYPE:
          switch(s) {
            case 0:
              pAxis.setPosition(JLAxis.VERTICAL_LEFT);
              break;
            case 1:
              pAxis.setPosition(JLAxis.VERTICAL_ORG);
              break;
          }
          break;

        case Y2_TYPE:
          switch (s) {
            case 0:
              pAxis.setPosition(JLAxis.VERTICAL_RIGHT);
              break;
            case 1:
              pAxis.setPosition(JLAxis.VERTICAL_ORG);
              break;
          }
          break;

      }
      Commit();

    } else if (e.getSource() == ScaleCombo) {

      int s = ScaleCombo.getSelectedIndex();
      pAxis.setScale(s);
      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == SubGridCheck) {

      pAxis.setSubGridVisible(SubGridCheck.isSelected());
      Commit();

    } else if (e.getSource() == OppositeCheck) {

      pAxis.setDrawOpposite(OppositeCheck.isSelected());
      Commit();

    } else if (e.getSource() == VisibleCheck) {

      pAxis.setVisible(VisibleCheck.isSelected());
      Commit();

    } else if (e.getSource() == ColorBtn) {

      Color c = JColorChooser.showDialog(this, "Choose axis Color", pAxis.getAxisColor());
      if (c != null) {
        pAxis.setAxisColor(c);
        ColorView.setBackground(c);
        Commit();
      }

    }

  }

  public void keyPressed(KeyEvent e) {}

  public void keyTyped(KeyEvent e) {}

  public void keyReleased(KeyEvent e) {

   if ((e.getSource() == MinText || e.getSource() == MaxText) && !pAxis.isAutoScale()) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {

        try {

          double min = Double.parseDouble(MinText.getText());
          double max = Double.parseDouble(MaxText.getText());

          if (max <= min) {
            error("Min must be strictly lower than max.");
            return;
          }

          if (pAxis.getScale() == JLAxis.LOG_SCALE) {
            if (min <= 0 || max <= 0) {
              error("Min and max must be strictly positive with logarithmic scale.");
              return;
            }
          }

          pAxis.setMinimum(min);
          pAxis.setMaximum(max);
          Commit();

        } catch (NumberFormatException err) {
          error("Min or Max: malformed number.");
        }

      }

      // ------------------------------------------------------------
    } else if (e.getSource() == TitleText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        pAxis.setName(TitleText.getText());
        Commit();
      }

    }

  }

  private void Commit() {
    if (pChart != null) pChart.repaint();
  }

  private void error(String m) {
    JOptionPane.showMessageDialog(this, m, "Chart options error",
      JOptionPane.ERROR_MESSAGE);
  }

}
