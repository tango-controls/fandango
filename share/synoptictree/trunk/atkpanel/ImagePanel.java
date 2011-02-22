/*
 *  
 *   File          :   ImagePanel.java
 *  
 *   Project       :   atkpanel generic java application
 *  
 *   Description   :   The panel to display a  number image attribute
 *  
 *   Author        :   Faranguiss Poncet
 *  
 *   Original      :   Mars 2002
 *  
 *   $Revision$				$Author$
 *   $Date$					$State$
 *  
 *   $Log$
 *   Revision 3.5  2008/05/26 17:00:47  poncet
 *   The "Scalar" Tab is not refreshed anymore when it's hidden by another Tab. The attributePolledList refreshers (for trends) are not started any more by default.
 *
 *   Revision 3.4  2008/05/16 09:37:51  poncet
 *   Added clearModel() methods in all panel classes. Added clearAllModels() method in MainPanel.
 *
 *   Revision 3.3  2007/11/20 17:48:14  poncet
 *   Suppressed the Status and State attributes from scalar attribute lists because now they are added when attribute factory get + wildcard is called. This was not the case before ATK release 3.0.8.
 *
 *   Revision 3.2  2007/10/08 11:08:41  poncet
 *   Simplified the panel container hierarchy in ImagePanel.java to fix a display problem which was flashing in some cases. NumberImageViewer is now directly inside the ScrollPane.
 *
 *   Revision 3.1  2007/07/17 13:02:49  poncet
 *   For the spectrum and image attributes, now only the visible tab is refreshed to improve performance and network trafic.
 *
 *   Revision 3.0  2007/06/01 13:53:41  poncet
 *   Stop supporting Java 4.
 *
 *   Revision 2.18  2007/05/29 14:07:49  poncet
 *   Added the doFileQuit() method to the MainPanel class.
 *
 *   Revision 2.17  2007/05/23 13:42:53  poncet
 *   Added a public method : setExpertView(boolean) to the MainPanel class.
 *
 *   Revision 2.16  2007/05/03 16:46:21  poncet
 *   Added support for StringImage attributes. Needs ATK 2.8.11 or higher.
 *
 *   Revision 2.15  2007/03/30 15:33:40  poncet
 *   Added the tooltip to some of atk scalar viewer and the state is also added to the stateViewer's tooltip
 *
 *   Revision 2.14  2007/02/09 16:24:18  poncet
 *   Fixed a nullPointerException bug in MainPanel.java:stopAtkPanel() method.
 *
 *   Revision 2.13  2007/02/09 15:20:39  poncet
 *   Added the EnumScalar attributes in scalar attribute lists.
 *
 *   Revision 2.12  2007/01/31 17:52:30  poncet
 *   Removed "view graph" checkbox from spectrum panels. They use exclusively NumberSpectrumViewer now. Compatible with ATK 2.7.2 and higher.
 *
 *   Revision 2.11  2007/01/12 17:09:59  poncet
 *   Added BooleanScalarComboEditor and BooleanTrend. Needs ATK release>=2.6.2. Added the JSplitPane in the MainWindow.
 *
 *   Revision 2.10  2006/12/14 09:45:58  poncet
 *   Bug fixed by Raphael from Soleil concerning the NumberImage and NumberSpectrum attributes operator / expert.
 *
 *   Revision 2.9  2006/10/23 15:17:36  poncet
 *   Workaround to put optionPane in front of Splash. Modified Makefile.
 *
 *   Revision 2.7  2006/04/24 09:36:36  poncet
 *   Fixed a bug concerning Trend Frame. The Trend is now created earlier and centered according to the MainPanel.
 *
 *   Revision 2.6  2006/01/09 15:13:41  poncet
 *   Changed Splash window message
 *
 *   Revision 2.5  2006/01/09 15:03:15  poncet
 *   Fixed few bugs.
 *
 *   Revision 2.4  2005/11/24 13:59:45  poncet
 *   Added menu item to set the device connection timeout. Remove splash window when application is aborted and not standalone.
 *
 *   Revision 2.3  2005/11/10 14:22:08  poncet
 *   Removed traces.
 *
 *   Revision 2.2  2005/11/10 14:13:25  poncet
 *   The atkpanel releases > 2.0 are incompatible with ATK releases below ATKWidget-2.2.0. Release 2.2 of AtkPanel includes code which allows to free memory when atkpanel exits.
 *
 *   Revision 2.1  2005/11/08 14:16:16  poncet
 *   The 2.0 release of atkpanel and higher is incompatible with ATK releases below ATKWidget-2.2.0. Updated the release number displayed in Splash window.
 *
 *   Revision 2.0  2005/11/08 14:11:42  poncet
 *   The ErrorPopup is now a singleton class in ATK. The 2.0 release of atkpanel and higher is incompatible with ATK releases below ATKWidget-2.2.0.
 *
 *   Revision 1.16  2005/05/03 17:02:00  poncet
 *   Added an new attribute list for state and status attributes without events.
 *
 *   Revision 1.15  2005/04/15 12:16:28  poncet
 *   Added the BooleanScalarAttribute, stateAttributeViewer and statusAttributeViewer.
 *
 *   Revision 1.14  2004/11/24 14:11:54  poncet
 *   Added new constructor (Boolean arguments instead of boolean) to be used in synoptics.
 *
 *   Revision 1.13  2004/11/23 09:37:11  poncet
 *   Added ReadOnly mode for MainPanel which supresses all commands. Removed the
 *   TabbedPanel in the MainPanel when the device has no attribute at all. This
 *   Allows to have a smaller window for gauges for example.
 *
 *   Revision 1.11  2004/10/12 12:55:41  poncet
 *   Committed to keep the same CVS revision number for all files.
 *
 *   Revision 1.10  2003/12/16 17:56:56  poncet
 *   Added the handling of StringSpectrum Attributes in atkpanel.
 *
 *   Revision 1.9  2003/09/25 15:10:50  poncet
 *   Fixed a bug in the handling of keepStateRefresher flag. Stop state refresher
 *   when this flag is set to false and the menu bar command preferences->Stop
 *   refreshing is called.
 *
 *   Revision 1.8  2003/09/19 08:01:15  poncet
 *   Tagged to the same revision number all files.
 *
 *   Revision 1.6  2003/09/19 07:59:18  poncet
 *   Added the operator and expert modes handling. Scalars now displayed by
 *   ATK ScalarListViewer. The Image attributes now displayed by the new
 *   ATK viewer NumberImageViewer.
 *
 *   Revision 1.5  2003/02/03 15:48:09  poncet
 *   Fixed a bug in SpectrumPanel.java related to JTableAdapter.
 *
 *   Revision 1.4  2003/02/03 15:32:09  poncet
 *   Committed to have a coherent and identical revision numbers to
 *   avoid using tags.
 *
 *   Revision 1.2  2003/01/28 16:57:40  poncet
 *   Added bin and doc directory
 *
 *   Revision 1.1.1.1  2003/01/28 16:35:55  poncet
 *   Initial import
 *
 *  
 *   Copyright (c) 2002 by European Synchrotron Radiation Facility,
 *  		       Grenoble, France
 *  
 *                         All Rights Reserved
 *  
 *  
 */

