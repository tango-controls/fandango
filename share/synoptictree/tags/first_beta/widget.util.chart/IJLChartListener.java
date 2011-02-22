// File:          JLChartListener.java
// 

package fr.esrf.tangoatk.widget.util.chart;
import java.util.EventListener;

/**   An interface to handle some event comming from the chart */
public interface IJLChartListener extends EventListener, java.io.Serializable {

    /**
      * Called when the user click on the chart
      * @param evt Event object (containing click inforamtion)
      * @return A set of string to display in the value tooltip. Does not
      *         display the tooltip if an empty array is returned.
      *         Keep default behavior when null is returned
      */		
    public String[] clickOnChart(JLChartEvent evt);

}
