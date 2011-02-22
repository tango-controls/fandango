package fr.esrf.tangoatk.widget.util.jdraw;

import java.io.FileReader;
import java.io.IOException;
import java.awt.*;
import java.util.Vector;

/** A class to load JLX file (jloox) */
class JLXFileLoader {

  private int CrtLine;
  private int StartLine;
  private char CurrentChar;
  String version;

  private String word;
  FileReader f;

  final static int[] ToJDTextAlign = {
    JDLabel.LEFT_ALIGNMENT,
    JDLabel.CENTER_ALIGNMENT,
    JDLabel.RIGHT_ALIGNMENT
  };

  static String extNames[] = {"className","classParam"};

  // ****************************************************
  public JLXFileLoader(FileReader fr) {
    f = fr;
    CrtLine = 1;
    CurrentChar = ' ';
  }

  // ****************************************************
  private void read_char() throws IOException {

    if (f.ready())
      CurrentChar = (char) f.read();
    else
      CurrentChar = 0;
    if (CurrentChar == '\n') CrtLine++;
  }

  // ****************************************************
  String read_safe_word() throws IOException {
    word = read_word(false);
    if(word==null)
      throw new IOException("Unexpected end of file " + CrtLine);
    return word;
  }

  String read_safe_full_word() throws IOException {
    word = read_word(true);
    if(word==null)
      throw new IOException("Unexpected end of file " + CrtLine);
    return word;
  }

  // ****************************************************
  void jump_space() throws IOException {

    while (CurrentChar <= 32 && CurrentChar > 0) read_char();
  }

  // ****************************************************
  String read_word(boolean ignoreColon) throws IOException {

    StringBuffer ret_word = new StringBuffer();

    /* Jump space */
    jump_space();

    StartLine = CrtLine;

    /* Treat special character */
    if (!ignoreColon) {
      if (CurrentChar == ';') {
        ret_word.append(CurrentChar);
        read_char();
        return ret_word.toString();
      }
    }

    /* Treat string */
    if (CurrentChar == '"') {
      ret_word.append(CurrentChar);
      read_char();
      while (CurrentChar != '"' && CurrentChar != 0) {
        ret_word.append(CurrentChar);
        read_char();
      }
      if (CurrentChar == 0 || CurrentChar == '\n') {
        IOException e = new IOException("String too long at line " + StartLine);
        throw e;
      }
      ret_word.append(CurrentChar);
      read_char();
      return ret_word.toString();
    }

    /* Treat other word */
    if (ignoreColon) {
      while (CurrentChar > 32 && CurrentChar != '\n') {
        ret_word.append(CurrentChar);
        read_char();
      }
    } else {
      while (CurrentChar > 32 && CurrentChar != '\n' && CurrentChar != ';') {
        ret_word.append(CurrentChar);
        read_char();
      }
    }


    if (ret_word.length() == 0) {
      return null;
    }

    return ret_word.toString();
  }

  // ****************************************************
  public int getCurrentLine() {
    return StartLine;
  }

  // ****************************************************
  int read_int() throws IOException {

    int i;
    String s = read_safe_word();

    if(s.equals("!") || s.equals("$"))
      return 0;

    try {
      i = Integer.parseInt(s);
    } catch (NumberFormatException e) {
      throw new IOException("Bad integer format at line " + CrtLine + "\n" + e.getMessage());
    }

    return i;

  }

  // ****************************************************
  double read_double() throws IOException {

    double d;
    String s = read_safe_word();

    if(s.equals("!") || s.equals("$"))
      return 0.0;

    try {
      d = Double.parseDouble(s);
    } catch (NumberFormatException e) {
      throw new IOException("Bad double format at line " + CrtLine + "\n" + e.getMessage());
    }

    return d;

  }

  // ****************************************************
  Color read_color() throws IOException {

    String s = read_safe_word();

    if (s.equals("!") || s.equals("$"))
      return null;

    try {
      int i = (int) Long.parseLong(s, 16);
      int a = i >>> 24;
      int r = (i & 0xFF0000) >>> 16;
      int g = (i & 0x00FF00) >>> 8;
      int b = (i & 0x0000FF);
      return new Color(r, g, b, a);
    } catch (NumberFormatException e) {
      throw new IOException("Bad color format at line " + CrtLine + "\n" + e.getMessage());
    }

  }

