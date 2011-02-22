// File:          Refresher.java
// Created:       2002-10-03 13:48:38, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 10:47:9, erik>
// 
// $Id$
// 
// Description:       

package explorer.ui;

/**
 * <code>Refresher</code> describes the methods needed by the RefreshUI
 *
 * @author <a href="mailto:erik@assum.net">Erik Assum</a>
 * @version $Revision$
 */
public interface Refresher {

    public void startRefresher();

    public void stopRefresher();

    public void refresh();

    public void setRefreshInterval(int interval);

    public int getRefreshInterval();
}
