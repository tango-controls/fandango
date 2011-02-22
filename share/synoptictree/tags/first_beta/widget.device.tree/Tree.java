// File:          Tree.java
// Created:       2002-09-17 11:53:27, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-11-26 14:57:59, erik>
// 
// $Id$
// 
// Description:       

package fr.esrf.tangoatk.widget.device;

import java.awt.Frame;
import java.awt.event.ComponentListener;
import java.awt.event.FocusListener;
import java.awt.event.HierarchyBoundsListener;
import java.awt.event.HierarchyListener;
import java.awt.event.InputMethodListener;
import java.awt.event.KeyListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.MouseWheelListener;
import java.util.List;
import java.util.Vector;

import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JTree;
import javax.swing.event.TreeExpansionEvent;
import javax.swing.event.TreeWillExpandListener;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.ExpandVetoException;
import javax.swing.tree.TreePath;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;
import fr.esrf.tangoatk.core.ATKException;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.CommandList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.EventSupport;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IDevice;
import fr.esrf.tangoatk.core.IErrorListener;
import fr.esrf.tangoatk.core.IStatusListener;
import fr.esrf.tangoatk.widget.device.tree.DeviceTreeCellRenderer;
import fr.esrf.tangoatk.widget.device.tree.DomainNode;
import fr.esrf.tangoatk.widget.device.tree.FamilyNode;
import fr.esrf.tangoatk.widget.device.tree.HierarchyNode;
import fr.esrf.tangoatk.widget.device.tree.MemberNode;
import fr.esrf.tangoatk.widget.dnd.NodeFactory;
import fr.esrf.tangoatk.widget.util.ATKGraphicsUtils;


public class Tree extends JTree {
    DomainNode[] domains;
    EventSupport propChanges;
    
    DefaultMutableTreeNode top;
    

    public Tree() {
    	System.out.println("SRubio Modified release of fr.esrf.tangoatk.widget.device.Tree, srubio@cells.es, Jan/2008");
	initComponents();

    }

    /*
     * Not really efficient. You'd better re initialize the tree
     * and its listeners
     */
    public void refresh() {
	System.out.println("Tree.refres(): it will reimport all the devices from db!!!!!");
	top.removeAllChildren();
	importFromDb();
    }
    
    public synchronized void removeListeners(){
        propChanges.removeAtkEventListeners();

        ComponentListener[] CL = getComponentListeners();
        for (int i=0; i<CL.length; i++){
            removeComponentListener(CL[i]);
        }
        
        FocusListener[] FL = getFocusListeners();
        for (int i=0; i<FL.length; i++){
            removeFocusListener(FL[i]);
        }
        
        HierarchyBoundsListener[] HBL = getHierarchyBoundsListeners();
        for (int i=0; i<HBL.length; i++){
            removeHierarchyBoundsListener(HBL[i]);
        }
        
        HierarchyListener[] HL = getHierarchyListeners();
        for (int i=0; i<HL.length; i++){
            removeHierarchyListener(HL[i]);
        }
        
        InputMethodListener[] IML = getInputMethodListeners();
        for (int i=0; i<IML.length; i++){
            removeInputMethodListener(IML[i]);
        }
        
        KeyListener[] KL = getKeyListeners();
        for (int i=0; i<KL.length; i++){
            removeKeyListener(KL[i]);
        }
        
        MouseListener[] ML = getMouseListeners();
        for (int i=0; i<ML.length; i++){
            removeMouseListener(ML[i]);
        }
        
        MouseMotionListener[] MML = getMouseMotionListeners();
        for (int i=0; i<MML.length; i++){
            removeMouseMotionListener(MML[i]);
        }
        
        MouseWheelListener[] MWL = getMouseWheelListeners();
        for (int i=0; i<MWL.length; i++){
            removeMouseWheelListener(MWL[i]);
        }
        
        java.beans.PropertyChangeListener[] PCL = getPropertyChangeListeners();
        for (int i=0; i<PCL.length; i++){
            removePropertyChangeListener(PCL[i]);
        }
    }

    protected void error(Exception e) {
	propChanges.fireReadErrorEvent(this, e);
    }

    public void importFromDb() {
	try {
	    propChanges.fireStatusEvent(this, "Importing from database...");
	    Database db = new Database();
	    String [] dms = db.get_device_domain("*");
	    addDomains(top, db, dms);
	} catch (DevFailed e) {
	    error(new ATKException(e));
	}
	propChanges.fireStatusEvent(this, "Importing from database...Done");
	expandRow(0);
    }

