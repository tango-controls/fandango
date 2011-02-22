// File:          DomainNode.java
// Created:       2002-09-17 12:38:23, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-09-17 13:13:54, erik>
// 
// $Id$
// 
// Description:       
package fr.esrf.tangoatk.widget.device.tree;

import java.util.*;

import javax.swing.tree.*;
import fr.esrf.TangoApi.Database;

public class DomainNode extends DefaultMutableTreeNode {

    String name;
    Database db;
    private List families = new Vector();
    
    public DomainNode(String name, Database db) {
	this.name = name;
	this.db = db;
	
    }

    public void setName(String newname) {
	name=newname;
    }
	
    public String getName() {
	return name;
    }
    
    public Object getChildByName(String name) {
	List objects = getChildren();
	for (int i = 0; i < objects.size(); i++) {
	    Object node = objects.get(i);
	    if (node.toString().equals(name))
		return node;
	    else if (((DomainNode)node).getChildren().size()>0) {
		node = ((DomainNode)node).getChildByName(name);
		if (node!=null) return node;
	    }
	}
	return null;
    }    
    
    public void addChild(Object node) {
	getChildren().add(node);
    }
    
    public List getChildren() {
	System.out.println("DomainNode("+name+").getChildren()");
	return families;
    }

    public String toString() {
	return name;
    }
    
}
