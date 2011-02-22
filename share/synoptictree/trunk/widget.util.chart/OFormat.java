//
package fr.esrf.tangoatk.widget.util.chart;

import java.awt.*;
import java.util.*;

/** Helper class for load/save graph settings. Multiple field parameters are returned in one
 * string , each field is separated by a colon */
public class OFormat {

  /**
   * Convert Color to String.
   * @param c Color to convert
   * @return A string containing color: "rrr,ggg,bbb"
   */
  public static String color(Color c) {
    return c.getRed()+","+c.getGreen()+","+c.getBlue();
  }
  /**
   * Convert Font to String
   * @param f Font to convert
   * @return A string containing the font: "Family,Style,Size"
   */
  public static String font(Font f) {
    return f.getFamily()+","+f.getStyle()+","+f.getSize();
  }

  /**
   * Convert String to String
   * @param s Input string
   * @return if s is equals to "null" return null, the given string otherwise
   */
  public static String getName(String s) {
    if( s.equalsIgnoreCase("null") )
      return null;
    else
      return s;
  }

  /**
   * Convert String to Boolean
   * @param s String to convert
   * @return true is string is "true" (case unsensitive), false otherwise
   */
  public static boolean getBoolean(String s) {
    return s.equalsIgnoreCase("true");
  }

  /**
   * Convert String to integer
   * @param s String to convert
   * @return Interger representation of the given string.
   */
  public static int getInt(String s) {
    int ret=0;    
    try {
      ret = Integer.parseInt(s);
    } catch( NumberFormatException e ) {
      System.out.println("Failed to parse '" + s + "' as integer");
    }      
    return ret;  
  }    

  /**
   * Convert String to double
   * @param s String to convert
   * @return Double representation of the given string.
   */
  public static double getDouble(String s) {
    double ret=0;    
    try {
      ret = Double.parseDouble(s);
    } catch( NumberFormatException e ) {
      System.out.println("Failed to parse '" + s + "' as double");
    }
    return ret;  
  }

  /**
   * Convert String to Color
   * @param v Vector to convert (coming from CfFileReader.getParam)
   * @return Color representation of the given string.
   * @see OFormat#color
   * @see CfFileReader#getParam
   */
  public static Color getColor(Vector v) {    
    
    int r=0,g=0,b=0;
    
    if( v.size()!=3 ) {
      System.out.println("Invalid color parameters.");
      return new Color(0,0,0);
    }
    
    try {
      r = saturate(Integer.parseInt(v.get(0).toString()));
      g = saturate(Integer.parseInt(v.get(1).toString()));
      b = saturate(Integer.parseInt(v.get(2).toString()));
    } catch( Exception e ) {
      System.out.println("Invalid color parameters.");
    }
    
    return new Color(r,g,b);  
  }

  private static int saturate(int value) {
    if(value<0)
      return 0;
    else if(value>255)
      return 255;
    else
      return value;
  }

  /**
   * Convert String to Font
   * @param v Vector to convert (coming from CfFileReader.getParam)
   * @return Font handle coresponding to the given string.
   * @see OFormat#font
   * @see CfFileReader#getParam
   */
  public static Font getFont(Vector v) {

    String f="Dialog";
    int style=Font.PLAIN;
    int size=11;
        
    if( v.size()!=3 ) {
      System.out.println("Invalid font parameters.");
      return new Font(f,style,size);  
    }
    
    try {
      f = v.get(0).toString();
      style = Integer.parseInt(v.get(1).toString());
      size  = Integer.parseInt(v.get(2).toString());
    } catch( Exception e ) {
      System.out.println("Invalid font parameters.");
    }
    
    return new Font(f,style,size);  
  }    
  
  /**
   * Convert String to Point
   * @param v Vector to convert (coming from CfFileReader.getParam)
   * @return Point coresponding to the given string.
   * @see CfFileReader#getParam
   */
  public static Point getPoint(Vector v) {

    int x=0;
    int y=0;

    if( v.size()!=2 ) {
      System.out.println("Invalid point parameter.");
      return new Point(x,y);
    }

    try {
      x = Integer.parseInt(v.get(0).toString());
      y = Integer.parseInt(v.get(1).toString());
    } catch( Exception e ) {
      System.out.println("Invalid point parameter.");
    }
    
    return new Point(x,y);
  }

}
