//
// JLChartOption.java
// Description: A Class to handle 2D graphics plot
//
// JL Pons (c)ESRF 2002

package fr.esrf.tangoatk.widget.util.chart;

import fr.esrf.tangoatk.widget.util.JSmoothLabel;
import fr.esrf.tangoatk.widget.util.ATKFontChooser;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;

/**
 * A class to display global graph settings dialog.
 */
public class JLChartOption extends JDialog implements ActionListener, MouseListener, ChangeListener, KeyListener {

  // Local declaration
  private JLChart chart;
  private JTabbedPane tabPane;
  private JButton closeBtn;

  // general panel
  private JPanel generalPanel;

  private JPanel gLegendPanel;

  private JLabel generalLegendLabel;
  private JTextField generalLegendText;

  private JCheckBox generalLabelVisibleCheck;

  private JPanel gColorFontPanel;

  private JLabel generalFontHeaderLabel;
  private JSmoothLabel generalFontHeaderSampleLabel;
  private JButton generalFontHeaderBtn;

  private JLabel generalFontLabelLabel;
  private JSmoothLabel generalFontLabelSampleLabel;
  private JButton generalFontLabelBtn;

  private JLabel generalBackColorLabel;
  private JLabel generalBackColorView;
  private JButton generalBackColorBtn;

  private JPanel gGridPanel;

  private JComboBox generalGridCombo;

  private JComboBox generalLabelPCombo;
  private JLabel generalLabelPLabel;

  private JComboBox generalGridStyleCombo;
  private JLabel generalGridStyleLabel;

  private JPanel gMiscPanel;

  private JLabel generalDurationLabel;
  private JTextField generalDurationText;


  // Axis panel
  private AxisPanel y1Panel;
  private AxisPanel y2Panel;
  private AxisPanel xPanel;

  //
  // parent: parent frame
  // chart:  Chart to edit
  /**
   * JLChartOption constructor.
   * @param parent Parent dialog
   * @param chart Chart to be edited.
   */
  public JLChartOption(JDialog parent, JLChart chart) {
    super(parent, false);
    this.chart = chart;
    initComponents();
  }

  /**
   * JLChartOption constructor.
   * @param parent Parent frame
   * @param chart Chart to be edited.
   */
  public JLChartOption(JFrame parent, JLChart chart) {
    super(parent, false);
    this.chart = chart;
    initComponents();
  }


