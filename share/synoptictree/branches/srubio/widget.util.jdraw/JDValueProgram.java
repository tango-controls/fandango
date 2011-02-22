/** A class to map object value to type used in jdraw */
package fr.esrf.tangoatk.widget.util.jdraw;

import java.util.Vector;
import java.awt.*;
import java.io.FileWriter;
import java.io.IOException;

/* ------------ mapEntry classes ---------------------------*/

abstract class mapEntry {
  int     minValue;
  int     maxValue;
  abstract mapEntry copy();
}

class colorMapEntry extends mapEntry {
  Color color;
  colorMapEntry(int min,int max,Color c) {
    minValue = min;
    maxValue = max;
    color = c;
  }
  mapEntry copy() {
    return new colorMapEntry(minValue,maxValue,new Color(color.getRGB()));
  }
}

class integerMapEntry extends mapEntry {
  int value;
  integerMapEntry(int min,int max,int v) {
    minValue = min;
    maxValue = max;
    value = v;
  }
  mapEntry copy() {
    return new integerMapEntry(minValue,maxValue,value);
  }
}

class booleanMapEntry extends mapEntry {
  boolean value;
  booleanMapEntry(int min,int max,boolean v) {
    minValue = min;
    maxValue = max;
    value = v;
  }
  mapEntry copy() {
    return new booleanMapEntry(minValue,maxValue,value);
  }

}

/** A class to handle dynamic value program. */
public class JDValueProgram {

  /** Map object value to value defined by a correspondence table. */
  public final static int MAP_BY_VALUE=0;
  /** Linear map of object value. (only for INTEGER) */
  public final static int MAP_LINEAR=1;
  /** Remap value to coordinates of the peer JDObject. (only for INTEGER) */
  public final static int MAP_REMAP=2;

  public final static int INTEGER_TYPE   = 1;
  public final static int COLOR_TYPE     = 2;
  public final static int BOOLEAN_TYPE   = 3;

  private int        mode;
  private int        type;
  private Vector     tableMap;
  private mapEntry   defaultValue;
  private int        parsePos;

  /**
   * Contruct a dynamic value program.
   * @param type Type of data.
   * @see #INTEGER_TYPE
   * @see #COLOR_TYPE
   * @see #BOOLEAN_TYPE
   */
  public JDValueProgram(int type) {
    this.mode=MAP_BY_VALUE;
    this.type=type;
    tableMap=new Vector();
    switch(type) {
      case INTEGER_TYPE:
      defaultValue = new integerMapEntry(0,1,0);
      break;
      case BOOLEAN_TYPE:
      defaultValue = new booleanMapEntry(0,1,false);
      break;
      case COLOR_TYPE:
      defaultValue = new colorMapEntry(0,1,Color.GRAY);
      break;
    }
  }

  JDValueProgram copy() {

    // Check validity
    if(mode==MAP_BY_VALUE && getEntryNumber()==0)
      return null;

    JDValueProgram ret = new JDValueProgram(type);
    ret.mode = mode;
    for(int i=0;i<getEntryNumber();i++)
      ret.tableMap.add(((mapEntry)tableMap.get(i)).copy());
    ret.defaultValue=defaultValue.copy();
    return ret;
  }

  // ---------------------------------------------------------

  public int getType() {
    return type;
  }

  /** Sets the mode of this program.
   * @param m Mode to be set
   * @return true only if this mode if allowed for the data type.
   * @see #MAP_BY_VALUE
   * @see #MAP_LINEAR
   * @see #MAP_REMAP
   */
  public boolean setMode(int m) {
    if(type!=INTEGER_TYPE && (m==MAP_LINEAR || m==MAP_REMAP))
      return false;
    mode=m;
    return true;
  }

  public int getMode() {
    return mode;
  }

  // -Table manager------------------------------------

  /** Add a new entry to the corespondance table. */
  public void addNewEntry() {

    switch(type) {
      case INTEGER_TYPE:
        tableMap.add(new integerMapEntry(0,0,getIntegerMapping(defaultValue)));
        break;
      case BOOLEAN_TYPE:
        tableMap.add(new booleanMapEntry(0,0,getBooleanMapping(defaultValue)));
        break;
      case COLOR_TYPE:
        tableMap.add(new colorMapEntry(0,0,getColorMapping(defaultValue)));
        break;
    }

  }

