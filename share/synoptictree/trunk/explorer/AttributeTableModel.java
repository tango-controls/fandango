// File:          AttributeTableAdapter.jaav
// Created:       2002-09-10 13:53:19, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-30 11:23:20, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.util.ArrayList;
import javax.swing.JComponent;
import javax.swing.JLabel;
import com.braju.format.Format;
import fr.esrf.TangoDs.AttrManip;
import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.BooleanScalarEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IBooleanScalar;
import fr.esrf.tangoatk.core.IBooleanScalarListener;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.IImageListener;
import fr.esrf.tangoatk.core.INumberImage;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.IStateListener;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.NumberImageEvent;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.core.Property;
import fr.esrf.tangoatk.core.StateEvent;
import fr.esrf.tangoatk.core.StatusEvent;
import fr.esrf.tangoatk.core.StringScalarEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;

/**
 * Implements parts of the table model needed by AttributeTable
 * 
 * @author Erik ASSUM
 */
public class AttributeTableModel extends EntityTableModel {

    public final static String LABEL = "Label";
    public final static String VALUE = "Value";
    public final static String DISP_UNIT = "Disp. Unit";
    public final static String MIN_VAL = "Min value";
    public final static String MAX_VAL = "Max value";
    public final static String MIN_ALARM = "Min alarm";
    public final static String MAX_ALARM = "Max alarm";
    public final static String UNIT = "Unit";
    public final static String DATA_FORMAT = "Data format";
    public final static String DATA_TYPE = "Data type";
    public final static String DESCRIPTION = "Description";
    public final static String WRITABLE = "Writable";
    public final static String WRITABLE_NAME = "Writable name";
    public final static String MAX_Y = "Max dim y";
    public final static String MAX_X = "Max dim x";
    public final static String STD_UNIT = "Standar unit";
    public final static String SET = "Set";
    protected AttributePanel panel;

    //protected AttributePolledList entitiesToRefresh;
    protected AttributeList entitiesToRefresh;

    /**
     * Class constructor, initializer, with possibility to set status and
     * preferences.
     * 
     * @param status
     *            the status
     * @param preferences
     *            the preferences
     */
    public AttributeTableModel(Status status, Preferences preferences) {
        this.status = status;
	if (true) {
	    entities = new fr.esrf.tangoatk.core.AttributePolledList();
	    entitiesToRefresh = new fr.esrf.tangoatk.core.AttributePolledList();
	} else {
	    entities = new fr.esrf.tangoatk.core.AttributeList();
	    entitiesToRefresh = new fr.esrf.tangoatk.core.AttributeList();
	}
        //entitiesToRefresh.setSynchronizedPeriod(true);
        adapters = new ArrayList();
        columnIdentifiers = new ArrayList();
        this.preferences = preferences;
        setRefreshInterval(preferences.getInt("refreshInterval", 1000));
    }

    /**
     * Columns initialization. Sets the columns titles
     */
    protected void initColumns() {
        columnIdentifiers.add(DEVICE); // , true, deviceRenderer);
        columnIdentifiers.add(NAME); // , true);
        columnIdentifiers.add(LABEL); // , true);
        columnIdentifiers.add(VALUE); // , true, entityRenderer);
        columnIdentifiers.add(DISP_UNIT); // , true);
        columnIdentifiers.add(DESCRIPTION); // , true);
        columnIdentifiers.add(UNIT); // , true);
        columnIdentifiers.add(WRITABLE); // , true);
        columnIdentifiers.add(SET); // , true,

        columnNames = new ArrayList(columnIdentifiers);

        columnNames.add(MIN_ALARM); // , false
        columnNames.add(MAX_ALARM); // , false
        columnNames.add(DATA_FORMAT); // , false
        columnNames.add(DATA_TYPE); // , false
        columnNames.add(MIN_VAL); // , false
        columnNames.add(MAX_VAL); // , false
        columnNames.add(WRITABLE_NAME); // , false
        columnNames.add(MAX_X); // , false
        columnNames.add(MAX_Y); // , false
        columnNames.add(LEVEL); // , false
        columnNames.add(STD_UNIT); // , false

        fireTableStructureChanged();
    }

