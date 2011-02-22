// File:          Status.java
// Created:       2003-01-16 15:28:06, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2003-01-16 15:30:38, erik>
// 
// $Id$
// 
// Description:       
package explorer;
/** Interface for status bar*/
public interface Status {

    /**
     * To put a message in status bar because of an exception
     * @param message the message
     * @param e the exception associated
     */
    public void status(String message, Exception e);

}
