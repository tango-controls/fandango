import ij.measure.Calibration;
import ij.plugin.*;
import ij.plugin.frame.PlugInFrame;
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
     Opens a control window for setting up the Ccd e.g. exposure etc.
*/
public class Tango_Ccd_Setup extends PlugInFrame implements ActionListener {

	static long ccd_count=0;
	String ccd_name;
	DeviceProxy ccd_proxy;
	DevState state;
	double exposure;
	int width;
	int height;
	short depth;
	int frames;
	String mode;
	short format;
	Label state_label, width_label, height_label, depth_label;
	Label width_read_label, height_read_text, depth_read_label;
	Label exposure_read_label, frames_read_label, mode_read_label;
	Label format_read_label, file_directory_read_label, file_prefix_read_label;
	Label file_number_read_label, file_suffix_read_label;
	TextField exposure_write_text, frames_write_text, mode_write_text;
	TextField format_write_text, file_directory_write_text, file_prefix_write_text;
	TextField file_number_write_text, file_suffix_write_text;
	Button write_file_button;
	String file_params[];
	Thread update_thread;
	
	Panel panel;
	int previousID;
	static Frame instance;
	
	public Tango_Ccd_Setup() {
		super("Tango Ccd Setup");
		IJ.showStatus("Plugin Tango Ccd Setup started.");
    	ccd_name = Prefs.getString(".tango.ccd","test/ccd1394/1");
		ccd_name = IJ.getString("Please enter the tango device name : ",ccd_name);
    	if (ccd_name.equals("")) {
    		return;
    	}
     	IJ.showProgress(50.0);
    	try {
			ccd_proxy = new DeviceProxy(ccd_name);
	    	Prefs.set("tango.ccd",ccd_name);
		} catch (DevFailed e) {
			// Auto-generated catch block
			e.printStackTrace();
		}
		ccd_count++;
		
//		if (instance!=null) {
//			instance.toFront();
//			return;
//		}
		instance = this;
		IJ.register(Tango_Ccd_Setup.class);
		readAttributes();
		setLayout(new FlowLayout());
		panel = new Panel();
		panel.setLayout(new GridLayout(11, 3, 1, 1));
		Label device_label = new Label("device name =");
		panel.add(device_label);
		Label ccd_name_label = new Label(ccd_name);
		panel.add(ccd_name_label);
		state_label = new Label("STATE");
		updateState();
		panel.add(state_label);
		width_label = new Label("width = "+Integer.toString(width));
		panel.add(width_label);
		height_label = new Label("height = "+Integer.toString(height));
		panel.add(height_label);
		depth_label = new Label("depth = "+Integer.toString(depth));
		panel.add(depth_label);
		Label exposure_label = new Label("exposure =");
		panel.add(exposure_label);
		exposure_read_label = new Label(Double.toString(exposure));
		panel.add(exposure_read_label);
		exposure_write_text = new TextField(Double.toString(exposure));
		exposure_write_text.addActionListener(this);
		panel.add(exposure_write_text);
		Label frames_label = new Label("frames =");
		panel.add(frames_label);
		frames_read_label = new Label(Integer.toString(frames));
		panel.add(frames_read_label);
		frames_write_text = new TextField(Integer.toString(frames));
		frames_write_text.addActionListener(this);
		panel.add(frames_write_text);
		Label mode_label = new Label("mode =");
		panel.add(mode_label);
		mode_read_label = new Label(mode);
		panel.add(mode_read_label);
		mode_write_text = new TextField(mode);
		mode_write_text.addActionListener(this);
		panel.add(mode_write_text);
		Label format_label = new Label("format =");
		panel.add(format_label);
		format_read_label = new Label(Short.toString(format));
		panel.add(format_read_label);
		format_write_text = new TextField(Short.toString(format));
		format_write_text.addActionListener(this);
		panel.add(format_write_text);
		Label file_directory_label = new Label("file directory =");
		panel.add(file_directory_label);
		file_directory_read_label = new Label(file_params[0]);
		panel.add(file_directory_read_label);
		file_directory_write_text = new TextField(file_params[0]);
		file_directory_write_text.addActionListener(this);
		panel.add(file_directory_write_text);
		Label file_prefix_label = new Label("file prefix =");
		panel.add(file_prefix_label);
		file_prefix_read_label = new Label(file_params[1]);
		panel.add(file_prefix_read_label);
		file_prefix_write_text = new TextField(file_params[1]);
		file_prefix_write_text.addActionListener(this);
		panel.add(file_prefix_write_text);
		Label file_number_label = new Label("file number =");
		panel.add(file_number_label);
		file_number_read_label = new Label(file_params[2]);
		panel.add(file_number_read_label);
		file_number_write_text = new TextField(file_params[2]);
		file_number_write_text.addActionListener(this);
		panel.add(file_number_write_text);
		Label file_suffix_label = new Label("file suffix =");
		panel.add(file_suffix_label);
		file_suffix_read_label = new Label(file_params[3]);
		panel.add(file_suffix_read_label);
		file_suffix_write_text = new TextField(file_params[3]);
		file_suffix_write_text.addActionListener(this);
		panel.add(file_suffix_write_text);
		write_file_button = new Button("Write File");
		write_file_button.addActionListener(this);
		panel.add(write_file_button);
		panel.validate();
		add(panel);			
		pack();
		update_thread=new UpdateThread();
		update_thread.start();
		//GUI.center(this);
		show();
	}
	
