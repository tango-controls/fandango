//
// DataList.java
// Description: A Class to handle 2D graphics plot
//
// JL Pons (c)ESRF 2002

package fr.esrf.tangoatk.widget.util.chart;

/**
 * Class to handle plot data (LinkedList).
 * @author JL Pons
 */

public class DataList implements java.io.Serializable {

	// Original coordinates
	/** x value */
	public double x;
	
	/** y value */
	public double y;
	
	//pointer to next item
	public DataList next;

	//Construct a node
	DataList(double x,double y) {
	  this.x = x;
	  this.y = y;
	  next=null;
	}
	
}
