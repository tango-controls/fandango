// File:          Adapter.java
// Created:       2002-10-01 10:51:50, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 14:16:34, erik>
// 
// $Id$
// 
// Description:       
package explorer;

import fr.esrf.tangoatk.core.*;

/**
 * <code>EntityAdapter</code> serves as the connection between the
 * command and attribute table models. 
 * @author <a href="mailto:erik@assum.net">Erik Assum</a>
 * @version $Revision$
 */
interface EntityAdapter {

    /**
     * <code>getEntity</code> returns the entity of this adapter
     *
     * @return an <code>IEntity</code> value
     */
    public IEntity getEntity();

    /**
     * <code>reloadProperties</code> is called to make sure the 
     * newly edited properties are displayed correctly in the table.
     */
    public void reloadProperties();

    /**
     * <code>remove</code> cleans up the adapter.
     *
     */
    public void remove();

}