  private void initComponents() {

    JPanel innerPane = new JPanel();
    innerPane.setLayout(null);

    addWindowListener(new WindowAdapter() {
      public void windowClosing(WindowEvent evt) {
        setVisible(false);
        dispose();
      }
    });

    setTitle("Chart properties");

    tabPane = new JTabbedPane();

    // **********************************************
    // General panel construction
    // **********************************************

    generalPanel = new JPanel();
    generalPanel.setLayout(null);

    gLegendPanel = new JPanel();
    gLegendPanel.setLayout(null);
    gLegendPanel.setBorder(GraphicsUtils.createTitleBorder("Legends"));

    gColorFontPanel= new JPanel();
    gColorFontPanel.setLayout(null);
    gColorFontPanel.setBorder(GraphicsUtils.createTitleBorder("Colors & Fonts"));

    gGridPanel= new JPanel();
    gGridPanel.setLayout(null);
    gGridPanel.setBorder(GraphicsUtils.createTitleBorder("Axis grid"));

    gMiscPanel= new JPanel();
    gMiscPanel.setLayout(null);
    gMiscPanel.setBorder(GraphicsUtils.createTitleBorder("Misc"));

    generalLegendLabel = new JLabel("Chart title");
    generalLegendLabel.setFont(GraphicsUtils.labelFont);
    generalLegendLabel.setForeground(GraphicsUtils.fColor);
    generalLegendText = new JTextField();
    generalLegendText.setEditable(true);
    generalLegendText.setText(chart.getHeader());
    generalLegendText.setMargin(GraphicsUtils.zInset);
    generalLegendText.addKeyListener(this);

    generalLabelVisibleCheck = new JCheckBox();
    generalLabelVisibleCheck.setFont(GraphicsUtils.labelFont);
    generalLabelVisibleCheck.setForeground(GraphicsUtils.fColor);
    generalLabelVisibleCheck.setText("Visible");
    generalLabelVisibleCheck.setSelected(chart.isLabelVisible());
    generalLabelVisibleCheck.addActionListener(this);

    generalBackColorLabel = new JLabel("Chart background");
    generalBackColorLabel.setFont(GraphicsUtils.labelFont);
    generalBackColorLabel.setForeground(GraphicsUtils.fColor);
    generalBackColorView = new JLabel("");
    generalBackColorView.setOpaque(true);
    generalBackColorView.setBorder(BorderFactory.createLineBorder(Color.black));
    generalBackColorView.setBackground(chart.getChartBackground());
    generalBackColorBtn = new JButton("...");
    generalBackColorBtn.addMouseListener(this);
    generalBackColorBtn.setMargin(GraphicsUtils.zInset);

    generalLabelPLabel = new JLabel("Placement");
    generalLabelPLabel.setHorizontalAlignment(JLabel.RIGHT);
    generalLabelPLabel.setFont(GraphicsUtils.labelFont);
    generalLabelPLabel.setForeground(GraphicsUtils.fColor);

    generalLabelPCombo = new JComboBox();
    generalLabelPCombo.setFont(GraphicsUtils.labelFont);
    generalLabelPCombo.addItem("Bottom");
    generalLabelPCombo.addItem("Top");
    generalLabelPCombo.addItem("Right");
    generalLabelPCombo.addItem("Left");
    generalLabelPCombo.setSelectedIndex(chart.getLabelPlacement());
    generalLabelPCombo.addActionListener(this);

    generalGridCombo = new JComboBox();
    generalGridCombo.setFont(GraphicsUtils.labelFont);
    generalGridCombo.addItem("None");
    generalGridCombo.addItem("On X");
    generalGridCombo.addItem("On Y1");
    generalGridCombo.addItem("On Y2");
    generalGridCombo.addItem("On X and Y1");
    generalGridCombo.addItem("On X and Y2");

    boolean vx = chart.getXAxis().isGridVisible();
    boolean vy1 = chart.getY1Axis().isGridVisible();
    boolean vy2 = chart.getY2Axis().isGridVisible();

    int sel = 0;
    if (vx && !vy1 && !vy2) sel = 1;
    if (!vx && vy1 && !vy2) sel = 2;
    if (!vx && !vy1 && vy2) sel = 3;
    if (vx && vy1 && !vy2) sel = 4;
    if (vx && !vy1 && vy2) sel = 5;

    generalGridCombo.setSelectedIndex(sel);
    generalGridCombo.addActionListener(this);

    generalGridStyleLabel = new JLabel("Style");
    generalGridStyleLabel.setFont(GraphicsUtils.labelFont);
    generalGridStyleLabel.setHorizontalAlignment(JLabel.RIGHT);
    generalGridStyleLabel.setForeground(GraphicsUtils.fColor);

    generalGridStyleCombo = new JComboBox();
    generalGridStyleCombo.setFont(GraphicsUtils.labelFont);
    generalGridStyleCombo.addItem("Solid");
    generalGridStyleCombo.addItem("Dot");
    generalGridStyleCombo.addItem("Short dash");
    generalGridStyleCombo.addItem("Long dash");
    generalGridStyleCombo.addItem("Dot dash");
    generalGridStyleCombo.setSelectedIndex(chart.getY1Axis().getGridStyle());
    generalGridStyleCombo.addActionListener(this);

    generalDurationLabel = new JLabel("Display duration (s)");
    generalDurationLabel.setFont(GraphicsUtils.labelFont);
    generalDurationLabel.setForeground(GraphicsUtils.fColor);
    generalDurationText = new JTextField();
    generalDurationText.setEditable(true);
    generalDurationText.setToolTipText("Type Infinity to disable");
    generalDurationText.setText(Double.toString(chart.getDisplayDuration() / 1000.0));
    generalDurationText.setMargin(GraphicsUtils.zInset);
    generalDurationText.addKeyListener(this);

    generalFontHeaderLabel = new JLabel("Header font");
    generalFontHeaderLabel.setFont(GraphicsUtils.labelFont);
    generalFontHeaderLabel.setForeground(GraphicsUtils.fColor);
    generalFontHeaderSampleLabel = new JSmoothLabel();
    generalFontHeaderSampleLabel.setText("Sample text");
    generalFontHeaderSampleLabel.setForeground(GraphicsUtils.fColor);
    generalFontHeaderSampleLabel.setOpaque(false);
    generalFontHeaderSampleLabel.setFont(chart.getHeaderFont());
    generalFontHeaderBtn = new JButton("...");
    generalFontHeaderBtn.addMouseListener(this);
    generalFontHeaderBtn.setMargin(GraphicsUtils.zInset);

    generalFontLabelLabel = new JLabel("Label font");
    generalFontLabelLabel.setFont(GraphicsUtils.labelFont);
    generalFontLabelLabel.setForeground(GraphicsUtils.fColor);
    generalFontLabelSampleLabel = new JSmoothLabel();
    generalFontLabelSampleLabel.setText("Sample 0123456789");
    generalFontLabelSampleLabel.setForeground(GraphicsUtils.fColor);
    generalFontLabelSampleLabel.setOpaque(false);
    generalFontLabelSampleLabel.setFont(chart.getXAxis().getFont());
    generalFontLabelBtn = new JButton("...");
    generalFontLabelBtn.addMouseListener(this);
    generalFontHeaderBtn.setMargin(GraphicsUtils.zInset);

    gLegendPanel.add(generalLabelVisibleCheck);
    gLegendPanel.add(generalLabelPLabel);
    gLegendPanel.add(generalLabelPCombo);
    generalPanel.add(gLegendPanel);

    gGridPanel.add(generalGridCombo);
    gGridPanel.add(generalGridStyleLabel);
    gGridPanel.add(generalGridStyleCombo);
    generalPanel.add(gGridPanel);

    gColorFontPanel.add(generalBackColorLabel);
    gColorFontPanel.add(generalBackColorView);
    gColorFontPanel.add(generalBackColorBtn);
    gColorFontPanel.add(generalFontHeaderLabel);
    gColorFontPanel.add(generalFontHeaderSampleLabel);
    gColorFontPanel.add(generalFontHeaderBtn);
    gColorFontPanel.add(generalFontLabelLabel);
    gColorFontPanel.add(generalFontLabelSampleLabel);
    gColorFontPanel.add(generalFontLabelBtn);
    generalPanel.add(gColorFontPanel);

    gMiscPanel.add(generalLegendLabel);
    gMiscPanel.add(generalLegendText);
    gMiscPanel.add(generalDurationLabel);
    gMiscPanel.add(generalDurationText);
    generalPanel.add(gMiscPanel);

    generalLabelVisibleCheck.setBounds(5, 20, 80, 25);
    generalLabelPLabel.setBounds(90, 20, 95, 25);
    generalLabelPCombo.setBounds(190, 20, 95, 25);
    gLegendPanel.setBounds(5,10,290,55);

    generalBackColorLabel.setBounds(10, 20, 140, 25);
    generalBackColorView.setBounds(155, 20, 95, 25);
    generalBackColorBtn.setBounds(255, 20, 30, 25);
    generalFontHeaderLabel.setBounds(10, 50, 90, 25);
    generalFontHeaderSampleLabel.setBounds(105, 50, 145, 25);
    generalFontHeaderBtn.setBounds(255, 50, 30, 25);
    generalFontLabelLabel.setBounds(10, 80, 90, 25);
    generalFontLabelSampleLabel.setBounds(105, 80, 145, 25);
    generalFontLabelBtn.setBounds(255, 80, 30, 25);
    gColorFontPanel.setBounds(5,70,290,115);

    generalGridCombo.setBounds(10, 20, 120, 25);
    generalGridStyleLabel.setBounds(135, 20, 45, 25);
    generalGridStyleCombo.setBounds(185, 20, 100, 25);
    gGridPanel.setBounds(5,190,290,55);

    generalLegendLabel.setBounds(10, 20, 70, 25);
    generalLegendText.setBounds(85, 20, 200, 25);
    generalDurationLabel.setBounds(10, 50, 120, 25);
    generalDurationText.setBounds(135, 50, 150, 25);
    gMiscPanel.setBounds(5,250,290,85);

    // **********************************************
    // Axis panel construction
    // **********************************************
    y1Panel = new AxisPanel(chart.getY1Axis(),AxisPanel.Y1_TYPE,chart);
    y2Panel = new AxisPanel(chart.getY2Axis(),AxisPanel.Y2_TYPE,chart);
    xPanel  = new AxisPanel(chart.getXAxis() ,AxisPanel.X_TYPE ,chart);

    // Global frame construction

    tabPane.add("General", generalPanel);
    if(chart.getXAxis().getAnnotation()!=JLAxis.TIME_ANNO) tabPane.add("X axis", xPanel);
    tabPane.add("Y1 axis", y1Panel);
    tabPane.add("Y2 axis", y2Panel);

    innerPane.add(tabPane);

    closeBtn = new JButton();
    closeBtn.setText("Close");
    innerPane.add(closeBtn);

    tabPane.setBounds(5, 5, 300, 370);
    closeBtn.setBounds(225, 380, 80, 25);

    closeBtn.addMouseListener(this);

    innerPane.setPreferredSize(new Dimension(310,410));
    setContentPane(innerPane);
    setResizable(false);

  }

