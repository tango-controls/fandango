package fr.esrf.tangoatk.widget.attribute;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.File;
import java.io.FileWriter;
import java.util.Vector;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JToolBar;
import javax.swing.filechooser.FileFilter;

import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IAttributeStateListener;
import fr.esrf.tangoatk.core.IErrorListener;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;
import fr.esrf.tangoatk.widget.util.chart.CfFileReader;
import fr.esrf.tangoatk.widget.util.chart.JLChart;
import fr.esrf.tangoatk.widget.util.chart.JLDataView;
import fr.esrf.tangoatk.widget.util.chart.OFormat;

public class NumberSpectrumTrendViewer extends JPanel implements ISpectrumListener, IAttributeStateListener, IErrorListener, ActionListener
{
    protected INumberSpectrum model;
    protected JLabel nameLabel;
    protected final static String DEFAULT_NAME = "No Attribute";
    protected AttributePolledList attList;
    protected Vector<JLDataView> views;
    protected JLChart chart;

    protected JToolBar theToolBar;
    protected JButton optionButton;
    protected JButton stopButton;
    protected JButton startButton;
    protected JButton loadButton;
    protected JButton saveButton;
    protected JButton zoomButton;
    protected JButton timeButton;
    protected JButton resetButton;
    protected JPanel innerPanel;

    protected String lastConfig = "";

    protected final static Color[] defaultColor = { 
            Color.red, Color.blue, Color.cyan, Color.green, 
            Color.magenta, Color.orange, Color.pink,
            Color.yellow, Color.black, Color.white 
    };

    protected final static int [] defaultMarkerStyle = {
            JLDataView.MARKER_BOX, JLDataView.MARKER_CIRCLE, 
            JLDataView.MARKER_CROSS, JLDataView.MARKER_DIAMOND,
            JLDataView.MARKER_DOT, JLDataView.MARKER_HORIZ_LINE,
            JLDataView.MARKER_SQUARE, JLDataView.MARKER_STAR,
            JLDataView.MARKER_TRIANGLE, JLDataView.MARKER_VERT_LINE
    };

    public NumberSpectrumTrendViewer ()
    {
        super();
        initComponents();
        addComponents();
    }

