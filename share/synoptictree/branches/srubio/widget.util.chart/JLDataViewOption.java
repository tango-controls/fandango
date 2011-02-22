//
// JLDataViewOption.java
// Description: A Class to handle 2D graphics plot
//
// JL Pons (c)ESRF 2002

package fr.esrf.tangoatk.widget.util.chart;


import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;

/**
 * A class to display dataview settings dialog.
 * @author JL Pons
 */
public class JLDataViewOption extends JDialog implements ActionListener, MouseListener, ChangeListener, KeyListener {


  // Local declaration
  private JLDataView dataView;
  protected JLChart chart;
  protected JLabel nameLabel;
  private JTabbedPane tabPane;
  protected JButton closeBtn;

  // DataView general option panel
  private JPanel linePanel;

  private JLabel viewTypeLabel;
  private JComboBox viewTypeCombo;

  private JLabel lineColorView;
  private JButton lineColorBtn;
  private JLabel lineColorLabel;

  private JLabel fillColorView;
  private JButton fillColorBtn;
  private JLabel fillColorLabel;

  private JLabel fillStyleLabel;
  private JComboBox fillStyleCombo;

  private JLabel lineWidthLabel;
  private JSpinner lineWidthSpinner;

  private JLabel lineDashLabel;
  private JComboBox lineDashCombo;

  private JLabel lineNameLabel;
  private JTextField lineNameText;

  // Bar panel
  private JPanel barPanel;

  private JLabel barWidthLabel;
  private JSpinner barWidthSpinner;

  private JLabel    fillMethodLabel;
  private JComboBox fillMethodCombo;

  // marker option panel
  private JPanel markerPanel;

  private JLabel markerColorView;
  private JButton markerColorBtn;
  private JLabel markerColorLabel;

  private JLabel markerSizeLabel;
  private JSpinner markerSizeSpinner;

  private JLabel markerStyleLabel;
  private JComboBox markerStyleCombo;

  private JCheckBox labelVisibleCheck;

  //transformation panel
  private JPanel transformPanel;

  private JTextArea transformHelpLabel;

  private JLabel transformA0Label;
  private JTextField transformA0Text;

  private JLabel transformA1Label;
  private JTextField transformA1Text;

  private JLabel transformA2Label;
  private JTextField transformA2Text;

  //Interpolation panel
  private JPanel interpPanel;

  private ButtonGroup          methodIntBtnGrp;
  private JRadioButton         noInterpBtn;
  private JRadioButton         linearBtn;
  private JRadioButton         cosineBtn;
  private JRadioButton         cubicBtn;
  private JRadioButton         hermiteBtn;
  private JSpinner             stepSpinner;
  private JTextField           tensionText;
  private JTextField           biasText;

  //Smoothing panel
  private JPanel smoothPanel;

  private ButtonGroup          methodSmBtnGrp;
  private JRadioButton         noSmoothBtn;
  private JRadioButton         flatSmoothBtn;
  private JRadioButton         triangularSmoothBtn;
  private JRadioButton         gaussianSmoothBtn;
  private JSpinner             neighborSpinner;
  private JTextField           sigmaText;
  private ButtonGroup          methodExtBtnGrp;
  private JRadioButton         noExtBtn;
  private JRadioButton         flatExtBtn;
  private JRadioButton         linearExtBtn;

  //Math panel
  private JPanel mathPanel;

  private ButtonGroup          mathBtnGrp;
  private JRadioButton         noMathBtn;
  private JRadioButton         derivativeBtn;
  private JRadioButton         integralBtn;
  private JRadioButton         fftModBtn;
  private JRadioButton         fftPhaseBtn;

  /**
   * Dialog constructor.
   * @param parent Parent dialog
   * @param chart Chart used to commit change (can be null)
   * @param v DataView to edit
   */
  public JLDataViewOption(JDialog parent, JLChart chart, JLDataView v) {
    super(parent, true);
    dataView = v;
    this.chart = chart;
    initComponents();
  }