  private void Commit() {
    if (chart != null) chart.repaint();
  }

  // Mouse Listener
  public void mouseClicked(MouseEvent e) {
    // ------------------------------
    if (e.getSource() == closeBtn) {
      setVisible(false);
      dispose();
    } else if (e.getSource() == generalBackColorBtn) {
      Color c = JColorChooser.showDialog(this, "Choose background Color", chart.getChartBackground());
      if (c != null) {
        chart.setChartBackground(c);
        generalBackColorView.setBackground(c);
        Commit();
      }
    } else if (e.getSource() == generalFontHeaderBtn) {

      Font f = ATKFontChooser.getNewFont(this,"Choose Header Font", chart.getHeaderFont());
      if (f != null) {
        chart.setHeaderFont(f);
        generalFontHeaderSampleLabel.setFont(f);
        Commit();
      }

    } else if (e.getSource() == generalFontLabelBtn) {

      Font f = ATKFontChooser.getNewFont(this,"Choose label Font", chart.getXAxis().getFont());
      if (f != null) {
        chart.getXAxis().setFont(f);
        chart.getY1Axis().setFont(f);
        chart.getY2Axis().setFont(f);
        chart.setLabelFont(f);
        generalFontLabelSampleLabel.setFont(f);
        Commit();
      }

    }

  }

