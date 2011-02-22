// File:          FileManager.java
// Created:       2002-11-25 11:13:03, erik
// By:            <Erik Assum <erik@assum.net>>
// Time-stamp:    <2003-01-14 18:10:54, erik>
// 
// $Id$
// 
// Description:       
package explorer;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import javax.swing.JOptionPane;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;

import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.CommandList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.EventSupport;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IErrorListener;

/**
 * Class that manages all interactions with files (load/save, errors, etc...)
 * 
 * @author Erik ASSUM
 */
public class FileManager {
    /** the list of attributes to save/load */
    List attributes = new LinkedList();

    /** the list of commands to save/load */
    List commands = new LinkedList();

    /** the preferences to save/load */
    Preferences preferences = new Preferences();

    /** manages errors */
    EventSupport propChanges = new EventSupport();

    protected static FileManager instance;

    /**
     * Class constructor, initializer.
     */
    protected FileManager() {

    }

    /**
     * Returns the file manager in session
     */
    public synchronized static FileManager getInstance() {
        if (instance == null) {
            instance = new FileManager();
        }
        return instance;
    }

    /**
     * Publishes an error in a <code>EventSupport</code>
     * 
     * @param e
     *            the error to publish
     */
    void publishError(Exception e) {
        propChanges.fireReadErrorEvent(this, e);
    }

    /**
     * Adds an error listener in the <code>EventSupport</code>
     * 
     * @param l
     *            the listener to add
     */
    public void addErrorListener(IErrorListener l) {
        propChanges.addErrorListener(l);
    }

    /**
     * Removes an error listener from the <code>EventSupport</code>
     * 
     * @param l
     *            the listener to remove
     */
    public void removeErrorListener(IErrorListener l) {
        propChanges.removeErrorListener(l);
    }

    /**
     * Sets the preferences to a specific value
     * 
     * @param prefs
     *            the value
     */
    public void setPreferences(Preferences prefs) {
        preferences = prefs;
    }

    /**
     * Returns the preferences associated with this file manager
     */
    public Preferences getPreferences() {
        return preferences;
    }

    /**
     * Sets the list of attributes of this file manager. This is used on
     * loading/saving a file
     * 
     * @param attributeList
     *            the list of attributes
     */
    public void setAttributes(AttributePolledList attributeList) {
        attributes.clear();
        for (int i = 0; i < attributeList.size(); i++) {
            IAttribute attribute = (IAttribute) attributeList.get(i);
            AttributeCache cache = new AttributeCache(attribute.getName(),
                    attribute.getAlias(), attribute.getDevice().getAlias());
            attributes.add(cache);
        }
    }

    /**
     * Sets the list of commands of this file manager. This is used on
     * loading/saving a file
     * 
     * @param commandList
     *            the list of commands
     */
    public void setCommands(CommandList commandList) {
        commands.clear();
        for (int i = 0; i < commandList.size(); i++) {
            ICommand command = (ICommand) commandList.get(i);
            CommandCache cache = new CommandCache(command.getName(), command
                    .getAlias(), command.getDevice().getAlias());
            commands.add(cache);
        }
    }

    /**
     * @return the list of attributes of this file manager
     */
    public AttributePolledList getAttributeList() {
        AttributePolledList list = new AttributePolledList();

        for (int i = 0; i < attributes.size(); i++) {
            //IAttribute attribute;
            AttributeCache cache = (AttributeCache) attributes.get(i);

            try {
                /*attribute = (IAttribute) */
                list.add(cache.name);
                /*if (cache.alias != null)
                    attribute.setAlias(cache.alias);*/
                /*
                 * if (cache.deviceAlias != null)
                 * attribute.getDevice().setAlias(cache.deviceAlias);
                 */
            }
            catch (ConnectionException e) {
                publishError(e);
            }
        }
        return list;
    }

    /**
     * @return the list of commands of this file manager
     */
    public CommandList getCommandList() {
        CommandList list = new CommandList();

        for (int i = 0; i < commands.size(); i++) {
            ICommand command;
            CommandCache cache = (CommandCache) commands.get(i);
            try {
                command = (ICommand) list.add(cache.name);
                if (cache.alias != null)
                    command.setAlias(cache.alias);
                /*
                 * if (cache.deviceAlias != null)
                 * command.getDevice().setAlias(cache.deviceAlias);
                 */
            }
            catch (ConnectionException e) {
                publishError(e);
            }
        }
        return list;
    }

