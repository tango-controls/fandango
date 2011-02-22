/*
 * CfFileReader.java
 * A config file browser
 */

package fr.esrf.tangoatk.widget.util.chart;

import java.io.*;
import java.util.*;

/**
 * A class to parse configuration file
 * @author JL Pons
 */
public class CfFileReader {

  // ----------------------------------------------------
  // Inner class Item
  // Handle one property in the config file
  // ----------------------------------------------------
  class Item {

    public Vector items;
    String name;

    public Item(String name) {
      items = new Vector();
      this.name=name;
    }

    public void addProp(String value) {
      items.add( value );
    }

    public String toString() {
      return name;
    }

  }

  // ----------------------------------------------------
  // Class variable
  // ----------------------------------------------------
  Vector     prop;
  FileReader file;
  String     cfStr;
  char       currentChar;

  // ----------------------------------------------------
  // General constructor
  // ----------------------------------------------------
  public CfFileReader() {
    prop  = new Vector();
    cfStr = null;
    file  = null;
  }

  // ----------------------------------------------------
  // Get the current char
  // ----------------------------------------------------
  private char getCurrentChar() throws IOException {

    char c;

    if( file!=null ) {
      return (char)file.read();
    } else if( cfStr!=null ) {
      c = (char)cfStr.charAt(0);
      cfStr = cfStr.substring(1);
      return c;
    }

    return (char)0;
  }

  // ----------------------------------------------------
  // Return true when EOF
  // ----------------------------------------------------
  private boolean eof() throws IOException {

    if( file!=null ) {
      return !file.ready();
    } else if( cfStr!=null ) {
      return cfStr.length()==0;
    }

    return true;
  }

  // ----------------------------------------------------
  // Read the file word by word
  // ----------------------------------------------------
  private String readWord() throws IOException {

    boolean found=(currentChar>32);
    String  ret = "";

    // Jump space
    while( !eof() && !found ) {
      currentChar = getCurrentChar();
      found = (currentChar>32);
    }

    if( !found ) return null;

    // Treat strings
    if( currentChar=='\'' ) {

      found=false;
      while( !eof() && !found ) {
        currentChar = getCurrentChar();
        found = (currentChar=='\'');
	if( !found ) ret += currentChar;
      }

      if( !found ) {
         System.out.println("CfFileReader.parse: '\'' is missing");
	 return null;
      }

      //System.out.println("ReadWord:" + ret);
      currentChar = getCurrentChar();
      return ret;
    }

    // Read the next word
    ret += currentChar;
    if( (currentChar==',') || (currentChar==':') ) {
      currentChar = getCurrentChar();
      //System.out.println("ReadWord:" + ret);
      return ret;
    } else {
      found = false;
      while( !eof() && !found ) {
        currentChar = getCurrentChar();
        found = (currentChar==',') || (currentChar==':') || (currentChar<=32);
        if( !found) ret += currentChar;
      }
      //System.out.println("ReadWord:" + ret);
      return ret;
    }

  }

  // ----------------------------------------------------
  // Read the config file and fill properties vector
  // Return true when succesfully browsed
  // ----------------------------------------------------
  private boolean parse() throws IOException {

    prop.clear();
    currentChar=0;
    String word=readWord();
    boolean sameItem;

    while(word!=null) {

         // Create new item
	 Item it = new Item(word);

	 // Jump ':'
         word = readWord();

	 if( !word.equals(":") ) {
	   System.out.println("CfFileReader.parse: ':' expected instead of " + word);
	   return false;
	 }

	 // Read values

	 sameItem = true;
	 while( sameItem ) {
	   sameItem = false;
	   word = readWord();
	   if( word!=null ) it.addProp( word );
	   word = readWord();
	   if( word!=null ) sameItem = word.equals(",");
	 }

	 prop.add( it );

    }

    return true;
  }

  /**
  * Parse the given string and fill property vector.
  * @param text String containing text to parse
  * @return Return true when text succesfully parsed
  */

  public boolean parseText(String text) {
    boolean ok=false;
    try {
      cfStr=text;
      ok = parse();
    } catch ( Exception e ) {
    }

    return ok;
  }

  /**
  * Parse the given file and fill property vector.
  * @param filename File to parse
  * @return Return true when file succesfully parsed
  */

  public boolean readFile(String filename) {
    boolean ok=false;
    try {
      file = new FileReader(filename);
      ok = parse();
      file.close();
    } catch ( Exception e ) {
    }

    return ok;
  }

  /**
  * Return all parameter names found in the config file.
  * @return Returns a vector of String.
  */

   public Vector getNames() {

    Vector v = new Vector();
    for( int i=0;i<prop.size();i++ ) {
      v.add( prop.get(i).toString() );
    }
    return v;

  }

  /**
  * Return parameter value, one parameter can have multiple fields seperated by a colon.
  * @param name Parameter name
  * @return Returns a vector of String. (1 string per field)
  */

  public Vector getParam(String name) {
    boolean found=false;
    int i=0;

    while( !found && i<prop.size() ) {
      found = name.equals( prop.get(i).toString() );
      if(!found) i++;
    }
    if( found ) {
      Item it = (Item)prop.get(i);
      return it.items;
    } else {
      return null;
    }

  }

  // ----------------------------------------------------
  public static void main(String args[]) {
      final CfFileReader cf = new CfFileReader();

      if( cf.readFile("test.cfg") ) {

	Vector names = cf.getNames();
        System.out.println("Read " + names.size() +" params");

	for(int i=0;i<names.size();i++) {
	  System.out.println( names.get(i).toString() );
	  Vector values = cf.getParam( names.get(i).toString() );
	  for(int j=0;j<values.size();j++) {
	    System.out.println( "   " + values.get(j).toString() );
	  }
	}

      } else {
        System.out.println("Error while reading config file");
      }
  }

}
