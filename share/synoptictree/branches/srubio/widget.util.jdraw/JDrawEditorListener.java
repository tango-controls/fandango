package fr.esrf.tangoatk.widget.util.jdraw;

/** An interface to handle interaction between the editor and the main program. */
public interface JDrawEditorListener {

  /** Called when the user end the creation mode */
  public void creationDone();

  /** Called when the selection change */
  public void selectionChanged();

  /** Called when the drawing currently edited change, also called after laoding a file. */
  public void valueChanged();

  /** Called when the clipboard change , after a copy/cut */
  public void clipboardChanged();

  /** Called when the size of the editor change, usualy after a zoom or a load.
   * Note: If the editor is within a JScrollPane, a called to revalidate on this
   * ScrollPane is needed.
   * */
  public void sizeChanged();


}