    /**
     * Gives a prefix representing the name of the attribute table. You might
     * need this to reorganize the table (like adding/removing a column)
     * 
     * @return the <code>StringBuffer</code> containing the prefix
     */
    protected StringBuffer getPreferencePrefix() {
        return new StringBuffer("AttributeTable.");
    }

    /**
     * Returns the value to put in the specified row and column
     * 
     * @param row
     *            the row index
     * @param column
     *            the column index
     * @return the corresponding value, <code>null</code> when no value can
     *         correspond with the specified row and column
     */
    public Object getValueAt(int row, int column) {

        Object o = adapters.get(row);
        AttributeAdapter adapter = (AttributeAdapter) o;
        IAttribute attribute = adapter.getAttribute();

        String header = getColumnName(column);

        if (DEVICE.equals(header))
            return getDeviceAlias(attribute.getDevice());
        if (NAME.equals(header))
            return getEntityAlias(attribute);
        if (LABEL.equals(header))
            return attribute.getLabel();
        if (VALUE.equals(header))
            if (attribute instanceof IBooleanScalar)
                return attribute;
            else
                return adapter;
        if (DISP_UNIT.equals(header))
            return attribute.getDisplayUnit();
        if (MIN_VAL.equals(header))
            if (attribute instanceof INumberScalar)
                return new Double(((INumberScalar) attribute).getMinValue());
            else
                return new Double(Double.NaN);
        if (MAX_VAL.equals(header))
            if (attribute instanceof INumberScalar)
                return new Double(((INumberScalar) attribute).getMaxValue());
            else
                return new Double(Double.NaN);
        if (MIN_ALARM.equals(header))
            if (attribute instanceof INumberScalar)
                return new Double(((INumberScalar) attribute).getMinAlarm());
            else
                return new Double(Double.NaN);
        if (MAX_ALARM.equals(header))
            if (attribute instanceof INumberScalar)
                return new Double(((INumberScalar) attribute).getMinAlarm());
            else
                return new Double(Double.NaN);
        if (UNIT.equals(header))
            return attribute.getUnit();
        if (DATA_FORMAT.equals(header))
            return adapter.getDataFormat();
        if (DATA_TYPE.equals(header))
            return adapter.getDataType();
        if (DESCRIPTION.equals(header))
            return attribute.getDescription();
        if (WRITABLE.equals(header))
            return adapter.getWritable();

        if (WRITABLE_NAME.equals(header))
            return adapter.getWritableName();

        if (MAX_X.equals(header))
            return new Integer(attribute.getMaxXDimension());
        if (MAX_Y.equals(header))
            return new Integer(attribute.getMaxYDimension());
        if (LEVEL.equals(header))
            return adapter.getLevel();
        if (SET.equals(header))
        {
            if (attribute instanceof IBooleanScalar)
            {
                boolean val = ((IBooleanScalar)attribute).getValue();
                return val ? SET + " FALSE" : SET + " TRUE";
            }
            else return SET;
        }

        return null;
    }

    public void load(String name, String alias, String deviceAlias)
            throws ConnectionException {
        IAttribute attribute;

        attribute = (IAttribute) entities.add(name);
        if (deviceList != null)
        {
            deviceList.add(attribute.getDevice());
        }
        //	if (alias != null) attribute.setAlias(alias);
        //	if (deviceAlias != null) attribute.getDevice().setAlias(deviceAlias);
        addAttribute(attribute);
    }

    /**
     * Adds an attribute in the table. Uses <code>addAttribute(...)</code>
     * 
     * @param attribute the attribute to add
     */
    public void addEntity(IEntity attribute) {
        try {
            load(attribute.getName(),null,null);
        } catch (ConnectionException e) {
            status.status("AttributeTableModel.addEntity: Cannot load attribute " + attribute.getName(), e);
        }
    }

    public void removeEntityAt(int row) {
        IEntity attribute = null;
        try
        {
            attribute = this.getEntityAt(row);
        }
        catch(Exception e)
        {
            return;
        }
        panel.removeAttribute(attribute);
        if (deviceList != null)
        {
            deviceList.remove(attribute.getDevice());
        }
        ((EntityAdapter)adapters.get(row)).remove();
        adapters.remove(row);
        //entitiesToRefresh.removeElement(entities.remove(row));
        entitiesToRefresh.remove(attribute.getName());
        fireTableRowsDeleted(row, row);
    }