    /**
     * Writes the necessary information about an attribute/command in file
     * 
     * @param writer
     *            the <code>PrintWriter</code> that controls the file
     * @param entity
     *            the <code>EntityCache</code> containing entity informations
     */
    public void writeEntity(PrintWriter writer, EntityCache entity) {
        String name = entity.name;
        String alias = entity.alias;
        String deviceAlias = entity.deviceAlias;

        writer.println("name = \"" + name + "\"");
        if (alias != null) {
            writer.println(" alias = \"" + alias + "\"");

        }
        if (deviceAlias != null) {
            writer.println(" deviceAlias = \"" + deviceAlias + "\"");
        }
    }

    /**
     * Saves the informations about the entities of this file manager in file
     * 
     * @param writer
     *            the <code>PrintWriter</code> that controls the file
     */
    void saveEntities(PrintWriter writer) {
        writer.println("\t<tangoentities>");
        writer.println("\t\t<attributes>");

        for (int i = 0; i < attributes.size(); i++) {
            EntityCache attribute = (EntityCache) attributes.get(i);
            writer.print("\t\t\t<attribute ");
            writeEntity(writer, attribute);
            writer.println("/>");
        }

        writer.println("\t\t</attributes>");
        writer.println("\t\t<commands>");

        for (int i = 0; i < commands.size(); i++) {
            EntityCache command = (EntityCache) commands.get(i);
            writer.print("\t\t\t<command ");
            writeEntity(writer, command);
            writer.println("/>");
        }

        writer.println("\t\t</commands>");
        writer.println("\t</tangoentities>");
    }

    /**
     * Saves presentation preferences of the application in file
     * 
     * @param writer
     *            the <code>PrintWriter</code> that controls the file
     */
    void savePreferences(PrintWriter writer) {
        writer.println("<map MAP_XML_VERSION=\"1.0\">");
        Iterator i = preferences.getKeys().iterator();

        while (i.hasNext()) {
            String key = (String) i.next();
            writer.print("  <entry key=");
            writer.print("\"" + key + "\"");
            writer.print(" ");
            writer.print("value=");
            writer.print("\"" + preferences.get(key) + "\"");
            writer.println(" />");
        }
        writer.println("</map>");
    }

    /**
     * Creates an <code>AttributeCache</code> with the necessary information
     * for an attribute
     * 
     * @param name
     *            the name of the attribute
     * @param alias
     *            the alias of the attribute. Deprecated
     * @param devAlias
     *            the alias of the attribute's device. Deprecated
     */
    protected void cacheAttr(String name, String alias, String devAlias) {
        AttributeCache cache = new AttributeCache(name, alias, devAlias);
        attributes.add(cache);

    }

    /**
     * Creates an <code>CommandCache</code> with the necessary information for
     * a command
     * 
     * @param name
     *            the name of the command
     * @param alias
     *            the alias of the command. Deprecated
     * @param devAlias
     *            the alias of the command's device. Deprecated
     */
    protected void cacheCmd(String name, String alias, String devAlias) {
        CommandCache cache = new CommandCache(name, alias, devAlias);
        commands.add(cache);
    }

    protected void startEntity(String uri, String localName, String qname,
            Attributes attrs) throws ConnectionException {

        if ("attribute".equalsIgnoreCase(qname)) {
            String name = attrs.getValue("name");
            String alias = attrs.getValue("alias");
            String device = attrs.getValue("deviceAlias");
            cacheAttr(name, alias, device);
            return;
        }

        if ("command".equalsIgnoreCase(qname)) {
            String name = attrs.getValue("name");
            String alias = attrs.getValue("alias");
            String device = attrs.getValue("deviceAlias");
            cacheCmd(name, alias, device);
            return;
        }

        if ("entry".equalsIgnoreCase(qname)) {
            String key = attrs.getValue("key");
            String value = attrs.getValue("value");

            if ("true".equals(value) || "false".equals(value)) {
                preferences.putBoolean(key, "true".equals(value));
                return;
            }

            if (value.length() < 20) {
                try {
                    preferences.putDouble(key, Double.parseDouble(value));
                }
                catch (NumberFormatException e) {
                    preferences.putString(key, value);
                }
            }
            else {
                preferences.putString(key, value);
            }

        }

    }

