package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;

/** An interface that must be implemented by a JComponent which can be edited with JDrawEditor.
 * @see JDrawableList#addClass
 */
public interface JDrawable {

  /** Call after a component of a JDSwingObject is created, this give a default look
   * and feel for editing. */
  public void initForEditing();

  /** Returns the JComponent that implements this interface. */
  public JComponent getComponent();

  /** Returns list of extension name for this objects (Empty array for none). */
  public String[] getExtensionList();

  /** Sets the specified param.
   * @param name Parameter name (Case unsensitive).
   * @param value Parameter value.
   * @param popupAllowed true when the JDrawable should display a popup if
   * the parameter value is incorrect, false otherwise. Note that the JDrawable
   * must not display an error message if the parameter does not exists even
   * if popupAllowed is true.
   * @return true if parameters has been succesfully applied, false otherwise.
   */
  public boolean setExtendedParam(String name,String value,boolean popupAllowed);

  /**
   * Returns the specified parameter value.
   * @param name Param name (Case unsensitive).
   * @return Empty string if not exists, the value otherwise.
   */
  public String getExtendedParam(String name);

  /**
   * Get a description of this extensions.
   * @param extName Extension name
   * @return Empty string for no description.
   */ 
  public String getDescription(String extName);

}
