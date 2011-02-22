package fr.esrf.tangoatk.widget.util.jdraw;

import fr.esrf.tangoatk.widget.util.ATKConstant;

import java.io.IOException;
import java.awt.geom.Rectangle2D;
import java.awt.*;

class LXObject {

  int         type;
  String      name = "";
  Font        font = ATKConstant.labelFont;
  boolean     visible = true;
  int         userClass = 0;
  Color       foreground = Color.BLACK;
  Color       background = Color.WHITE;
  int         lineWidth = 1;
  int         lineStyle = 0;
  int         lineArrow = 0;
  int         fillStyle = 0;
  int         shadowWidth = 0;
  boolean     invertShadow = false;
  int         arcMode = 0;

  double      px=0,py=0;
  Rectangle2D boundRect;

  // For the '=' management
  static Color lastForeground;
  static Color lastBackground;
  static int   lastLineWidth;
  static int   lastLineStyle;
  static int   lastLineArrow;
  static int   lastFillStyle;
  static int   lastArcMode;
  static Font  lastFont;

  LXObject() {}

  void setBounds(double x,double y,double w,double h) {
    boundRect = new Rectangle2D.Double(x+px,y+py,w,h);
  }

  boolean toDo(int mask,int i) {
    return (mask & i) == i;
  }

  void parse(LXFileLoader f, boolean inGroup) throws IOException {

    if (!inGroup) {

      // Read Object number
      f.read_safe_word();      // 'N'
      f.read_int();            // Object number

      f.read_safe_word();        // 'P'
      px = f.read_double();      // Object X position
      py = f.read_double();      // Object Y position

      f.read_safe_word();        // 'T'
      int traj = f.read_int();   // Trajectory params
      if (traj != -1) {
        f.read_int();
        f.read_int();
        f.read_int();
        f.read_int();
        f.read_int();
        f.read_int();
      }

      f.read_safe_word();         // 'R'
      f.read_int();               // Rotation param
      f.read_int();               // Rotation param

      f.read_int();               // Lock flag

    }

    // Read object
    f.read_int();               // '0' ???
    type = f.read_int();        // Object type
    f.read_int();               // ???
    userClass = f.read_int();   // User class

    f.jump_space();
    if (f.CurrentChar == 'N') {
      f.read_safe_word();         // 'Name'
      f.jump_space();
      name = f.read_line();       // Object name
    }

    f.read_int();               // Blink
    visible = (f.read_int() == 1);// Visible flag
    f.read_int();               // Layer

    // Object Attribute
    f.read_safe_word();           // '!'
    f.jump_space();
    if (f.CurrentChar != '=') {

      int doMask = f.read_int_16(); // to do flag

      if (toDo(doMask, 1))
        f.read_safe_word();

      if (toDo(doMask, 2)) {
        foreground = f.read_color();
        lastForeground = foreground;
      }

      if (toDo(doMask, 4)) {
        background = f.read_color();
        lastBackground = background;
      }

      if (toDo(doMask, 8)) {
        lineWidth = f.read_int() + 1;    // DOLINEWIDTH
        if (lineWidth > 6) lineWidth = 0;
        lastLineWidth = lineWidth;
      }

      if (toDo(doMask, 16)) {
        lineStyle = JLXStyle.ToJDLineStyle[f.read_int()]; // DOLINESTYLE
        lastLineStyle = lineStyle;
      }

      if (toDo(doMask, 32)) {
        lineArrow = JLXPath.ToJDLineArrow[f.read_int()];  // DOARROW
        lastLineArrow = lineArrow;
      }

      if (toDo(doMask, 64)) {
        fillStyle = JLXStyle.ToJDFillStyle[f.read_int()]; // DOFILLSTYLE
        f.read_int();                // transparency
        lastFillStyle = fillStyle;
      }

      if (toDo(doMask, 128)) {
        arcMode = f.read_int();       // DOARCMODE
        lastArcMode = arcMode;
      }

      if (toDo(doMask, 256)) {
        font = f.read_font();               // DOFONT
        lastFont = font;
      }

    } else {

      f.read_safe_word();  // '='

      // aplly last read attributes
      font = lastFont;
      arcMode = lastArcMode;
      fillStyle = lastFillStyle;
      lineArrow = lastLineArrow;
      lineStyle = lastLineStyle;
      lineWidth = lastLineWidth;
      foreground = lastForeground;
      background = lastBackground;

    }

    if( fillStyle>1 ) {
      // Hatched fill style
      background = foreground;
    }

  }


}
