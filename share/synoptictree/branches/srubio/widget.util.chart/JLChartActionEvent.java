// JLChartActionEvent.java
//
// Description:

package fr.esrf.tangoatk.widget.util.chart;

import java.util.EventObject;

/** Event sent when when the user select a user action from
  * the contextual menu
  */
public class JLChartActionEvent extends EventObject {

  private String  actionName;
  private boolean state;

  public JLChartActionEvent(Object source, String name) {
    super(source);
    actionName = name;
    state=false;
  }

  public JLChartActionEvent(Object source, String name, boolean s) {
    super(source);
    actionName = name;
    state=s;
  }

  public void setSource(Object source) {
    this.source = source;
  }

  public String getVersion() {
    return "$Id$";
  }

  public Object clone() {
    return new JLChartActionEvent(source, actionName);
  }


  /**
   * Gets the action name
   */
  public String getName() {
    return actionName;
  }

  /**
   * Gets the action state
   */
  public boolean getState() {
    return state;
  }

}
