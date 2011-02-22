// File:          DeviceTreeCellRenderer.java<2>
// Created:       2002-09-18 16:34:33, erik
// By:            <erik@skiinfo.fr>
// Time-stamp:    <2002-09-18 17:30:42, erik>
// 
// $Id$
// 
// Description:       
package fr.esrf.tangoatk.widget.device.tree;

import javax.swing.tree.*;
import javax.swing.*;
import java.awt.*;
import fr.esrf.tangoatk.widget.dnd.*;

public class DeviceTreeCellRenderer implements TreeCellRenderer {
    TreeCellRenderer defaultRenderer;

    public DeviceTreeCellRenderer() {


    }

    public DeviceTreeCellRenderer(TreeCellRenderer defaultRenderer) {
	this.defaultRenderer = defaultRenderer;
    }

    public Component getTreeCellRendererComponent(JTree tree,
						  Object value,
						  boolean sel,
						  boolean expanded,
						  boolean leaf,
						  int row,
						  boolean hasFocus) {

	defaultRenderer.getTreeCellRendererComponent(tree, value, sel,
						     expanded, leaf, row,
						     hasFocus);
		
	Object o = ((DefaultMutableTreeNode)value).getUserObject();
	if (o == null || !(o instanceof Node)) { 
	    if (value instanceof MemberNode) {
		DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
		renderer.getTreeCellRendererComponent(tree, value, sel,
						      expanded, leaf, row,
						      hasFocus);
		renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/bulbEnabled.gif")));
		return renderer;
	    }	 	    
	    if (value instanceof HierarchyNode) {
		DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
		renderer.getTreeCellRendererComponent(tree, value, sel,
						      expanded, leaf, row,
						      hasFocus);
		renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/synoptic.gif")));
		return renderer;
	    }	      	    
	    if (value instanceof DomainNode) {
		DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
		renderer.getTreeCellRendererComponent(tree, value, sel,
						      expanded, leaf, row,
						      hasFocus);
		renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/ALBA-mini.gif")));
		return renderer;
	    }	 	    
	    return (java.awt.Component)defaultRenderer;	    
	}
	Node node = (Node)o;
	
	if (node instanceof NumberScalarNode) {
	    DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
	    renderer.getTreeCellRendererComponent(tree, value, sel,
						  expanded, leaf, row,
						  hasFocus);
	    renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/numberscalar.gif")));
	    return renderer;
	}

	if (node instanceof StringScalarNode) {
	    DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
	    renderer.getTreeCellRendererComponent(tree, value, sel,
						  expanded, leaf, row,
						  hasFocus);
	    renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/stringscalar.gif")));
	    return renderer;
	}


	if (node instanceof NumberSpectrumNode) {
	    DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
	    renderer.getTreeCellRendererComponent(tree, value, sel,
						  expanded, leaf, row,
						  hasFocus);
	    renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/numberspectrum.gif")));
	    return renderer;
	}

	if (node instanceof NumberImageNode) {
	    DefaultTreeCellRenderer renderer = new DefaultTreeCellRenderer();
	    renderer.getTreeCellRendererComponent(tree, value, sel,
						  expanded, leaf, row,
						  hasFocus);
	    renderer.setIcon(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/icons/numberimage.gif")));
	    return renderer;
	}
	
	return (java.awt.Component)defaultRenderer;
    }
}
		

