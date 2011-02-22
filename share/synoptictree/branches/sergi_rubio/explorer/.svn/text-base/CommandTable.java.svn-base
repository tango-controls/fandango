// File:          CommandTable.java
// Created:       2002-09-13 12:47:34, erik
// By:            <erik@assum.net>
// Time-stamp:    <2003-01-16 15:50:20, erik>
// 
// $Id$
// 
// Description:       

package explorer;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.datatransfer.DataFlavor;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JMenuItem;
import javax.swing.JTable;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import explorer.ui.PreferencesDialog;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.command.VoidVoidCommand;
import fr.esrf.tangoatk.widget.command.AnyCommandViewer;
import fr.esrf.tangoatk.widget.dnd.NodeFactory;
import fr.esrf.tangoatk.widget.util.HelpWindow;

/**
 * Class representing all things specific to the command table. It extends
 * <code>explorer.EntityTable</code>, the javadoc of which you can see for
 * further informations
 * 
 * @author Erik ASSUM
 */
public class CommandTable extends EntityTable {
    /** Adds the option to execute command in menu */
    protected JMenuItem execute;

    /** To view the command */
    protected AnyCommandViewer commandViewer;

    /** The "execute" panel */
    protected JDialog commandDialog;

    /**
     * Creates a new <code>CommandTable</code> instance.
     * 
     * @param isAdmin
     *            a <code>boolean</code> value, which is true if this is an
     *            administrator session.
     */
    public CommandTable(CommandTableModel model, Preferences prefs,
            boolean isAdmin) {
        setAdmin(isAdmin);
        preferences = prefs;
        initComponents(model, isAdmin);
        flavor = NodeFactory.MIME_COMMAND;
        setModel(model);
        initBorder ();
    }

    /**
     * Shows the "execute" panel
     */
    protected void showExecuteDialog() {
        ICommand command;

        if (getSelectedRow() == -1)
            return;

        command = (ICommand) model.getEntityAt(getSelectedRow());

        if (command instanceof VoidVoidCommand) {
            command.execute();
            return;
        }

        commandViewer = new AnyCommandViewer();
        commandDialog = new JDialog();
        commandViewer.initialize(command);
        commandViewer.setDeviceButtonVisible(false);
        commandViewer.setDescriptionVisible(true);
        //	commandViewer.setInfoButtonVisible(true);
        commandViewer.setBorder(null);
        String title = command.getAlias() != null ? command.getAlias()
                : command.getName();

        if (!command.takesInput()) {
            command.execute();
        }

        commandDialog.setTitle(title);
        commandDialog.getContentPane().add(commandViewer);
        commandDialog.pack();
        commandDialog.show();

    }

    /**
     * Initializes the "help" window
     */
    protected void initHelp() {
        helpUrl = "/explorer/html/CommandTableHelp.html";
        HelpWindow.getInstance().addCategory("Command Table", "Command table",
                getClass().getResource(helpUrl));

    }

    /**
     * Menus initialization for the command
     */
    protected void initMenus() {
        execute = new JMenuItem("Execute last selected...");
        execute.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                showExecuteDialog();
            }
        });
        //	popup.add(execute);
    }

    /**
     * Presentation preferences initialization for the command table (visible
     * fields)
     */
    protected void initPreferences() {
        PreferencesDialog.getInstance().addCategory("Command table",
                "visible fields", new ViewDialog(model));
    }

    /**
     * Manages the "drop" of a command in the table due to drag and drop
     * 
     * @param name
     *            the name of the command
     * @param flavor
     *            its <code>DataFlavor</code> representation for drag and drop
     */
    protected void dtHandleDrop(String name, DataFlavor flavor) {
        String mimeType = flavor.getMimeType();

        if (mimeType.startsWith(NodeFactory.MIME_COMMAND)) {
            ((CommandTableModel) model).addCommand(name);
            return;
        }
    }

    /**
     * Manages the right clicking over the command table to show the
     * corresponding menu
     * 
     * @param evt
     *            the <code>MouseEvent</code> for the "click"
     */
    protected void showPopup(MouseEvent evt) {
        int row = getRowAtPoint(evt.getPoint());

        if (row == -1)
            return;
        int[] rows = getSelectedRows();

        if (evt.isPopupTrigger()) {
            if (evt.isControlDown())
            {
                table.addRowSelectionInterval(row,row);
                rows = getSelectedRows();
            }
            else if (evt.isShiftDown())
            {
                rows = getSelectedRows();
                int min = rows[0];
                for (int i = 0; i < rows.length; i++)
                {
                    if (rows[i] < min) min = rows[i];
                }
                table.addRowSelectionInterval(min, row);
                rows = getSelectedRows();
            }
            else
            {
                boolean isInSelection = false;
                for (int i = 0; i < rows.length; i++)
                {
                    if (rows[i] == row)
                    {
                        isInSelection = true;
                        break;
                    }
                }
                if (!isInSelection)
                {
                    table.setRowSelectionInterval(row,row);
                }
            }
            popup.show(evt.getComponent(), evt.getX(), evt.getY());
        }
    }

    /**
     * Manages the clicking over the command table to select the command and
     * launch the "execute" panel when necessary
     * 
     * @param evt
     *            the <code>MouseEvent</code> for the "click"
     */
    protected void entityTableMouseClicked(MouseEvent evt) {
        int row = getRowAtPoint(evt.getPoint());
        //int column = 0;
        if (row == -1)
            return;
        //ICommand command = (ICommand) model.getEntityAt(row);

        if (model.isExecuteColumn(getColumnAtPoint(evt.getPoint())) && !evt.isPopupTrigger() ) {
            showExecuteDialog();
        }
    }

    /**
     * Creates/adds a column in the command table
     * 
     * @param name
     *            the name of the column
     * @param i
     *            the index of the column in the model which is to be displayed
     *            by this TableColumn
     */
    protected TableColumn createTableColumn(String name, int i) {
        if (EntityTableModel.DEVICE.equals(name)) {// device column;
            return new TableColumn(i, 75, deviceRenderer, null);
        }
        return new TableColumn(i, 75, new TableCellRenderer() {
            JButton renderer;

            public Component getTableCellRendererComponent(JTable table,
                    Object value, boolean isSelected, boolean focus, int row,
                    int column) {
                if (renderer == null)
                    renderer = new JButton();
                JButton dummy = new JButton();
                if (isSelected)
                {
                    renderer.setBackground(Color.DARK_GRAY);
                    renderer.setForeground(Color.WHITE);
                }
                else
                {
                    renderer.setBackground(dummy.getBackground());
                    renderer.setForeground(dummy.getForeground());
                }

                try {
                    String commandName = model.getValueAt(row, column)
                            .toString();
                    renderer.setText(commandName);
                } catch (Exception e) {
                    System.out.println("CommandTableModel " + e);
                }

                return renderer;
            }
        }, null);
    }

    private void initBorder ()
    {
        Font font = new Font("Arial", Font.PLAIN, 10);
        Color color = new Color(0,0,150);
        String title = "Command Panel";
        TitledBorder tb = BorderFactory.createTitledBorder
                ( BorderFactory.createMatteBorder(1, 1, 1, 1, color) ,
                  title ,
                  TitledBorder.CENTER ,
                  TitledBorder.TOP,
                  font,
                  color
                );
        Border border = ( Border ) ( tb );
        this.setBorder( border );
    }
}