  /**
   * Dialog constructor.
   * @param parent Parent frame
   * @param chart Chart used to commit change (can be null)
   * @param v DataView to edit
   */
  public JLDataViewOption(JFrame parent, JLChart chart, JLDataView v) {
    super(parent, true);
    dataView = v;
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

    setTitle("Data view options");

    tabPane = new JTabbedPane();
    tabPane.setFont(GraphicsUtils.labelFont);

    // Line panel construction

    linePanel = new JPanel();
    linePanel.setLayout(null);

    viewTypeLabel = new JLabel("View type");
    viewTypeLabel.setFont(GraphicsUtils.labelFont);
    viewTypeLabel.setForeground(GraphicsUtils.fColor);

    viewTypeCombo = new JComboBox();
    viewTypeCombo.setFont(GraphicsUtils.labelFont);
    viewTypeCombo.addItem("Line");
    viewTypeCombo.addItem("Bar graph");
    viewTypeCombo.setSelectedIndex(dataView.getViewType());
    viewTypeCombo.addActionListener(this);

    lineColorView = new JLabel("");
    lineColorView.setBackground(dataView.getColor());
    lineColorView.setOpaque(true);
    lineColorView.setBorder(BorderFactory.createLineBorder(Color.black));
    lineColorBtn = new JButton("...");
    lineColorBtn.addMouseListener(this);
    lineColorLabel = new JLabel("Line Color");
    lineColorLabel.setFont(GraphicsUtils.labelFont);
    lineColorLabel.setForeground(GraphicsUtils.fColor);

    fillColorView = new JLabel("");
    fillColorView.setBackground(dataView.getFillColor());
    fillColorView.setOpaque(true);
    fillColorView.setBorder(BorderFactory.createLineBorder(Color.black));
    fillColorBtn = new JButton("...");
    fillColorBtn.addMouseListener(this);
    fillColorLabel = new JLabel("Fill Color");
    fillColorLabel.setFont(GraphicsUtils.labelFont);
    fillColorLabel.setForeground(GraphicsUtils.fColor);

    lineWidthLabel = new JLabel("Line Width");
    lineWidthLabel.setFont(GraphicsUtils.labelFont);
    lineWidthLabel.setForeground(GraphicsUtils.fColor);
    lineWidthSpinner = new JSpinner();
    Integer value = new Integer(dataView.getLineWidth());
    Integer min = new Integer(0);
    Integer max = new Integer(10);
    Integer step = new Integer(1);
    SpinnerNumberModel spModel = new SpinnerNumberModel(value, min, max, step);
    lineWidthSpinner.setModel(spModel);
    lineWidthSpinner.addChangeListener(this);

    lineDashLabel = new JLabel("Line style");
    lineDashLabel.setFont(GraphicsUtils.labelFont);
    lineDashLabel.setForeground(GraphicsUtils.fColor);
    lineDashCombo = new JComboBox();
    lineDashCombo.setFont(GraphicsUtils.labelFont);
    lineDashCombo.addItem("Solid");
    lineDashCombo.addItem("Point dash");
    lineDashCombo.addItem("Short dash");
    lineDashCombo.addItem("Long dash");
    lineDashCombo.addItem("Dot dash");
    lineDashCombo.setSelectedIndex(dataView.getStyle());
    lineDashCombo.addActionListener(this);

    fillStyleLabel = new JLabel("Fill style");
    fillStyleLabel.setFont(GraphicsUtils.labelFont);
    fillStyleLabel.setForeground(GraphicsUtils.fColor);
    fillStyleCombo = new JComboBox();
    fillStyleCombo.setFont(GraphicsUtils.labelFont);
    fillStyleCombo.addItem("No fill");
    fillStyleCombo.addItem("Solid");
    fillStyleCombo.addItem("Large leff hatch");
    fillStyleCombo.addItem("Large right hatch");
    fillStyleCombo.addItem("Large cross hatch");
    fillStyleCombo.addItem("Small leff hatch");
    fillStyleCombo.addItem("Small right hatch");
    fillStyleCombo.addItem("Small cross hatch");
    fillStyleCombo.addItem("Dot pattern 1");
    fillStyleCombo.addItem("Dot pattern 2");
    fillStyleCombo.addItem("Dot pattern 3");
    fillStyleCombo.setSelectedIndex(dataView.getFillStyle());
    fillStyleCombo.addActionListener(this);

    lineNameLabel = new JLabel("Name");
    lineNameLabel.setFont(GraphicsUtils.labelFont);
    lineNameLabel.setForeground(GraphicsUtils.fColor);
    lineNameText = new JTextField();
    lineNameText.setEditable(true);
    lineNameText.setText(dataView.getName());
    lineNameText.setMargin(GraphicsUtils.zInset);
    lineNameText.addKeyListener(this);

    linePanel.add(viewTypeLabel);
    linePanel.add(viewTypeCombo);
    linePanel.add(lineColorLabel);
    linePanel.add(lineColorView);
    linePanel.add(lineColorBtn);
    linePanel.add(fillColorLabel);
    linePanel.add(fillColorView);
    linePanel.add(fillColorBtn);
    linePanel.add(lineWidthLabel);
    linePanel.add(lineWidthSpinner);
    linePanel.add(lineDashLabel);
    linePanel.add(lineDashCombo);
    linePanel.add(fillStyleLabel);
    linePanel.add(fillStyleCombo);
    linePanel.add(lineNameLabel);
    linePanel.add(lineNameText);

    viewTypeLabel.setBounds(10, 10, 100, 25);
    viewTypeCombo.setBounds(115, 10, 125, 25);

    lineColorLabel.setBounds(10, 40, 100, 25);
    lineColorView.setBounds(115, 40, 80, 25);
    lineColorBtn.setBounds(200, 40, 40, 27);

    fillColorLabel.setBounds(10, 70, 100, 25);
    fillColorView.setBounds(115, 70, 80, 25);
    fillColorBtn.setBounds(200, 70, 40, 27);

    fillStyleLabel.setBounds(10, 100, 100, 25);
    fillStyleCombo.setBounds(115, 100, 125, 25);

    lineWidthLabel.setBounds(10, 130, 100, 25);
    lineWidthSpinner.setBounds(115, 130, 125, 25);

    lineDashLabel.setBounds(10, 160, 100, 25);
    lineDashCombo.setBounds(115, 160, 125, 25);

    lineNameLabel.setBounds(10, 190, 100, 25);
    lineNameText.setBounds(115, 190, 125, 25);

    // Bar panel construction
    barPanel = new JPanel();
    barPanel.setLayout(null);

    barWidthLabel = new JLabel("Bar Width");
    barWidthLabel.setFont(GraphicsUtils.labelFont);
    barWidthLabel.setForeground(GraphicsUtils.fColor);
    barWidthSpinner = new JSpinner();
    value = new Integer(dataView.getBarWidth());
    min = new Integer(0);
    max = new Integer(100);
    step = new Integer(1);
    spModel = new SpinnerNumberModel(value, min, max, step);
    barWidthSpinner.setModel(spModel);
    barWidthSpinner.addChangeListener(this);

    fillMethodLabel = new JLabel("Filling method");
    fillMethodLabel.setFont(GraphicsUtils.labelFont);
    fillMethodLabel.setForeground(GraphicsUtils.fColor);
    fillMethodCombo = new JComboBox();
    fillMethodCombo.setFont(GraphicsUtils.labelFont);
    fillMethodCombo.addItem("From Up");
    fillMethodCombo.addItem("From Zero");
    fillMethodCombo.addItem("From Bottom");
    fillMethodCombo.setSelectedIndex(dataView.getFillMethod());
    fillMethodCombo.addActionListener(this);

    barPanel.add(barWidthLabel);
    barPanel.add(barWidthSpinner);
    barPanel.add(fillMethodLabel);
    barPanel.add(fillMethodCombo);

    barWidthLabel.setBounds(10, 10, 100, 25);
    barWidthSpinner.setBounds(115, 10, 125, 25);

    fillMethodLabel.setBounds(10, 40, 100, 25);
    fillMethodCombo.setBounds(115, 40, 125, 25);

    // Marker panel construction

    markerPanel = new JPanel();
    markerPanel.setLayout(null);

    markerColorView = new JLabel("");
    markerColorView.setBackground(dataView.getMarkerColor());
    markerColorView.setOpaque(true);

    markerColorView.setBorder(BorderFactory.createLineBorder(Color.black));

    markerColorBtn = new JButton("...");
    markerColorBtn.addMouseListener(this);

    markerColorLabel = new JLabel("Color");
    markerColorLabel.setFont(GraphicsUtils.labelFont);
    markerColorLabel.setForeground(GraphicsUtils.fColor);

    markerSizeLabel = new JLabel("Size");
    markerSizeLabel.setFont(GraphicsUtils.labelFont);
    markerSizeLabel.setForeground(GraphicsUtils.fColor);

    markerSizeSpinner = new JSpinner();
    value = new Integer(dataView.getMarkerSize());
    spModel = new SpinnerNumberModel(value, min, max, step);
    markerSizeSpinner.setModel(spModel);
    markerSizeSpinner.addChangeListener(this);

    markerStyleLabel = new JLabel("Marker style");
    markerStyleLabel.setFont(GraphicsUtils.labelFont);
    markerStyleLabel.setForeground(GraphicsUtils.fColor);

    markerStyleCombo = new JComboBox();
    markerStyleCombo.addItem("None");
    markerStyleCombo.addItem("Dot");
    markerStyleCombo.addItem("Box");
    markerStyleCombo.addItem("triangle");
    markerStyleCombo.addItem("Diamond");
    markerStyleCombo.addItem("Star");
    markerStyleCombo.addItem("Vert. line");
    markerStyleCombo.addItem("Horz. line");
    markerStyleCombo.addItem("Cross");
    markerStyleCombo.addItem("Circle");
    markerStyleCombo.addItem("Sqaure");
    markerStyleCombo.setSelectedIndex(dataView.getMarker());
    markerStyleCombo.addActionListener(this);

    labelVisibleCheck = new JCheckBox();
    labelVisibleCheck.setFont(GraphicsUtils.labelFont);
    labelVisibleCheck.setForeground(GraphicsUtils.fColor);
    labelVisibleCheck.setText("Legend visible");
    labelVisibleCheck.setSelected(dataView.isLabelVisible());
    labelVisibleCheck.addActionListener(this);

    markerPanel.add(markerColorLabel);
    markerPanel.add(markerColorView);
    markerPanel.add(markerColorBtn);
    markerPanel.add(markerSizeLabel);
    markerPanel.add(markerSizeSpinner);
    markerPanel.add(markerStyleLabel);
    markerPanel.add(markerStyleCombo);
    markerPanel.add(labelVisibleCheck);

    markerColorLabel.setBounds(10, 10, 100, 25);
    markerColorView.setBounds(115, 10, 80, 25);
    markerColorBtn.setBounds(200, 10, 40, 27);

    markerSizeLabel.setBounds(10, 40, 100, 25);
    markerSizeSpinner.setBounds(115, 40, 125, 25);

    markerStyleLabel.setBounds(10, 70, 100, 25);
    markerStyleCombo.setBounds(115, 70, 125, 25);

    labelVisibleCheck.setBounds(10, 100, 225, 25);

    // Transform panel construction
    transformPanel = new JPanel();
    transformPanel.setLayout(null);

    transformHelpLabel = new JTextArea("This apply a polynomial transform\nto the data view:\n y' = A0 + A1*y + A2*y^2");
    transformHelpLabel.setFont(GraphicsUtils.labelFont);
    transformHelpLabel.setForeground(GraphicsUtils.fColor);
    transformHelpLabel.setFont(markerStyleLabel.getFont());
    transformHelpLabel.setEditable(false);
    transformHelpLabel.setBackground(markerStyleLabel.getBackground());

    transformA0Label = new JLabel("A0");
    transformA0Label.setFont(GraphicsUtils.labelFont);
    transformA0Label.setForeground(GraphicsUtils.fColor);
    transformA0Text = new JTextField();
    transformA0Text.setEditable(true);
    transformA0Text.setText(Double.toString(dataView.getA0()));
    transformA0Text.setMargin(GraphicsUtils.zInset);
    transformA0Text.addKeyListener(this);

    transformA1Label = new JLabel("A1");
    transformA1Label.setFont(GraphicsUtils.labelFont);
    transformA1Label.setForeground(GraphicsUtils.fColor);
    transformA1Text = new JTextField();
    transformA1Text.setEditable(true);
    transformA1Text.setText(Double.toString(dataView.getA1()));
    transformA1Text.setMargin(GraphicsUtils.zInset);
    transformA1Text.addKeyListener(this);

    transformA2Label = new JLabel("A2");
    transformA2Label.setFont(GraphicsUtils.labelFont);
    transformA2Label.setForeground(GraphicsUtils.fColor);
    transformA2Text = new JTextField();
    transformA2Text.setEditable(true);
    transformA2Text.setText(Double.toString(dataView.getA2()));
    transformA2Text.setMargin(GraphicsUtils.zInset);
    transformA2Text.addKeyListener(this);

    transformPanel.add(transformHelpLabel);
    transformPanel.add(transformA0Label);
    transformPanel.add(transformA0Text);
    transformPanel.add(transformA1Label);
    transformPanel.add(transformA1Text);
    transformPanel.add(transformA2Label);
    transformPanel.add(transformA2Text);

    transformHelpLabel.setBounds(10, 100, 240, 100);

    transformA0Label.setBounds(60, 10, 30, 25);
    transformA0Text.setBounds(95, 10, 100, 25);
    transformA1Label.setBounds(60, 40, 30, 25);
    transformA1Text.setBounds(95, 40, 100, 25);
    transformA2Label.setBounds(60, 70, 30, 25);
    transformA2Text.setBounds(95, 70, 100, 25);

    //Interpolation panel
    interpPanel = new JPanel();
    interpPanel.setLayout(null);

    methodIntBtnGrp = new ButtonGroup();

    noInterpBtn = new JRadioButton("None");
    noInterpBtn.setForeground(GraphicsUtils.fColor);
    noInterpBtn.setFont(GraphicsUtils.labelFont);
    noInterpBtn.setBounds(5,10,90,25);
    interpPanel.add(noInterpBtn);
    methodIntBtnGrp.add(noInterpBtn);
    linearBtn = new JRadioButton("Linear");
    linearBtn.setForeground(GraphicsUtils.fColor);
    linearBtn.setFont(GraphicsUtils.labelFont);
    linearBtn.setBounds(5,35,90,25);
    interpPanel.add(linearBtn);
    methodIntBtnGrp.add(linearBtn);
    cosineBtn = new JRadioButton("Cosine");
    cosineBtn.setForeground(GraphicsUtils.fColor);
    cosineBtn.setFont(GraphicsUtils.labelFont);
    cosineBtn.setBounds(5,60,90,25);
    interpPanel.add(cosineBtn);
    methodIntBtnGrp.add(cosineBtn);
    cubicBtn = new JRadioButton("Cubic");
    cubicBtn.setForeground(GraphicsUtils.fColor);
    cubicBtn.setFont(GraphicsUtils.labelFont);
    cubicBtn.setBounds(5,85,90,25);
    interpPanel.add(cubicBtn);
    methodIntBtnGrp.add(cubicBtn);
    hermiteBtn = new JRadioButton("Hermite");
    hermiteBtn.setForeground(GraphicsUtils.fColor);
    hermiteBtn.setFont(GraphicsUtils.labelFont);
    hermiteBtn.setBounds(5,110,90,25);
    interpPanel.add(hermiteBtn);
    methodIntBtnGrp.add(hermiteBtn);

    JLabel stepLabel = new JLabel("Step");
    stepLabel.setFont(GraphicsUtils.labelFont);
    stepLabel.setForeground(GraphicsUtils.fColor);
    stepLabel.setHorizontalAlignment(JLabel.RIGHT);
    stepLabel.setBounds(100,10,85,25);
    interpPanel.add(stepLabel);

    stepSpinner = new JSpinner();
    value = new Integer(dataView.getInterpolationStep());
    min = new Integer(2);
    max = new Integer(100);
    spModel = new SpinnerNumberModel(value, min, max, step);
    stepSpinner.setModel(spModel);
    stepSpinner.addChangeListener(this);
    stepSpinner.setBounds(195,10,50,25);
    interpPanel.add(stepSpinner);

    JLabel tensionLabel = new JLabel("Tension");
    tensionLabel.setFont(GraphicsUtils.labelFont);
    tensionLabel.setForeground(GraphicsUtils.fColor);
    tensionLabel.setHorizontalAlignment(JLabel.RIGHT);
    tensionLabel.setBounds(100,40,85,25);
    interpPanel.add(tensionLabel);
    tensionText = new JTextField();
    tensionText.setFont(GraphicsUtils.labelFont);
    tensionText.setEditable(true);
    tensionText.setBounds(195,40,50,25);
    tensionText.setEnabled(false);
    tensionText.addKeyListener(this);
    interpPanel.add(tensionText);

    JLabel biasLabel = new JLabel("Bias");
    biasLabel.setFont(GraphicsUtils.labelFont);
    biasLabel.setForeground(GraphicsUtils.fColor);
    biasLabel.setHorizontalAlignment(JLabel.RIGHT);
    biasLabel.setBounds(100,70,85,25);
    interpPanel.add(biasLabel);
    biasText = new JTextField();
    biasText.setFont(GraphicsUtils.labelFont);
    biasText.setEditable(true);
    biasText.setBounds(195,70,50,25);
    biasText.setEnabled(false);
    biasText.addKeyListener(this);
    interpPanel.add(biasText);

    switch(dataView.getInterpolationMethod()) {
      case JLDataView.INTERPOLATE_NONE:
        noInterpBtn.setSelected(true);
        break;
      case JLDataView.INTERPOLATE_LINEAR:
        linearBtn.setSelected(true);
        break;
      case JLDataView.INTERPOLATE_CUBIC:
        cubicBtn.setSelected(true);
        break;
      case JLDataView.INTERPOLATE_COSINE:
        cosineBtn.setSelected(true);
        break;
      case JLDataView.INTERPOLATE_HERMITE:
        hermiteBtn.setSelected(true);
        break;
    }

    noInterpBtn.addChangeListener(this);
    linearBtn.addChangeListener(this);
    cosineBtn.addChangeListener(this);
    cubicBtn.addChangeListener(this);
    hermiteBtn.addChangeListener(this);
    tensionText.setText(Double.toString(dataView.getHermiteTension()));
    biasText.setText(Double.toString(dataView.getHermiteBias()));

    // Smoothing panel
    smoothPanel = new JPanel();
    smoothPanel.setLayout(null);

    methodSmBtnGrp = new ButtonGroup();

    noSmoothBtn = new JRadioButton("None");
    noSmoothBtn.setForeground(GraphicsUtils.fColor);
    noSmoothBtn.setFont(GraphicsUtils.labelFont);
    noSmoothBtn.setBounds(5,10,90,25);
    smoothPanel.add(noSmoothBtn);
    methodSmBtnGrp.add(noSmoothBtn);

    flatSmoothBtn = new JRadioButton("Flat");
    flatSmoothBtn.setForeground(GraphicsUtils.fColor);
    flatSmoothBtn.setFont(GraphicsUtils.labelFont);
    flatSmoothBtn.setBounds(5,35,90,25);
    smoothPanel.add(flatSmoothBtn);
    methodSmBtnGrp.add(flatSmoothBtn);

    triangularSmoothBtn = new JRadioButton("Linear");
    triangularSmoothBtn.setForeground(GraphicsUtils.fColor);
    triangularSmoothBtn.setFont(GraphicsUtils.labelFont);
    triangularSmoothBtn.setBounds(5,60,90,25);
    smoothPanel.add(triangularSmoothBtn);
    methodSmBtnGrp.add(triangularSmoothBtn);

    gaussianSmoothBtn = new JRadioButton("Gaussian");
    gaussianSmoothBtn.setForeground(GraphicsUtils.fColor);
    gaussianSmoothBtn.setFont(GraphicsUtils.labelFont);
    gaussianSmoothBtn.setBounds(5,85,90,25);
    smoothPanel.add(gaussianSmoothBtn);
    methodSmBtnGrp.add(gaussianSmoothBtn);

    JLabel neighborLabel = new JLabel("Neighbors");
    neighborLabel.setFont(GraphicsUtils.labelFont);
    neighborLabel.setForeground(GraphicsUtils.fColor);
    neighborLabel.setHorizontalAlignment(JLabel.RIGHT);
    neighborLabel.setBounds(100,10,90,25);
    smoothPanel.add(neighborLabel);

    neighborSpinner = new JSpinner();
    value = new Integer(dataView.getSmoothingNeighbors());
    min = new Integer(2);
    max = new Integer(99);
    step = new Integer(2);
    spModel = new SpinnerNumberModel(value, min, max, step);
    neighborSpinner.setModel(spModel);
    neighborSpinner.addChangeListener(this);
    neighborSpinner.setBounds(195,10,50,25);
    smoothPanel.add(neighborSpinner);

    JLabel sigmaLabel = new JLabel(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/util/chart/sigma_small.gif")));
    sigmaLabel.setForeground(GraphicsUtils.fColor);
    sigmaLabel.setHorizontalAlignment(JLabel.RIGHT);
    sigmaLabel.setBounds(100,40,85,25);
    smoothPanel.add(sigmaLabel);
    sigmaText = new JTextField(Double.toString(dataView.getSmoothingGaussSigma()));
    sigmaText.setFont(GraphicsUtils.labelFont);
    sigmaText.setEditable(true);
    sigmaText.setBounds(195,40,50,25);
    sigmaText.setEnabled(false);
    sigmaText.addKeyListener(this);
    smoothPanel.add(sigmaText);

    JPanel bPanel = new JPanel();
    bPanel.setLayout(null);
    bPanel.setBorder( GraphicsUtils.createTitleBorder("Boundary extrapolation") );

    methodExtBtnGrp = new ButtonGroup();

    noExtBtn = new JRadioButton("None");
    noExtBtn.setForeground(GraphicsUtils.fColor);
    noExtBtn.setFont(GraphicsUtils.labelFont);
    noExtBtn.setBounds(5,20,90,25);
    bPanel.add(noExtBtn);
    methodExtBtnGrp.add(noExtBtn);

    flatExtBtn = new JRadioButton("Flat");
    flatExtBtn.setForeground(GraphicsUtils.fColor);
    flatExtBtn.setFont(GraphicsUtils.labelFont);
    flatExtBtn.setBounds(5,45,90,25);
    bPanel.add(flatExtBtn);
    methodExtBtnGrp.add(flatExtBtn);

    linearExtBtn = new JRadioButton("Linear");
    linearExtBtn.setForeground(GraphicsUtils.fColor);
    linearExtBtn.setFont(GraphicsUtils.labelFont);
    linearExtBtn.setBounds(5,70,90,25);
    bPanel.add(linearExtBtn);
    methodExtBtnGrp.add(linearExtBtn);

    bPanel.setBounds(5,120,245,100);
    smoothPanel.add(bPanel);

    switch(dataView.getSmoothingExtrapolation()) {
      case JLDataView.SMOOTH_EXT_NONE:
        noExtBtn.setSelected(true);
        break;
      case JLDataView.SMOOTH_EXT_FLAT:
        flatExtBtn.setSelected(true);
        break;
      case JLDataView.SMOOTH_EXT_LINEAR:
        linearExtBtn.setSelected(true);
        break;
    }

    switch(dataView.getSmoothingMethod()) {
      case JLDataView.SMOOTH_NONE:
        noSmoothBtn.setSelected(true);
        break;
      case JLDataView.SMOOTH_FLAT:
        flatSmoothBtn.setSelected(true);
        break;
      case JLDataView.SMOOTH_TRIANGULAR:
        triangularSmoothBtn.setSelected(true);
        break;
      case JLDataView.SMOOTH_GAUSSIAN:
        gaussianSmoothBtn.setSelected(true);
        break;
    }

    noExtBtn.addChangeListener(this);
    flatExtBtn.addChangeListener(this);
    linearExtBtn.addChangeListener(this);

    noSmoothBtn.addChangeListener(this);
    flatSmoothBtn.addChangeListener(this);
    triangularSmoothBtn.addChangeListener(this);
    gaussianSmoothBtn.addChangeListener(this);

    //Math panel
    mathPanel = new JPanel();
    mathPanel.setLayout(null);

    mathBtnGrp = new ButtonGroup();

    noMathBtn = new JRadioButton("No operation");
    noMathBtn.setForeground(GraphicsUtils.fColor);
    noMathBtn.setFont(GraphicsUtils.labelFont);
    noMathBtn.setBounds(5,10,160,25);
    mathPanel.add(noMathBtn);
    mathBtnGrp.add(noMathBtn);
    derivativeBtn = new JRadioButton("Derivative");
    derivativeBtn.setForeground(GraphicsUtils.fColor);
    derivativeBtn.setFont(GraphicsUtils.labelFont);
    derivativeBtn.setBounds(5,35,160,25);
    mathPanel.add(derivativeBtn);
    mathBtnGrp.add(derivativeBtn);
    integralBtn = new JRadioButton("Integral");
    integralBtn.setForeground(GraphicsUtils.fColor);
    integralBtn.setFont(GraphicsUtils.labelFont);
    integralBtn.setBounds(5,60,160,25);
    mathPanel.add(integralBtn);
    mathBtnGrp.add(integralBtn);
    fftModBtn = new JRadioButton("FFT (modulus)");
    fftModBtn.setForeground(GraphicsUtils.fColor);
    fftModBtn.setFont(GraphicsUtils.labelFont);
    fftModBtn.setBounds(5,85,160,25);
    fftModBtn.setEnabled(false);
    mathPanel.add(fftModBtn);
    mathBtnGrp.add(fftModBtn);
    fftPhaseBtn = new JRadioButton("FFT (phase radians)");
    fftPhaseBtn.setForeground(GraphicsUtils.fColor);
    fftPhaseBtn.setFont(GraphicsUtils.labelFont);
    fftPhaseBtn.setBounds(5,110,160,25);
    fftPhaseBtn.setEnabled(false);
    mathPanel.add(fftPhaseBtn);
    mathBtnGrp.add(fftPhaseBtn);

    switch(dataView.getMathFunction()) {
      case JLDataView.MATH_NONE:
        noMathBtn.setSelected(true);
        break;
      case JLDataView.MATH_DERIVATIVE:
        derivativeBtn.setSelected(true);
        break;
      case JLDataView.MATH_INTEGRAL:
        integralBtn.setSelected(true);
        break;
      case JLDataView.MATH_FFT_MODULUS:
        fftModBtn.setSelected(true);
        break;
      case JLDataView.MATH_FFT_PHASE:
        fftPhaseBtn.setSelected(true);
        break;
    }

    noMathBtn.addChangeListener(this);
    derivativeBtn.addChangeListener(this);
    integralBtn.addChangeListener(this);
    fftModBtn.addChangeListener(this);
    fftPhaseBtn.addChangeListener(this);

    // Global frame construction
    nameLabel = new JLabel();
    nameLabel.setText(dataView.getName());

    tabPane.add("Curve", linePanel);
    tabPane.add("Bar", barPanel);
    tabPane.add("Marker", markerPanel);
    tabPane.add("Transform", transformPanel);
    tabPane.add("Interpolation", interpPanel);
    tabPane.add("Smoothing", smoothPanel);
    tabPane.add("Math", mathPanel);

    innerPane.add(tabPane);
    innerPane.add(nameLabel);

    closeBtn = new JButton();
    closeBtn.setText("Close");
    innerPane.add(closeBtn);

    tabPane.setBounds(5, 5, 260, 270);
    closeBtn.setBounds(185, 280, 80, 25);
    nameLabel.setBounds(10, 280, 170, 25);

    closeBtn.addMouseListener(this);

    updateControls();

    innerPane.setPreferredSize(new Dimension(270,310));
    setContentPane(innerPane);
    setResizable(false);

  }

  private void updateControls() {

    biasText.setEnabled(false);
    tensionText.setEnabled(false);
    sigmaText.setEnabled(false);

    switch(dataView.getInterpolationMethod()) {
      case JLDataView.INTERPOLATE_HERMITE:
        biasText.setEnabled(true);
        tensionText.setEnabled(true);
        break;
    }

    switch(dataView.getSmoothingMethod()) {
      case JLDataView.SMOOTH_GAUSSIAN:
        sigmaText.setEnabled(true);
        break;
    }

  }

  /**
   * Commit change. Repaint the graph.
   */
  public void Commit() {
    if (chart != null) chart.repaint();
  }

  // Mouse Listener
  public void mouseClicked(MouseEvent e) {
    if (e.getSource() == closeBtn) {
      setVisible(false);
      dispose();
    } else if (e.getSource() == lineColorBtn) {
      Color c = JColorChooser.showDialog(this, "Choose Line Color", dataView.getColor());
      if (c != null) {
        dataView.setColor(c);
        lineColorView.setBackground(c);
        Commit();
      }
    } else if (e.getSource() == fillColorBtn) {
      Color c = JColorChooser.showDialog(this, "Choose Fill Color", dataView.getFillColor());
      if (c != null) {
        dataView.setFillColor(c);
        fillColorView.setBackground(c);
        Commit();
      }
    } else if (e.getSource() == markerColorBtn) {
      Color c = JColorChooser.showDialog(this, "Choose marker Color", dataView.getMarkerColor());
      if (c != null) {
        dataView.setMarkerColor(c);
        markerColorView.setBackground(c);
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

  //Action listener
  public void actionPerformed(ActionEvent e) {

    if (e.getSource() == lineDashCombo) {
      dataView.setStyle(lineDashCombo.getSelectedIndex());
      Commit();
    } else if (e.getSource() == fillStyleCombo) {
      dataView.setFillStyle(fillStyleCombo.getSelectedIndex());
      Commit();
    } else if (e.getSource() == fillMethodCombo) {
      dataView.setFillMethod(fillMethodCombo.getSelectedIndex());
      Commit();
    } else if (e.getSource() == viewTypeCombo) {
      dataView.setViewType(viewTypeCombo.getSelectedIndex());
      Commit();
    } else if (e.getSource() == markerStyleCombo) {
      dataView.setMarker(markerStyleCombo.getSelectedIndex());
      Commit();
    } else if (e.getSource() == labelVisibleCheck) {
      dataView.setLabelVisible(labelVisibleCheck.isSelected());
      Commit();
    }


  }

  //Change listener
  public void stateChanged(ChangeEvent e) {

    Integer v;
    Object src = e.getSource();

    if (src == lineWidthSpinner) {
      v = (Integer) lineWidthSpinner.getValue();
      dataView.setLineWidth(v.intValue());
    } else if (src == barWidthSpinner) {
      v = (Integer) barWidthSpinner.getValue();
      dataView.setBarWidth(v.intValue());
    } else if (src == markerSizeSpinner) {
      v = (Integer) markerSizeSpinner.getValue();
      dataView.setMarkerSize(v.intValue());
    } else if (src == stepSpinner) {
      v = (Integer) stepSpinner.getValue();
      dataView.setInterpolationStep(v.intValue());
    } else if (src == neighborSpinner) {
      v = (Integer) neighborSpinner.getValue();
      dataView.setSmoothingNeighbors(v.intValue());
    } else if (src == noInterpBtn) {
      if(noInterpBtn.isSelected())
        dataView.setInterpolationMethod(JLDataView.INTERPOLATE_NONE);
    } else if (src == linearBtn) {
      if(linearBtn.isSelected())
        dataView.setInterpolationMethod(JLDataView.INTERPOLATE_LINEAR);
    } else if (src == cosineBtn) {
      if(cosineBtn.isSelected())
        dataView.setInterpolationMethod(JLDataView.INTERPOLATE_COSINE);
    } else if (src == cubicBtn) {
      if(cubicBtn.isSelected())
        dataView.setInterpolationMethod(JLDataView.INTERPOLATE_CUBIC);
    } else if (src == hermiteBtn) {
      if(hermiteBtn.isSelected())
        dataView.setInterpolationMethod(JLDataView.INTERPOLATE_HERMITE);
    } else if (src == noSmoothBtn) {
      if(noSmoothBtn.isSelected())
        dataView.setSmoothingMethod(JLDataView.SMOOTH_NONE);
    } else if (src == flatSmoothBtn) {
      if(flatSmoothBtn.isSelected())
        dataView.setSmoothingMethod(JLDataView.SMOOTH_FLAT);
    } else if (src == triangularSmoothBtn) {
      if(triangularSmoothBtn.isSelected())
        dataView.setSmoothingMethod(JLDataView.SMOOTH_TRIANGULAR);
    } else if (src == gaussianSmoothBtn) {
      if(gaussianSmoothBtn.isSelected())
        dataView.setSmoothingMethod(JLDataView.SMOOTH_GAUSSIAN);
    } else if (src == noExtBtn) {
      if(noExtBtn.isSelected())
        dataView.setSmoothingExtrapolation(JLDataView.SMOOTH_EXT_NONE);
    } else if (src == flatExtBtn) {
      if(flatExtBtn.isSelected())
        dataView.setSmoothingExtrapolation(JLDataView.SMOOTH_EXT_FLAT);
    } else if (src == linearExtBtn) {
      if(linearExtBtn.isSelected())
        dataView.setSmoothingExtrapolation(JLDataView.SMOOTH_EXT_LINEAR);
    } else if (src == noMathBtn) {
      if(noMathBtn.isSelected())
        dataView.setMathFunction(JLDataView.MATH_NONE);
    } else if (src == derivativeBtn) {
      if(derivativeBtn.isSelected())
        dataView.setMathFunction(JLDataView.MATH_DERIVATIVE);
    } else if (src == integralBtn) {
      if(integralBtn.isSelected())
        dataView.setMathFunction(JLDataView.MATH_INTEGRAL);
    } else if (src == fftModBtn) {
      if(fftModBtn.isSelected())
        dataView.setMathFunction(JLDataView.MATH_FFT_MODULUS);
    } else if (src == fftPhaseBtn) {
      if(fftPhaseBtn.isSelected())
        dataView.setMathFunction(JLDataView.MATH_FFT_PHASE);
    }

    updateControls();
    Commit();

  }

  //Key listener
  public void keyPressed(KeyEvent e) {
  }

  public void keyTyped(KeyEvent e) {
  }

  public void keyReleased(KeyEvent e) {

    if (e.getSource() == transformA0Text) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = transformA0Text.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setA0(d);
          Commit();
        } catch (NumberFormatException err) {
          transformA0Text.setText(Double.toString(dataView.getA0()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        transformA0Text.setText(Double.toString(dataView.getA0()));
      }

    } else if (e.getSource() == transformA1Text) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = transformA1Text.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setA1(d);
          Commit();
        } catch (NumberFormatException err) {
          transformA1Text.setText(Double.toString(dataView.getA1()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        transformA1Text.setText(Double.toString(dataView.getA1()));
      }

    } else if (e.getSource() == transformA2Text) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = transformA2Text.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setA2(d);
          Commit();
        } catch (NumberFormatException err) {
          transformA2Text.setText(Double.toString(dataView.getA2()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        transformA2Text.setText(Double.toString(dataView.getA2()));
      }


    } else if (e.getSource() == lineNameText) {

      dataView.setName(lineNameText.getText());
      Commit();

    } else if (e.getSource() == tensionText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = tensionText.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setHermiteTension(d);
          Commit();
        } catch (NumberFormatException err) {
          tensionText.setText(Double.toString(dataView.getHermiteTension()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        tensionText.setText(Double.toString(dataView.getHermiteTension()));
      }

    } else if (e.getSource() == biasText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = biasText.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setHermiteBias(d);
          Commit();
        } catch (NumberFormatException err) {
          tensionText.setText(Double.toString(dataView.getHermiteBias()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        biasText.setText(Double.toString(dataView.getHermiteBias()));
      }

    } else if (e.getSource() == sigmaText) {

      if (e.getKeyCode() == KeyEvent.VK_ENTER) {
        String s = sigmaText.getText();
        try {
          double d = Double.parseDouble(s);
          dataView.setSmoothingGaussSigma(d);
          Commit();
        } catch (NumberFormatException err) {
          sigmaText.setText(Double.toString(dataView.getSmoothingGaussSigma()));
        }
      }

      if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
        sigmaText.setText(Double.toString(dataView.getSmoothingGaussSigma()));
      }

    }

  }
}
