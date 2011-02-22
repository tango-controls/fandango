// File:          AttributeTableCellRenderer.java
// Created:       2002-09-11 14:55:40, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-14 16:3:13, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.Component;
import java.util.Hashtable;
import java.util.Map;
import javax.swing.JComponent;
import javax.swing.JTable;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellRenderer;
import fr.esrf.tangoatk.core.IBooleanScalar;

/**
 * A cell renderer for device tree application
 * 
 * @author Erik ASSUM
 */
class MyCellRenderer implements TableCellRenderer {
    Map holders = new Hashtable();

    /**
     * Returns the renderer corresponding to the parameters :
     * 
     * @param table
     *            the table that needs the cell renderer component
     * @param value
     *            the value in cell
     * @param hasFocus
     *            defines if the cell has focus or not
     * @param row
     *            the row index
     * @param column
     *            the column index
     */
    public Component getTableCellRendererComponent(JTable table, Object value,
            boolean isSelected, boolean hasFocus, int row, int column) {
        Holder holder;
        if ((holder = (Holder) holders.get(value)) == null) {
            DefaultTableCellRenderer r = new DefaultTableCellRenderer();
            Component comp;
            if (value instanceof IBooleanScalar)
            {
                comp = new BooleanViewer(null);
            }
            else
            {
                comp = r.getTableCellRendererComponent(table, value,
                        false, hasFocus, row, column);
            }
            holder = new Holder(comp);
            holders.put(value, holder);
        }

        return holder.getRenderer();

    }

    /**
     * Returns the renderer adapted to the object in parameter
     * 
     * @param value
     *            the object that needs a renderer
     */
    public JComponent getRenderer(Object value) {
        Holder holder = (Holder) holders.get(value);

        if (holder == null)
            return null;

        return holder.getRenderer();
    }

    /**
     * Removes the correspondance between an object and a renderer
     * 
     * @param value
     *            the object for which you want to remove correspondance with a
     *            renderer
     */
    public void removeRenderer(Object value) {
        holders.remove(value);
    }

    class Holder {
        JComponent renderer;

        protected Holder(Component renderer) {
            this.renderer = (JComponent) renderer;
        }

        public JComponent getRenderer() {
            return renderer;
        }

        public String toString() {
            return renderer.toString();
        }
    }
}