    public void clear() {
	entitiesToRefresh.clear();
	super.clear();
    }

    /**
     * Adds an attribute in the list of attributes to refresh
     * 
     * @param attribute
     *            the attribute to add
     */
    public void addToRefresher(IAttribute attribute) {
        removeFromRefresher(attribute);
        entitiesToRefresh.add(attribute);
    }

    /**
     * Removes an attribute from the list of attributes to refresh
     * 
     * @param attribute
     *            the attribute to add
     */
    public void removeFromRefresher(IAttribute attribute) {
        while(entitiesToRefresh.remove(attribute.getName()));
    }

    /**
     * Adds an attribute in the table if it is not already present.
     * 
     * @param attribute
     *            the attribute to add
     */
    public void addAttribute(IAttribute attribute) {
        if (exists(attribute))
            return;
        addToRefresher(attribute);
        panel.addEntity(attribute);

        adapters.add(new AttributeAdapter(attribute, adapters.size()));
        fireTableRowsInserted(adapters.size() - 1, adapters.size() - 1);
    }

    /**
     * Adds a number scalar attribute in the table. Uses
     * <code>addAttribute(...)</code>
     * 
     * @param name
     *            the name of the attribute to add
     */
    protected void addNumberScalar(String name) {
        INumberScalar scalar;
        try {
            scalar = (INumberScalar) entities.add(name);
            addAttribute(scalar);
        } catch (ConnectionException e) {
            status.status("AttributeTableModel.addNumberScalar: Cannot load attribute " + name, e);
        }
    }

    /**
     * Adds a string scalar attribute in the table. Uses
     * <code>addAttribute(...)</code>
     * 
     * @param name
     *            the name of the attribute to add
     */
    protected void addStringScalar(String name) {
        IStringScalar scalar;
        try {
            scalar = (IStringScalar) entities.add(name);
            addAttribute(scalar);
        } catch (ConnectionException e) {
            status.status( "AttributeTableModel.addStringScalar: Cannot load attribute " + name, e );
        }
    }

    /**
     * Adds a number spectrum attribute in the table. Uses
     * <code>addAttribute(...)</code>
     * 
     * @param name
     *            the name of the attribute to add
     */
    protected void addNumberSpectrum(String name) {
        INumberSpectrum spectrum;
        try {
            spectrum = (INumberSpectrum) entities.add(name);
            addAttribute(spectrum);
        } catch (ConnectionException e) {
            status.status("AttributeTableModel.addNumberSpectrum: Cannot load attribute " + name, e);
        }
    }

    /**
     * Adds a number image attribute in the table. Uses
     * <code>addAttribute(...)</code>
     * 
     * @param name
     *            the name of the attribute to add
     */
    protected void addNumberImage(String name) {
        INumberImage image;
        try {
            image = (INumberImage) entities.add(name);
            addAttribute(image);
        } catch (ConnectionException e) {
            status.status("AttributeTableModel.addNumberImage: Cannot load attribute " + name, e);
        }
    }

    /**
     * Method that returns a boolean representing if the specified column is the
     * "set" column or not
     * 
     * @param i the column index
     * @return <code>true</code> if the corresponding column is the "set"
     *         column, <code>false</code> otherwise
     */
    protected boolean isExecuteColumn(int i) {
         return SET.equals(columnModel.getColumn(i).getHeaderValue());
    }

    public void refresh() {
        if (!entitiesToRefresh.isRefresherStarted()) {
            entitiesToRefresh.refresh();
            if (deviceList != null) deviceList.refresh();
        }
    }

    public boolean isRefresherStarted() {
        return entitiesToRefresh.isRefresherStarted();
    }

    public void setRefreshInterval(int milliseconds) {
        preferences.putInt("refreshInterval", milliseconds);
        entitiesToRefresh.setRefreshInterval(milliseconds);
        if (deviceList != null) deviceList.setRefreshInterval(milliseconds);
    }