  /** Remove the entry in the correspondance table at the specified index. */
  public void removeEntry(int idx) {
    tableMap.remove(idx);
  }

  /** Return number of entries in the correspondance table. */
  public int getEntryNumber() {
    return tableMap.size();
  }

  // - Default value------------------------------------

  /** Return a string representation of the default value, (correspondance table) */
  public String getDefaultMapping() {
    return getStrValue(defaultValue);
  }

  /** Sets the default value. */
  public boolean setDefaultMapping(String v) {

    switch(type) {
      case INTEGER_TYPE:
        return setIntegerMapping((integerMapEntry)defaultValue,v);
      case BOOLEAN_TYPE:
        return setBooleanMapping((booleanMapEntry)defaultValue,v);
      case COLOR_TYPE:
        return setColorMapping((colorMapEntry)defaultValue,v);
    }
    return false;

  }

  public Color getDefaultColorMapping() {
    return getColorMapping(defaultValue);
  }

  public boolean getDefaultBooleanMapping() {
    return getBooleanMapping(defaultValue);
  }

  public int getDefaultIntegerMapping() {
    return getIntegerMapping(defaultValue);
  }

  // - Value  ------------------------------------------

  public String getValue(int idx) {
    mapEntry mp = (mapEntry)tableMap.get(idx);
    if( mp.minValue==mp.maxValue )
      return Integer.toString(mp.minValue);
    else
      return Integer.toString(mp.minValue) + ".." + Integer.toString(mp.maxValue);
  }

  public String getCompleteValue(int idx) {
    mapEntry mp = (mapEntry)tableMap.get(idx);
    return Integer.toString(mp.minValue) + "," + Integer.toString(mp.maxValue);
  }

  public boolean setValueAt(int idx,String v) {

    mapEntry mp = (mapEntry) tableMap.get(idx);
    parsePos = 0;
    try {
      mp.minValue = parseNumber(v);

      if ((parsePos + 2 <= v.length()) && (v.substring(parsePos, parsePos + 2).equals(".."))) {
        // Range definition
        parsePos+=2;
        mp.maxValue = parseNumber(v);
      } else {
        if ((parsePos + 2 > v.length()))
          mp.maxValue = mp.minValue;
        else
          return false;
      }

      return (mp.minValue <= mp.maxValue);
    } catch (Exception e) {
      return false;
    }

  }

  // - Mapped value ------------------------------------

  public String getMapping(int idx) {
    return getStrValue((mapEntry)tableMap.get(idx));
  }

  public boolean setMappingAt(int idx,String v) {

    switch(type) {
      case INTEGER_TYPE:
        return setIntegerMapping((integerMapEntry)tableMap.get(idx),v);
      case BOOLEAN_TYPE:
        return setBooleanMapping((booleanMapEntry)tableMap.get(idx),v);
      case COLOR_TYPE:
        return setColorMapping((colorMapEntry)tableMap.get(idx),v);
    }
    return false;

  }

  public Color getColorMappingAt(int idx) {
    return getColorMapping((mapEntry)tableMap.get(idx));
  }

  public boolean getBooleanMappingAt(int idx) {
    return getBooleanMapping((mapEntry)tableMap.get(idx));
  }

  public int getIntegerMappingAt(int idx) {
    return getIntegerMapping((mapEntry)tableMap.get(idx));
  }

  boolean getBooleanMappingFor(JDObject p) {
    booleanMapEntry m = (booleanMapEntry)findEntry(p.getValue());
    if(m==null) return ((booleanMapEntry)defaultValue).value;
    else        return  m.value;
  }

  Color getColorMappingFor(JDObject p) {
    colorMapEntry m = (colorMapEntry)findEntry(p.getValue());
    if(m==null) return ((colorMapEntry)defaultValue).color;
    else        return  m.color;
  }

