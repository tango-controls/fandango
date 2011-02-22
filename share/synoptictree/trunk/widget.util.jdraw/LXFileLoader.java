package fr.esrf.tangoatk.widget.util.jdraw;

import java.io.FileReader;
import java.io.IOException;
import java.awt.*;
import java.util.Vector;
import java.util.StringTokenizer;

class Dynamics {

String dynClassName;
int    dynValueFlag;
int    dynSensitive;
int    dynMinColor;
int    dynMaxColor;
int    dynNumColors;
int    dynColorIndicator;
int    dynUseThreshold;
String dynTextFormat;
double dynMinimum;
double dynMaximum;
double dynUserMinimum;
double dynUserMaximum;
double dynValue;
double dynThreshold;

}

/** A class to load JLX file (jloox) */
class LXFileLoader {

  private int CrtLine;
  private int StartLine;
  char CurrentChar;
  String version;

  private String word;
  FileReader f;

  // ****************************************************
  public LXFileLoader(FileReader fr) {
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

  // ****************************************************
  String read_safe_full_word() throws IOException {
    word = read_word(true);
    if(word==null)
      throw new IOException("Unexpected end of file " + CrtLine);
    return word;
  }

  // ****************************************************
  String read_line() throws IOException {

    StringBuffer ret_word = new StringBuffer();
    while (CurrentChar != '\n' && CurrentChar!=0) {
      if(CurrentChar!=0) ret_word.append(CurrentChar);
      read_char();
    }

    if(ret_word.length()==0)
      throw new IOException("Unexpected end of file " + CrtLine);
    else
      return ret_word.toString();

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

    try {
      i = Integer.parseInt(s);
    } catch (NumberFormatException e) {
      throw new IOException("Bad integer format at line " + CrtLine + "\n" + e.getMessage());
    }

    return i;

  }

  // ****************************************************
  int read_int_16() throws IOException {

    int i;
    String s = read_safe_word();

    try {
      i = (int)Long.parseLong(s,16);
    } catch (NumberFormatException e) {
      throw new IOException("Bad integer format at line " + CrtLine + "\n" + e.getMessage());
    }

    return i;

  }

  // ****************************************************
  double read_double() throws IOException {

    double d;
    String s = read_safe_word();

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

    String s10 = s.substring(0, 2);
    String s12 = s.substring(2, 4);
    String s14 = s.substring(4, 6);
    if(s10.equals("-1"))
        s10 = "FF";
    if(s12.equals("-1"))
        s12 = "FF";
    if(s14.equals("-1"))
        s14 = "FF";

    try {
      return new Color(Integer.parseInt(s10, 16), Integer.parseInt(s12, 16), Integer.parseInt(s14, 16));
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

  // ****************************************************
  Font read_font() throws IOException {

      jump_space();
      String s = read_line();

      // Parse an X11 font name
      StringTokenizer stringtokenizer = new StringTokenizer(s, "-");
      if(stringtokenizer.countTokens() < 7)
          return new Font(s, 0, 10);

      stringtokenizer.nextToken();
      String s1 = stringtokenizer.nextToken();
      String s2 = stringtokenizer.nextToken();
      String s3 = stringtokenizer.nextToken();
      stringtokenizer.nextToken();
      stringtokenizer.nextToken();
      String s4 = stringtokenizer.nextToken();
      int size = 0;
      int style = 0;
      if(s2.equals("bold"))
          style |= Font.BOLD;
      if(s3.equals("i"))
          style |= Font.ITALIC;
      try
      {
          size = Integer.parseInt(s4);
      }
      catch(NumberFormatException numberformatexception)
      {
          size = 12;
      }

      return new Font(s1, style, size);
  }

  // ****************************************************
  void jump_dynamics() throws IOException {

    jump_space();
    if(CurrentChar=='d') {
      word = read_safe_word();  // dynamics
      while(!word.equals("end"))
        word = read_safe_word();
      read_safe_word();         // end dynamics
    }

  }

  // ******************************************************
  Dynamics read_dynamics() throws IOException {

    jump_space();
    if(CurrentChar=='d') {

      Dynamics dyna = new Dynamics();
      read_safe_word(); // 'dynamics'

      while (true) {

        String extName = read_safe_word();
        if (extName.equals("_dynClassName")) {
          dyna.dynClassName = read_safe_word();
        } else if (extName.equals("_dynValueFlag")) {
          dyna.dynValueFlag = read_int();
        } else if (extName.equals("_dynSensitive")) {
          dyna.dynSensitive = read_int();
        } else if (extName.equals("_dynMinColor")) {
          dyna.dynMinColor = read_int();
        } else if (extName.equals("_dynMaxColor")) {
          dyna.dynMaxColor = read_int();
        } else if (extName.equals("_dynNumColors")) {
          dyna.dynNumColors = read_int();
        } else if (extName.equals("_dynColorIndicator")) {
          dyna.dynColorIndicator = read_int();
        } else if (extName.equals("_dynUseThreshold")) {
          dyna.dynUseThreshold = read_int();
        } else if (extName.equals("_dynTextFormat")) {
          jump_space();
          dyna.dynTextFormat = read_line();
        } else if (extName.equals("_dynMinimum")) {
          dyna.dynMinimum = read_double();
        } else if (extName.equals("_dynMaximum")) {
          dyna.dynMaximum = read_double();
        } else if (extName.equals("_dynUserMinimum")) {
          dyna.dynUserMinimum = read_double();
        } else if (extName.equals("_dynUserMaximum")) {
          dyna.dynUserMaximum = read_double();
        } else if (extName.equals("_dynValue")) {
          dyna.dynValue = read_double();
        } else if (extName.equals("_dynThreshold")) {
          dyna.dynThreshold = read_double();
        } else if (extName.equals("end")) {
          read_safe_word(); // 'dynamics'
          return dyna;
        } else {
          throw new IOException("Invalid loox dynamics keyword :" + extName);
        }

      }
    }

    return null;
  }

  // ****************************************************
  JDObject parseLxRectangle(LXObject lxObj) throws IOException {

    jump_dynamics();
    double x      = read_double();
    double y      = read_double();
    double w      = read_double();
    double h      = read_double();
    lxObj.setBounds(x,y,w,h);
    if(CurrentChar!='\n') {
      lxObj.shadowWidth = read_int();
      lxObj.invertShadow = (read_int()!=0);
    }
    return new JDRectangle(lxObj);

  }

  // ****************************************************
  JDObject parseLxLine(LXObject lxObj) throws IOException {

    jump_dynamics();
    int nb = read_int(); // Number of point (Should be 2)

    if(nb!=2)
      throw new IOException("Only 2 point are allowed for line object, line " + CrtLine + "\n");

    double x1 = read_double();
    double y1 = read_double();
    double x2 = read_double();
    double y2 = read_double();
    lxObj.setBounds(x1,y1,x2,y2);
    return new JDLine(lxObj,
                      x1+lxObj.px,y1+lxObj.py,
                      x2+lxObj.px,y2+lxObj.py,
                      lxObj.lineArrow);

  }

  // ****************************************************
  JDObject parseLxPolyline(LXObject lxObj) throws IOException {

    jump_dynamics();
    boolean isSpline = (read_int()==1);
    boolean closed = (read_int()==1);
    read_int(); // ???

    lxObj.shadowWidth = read_int();
    lxObj.invertShadow = (read_int()!=0);
    read_int(); // ???
    read_int(); // ???
    read_int(); // ???

    int nb = read_int(); // Number of point

    if(isSpline) {

      // Jump first duplicated point
      read_double();
      read_double();
      double[] x = new double[nb-1];
      double[] y = new double[nb-1];
      for(int i=0;i<nb-1;i++) {
        x[i] = read_double() + lxObj.px;
        y[i] = read_double() + lxObj.py;
      }
      return new JDSpline(lxObj,x,y,closed);

    } else {

      double[] x = new double[nb];
      double[] y = new double[nb];
      for(int i=0;i<nb;i++) {
        x[i] = read_double() + lxObj.px;
        y[i] = read_double() + lxObj.py;
      }
      return new JDPolyline(lxObj,x,y,closed);

    }

  }

  // ****************************************************
  JDObject parseLxEllipse(LXObject lxObj) throws IOException {

    jump_dynamics();
    double x = read_double();
    double y = read_double();
    double w = read_double();
    double h = read_double();
    lxObj.setBounds(x,y,w,h);
    int a  = read_int()/64;
    int b  = read_int()/64;
    return new JDEllipse(lxObj,360-(a+b),b,lxObj.arcMode);

  }

  // ****************************************************
  JDObject parseLxText(LXObject lxObj) throws IOException {

    jump_dynamics();
    lxObj.px += read_double();  // X location
    lxObj.py += read_double();  // Y location
    lxObj.fillStyle = 0;
    read_int();     // ???
    read_char();    // Read the '\n'
    read_char();    // Read the '\t'

    String s = read_line();
    s = s.replace('\001', '\n');
    return new JDLabel(lxObj,s);

  }

  // ****************************************************
  JDObject parseLxPara(LXObject lxObj) throws IOException {

    jump_dynamics();
    read_int();  // ???
    lxObj.shadowWidth = read_int();
    lxObj.invertShadow = (read_int()!=0);
    read_int();  // ???
    read_int();  // ???

    int nb = 4;
    double[] x = new double[nb];
    double[] y = new double[nb];
    for (int i = 0; i < nb; i++) {
      x[i] = read_double() + lxObj.px;
      y[i] = read_double() + lxObj.py;
    }
    return new JDPolyline(lxObj, x, y, true);

  }

  // ****************************************************
  JDObject parseLxImage(LXObject lxObj) throws IOException {

    jump_dynamics();
    read_int();  // ???
    double x = read_double(); // Location X
    double y = read_double(); // Location Y
    double w = read_double(); // Size X
    double h = read_double(); // Size Y
    String fileName = read_safe_word();
    lxObj.setBounds(x,y,w,h);
    return new JDImage(lxObj,fileName);

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
  JDObject parseLxGroup(LXObject lxObj) throws IOException {

    Dynamics dyn = read_dynamics();

    double x      = read_double();
    double y      = read_double();
    double w      = read_double();
    double h      = read_double();
    lxObj.setBounds(x,y,w,h);

    JDObject obj;
    Vector objects = new Vector();

    while((obj = parseObject(true))!=null) {
      objects.add(obj);
      obj.translate(lxObj.px,lxObj.py);
    }

    JDObject ret = new JDGroup(lxObj,objects);

    if (dyn != null) {

      if (dyn.dynClassName.equals("multipleStatesClass")) {

        int min = (int) dyn.dynMinimum;
        int max = (int) dyn.dynMaximum;

        // Set up visibilty mappers
        for (int i = min; i <= max; i++) {

          String oname = Integer.toString(i);

          Vector subO = findObjects(oname, objects);
          if (subO.size() == 0) {

            System.out.println("LXFileLoader.parseLxGroup() : Warning, sub-object '" + oname + "' not found in " + lxObj.name);

          } else {

            JDValueProgram vp = new JDValueProgram(JDValueProgram.BOOLEAN_TYPE);
            vp.addNewEntry();
            vp.setDefaultMapping("false");
            vp.setMappingAt(0, "true");
            vp.setValueAt(0, oname);

            for (int j = 0; j < subO.size(); j++)
              ((JDObject) subO.get(j)).setVisibilityMapper(vp.copy());

          }

        }

        ret.setMinValue(min);
        ret.setMaxValue(max);
        ret.setInitValue((int) dyn.dynValue);
        ret.setInteractive(dyn.dynSensitive == 1);
        ret.setValueChangeMode(JDObject.VALUE_INC_ON_CLICK);
      } else {
        System.out.println("LXFileLoader.parseLxGroup() : Warning, " + dyn.dynClassName + " not suported.");
      }
    }

    return ret;

  }

  JDObject parseLxEndGroup(LXObject lxObj) throws IOException {

    jump_dynamics();
    // Jump 0 0 0 0
    read_double();
    read_double();
    read_double();
    read_double();
    return null;

  }

  // ****************************************************
  JDObject parseObject(boolean inGroup) throws IOException {

    // Check end of file
    jump_space();
    if(CurrentChar==0)
      return null;

    // Parse object header
    LXObject lxObj = new LXObject();
    lxObj.parse(this,inGroup);

    // Parse object
    switch(lxObj.type) {
      case 0:
        return parseLxPolyline(lxObj);
      case 1:
        return parseLxText(lxObj);
      case 2:
        return parseLxEndGroup(lxObj);
      case 3:
        return parseLxGroup(lxObj);
      case 4:
        return parseLxRectangle(lxObj);
      case 5:
        return parseLxEllipse(lxObj);
      case 6:
        return parseLxLine(lxObj);
      case 11:
        return parseLxImage(lxObj);
      case 13:
        return parseLxPara(lxObj);
      default:
        throw new IOException("Object type " + lxObj.type + "not supported");
    }

  }

  // ****************************************************
  Vector parseFile() throws IOException {

    Vector objects = new Vector();

    /* CHECK BEGINING OF FILE  */
    word = read_word(false);
    if (word == null) throw new IOException("File empty !");
    if (!word.equalsIgnoreCase("L3.3")) throw new IOException("Invalid header , Loox V3.3 file or higher required!");

    // Jump default loox attribute
    word = read_safe_word();
    for(boolean end=false;!end;) {
      end = word.equals("gend");
      if(!end) word = read_safe_word();
    }

    // Read objects
    JDObject o;
    while((o=parseObject(false))!=null)
      objects.add(o);

    // Build object array
    return objects;

  }

  public static void main(String[] args) {

    try {
      FileReader fr = new FileReader(args[0]);
      LXFileLoader f = new LXFileLoader(fr);
      f.parseFile();
      fr.close();
    } catch (IOException e) {
      System.out.println("Reading of "+args[0]+" failed " + e.getMessage());
      e.printStackTrace();
    }
    System.exit(0);

  }

}