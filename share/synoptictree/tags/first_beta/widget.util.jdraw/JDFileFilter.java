package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.filechooser.FileFilter;
import java.io.File;

/** A basic file filter class */
public class JDFileFilter extends FileFilter {

  private String   description = null;
  private String[] extensions;

  /**
   * Construct a File filter for the set of extension.
   * @param desc Description of this filter
   * @param ext Extension set
   */
  public JDFileFilter(String desc,String[] ext) {
    extensions = ext;
    description = desc + "  (";
    for(int i=0;i<ext.length;i++) {
      description += "." + ext[i];
      if(i<ext.length-1)
        description += ",";
    }
    description += ")";
  }

  // -------------------------------------------------
  // FileFilter interface
  // -------------------------------------------------
  /**
   * Returns true if the specified file has an allowed extension.
   * @param f File to be tested.
   */ 
  public boolean accept(File f) {
    if (f != null) {
      if (f.isDirectory())
        return true;
      return isWantedExtension(getExtension(f));
    }
    return false;
  }
  /**
   * Return the description of this FileFilter
   */
  public String getDescription() {
    return description;
  }

  // -------------------------------------------------

  private String getExtension(File f) {
    if (f != null) {
      String filename = f.getName();
      int i = filename.lastIndexOf('.');
      if (i > 0 && i < filename.length() - 1)
        return filename.substring(i + 1).toLowerCase();
    }
    return null;
  }

  private boolean isWantedExtension(String ext) {

    int i=0;
    boolean found=false;

    if( ext==null )
      return false;

    while(i<extensions.length && !found) {
      found = ext.equalsIgnoreCase(extensions[i]);
      i++;
    }

    return found;
  }


}
