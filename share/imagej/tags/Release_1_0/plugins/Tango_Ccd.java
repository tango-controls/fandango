import ij.measure.Calibration;
import ij.plugin.*;
import ij.*;
import ij.gui.*;
import ij.process.*;
import ij.util.Tools;

import java.awt.*;
import java.awt.image.*;
import java.awt.event.*;
import java.text.NumberFormat;

import fr.esrf.Tango.*;
import fr.esrf.TangoApi.ApiUtil;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.TangoApi.DeviceProxy;

/**
     An ImageJ plugin for Tango devices which implement the Ccd interface.
     Opens a blank window with a default size of 640x480. Adds a panel below 
     the image containing "Read Image" , "Start" and "Stop" buttons and a text
     field for entering exposure values.
*/
public class Tango_Ccd implements PlugIn {

	static long ccd_count=0;
	String ccd_name;
    DeviceProxy ccd_proxy;
    int width = 640;
    int height = 480;
    double exposure;
	Thread live_thread, state_thread;
	boolean live_update = true;
	boolean profile_selected = false;
	ProfilePlot profile_plot = null;
	PlotWindow plot_window = null;
	double [] x;
	double [] y;
	DevState state;
	//Prefs prefs;

    public void run(String arg) {
    	IJ.showStatus("Plugin Tango Ccd started.");
    	IJ.showProgress(0.0);
    	ccd_name = Prefs.getString(".tango.ccd","test/ccd1394/1");
    	ccd_name = IJ.getString("Please enter the tango device name : ",ccd_name);
    	if (ccd_name.equals("")) {
    		return;
    	}
     	IJ.showProgress(50.0);
    	try {
			ccd_proxy = new DeviceProxy(ccd_name);
			ccd_proxy.set_source(DevSource.DEV);
	    	Prefs.set("tango.ccd",ccd_name);
		} catch (DevFailed e) {
			// Auto-generated catch block
			e.printStackTrace();
		}
    	ImagePlus imp = null;
    	ImageProcessor ip = new ShortProcessor(width, height);
    	ip.setColor(Color.red);
    	ip.fill();
    	ccd_count++;
    	imp = new ImagePlus("Tango Ccd " + Long.toString(ccd_count)+" - "+ccd_name, ip);   	
    	CustomCanvas cc = new CustomCanvas(imp);
    	new CustomWindow(imp, cc);
    	IJ.showProgress(1.0);
    }

    class CustomCanvas extends ImageCanvas {
    
        CustomCanvas(ImagePlus imp) {
            super(imp);
        }
    
    } // CustomCanvas inner class
    
    
    class CustomWindow extends ImageWindow implements ActionListener, ItemListener {
    
        private Button update_button, live_button, start_stop_button, profile_button;
        private Button setup_button, stats_button;
        private Label state_label;
        private Checkbox singleshot_checkbox;
       
        CustomWindow(ImagePlus imp, ImageCanvas ic) {
            super(imp, ic);
            addPanel();
        }
    
        void addPanel() {
            Panel panel = new Panel();
            panel.setLayout(new FlowLayout(FlowLayout.RIGHT));
        	try {
				DeviceAttribute attr_exposure = ccd_proxy.read_attribute("state");
				state = attr_exposure.extractState();
			} catch (DevFailed e1) {
				// Auto-generated catch block
				e1.printStackTrace();
				state = DevState.FAULT;
			}
            state_label = new Label("CCD is STATUS");
            panel.add(state_label);
			start_stop_button = new Button("Start Ccd");
            if (state == DevState.OFF) {
            	start_stop_button.setLabel("Start Ccd");
            	state_label.setText("CCD is OFF");
            	state_label.setBackground(Color.white);
            }           
            else if (state == DevState.ON) {
            	start_stop_button.setLabel("Stop Ccd");            	
            	state_label.setText("CCD is ON");
            	state_label.setBackground(Color.green);
            }
            else {
            	start_stop_button.setLabel("Reset Ccd");            	            	
            	state_label.setText("CCD is FAULT");
            	state_label.setBackground(Color.red);
            }
            start_stop_button.addActionListener(this);
            panel.add(start_stop_button);
            live_button = new Button("Start Live Refresh");
            live_button.addActionListener(this);
            panel.add(live_button);
            update_button = new Button("Refresh Once");
            update_button.addActionListener(this);
            panel.add(update_button);
            profile_button = new Button("Profile");
            profile_button.addActionListener(this);
            panel.add(profile_button);
            stats_button = new Button("Stats");
            stats_button.addActionListener(this);
            panel.add(stats_button);
            setup_button = new Button("Setup");
            setup_button.addActionListener(this);
            panel.add(setup_button);
            singleshot_checkbox = new Checkbox("Singleshot");
            singleshot_checkbox.addItemListener(this);
            panel.add(singleshot_checkbox);
            add(panel);
            pack();
			state_thread=new StateThread();
			state_thread.start();       
            Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();
            Point loc = getLocation();
            Dimension size = getSize();
            if (loc.y+size.height>screen.height)
                getCanvas().zoomOut(0, 0);
         }

