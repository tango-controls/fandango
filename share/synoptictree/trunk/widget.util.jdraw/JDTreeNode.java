package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.tree.DefaultMutableTreeNode;

class JDTreeNode extends DefaultMutableTreeNode {

  private boolean areChildrenDefined = false;
  JDObject        theObject;

  public JDTreeNode(JDObject obj) {
    // Object node
    theObject = obj;
  }

  public JDTreeNode() {
    /// Root node
    theObject=null;
  }

  public int getChildCount() {
    if (!areChildrenDefined)
      defineChildNodes();
    return (super.getChildCount());
  }

  // *****************************************************************************************************************
  // Add dinamycaly nodes in the tree when the user open a branch.
  private void defineChildNodes() {

    int i;
    areChildrenDefined = true;

    // Root node
    if( theObject==null )
      return;

    // Add children of group
    if( theObject instanceof JDGroup ) {

      JDGroup g = (JDGroup)theObject;
      for(i=0;i<g.getChildrenNumber();i++)
        add(new JDTreeNode(g.getChildAt(i)));

    } else if ( theObject instanceof JDSlider ) {

      add(new JDTreeNode(((JDSlider)theObject).getCursor()));

    }


  }

  public JDObject getObject() {
    return theObject;
  }

  public String toString() {
     return "Selection";
  }

}
