/** A panel for value to JDraw object property mapping */
package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;

import javax.swing.*;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.AbstractTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseListener;
import java.awt.event.MouseEvent;

class ValueMapTableRenderer implements TableCellRenderer {
  private TableCellRenderer __defaultRenderer;
  private JDValueMappingPanel invoker;

  public ValueMapTableRenderer(TableCellRenderer renderer,JDValueMappingPanel parent) {
    __defaultRenderer = renderer;
     invoker=parent;
  }

  public Component getTableCellRendererComponent(JTable table, Object value,
						 boolean isSelected,
						 boolean hasFocus,
						 int row, int column)
  {
    Component ret;
    if(value instanceof Component)
      ret = (Component)value;
    else
      ret =__defaultRenderer.getTableCellRendererComponent(
	         table, value, isSelected, hasFocus, row, column);
    if( column==2 && invoker.getMapper().getType()==JDValueProgram.COLOR_TYPE )
      ret.setBackground(invoker.getMapper().getColorMappingAt(row));
    return ret;
  }
}

class ValueMapTableMouseListener implements MouseListener {
  private JDValueMappingPanel invoker;
  public ValueMapTableMouseListener(JDValueMappingPanel parent) {
    invoker=parent;
  }
  public void mouseClicked(MouseEvent e) {}
  public void mouseEntered(MouseEvent e) {}
  public void mouseExited(MouseEvent e) {}
  public void mousePressed(MouseEvent e) {
    int column = invoker.getTable().getColumnModel().getColumnIndexAtX(e.getX());
    int row    = e.getY() / invoker.getTable().getRowHeight();
    if(column==2) {
      switch( invoker.getMapper().getType() ) {
        case JDValueProgram.BOOLEAN_TYPE:
          boolean ob = invoker.getMapper().getBooleanMappingAt(row);
          boolean nb = JDUtils.showBooleanDialog(invoker,invoker.getDescription() + " mapped value",ob);
          if(nb!=ob) invoker.setMappingAt(Boolean.toString(nb),row);
          break;
        case JDValueProgram.COLOR_TYPE:
          Color c = JColorChooser.showDialog(invoker, "Choose color",invoker.getMapper().getColorMappingAt(row));
          if(c!=null) invoker.setMappingAt(c.getRed()+","+c.getGreen()+","+c.getBlue(),row);
          break;
        case JDValueProgram.INTEGER_TYPE:
          int oi = invoker.getMapper().getIntegerMappingAt(row);
          int ni = JDUtils.showIntegerDialog(invoker,invoker.getDescription() + " mapped value",oi);
          if(ni!=oi) invoker.setMappingAt(Integer.toString(ni),row);
          break;
      }
    }
  }
  public void mouseReleased(MouseEvent e) {}
}

class ValueMapTableModel extends AbstractTableModel {

      private String colName[] = { "JDObject Value" , "Mapped to" , "Set" };
      private Object[][] rows;
      private JDValueMappingPanel invoker;

      public ValueMapTableModel(JDValueMappingPanel parent) {
        invoker=parent;
      }

      public void setRows(Object[][] r) {
        rows=r;
        fireTableDataChanged();
      }

      public Class getColumnClass(int columnIndex) {
        if( columnIndex<=1 )
         return String.class;
        else
         return JButton.class;
      }

      public boolean isCellEditable(int row,int col) {
        return col<=1;
      }

      public Object getValueAt(int row, int column) {
        return rows[row][column];
      }

      public String getColumnName(int column) {
        return colName[column];
      }

      public int getRowCount() {
        return rows.length;
      }

      public int getColumnCount() {
        return colName.length;
      }

      public void setValueAt(Object e,int row,int col) {
        if( col==0 ) {
          if(!invoker.setValueAt((String)e,row)) {
            JOptionPane.showMessageDialog(invoker, "Invalid value syntax, Use integer number or integer range ex:1..6");
          }
        }
        if( col==1 ) {
          if(!invoker.setMappingAt((String)e,row)) {
            JOptionPane.showMessageDialog(invoker, "Invalid mapped value syntax.");
          }
        }
      }

}

class JDValueMappingPanel extends JPanel implements ActionListener {

  JDObject[] allObjects;
  JComponent   invoker;
  String propName;
  private JDValueProgram theMapper;

