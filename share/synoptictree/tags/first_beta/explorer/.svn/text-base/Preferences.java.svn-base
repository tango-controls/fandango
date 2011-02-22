// File:          Preferences.java
// Created:       2002-11-21 13:38:50, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2003-01-14 18:11:10, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.util.*;

/**
 * A class to manage preferences for device tree application. You control your
 * preferences by associating keys with values.
 * 
 * @author Erik ASSUM
 */
public class Preferences {
    Map values = new HashMap();

    /**
     * Gives the <code>int</code> value associated to a key
     * 
     * @param key
     *            the key for which you want the associated <code>int</code>
     * @param def
     *            the default value if no association exists
     * @return the <code>int</code> associtated with the key if this
     *         association exists, the default value in parameter otherwise
     */
    public int getInt(String key, int def) {
        int val = def;
        Number tmp;
        tmp = (Number) values.get(key);
        if (tmp != null)
            val = tmp.intValue();
        return val;
    }

    /**
     * Associates an <code>int</code> value with a key
     * 
     * @param key
     *            the key
     * @param val
     *            the <code>int</code> value
     */
    public void putInt(String key, int val) {
        values.put(key, new Integer(val));
    }

    /**
     * Gives the <code>double</code> value associated to a key
     * 
     * @param key
     *            the key for which you want the associated <code>double</code>
     * @param def
     *            the default value if no association exists
     * @return the <code>double</code> associtated with the key if this
     *         association exists, the default value in parameter otherwise
     */
    public double getDouble(String key, double def) {
        double val = def;
        Number tmp;
        tmp = (Number) values.get(key);
        if (tmp != null)
            val = tmp.doubleValue();
        return val;
    }

    /**
     * Associates a <code>double</code> value with a key
     * 
     * @param key
     *            the key
     * @param val
     *            the <code>double</code> value
     */
    public void putDouble(String key, double val) {
        values.put(key, new Double(val));
    }

    /**
     * Gives the <code>boolean</code> value associated to a key
     * 
     * @param key
     *            the key for which you want the associated <code>boolean</code>
     * @param def
     *            the default value if no association exists
     * @return the <code>boolean</code> associtated with the key if this
     *         association exists, the default value in parameter otherwise
     */
    public boolean getBoolean(String key, boolean def) {
        boolean val = def;
        Boolean tmp;
        tmp = (Boolean) values.get(key);
        if (tmp != null)
            val = tmp.booleanValue();
        return val;
    }

    /**
     * Associates a <code>boolean</code> value with a key
     * 
     * @param key
     *            the key
     * @param val
     *            the <code>boolean</code> value
     */
    public void putBoolean(String key, boolean val) {
        values.put(key, new Boolean(val));
    }

    /**
     * Gives the <code>String</code> value associated to a key
     * 
     * @param key
     *            the key for which you want the associated <code>String</code>
     * @param def
     *            the default value if no association exists
     * @return the <code>String</code> associtated with the key if this
     *         association exists, the default value in parameter otherwise
     */
    public String getString(String key, String def) {
        String val = def;
        String tmp;
        tmp = (String) values.get(key);
        if (tmp != null)
            return tmp;
        else
            return val;
    }

    /**
     * Associates a <code>String</code> value with a key
     * 
     * @param key
     *            the key
     * @param val
     *            the <code>String</code> value
     */
    public void putString(String key, String val) {
        values.put(key, new String(val));
    }

    /**
     * Returns the list of keys as a <code>Set</code>
     */
    public Set getKeys() {
        return values.keySet();
    }

    /**
     * Gives the value associated to a key
     * 
     * @param key
     *            the key for which you want the associated value
     * @return the value associated to the key
     */
    public Object get(String key) {
        return values.get(key);
    }

}