  // ****************************************************
  void jump_colon() throws IOException {

    String s = read_safe_word();
    if( !s.equals(";") )
      throw new IOException("';' expected at line " + CrtLine + "\n");

  }

  double[] parseDouleArray() throws IOException {

    double[] ret;
    String s = read_safe_full_word();
    if(s.equals("!") || s.equals("$")) {
      ret = new double[2];
      ret[0]=ret[1]=0.0;
      return ret;
    }

    String[] a = s.split(";");
    ret = new double[a.length];
    try {
      for (int i = 0; i < ret.length; i++)
        ret[i] = Double.parseDouble(a[i]);
    } catch (NumberFormatException e) {
      throw new IOException("Number expected at line " + getCurrentLine() + "\n" + e.getMessage());
    }

    return ret;

  }

  // ****************************************************
  private String extractQuote(String s) {
    if(s.charAt(0)=='\"')
      return s.substring(1,s.length()-1);
    else
      return s;
  }

  // ****************************************************
  String read_string() throws IOException {
    String s = read_safe_word();
    return extractQuote(s);
  }

  // ****************************************************
  JDObject parseLxRectangle(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Rectangle");
    r.parse(this,false);
    r.correct(x,y);
    int arcW = (int)read_double(); // Arc width
    read_double(); // Arc height
    int type = read_int();
    if(type==0)
      return new JDRectangle(r);
    else
      return new JDRoundRectangle(r,arcW);

  }

  // ****************************************************
  JDObject parseLxCircle(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Ellipse");
    r.parse(this,false);
    r.correct(x,y);
    int a = (int)read_double(); // Angle start
    int b = (int)read_double(); // Angle extent
    int atype = read_int();     // Chord closed
    return new JDEllipse(r,360-(a+b),b,atype);

  }

  // ****************************************************
  JDObject parseLxLine(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Line");
    r.parse(this,false);
    r.correct(x,y);
    JLXPath p = new JLXPath();
    p.parse(this,false,true);
    return new JDLine(r,p);

  }

  // ****************************************************
  JDObject parseLxParallelogram(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Polyline");
    r.parse(this,false);
    r.correct(x,y);
    JLXPath p = new JLXPath();
    p.parse(this,true,false);
    read_int(); // Rotation lock
    read_int(); // Angle lock
    return new JDPolyline(r,p);

  }

  // ****************************************************
  JDObject parseLxPolyline(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Polyline");
    r.parse(this,false);
    r.correct(x,y);
    JLXPath p = new JLXPath();
    p.parse(this,true,true);
    return new JDPolyline(r,p);

  }

  // ****************************************************
  JDObject parseLxText(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Text");
    r.parse(this,false);
    r.correct(x,y);
    read_int();    // Shew enabled
    read_double(); // Rotation angle
    String fname = read_string();
    int fstyle = read_int();
    int fsize = read_int();
    String txt = read_string();
    r.style.fillStyle = JDObject.FILL_STYLE_NONE;
    r.style.lineWidth = 0;
    return new JDLabel(r,new Font(fname,fstyle,fsize),txt,JDLabel.CENTER_ALIGNMENT,true);

  }

  // ****************************************************
  JDObject parseLxTextArea(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Text");
    r.parse(this,false);
    r.correct(x,y);
    JLXPath p = new JLXPath();
    p.parse(this,true,false);
    read_int();    // Shew enabled
    read_double(); // Rotation angle
    String fname = read_string();
    int fstyle = read_int();
    int fsize = read_int();
    String txt = read_string();
    read_int();    // Boder width
    read_int();    // Border height
    read_int();    // Offset X
    read_int();    // Offset Y
    int align = read_int(); // Alignement
    Color txtColor = read_color();
    if( txtColor==null )
      r.style.lineColor = Color.BLACK;
    else
      r.style.lineColor = txtColor;
    read_double(); // Angle

    return new JDLabel(r,new Font(fname,fstyle,fsize),txt,ToJDTextAlign[align],false);

  }