        class StateThread extends Thread {
			
        	public void run() {
        		while (true) {
        			try {
        				state = ccd_proxy.state();
        			} catch (DevFailed e1) {
        				// Auto-generated catch block
        				//e1.printStackTrace();
        				state = DevState.FAULT;
        			}
        			if (state == DevState.OFF) {
        				start_stop_button.setLabel("Start Ccd");
        				start_stop_button.setBackground(Color.white);
        				state_label.setText("CCD is OFF");
        				state_label.setBackground(Color.white);
        			}
        			else if (state == DevState.ON) {
        				start_stop_button.setLabel("Stop Ccd");
        				start_stop_button.setBackground(Color.orange);
        				state_label.setText("CCD is ON");
        				state_label.setBackground(Color.green);
        			}
        			else {
        				start_stop_button.setLabel("Reset Ccd");            	            	
        				start_stop_button.setBackground(Color.red);
        				state_label.setText("CCD is FAULT");
        				state_label.setBackground(Color.red);
        			}
        			try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						// Auto-generated catch block
						//e.printStackTrace();
					}
        		}
        	}
        	
        	}


        class LiveThread extends Thread {
			
        	public void run() {
				//System.out.println("LiveThread(): start running ...");
				short image[] = null;
     			DeviceAttribute attr;
     			long start_time = System.currentTimeMillis();
     			long n_images=0;
     			double image_rate;
     			NumberFormat nf = NumberFormat.getInstance();
     			nf.setMaximumFractionDigits(1);
     			nf.setMinimumFractionDigits(1);
     			// start off by setting the nframes to zero (for continuous update)
				try {
					DeviceAttribute attr_frames = new DeviceAttribute("frames",0);
					ccd_proxy.write_attribute(attr_frames);
					singleshot_checkbox.setState(false);
					ccd_proxy.command_inout("start");
				} catch (DevFailed e) {
					// Auto-generated catch block
					//e.printStackTrace();
				}

				//live_thread.setPriority(Thread.MIN_PRIORITY);
				while(live_update) {
					try {
						// update image and rate
						attr = ccd_proxy.read_attribute("image");
						image = attr.extractShortArray();
						imp.getProcessor().setPixels(image);
						n_images++;
						image_rate = (double)n_images/((double)(System.currentTimeMillis()-start_time)/1000.0);
						imp.getProcessor().drawString(nf.format(image_rate)+" fps", 20, 20);
						imp.updateAndDraw();
						// update live profile
						if (profile_selected) {							
							profile_plot = new ProfilePlot(imp);
							y = profile_plot.getProfile();
							if (y != null) {
								x = new double[y.length];
								for (int i=0; i<x.length; i++)
									x[i] = i;
								Plot plot = new Plot("profile", "X", "Y", x, y);
								double ymin = ProfilePlot.getFixedMin();
								double ymax= ProfilePlot.getFixedMax();
								if (!(ymin==0.0 && ymax==0.0)) {
									double[] a = Tools.getMinMax(x);
									double xmin=a[0]; double xmax=a[1];
									plot.setLimits(xmin, xmax, ymin, ymax);
								}
								if (plot_window ==null)
									plot_window = plot.show();
								else
									plot_window.drawPlot(plot);
							}
							else
							{
								profile_selected = false;
							}

	        			}

					} catch (DevFailed e) {
						// Auto-generated catch block
						e.printStackTrace();
					}
					//Thread.yield();
				}
				try {
					DeviceAttribute attr_frames = new DeviceAttribute("frames",1);
					ccd_proxy.write_attribute(attr_frames);
					singleshot_checkbox.setState(true);
					ccd_proxy.command_inout("stop");
    				update_button.setEnabled(true);
				} catch (DevFailed e) {
					// Auto-generated catch block
					//e.printStackTrace();
				}
			}
        	
        }
        public void actionPerformed(ActionEvent e) {
        	try {
        		short image[];
     			DeviceAttribute attr;
        		Object b = e.getSource();
        		if (b==live_button) {
        			if (live_button.getLabel().indexOf("Start") != -1) {
        				live_update = true;
        				live_button.setLabel("Stop Live Refresh");
        				live_thread=new LiveThread();
        				live_button.setBackground(Color.orange);
        				update_button.setEnabled(false);
        				live_thread.start();
         			}
        			else {
        				live_update = false;;
         				live_thread = null;
        				live_button.setLabel("Start Live Refresh");
        				live_button.setBackground(Color.white);
        			}
        		} else if (b==update_button) {
        			DevState update_state;
        			update_button.setBackground(Color.orange);
					ccd_proxy.command_inout("start");
       				update_state = ccd_proxy.state();
    				while (update_state == DevState.ON) {
    					update_state = ccd_proxy.state();
     				}
        			ccd_proxy.command_inout("stop");
        			attr = ccd_proxy.read_attribute("width");
    				int new_width = attr.extractLong();
    				attr = ccd_proxy.read_attribute("height");
    				int new_height = attr.extractLong();
    				if (new_width != 0 && new_height != 0 && (new_width != width || new_height != height))
    				{
	    				width = new_width;
	    				height = new_height;
	    				ImageProcessor new_ip = imp.getProcessor().resize(width, height);
	    				imp.setProcessor(null, new_ip);
    				}
        			attr = ccd_proxy.read_attribute("image");
        			image = attr.extractShortArray();
        			imp.getProcessor().setPixels(image);
        			imp.updateAndDraw();
        			update_button.setBackground(Color.white);
        		} else if (b==start_stop_button) {
        			if (start_stop_button.getLabel().indexOf("Start") != -1) {
            			ccd_proxy.command_inout("start");
            			start_stop_button.setLabel("Stop Ccd");
        				start_stop_button.setBackground(Color.orange);
        			}
        			else {
            			ccd_proxy.command_inout("stop");        			        				
            			start_stop_button.setLabel("Start Ccd");
        				start_stop_button.setBackground(Color.white);
        			}
        		}
        		else if (b==profile_button) {
        			profile_plot = new ProfilePlot(imp);
        			y = profile_plot.getProfile();
        			if (y != null) {
        				x = new double[y.length];
        				for (int i=0; i<x.length; i++)
        					x[i] = i;
        				Plot plot = new Plot("profile", "X", "Y", x, y);
        				double ymin = ProfilePlot.getFixedMin();
        				double ymax= ProfilePlot.getFixedMax();
        				if (!(ymin==0.0 && ymax==0.0)) {
        					double[] a = Tools.getMinMax(x);
        					double xmin=a[0]; double xmax=a[1];
        					plot.setLimits(xmin, xmax, ymin, ymax);
        				}
        				if (plot_window ==null)
        					plot_window = plot.show();
        				else
        					plot_window.drawPlot(plot);
        				profile_selected = true;
        			}
        		}
        		else if (b==setup_button) {
        			IJ.runPlugIn("Tango_Ccd_Setup", ccd_name);
        		}
        	} catch (DevFailed e1) {
        	}     	       
        }

		public void itemStateChanged(ItemEvent e) {
			Object c = e.getSource();
			int frames;
			if (c==singleshot_checkbox) {
				if (singleshot_checkbox.getState())
				{
					frames = 1;
				}
				else
				{
					frames = 0;
				}
				try {
					DeviceAttribute attr_frames = new DeviceAttribute("frames",frames);
					ccd_proxy.write_attribute(attr_frames);
					
				} catch (DevFailed ef) {
					// Auto-generated catch block
					//ef.printStackTrace();
				}
			}
		}
        
    } // CustomWindow inner class

} // Panel_Window class