package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.*;

class JDGlobalPanel extends JPanel implements ActionListener {

  private JLabel backgroundLabel;
  private JButton backgroundButton;
  private JButton dismissBtn;
  private JCheckBox resizeLabelFontCheck;
  private JCheckBox resizeLabelTextCheck;

  JDrawEditor invoker;

  public JDGlobalPanel(JDrawEditor jc) {

    invoker = jc;

    setForeground(JDUtils.labelColor);
    setFont(JDUtils.labelFont);
    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(280, 184));

    // -----------------------------------------------------------------
    JPanel colorPanel = new JPanel(null);
    colorPanel.setBorder(JDUtils.createTitleBorder("Colors"));
    colorPanel.setBounds(5, 5, 270, 55);

    backgroundLabel = JDUtils.createLabel("Background");
    backgroundLabel.setBounds(10, 20, 180, 24);
    colorPanel.add(backgroundLabel);
    backgroundButton = new JButton("");
    backgroundButton.setMargin(new Insets(0, 0, 0, 0));
    backgroundButton.setBackground(invoker.getBackground());
    backgroundButton.setForeground(Color.BLACK);
    backgroundButton.addActionListener(this);
    backgroundButton.setBounds(200, 20, 60, 24);
    colorPanel.add(backgroundButton);

    add(colorPanel);

    // -----------------------------------------------------------------
    JPanel editorPanel = new JPanel(null);
    editorPanel.setBorder(JDUtils.createTitleBorder("Editor settings"));
    editorPanel.setBounds(5, 65, 270, 85);

    resizeLabelFontCheck = new JCheckBox("Resize label when changing font");
    resizeLabelFontCheck.setFont(JDUtils.labelFont);
    resizeLabelFontCheck.setForeground(JDUtils.labelColor);
    resizeLabelFontCheck.setBounds(10, 20, 250, 25);
    resizeLabelFontCheck.setSelected(invoker.resizeLabelOnFontChange);
    editorPanel.add(resizeLabelFontCheck);

    resizeLabelTextCheck = new JCheckBox("Resize label when changing text");
    resizeLabelTextCheck.setFont(JDUtils.labelFont);
    resizeLabelTextCheck.setForeground(JDUtils.labelColor);
    resizeLabelTextCheck.setBounds(10, 50, 250, 25);
    resizeLabelTextCheck.setSelected(invoker.resizeLabelOnTextChange);
    editorPanel.add(resizeLabelTextCheck);

    add(editorPanel);

    dismissBtn = new JButton("Dismiss");
    dismissBtn.setMargin(new Insets(0, 0, 0, 0));
    dismissBtn.setFont(JDUtils.labelFont);
    dismissBtn.addActionListener(this);
    dismissBtn.setBounds(192, 155, 80, 24);
    add(dismissBtn);

  }

  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();

    if (src == backgroundButton) {
      Color c = JColorChooser.showDialog(this, "Choose background color", invoker.getBackground());
      if (c != null) {
        invoker.setBackground(c);
        backgroundButton.setBackground(c);
      }
    } else if (src == dismissBtn) {
      invoker.resizeLabelOnFontChange = resizeLabelFontCheck.isSelected();
      invoker.resizeLabelOnTextChange = resizeLabelTextCheck.isSelected();
      ATKGraphicsUtils.getWindowForComponent(this).setVisible(false);
    }

  }

}