  int getIntegerMappingFor(JDObject p,JDObject master) {

    double    ratio;
    Rectangle r;

    switch( mode ) {

      case MAP_BY_VALUE:

        integerMapEntry m = (integerMapEntry) findEntry(p.getValue());
        if (m == null)
          return ((integerMapEntry) defaultValue).value;
        else
          return m.value;

      case MAP_LINEAR:

        ratio = (double)(p.getValue()-p.getMinValue())/(double)(p.getMaxValue()-p.getMinValue());
        return  defaultValue.minValue+(int)(ratio*(defaultValue.maxValue-defaultValue.minValue)+0.5);

      case MAP_REMAP:
        ratio = (double)(p.getValue()-p.getMinValue())/(double)(p.getMaxValue()-p.getMinValue());
        r = master.getBoundRect();
        // We start from the middle of the object in MAP_REMAP mode
        switch(master.getValueChangeMode()) {
          case JDObject.VALUE_CHANGE_ON_XDRAG_LEFT:
            return  (int)((double)r.width*ratio)-r.width/2;
          case JDObject.VALUE_CHANGE_ON_XDRAG_RIGHT:
            return -(int)((double)r.width*ratio)+r.width/2;
          case JDObject.VALUE_CHANGE_ON_YDRAG_TOP:
            return  (int)((double)r.height*ratio)-r.height/2;
          case JDObject.VALUE_CHANGE_ON_YDRAG_BOTTOM:
            return -(int)((double)r.height*ratio)+r.height/2;
        }
        break;

    }

    return 0;

  }

  // - Linear mapping mode --------------------------------

  public int getMinLinearMapping() {
    return defaultValue.minValue;
  }

  public int getMaxLinearMapping() {
    return defaultValue.maxValue;
  }

  public void setMinLinearValue(int min) {
    defaultValue.minValue = min;
  }

  public void setMaxLinearValue(int max) {
    defaultValue.maxValue = max;
  }

  // -----------------------------------------------------------
  // File management
  // -----------------------------------------------------------
  public void saveObject(FileWriter f, String decal) throws IOException {


    String to_write;
    int i;

    to_write = decal + "mapping_type:"    + type + "\n";
    f.write(to_write);
    to_write = decal + "mode:"    + mode + "\n";
    f.write(to_write);
    to_write = decal + "default:" + getDefaultMapping() + "\n";
    f.write(to_write);
    switch( mode ) {
      case MAP_BY_VALUE:
        for(i=0;i<getEntryNumber();i++) {
          to_write = decal + "map:" + getCompleteValue(i) + "," + getMapping(i) + "\n";
          f.write(to_write);
        }
        break;
      case MAP_LINEAR:
        to_write = decal + "lmin:" + getMinLinearMapping() + "\n";
        f.write(to_write);
        to_write = decal + "lmax:" + getMaxLinearMapping() + "\n";
        f.write(to_write);
        break;
    }

  }

