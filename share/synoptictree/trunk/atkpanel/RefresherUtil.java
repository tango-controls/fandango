package atkpanel;

import java.awt.Component;
import fr.esrf.tangoatk.core.*;

public class RefresherUtil {

	public static void activateRefresh(Component comp)
	{
		if(comp instanceof ImagePanel)
		{
			ImagePanel imgComp = (ImagePanel)comp;
			imgComp.getModel().setSkippingRefresh(false);
		}
		if(comp instanceof SpectrumPanel)
		{
			SpectrumPanel imgComp = (SpectrumPanel)comp;
			imgComp.getModel().setSkippingRefresh(false);
		}
		if(comp instanceof StringSpectrumPanel)
		{
			StringSpectrumPanel imgComp = (StringSpectrumPanel)comp;
			imgComp.getModel().setSkippingRefresh(false);
		}		
	}
	
	public static void refresh(Component comp)
	{
		if(comp instanceof ImagePanel)
		{
			ImagePanel    imgComp = (ImagePanel)comp;
			INumberImage  ini = imgComp.getModel();
			refreshIfNeeded(ini);
		}
		if(comp instanceof SpectrumPanel)
		{
			SpectrumPanel    spectComp = (SpectrumPanel)comp;
			INumberSpectrum  ins = spectComp.getModel();
			refreshIfNeeded(ins);
		}
		if(comp instanceof StringSpectrumPanel)
		{
			StringSpectrumPanel strSpectComp = (StringSpectrumPanel)comp;
			IStringSpectrum     iss = strSpectComp.getModel();
			refreshIfNeeded(iss);
		}		
		if(comp instanceof StringImagePanel)
		{
			StringImagePanel    strImageComp = (StringImagePanel)comp;
			IStringImage        isi = strImageComp.getModel();
			refreshIfNeeded(isi);
		}		
	}	
	
	public static void skippingRefresh(Component comp)
	{
		if(comp instanceof ImagePanel)
		{
			ImagePanel imgComp = (ImagePanel)comp;
			imgComp.getModel().setSkippingRefresh(true);
		}
		if(comp instanceof SpectrumPanel)
		{
			SpectrumPanel imgComp = (SpectrumPanel)comp;
			imgComp.getModel().setSkippingRefresh(true);
		}
		if(comp instanceof StringSpectrumPanel)
		{
			StringSpectrumPanel imgComp = (StringSpectrumPanel)comp;
			imgComp.getModel().setSkippingRefresh(true);
		}		
	}
	
	public static void activateRefreshForAllComponent(javax.swing.JTabbedPane jtabbedPane)
	{
		Component[] components = jtabbedPane.getComponents();
		for(int i=0;i < components.length;i++)
		{
			activateRefresh(components[i]);
		}
	}
	
	public static void skippingRefreshForAllComponent(javax.swing.JTabbedPane jtabbedPane)
	{
		Component[] components = jtabbedPane.getComponents();
		for(int i=0;i < components.length;i++)
		{
			skippingRefresh(components[i]);
		}		
	}
	
	public static void refreshIfNeeded(IAttribute  iatt)
	{ // call refresh() if and only if the attribute is not updated thanks to the Tango events
	        if (!iatt.hasEvents()) // events are not possible for this attribute (event subscription failed)
        	{
        		iatt.refresh();
        	}

	}
		
}