  public void mouseEntered(MouseEvent e) {
  }

  public void mouseExited(MouseEvent e) {
  }

  public void mousePressed(MouseEvent e) {
  }

  public void mouseReleased(MouseEvent e) {
  }

  //***************************************************************
  //Action listener
  //***************************************************************
  public void actionPerformed(ActionEvent e) {

    // General ----------------------------------------------------
    if (e.getSource() == generalLabelVisibleCheck) {

      chart.setLabelVisible(generalLabelVisibleCheck.isSelected());
      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == generalGridCombo) {

      int sel = generalGridCombo.getSelectedIndex();

      switch (sel) {
        case 1: // On X
          chart.getXAxis().setGridVisible(true);
          chart.getY1Axis().setGridVisible(false);
          chart.getY2Axis().setGridVisible(false);
          break;
        case 2: // On Y1
          chart.getXAxis().setGridVisible(false);
          chart.getY1Axis().setGridVisible(true);
          chart.getY2Axis().setGridVisible(false);
          break;
        case 3: // On Y2
          chart.getXAxis().setGridVisible(false);
          chart.getY1Axis().setGridVisible(false);
          chart.getY2Axis().setGridVisible(true);
          break;
        case 4: // On X,Y1
          chart.getXAxis().setGridVisible(true);
          chart.getY1Axis().setGridVisible(true);
          chart.getY2Axis().setGridVisible(false);
          break;
        case 5: // On X,Y2
          chart.getXAxis().setGridVisible(true);
          chart.getY1Axis().setGridVisible(false);
          chart.getY2Axis().setGridVisible(true);
          break;
        default: // None
          chart.getXAxis().setGridVisible(false);
          chart.getY1Axis().setGridVisible(false);
          chart.getY2Axis().setGridVisible(false);
          break;
      }
      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == generalGridStyleCombo) {

      int s = generalGridStyleCombo.getSelectedIndex();
      chart.getXAxis().setGridStyle(s);
      chart.getY1Axis().setGridStyle(s);
      chart.getY2Axis().setGridStyle(s);
      Commit();

      // ------------------------------------------------------------
    } else if (e.getSource() == generalLabelPCombo) {

      int s = generalLabelPCombo.getSelectedIndex();
      chart.setLabelPlacement(s);
      Commit();

    }
  }

  //***************************************************************
  //Change listener
  //***************************************************************
  public void stateChanged(ChangeEvent e) {
  }

  //***************************************************************
  //Key listener
  //***************************************************************
  public void keyPressed(KeyEvent e) {
  }

  public void keyTyped(KeyEvent e) {
  }

  public void keyReleased(KeyEvent e) {

    // General ------------------------------------------------------------
    if (e.getSource() == generalLegendText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        chart.setHeader(generalLegendText.getText());
        Commit();
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        generalLegendText.setText(chart.getHeader());
      }

    } else if (e.getSource() == generalDurationText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {


        if (generalDurationText.getText().equalsIgnoreCase("infinty")) {
          chart.setDisplayDuration(Double.POSITIVE_INFINITY);
          return;
        }

        try {

          double d = Double.parseDouble(generalDurationText.getText());
          chart.setDisplayDuration(d * 1000);
          Commit();

        } catch (NumberFormatException err) {
          error("Display duration: malformed number.");
        }
        Commit();
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        generalLegendText.setText(Double.toString(chart.getDisplayDuration() / 1000.0));
      }

    }

  } // End keyReleased

  // Error message
  private void error(String m) {
    JOptionPane.showMessageDialog(this, m, "Chart options error",
      JOptionPane.ERROR_MESSAGE);
  }


}
