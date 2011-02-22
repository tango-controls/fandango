package fr.esrf.tangoatk.widget.util.chart;

import fr.esrf.tangoatk.widget.util.JTableRow;

import javax.swing.*;
import java.awt.*;

/**
 * Table dialog.
 */
public class JLTable extends JFrame {

  JTableRow theTable;

  /**
   * Construction
   */
  public JLTable() {

    theTable = new JTableRow();
    setContentPane(theTable);
    setTitle("Graph data");

  }

  /**
   * Sets the data.
   * @param data Handle to data array.
   * @param colNames Name of columns
   */
  public void setData(Object[][] data, String[] colNames) {
    theTable.setData(data,colNames);
  }

  /**
   * Clear the table
   */
  public void clearData() {
    theTable.clearData();
  }

  // Center the window
  public void centerWindow() {

    theTable.adjustColumnSize();
    theTable.adjustSize();

    // Center the frame and saturate to 800*600
    Toolkit toolkit = Toolkit.getDefaultToolkit();
    Dimension scrsize = toolkit.getScreenSize();
    pack();
    Dimension appsize = getPreferredSize();
    if( appsize.height>600 ) {
      appsize.height=600;
      if(appsize.width<800) {
        // When we saturate the height
        // it is better to reserver space for
        // the vertical scrollbar
        appsize.width += 16;
      }
    }
    if( appsize.width>800 ) appsize.width=800;

    int x = (scrsize.width - appsize.width) / 2;
    int y = (scrsize.height - appsize.height) / 2;
    setBounds(x, y, appsize.width, appsize.height);

  }

}