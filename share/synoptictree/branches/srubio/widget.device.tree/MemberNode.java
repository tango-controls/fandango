// File:          MemberNode.java
// Created:       2002-09-17 12:39:15, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-09-17 13:49:46, erik>
// 
// $Id$
// 
// Description:       
package fr.esrf.tangoatk.widget.device.tree;
import fr.esrf.TangoApi.Database;

import fr.esrf.tangoatk.core.*;


public class MemberNode extends FamilyNode {
    FamilyNode parent;
    AttributeList attributes;
    CommandList commands;
    IDevice device;
    
    public MemberNode(FamilyNode family, String name, Database db) {
	super(name, db);
	this.parent = family;
	parent.addChild(this);
    }

    public void setAttributeList(AttributeList list) {
	attributes = list;
    }

    public void setCommandList(CommandList list) {
	commands = list;
    }

    public void setDevice(IDevice device) {
	this.device = device;
    }

    public String getName() {
	return parent.getName() + "/" + name;
    }

    public String getShortName() {
    return name;
    }    
}
