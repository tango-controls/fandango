// File:          FileUI.java
// Created:       2002-09-18 12:57:09, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 10:25:57, erik>
// 
// $Id$
// 
// Description:       

package explorer.ui;

import java.awt.Container;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;
import java.awt.print.PageFormat;
import java.awt.print.Pageable;
import java.awt.print.Paper;
import java.awt.print.Printable;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;
import java.io.File;
import java.sql.Timestamp;
import java.util.Vector;
import javax.swing.ImageIcon;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JSeparator;
import javax.swing.JToolBar;
import javax.swing.filechooser.FileFilter;

/**
 * Usefull class to print
 * 
 * @author SOLEIL
 */
class DTPrinter implements Printable, Pageable
{
    private Container       container;
    private PageFormat      pageFormat;
    private PrinterJob      printJob;
    private Vector          taillePages;
    private String          documentTitle;
    private BufferedImage   toPrint;
    private int             fitMode;
    private int             pageCount      = 1;
    private double          ratio          = 1;
    private Timestamp       date;

    public final static int PORTRAIT       = PageFormat.PORTRAIT;
    public final static int LANDSCAPE      = PageFormat.LANDSCAPE;

    public final static int FIT_PAGE_WIDTH = 0;
    public final static int FIT_PAGE       = 1;
    public final static int NO_FIT         = 2;


    public DTPrinter (Container container)
    {
        toPrint = null;
        documentTitle = "";
        this.container = container;
        initPrintablePanel();
    }

    public void initPrintablePanel ()
    {
        fitMode = NO_FIT;
        printJob = PrinterJob.getPrinterJob();
        pageFormat = printJob.defaultPage();
        Paper paper = (Paper)pageFormat.getPaper().clone();
        paper.setImageableArea( paper.getImageableX(), paper.getImageableY(), paper.getWidth() - 30, paper.getHeight() - 30);
        pageFormat.setPaper(paper);
    }

    public void setOrientation (int orientation)
    {
        pageFormat.setOrientation( orientation );
    }

    public void setFitMode (int fitMode)
    {
        this.fitMode = fitMode;
    }

    public int getPageWidth ()
    {
        return (int) pageFormat.getImageableWidth();
    }

    public double getMarginTop ()
    {
        return pageFormat.getImageableY();
    }

    public double getMarginLeft ()
    {
        return pageFormat.getImageableX();
    }

    public void setLRMargins (double margin)
    {
        Paper paper = pageFormat.getPaper();
        paper.setImageableArea(
                margin,
                paper.getImageableY(),
                paper.getWidth() - margin,
                paper.getImageableHeight()
        );
        pageFormat.setPaper( paper );
    }

    public void setTBMargins (double margin)
    {
        Paper paper = pageFormat.getPaper();
        paper.setImageableArea(
                paper.getImageableX(),
                margin,
                paper.getImageableWidth(),
                paper.getHeight() - margin
        );
        pageFormat.setPaper(paper);
    }

    public void setDocumentTitle (String title)
    {
        documentTitle = title;
    }

    public void setJobName (String jobName)
    {
        printJob.setJobName(jobName);
    }

    public int print (Graphics g, PageFormat pf, int pageIndex)
            throws PrinterException
    {
        if ( pageIndex >= pageCount ) return 1;
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(
                RenderingHints.KEY_INTERPOLATION,
                RenderingHints.VALUE_INTERPOLATION_BICUBIC
        );
        g2d.setRenderingHint(
                RenderingHints.KEY_TEXT_ANTIALIASING,
                RenderingHints.VALUE_TEXT_ANTIALIAS_ON
        );
        g2d.translate( pf.getImageableX(), pf.getImageableY() );
        int yPosition = 0;
        if (ratio != 1)
        {
            g2d.scale( ratio, ratio );
        }
        if ( pageIndex > 0 )
        {
            yPosition = (int)Math.rint( ( (Double)taillePages.get( pageIndex - 1 ) ).doubleValue()/ratio );
        }
        String details = documentTitle + " - [" + ( pageIndex + 1 ) + "/" + pageCount + "] (" + date.toString() + ") ";
        Font formerPrintFont = g2d.getFont();
        Font newPrintFont = new Font(
                formerPrintFont.getName(),
                formerPrintFont.getStyle(),
                (int)Math.rint(formerPrintFont.getSize()/ratio)
        );
        g2d.setFont(newPrintFont);
        g2d.drawImage(toPrint, 0, yPosition, null);
        g2d.drawString(
                details,
                0,
                g2d.getClip().getBounds().height - (int)Math.rint(5/ratio)
        );
        formerPrintFont = null;
        newPrintFont = null;
        details = null;
        g2d.dispose();
        g2d = null;
        return 0;
    }