  private JPanel    modePanel;
  private JLabel    modeLabel;
  private JComboBox modelCombo;

  private JPanel        tablePanel;
  private ValueMapTableModel tableModel;
  private JScrollPane   tableView;
  private JTable        theTable=null;
  private JLabel        defaultValueLabel;
  private JTextField    defaultValueText;
  private JButton       defaultValueBtn;

  private JPanel        linearPanel;
  private JLabel        maxValueLabel;
  private JTextField    maxValueText;
  private JLabel        minValueLabel;
  private JTextField    minValueText;

  private JButton       newEntryBtn;
  private JButton       removeEntryBtn;

  private JButton       applyBtn;
  private JButton       cancelBtn;

  private boolean       hasChanged;
  private boolean       isUpdating;

  public JDValueMappingPanel(JDObject[] p, JComponent jc,String desc,int type,JDValueProgram mapper) {

    allObjects = p;
    invoker = jc;
    hasChanged=false;
    isUpdating=false;
    propName=desc;
    if(mapper==null)  theMapper= new JDValueProgram(type);
    else              theMapper = mapper.copy();

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());

    // ------------------------------------------------------------------------------------

    modePanel = new JPanel();
    modePanel.setLayout(null);
    modePanel.setBorder( JDUtils.createTitleBorder("Mapping mode for " + desc) );

    modeLabel = JDUtils.createLabel("Mode");
    modeLabel.setBounds(10, 20, 100, 25);
    modePanel.add(modeLabel);

    modelCombo = new JComboBox();
    modelCombo.setFont(JDUtils.labelFont);
    modelCombo.addItem("By table");
    modelCombo.addItem("Linear mapping");
    modelCombo.addItem("Restore value");
    modelCombo.addActionListener(this);
    modelCombo.setBounds(115, 20, 170, 25);
    modePanel.add(modelCombo);

    add(modePanel);

    modePanel.setBounds(5,10,295,55);

    // ------------------------------------------------------------------------------------

    tablePanel = new JPanel();
    tablePanel.setLayout(null);
    tablePanel.setBorder( JDUtils.createTitleBorder("Correspondence table") );

    defaultValueLabel = JDUtils.createLabel("Default mapped value");
    defaultValueLabel.setBounds(10, 20, 120, 25);
    tablePanel.add(defaultValueLabel);

    defaultValueText = new JTextField();
    defaultValueText.setMargin(JDUtils.zMargin);
    defaultValueText.setText(theMapper.getDefaultMapping());
    defaultValueText.setBounds(140, 20, 115, 25);
    defaultValueText.addActionListener(this);
    tablePanel.add(defaultValueText);

    defaultValueBtn = JDUtils.createSetButton(this);
    defaultValueBtn.setBounds(260, 20, 25, 25);
    tablePanel.add(defaultValueBtn);
    if( theMapper.getType()==JDValueProgram.COLOR_TYPE )
      defaultValueBtn.setBackground(theMapper.getDefaultColorMapping());

    tableModel = new ValueMapTableModel(this);
    updateRows();
    theTable = new JTable(tableModel);
    theTable.setRowHeight(20);

    TableCellRenderer defaultRenderer = theTable.getDefaultRenderer(JButton.class);
    theTable.setDefaultRenderer(JButton.class,new ValueMapTableRenderer(defaultRenderer,this));
    theTable.addMouseListener(new ValueMapTableMouseListener(this));
    sizeTable();

    tableView = new JScrollPane(theTable);
    tableView.setBounds(10,50,275,230);
    tablePanel.add(tableView);

    newEntryBtn = new JButton("New entry");
    newEntryBtn.setFont(JDUtils.labelFont);
    newEntryBtn.setMargin(new Insets(0, 0, 0, 0));
    newEntryBtn.setForeground(Color.BLACK);
    newEntryBtn.addActionListener(this);
    newEntryBtn.setBounds(10, 285, 80, 25);
    tablePanel.add(newEntryBtn);

    removeEntryBtn = new JButton("Remove");
    removeEntryBtn.setFont(JDUtils.labelFont);
    removeEntryBtn.setMargin(new Insets(0, 0, 0, 0));
    removeEntryBtn.setForeground(Color.BLACK);
    removeEntryBtn.addActionListener(this);
    removeEntryBtn.setBounds(100, 285, 80, 25);
    tablePanel.add(removeEntryBtn);