    public void addErrorListener(IErrorListener l) {
	propChanges.addErrorListener(l);
    }

    public void removeErrorListener(IErrorListener l) {
	propChanges.removeErrorListener(l);
    }

    public void addStatusListener(IStatusListener l) {
	propChanges.addStatusListener(l);
    }

    public void removeStatusListener(IStatusListener l) {
	propChanges.removeStatusListener(l);
    }

    protected void initComponents() {
	propChanges = new EventSupport();
	
	//top = new DefaultMutableTreeNode("Devices");
	top = new DomainNode("Devices",null);//new Database());
	setTransferHandler(new fr.esrf.tangoatk.widget.dnd.TransferHandler());
	setCellRenderer(new DeviceTreeCellRenderer(getCellRenderer()));	
	addMouseListener(new MouseAdapter() {
		public void mousePressed(MouseEvent e) {
		    /*if (!e.isPopupTrigger())
			return;*/ //removed because it avoided selection by rightclicking
            if (getPathForLocation(e.getX(),e.getY()) != null)
            {
              clearSelection();
			  setSelectionPath( getPathForLocation(e.getX(),e.getY()) );
		    }
		}
	    });
	((DefaultTreeModel)getModel()).setRoot(top);
    }

    protected void addDomains(DefaultMutableTreeNode top, Database db,
			    String[] dms) throws DevFailed {

	domains = new DomainNode[dms.length];

	for (int i = 0; i < dms.length; i++) {
	    String name = dms[i];
	    domains[i] = new DomainNode(name, db);
	    addFamilies(domains[i], db, db.get_device_family(name + "/*"));

	    top.add(domains[i]);
	} // end of for ()
    }

    protected void addFamilies(DomainNode top, Database db, String [] fms)
	throws DevFailed {

	for (int i = 0; i < fms.length; i++) {
	    String name = fms[i];

	    String []members = db.get_device_member(top.getName() + "/" + 
						     name + "/*");

	    FamilyNode family = new FamilyNode(top, name, db);

	    initialAddMembers(family, db, members);
	    top.add(family);
	} // end of for ()
    }

    protected void initialAddMembers(FamilyNode top, Database db,
				   String [] members) throws DevFailed {

	//DefaultMutableTreeNode memberNode = null;
	for (int i = 0; i < members.length; i++) {
	    String m = members[i];

	    MemberNode member = new MemberNode(top, m, db);
	    top.add(member);
	} // end of for ()
    }


    protected void addAttributes(DefaultMutableTreeNode top,
				 AttributeList attributes) {
	NodeFactory nodeFactory = NodeFactory.getInstance();
	IAttribute attribute;
	DefaultMutableTreeNode node;
	for (int j = 0; j < attributes.size(); j++) {
	    attribute = (IAttribute)attributes.get(j);
	    node = new DefaultMutableTreeNode
		(nodeFactory.getNode4Entity(attribute));
	    top.add(node);
	} // end of for ()
    }

    protected void addCommands(DefaultMutableTreeNode top,
			     CommandList commands) {
	NodeFactory nodeFactory = NodeFactory.getInstance();
	ICommand command;
	DefaultMutableTreeNode node;
	for (int j = 0; j < commands.size(); j++) {
	    command = (ICommand)commands.get(j);
	    node = new DefaultMutableTreeNode
		(nodeFactory.getNode4Entity(command));
	    top.add(node);
	} // end of for ()
    }

    /** srubio@cells.es:
     * I've added that method to be able of getting members of a family when the name of the member node
     * already includes the full tango name (domain/family/member).
     */
    private Object getFamilyChild(FamilyNode family, String name) {
	List members = family.getChildren();
	for (int k = 0; k < members.size(); k++) {
	    Object node = members.get(k);	    
	    if (node.toString().equals(name))
		return node;
	    if ((node instanceof MemberNode) && ((MemberNode)node).getName().equals(name))
		return node;
	    ///Or: if (node.toString().indexOf("/")>0 && node.toString().equals(name)) return node;
	}
	return null;
    }
    