    public void print ()
    {
        calculatePages();
        printJob.setPageable(this);
        try
        {
            if ( printJob.printDialog() )
            {
                date = new Timestamp(System.currentTimeMillis());
                toPrint = new BufferedImage(
                        container.getWidth(),
                        container.getHeight(),
                        BufferedImage.TYPE_INT_ARGB
                );
                container.printAll(toPrint.getGraphics());
                Paper paper = pageFormat.getPaper();
                Paper save = pageFormat.getPaper();
                pageFormat.setPaper( paper );
                printJob.setPrintable( this, pageFormat );
                printJob.print();
                pageFormat.setPaper( save );
            }
        }
        catch (PrinterException pe)
        {
            System.out.println( "Error while printing document:\n" + pe.getMessage() );
        }
        finally
        {
            toPrint = null;
            date = null;
        }
    }

    private void calculatePages ()
    {
        double pageHeight = pageFormat.getImageableHeight();
        double pageWidth = pageFormat.getImageableWidth();
        double documentWidth = container.getWidth();
        double documentHeight = container.getHeight();
        double scaleX = pageWidth / documentWidth;
        double scaleY = pageHeight / documentHeight;
        double documentScaledHeight;
        double cumulatedYMove = 0.0D;
        switch(fitMode)
        {
            case FIT_PAGE:
                ratio = Math.min(scaleX, scaleY);
                break;
            case FIT_PAGE_WIDTH:
                ratio = scaleX;
                break;
            case NO_FIT:
                ratio = 1;
                break;
        }
        taillePages = new Vector();
        documentScaledHeight = documentHeight * ratio;
        if ( documentScaledHeight > pageHeight )
        {
            int fullPagesCount = (int)Math.ceil(documentScaledHeight / pageHeight);
            for (int i = 0; i < fullPagesCount; i++)
            {
                cumulatedYMove -= pageHeight;
                taillePages.add( new Double( cumulatedYMove ) );
            }
            pageCount = taillePages.size();
        }
        else
        {
            pageCount = 1;
        }
    }

    public int getNumberOfPages ()
    {
        return pageCount;
    }

    public PageFormat getPageFormat (int pageIndex) throws IndexOutOfBoundsException
    {
        return pageFormat;
    }

    public Printable getPrintable (int pageIndex) throws IndexOutOfBoundsException
    {
        return this;
    }
}

/**
 * <code>FileUI</code> is responsible for handling the file part of the user
 * interface. It will instansiate all menu- and toolbar items, and handle their
 * state. The items open, new, save, and save as are only available in
 * administrator mode. Save is only available when the filename is set, either
 * through open or save as. The icons are from the java ui standard
 * icon-package.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */

public class FileUI {
    UIBit saveBit;
    UIBit closeBit;    

    File file;

    JFileChooser fc;

    FileHandler main;

    JToolBar toolbar;

