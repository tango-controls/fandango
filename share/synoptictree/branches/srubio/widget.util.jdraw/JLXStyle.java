package fr.esrf.tangoatk.widget.util.jdraw;

import java.awt.*;
import java.io.IOException;

class JLXStyle {

  static int ToJDLineStyle[] = {
    JDObject.LINE_STYLE_SOLID,
    JDObject.LINE_STYLE_DOT,
    JDObject.LINE_STYLE_DASH,
    JDObject.LINE_STYLE_LONG_DASH,
    JDObject.LINE_STYLE_DASH_DOT,
    JDObject.LINE_STYLE_LONG_DASH,
    JDObject.LINE_STYLE_DASH_DOT
  };

  static int ToJDFillStyle[] = {
    JDObject.FILL_STYLE_NONE,
    JDObject.FILL_STYLE_SOLID,
    JDObject.FILL_STYLE_SOLID,
    JDObject.FILL_STYLE_DOT_PATTERN_1,
    JDObject.FILL_STYLE_DOT_PATTERN_3,
    JDObject.FILL_STYLE_DOT_PATTERN_2,
    JDObject.FILL_STYLE_SMALL_LEFT_HATCH,
    JDObject.FILL_STYLE_LARGE_LEFT_HATCH,
    JDObject.FILL_STYLE_SMALL_RIGHT_HATCH,
    JDObject.FILL_STYLE_LARGE_RIGHT_HATCH,
    JDObject.FILL_STYLE_LARGE_CROSS_HATCH,
    JDObject.FILL_STYLE_SMALL_CROSS_HATCH,
    JDObject.FILL_STYLE_LARGE_CROSS_HATCH, // Square
    JDObject.FILL_STYLE_SMALL_CROSS_HATCH  // Square
  };

  Color   lineColor;
  int     lineStyle;
  int     lineWidth;
  Color   fillColor;
  int     fillStyle;
  float   gradientX1;
  float   gradientX2;
  float   gradientY1;
  float   gradientY2;
  Color   gradientC1;
  Color   gradientC2;
  boolean gradientCyclic;

  JLXStyle() {

    lineColor = Color.BLACK;
    fillColor = Color.WHITE;
    lineWidth = 1;
    lineStyle = JDObject.LINE_STYLE_SOLID;
    fillStyle = JDObject.FILL_STYLE_NONE;
    gradientX1=0.0F;
    gradientX2=10.0F;
    gradientY1=0.0F;
    gradientY2=10.0F;
    gradientC1=Color.white;
    gradientC2=Color.black;
    gradientCyclic=false;

  }

  public void parse(JLXFileLoader f) throws IOException {

    String type  = f.read_safe_word();

    if( type.equals("!") ) {

      // Default style
      return;

    } else  if( type.equals("A") ) {

      lineStyle = ToJDLineStyle[f.read_int()];
      lineWidth = (int)(f.read_double());
      if(f.version.compareTo("2.0.0") >= 0)
      {
        f.read_int(); // Line cap
        f.read_int(); // Line join
      }
      Color c = f.read_color();
      if(c!=null) lineColor = c;
      f.read_double(); // Transparency

      String fs = f.read_safe_word();
      if(fs.equals("!")) {
        // No fill
      } else if(fs.equals("F")) {
        fillColor = f.read_color();
        fillStyle = JDObject.FILL_STYLE_SOLID;
        if( fillColor==null )
          fillColor=Color.black;
        f.read_color();
      } else if (fs.equals("B")) {
        f.read_color();
        fillColor = f.read_color();
        if( fillColor==null )
          fillColor=Color.black;
        fillStyle = JDObject.FILL_STYLE_SOLID;
      } else if (fs.equals("C")) {
        fillColor = f.read_color();
        if( fillColor==null )
          fillColor=Color.white;
        fillStyle = JDObject.FILL_STYLE_SOLID;
      } else if (fs.equals("G")) {

        // Gradient fill
        gradientX1 = (float)f.read_double();
        f.jump_colon();
  	    gradientY1 = (float)f.read_double();
        f.jump_colon();
  	    gradientX2 = (float)f.read_double();
        f.jump_colon();
  	    gradientY2 = (float)f.read_double();

        String flags = f.read_safe_word();
        gradientCyclic      = flags.charAt(0)=='1';
        boolean transparent = flags.charAt(1)=='1';
        Color color  = f.read_color();
        if(color!=null) gradientC1 = color;
        color = f.read_color();
        if(color!=null) gradientC2 = color;

        if (transparent)
          gradientC1 = new Color(gradientC1.getRed(), gradientC1.getGreen(), gradientC1.getBlue(), 0);

        int gradientType = 0; // Radial
        if (f.version.compareTo("2.0.2") >= 0)
          gradientType = f.read_int();

        if (gradientType == 0) {
          // Linear gradient
          fillStyle=JDObject.FILL_STYLE_GRADIENT;
        } else if (gradientType == 1) {
          // Radial grdient
        }

      } else if(fs.equals("T")) {

         // Bitmap fill
         f.read_string(); // Filename
         f.read_color();
         f.read_color();

      } else if(fs.equals("S")) {

        int fillstyle = f.read_int();
        Color color   = f.read_color();
        Color color2  = f.read_color();
        if( fillstyle==1 )
          fillColor = color;
        else if ( fillstyle==2 )
          fillColor = color2;
        else
          fillColor = Color.BLACK;

        if( fillColor==null )
          fillColor = Color.BLACK;

        fillStyle = ToJDFillStyle[fillstyle];

      } else
        throw new IOException("Bad style format at line " + f.getCurrentLine());

      f.read_safe_full_word(); // Jump layer array

    } else {

      throw new IOException("Unsupported style type at line " + f.getCurrentLine());

    }


  }


}
