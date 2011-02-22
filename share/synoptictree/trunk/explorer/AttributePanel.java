// File:          AttributePanel.java
// Created:       2002-09-13 12:30:54, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-17 11:48:1, erik>
// 
// $Id$
// 
// Description:       
package explorer;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JCheckBox;
import javax.swing.JComponent;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import javax.swing.table.TableColumn;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberImage;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.IScalarAttribute;
import fr.esrf.tangoatk.widget.attribute.NumberImageTable;
import fr.esrf.tangoatk.widget.attribute.NumberImageViewer;
import fr.esrf.tangoatk.widget.attribute.NumberSpectrumViewer;

/**
 * The <code>AttributePanel</code> is a panel that contains the attribute
 * table and the the viewers for all images that are not of type scalar. It is
 * told by the AttributeTable when to add and remove viewers for these special
 * kind of attributes, that is, images and spectrums.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version 1.0
 */
public class AttributePanel extends JTabbedPane {
    /** the model of construction of the table */
    protected AttributeTableModel tableModel;

    /** the list of attributes */
    protected Map attributes;

    /** to manage the scrolling in the panel */
    protected JScrollPane scroll;

    protected AttributeTable attributeTable;

    /**
     * Class constructor, initializer
     */
    public AttributePanel() {
        attributes = new HashMap();
        initBorder ();
    }

    /**
     * <code>setTable</code> adds the table to this panel, that is, creates
     * "Attributes" tab, which contains all attributes
     */
    public void setTable(AttributeTable table) {
        tableModel = (AttributeTableModel) table.getModel();
        tableModel.setPanel(this);
        attributeTable = table;
        scroll = new JScrollPane(table);
        add(attributeTable, "Attributes");
    }

    /**
     * <code>clear</code> clears all viewers from this tabbedpane, except from
     * the attribute table.
     *  
     */
    public void clear() {
        attributes.clear();
        Component[] components = getComponents();
        for (int i = 0; i < components.length; i++) {
            if (components[i] == attributeTable)
                continue; // the table should never
            // be removed
            if (components[i].getClass().getName().toLowerCase().indexOf("commandtable")>0) {
            	System.out.println("The tab commandTable should never be removed");
                continue; // the table should never
            // be removed
            }
            System.out.println("Removing Tab: AttributePanel."+components[i].getClass().getName());
            remove(components[i]);
        }
    }

    /**
     * Manages what to do when adding an attribute in the main attribute table
     * 
     * @param entity
     *            the attribute to add in the main attribute table
     */
    public void addEntity(IEntity entity) {
        if (entity instanceof IScalarAttribute)
            return;

        if (entity instanceof INumberSpectrum) {
            addAttribute((INumberSpectrum) entity);
            return;
        }

        if (entity instanceof INumberImage) {
            addAttribute((INumberImage) entity);
            return;
        }
    }

    /**
     * <code>addAttribute</code> adds an attribute to this tabbed pane. It
     * will create a viewer for this attribute (in this case an imageviewer),
     * connect it to the attribute and display it in a tab.
     * 
     * @param image
     *            an <code>INumberImage</code> value
     */
    public void addAttribute(INumberImage image) {
        if (attributes.containsKey(image))
            return;
        String alias = image.getAlias();

        if (alias == null) {
            alias = image.getName();
        }
        NumberImageViewer viewer = new NumberImageViewer();
        viewer.setModel(image);

        attributes.put(image, viewer);
        addTab(alias, new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/icons/numberimage.gif")), viewer,
                image.getName());

    }

    /**
     * <code>addAttribute</code> adds an attribute to this tabbed pane. It
     * will create a viewr for this attribute (in this case a spectrum viewer),
     * connect it to the attribute and display it in a tab.
     * 
     * @param spectrum
     *            an <code>INumberSpectrum</code> value
     */
    public void addAttribute(INumberSpectrum spectrum) {
        if (attributes.containsKey(spectrum))
            return;      

        SpectrumViewer viewer = new SpectrumViewer(spectrum);
        String alias = spectrum.getAlias();
        if (alias == null) {
            alias = spectrum.getName();
        }
        attributes.put(spectrum, viewer);
        
        addTab(alias, new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/icons/numberspectrum.gif")), viewer,
                spectrum.getName());
        System.out.println("DEBUG: Spectrum Tab added!");
    }