    tablePanel.setBounds(5,75,295,320);
    add(tablePanel);

    // ------------------------------------------------------------------------------------
    linearPanel = new JPanel();
    linearPanel.setLayout(null);
    linearPanel.setBorder( JDUtils.createTitleBorder("Linear Mapping") );

    minValueLabel =JDUtils.createLabel("Convert min object value to");
    minValueLabel.setBounds(10, 20, 180, 25);
    linearPanel.add(minValueLabel);

    minValueText = new JTextField();
    minValueText.setMargin(JDUtils.zMargin);
    minValueText.setEditable(true);
    minValueText.setFont(JDUtils.labelFont);
    minValueText.setBounds(195, 20, 50, 24);
    minValueText.addActionListener(this);
    linearPanel.add(minValueText);

    maxValueLabel = JDUtils.createLabel("Convert max object value to");
    maxValueLabel.setBounds(10, 45, 180, 25);
    linearPanel.add(maxValueLabel);

    maxValueText = new JTextField();
    maxValueText.setMargin(JDUtils.zMargin);
    maxValueText.setEditable(true);
    maxValueText.setFont(JDUtils.labelFont);
    maxValueText.setBounds(195, 45, 50, 24);
    maxValueText.addActionListener(this);
    linearPanel.add(maxValueText);

    linearPanel.setBounds(5,75,295,320);
    add(linearPanel);


    // ------------------------------------------------------------------------------------
    cancelBtn = new JButton("Cancel");
    cancelBtn.setFont(JDUtils.labelFont);
    cancelBtn.setMargin(new Insets(0, 0, 0, 0));
    cancelBtn.setForeground(Color.BLACK);
    cancelBtn.addActionListener(this);
    cancelBtn.setBounds(217, 400, 80, 25);
    add(cancelBtn);

    applyBtn = new JButton("Apply");
    applyBtn.setFont(JDUtils.labelFont);
    applyBtn.setMargin(new Insets(0, 0, 0, 0));
    applyBtn.setForeground(Color.BLACK);
    applyBtn.addActionListener(this);
    applyBtn.setBounds(127, 400, 80, 25);
    add(applyBtn);

