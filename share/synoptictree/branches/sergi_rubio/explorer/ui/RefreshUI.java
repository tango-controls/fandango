// File:          RefreshUI.java
// Created:       2002-09-18 11:50:43, erik
// By:            <erik@assum.net>
// Time-stamp:    <2002-10-18 11:0:12, erik>
// 
// $Id$
// 
// Description:       

package explorer.ui;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.prefs.Preferences;

import javax.swing.ImageIcon;
import javax.swing.JSeparator;
import javax.swing.JToolBar;

import fr.esrf.tangoatk.widget.attribute.Trend;

/**
 * <code>RefreshUI</code> is responsible for handling the refresh part fo the
 * user interface.
 * 
 * @author <a href="mailto:erik@assum.net">Erik Assum </a>
 * @version $Revision$
 */
public class RefreshUI {
    UIBit startBit;
    UIBit stopBit;
    UIBit refreshBit;
    UIBit intervalBit;
    ImageIcon startIcon;
    ImageIcon stopIcon;
    ImageIcon refreshIcon;
    explorer.ui.Dialog rDialog;
    Preferences prefs;
    RefreshDialog refresh;
    Refresher main;
    Trend globalTrend;

    /**
     * constructor
     * @param main the main class for refresh control
     * @param toolbar the tool bar in which icons will be set
     * @param menubar the menu bar containing the "refresh" menu
     */
    public RefreshUI(Refresher main, JToolBar toolbar, DTMenuBar menubar) {

        globalTrend = null;
        this.main = main;

        refresh = new RefreshDialog(this);
        PreferencesDialog.getInstance().addTop("Refresh interval", refresh);
        stopIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Pause16.gif"));
        startIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Play16.gif"));
        refreshIcon = new ImageIcon(getClass().getResource(
                "/fr/esrf/tangoatk/widget/util/Refresh16.gif"));
        startBit = new UIBit("Start", "Start refresher", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                startRefresher();
            }
        }, startIcon);
        refreshBit = new UIBit("Refresh", "Refresh", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                refresh();
            }
        }, refreshIcon);
        refreshBit.setAccelerator("F5");
        stopBit = new UIBit("Stop", "Stop refresher", new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                stopRefresher();
            }
        }, stopIcon);
        intervalBit = new UIBit("Set refresh interval...",
                new ActionListener() {
                    public void actionPerformed(ActionEvent e) {
                        showRefreshIntervalDialog();
                    }

                });

        menubar.add2RefreshMenu(refreshBit.getItem());
        menubar.add2RefreshMenu(startBit.getItem());
        menubar.add2RefreshMenu(stopBit.getItem());
        menubar.add2RefreshMenu(new JSeparator());
        menubar.add2RefreshMenu(intervalBit.getItem());

        stopBit.setEnabled(false);

        toolbar.add(stopBit.getButton());
        toolbar.add(startBit.getButton());
        toolbar.add(refreshBit.getButton());

    }

    /**
     * <code>showRefreshIntervalDialog</code> shows the refresh interval
     * dialog.
     */
    public void showRefreshIntervalDialog() {
        if (rDialog == null) {
            rDialog = new explorer.ui.Dialog();
            rDialog.setComponent(refresh);
        }

        rDialog.show();
    }

    /**
     * Associates the trend to this ui.
     * This is used for trend synchronization
     * @param trend 21 sept. 2005
     */
    public void setTrend(Trend trend) {
        globalTrend = trend;
    }

    /**
     * To set the "stop" button enabled
     */
    public void enableStopBit() {
        stopBit.setEnabled(true);
    }

    /**
     * To set the "stop" button disabled
     */
    public void disableStopBit() {
        stopBit.setEnabled(false);
    }

    /**
     * To set the "start" and "refresh" buttons enabled
     */
    public void enableStartAndRefreshBit() {
        startBit.setEnabled(true);
        refreshBit.setEnabled(true);
    }

    /**
     * To set the "start" and "refresh" buttons disabled
     */
    public void disableStartAndRefreshBit() {
        startBit.setEnabled(false);
        refreshBit.setEnabled(false);
    }

    /**
     * @return <code>true</code> if "start" button is enabled,
     * <code>false</code> otherwise 
     */
    public boolean isStartBitEnabled() {
        return startBit.isEnabled();
    }

    /**
     * <code>setRefreshInterval</code> calls its Refresher
     * <code>setRefreshInterval</code> method.
     * 
     * @param milliseconds
     *            an <code>int</code> value specifying the interval.
     */
    public void setRefreshInterval(int milliseconds) {
        main.setRefreshInterval(milliseconds);
        if (globalTrend != null && globalTrend.getModel() != null)
            globalTrend.getModel().setRefreshInterval(milliseconds);
    }

    /**
     * <code>getRefreshInterval</code> calls its Refreshers
     * <code>getRefreshInterval</code> method.
     * 
     * @return an <code>int</code> value
     */
    public int getRefreshInterval() {
        return main.getRefreshInterval();
    }

    /**
     * <code>startRefresher</code> calls its Refreshers
     * <code>startRefresher</code> method
     */
    public void startRefresher() {
        stopBit.setEnabled(true);
        if ( globalTrend != null 
             && globalTrend.getModel() != null 
             && !globalTrend.getModel().isRefresherStarted() ){
            globalTrend.getModel().startRefresher();
        }
        if (globalTrend==null || globalTrend.getModel()==null
                 || globalTrend.getModel().isEmpty()){
            startBit.setEnabled(false);
            refreshBit.setEnabled(false);
        }
        main.startRefresher();

    }

    /**
     * <code>refresh</code> calls its Refreshers <code>refresh</code> method
     *  
     */
    public void refresh() {
        main.refresh();
        if (globalTrend != null && globalTrend.getModel() != null
            && !globalTrend.getModel().isRefresherStarted()) {
            globalTrend.getModel().refresh();
        }
    }

    /**
     * <code>stopRefresher</code> calls its Refreshers
     * <code>stopRefresher</code> method.
     *  
     */
    void stopRefresher() {
        startBit.setEnabled(true);
        if (globalTrend != null) {
            if (globalTrend.getModel() != null) {
                globalTrend.getModel().stopRefresher();
            }
            if (globalTrend.getModel() == null
                || globalTrend.getModel().isEmpty()) {
                stopBit.setEnabled(false);
            }
        }
        else {
            stopBit.setEnabled(false);
        }
        refreshBit.setEnabled(true);
        main.stopRefresher();
    }
}