/** A panel for Extensions editing */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import javax.swing.border.Border;
import javax.swing.event.DocumentListener;
import javax.swing.event.AncestorListener;
import javax.swing.event.AncestorEvent;
import javax.swing.event.DocumentEvent;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableCellEditor;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

class MultiLineCellRenderer extends JTextArea implements TableCellRenderer {

  static Color selColor = new Color(200,200,255);
  static Border selBorder = BorderFactory.createLineBorder(selColor);

  public MultiLineCellRenderer() {
    setEditable(false);
    setLineWrap(false);
    setWrapStyleWord(false);
  }

  public Component getTableCellRendererComponent(JTable table, Object value,
                                                 boolean isSelected, boolean hasFocus, int row, int column) {

    if (value instanceof String) {
      setText((String) value);
      // set the table's row height, if necessary
      //updateRowHeight(row,getPreferredSize().height);
    } else
      setText("");

    if (row==table.getSelectedRow() && column==0)
      setBackground(selColor);
    else
      setBackground(Color.WHITE);

    if(isSelected && column==1) {
      setBorder(selBorder);
    } else {
      setBorder(null);
    }

    return this;
  }
}

class MultiLineCellEditor extends AbstractCellEditor implements TableCellEditor {

  MyTextArea textArea;
  JTable table;

  public MultiLineCellEditor(JTable ta) {
    super();
    table = ta;
    // this component relies on having this renderer for the String class
    MultiLineCellRenderer renderer = new MultiLineCellRenderer();
    table.setDefaultRenderer(String.class, renderer);

    textArea = new MyTextArea();
    textArea.setLineWrap(false);
    textArea.setWrapStyleWord(false);
    textArea.setBorder(MultiLineCellRenderer.selBorder);
  }

  // This method determines the height in pixel of a cell given the text it contains
  private int cellHeight(int row, int col) {
    if (row == table.getEditingRow() && col == table.getEditingColumn())
      return textArea.getPreferredSize().height;
    else
      return table.getDefaultRenderer(String.class).getTableCellRendererComponent(table,
                                                                                  table.getModel().getValueAt(row, col), false, false, row, col).getPreferredSize().height;
  }

  void updateRows() {
    for (int i = 0; i < table.getRowCount(); i++) updateRow(i);
  }

  void updateRow(int row) {
    int maxHeight = 0;
    for (int j = 0; j < table.getColumnCount(); j++) {
      int ch;
      if ((ch = cellHeight(row, j)) > maxHeight) {
        maxHeight = ch;
      }
    }
    table.setRowHeight(row, maxHeight);
  }

  public Object getCellEditorValue() {
    return textArea.getText();
  }

  public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected,
                                               int row, int column) {
    textArea.rowEditing = row;
    textArea.columnEditing = column;
    textArea.setEditable(true);
    textArea.ingoreChange = true;
    textArea.setText(table.getValueAt(row, column).toString());
    textArea.ingoreChange = false;

    // Column 0 not editable
    return textArea;
  }

  class MyTextArea extends JTextArea implements DocumentListener {

    boolean ingoreChange = true;
    int rowEditing;
    int columnEditing;

    MyTextArea() {
      getDocument().addDocumentListener(this);
      // This is a fix to Bug Id 4256006
      addAncestorListener(new AncestorListener() {
        public void ancestorAdded(AncestorEvent e) {
          requestFocus();
        }

        public void ancestorMoved(AncestorEvent e) {
        }

        public void ancestorRemoved(AncestorEvent e) {
        }
      });
    }

    public void updateField() {
      if (!ingoreChange) {
        table.setValueAt(getText(), rowEditing, columnEditing);
        updateRow(rowEditing);
      }
    }

    public void insertUpdate(DocumentEvent e) {
      updateField();
    }

    public void removeUpdate(DocumentEvent e) {
      updateField();
    }

    public void changedUpdate(DocumentEvent e) {
    }

  }
}

class JDExtensionPanel extends JPanel implements ActionListener {