    public int getRefreshInterval() {
        return entitiesToRefresh.getRefreshInterval();
    }

    public void startRefresher() {
        if (!refresherStarted)
        {
            entitiesToRefresh.startRefresher();
            refresherStarted = true;
        }
        if (deviceList != null)  deviceList.start();
    }

    public void stopRefresher() {
        refresherStarted = false;
        entitiesToRefresh.stopRefresher();
        if (deviceList != null)  deviceList.stop();
    }
    
    /**
     * A listener for the attributes in table
     * 
     * @author Erik ASSUM
     */
    class AttributeAdapter implements IStringScalarListener,
            INumberScalarListener, ISpectrumListener, IImageListener,
            IStateListener, EntityAdapter, IBooleanScalarListener {
        int row;

        IAttribute attribute;

        String last = "See tab";

        String format = "";

        double doubleVal;

        boolean boolVal;

        /**
         * returns the <code>IEntity</code> representation of the attribute
         */
        public IEntity getEntity() {
            return attribute;
        }

        /**
         * Refreshes the properties of this attribute
         */
        public void reloadProperties() {
            fireTableRowsUpdated(row, row);
        }

        /**
         * Class constructor, initializer. Associates the listener with an
         * attribute and a row in the table
         * 
         * @param attribute
         *            the attribute
         * @param row
         *            the row index
         */
        public AttributeAdapter(IAttribute attribute, int row) {
            this.row = row;
            this.attribute = attribute;
            attribute.getDevice().addStateListener(this);

            if (attribute instanceof INumberScalar) {
                last = "----";
                ((INumberScalar) attribute).addNumberScalarListener(this);
                format = attribute.getFormat();
            }

            if (attribute instanceof IStringScalar) {
                last = "----";
                ((IStringScalar) attribute).addStringScalarListener(this);
            }

            if (attribute instanceof IBooleanScalar) {
                last = "----";
                ((IBooleanScalar) attribute).addBooleanScalarListener(this);
            }

            if (attribute instanceof INumberSpectrum) {
                ((INumberSpectrum) attribute).addSpectrumListener(this);
            }

            if (attribute instanceof INumberImage) {
                ((INumberImage) attribute).addImageListener(this);
            }
        }

        /**
         * Method to remove listener from the associated attribute. Called when
         * removing an attribute from table
         */
        public void remove() {
            attribute.getDevice().removeStateListener(this);
            if (attribute instanceof INumberScalar) {
                ((INumberScalar) attribute).removeNumberScalarListener(this);
            } else if (attribute instanceof IStringScalar) {
                ((IStringScalar) attribute).removeStringScalarListener(this);
            } else if (attribute instanceof IBooleanScalar) {
                ((IBooleanScalar) attribute).removeBooleanScalarListener(this);
            } else if (attribute instanceof INumberSpectrum) {
                ((INumberSpectrum) attribute).removeSpectrumListener(this);
            } else if (attribute instanceof INumberImage) {
                ((INumberImage) attribute).removeImageListener(this);
            }
        }

        /**
         * useless method (empty)
         * 
         * @param evt
         *            unused
         */
        public void statusChange(StatusEvent evt) {
            /* RG comment : not used */
        }

        /**
         * Changes the state of this listener according a
         * <code>StateEvent</code>
         * 
         * @param evt
         *            the <code>StateEvent</code>
         */
        public void stateChange(StateEvent evt) {
            JComponent r = getDeviceRenderer(getDeviceAlias(attribute
                    .getDevice()));
            if (r == null)
                return;

            r.setBackground(ATKConstant.getColor4State(evt.getState()));
            r.setToolTipText(evt.getState());
            fireTableRowsUpdated(row, row);
        }

        /**
         * Gets the value renderer for this listener. For more informations, see :
         * <code>explorer.EntityTableModel.getRenderer(...)</code>
         * 
         * @return the value renderer
         */
        JComponent getValueRenderer() {
            if (attribute instanceof IBooleanScalar)
                return getRenderer(attribute, VALUE);
            else
                return getRenderer(this, VALUE);
        }

        /**
         * Present because of implementation of stateListener,
         * but empty
         * 
         * @param evt
         *            unused
         */
        public void errorChange(ErrorEvent evt) {
            /* RG comment : not used */
        }

        /**
         * Changes the state of this listener according an
         * <code>AttributeStateEvent</code>
         * 
         * @param evt
         *            the <code>AttributeStateEvent</code>
         */
        public void stateChange(AttributeStateEvent evt) {
            JComponent r = getValueRenderer();
            if (r == null)
                return;

            r.setToolTipText(evt.getState());
            r.setBackground(ATKConstant.getColor4Quality(evt.getState()));
            fireTableRowsUpdated(row, row);
        }

        /**
         * Changes the state of this listener according an
         * <code>StringScalarEvent</code>
         * 
         * @param evt
         *            the <code>StringScalarEvent</code>
         */
        public void stringScalarChange(StringScalarEvent evt) {
            last = evt.getValue();
            updateRenderer();
        }

        /**
         * Changes the state of this listener according an
         * <code>NumberScalarEvent</code>
         * 
         * @param evt
         *            the <code>NumberScalarEvent</code>
         */
        public void numberScalarChange(NumberScalarEvent evt) {
            doubleVal = evt.getValue();
            last = Double.toString(doubleVal);
            updateRenderer();
        }

        /**
         * Changes the state of this listener according a
         * <code>BooleanScalarEvent</code>
         * 
         * @param evt
         *            the <code>BooleanScalarEvent</code>
         */
        public void booleanScalarChange (BooleanScalarEvent evt)
        {
            boolVal = evt.getValue();
            last = boolVal ? "true" : "false";
            updateRenderer();
        }

        /**
         * Updates the renderer of this listener
         */
        void updateRenderer() {
            JComponent r = getValueRenderer();
            if (r == null)
                return;
            if (r instanceof BooleanViewer)
            {
                ((BooleanViewer) r).setText(getLastValue());
            }
            else ((JLabel) r).setText(getLastValue());
            fireTableRowsUpdated(row, row);
        }

        /**
         * useless method (empty)
         * @param evt unused
         */
        public void spectrumChange(NumberSpectrumEvent evt) {
            // we don't to anything on a spectrum change
        }

        /**
         * useless method (empty)
         * @param evt unused
         */
        public void imageChange(NumberImageEvent evt) {
            // nor on an imagechange
        }

        /**
         * Returns the <code>IAttribute</code> representation of the attribute
         */
        public IAttribute getAttribute() {
            return attribute;
        }

        /**
         * Returns the last value of the attribute
         * @return the value of the attribute as a <code>String</code>
         */
        public String getLastValue() {

            if (format.equals("No format") || format == "")
                return last;

            if (format.indexOf('%') == -1)
                return AttrManip.format(format, doubleVal);
            Object[] o = { new Double(doubleVal) };
            return Format.sprintf(format, o);
        }

        /**
         * Same as <code>getLastValue()</code>
         */
        public String toString() {
            return getLastValue();
        }

        // The following methods are just convenience wrappers for the
        // getValueAt of the AttributeAdapter.

        public String getLevel() {
            return ((Property) attribute.getPropertyMap().get("level"))
                    .getPresentation();
        }

        public String getDataFormat() {
            return ((Property) attribute.getPropertyMap().get("data_format"))
                    .getPresentation();
        }

        public String getDataType() {
            return ((Property) attribute.getPropertyMap().get("data_type"))
                    .getPresentation();
        }

        public String getWritable() {
            return ((Property) attribute.getPropertyMap().get("writable"))
                    .getPresentation();
        }

        public String getWritableName() {
            return ((Property) attribute.getPropertyMap().get(
                    "writable_attr_name")).getPresentation();
        }

    }

    public void setSynchronizedPeriod(boolean synchro)
    {
        entitiesToRefresh.setSynchronizedPeriod(synchro);
    }

    /**
     * Returns the AttributePanel associated with this AttributeTableModel
     * @return The AttributePanel associated with this AttributeTableModel
     */
    public AttributePanel getPanel ()
    {
        return panel;
    }

    /**
     * Associates an AttributePanel with this AttributeTableModel
     * @param panel the AttributePanel
     */
    public void setPanel (AttributePanel panel)
    {
        this.panel = panel;
    }
}