  public JDValueProgram(JDFileLoader f) throws IOException {

    int min,max,i;
    Color c;
    boolean b;
    int sl=f.getCurrentLine();
    type=-1;
    mode=MAP_BY_VALUE;
    tableMap=new Vector();
    defaultValue=null;
    f.startBlock();

    while (!f.isEndBlock()) {

      String propName = f.parseProperyName();

      if( propName.equals("mapping_type") ) {
        type=(int) f.parseDouble();
      } else if ( propName.equals("mode") ) {
        mode=(int) f.parseDouble();
      } else if ( propName.equals("lmin") ) {

        if(defaultValue!=null)
          defaultValue.minValue =(int) f.parseDouble();
        else
          throw new IOException("default must be specified before lmin line " + f.getCurrentLine());

      }  else if ( propName.equals("lmax") ) {

        if(defaultValue!=null)
          defaultValue.maxValue =(int) f.parseDouble();
        else
          throw new IOException("default must be specified before lmax at line " + f.getCurrentLine());

      } else if ( propName.equals("default")) {

        switch(type) {
          case INTEGER_TYPE:
            i=(int) f.parseDouble();
            defaultValue = new integerMapEntry(0,1,i);
            break;
          case BOOLEAN_TYPE:
            b = f.parseBoolean();
            defaultValue = new booleanMapEntry(0,1,b);
            break;
          case COLOR_TYPE:
            c = f.parseColor();
            defaultValue = new colorMapEntry(0,1,c);
            break;
        }

      } else if ( propName.equals("map")) {

        min=(int) f.parseDouble();
        f.jumpLexem(JDFileLoader.COMA);
        max=(int) f.parseDouble();
        f.jumpLexem(JDFileLoader.COMA);
        switch(type) {
          case INTEGER_TYPE:
            i=(int) f.parseDouble();
            tableMap.add(new integerMapEntry(min,max,i));
            break;
          case BOOLEAN_TYPE:
            b = f.parseBoolean();
            tableMap.add(new booleanMapEntry(min,max,b));
            break;
          case COLOR_TYPE:
            c = f.parseColor();
            tableMap.add(new colorMapEntry(min,max,c));
            break;
          default:
            throw new IOException("No mapping_type specified for the ValueMapper at line " + sl);
        }

      } else {

        System.out.println("Unknown property found:" + propName);
        f.jumpPropertyValue();

      }

    }

    f.endBlock();

    if( defaultValue==null )
      throw new IOException("No default specified for the ValueMapper at line " + sl);
    if( type==-1 )
      throw new IOException("No mapping_type specified for the ValueMapper at line " + sl);
    if( mode==MAP_BY_VALUE && getEntryNumber()==0 )
      throw new IOException("No mapping table found for the ValueMapper at line " + sl);

  }


  // --------------------------------------------------
  private boolean isNumber(char c) {
    return (c>='0' && c<='9') || (c=='-');
  }

  private String getStrValue(mapEntry mp) {

    if(mp instanceof colorMapEntry) {
      Color c=((colorMapEntry)mp).color;
      return c.getRed() + "," + c.getGreen() + "," + c.getBlue();
    } else if (mp instanceof integerMapEntry) {
      return Integer.toString(((integerMapEntry)mp).value);
    } else if (mp instanceof booleanMapEntry) {
      return Boolean.toString(((booleanMapEntry)mp).value);
    } else {
      return "Invalid mapping";
    }

  }

  private Color getColorMapping(mapEntry mp) {
    return ((colorMapEntry)mp).color;
  }

  private int getIntegerMapping(mapEntry mp) {
    return ((integerMapEntry)mp).value;
  }

  private boolean getBooleanMapping(mapEntry mp) {
    return ((booleanMapEntry)mp).value;
  }

  private boolean setColorMapping(colorMapEntry mp,String c) {

    int r,g,b;
    parsePos=0;
    try {
      r = parseNumber(c);
      if(c.charAt(parsePos)!=',') return false;
      parsePos++;
      g = parseNumber(c);
      if(c.charAt(parsePos)!=',') return false;
      parsePos++;
      b = parseNumber(c);
      mp.color = new Color(r,g,b);
      return true;
    } catch (Exception e) {
      return false;
    }

  }

  private boolean setBooleanMapping(booleanMapEntry mp,String c) {
    mp.value=Boolean.valueOf(c).booleanValue();
    return true;
  }

  private boolean setIntegerMapping(integerMapEntry mp,String c) {
    parsePos=0;
    try {
      mp.value = parseNumber(c);
      return true;
    } catch (Exception e) {
      return false;
    }
  }

  private int parseNumber(String v) {

    StringBuffer num=new StringBuffer();
    int l = v.length();
    boolean ok=true;
    while( parsePos<l && ok) {
      ok = isNumber(v.charAt(parsePos));
      if(ok) {
        num.append(v.charAt(parsePos));
        parsePos++;
      }
    }

   return Integer.parseInt(num.toString());

  }

  private mapEntry findEntry(int value) {
    boolean found=false;
    int i=0;
    mapEntry m=null;
    while(!found && i<tableMap.size()) {
      m = (mapEntry)tableMap.get(i);
      found = value>=m.minValue && value<=m.maxValue;
      if(!found) i++;
    }
    if(found) return m;
    else      return null;
  }


}
