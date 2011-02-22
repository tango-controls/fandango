// By:            <srubio@cells.es>
// Time-stamp:    <2007-06-29 13:49:46, srubio>
// 
package fr.esrf.tangoatk.widget.device.tree;
import fr.esrf.TangoApi.Database;

import fr.esrf.tangoatk.core.*;


public class HierarchyNode extends FamilyNode {
	private String filename=null;
	private String config=null;

	public HierarchyNode(String name, Database db) {
		super(name, db);
	}
	public HierarchyNode(Object parent, String name, Database db) {
		super(parent, name, db);
	}
	public void setFileName(String filename) {
		this.filename=filename;
	}
	public String getFileName() {
		return filename;
	}
	public void setConfig(String config) {
		this.config=filename;
	}
	public String getConfig() {
		return config;
	}    
}

