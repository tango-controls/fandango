// File:          JLChartListener.java
//

package fr.esrf.tangoatk.widget.util.chart;
import java.util.EventListener;

/**  An interface to handle some user defined action available from
 * the chart contextual menu
 */
public interface IJLChartActionListener extends EventListener, java.io.Serializable {

    /**
      * Called when the user select a user action (available from
      * contextual chart menu)
      * @param evt Event object (containing acion name and state)
      * @see JLChart#addUserAction
      */
    public void actionPerformed(JLChartActionEvent evt);

   /**
    * Called when the the action name starting with 'chk'
    * (displayed as check box menu item) and each time the chart menu
    * is shown.
    * if several listener handle the same action, the result will be a
    * logical and of all results.
    * @param evt Event object (containing acion name)
    * @see JLChart#addUserAction
    */
    public boolean getActionState(JLChartActionEvent evt);

}
