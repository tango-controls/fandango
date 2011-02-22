// File:          Icons.java
// Created:       2002-07-17 10:01:43, assum
// By:            <erik@assum.net>
// Time-stamp:    <2002-07-17 10:15:41, assum>
// 
// $Id$
// 
// Description:       

package fr.esrf.tangoatk.widget.icons;
import javax.swing.ImageIcon;

public class Icons {
    private static ImageIcon property = new ImageIcon(Icons.class.getResource("/fr/esrf/tangoatk/widget/icons/Properties16.gif"));

    public static ImageIcon getPropertyIcon() {
	return property;
    }
}