  // ****************************************************
  JDObject parseLxGeneralPath(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Polyline");
    r.parse(this,false);
    r.correct(x,y);
    JLXPath p = new JLXPath();
    p.parse(this,true,false);
    switch(p.pathType) {
      case 0:
      case 1: // Polyline path
        return new JDPolyline(r,p);
      case 2:
      case 3: // Spline path
        return new JDSpline(r,p);
      default:
        throw new IOException("Bad path format at line " + CrtLine);
    }

  }

  // ****************************************************
  JDObject parseLxImage(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Image");
    r.parse(this,false);
    r.correct(x,y);
    read_int(); // Skew enable
    if( version.compareTo("0.3.0") >= 0 ) {
      read_int(); // H Flip
      read_int(); // V Flip
    }
    read_double(); // Rotation
    if( version.compareTo("1.0.1") >= 0) {
      read_int(); // Animation flag
    }
    String iname = read_string();
    return new JDImage(r,iname);

  }

  // ****************************************************
  JDObject parseLxGroup(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Group");
    r.parse(this,true);
    r.correct(x,y);
    Vector objects = new Vector();

    int nbObject = read_int();
    for(int i=0;i<nbObject;i++) {
      JDObject o = parseObject(r.boundRect.getX(),r.boundRect.getY());
      if(o!=null) objects.add(o);
    }

    return new JDGroup(r,objects);

  }

  // ****************************************************
  JDObject parseLxPushButton(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Button");
    r.parse(this,true);
    r.correct(x,y);
    Vector objects = new Vector();

    int nbObject = read_int();
    for(int i=0;i<nbObject;i++) {
      JDObject o = parseObject(r.boundRect.getX(),r.boundRect.getY());
      if(o!=null) objects.add(o);
    }

    JDObject ret = new JDGroup(r,objects);

    // Set up the invertShadow mapper
    JDValueProgram vp = new JDValueProgram(JDValueProgram.BOOLEAN_TYPE);
    vp.addNewEntry();
    vp.setDefaultMapping("false");
    vp.setMappingAt(0,"true");
    vp.setValueAt(0,"1");
    ret.setInvertShadowMapper(vp);
    ret.setMinValue(0);
    ret.setMaxValue(1);
    ret.setInitValue(0);
    ret.setValueChangeMode(JDObject.VALUE_INC_ON_PRESSRELEASE);
    boolean interactive=false;
    if(version.compareTo("1.3.0") >= 0)
      interactive = (read_int()==1);
    ret.setInteractive(interactive);

    return ret;

  }

  // ****************************************************
  private Vector findObjects(String name,Vector objs) {
    int nb = objs.size();
    boolean found;
    Vector ret = new Vector();
    for(int i=0;i<nb;i++) {
      JDObject obj = (JDObject)objs.get(i);
      if(obj instanceof JDGroup) {
        if(obj.name.equals(name)) {
          ret.add(obj);
        } else {
          Vector objs2 = ((JDGroup)obj).getChildren();
          Vector ret2 = findObjects(name,objs2);
          ret.addAll(ret2);
        }
      } else {
        found = obj.name.equals(name);
        if(found) ret.add(objs.get(i));
      }
    }
    return ret;
  }

  // ****************************************************
  JDObject parseLxMultiState(double x,double y) throws IOException {

    JLXObject r = new JLXObject("MultiState");
    r.parse(this,true);
    r.correct(x,y);
    Vector objects = new Vector();

    int nbObject = read_int();
    int i;

    for(i=0;i<nbObject;i++) {
      JDObject o = parseObject(r.boundRect.getX(),r.boundRect.getY());
      if(o!=null) objects.add(o);
    }

    boolean interactive=false;
    if(version.compareTo("1.3.0") >= 0)
      interactive = (read_int()==1);

    int min  = read_int(); // Min  value
    int max  = read_int(); // Max  value
    int v0   = read_int(); // Init value

    // Set up visibilty mappers
    for(i=min;i<=max;i++) {

      String oname = Integer.toString(i);

      Vector subO = findObjects(oname,objects);
      if(subO.size()==0) {

        System.out.println("JLXFileLoader.parseLxMultiState() : Warning, sub-object '" + oname + "' not found in " + r.name);

      } else {

        JDValueProgram vp = new JDValueProgram(JDValueProgram.BOOLEAN_TYPE);
        vp.addNewEntry();
        vp.setDefaultMapping("false");
        vp.setMappingAt(0,"true");
        vp.setValueAt(0,oname);

        for(int j=0;j<subO.size();j++)
          ((JDObject)subO.get(j)).setVisibilityMapper(vp.copy());

      }

    }

    JDObject ret = new JDGroup(r,objects);
    ret.setMinValue(min);
    ret.setMaxValue(max);
    ret.setInitValue(v0);
    ret.setInteractive(interactive);
    ret.setValueChangeMode(JDObject.VALUE_INC_ON_CLICK);

    return ret;

  }