	void readAttributes() {
		DeviceAttribute attr;
		try {
			attr = ccd_proxy.read_attribute("state");
			state = attr.extractState();
			attr = ccd_proxy.read_attribute("width");
			width = attr.extractLong();
			attr = ccd_proxy.read_attribute("height");
			height = attr.extractLong();
			attr = ccd_proxy.read_attribute("depth");
			depth = attr.extractShort();
			attr = ccd_proxy.read_attribute("exposure");
			exposure = attr.extractDouble();
			attr = ccd_proxy.read_attribute("mode");
			mode = attr.extractString();
			attr = ccd_proxy.read_attribute("format");
			format = attr.extractShort();
			attr = ccd_proxy.read_attribute("frames");
			frames = attr.extractLong();
			attr = ccd_proxy.read_attribute("fileparams");
			file_params = attr.extractStringArray();
		} catch (DevFailed e1) {
			// Auto-generated catch block
			e1.printStackTrace();
			state = DevState.FAULT;
		}	
	}

	void updateState() {
		if (state == DevState.ON) {
			state_label.setText("ON");
			state_label.setBackground(Color.green);
		}
		else if (state == DevState.OFF) {
			state_label.setText("OFF");
			state_label.setBackground(Color.white);
		}
		else if (state == DevState.FAULT) {
			state_label.setText("FAULT");
			state_label.setBackground(Color.red);
		}
		else {
			state_label.setText("UNKNOWN");
			state_label.setBackground(Color.gray);
		}
	}
	
    class UpdateThread extends Thread {
		
    	public void run() {
    		while (true) {
    			readAttributes();
    			updateState();
    			width_label.setText("width = "+Integer.toString(width));
    			height_label.setText("height = "+Integer.toString(height));
    			depth_label.setText("depth = "+Integer.toString(depth));
    			exposure_read_label.setText(Double.toString(exposure));
    			mode_read_label.setText(mode);
    			format_read_label.setText(Short.toString(format));
    			frames_read_label.setText(Integer.toString(frames));
    			file_directory_read_label.setText(file_params[0]);
    			file_prefix_read_label.setText(file_params[1]);
    			file_number_read_label.setText(file_params[2]);
    			file_suffix_read_label.setText(file_params[3]);
    			panel.validate();
    			try {
					Thread.sleep(1000);
				} catch (InterruptedException e) {
					// Auto-generated catch block
					e.printStackTrace();
				}
    		}
    	}
    	
    	}

	
	public void actionPerformed(ActionEvent e) {
		Object b = e.getSource();
		DeviceAttribute attr;
		try {
			if (b==exposure_write_text) {
				double exposure_write = Double.parseDouble(exposure_write_text.getText());
				attr = new DeviceAttribute("exposure");
				attr.insert(exposure_write);
				ccd_proxy.write_attribute(attr);
			}
			else if (b==mode_write_text) {
				attr = new DeviceAttribute("mode");
				attr.insert(mode_write_text.getText());
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==frames_write_text) {
				int frames_write = Integer.parseInt(frames_write_text.getText());
				attr = new DeviceAttribute("frames");
				attr.insert(frames_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==format_write_text) {
				short format_write = Short.parseShort(format_write_text.getText());
				attr = new DeviceAttribute("format");
				attr.insert(format_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==file_directory_write_text) {
				String file_params_write[] = new String[4];
				file_params_write[0] = file_directory_write_text.getText();
				file_params_write[1] = file_params[1];
				file_params_write[2] = file_params[2];
				file_params_write[3] = file_params[3];
				attr = new DeviceAttribute("fileparams");
				attr.insert(file_params_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==file_prefix_write_text) {
				String file_params_write[] = new String[4];
				file_params_write[0] = file_params[0];
				file_params_write[1] = file_prefix_write_text.getText();
				file_params_write[2] = file_params[2];
				file_params_write[3] = file_params[3];
				attr = new DeviceAttribute("fileparams");
				attr.insert(file_params_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==file_number_write_text) {
				String file_params_write[] = new String[4];
				file_params_write[0] = file_params[0];
				file_params_write[1] = file_params[1];
				file_params_write[2] = file_number_write_text.getText();
				file_params_write[3] = file_params[3];
				attr = new DeviceAttribute("fileparams");
				attr.insert(file_params_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==file_suffix_write_text) {
				String file_params_write[] = new String[4];
				file_params_write[0] = file_params[0];
				file_params_write[1] = file_params[1];
				file_params_write[2] = file_params[2];
				file_params_write[3] = file_prefix_write_text.getText();
				attr = new DeviceAttribute("fileparams");
				attr.insert(file_params_write);
				ccd_proxy.write_attribute(attr);	
			}
			else if (b==write_file_button) {
				ccd_proxy.command_inout("WriteFile");
			}
		} catch (DevFailed e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}


		
	}
	
}