package atkpanel;

/**
 *
 * @author  poncet
 */
import java.util.*;
import java.lang.*;
import javax.swing.*;
import javax.swing.event.*;
import java.awt.event.*;
import fr.esrf.tangoatk.core.*;
import fr.esrf.tangoatk.core.attribute.NumberImage;
import fr.esrf.tangoatk.widget.attribute.*;

public class ImagePanel extends javax.swing.JPanel
{

    private JScrollPane             jScrollPane1;
    private JPanel                  jPanel1;
    private NumberImageViewer       imageViewer1;
    private INumberImage            niModel;


    /** Creates new form ImagePanel */
    public ImagePanel()
    {
        niModel = null;
	initComponents();
    }

    /** Creates new form ImagePanel to display a NumberSpectrum attribute */
    public ImagePanel(INumberImage  niAtt)
    {
        initComponents();
	niModel = niAtt;
        imageViewer1.setModel(niAtt);
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    private void initComponents()
    {
            java.awt.GridBagConstraints       gridBagConstraints1;
	    
	    
            gridBagConstraints1 = new java.awt.GridBagConstraints();
            jScrollPane1 = new javax.swing.JScrollPane();
            imageViewer1 = new NumberImageViewer();
            
            setLayout(new java.awt.GridBagLayout());

            gridBagConstraints1.gridx = 0;
            gridBagConstraints1.gridy = 0;
            gridBagConstraints1.fill = java.awt.GridBagConstraints.BOTH;
            gridBagConstraints1.insets = new java.awt.Insets(3, 3, 3, 5);
            gridBagConstraints1.weightx = 1.0;
            gridBagConstraints1.weighty = 1.0;
            add(jScrollPane1, gridBagConstraints1);
        
            jScrollPane1.setViewportView(imageViewer1);
        
    }
    
    protected INumberImage getModel()
    {
       return niModel;
    }

    
    protected void clearModel()
    {
       if (niModel == null) return;
       if (imageViewer1 == null) return;
       imageViewer1.clearModel();
       
       if (niModel instanceof NumberImage)
       {
           NumberImage   ni = (NumberImage) niModel;
           ni.freeInternalData();
       }
    }

}