  // ****************************************************
  JDObject parseLxToggle(double x,double y) throws IOException {

    JLXObject r = new JLXObject("Toggle");
    r.parse(this,true);
    r.correct(x,y);
    Vector objects = new Vector();

    int nbObject = read_int();
    int i;

    for(i=0;i<nbObject;i++) {
      JDObject o = parseObject(r.boundRect.getX(),r.boundRect.getY());
      if(o!=null) objects.add(o);
    }

    boolean interactive=false;
    if(version.compareTo("1.3.0") >= 0)
      interactive = (read_int()==1);

    int v0   = read_int(); // Init value

    // Set up visibilty mappers

    Vector subO = findObjects("OFF",objects);
    Vector sub1 = findObjects("ON",objects);
    if(subO.size()==0)
        throw new IOException("Toggle sub-object '" + "OFF" + "' not found in " + r.name);
    if(sub1.size()==0)
        throw new IOException("Toggle sub-object '" + "ON" + "' not found in " + r.name);

    JDValueProgram vp = new JDValueProgram(JDValueProgram.BOOLEAN_TYPE);
    vp.addNewEntry();
    vp.setDefaultMapping("false");
    vp.setMappingAt(0,"true");
    vp.setValueAt(0,"1");
    for(int j=0;j<subO.size();j++)
      ((JDObject)subO.get(j)).setVisibilityMapper(vp);

    JDValueProgram vp2 = new JDValueProgram(JDValueProgram.BOOLEAN_TYPE);
    vp2.addNewEntry();
    vp2.setDefaultMapping("true");
    vp2.setMappingAt(0,"false");
    vp2.setValueAt(0,"1");
    for(int j=0;j<sub1.size();j++)
      ((JDObject)sub1.get(j)).setVisibilityMapper(vp2);

    JDObject ret = new JDGroup(r,objects);
    ret.setMinValue(0);
    ret.setMaxValue(1);
    ret.setInitValue(v0);
    ret.setInteractive(interactive);
    ret.setValueChangeMode(JDObject.VALUE_INC_ON_CLICK);

    return ret;

  }

  // ****************************************************
  JDObject parseLxCustomShape(double x,double y) throws IOException {

    Vector objects = new Vector();

    JLXObject r = new JLXObject("Custom shape");
    r.parse(this,false);
    r.correct(x,y);

    if(version.compareTo("1.1.0") >= 0) {
      read_int();    // Inverted flag
      read_double(); // Shadow thichness
    }

    int nbPath = read_int();
    JLXPath p = new JLXPath();

    for (int i = 0; i < nbPath; i++) {
      int pathType = read_int();
      if( pathType==991 )
        read_int(); // // Inverted shadow flag (for sub shadow shape, ignored)
      switch (pathType) {
        case 990: // Standart path
          p.parseCustom(this,r,objects);
          break;
        case 991: // Shadowed path (Ignore, already handled by JDPolyline)
          p.parseCustom(this,r,null);
          break;
        case 992: // Line path
          System.out.println("JLXFileLoader.parseLxCustomShape() Not supported custom shape type :" + pathType);
          p.parseCustom(this,r,null);
          break;
        default:
          System.out.println("Invalid custom shape type :" + pathType);
      }
    }

    if( objects.size()==1 )
      return (JDObject)objects.get(0);
    else
      return new JDGroup(r,objects);

  }