    /** It allows to modify the root node name */
    public void setRootName(java.lang.String name) {
	//String t=(String)top.getUserObject(); t=name;
	//top.setUserObject(name);
	((DomainNode)top).setName(name);
	System.out.println("fr.esrf.tangoatk.core.Tree.setRootName("+name+"): top.toString()="+top.toString());
    }
    public String getRootName() {
    	return ((DomainNode)top).getName();
    }
    
    protected void addMembers(FamilyNode family) {
	System.out.println( "Tree.addMembers("+family.toString()+"): entering ...");
	if (family.isFilled()) {
	    System.out.println( "Tree.addMembers: that family was already filled, bye bye");
	    return;
	}
	JDialog waitingDialog = new JDialog((Frame)null,"Importing devices on " + family + "...");
	//waitingDialog.setVisible(true);
	ATKGraphicsUtils.centerDialog(waitingDialog,400,0);
	
	propChanges.fireStatusEvent(this, "Importing devices on " + family + "...");
	family.setFilled(true);
	List  members = family.getChildren();
	List devices = new Vector();
	DeviceFactory factory = DeviceFactory.getInstance();
	System.out.println("addMembers(...): DeviceFactory.getInstance() done");
	for (int i = 0; i < members.size(); i++) {
	    /** srubio@cells.es: 
	     *  I need some member nodes to be named with the full tango name (d/f/m);
	     *  I've modified that method for getting the full path name only if needed.
	     */
	    if (!(members.get(i) instanceof MemberNode)) continue;
	    String fqName = ((MemberNode)members.get(i)).toString();
	    if (fqName.indexOf("/")<0) {
		fqName = ((MemberNode)members.get(i)).getName();
	    } 
	    System.out.println( "Tree.addMembers: fqName="+fqName);
	    try {
		devices.add(factory.getDevice(fqName));
	    } catch (Exception e) {
		family.setFilled(false);
		error(new ConnectionException(e));
	    } // end of try-catch
	} // end of for ()
	addDevices(family, devices);
	//waitingDialog.setVisible(false);
	//waitingDialog=null;
	propChanges.fireStatusEvent(this, "Importing devices on " + family + "..." +
				    "done");
    }
    
    class AttrListAdder implements Runnable {
        MemberNode device = null;
	DefaultMutableTreeNode attributes = null;
	DefaultMutableTreeNode commands = null;
	IDevice d;
	
	AttrListAdder(IDevice _d, MemberNode _dev, DefaultMutableTreeNode _attrs, DefaultMutableTreeNode _comms) {
	    d = _d;
	    device = _dev;
	    attributes = _attrs;
	    commands = _comms;
	}
	
	public void run (){
		AttributeList al = new AttributeList();
		CommandList cl = new CommandList();
	    
		device.setAttributeList(al);
		device.setCommandList(cl);
		device.setDevice(d);

		//IAttribute a;
		System.out.println( "Tree.addDevices("+d.getName()+"): setting attributes list");		
		try {
		    al.add(d.getName() + "/*");
		} catch (ATKException e) {
		    error(e);
		} 

		if (al.size() > 0) {
		    attributes = new DefaultMutableTreeNode("Attributes");

		    device.add(attributes);
		    addAttributes(attributes, al);
		}

		//ICommand c;
		System.out.println( "Tree.addDevices("+d.getName()+"): setting commands list");		
		try {
		    cl.add(d.getName() + "/*");
		} catch (ConnectionException e) {
		    error(e);
		} // end of try-catch
		if (cl.size() > 0) {
		    commands = new DefaultMutableTreeNode("commands");
		    device.add(commands);
		    addCommands(commands, cl);
		}	    
		propChanges.fireStatusEvent(this, "Imported device");// + family + "..." +"done "+i+"/"+devices.size());		
	}
    }
    
    protected void addDevices(FamilyNode family,
			    java.util.List devices) {
        MemberNode device = null;
	DefaultMutableTreeNode attributes = null;
	DefaultMutableTreeNode commands = null;
	IDevice d;
	
	for (int i = 0; i < devices.size(); i++) {
	    //AttributeList al = new AttributeList();
	    //CommandList cl = new CommandList();
	
	    d = (IDevice)devices.get(i);
	    System.out.println( "Tree.addDevices: d.getName()="+d.getName());
	    //device = family.getChild(d.getName());
	    device = (MemberNode)getFamilyChild(family,d.getName());
	    if (device!=null) {
		AttrListAdder ala = new AttrListAdder(d,device,attributes,commands);
		new Thread(ala).start();
	    }
	}
    }
    
