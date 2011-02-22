package fr.esrf.tangoatk.widget.util.chart;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.File;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.filechooser.FileFilter;

public class AdvancedJLChart extends JLChart {

    /* Load data file menu item */
    public static final int MENU_DATALOAD  = 6;
    /* Reset Chart menu item */
    public static final int MENU_RESET     = 7;

    protected JPopupMenu dataViewMenu;
    protected JMenuItem removeDataViewMenuItem;
    protected JMenuItem dataViewOptionItem;
    protected JMenuItem loadFileMenuItem;
    protected JMenuItem resetMenuItem;

    public AdvancedJLChart () {
        super();
        loadFileMenuItem = new JMenuItem("Load data File");
        loadFileMenuItem.addActionListener(this);
        resetMenuItem = new JMenuItem("Reset Chart");
        resetMenuItem.addActionListener(this);
        chartMenu.add(loadFileMenuItem);
        chartMenu.add(resetMenuItem);
    }

    @Override
    public void removeMenuItem (int menu) {
        switch (menu) {
            /* Save data file menu item */
            case MENU_DATALOAD:
                chartMenu.remove(loadFileMenuItem);
                break;
            /* Reset Chart menu item */
            case MENU_RESET:
                chartMenu.remove(resetMenuItem);
                break;
            default:
                super.removeMenuItem(menu);
        }
    }

    @Override
    public void actionPerformed (ActionEvent evt) {
        if ( evt.getSource() == loadFileMenuItem ) {
            JFileChooser chooser = new JFileChooser(lastDataFileLocation);
            chooser.addChoosableFileFilter(
                    new FileFilter() {
                        public boolean accept (File f) {
                            if ( f.isDirectory() ) {
                                return true;
                            }
                            String extension = getExtension(f);
                            if ( extension != null
                                    && extension.equals("txt") ) {
                                return true;
                            }
                            return false;
                        }

                        public String getDescription () {
                            return "text files ";
                        }
                    }
            );
            chooser.setDialogTitle(
                    "Load Graph Data (Text file with TAB separated fields)"
            );
            int returnVal = chooser.showOpenDialog(this);
            if (returnVal == JFileChooser.APPROVE_OPTION) {
                File f = chooser.getSelectedFile();
                if ( f != null ) {
                    loadDataFile( f.getAbsolutePath() );
                    lastDataFileLocation = f.getParentFile().getAbsolutePath();
                }
            }
        }
        else if (evt.getSource() == resetMenuItem) {
            reset();
            repaint();
        }
        else {
            super.actionPerformed(evt);
        }
    }

    @Override
    public void mousePressed (MouseEvent e) {
        boolean displayDataViewMenu = false;
        if ( e.getButton() == MouseEvent.BUTTON3 ) {
            int i = 0;
            // Click on label
            while ( i < labelRect.size() ) {
                final LabelRect r = (LabelRect) labelRect.get(i);
                if ( r.rect.contains( e.getX(), e.getY() ) ) {
                    displayDataViewMenu = prepareDataViewMenu(r.view);
                    break;
                }
                i++;
            }
        }

	    if (displayDataViewMenu) {
            dataViewMenu.show( this, e.getX(), e.getY() );
        }
        else {
            super.mousePressed( e );
        }
    }

    protected boolean prepareDataViewMenu(JLDataView dataView) {
        if (dataViewMenu == null) {
            dataViewMenu = new JPopupMenu();
            removeDataViewMenuItem = new JMenuItem("Remove");
            dataViewOptionItem = new JMenuItem("Options");
            dataViewMenu.add(removeDataViewMenuItem);
            dataViewMenu.add(dataViewOptionItem);
        }
        final JLDataView theView = dataView;
        removeDataViewMenuItem.setText( "Remove : "
                + dataView.getName() );
        ActionListener[] listeners = removeDataViewMenuItem
                .getActionListeners();
        for (int j = 0; j < listeners.length; j++) {
            removeDataViewMenuItem
                    .removeActionListener( listeners[j] );
        }
        removeDataViewMenuItem.addActionListener(
                new ActionListener() {
                    public void actionPerformed (ActionEvent e) {
                        AdvancedJLChart.this.removeDataView(theView);
                        AdvancedJLChart.this.repaint();
                    }
                }
        );
        dataViewOptionItem.setText(
                "Options : " + dataView.getName()
        );
        listeners = dataViewOptionItem.getActionListeners();
        for (int j = 0; j < listeners.length; j++) {
            dataViewOptionItem.removeActionListener( listeners[j] );
        }
        dataViewOptionItem.addActionListener(
                new ActionListener() {
                    public void actionPerformed (ActionEvent e) {
                        showDataOptionDialog(theView);
                    }
                }
        );
        return true;
    }

    public static void main (String[] args) {
        final JFrame f = new JFrame();
        final AdvancedJLChart chart = new AdvancedJLChart();

        // Initialise chart properties
        chart.setHeaderFont(new Font("Times", Font.BOLD, 18));
        chart.setLabelFont(new Font("Times", Font.BOLD, 12));
        chart.setHeader("Test DataView");

        String fileName;
        if (args.length > 0) {
            fileName = args[0];
        }
        else {
            JFileChooser chooser = new JFileChooser(".");
            chooser.addChoosableFileFilter(
                    new FileFilter() {
                        public boolean accept(File f) {
                            if (f.isDirectory()) {
                                return true;
                            }
                            String extension = null;
                            String s = f.getName();
                            int i = s.lastIndexOf('.');
                            if (i > 0 && i < s.length() - 1) {
                                extension = s.substring(i+1).toLowerCase();
                            }
                            if ( extension != null
                                    && extension.equals("txt") ) {
                                return true;
                            }
                            return false;
                        }

                        public String getDescription() {
                            return "text files ";
                        }
                    }
            );
            chooser.setDialogTitle(
                    "Load Graph Data (Text file with TAB separated fields)"
            );
            int returnVal = chooser.showOpenDialog(null);
            if (returnVal == JFileChooser.APPROVE_OPTION) {
                File file = chooser.getSelectedFile();
                fileName = file.getAbsolutePath();
            }
            else {
                fileName = "";
                System.exit( 0 );
            }
        }

        chart.reset(false);
        chart.loadDataFile(fileName);

        JPanel bot = new JPanel();
        bot.setLayout( new FlowLayout() );
        JButton b = new JButton("Exit");
        b.addMouseListener(
                new MouseAdapter() {
                    public void mouseClicked (MouseEvent e) {
                        System.exit(0);
                    }
                }
        );
        bot.add(b);

        JButton c = new JButton("Options");
        c.addMouseListener(
                new MouseAdapter() {
                    public void mouseClicked (MouseEvent e) {
                        chart.showOptionDialog();
                    }
                }
        );
        bot.add(c);
 
        f.getContentPane().setLayout( new BorderLayout() );
        f.getContentPane().add(chart, BorderLayout.CENTER);
        f.getContentPane().add(bot, BorderLayout.SOUTH);
        f.setSize(400, 300);
        f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        f.setVisible(true);
    }

}
