// File:          DeviceList.java
// Created:       2006-05-10 13:53:46, SOLEIL
// By:            SOLEIL
// Time-stamp:    
// 
// $Id: 
// 
// Description:       
package explorer;

import java.util.Hashtable;
import java.util.Iterator;
import java.util.Set;
import fr.esrf.tangoatk.core.IDevice;
import fr.esrf.tangoatk.core.IRefreshee;
import fr.esrf.tangoatk.core.Refresher;

/**
 * A class to manage a list of devices to refresh
 * @author SOLEIL
 *
 */
public class DeviceList extends Hashtable implements IRefreshee
{
    protected Refresher refresher;
    protected boolean refresherStarted;

    public DeviceList ()
    {
        super();
        refresher = new Refresher();
        refresher.stop();
        refresher.addRefreshee(this);
        refresher.setRefreshInterval(1000);
        refresherStarted = false;
    }

    public Object put(Object key, Object value)
    {
        Object obj = this.get(key);
        if (key instanceof IDevice && value instanceof Integer)
        {
            super.put(key, value);
        }
        return obj;
    }

    /**
     * Adds a device in the table, if it is not already present.
     * Otherwise, increase its associated number.
     * @param device
     */
    public void add(IDevice device)
    {
        Object associated = this.get(device);
        Integer count = associated == null ? new Integer( 1 ) : new Integer( ((Integer)associated).intValue() + 1 );
        put(device, count);
    }

    /**
     * Will decrease the number associated to the device if the key is an IDevice.
     * If the number becomes 0, remmoves the Device from table.
     */
    public Object remove(Object key)
    {
        Object associated = this.get(key);
        if (key instanceof IDevice)
        {
            Integer count = associated == null ? new Integer( 0 ) : new Integer( ((Integer)associated).intValue() - 1 );
            if (count.intValue() <= 0)
            {
                super.remove(key);
            }
            else put(key, count);
        }
        return associated;
    }

    public void refresh ()
    {
        Set deviceSet = keySet();
        Iterator deviceIterator = deviceSet.iterator();
        while (deviceIterator.hasNext())
        {
            IDevice device = (IDevice)deviceIterator.next();
            device.refresh();
        }
    }

    /**
     * Sets the refresher's refresh interval
     * @param milliseconds The refresh interval
     */
    public void setRefreshInterval(long milliseconds)
    {
        refresher.setRefreshInterval(milliseconds);
    }

    /**
     * Sets the refresher's synchronized period variable
     * @param synchro The synchronized period variable
     */
    public void setSynchronizedPeriod(boolean synchro)
    {
        refresher.setSynchronizedPeriod(synchro);
    }

    /**
     * Sets the refresher's trace unexpected variable
     * @param trace The trace unexpected variable
     */
    public void setTraceUnexpected(boolean trace)
    {
        refresher.setTraceUnexpected(trace);
    }

    /**
     * Starts refresher;
     */
    public void start()
    {
        if (!isRefresherStarted()) refresher.start();
        refresherStarted = true;
    }

    /**
     * Stops refresher;
     */
    public void stop()
    {
        refresher.stop();
        refresherStarted = false;
    }

    /**
     * Returns a boolean to know wheather the refresher of this list is started
     * or not
     * 
     * @return A boolean to know wheather the refresher of this list is started
     *         or not
     */
    public boolean isRefresherStarted ()
    {
        return refresherStarted;
    }

}