    /** It returns the object related to a Node (or null if it doesn't exist) */
    protected Object getNode(String NodeName) {
	/*
	    TreePath tp = getNextMatch(NodeName,0,javax.swing.text.Position.Bias.Forward);
	    if (tp!=null) {
		System.out.println( "Match was: "+tp.toString());
		return tp.getLastPathComponent();
	    } else return null;	
	 */
	return ((DomainNode)top).getChildByName(NodeName);
    }
    
    /** It allows to add a new Family Node below an specified parent */
    public HierarchyNode addNewNode(String ParentNode, String NodeName) {
    	return addNewNode(ParentNode, NodeName, NodeName, null);
    }
    public HierarchyNode addNewNode(String ParentNode, String NodeName, String FileName, String ConfigFile) {
    	HierarchyNode family = null;
    	System.out.println("fr.esrf.tangoatk.widget.Tree.addNewNode("+ParentNode+","+NodeName+"), entering ...");	    	
    	try {
    		family = (HierarchyNode)getNode(NodeName);
    		if (family != null) {
    			System.out.println("fr.esrf.tangoatk.widget.Tree.addNewNode(): The Node "+NodeName+" already exists!");
    		} else {
    			Object parent = getNode(ParentNode);	
    			//DefaultMutableTreeNode parent = (DefaultMutableTreeNode)getNode(ParentNode);
    			Database db = new Database(); ///THIS DB FIELD IS NO LONGER USED!!! IT COULD BE ELIMINATED
    			propChanges.fireStatusEvent(this, "Adding a new Node ...");
    			if (parent == null) { 
    				System.out.println("fr.esrf.tangoatk.widget.Tree.addNewNode(): ParentNode "+ParentNode+" was not found!");
    				parent = top;
    			}
    			System.out.println( "fr.esrf.tangoatk.widget.Tree.addNewNode("+NodeName+"): Parent(obj) is "+parent.toString());
    			family = new HierarchyNode(parent, NodeName, db);
    			///IT SHOULD BE ONLY FOR JDRAW FILES ... NOT FOR OTHER KIND OF HIERARCHIC NODES!
    			family.setFileName(FileName);
    			family.setConfig(ConfigFile);
    			if (parent instanceof HierarchyNode) {
    				HierarchyNode fm=(HierarchyNode)parent;
    				System.out.println("Tree.addNewNode: adding "+family.toString()+" to FamilyNode "+parent.toString());
    				/*		    
		    System.out.print("Parent path("+fm.getChildCount()+"="+fm.getChildren().size()+"): ");   
		    for (int x=0;x<fm.getPath().length;x++) 
			    System.out.print(fm.getPath()[x].toString()+" - ");
		    System.out.println("");
		    System.out.print("Node Childs: ");
		    for (int x=0;x<fm.getChildCount();x++) 
			    System.out.print(fm.getChildAt(x).toString()+" - ");
		    System.out.println("");		    
		    System.out.print("Family Children: ");
		    for (int x=0;x<fm.getChildren().size();x++) 
			    System.out.print(fm.getChildren().get(x).toString()+" - ");
		    System.out.println("");
    				 */		    
    				//fm.add(family); ///Why not addChild(?); addChild is performed inside FamilyNode constructor.
    				fm.insert(family,0);
    				/*
		    System.out.print("Parent path("+fm.getChildCount()+"="+fm.getChildren().size()+"): ");    
		    for (int x=0;x<fm.getPath().length;x++) 
			    System.out.print(fm.getPath()[x].toString()+" - ");
		    System.out.println("");
		    System.out.print("Node Childs: ");
		    for (int x=0;x<fm.getChildCount();x++) 
			    System.out.print(fm.getChildAt(x).toString()+" - ");
		    System.out.println("");		    
		    System.out.print("Family Children: ");
		    for (int x=0;x<fm.getChildren().size();x++) 
			    System.out.print(fm.getChildren().get(x).toString()+" - ");
		    System.out.println("");

		    System.out.print("Children path: ");
		    for (int x=0;x<family.getPath().length;x++) 
			    System.out.print(family.getPath()[x].toString()+" - ");
		    System.out.println("");
    				 */		    
    			} else if (parent instanceof DomainNode) {
    				System.out.println("Tree.addNewNode: adding "+family.toString()+" to DomainNode "+parent.toString());
    				((DomainNode)parent).add(family); ///Why not addChild(?)		
    			} else {
    				System.out.println( "fr.esrf.tangoatk.widget.Tree.addNewNode(): ---------------Solo sé que no se nada-----------------");	    
    			}
    		}
    	} catch (Exception e) { //DevFailed e) {
    		System.out.println("Exception at Tree.addNewNode: "+e.toString());
    		error(new ATKException(e));
    	}

    	propChanges.fireStatusEvent(this, "Adding a new Node ... Done");
    	if (getNode(NodeName)==null) System.out.println("NODE "+NodeName+" DOESN'T EXISTS!!! (1)");
    	collapseRow(0);
    	expandRow(0);
    	/*
	System.out.println("expandRow("+getRowForPath(getNextMatch(ParentNode,0,javax.swing.text.Position.Bias.Forward))+")");
	expandRow(getRowForPath(getNextMatch(ParentNode,0,javax.swing.text.Position.Bias.Forward)));*/
    	if (getNode(NodeName)==null) System.out.println("NODE "+NodeName+" DOESN'T EXISTS!!! (2)");
    	return family;
    }
    