  JDObject[] allObjects = null;
  JDrawEditor invoker;
  JTable theTable;
  JScrollPane tableView;
  DefaultTableModel theModel;
  JButton newExtensionBtn;
  JButton delExtensionBtn;
  JButton editExtensionBtn;
  JButton helpExtensionBtn;
  JButton applyBtn;
  MultiLineCellEditor cellEditor = null;

  static String colName[] = {"Name", "Value"};

  public JDExtensionPanel(JDObject[] p, JDrawEditor jc) {

    invoker = jc;

    setLayout(null);
    setBorder(BorderFactory.createEtchedBorder());
    setPreferredSize(new Dimension(380, 290));

    // ------------------------------------------------------------------------------------
    JPanel extPanel = new JPanel(null);
    extPanel.setBorder(JDUtils.createTitleBorder("Extensions"));
    extPanel.setBounds(5, 5, 370, 280);

    theModel = new DefaultTableModel() {
      public Class getColumnClass(int columnIndex) {
        return String.class;
      }
      public boolean isCellEditable(int row, int column) {
        return column==1;
      }
      public void setValueAt(Object aValue, int row, int column) {
        if(!aValue.equals(getValueAt(row,column))) {
          super.setValueAt(aValue,row,column);
          applyBtn.setEnabled(true);
        }
      }
    };

    theTable = new JTable(theModel);

    cellEditor = new MultiLineCellEditor(theTable);
    theTable.setDefaultEditor(String.class, cellEditor);

    tableView = new JScrollPane(theTable);
    tableView.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
    tableView.setBounds(10, 20, 350, 220);
    extPanel.add(tableView);

    newExtensionBtn = new JButton("New");
    newExtensionBtn.setMargin(new Insets(0, 0, 0, 0));
    newExtensionBtn.setFont(JDUtils.labelFont);
    newExtensionBtn.addActionListener(this);
    newExtensionBtn.setBounds(10, 245, 50, 24);
    extPanel.add(newExtensionBtn);

    delExtensionBtn = new JButton("Delete");
    delExtensionBtn.setMargin(new Insets(0, 0, 0, 0));
    delExtensionBtn.setFont(JDUtils.labelFont);
    delExtensionBtn.addActionListener(this);
    delExtensionBtn.setBounds(65, 245, 60, 24);
    extPanel.add(delExtensionBtn);

    editExtensionBtn = new JButton("Edit");
    editExtensionBtn.setMargin(new Insets(0, 0, 0, 0));
    editExtensionBtn.setFont(JDUtils.labelFont);
    editExtensionBtn.addActionListener(this);
    editExtensionBtn.setBounds(130, 245, 60, 24);
    extPanel.add(editExtensionBtn);

    helpExtensionBtn = new JButton("?");
    helpExtensionBtn.setMargin(new Insets(0, 0, 0, 0));
    helpExtensionBtn.setFont(JDUtils.labelFont);
    helpExtensionBtn.addActionListener(this);
    helpExtensionBtn.setBounds(195, 245, 30, 24);
    extPanel.add(helpExtensionBtn);

    applyBtn = new JButton("Apply");
    applyBtn.setMargin(new Insets(0, 0, 0, 0));
    applyBtn.setFont(JDUtils.labelFont);
    applyBtn.addActionListener(this);
    applyBtn.setBounds(270, 245, 90, 24);
    applyBtn.setEnabled(false);
    extPanel.add(applyBtn);

    add(extPanel);
    updatePanel(p);

  }

  public void updatePanel(JDObject[] objs) {

    allObjects = objs;
    refreshTable();

  }

