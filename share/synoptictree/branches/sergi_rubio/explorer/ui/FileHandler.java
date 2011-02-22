// File:          FileHandler.java
// Created:       2002-10-03 13:52:10, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 10:35:53, erik>
// 
// $Id$
// 
// Description:       

package explorer.ui;
import java.io.File;

/**
 * <code>FileHandler</code> describes the methods needed by the file ui
 *
 * @author <a href="mailto:erik@assum.net">Erik Assum</a>
 * @version $Revision$
 */
public interface FileHandler {

    public void open(File file);

    public void quit();

    public void newFile();

    public void save(File file);
    
    public void close();
}