    public void setModel(String attributeName)
    {
        if (attributeName == null || "".equals(attributeName.trim()))
        {
            setModel((INumberSpectrum)null);
            return;
        }
        attList.stopRefresher();
        attList.clear();
        chart.getY1Axis().clearDataView();
        views.clear();
        if (model != null)
        {
            model.removeSpectrumListener(this);
        }
        try
        {
            model = (INumberSpectrum) attList.add(attributeName);
            model.addSpectrumListener(this);
            attList.add(model);
            attList.startRefresher();

            String quality = model.getState();
            nameLabel.setText(model.getName());
            nameLabel.setBackground(ATKConstant.getColor4Quality(quality));
            nameLabel.setToolTipText(quality);
            nameLabel.repaint();
            quality = null;
        }
        catch (Exception e)
        {
            model = null;
            nameLabel.setText(DEFAULT_NAME);
            nameLabel.setToolTipText(DEFAULT_NAME);
            nameLabel.setBackground(ATKConstant.getColor4Quality(IAttribute.UNKNOWN));
            JOptionPane.showMessageDialog(this, "Failed to set " + attributeName + " as model", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public void setModel(INumberSpectrum attribute)
    {
        attList.stopRefresher();
        attList.clear();
        chart.getY1Axis().clearDataView();
        views.clear();
        if (model != null)
        {
            model.removeSpectrumListener(this);
            model.removeStateListener(this);
            model.removeErrorListener(this);
        }
        model = attribute;
        if (model == null)
        {
            nameLabel.setText(DEFAULT_NAME);
            nameLabel.setBackground(ATKConstant.getColor4Quality(IAttribute.UNKNOWN));
            nameLabel.setToolTipText(DEFAULT_NAME);
            nameLabel.repaint();
            chart.repaint();
            return;
        }
        model.addSpectrumListener(this);
        model.addStateListener(this);
        model.addErrorListener(this);
        attList.add(model);
        attList.startRefresher();

        String quality = model.getState();
        nameLabel.setText(model.getName());
        nameLabel.setBackground(ATKConstant.getColor4Quality(quality));
        nameLabel.setToolTipText(quality);
        nameLabel.repaint();
        quality = null;
    }

    public void clearModel()
    {
        setModel((INumberSpectrum)null);
    }
    public void spectrumChange (NumberSpectrumEvent e)
    {
        for (int i = 0; i < e.getValue().length; i++)
        {
            JLDataView data;
            if (i < views.size())
            {
                data = views.get(i);
                data.add(e.getTimeStamp(), e.getValue()[i]);
                chart.garbageData(data);
            }
            else
            {
                data = new JLDataView();
                data.add(e.getTimeStamp(), e.getValue()[i]);
                Color drawColor = defaultColor [ i % defaultColor.length ];
                int markerStyle = defaultMarkerStyle [ (i / defaultColor.length) % defaultMarkerStyle.length ];
                data.setMarkerSize(3);
                data.setViewType(JLDataView.TYPE_LINE);
                data.setColor(drawColor);
                data.setMarker(markerStyle);
                data.setMarkerColor(drawColor);
                data.setStyle(JLDataView.STYLE_SOLID);
                chart.getY1Axis().addDataView(data);
                views.add(data);
            }
            if ( i < ((INumberSpectrum)e.getSource()).getXDimension() )
            {
                data.setLineWidth(1);
                data.setName(Integer.toString(i));
            }
            else
            {
                data.setLineWidth(2);
                data.setName( (i-((INumberSpectrum)e.getSource()).getXDimension()) + "(write)" );
            }
            data.setUnit( ( (INumberSpectrum)e.getSource() ).getUnit() );
            data = null;
        }

        chart.repaint();

        String quality = ((INumberSpectrum)e.getSource()).getState();
        nameLabel.setBackground(ATKConstant.getColor4Quality(quality));
        nameLabel.setToolTipText(quality);
        nameLabel.repaint();
        quality = null;
    }

    public void stateChange (AttributeStateEvent e)
    {
        String quality = ((INumberSpectrum)e.getSource()).getState();
        nameLabel.setBackground(ATKConstant.getColor4Quality(quality));
        nameLabel.setToolTipText(quality);
        nameLabel.repaint();
        quality = null;
    }

    public void errorChange (ErrorEvent evt)
    {
        for (int i = 0; i < views.size(); i++)
        {
            JLDataView data = views.get(i);
            data.add(evt.getTimeStamp(), Double.NaN);
            chart.garbageData(data);
        }
        chart.repaint();

        String quality = ((INumberSpectrum)evt.getSource()).getState();
        nameLabel.setBackground(ATKConstant.getColor4Quality(quality));
        nameLabel.setToolTipText(quality);
        nameLabel.repaint();
        quality = null;
    }

    public void setRefreshInterval(int refreshinterval)
    {
        attList.setRefreshInterval(refreshinterval);
    }

    public int getRefreshInterval()
    {
        return attList.getRefreshInterval();
    }

    public void actionPerformed (ActionEvent e)
    {
        Object o = e.getSource();
        if (o == optionButton) {
          chart.showOptionDialog();
        } else if (o == stopButton) {
          attList.stopRefresher();
        } else if (o == startButton) {
          attList.startRefresher();
        } else if (o == loadButton) {
          loadButtonActionPerformed();
        } else if (o == saveButton) {
          saveButtonActionPerformed();
        } else if (o == zoomButton) {
          if (!chart.isZoomed())
              chart.enterZoom();
          else
              chart.exitZoom();
        } else if (o == timeButton) {
          setRefreshInterval();
        }
        else if (o == resetButton) {
            resetTrend();
        }
    }

    protected void initComponents()
    {
        nameLabel = new JLabel(DEFAULT_NAME, JLabel.CENTER);
        nameLabel.setBackground(ATKConstant.getColor4Quality(IAttribute.UNKNOWN));
        nameLabel.setToolTipText(DEFAULT_NAME);
        nameLabel.setOpaque(true);
        nameLabel.setMaximumSize(new Dimension(Integer.MAX_VALUE, nameLabel.getPreferredSize().height));
        attList = new AttributePolledList();
        chart = new JLChart();
        chart.getY1Axis().setAutoScale(true);
        chart.setDisplayDuration(300000.0); // 5min
        chart.setLabelVisible(false);
        views = new Vector<JLDataView>();

        theToolBar = new JToolBar();
        theToolBar.setFloatable(true);

        loadButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_load.gif")));
        loadButton.setToolTipText("Load configuration");
        saveButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_save.gif")));
        saveButton.setToolTipText("Save configuration");
        optionButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_settings.gif")));
        optionButton.setToolTipText("Global settings");
        zoomButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_zoom.gif")));
        zoomButton.setToolTipText("Zoom");
        startButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_start.gif")));
        startButton.setToolTipText("Start monitoring");
        stopButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_stop.gif")));
        stopButton.setToolTipText("Stop monitoring");
        timeButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_time.gif")));
        timeButton.setToolTipText("Set refresh interval");
        resetButton = new JButton(new ImageIcon(getClass().getResource("/fr/esrf/tangoatk/widget/attribute/trend_reset.gif")));
        resetButton.setToolTipText("Reset viewer");

        loadButton.addActionListener(this);
        saveButton.addActionListener(this);
        optionButton.addActionListener(this);
        zoomButton.addActionListener(this);
        stopButton.addActionListener(this);
        startButton.addActionListener(this);
        timeButton.addActionListener(this);
        resetButton.addActionListener(this);

        theToolBar.add(loadButton);
        theToolBar.add(saveButton);
        theToolBar.add(optionButton);
        theToolBar.add(zoomButton);
        theToolBar.add(startButton);
        theToolBar.add(stopButton);
        theToolBar.add(timeButton);
        theToolBar.add(resetButton);

    }

    protected void addComponents()
    {
        innerPanel = new JPanel();
        innerPanel.setLayout(new BorderLayout());

        setLayout(new BorderLayout());
        add(theToolBar, BorderLayout.NORTH);
        innerPanel.add(nameLabel, BorderLayout.NORTH);
        innerPanel.add(chart, BorderLayout.CENTER);
        add(innerPanel, BorderLayout.CENTER);
    }

    protected void loadButtonActionPerformed ()
    {
        int ok = JOptionPane.YES_OPTION;
        JFileChooser chooser = new JFileChooser();
        chooser.addChoosableFileFilter( new FileFilter() {
            public boolean accept (File f)
            {
                if ( f.isDirectory() )
                {
                    return true;
                }
                String extension = getExtension( f );
                if ( extension != null && extension.equals( "txt" ) ) return true;
                return false;
            }

            public String getDescription ()
            {
                return "text files ";
            }
        } );
        if ( lastConfig.length() > 0 ) chooser.setSelectedFile( new File(
                lastConfig ) );
        int returnVal = chooser.showOpenDialog( this );
        if ( returnVal == JFileChooser.APPROVE_OPTION )
        {
            File f = chooser.getSelectedFile();
            if ( f != null )
            {
                if ( ok == JOptionPane.YES_OPTION )
                {
                    String err = loadSetting( f.getAbsolutePath() );
                    if ( err.length() > 0 )
                    {
                        JOptionPane.showMessageDialog( this, err,
                                "Errors reading " + f.getName(),
                                JOptionPane.ERROR_MESSAGE );
                    }
                }
            }
        }

    }

    /**
     * <code>getExtension</code> returns the extension of a given file,
     * that is the part after the last `.' in the filename.
     *
     * @param f a <code>File</code> value
     * @return a <code>String</code> value
     */
    protected String getExtension(File f) {
        String ext = null;
        String s = f.getName();
        int i = s.lastIndexOf('.');
        if (i > 0 &&  i < s.length() - 1) {
            ext = s.substring(i+1).toLowerCase();
        }
        return ext;
    }

    /**
     *  Load graph settings.
     * @param filename file to be read
     * @return An error string or An empty string when succes
     */
    public String loadSetting(String filename) {

      CfFileReader f = new CfFileReader();

      // Read and browse the file
      if (!f.readFile(filename)) {
        return "Failed to read " + filename;
      }
      lastConfig = filename;

      return applySettings(f);
    }

    protected String applySettings (CfFileReader f)
    {
        String errBuff = "";
        Vector p;

        // Get model
        p = f.getParam( "model" );
        if (p == null)
        {
            clearModel();
        }
        else
        {
            setModel(p.get(0).toString());
        }

        //Get Refresh Interval
        p = f.getParam("refresh_time");
        attList.stopRefresher();
        if (p != null)
          attList.setRefreshInterval(OFormat.getInt(p.get(0).toString()));
        else
          attList.setRefreshInterval(1000);
        attList.startRefresher();

        chart.setMaxDisplayDuration( Double.POSITIVE_INFINITY );
        chart.setDisplayDuration( Double.POSITIVE_INFINITY );
        chart.applyConfiguration(f);
        chart.getXAxis().applyConfiguration("x",f);
        chart.getY1Axis().applyConfiguration("y1", f);
        chart.getY2Axis().applyConfiguration("y2", f);

        return errBuff;
    }

    /** returns the configuration as string.
      * @see #setSetting
      */
    public String getSettings() {

      String to_write = "";

      // General settings
      to_write += chart.getConfiguration();

      if (attList != null) to_write += "refresh_time:" + attList.getRefreshInterval() + "\n";

      // model
      if (model != null)
      {
          to_write += "model:\'" + model.getName() + "\'\n";
      }

      // Axis
      to_write += chart.getXAxis().getConfiguration("x");
      to_write += chart.getY1Axis().getConfiguration("y1");
      to_write += chart.getY2Axis().getConfiguration("y2");

      return to_write;
    }

    private void saveButtonActionPerformed ()
    {
        int ok = JOptionPane.YES_OPTION;
        JFileChooser chooser = new JFileChooser( "." );
        chooser.addChoosableFileFilter( new FileFilter() {
            public boolean accept (File f)
            {
                if ( f.isDirectory() )
                {
                    return true;
                }
                String extension = getExtension( f );
                if ( extension != null && extension.equals( "txt" ) ) return true;
                return false;
            }

            public String getDescription ()
            {
                return "text files ";
            }
        } );
        if ( lastConfig.length() > 0 ) chooser.setSelectedFile( new File(
                lastConfig ) );
        int returnVal = chooser.showSaveDialog( this );
        if ( returnVal == JFileChooser.APPROVE_OPTION )
        {
            File f = chooser.getSelectedFile();
            if ( f != null )
            {
                if ( getExtension( f ) == null )
                {
                    f = new File( f.getAbsolutePath() + ".txt" );
                }
                if ( f.exists() ) 
                    ok = JOptionPane.showConfirmDialog( this,
                        "Do you want to overwrite " + f.getName() + " ?",
                        "Confirm overwrite", JOptionPane.YES_NO_OPTION );
                if ( ok == JOptionPane.YES_OPTION )
                {
                    saveSetting( f.getAbsolutePath() );
                }
            }
        }
    }

    /**
     * Save settings.
     * 
     * @param filename
     *            file to be saved.
     */
    public void saveSetting (String filename)
    {
        try
        {
            FileWriter f = new FileWriter( filename );
            String s = getSettings();
            f.write( s, 0, s.length() );
            f.close();
            lastConfig = filename;
        }
        catch (Exception e)
        {
            JOptionPane.showMessageDialog( this, "Failed to write "
                    + filename, "Error", JOptionPane.ERROR_MESSAGE );
        }
    }

    protected void setRefreshInterval ()
    {
        int old_it = attList.getRefreshInterval();
        String i = JOptionPane.showInputDialog( this,
                "Enter refresh interval (ms)", new Integer( old_it ) );
        if ( i != null )
        {
            try
            {
                int it = Integer.parseInt( i );
                attList.setRefreshInterval( it );
            }
            catch (NumberFormatException e)
            {
                JOptionPane.showMessageDialog( this, "Invalid number !",
                        "Error", JOptionPane.ERROR_MESSAGE );
            }
        }
    }

    public void resetTrend () {
        if (views != null) {
            for (int i = 0; i < views.size(); i++) {
                JLDataView view = views.get(i);
                if (view != null) {
                    view.reset();
                }
            }
            chart.repaint();
        }
    }

    public static void main(String[] args)
    {
        String attributeName;
        if (args.length > 0)
        {
            attributeName = args[0];
        }
        else
        {
            attributeName = "tango/tangotest/1/float_spectrum_ro";
        }
        final NumberSpectrumTrendViewer viewer = new NumberSpectrumTrendViewer();
        viewer.setRefreshInterval(1000);
        JFrame f = new JFrame("NumberSpectrumTrendViewer - close once to clear model, twice to exit");
        f.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        f.addWindowListener(
                new WindowAdapter()
                {
                    int closecount = 0;
                    public void windowClosing (WindowEvent e)
                    {
                        if(closecount++ == 1)
                        {
                            System.exit(0);
                        }
                        else
                        {
                            viewer.clearModel();
                        }
                    }
                }
        );
        f.getContentPane().add(viewer);
        viewer.setModel(attributeName);
        f.setSize(800,600);
        f.setVisible(true);
    }
}