  private void refreshTable() {

    if(allObjects==null || allObjects.length==0) {

      theModel.setDataVector(null,colName);
      delExtensionBtn.setEnabled(false);
      editExtensionBtn.setEnabled(false);
      helpExtensionBtn.setEnabled(false);

    } else {

      int sz = allObjects[0].getExtendedParamNumber();
      Object[][] rows = new Object[sz][2];
      for(int i=0;i<sz;i++) {
        rows[i][0]=allObjects[0].getExtendedParamName(i);
        rows[i][1]=allObjects[0].getExtendedParam(i);
      }
      theModel.setDataVector(rows, colName);
      cellEditor.updateRows();

      delExtensionBtn.setEnabled(sz>0);
      editExtensionBtn.setEnabled(sz>0);
      helpExtensionBtn.setEnabled(sz>0);

    }
    applyBtn.setEnabled(false);
    theTable.getColumnModel().getColumn(1).setPreferredWidth(230);

  }

  // ---------------------------------------------------------
  // Action listener
  // ---------------------------------------------------------
  public void actionPerformed(ActionEvent e) {
    Object src = e.getSource();
    int i;
    if (src == newExtensionBtn) {

      String newExt = JOptionPane.showInputDialog("Enter extension name");
      if (newExt != null) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].addExtension(newExt);
        refreshTable();
        invoker.setNeedToSave(true, "New extension");
      }

    } else if (src == delExtensionBtn) {

      int row = theTable.getSelectedRow();
      if (row >= 0) {
        for (i = 0; i < allObjects.length; i++)
          allObjects[i].removeExtension(row);
        refreshTable();
        invoker.setNeedToSave(true, "Remove extension");
      } else {
        JOptionPane.showMessageDialog(this,"Please select a row first.","Error",JOptionPane.ERROR_MESSAGE);
      }

    } else if (src == applyBtn) {

      if (theModel.getRowCount() > 0) {

        // Reapply the whole extension set
        for (int row = 0; row < theModel.getRowCount(); row++) {
          String extName = (String) theModel.getValueAt(row, 0);
          String value = (String) theModel.getValueAt(row, 1);
          applyExtension(extName,value);
        }
        invoker.setNeedToSave(true, "Edit extension");
        refreshTable();

      }

    } else if (src==editExtensionBtn) {

      int row = theTable.getSelectedRow();
      if(row>=0) {
        String extName = (String) theModel.getValueAt(row, 0);
        String value = (String) theModel.getValueAt(row, 1);
        String newValue = JDExtensionEditor.showExtensionEditor(this,"Edit "+extName,value);
        if(newValue!=null) {
          applyExtension(extName,newValue);
          invoker.setNeedToSave(true, "Edit extension");
        }
        refreshTable();
      } else {
        JOptionPane.showMessageDialog(this,"Please select a row first.","Error",JOptionPane.ERROR_MESSAGE);
      }

    } else if (src==helpExtensionBtn) {

      int row = theTable.getSelectedRow();
      if(row>=0) {
        String extName = (String) theModel.getValueAt(row, 0);
        String helpStr = allObjects[0].getExtendedParamDesc(extName);
        if(helpStr!=null && helpStr.length()>0) {
          JOptionPane.showMessageDialog(this,helpStr,"Help for " + extName,JOptionPane.INFORMATION_MESSAGE);
        } else {
          JOptionPane.showMessageDialog(this,"No help for "+extName+".","Error",JOptionPane.ERROR_MESSAGE);
        }
      } else {
        JOptionPane.showMessageDialog(this,"Please select a row first.","Error",JOptionPane.ERROR_MESSAGE);
      }

    }

  }

  private void applyExtension(String extName,String value) {

    JDObject obj = allObjects[0];

    obj.setExtendedParam(extName,value);

    if(obj instanceof JDSwingObject) {
      // Only swing object can be graphicaly affected by an extended param.
      invoker.repaint(obj.getRepaintRect());
    }

    for (int i = 1; i < allObjects.length; i++) {
      obj = allObjects[i];
      if(obj instanceof JDSwingObject ) {
        // Ignore error for other objects
        ((JDSwingObject)obj).setExtendedParam(extName,value,true);
        invoker.repaint(obj.getRepaintRect());
      } else {
        obj.setExtendedParam(extName, value);
      }
    }

  }


}