  // ****************************************************
  JDObject parseObject(double x,double y) throws IOException {

    String className = read_safe_word();

    if (className.equals("com.loox.jloox.LxRectangle")) {
      return parseLxRectangle(x,y);
    } else if (className.equals("com.loox.jloox.LxCircle")) {
      return parseLxCircle(x,y);
    } else if (className.equals("com.loox.jloox.LxLine")) {
      return parseLxLine(x,y);
    } else if (className.equals("com.loox.jloox.LxPolyline")) {
      return parseLxPolyline(x,y);
    } else if (className.equals("com.loox.jloox.LxParallelogram")) {
      return parseLxParallelogram(x,y);
    } else if (className.equals("com.loox.jloox.LxText")) {
      return parseLxText(x,y);
    } else if (className.equals("com.loox.jloox.LxTextArea")) {
      return parseLxTextArea(x,y);
    } else if (className.equals("com.loox.jloox.LxGeneralPath")) {
      return parseLxGeneralPath(x,y);
    } else if (className.equals("com.loox.jloox.LxImage")) {
      return parseLxImage(x,y);
    } else if (className.equals("com.loox.jloox.LxGroup")) {
      return parseLxGroup(x,y);
    } else if (className.equals("com.loox.jloox.LxPushButton")) {
      return parseLxPushButton(x,y);
    } else if (className.equals("com.loox.jloox.LxMultiState")) {
      return parseLxMultiState(x,y);
    } else if (className.equals("com.loox.jloox.LxCustomShape")) {
      return parseLxCustomShape(x,y);
    } else if (className.equals("com.loox.jloox.LxToggle")) {
      return parseLxToggle(x,y);
    } else {

      if(className.startsWith("com")) {

        System.out.println("JLXFileLoader.parseObject() Unknown class found:" + className + " at line " + StartLine);

        // Trigger to the next empty line
        char oChar=CurrentChar;
        read_char();
        while (oChar!='\n' || CurrentChar!='\n') {
          oChar=CurrentChar;
          read_char();
          if( CurrentChar==0 )
            throw new IOException("Unexpected end of file while trying to trigger to the next LxClass after : "+className);
        }

      }
      return null;

    }

  }

  // ****************************************************
  Vector parseFile() throws IOException {
    int i;
    Vector objects = new Vector();

    /* CHECK BEGINING OF FILE  */
    word = read_word(false);
    if (word == null) throw new IOException("File empty !");
    if (!word.equalsIgnoreCase("JLoox")) throw new IOException("Invalid header !");
    version = read_safe_word();

    if(version.compareTo("1.3.1")>=0)
      read_safe_word(); // Jump String encoding

    new JLXStyle().parse(this); // Default style1
    new JLXStyle().parse(this); // Default style2
    read_string();   // Default font name
    read_int();      // Default font style
    read_int();      // Default font sixe
    read_int();      // Default line arrow
    read_int();      // Default shawdow thickness
    read_safe_word();   // word[0] = Default Shadow Inversion
                        // word[1] = Default Arc Closure
                        // word[2] = Default DoubleClickActionActive

    int nbLayer = read_int();
    for(i = 0; i < nbLayer; i++)
    {
        read_string(); // Layer name
        read_int();    // Layer flag
    }

    int nbObject = read_int();

    for(i=0;i<nbObject;i++) {
      JDObject o = parseObject(0.0,0.0);
      if(o!=null) objects.add(o);
    }

    read_int(); // Jump the last 0

    word = read_word(false);
    if(word!=null) {
      if(word.equalsIgnoreCase("\"UserData\"")) {
        // Brwosing extensions
        for(i=0;i<nbObject;i++) {
          String ext = read_string();
          if(ext.equalsIgnoreCase("ud")) {
            read_int();
            ((JDObject)objects.get(i)).setExtensionList(extNames);
            ((JDObject)objects.get(i)).setExtendedParam(0,read_string());
            ((JDObject)objects.get(i)).setExtendedParam(1,read_string());
          }
        }
      }
    }

    // Build object array
    return objects;

  }

  public static void main(String[] args) {

    try {
      FileReader fr = new FileReader(args[0]);
      JLXFileLoader f = new JLXFileLoader(fr);
      f.parseFile();
      fr.close();
    } catch (IOException e) {
      System.out.println("Reading of "+args[0]+" failed " + e.getMessage());
    }
    System.exit(0);

  }

}