    /**
     * constructor
     * 
     * @param main
     *            the main class for file control
     * @param toolbar
     *            the tool bar in which icons will be set
     * @param menubar
     *            the menu bar containing the "file" menu
     * @param isAdmin
     *            to know wheather we are in admin mode or not
     * @param mainFrame
     *            the main frame of the application
     */
    public FileUI(FileHandler main, JToolBar toolbar, DTMenuBar menubar,
            boolean isAdmin, final JFrame mainFrame) {
        UIBit saveAsBit;
        UIBit newBit;
        UIBit openBit;
        UIBit printBit;

        ImageIcon saveIcon, saveAsIcon, newIcon, openIcon, closeIcon, printIcon;

        this.main = main;
        this.toolbar = toolbar;

        saveIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Save16.gif"));
        saveAsIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/SaveAs16.gif"));
        newIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/New16.gif"));
        openIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Open16.gif"));
        closeIcon = new ImageIcon(getClass().getResource(
        "/fr/esrf/tangoatk/widget/util/Stop16.gif"));        
        printIcon = new ImageIcon(getClass().getResource(
                "/explorer/ui/printer.gif"));

        saveBit = new UIBit("Save", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                save();
            }
        }, saveIcon);

        saveBit.setEnabled(false);
        saveBit.setAccelerator('S');
        saveBit.setVisible(isAdmin);

        saveAsBit = new UIBit("Save as..", "Save as", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                saveAs();
            }
        }, saveAsIcon);
        saveAsBit.setAccelerator('A');
        saveAsBit.setEnabled(isAdmin);
        saveAsBit.setVisible(isAdmin);
        newBit = new UIBit("New", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                newFile();
            }
        }, newIcon);
        newBit.setAccelerator('N');
        newBit.setEnabled(isAdmin);
        newBit.setVisible(isAdmin);
        openBit = new UIBit("Open...", "Open file", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                open();
            }
        }, openIcon);

        openBit.setAccelerator('O');
        openBit.setEnabled(true);

        closeBit = new UIBit("Close...", "Close file", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                close();
            }
        }, closeIcon);
        closeBit.setAccelerator('X');
        closeBit.setEnabled(false);
        
        printBit = new UIBit("Print..", "Print...", new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                DTPrinter printer = new DTPrinter(mainFrame);
                printer.setOrientation(PageFormat.LANDSCAPE);
                printer.setFitMode(DTPrinter.FIT_PAGE);
                printer.setDocumentTitle(mainFrame.getTitle());
                printer.setJobName(mainFrame.getTitle());
                printer.print();
            }
        }, printIcon);
        menubar.add2FileMenu(openBit.getItem(), 0);
        menubar.add2FileMenu(newBit.getItem(), 1);
        menubar.add2FileMenu(closeBit.getItem(), 2);
        menubar.add2FileMenu(new JSeparator(), 3);
        menubar.add2FileMenu(saveBit.getItem(), 4);
        menubar.add2FileMenu(saveAsBit.getItem(), 5);
        menubar.add2FileMenu(new JSeparator(), 6);
        menubar.add2FileMenu(printBit.getItem(), 7);

        toolbar.add(openBit.getButton());
        toolbar.add(newBit.getButton());
        toolbar.add(closeBit.getButton());
        toolbar.add(saveBit.getButton());
        toolbar.add(saveAsBit.getButton());
        toolbar.add(printBit.getButton());

        menubar.setQuitHandler(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                quit();
            }
        });

        fc = new JFileChooser(new File("."));
        
        fc.addChoosableFileFilter(new FileFilter() {

            public boolean accept(File f) {
                if (f.isDirectory()) {
                    return true;
                }

                String extension = getExtension(f);

                if (extension != null && extension.equals("jdw")) {
                    return true;
                }

                return false;
            }

            public String getDescription() {
                return "jdw files ";
            }

        }); 
        
        fc.addChoosableFileFilter(new FileFilter() {

            public boolean accept(File f) {
                if (f.isDirectory()) {
                    return true;
                }

                String extension = getExtension(f);

                if (extension != null && extension.equals("xml")) {
                    return true;
                }

                return false;
            }

            public String getDescription() {
                return "xml files ";
            }
        });   
    }

    /**
     * <code>getExtension</code> returns the extension of a given file, that
     * is the part after the last `.' in the filename.
     * 
     * @param f
     *            a <code>File</code> value
     * @return a <code>String</code> value
     */
    public String getExtension(File f) {
        String ext = null;
        String s = f.getName();
        int i = s.lastIndexOf('.');

        if (i > 0 && i < s.length() - 1) {
            ext = s.substring(i + 1).toLowerCase();
        }
        return ext;
    }

    /**
     * <code>quit</code> calls its FileHandler <code>quit()</code> method
     */
    public void quit() {
        main.quit();
    }

    /**
     * <code>open</code> shows a file-selection dialog and calls its
     * FileHandler <code>open(file)</code> method.
     *  
     */
    public void open() {
        int returnVal = fc.showOpenDialog(toolbar.getRootPane().getParent());

        if (returnVal == JFileChooser.APPROVE_OPTION) {
            file = fc.getSelectedFile();
            saveBit.setEnabled(true);
            closeBit.setEnabled(true);
            main.open(file);
        }
    }
    
    /**
     * <code>close</code> closes the active file by calling
     * FileHandler <code>close()</code> method.
     *  
     */
    public void close() {
    	file = null;
    	saveBit.setEnabled(false);
    	closeBit.setEnabled(false);
    	main.close();
    }    

    /**
     * <code>newFile</code> calls its FileHandler <code>newFile</code>
     * method.
     */
    public void newFile() {
        main.newFile();
    }

    /**
     * <code>save</code> calls its FileHandler <code>save(file)</code>
     * method.
     */
    public void save() {
        main.save(file);
    }

    /**
     * <code>confirm</code> a dialog which is used to make the user
     * confirm a save to an already existing file.
     * @return a <code>boolean</code> value
     */
    protected boolean confirm() {
        return JOptionPane.showConfirmDialog(null, "The file "
                + file.toString() + " exists, "
                + "do you want to overwrite it?", "Alert",
                JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION;
    }

    /**
     * <code>saveAs</code> shows a file selection dialog and calls
     * its FileHandler <code>save(file)</code> method.
     */
    public void saveAs() {
        int returnVal = fc.showSaveDialog(toolbar.getRootPane().getParent());

        if (returnVal == JFileChooser.APPROVE_OPTION) {
            file = fc.getSelectedFile();

            if (!file.exists() || confirm()) {
                if (getExtension(file) == null) {

                    file = new File(file.getAbsolutePath() + ".xml");
                }
                main.save(file);
                saveBit.setEnabled(true);
            }
        }
    }
}