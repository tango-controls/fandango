package fr.esrf.tangoatk.widget.util.jdraw;

import java.util.Vector;

/** A class to add JDrawable JDSwingObject to the editor.
 * @see JDrawEditorFrame#main
 * */
public class JDrawableList {

  // ---------------------------------------------------------
  // initialise default JDrawable list for the JDrawEditorFrame.
  // ---------------------------------------------------------
  static private void init() {

    if(!inited) {

      drawableList.add("fr.esrf.tangoatk.widget.attribute.NumberScalarWheelEditor");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.SimpleScalarViewer");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.NumberSpectrumViewer");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.NumberImageViewer");
      drawableList.add("fr.esrf.tangoatk.widget.command.VoidVoidCommandViewer");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.BooleanScalarCheckBoxViewer");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.NumberScalarComboEditor");
      drawableList.add("fr.esrf.tangoatk.widget.attribute.StringScalarComboEditor");

      inited=true;
    }

  }

  /**
   * Add a JDrawable to the editor, It must be called before the
   * JDrawEditor frame is constructed.
   * @param className JDrawable object to add.
   * @see JDrawEditorFrame#main
   */
  static public void addClass(String className) {
    init();
    drawableList.add(className);
  }

  /**
   * Returns the list of drawable object known by the editor.
   */
  static public String[] getDrawalbeList() {
    init();
    String[] ret = new String[drawableList.size()];
    for(int i=0;i<drawableList.size();i++)
      ret[i] = (String)drawableList.get(i);
    return ret;
  }

  private static Vector drawableList = new Vector();
  private static boolean inited = false;

}