    /**
     * <code>removeAttribute</code> removes the attributeviewer for the entity
     * passed as parameter.
     * 
     * @param entity
     *            an <code>IEntity</code> value
     */
    public void removeAttribute(IEntity entity) {
        JComponent component = (JComponent) attributes.get(entity);
        attributes.remove(entity);
        remove(component);
    }

    public Dimension getPreferredSize() {
        return new Dimension(0, 0);
    }

    /**
     * <code>getSpectrumGraphSettings</code> return a string containing graph
     * settings of the specified INumberSpectrum
     * 
     * @param entity
     *            an <code>IEntity</code> value
     */
    public String getSpectrumGraphSettings(IEntity entity) {
        if (entity instanceof INumberSpectrum) {
            if (attributes.containsKey(entity)) {
                SpectrumViewer v = (SpectrumViewer) attributes.get(entity);
                return v.getSpectrumViewer().getSettings();
            }
        }
        return "";
    }

    /**
     * <code>setSpectrumGraphSettings</code> set graph config of the specified
     * INumberSpectrum
     * 
     * @param entity
     *            an <code>IEntity</code> value
     */
    public String setSpectrumGraphSettings(IEntity entity, String cfg) {
        if (entity instanceof INumberSpectrum) {
            if (attributes.containsKey(entity)) {
                SpectrumViewer v = (SpectrumViewer) attributes.get(entity);
                return v.getSpectrumViewer().setSettings(cfg);
            }
        }
        return "";
    }

    private void initBorder ()
    {
        Color color = new Color(0,120,0);
        Font font = new Font("Arial", Font.PLAIN, 10);
        String title = "Attribute Panel";
        TitledBorder tb = BorderFactory.createTitledBorder
                ( BorderFactory.createMatteBorder(1, 1, 1, 1, color) ,
                  title ,
                  TitledBorder.CENTER ,
                  TitledBorder.TOP,
                  font,
                  color
                );
        Border border = ( Border ) ( tb );
        this.setBorder( border );
    }

    /**
     * This class manages the tab for spectrum attributes
     * 
     * @author Erik ASSUM
     */
    protected class SpectrumViewer extends JPanel {

        NumberSpectrumViewer chart;

        NumberImageTable imageTable;

        JCheckBox viewTable;

        JScrollPane scroll;

        SpectrumViewer(INumberSpectrum attribute) {
            GridBagConstraints c = new GridBagConstraints();
            viewTable = new JCheckBox("View Table");
            chart = new NumberSpectrumViewer();
            imageTable = new NumberImageTable();

            chart.setModel(attribute);
            imageTable.setImageModel(attribute);

            viewTable.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent evt) {
                    scroll.setVisible(viewTable.isSelected());
                }
            });

            Enumeration columns = imageTable.getColumnModel().getColumns();

            while (columns.hasMoreElements()) {
                ((TableColumn) columns.nextElement()).setMinWidth(40);
            }

            Dimension tableDim = new Dimension(attribute.getXDimension() * 60,
                    17);

            imageTable.setPreferredSize(tableDim);

            scroll = new JScrollPane();
            scroll.setViewportView(imageTable);
            Dimension scrollDim = scroll.getPreferredSize();
            Dimension newScrollDim = new Dimension((int) scrollDim.getWidth(),
                    50);

            scroll.setPreferredSize(newScrollDim);
            scrollDim = scroll.getPreferredSize();

            if (scrollDim.getWidth() <= tableDim.getWidth()) {
                imageTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
            }

            scroll.setHorizontalScrollBarPolicy(
                    JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS
            );

            this.setLayout(new GridBagLayout());
            c.gridx = 0;
            c.gridy = 0;
            c.fill = GridBagConstraints.BOTH;
            c.gridwidth = GridBagConstraints.REMAINDER;
            c.weightx = 1;
            c.weighty = 0.9;
            this.add(chart, c);
            c.fill = GridBagConstraints.HORIZONTAL;
            c.gridy = 1;
            c.weighty = 0;
            c.gridwidth = 1;
            c.weightx = 0.1;
            c.insets = new Insets(13, 45, 13, 0);
            this.add(viewTable, c);
            c.insets = new Insets(0, 0, 0, 25);
            c.gridx = 1;
            c.weightx = 0.9;
            c.weighty = 0.0;
            c.fill = GridBagConstraints.HORIZONTAL;
            this.add(scroll, c);
            viewTable.setSelected(true);

        }

        public NumberSpectrumViewer getSpectrumViewer() {
            return chart;
        }

    }

}