    refreshControls();
    setPreferredSize(new Dimension(304, 430));

  }

  public boolean hasChanged() {
    return hasChanged;
  }

  public JDValueProgram getMapper() {
    return theMapper;
  }

  public boolean setValueAt(String v,int idx) {
    boolean b = theMapper.setValueAt(idx,v);
    if(b) {
      updateRows();
      hasChanged=true;
    }
    return b;
  }

  public boolean setMappingAt(String v,int idx) {
    boolean b = theMapper.setMappingAt(idx,v);
    if(b) {
      updateRows();
      hasChanged=true;
    }
    return b;
  }

  JTable getTable() {
    return theTable;
  }

  public String getDescription() {
    return propName;
  }

  // ---------------------------------------------------------
  // Action listener
  // ---------------------------------------------------------

  public void actionPerformed(ActionEvent e) {

    if(isUpdating) return;

    Object src = e.getSource();
    int m;

    if( src==newEntryBtn ) {

      theMapper.addNewEntry();
      hasChanged=true;
      updateRows();

    } else if (src==removeEntryBtn) {

      int s = theTable.getSelectedRow();
      if(s>=0 && s<theMapper.getEntryNumber()) {
        theMapper.removeEntry(s);
        hasChanged=true;
      }
      updateRows();

    } else if ( src==defaultValueBtn ) {

      switch (theMapper.getType()) {
        case JDValueProgram.COLOR_TYPE:
          Color c = JColorChooser.showDialog(invoker, "Choose default color", theMapper.getDefaultColorMapping());
          if (c != null) {
            theMapper.setDefaultMapping(c.getRed() + "," + c.getGreen() + "," + c.getBlue());
            defaultValueBtn.setBackground(c);
            hasChanged = true;
          }
          defaultValueText.setText(theMapper.getDefaultMapping());
          break;

        case JDValueProgram.BOOLEAN_TYPE:
          boolean ob = theMapper.getDefaultBooleanMapping();
          boolean nb = JDUtils.showBooleanDialog(invoker,"Choose default value",ob);
          if(nb!=ob) {
            theMapper.setDefaultMapping(Boolean.toString(nb));
            hasChanged = true;
          }
          defaultValueText.setText(theMapper.getDefaultMapping());
          break;

        case JDValueProgram.INTEGER_TYPE:
          int oi = theMapper.getDefaultIntegerMapping();
          int ni = JDUtils.showIntegerDialog(invoker,"Enter default value",oi);
          if(ni!=oi) {
            theMapper.setDefaultMapping(Integer.toString(ni));
            hasChanged = true;
          }
          defaultValueText.setText(theMapper.getDefaultMapping());
          break;
      }

    } else if ( src==defaultValueText ) {

      if( !theMapper.setDefaultMapping(defaultValueText.getText()) )
        JOptionPane.showMessageDialog(invoker, "Invalid default value syntax");
      else
        hasChanged = true;
      defaultValueText.setText(theMapper.getDefaultMapping());
      defaultValueText.setCaretPosition(0);
      if(theMapper.getType()==JDValueProgram.COLOR_TYPE)
        defaultValueBtn.setBackground(theMapper.getDefaultColorMapping());

    } else if (src==modelCombo) {

      int s = modelCombo.getSelectedIndex();
      if(s>=JDValueProgram.MAP_BY_VALUE && s<=JDValueProgram.MAP_REMAP)
        if( theMapper.setMode(s) )
          hasChanged=true;
        else
          JOptionPane.showMessageDialog(invoker, "This mode is not allowed for " + propName );
      refreshControls();

    } else if (src==minValueText) {

      try {
        m=Integer.parseInt(minValueText.getText());
        theMapper.setMinLinearValue(m);
        hasChanged=true;
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(invoker, "Invalid number syntax for min value.");
      }
      refreshControls();

    } else if (src==maxValueText) {

      try {
        m=Integer.parseInt(maxValueText.getText());
        theMapper.setMaxLinearValue(m);
        hasChanged=true;
      } catch (Exception ex) {
        JOptionPane.showMessageDialog(invoker, "Invalid number syntax for max value.");
      }
      refreshControls();

    } else if (src==cancelBtn) {

      hasChanged = false;
      ATKGraphicsUtils.getWindowForComponent(this).setVisible(false);

    } else if (src==applyBtn) {

      if(theTable.getCellEditor()!=null)
        theTable.getCellEditor().stopCellEditing();
      ATKGraphicsUtils.getWindowForComponent(this).setVisible(false);

    }

  }

  // ---------------------------------------------------------
  private void refreshControls() {

    isUpdating=true;

    int mode = theMapper.getMode();
    modelCombo.setSelectedIndex(mode);
    switch(mode) {
      case JDValueProgram.MAP_BY_VALUE:
        linearPanel.setVisible(false);
        tablePanel.setVisible(true);
        break;
      case JDValueProgram.MAP_LINEAR:
        linearPanel.setVisible(true);
        tablePanel.setVisible(false);
        minValueText.setText(Integer.toString(theMapper.getMinLinearMapping()));
        maxValueText.setText(Integer.toString(theMapper.getMaxLinearMapping()));
        minValueText.setCaretPosition(0);
        maxValueText.setCaretPosition(0);
        break;
      case JDValueProgram.MAP_REMAP:
        linearPanel.setVisible(false);
        tablePanel.setVisible(false);
        break;
    }

    isUpdating=false;

  }

  private void sizeTable() {

    if (theTable != null) {
      theTable.getColumnModel().getColumn(0).setPreferredWidth(60);
      theTable.getColumnModel().getColumn(2).setPreferredWidth(30);
      theTable.getColumnModel().getColumn(2).setMaxWidth(30);
      theTable.setRowHeight(20);
    }

  }

  private void updateRows() {
    Object[][] rows = new Object[theMapper.getEntryNumber()][3];
    for (int i = 0; i < theMapper.getEntryNumber(); i++) {
      rows[i][0] = theMapper.getValue(i);
      rows[i][1] = theMapper.getMapping(i);
      rows[i][2] = JDUtils.createSetButton(null);
    }
    tableModel.setRows(rows);
    sizeTable();
  }


}