    /**
     * Saves all informations in file
     * 
     * @param file
     *            the file
     * @throws IOException
     *             on file access problems
     */
    public void save(File file) throws IOException {
        PrintWriter writer = new PrintWriter(new BufferedWriter(new FileWriter(
                file.getAbsolutePath())));
        writer.println("<?xml version=\"1.0\"?>");
        writer.println("<devicetree>");
        saveEntities(writer);
        savePreferences(writer);
        writer.println("</devicetree>");
        writer.flush();
        writer.close();
    }

    /**
     * Opens a file for loading
     * 
     * @param source
     *            the file path
     * @return <code>true</code> when the file is correctly opened and is a
     *         device tree file, <code>false</code> otherwise
     * @throws SAXException
     *             on xml parsing problems
     * @throws ParserConfigurationException
     *             on xml parsing problems
     * @throws IOException
     *             on file access problems
     */
    public boolean open(String source) throws SAXException,
            ParserConfigurationException, IOException {
        String src = source;
        BufferedReader reader = new BufferedReader(new FileReader(src));
        String line = "";

        try {
            line = reader.readLine();
            if ((line == null)
                    || !(line.trim()
                            .equalsIgnoreCase("<?xml version=\"1.0\"?>"))) {
                reader.close();
                throw new DeviceTreeFileException(
                        "This file is not an xml file (so it can't be a Device Tree configuration file)");
            }
            line = reader.readLine();
            if ((line == null)
                    || !(line.trim().equalsIgnoreCase("<devicetree>"))) {
                reader.close();
                throw new DeviceTreeFileException(
                        "This xml file is not a Device Tree configuration file");
            }
            reader.close();
            XMLReader parser = SAXParserFactory.newInstance().newSAXParser()
                    .getXMLReader();

            parser.setContentHandler(new DefaultHandler() {
                public void startElement(String uri, String localName,
                        String qname, Attributes attributes)
                        throws SAXException {
                    try {
                        startEntity(uri, localName, qname, attributes);
                    }
                    catch (Exception e) {
                        throw new SAXException(e);
                    }
                }

                public void endElement(String uri, String localName,
                        String qname) {
                    // we dont do anything on an endElement
                }

            });
            commands.clear();
            attributes.clear();
            parser.parse(src);
            return true;
        }
        catch (DeviceTreeFileException dtf) {
            JOptionPane.showMessageDialog(null, "Bad file - " + source
                    + " : \n" + dtf.getMessage(), "Error",
                    JOptionPane.ERROR_MESSAGE);
            return false;
        }
        catch (SAXParseException e) {
            JOptionPane.showMessageDialog(null, "Failed to parse " + source
                    + "\n" + e.getMessage() + "[Line " + e.getLineNumber()
                    + "]", "Error", JOptionPane.ERROR_MESSAGE);
            return false;
        }
        catch (Exception ex) {
            JOptionPane.showMessageDialog(null,
                    "Unexpected error in file opening", "Error",
                    JOptionPane.ERROR_MESSAGE);
            return false;
        }
    }

    /**
     * A class to have the essential informations about an entity
     * @author SOLEIL
     */
    abstract class EntityCache {
        String name, alias, deviceAlias;

        protected EntityCache() {

        }

        EntityCache(String name, String alias, String deviceAlias) {
            this.name = name;
            this.alias = alias;
            this.deviceAlias = deviceAlias;
        }

    }

    class AttributeCache extends EntityCache {
        AttributeCache(String name, String alias, String deviceAlias) {
            super(name, alias, deviceAlias);
        }

    }

    class CommandCache extends EntityCache {
        CommandCache(String name, String alias, String deviceAlias) {
            super(name, alias, deviceAlias);
        }

    }
}