    /** srubio@cells.es
     *  Method added for adding raw lists of devices to the tree
     *  param@ devList It's a Vector of fr.esrf.tangoatk.core.Device objects or String (Synoptic File Names) objects!
     *  It's not going to be easy to manage that ...
     */
    public void importDeviceList(String NodeName, java.util.List devList) {
	System.out.println("Tree.importDeviceList("+NodeName+"): entering ...");
	try {
	    HierarchyNode family = (HierarchyNode)getNode(NodeName);
	    if (family == null) {
		System.out.println("fr.esrf.tangoatk.widget.Tree.importDeviceList(): The Node "+NodeName+" does not exists!");
		return;
	    }
	    propChanges.fireStatusEvent(this, "Importing from Device List ...");	    
	    Database db = null;///new Database(); ///THIS DB FIELD IS NO LONGER USED!!! IT COULD BE ELIMINATED

	    String[] members = new String[devList.size()];
	    for (int k = 0; k<devList.size();k++) {
		///Why a list of devices and not a list of names?
		//members[k]=((fr.esrf.tangoatk.core.Device)devList.get(k)).getName();
		members[k]=(String)devList.get(k);
		
	    }

	    for (int l = 0; l < members.length; l++) {
		    String m = members[l];
		    MemberNode member = new MemberNode(family, m, db);
		    family.add(member);//top.add(member);
		    System.out.println("fr.esrf.tangoatk.widget.Tree.importDeviceList(): Device "+m+ " will be added to Family "+NodeName);
		} // end of for ()	
	    
	} catch (Exception e) { //DevFailed e) {
	    System.out.println("Exception at Tree.importDeviceList: "+e.toString());
	    error(new ATKException(e));
	}
	propChanges.fireStatusEvent(this, "Importing from Device List...Done");
	expandRow(0);
    }

    public void setShowEntities(boolean b) {
	System.out.println("fr.esrf.tangoatk.widget.Tree.setShowEntities("+(b?"true":"false")+"), srubio@cells.es Jan/2008");
	if (!b) return;
	addTreeWillExpandListener(new TreeWillExpandListener() {

 		public void treeWillCollapse(TreeExpansionEvent event)
 		    throws ExpandVetoException {
 		}

 		public void treeWillExpand(TreeExpansionEvent event)
 		    throws ExpandVetoException {
		    System.out.println("fr.esrf.tangoatk.widget.Tree.treeWillExpand()");
 		    TreePath tp = event.getPath();
 		    Object[] path = tp.getPath();
		    if (path.length > 1) {
			DefaultMutableTreeNode node = (DefaultMutableTreeNode)path[path.length-1];
//		    if (path.length == 3) {
// 			DefaultMutableTreeNode node = (DefaultMutableTreeNode)path[2];
 			if (!(node instanceof FamilyNode)) {
			    System.out.println("node '"+node.toString()+"'is not instance of FamilyNode");
 			    return;
			}
			addMembers((FamilyNode)node);
 		    }
		}
	    });
    }
    
    public static void main(String [] args) {
	JFrame frame = new JFrame();
	Tree tree = new Tree();
	tree.setShowEntities(true);
	frame.setContentPane(tree);
	frame.pack();
	frame.setVisible(true);

    }
	
}
